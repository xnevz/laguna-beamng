"""Renault Laguna II (phase 1) liftback, built from the reference game model.

Run:  blender --background --factory-startup --python tools/laguna2/build_from_ref.py

Takes blender/references/3d-model.fbx (see refmodel.py), keeps its shape, and
turns it into a clean, part-split body that uses this project's laguna2_*
materials.  Saves blender/laguna2_liftback.blend with the same Laguna2_* object
naming as build.py, so render.py, compare.py and export_dae.py work unchanged.

Parts: Body (shell, roof, sills, quarters), Hood, Bumper_F, Bumper_R,
Fender_L/R, Door_FL/FR/RL/RR, Tailgate.  The whole car is subdivided as one
surface (level 3; only real folds and lamp/glass outlines stay crisp), the
paint is Taubin-faired, then the seams are cut on planes in the smooth surface;
panels get rolled hems and the seams are real ~3.5 mm gaps over a dark floor.
Tail lamps follow the 2005 facelift (smoked red with four round eyes).  Lamps are built as units (lens, housing, reflectors,
bulbs); glass, trim, badges and the extras the game model lacks (mirrors, arch
liners, plates, fog lamps, sensors, interior, wheels) are separate objects.

Coordinates: car faces -Y, +X is the car's left, Z up.  s = metres behind the
front bumper tip (Blender Y = s - L/2), as in build.py.
"""

import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build as proc  # noqa: E402  (materials, wheels, interior)
import lights  # noqa: E402
import refmodel  # noqa: E402

PROJECT_ROOT = os.path.dirname(os.path.dirname(HERE))
BLEND_PATH = os.path.join(PROJECT_ROOT, "blender", "laguna2_liftback.blend")

L = refmodel.L
HALF = L / 2.0
REAL_WIDTH = 1.774          # body width without mirrors

# FBX slot name -> role
PAINT, TRIM, AMBER, RED, CHROME_ARC, LENS, BLACK, GLASS, BADGE = (
    "Material#4", "Material#12", "Material#14", "Material#16", "Material#10",
    "Material#11", "Material#13", "Material#8", "Material#15")


def S(v):
    """Distance behind the front bumper tip of a project-space point."""
    return v.y + HALF


# --------------------------------------------------------------------------
# Load + clean
# --------------------------------------------------------------------------
def load_clean():
    bm, sbm, slots, info = refmodel.load()
    if sbm is not None:
        sbm.free()  # build.py's interior has its own steering wheel
    # Real width: the game model is ~4 % too narrow for the real car / jbeam track.
    xs = [v.co.x for v in bm.verts]
    kx = REAL_WIDTH / (max(xs) - min(xs))
    for v in bm.verts:
        v.co.x *= kx
    info["width_scale"] = kx
    bmesh.ops.dissolve_degenerate(bm, dist=1e-6, edges=bm.edges)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0006)
    bm.faces.ensure_lookup_table()
    print("[ref]", {k: round(v, 4) for k, v in info.items()})
    return bm, slots


def islands(faces):
    """Split faces into edge-connected islands of the same material."""
    todo = set(faces)
    out = []
    while todo:
        f = todo.pop()
        comp, stack = [f], [f]
        while stack:
            g = stack.pop()
            for e in g.edges:
                for h in e.link_faces:
                    if h in todo and h.material_index == g.material_index:
                        todo.remove(h)
                        comp.append(h)
                        stack.append(h)
        out.append(comp)
    return out


def bbox(faces):
    vs = [v.co for f in faces for v in f.verts]
    lo = Vector([min(v[i] for v in vs) for i in range(3)])
    hi = Vector([max(v[i] for v in vs) for i in range(3)])
    return lo, hi


# --------------------------------------------------------------------------
# Landmarks measured off the model itself
# --------------------------------------------------------------------------
class Marks:
    pass


def landmarks(bm, slot):
    m = Marks()
    by = lambda name: [f for f in bm.faces if f.material_index == slot[name]]
    lens = by(LENS)
    head = [f for f in lens if S(f.calc_center_median()) < HALF]
    tail_clear = [f for f in lens if S(f.calc_center_median()) >= HALF]
    lo, hi = bbox(head)
    m.hl_bottom, m.hl_top, m.hl_rear = lo.z, hi.z, S(hi)
    reds = [f for f in by(RED) if abs(f.calc_center_median().x) > 0.2]
    lo, hi = bbox(reds + tail_clear)
    m.tl_bottom, m.tl_top, m.tl_front = lo.z, hi.z, S(lo)
    m.tl_inner = min(abs(v.co.x) for f in reds for v in f.verts)
    m.tl_outer = max(abs(v.co.x) for f in reds for v in f.verts)
    glass = by(GLASS)
    ws = [f for f in glass if S(f.calc_center_median()) < 2.2 and abs(f.calc_center_median().x) < 0.5]
    lo, hi = bbox(ws)
    m.ws_base_s, m.ws_base_z = S(lo), lo.z
    rw = [f for f in glass if S(f.calc_center_median()) > 3.4 and abs(f.calc_center_median().x) < 0.5]
    lo, hi = bbox(rw)
    m.rw_top_s, m.rw_bottom_s, m.rw_bottom_z, m.rw_halfw = S(lo), S(hi), lo.z, hi.x
    side = [f for f in glass if abs(f.calc_center_median().x) > 0.55]
    m.belt_z = min(v.co.z for f in side for v in f.verts)
    lo, hi = bbox([f for f in by(PAINT)])
    m.half_w, m.roof_z = hi.x, hi.z
    m.floor_z = min(v.co.z for f in by(PAINT) if 1.4 < S(f.calc_center_median()) < 3.3 for v in f.verts)
    # Rear bumper rubbing strip: the widest dark-trim island across the tail.
    tail_trim = [f for f in by(TRIM) if S(f.calc_center_median()) > 4.0]
    strip = max(islands(tail_trim), key=lambda isl: bbox(isl)[1].x - bbox(isl)[0].x)
    lo, hi = bbox(strip)
    m.rstrip_bottom, m.rstrip_top = lo.z, hi.z
    m.axle_f, m.axle_r = refmodel.AXLE_F, refmodel.AXLE_R
    print("[marks]", {k: round(v, 3) for k, v in vars(m).items()})
    return m


TAIL_SPLIT_U = 0.62     # tailgate / wing split across the tail lamp, from the lamp's inner end

# --------------------------------------------------------------------------
# Panel layout
# --------------------------------------------------------------------------
ARCH_R = 0.40   # outer radius of the arch cut-outs measured from the wheel centre


def panel_rules(m):
    """Cut planes (applied to paint only) and the face -> part classifier."""
    s_bf = m.axle_f - 0.37            # front bumper ends at the arch's leading edge
    s_door_f = m.axle_f + 0.43        # front door leading edge (just behind the arch)
    s_door_b = 2.56                   # B-pillar split between front and rear doors
    s_door_r = m.axle_r - 0.33        # rear door trailing edge (front of the rear arch)
    s_bumper_r = m.axle_r + 0.36      # rear bumper starts at the arch's trailing edge
    z_bf = m.hl_bottom - 0.005        # bumper / wing line under the headlamps
    z_br = min(m.rstrip_top + 0.07, m.tl_bottom - 0.02)   # rear bumper top = tailgate bottom
    z_sill = 0.35                     # door bottoms (sill stays on the body)
    x_hood = 0.66                     # hood / wing shut line (half width)
    # Liftback tailgate: its side edges split the tail lamps (inner third on the gate),
    # step out at the lamp tops and follow the rear window up to the roof.
    x_tg = m.tl_inner + TAIL_SPLIT_U * (m.tl_outer - m.tl_inner)
    x_tg_hi = max(m.rw_halfw + 0.045, x_tg + 0.02)
    z_step = m.tl_top + 0.015
    s_tg_top = m.rw_top_s - 0.04
    z_tg = z_br

    def tg_half(z):
        return x_tg if z < z_step else x_tg_hi

    rear = m.rw_bottom_s - 0.3
    cuts = [
        # (plane point, plane normal, region test on face centre)
        (Vector((0, s_bf - HALF, 0)), Vector((0, 1, 0)), lambda c: c.z < z_bf + 0.05),
        (Vector((0, 0, z_bf)), Vector((0, 0, 1)), lambda c: S(c) < s_bf + 0.05),
        (Vector((0, s_door_f - HALF, 0)), Vector((0, 1, 0)), lambda c: z_sill - 0.05 < c.z < m.belt_z + 0.03),
        (Vector((0, s_door_b - HALF, 0)), Vector((0, 1, 0)), lambda c: z_sill - 0.05 < c.z < m.belt_z + 0.03),
        (Vector((0, s_door_r - HALF, 0)), Vector((0, 1, 0)), lambda c: z_sill - 0.05 < c.z < m.belt_z + 0.03),
        (Vector((0, 0, z_sill)), Vector((0, 0, 1)), lambda c: s_door_f - 0.05 < S(c) < s_door_r + 0.05),
        (Vector((x_hood, 0, 0)), Vector((1, 0, 0)), lambda c: S(c) < m.ws_base_s + 0.05 and c.z > z_bf - 0.02),
        (Vector((-x_hood, 0, 0)), Vector((1, 0, 0)), lambda c: S(c) < m.ws_base_s + 0.05 and c.z > z_bf - 0.02),
        (Vector((0, s_bumper_r - HALF, 0)), Vector((0, 1, 0)), lambda c: c.z < z_br + 0.05),
        (Vector((0, 0, z_br)), Vector((0, 0, 1)), lambda c: S(c) > s_bumper_r - 0.05),
        (Vector((x_tg, 0, 0)), Vector((1, 0, 0)), lambda c: S(c) > rear and z_tg - 0.05 < c.z < z_step + 0.03),
        (Vector((-x_tg, 0, 0)), Vector((1, 0, 0)), lambda c: S(c) > rear and z_tg - 0.05 < c.z < z_step + 0.03),
        (Vector((0, 0, z_step)), Vector((0, 0, 1)), lambda c: S(c) > rear and x_tg - 0.05 < abs(c.x) < x_tg_hi + 0.05),
        (Vector((x_tg_hi, 0, 0)), Vector((1, 0, 0)), lambda c: S(c) > s_tg_top - 0.1 and c.z > z_step - 0.03),
        (Vector((-x_tg_hi, 0, 0)), Vector((1, 0, 0)), lambda c: S(c) > s_tg_top - 0.1 and c.z > z_step - 0.03),
        (Vector((0, s_tg_top - HALF, 0)), Vector((0, 1, 0)), lambda c: c.z > m.rw_bottom_z + 0.15 and abs(c.x) < x_tg_hi + 0.05),
    ]

    def classify(c, n):
        s, ax, z = S(c), abs(c.x), c.z
        side = "L" if c.x > 0 else "R"
        if s < s_bf and z < z_bf:
            return "Bumper_F"
        if s > s_bumper_r and z < z_br:
            return "Bumper_R"
        if s < m.ws_base_s + 0.02 and z >= z_bf - 0.005:
            if ax < x_hood and n.z > 0.25:
                return "Hood"
            if ax < x_hood and s < 0.45:          # hood nose over the grille and lamps
                return "Hood"
        if s < s_door_f and z >= z_bf - 0.005 or (s_bf <= s < s_door_f and z < z_bf + 0.6):
            if ax > 0.3 or n.z < 0.25:
                return "Fender_" + side
        if s_door_f <= s < s_door_r and z_sill <= z <= m.belt_z + 0.01 and ax > 0.6:
            return ("Door_F" if s < s_door_b else "Door_R") + side
        if s > s_tg_top and z >= z_tg and ax < tg_half(z):
            return "Tailgate"
        return "Body"

    lines = dict(s_bf=s_bf, s_door_f=s_door_f, s_door_b=s_door_b, s_door_r=s_door_r, s_bumper_r=s_bumper_r,
                 z_bf=z_bf, z_br=z_br, z_sill=z_sill, x_hood=x_hood, x_tg=x_tg, x_tg_hi=x_tg_hi, z_step=z_step)
    print("[panels]", {k: round(v, 3) for k, v in lines.items()})
    return cuts, classify


def apply_cuts(bm, paint_slot, cuts):
    for co, no, region in cuts:
        faces = [f for f in bm.faces if f.material_index == paint_slot and region(f.calc_center_median())]
        if not faces:
            continue
        edges = list({e for f in faces for e in f.edges})
        verts = list({v for f in faces for v in f.verts})
        bmesh.ops.bisect_plane(bm, geom=faces + edges + verts, dist=0.0008, plane_co=co, plane_no=no)
    bm.faces.ensure_lookup_table()


# --------------------------------------------------------------------------
# Object helpers
# --------------------------------------------------------------------------
def shade_obj(obj, angle=38.0, weighted=True):
    me = obj.data
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    me.set_sharp_from_angle(angle=math.radians(angle))
    if weighted:
        mod = obj.modifiers.new("WeightedNormal", "WEIGHTED_NORMAL")
        mod.keep_sharp = True
        mod.mode = "FACE_AREA_WITH_ANGLE"
        mod.weight = 50


GAP = 0.0035          # shut-line gap between two panels
HEM_DEPTH = 0.009     # how far a panel edge rolls under at a shut line
LIP_DEPTH = 0.016     # roll-under at open edges (arches, openings)


def finish_panel(obj, shut_kd, lamp_tree=None):
    """Give a (dense, already smooth) panel real edges.

    Borders that meet another panel are pulled back by half the gap; every border
    then rolls under (a small chamfer, then a flange), so panel edges catch light
    like pressed steel instead of ending in a knife edge.
    """
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    border = [e for e in bm.edges if e.is_boundary]
    bverts = {v for e in border for v in e.verts}
    inward = {v: Vector() for v in bverts}
    for e in border:
        f = e.link_faces[0]
        a, b_ = e.verts
        perp = f.normal.cross(b_.co - a.co).normalized()
        if perp.dot(f.calc_center_median() - (a.co + b_.co) / 2) < 0:
            perp.negate()
        inward[a] += perp
        inward[b_] += perp
    normal = {v: v.normal.copy() for v in bverts}
    shut = set()
    for v in bverts:
        inward[v].normalize()
        _co, _i, dist = shut_kd.find(v.co)
        if dist is not None and dist < 0.003:
            shut.add(v)
    for v in shut:
        v.co += inward[v] * (GAP / 2)
    if lamp_tree is not None:
        # Edges that meet a lamp lens stay flush: a roll-under there would show through the lens.
        at_lamp = {v for v in bverts if v not in shut and lamp_tree.find_nearest(v.co, 0.012)[0] is not None}
        border = [e for e in border if not (e.verts[0] in at_lamp and e.verts[1] in at_lamp)]
        bverts = {v for e in border for v in e.verts}
    ring1, ring2 = {}, {}
    for v in bverts:
        n, t_in = normal[v], inward[v]
        depth = HEM_DEPTH if v in shut else LIP_DEPTH
        ring1[v] = bm.verts.new(v.co + t_in * 0.0012 - n * 0.0022)
        ring2[v] = bm.verts.new(v.co + t_in * 0.0030 - n * depth)
    mat = border[0].link_faces[0].material_index if border else 0
    for e in border:
        a, b_ = e.verts
        for q in ((a, b_, ring1[b_], ring1[a]), (ring1[a], ring1[b_], ring2[b_], ring2[a])):
            try:
                bm.faces.new(q).material_index = mat
            except ValueError:
                continue
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.polygons.foreach_set("use_smooth", [True] * len(obj.data.polygons))
    obj.data.set_sharp_from_angle(angle=math.radians(60))


def obj_from_faces(name, src_bm, faces, mat_for_face, angle=38.0, weighted=False, flip=False):
    """Copy `faces` of src_bm into a new object; mat_for_face(face) -> laguna2 material name."""
    bm = bmesh.new()
    vmap = {}
    names = []
    for f in faces:
        vs = []
        for v in f.verts:
            nv = vmap.get(v)
            if nv is None:
                nv = vmap[v] = bm.verts.new(v.co)
            vs.append(nv)
        try:
            nf = bm.faces.new(vs[::-1] if flip else vs)
        except ValueError:
            continue
        mname = mat_for_face(f)
        if mname not in names:
            names.append(mname)
        nf.material_index = names.index(mname)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for n in names:
        me.materials.append(proc.MATS[n])
    obj = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(obj)
    shade_obj(obj, angle, weighted)
    return obj


def bm_object(name, bm, mats, angle=40.0, weighted=False):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for n in mats:
        me.materials.append(proc.MATS[n])
    obj = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(obj)
    shade_obj(obj, angle, weighted)
    return obj


# --------------------------------------------------------------------------
# Body panels + shut lines
# --------------------------------------------------------------------------
EXHAUST_TAG = -2


def prepare_paint(bm, slot, m):
    """On the low-poly mesh: drop paint the car should not have (under the lamp
    lenses, the rear hub dummies) and tag the exhaust.  Creates the int face layer
    'part' (-1 = untagged, EXHAUST_TAG = exhaust); real parts are assigned after
    subdivision so the seams can be cut on the smooth surface."""
    lay = bm.faces.layers.int.new("part")     # create before holding face references
    bm.faces.ensure_lookup_table()
    paint = [f for f in bm.faces if f.material_index == slot[PAINT]]
    # The game model's paint carries on underneath the lamp lenses; that would hide
    # the lamp housings, so drop any paint face that looks straight out at a lens.
    lamp_bm = copy_faces([f for f in bm.faces if f.material_index in (slot[LENS], slot[RED])])
    lamp_tree = BVHTree.FromBMesh(lamp_bm)
    lamp_bm.free()
    dead = set()
    for f in paint:
        f[lay] = -1
    keep_mats = {slot[LENS], slot[RED], slot[GLASS]}
    for f in bm.faces:
        if f.material_index in keep_mats:
            continue
        c = f.calc_center_median()
        if lamp_tree.ray_cast(c + f.normal * 0.0005, f.normal, 0.12)[0] is not None:
            dead.add(f)
    for isl in islands(paint):
        lo, hi = bbox(isl)
        c = (lo + hi) / 2
        if len(isl) < 120 and abs(S(c) - m.axle_r) < 0.25 and abs(c.z - refmodel.WHEEL_R) < 0.2 and abs(c.x) < 0.8:
            dead.update(isl)               # rear hub dummies: our wheels bring their own brakes
        elif len(isl) < 80 and S(c) > 3.9 and c.z < 0.45 and abs(c.x) < 0.6:
            for f in isl:
                f[lay] = EXHAUST_TAG
    for f in bm.faces:
        if f.material_index != slot[PAINT]:
            f[lay] = -1
    bmesh.ops.delete(bm, geom=list(dead), context="FACES")
    print(f"[panels] removed {len(dead)} faces hidden behind lamp lenses / dummies")


def label_parts(bm, slot, m):
    """On the dense, smooth mesh: cut the panel seams (straight, on planes) and tag
    every paint face with its part.  Returns the part names ('part' layer indexes)."""
    cuts, classify = panel_rules(m)
    apply_cuts(bm, slot[PAINT], cuts)
    lay = bm.faces.layers.int["part"]
    labels = {}
    for f in bm.faces:
        if f.material_index == slot[PAINT]:
            labels[f] = "Exhaust" if f[lay] == EXHAUST_TAG else classify(f.calc_center_median(), f.normal)
    names = sorted(set(labels.values()))
    for f, name in labels.items():
        f[lay] = names.index(name)
    print(f"[panels] parts={names}")
    return names


# Master subdivision: only real folds stay sharp.  Edges folding less than
# FOLD_LO are the game mesh's faceting and are rounded off completely; the
# crease ramps up to fully sharp at FOLD_HI.  Lamp, glass and trim outlines
# (material changes) are fully creased, which subdivides them into smooth
# curves with a crisp edge rather than polylines.
FOLD_LO, FOLD_HI = 48.0, 85.0


def subdivide_master(bm, slot, levels=3):
    """Catmull-Clark the whole car at once, so every part keeps fitting its neighbours."""
    lay = bm.faces.layers.int["part"]
    for e in bm.edges:
        fs = e.link_faces
        e.seam = len(fs) == 2 and (fs[0].material_index != fs[1].material_index or fs[0][lay] != fs[1][lay])
        # (the 'part' layer only holds the exhaust tag at this stage)
    bmesh.ops.join_triangles(bm, faces=bm.faces[:], cmp_seam=True, cmp_materials=True,
                             angle_face_threshold=math.radians(30), angle_shape_threshold=math.radians(45))
    cr = bm.edges.layers.float.get("crease_edge") or bm.edges.layers.float.new("crease_edge")
    for e in bm.edges:
        fs = e.link_faces
        if len(fs) != 2:
            e[cr] = 0.0
        elif fs[0].material_index != fs[1].material_index:
            e[cr] = 1.0
        else:
            ang = math.degrees(e.calc_face_angle())
            e[cr] = min(max((ang - FOLD_LO) / (FOLD_HI - FOLD_LO), 0.0), 1.0)
    me = bpy.data.meshes.new("_master")
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new("_master", me)
    bpy.context.scene.collection.objects.link(obj)
    sd = obj.modifiers.new("Subdivision", "SUBSURF")
    sd.levels = levels
    sd.render_levels = levels
    sd.boundary_smooth = "PRESERVE_CORNERS"
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    dense = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
    bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.meshes.remove(me)
    out = bmesh.new()
    out.from_mesh(dense)
    bpy.data.meshes.remove(dense)
    out.faces.ensure_lookup_table()
    fair_paint(out, slot)
    print(f"[subdiv] level {levels}: {len(out.faces)} faces")
    return out


def fair_paint(bm, slot, iterations=40, feature_deg=11.0, lam=0.5, mu=-0.53):
    """Iron out the game mesh's dents on the paint, keeping outlines and real folds.

    Taubin smoothing (alternating shrink/inflate steps, so the surface keeps its
    volume) on every paint vertex except those on borders, material changes and
    folds sharper than feature_deg.  Vectorised with numpy.
    """
    import numpy as np
    iterations = int(os.environ.get("LAGUNA_FAIR", iterations))
    if iterations <= 0:
        return
    bm.verts.index_update()
    bm.normal_update()
    nv = len(bm.verts)
    pinned = np.zeros(nv, bool)
    for f in bm.faces:
        if f.material_index != slot[PAINT]:
            for v in f.verts:
                pinned[v.index] = True
    ei, ej = [], []
    for e in bm.edges:
        a, b_ = e.verts[0].index, e.verts[1].index
        ei.append(a)
        ej.append(b_)
        if e.is_boundary or len(e.link_faces) != 2 or e.calc_face_angle() > math.radians(feature_deg):
            pinned[a] = pinned[b_] = True
    ei, ej = np.array(ei), np.array(ej)
    co = np.array([v.co for v in bm.verts], dtype=np.float64)
    deg = np.bincount(ei, minlength=nv) + np.bincount(ej, minlength=nv)
    deg = np.maximum(deg, 1)[:, None]
    move = (~pinned)[:, None]

    def step(c, k):
        acc = np.zeros_like(c)
        np.add.at(acc, ei, c[ej])
        np.add.at(acc, ej, c[ei])
        return c + k * (acc / deg - c) * move

    for _ in range(iterations):
        co = step(step(co, lam), mu)
    for v in bm.verts:
        v.co = co[v.index]
    bm.normal_update()


def build_panels(bm, slot, names):
    lay = bm.faces.layers.int["part"]
    part_of = {f: names[f[lay]] for f in bm.faces if f.material_index == slot[PAINT] and f[lay] >= 0}
    groups = {}
    for f, p_ in part_of.items():
        groups.setdefault(p_, []).append(f)
    shut_kd = build_shutlines(part_of)
    lamp_bm = copy_faces([f for f in bm.faces if f.material_index in (slot[LENS], slot[RED])])
    lamp_tree = BVHTree.FromBMesh(lamp_bm)
    lamp_bm.free()
    for p_, faces in sorted(groups.items()):
        mat = "laguna2_alloy_dark" if p_ == "Exhaust" else "laguna2_paint"
        obj = obj_from_faces("Laguna2_" + p_, bm, faces, lambda f, mat=mat: mat, weighted=False)
        if p_ != "Exhaust":
            finish_panel(obj, shut_kd, lamp_tree)


def build_shutlines(part_of, width=0.016, depth=0.0065):
    """Dark floor sunk under every seam between two paint parts (seen through the gap).

    Returns a KD-tree of points along the seams, used to tell shut-line borders
    from open borders when the panels are finished.
    """
    from mathutils.kdtree import KDTree
    bm = bmesh.new()
    samples = []
    seen = set()
    for f, p in part_of.items():
        if not p or p == "Exhaust":
            continue
        for e in f.edges:
            if e in seen:
                continue
            ps = {part_of.get(g) for g in e.link_faces}
            ps.discard(None)
            ps.discard("Exhaust")
            if len(ps) < 2:
                continue
            seen.add(e)
            a, b = e.verts[0].co.copy(), e.verts[1].co.copy()
            d = (b - a)
            if d.length < 1e-5:
                continue
            n = sum((g.normal for g in e.link_faces), Vector()).normalized()
            k = max(int(d.length / 0.003), 1)
            samples += [a.lerp(b, i / k) for i in range(k + 1)]
            side = d.cross(n).normalized() * (width / 2)
            off = -n * depth
            ext = d.normalized() * 0.004
            q = [a - ext - side + off, b + ext - side + off, b + ext + side + off, a - ext + side + off]
            face = bm.faces.new([bm.verts.new(p_) for p_ in q])
            if face.normal.dot(n) < 0:
                face.normal_flip()
    bm_object("Laguna2_ShutLines", bm, ["laguna2_gap"], angle=180.0)
    kd = KDTree(len(samples))
    for i, s in enumerate(samples):
        kd.insert(s, i)
    kd.balance()
    print(f"[shutlines] {len(seen)} seam edges")
    return kd


# --------------------------------------------------------------------------
# Glass, lamps, trim
# --------------------------------------------------------------------------
def build_details(bm, slot, m):
    by = lambda name: [f for f in bm.faces if f.material_index == slot[name]]
    front = lambda f: S(f.calc_center_median()) < HALF

    obj_from_faces("Laguna2_Glass", bm, by(GLASS), lambda f: "laguna2_glass", angle=50.0)

    # Headlamps: clear lens over a closed chrome housing with two round reflectors
    # (projector low beam, high beam) and an amber indicator bulb, as on the car.
    lens = [f for f in by(LENS) if front(f)]
    for side, sign in (("L", 1), ("R", -1)):
        faces = [f for f in lens if f.calc_center_median().x * sign > 0]
        build_headlamp(side, sign, faces)

    # Tail lamps: split where the tailgate opens; clear upper band inset in red.
    tail_clear = [f for f in by(LENS) if not front(f)]
    reds = by(RED)
    for side, sign in (("L", 1), ("R", -1)):
        faces = [f for f in reds + tail_clear if f.calc_center_median().x * sign > 0.2]
        build_taillamp(side, sign, faces, m)
    obj_from_faces("Laguna2_BrakeLight3", bm, [f for f in reds if abs(f.calc_center_median().x) <= 0.2],
                   lambda f: "laguna2_brake3")

    obj_from_faces("Laguna2_Repeaters", bm, by(AMBER),
                   lambda f: "laguna2_repeater_L" if f.calc_center_median().x > 0 else "laguna2_repeater_R")

    # Front grille: brushed chrome brow on top; everything behind and below the
    # slats is black plastic (the game model painted it chrome).
    bars = [f for f in by(TRIM) if S(f.calc_center_median()) < 0.25 and abs(f.calc_center_median().x) < 0.4]
    bar_top = max(v.co.z for f in bars for v in f.verts)
    grille = by(CHROME_ARC) + [f for f in by(BLACK) if front(f) and abs(f.calc_center_median().x) < 0.3] + bars
    gset = set(grille)

    def grille_mat(f):
        if f.material_index == slot[CHROME_ARC]:
            return "laguna2_chrome_brushed" if f.calc_center_median().z > bar_top - 0.004 else "laguna2_grille"
        if f.material_index == slot[TRIM]:
            return "laguna2_grille_slat"
        return "laguna2_grille"
    obj_from_faces("Laguna2_Grille", bm, grille, grille_mat, angle=35.0, weighted=False)

    trim = [f for f in by(TRIM) + by(BLACK) if f not in gset]
    obj_from_faces("Laguna2_Trim", bm, trim,
                   lambda f: "laguna2_black" if f.material_index == slot[BLACK] else "laguna2_trim", angle=35.0)

    # Badges: the game model's flat logos are replaced by proper diamonds (build_badges).
    # Its two red tabs under the tail lamps are not on the real car and are dropped.
    logos = [f for f in by(BADGE) if abs(f.calc_center_median().x) <= 0.2]
    recesses = []
    pockets = [f for f in by(BLACK) if front(f) and abs(f.calc_center_median().x) > 0.3]
    for sign in (1, -1):
        isls = [isl for isl in islands([f for f in pockets if f.calc_center_median().x * sign > 0])]
        if not isls:
            continue
        lowest = min(bbox(isl)[1].z for isl in isls)
        fs = [f for isl in isls if bbox(isl)[1].z < lowest + 0.03 for f in isl]
        lo, hi = bbox(fs)
        recesses.append(((lo + hi) / 2, hi.z - lo.z))
    # Black backing right behind the slats so the grille never shows paint.
    lo, hi = bbox(bars)
    gb = bmesh.new()
    lamp_inner = min(abs(v.co.x) for f in by(LENS) if front(f) for v in f.verts)
    s_b, w_b = S(hi) + 0.02, min(hi.x + 0.05, lamp_inner - 0.012)
    z0, z1 = lo.z - 0.04, bar_top + 0.015
    f_b = gb.faces.new([gb.verts.new(q) for q in ((-w_b, s_b - HALF, z0), (w_b, s_b - HALF, z0),
                                                    (w_b, s_b - HALF, z1), (-w_b, s_b - HALF, z1))])
    if f_b.normal.y > 0:
        f_b.normal_flip()
    bm_object("Laguna2_GrilleInsert", gb, ["laguna2_grille"], angle=60.0)
    return recesses, [(sum((f.calc_center_median() for f in isl), Vector()) / len(isl),
             sum((f.normal * f.calc_area() for f in isl), Vector()).normalized()) for isl in islands(logos)]


# --------------------------------------------------------------------------
# Lamp units
# --------------------------------------------------------------------------
def frame(p, n, up=Vector((0, 0, 1))):
    """4x4 matrix at p whose Z is n and whose X is horizontal (viewer's right when facing the surface)."""
    z = Vector(n).normalized()
    x = up.cross(z)
    if x.length < 1e-6:
        x = Vector((1, 0, 0))
    x.normalize()
    y = z.cross(x)
    mtx = Matrix((x, y, z)).transposed().to_4x4()
    mtx.translation = p
    return mtx


def copy_faces(faces, key=lambda f: 0):
    """Faces of the master bmesh -> new bmesh; the int layer 'key' keeps key(f)."""
    bm = bmesh.new()
    lay = bm.faces.layers.int.new("key")
    vmap = {}
    for f in faces:
        vs = []
        for v in f.verts:
            if v not in vmap:
                vmap[v] = bm.verts.new(v.co)
            vs.append(vmap[v])
        try:
            nf = bm.faces.new(vs)
        except ValueError:
            continue
        nf[lay] = key(f)
    bm.normal_update()
    return bm


def lamp_unit(name, lens_bm, lens_mats, back_mats, depth, wall_mat, gasket=0.005, push=None,
              lens_keep=None, rim=0.0, rim_mat="laguna2_tail_rim", outline=0.0, lens_angle=50.0):
    """Lens surface + closed housing behind it.

    lens_bm faces carry an int 'key'; lens_mats[key] / back_mats[key] pick the
    lens material and the material of the housing directly behind that face.
    Returns (lens object, outward direction, BVH of the lens).
    """
    lay = lens_bm.faces.layers.int["key"]
    area = sum((f.normal * f.calc_area() for f in lens_bm.faces), Vector())
    out = area.normalized()
    if push is not None:            # direction the housing is pushed back along (default: lens normal)
        out = push.normalized()
    centre = sum((v.co for v in lens_bm.verts), Vector()) / len(lens_bm.verts)
    tree = BVHTree.FromBMesh(lens_bm)

    # Housing: the lens pushed straight back, plus walls joining the two outlines.
    hb = bmesh.new()
    if push is not None:
        # Follow the lens: each point goes back along a blend of its own normal and
        # `push`, so flat-lying parts of the lens (its top) get a housing below them.
        back = {v: hb.verts.new(v.co - (v.normal * 0.6 + out * 0.4).normalized() * depth) for v in lens_bm.verts}
    else:
        back = {v: hb.verts.new(v.co - out * depth) for v in lens_bm.verts}
    front_ = {v: hb.verts.new(v.co - out * 0.0015) for v in lens_bm.verts}
    names = list(dict.fromkeys(list(back_mats) + [wall_mat, "laguna2_black"] + ([rim_mat] if rim else [])))
    for f in lens_bm.faces:
        nf = hb.faces.new([back[v] for v in f.verts])
        nf.material_index = names.index(back_mats[f[lay]])
    inside = centre - out * depth * 0.5
    for e in lens_bm.edges:
        if not e.is_boundary:
            continue
        a, b_ = e.verts
        nf = hb.faces.new((front_[a], front_[b_], back[b_], back[a]))
        nf.material_index = names.index(wall_mat)
        if nf.normal.dot(inside - nf.calc_center_median()) < 0:
            nf.normal_flip()
        # Dark gasket just under the lens edge, like the seal round a real lamp.
        f_in = e.link_faces[0]
        perp = f_in.normal.cross(b_.co - a.co).normalized()
        if perp.dot(f_in.calc_center_median() - (a.co + b_.co) / 2) < 0:
            perp.negate()
        sink = f_in.normal * 0.0008
        q = [a.co - sink, b_.co - sink, b_.co + perp * gasket - sink, a.co + perp * gasket - sink]
        gf = hb.faces.new([hb.verts.new(p) for p in q])
        gf.material_index = names.index("laguna2_black")
        if gf.normal.dot(f_in.normal) < 0:
            gf.normal_flip()
        ext = (b_.co - a.co).normalized() * 0.0012          # overlap neighbours so bands never break
        if rim:
            # Deep-red rim moulded round the edge of the lens (sits on the lens surface).
            lift = f_in.normal * 0.0007
            q = [a.co - ext + lift, b_.co + ext + lift, b_.co + ext + perp * rim + lift, a.co - ext + perp * rim + lift]
            rf = hb.faces.new([hb.verts.new(p) for p in q])
            rf.material_index = names.index(rim_mat)
            if rf.normal.dot(f_in.normal) < 0:
                rf.normal_flip()
        if outline:
            # Crisp dark seam where the lamp meets the bodywork.
            lift = f_in.normal * 0.0005
            q = [a.co - ext + lift, b_.co + ext + lift, b_.co + ext - perp * outline + lift, a.co - ext - perp * outline + lift]
            of = hb.faces.new([hb.verts.new(p) for p in q])
            of.material_index = names.index("laguna2_black")
            if of.normal.dot(f_in.normal) < 0:
                of.normal_flip()
    bm_object(name + "Housing", hb, names, angle=35.0)

    # Lens.
    lb = lens_bm.copy()
    if lens_keep is not None:
        bmesh.ops.delete(lb, geom=[f for f in lb.faces if not lens_keep(f)], context="FACES")
    lay2 = lb.faces.layers.int["key"]
    lnames = list(dict.fromkeys(lens_mats))
    for f in lb.faces:
        f.material_index = lnames.index(lens_mats[f[lay2]])
    lens_obj = bm_object(name + "Lens", lb, lnames, angle=lens_angle)
    return lens_obj, out, tree


def bowl(bm, centre, axis, radius, depth, mat, segs=32, rim=0.004):
    """Parabolic reflector opening along `axis`, with a short rolled rim."""
    mtx = frame(centre, axis)
    centre_v = bm.verts.new(mtx @ Vector((0, 0, -depth)))
    rings = []
    prof = [(radius * (i / 6) ** 0.5, -depth * (1 - i / 6)) for i in range(1, 7)]
    prof += [(radius * 1.04, rim * 0.5), (radius * 1.10, rim * 0.5)]
    for r, z in prof:
        rings.append([bm.verts.new(mtx @ Vector((r * math.cos(2 * math.pi * k / segs),
                                                 r * math.sin(2 * math.pi * k / segs), z))) for k in range(segs)])
    for k in range(segs):
        bm.faces.new((centre_v, rings[0][(k + 1) % segs], rings[0][k])).material_index = mat
    for a, b_ in zip(rings[:-1], rings[1:]):
        for k in range(segs):
            bm.faces.new((a[k], a[(k + 1) % segs], b_[(k + 1) % segs], b_[k])).material_index = mat
    return mtx


def dome(bm, centre, axis, radius, height, mat, segs=24):
    """Shallow spherical cap (projector lens, bulb glass) bulging along `axis`."""
    mtx = frame(centre, axis)
    top = bm.verts.new(mtx @ Vector((0, 0, height)))
    rings = []
    for i in range(1, 5):
        t = i / 4
        r = radius * math.sin(t * math.pi / 2)
        z = height * math.cos(t * math.pi / 2)
        rings.append([bm.verts.new(mtx @ Vector((r * math.cos(2 * math.pi * k / segs),
                                                 r * math.sin(2 * math.pi * k / segs), z))) for k in range(segs)])
    for k in range(segs):
        bm.faces.new((top, rings[0][k], rings[0][(k + 1) % segs])).material_index = mat
    for a, b_ in zip(rings[:-1], rings[1:]):
        for k in range(segs):
            bm.faces.new((a[k], b_[k], b_[(k + 1) % segs], a[(k + 1) % segs])).material_index = mat


def lens_slice(lens_bm, xc, sign, half=0.035):
    """Vertical extent of the lens around |x| = xc -> (z_mid, height)."""
    zs = [v.co.z for v in lens_bm.verts if abs(v.co.x * sign - xc) < half]
    if len(zs) < 2:
        zs = [v.co.z for v in lens_bm.verts]
    return (min(zs) + max(zs)) / 2, max(zs) - min(zs)


def hit_lens(tree, x, z, from_front=True):
    o = Vector((x, -HALF - 1.0 if from_front else HALF + 1.0, z))
    d = Vector((0, 1 if from_front else -1, 0))
    p, n, _i, _d = tree.ray_cast(o, d, 5.0)
    if p is None:
        return None, None
    if n.dot(d) > 0:
        n = -n
    return p, n


def build_headlamp(side, sign, faces):
    lens_bm = copy_faces(faces)
    _lens, out, tree = lamp_unit(f"Laguna2_Headlamp{side}_", lens_bm, ["laguna2_lamp_clear"],
                                 ["laguna2_lamp_housing"], 0.085, "laguna2_lamp_housing",
                                 push=Vector((0, -1, 0)))
    xs = [abs(v.co.x) for v in lens_bm.verts]
    x_in, x_out = min(xs), max(xs)
    bm = bmesh.new()
    CHROME, LOW_LENS, LOW, HIGH, SIGNAL, AMBER_, POS = range(7)
    units = (("low", x_in + 0.085, 0.47, 0.060), ("high", x_in + 0.200, 0.40, 0.046),
             ("ind", x_in + 0.292, 0.30, 0.030))
    for kind, xc, frac, rmax in units:
        if xc > x_out - 0.03:
            continue
        zc, h = lens_slice(lens_bm, xc, sign)
        p, n = hit_lens(tree, sign * xc, zc)
        if p is None:
            print("[warn] headlamp ray missed", kind, side)
            continue
        r = min(frac * h, rmax)
        c = p - n * 0.024
        if kind == "low":
            # Low beam: projector (big glass lens in a chrome ring) in its own bowl,
            # with the small sidelight bulb tucked under the projector.
            bowl(bm, c, n, r, r * 0.55, LOW)
            dome(bm, c + n * 0.002, n, r * 0.52, r * 0.30, LOW_LENS)
            bowl(bm, c + n * 0.001, n, r * 0.60, 0.004, CHROME, segs=28, rim=0.003)
            down = (Vector((0, 0, -1)) - n * n.z).normalized()
            dome(bm, c + down * r * 0.76 - n * 0.006, n, 0.0065, 0.009, POS, segs=14)
        elif kind == "high":
            bowl(bm, c, n, r, r * 0.55, HIGH)
            dome(bm, c - n * r * 0.18, n, 0.011, 0.016, HIGH, segs=16)
            dome(bm, c + n * 0.004, n, 0.016, 0.006, CHROME, segs=16)      # bulb shield cap
        else:
            bowl(bm, c, n, r, r * 0.55, SIGNAL)
            dome(bm, c - n * r * 0.15, n, 0.011, 0.016, AMBER_, segs=16)
    bm_object(f"Laguna2_Headlamp{side}_Reflectors", bm,
              ["laguna2_lamp_ring", "laguna2_hl_low_lens", "laguna2_hl_low", "laguna2_hl_high",
               f"laguna2_hl_signal_{side}", "laguna2_amber", "laguna2_hl_position"], angle=40.0)


def ring(bm, centre, axis, r0, r1, mat, segs=40, lift=0.0, drop=0.002):
    """Flat annulus (a lamp bezel) with a short skirt on the outside edge."""
    mtx = frame(centre, axis)
    pts = lambda r, z: [bm.verts.new(mtx @ Vector((r * math.cos(2 * math.pi * k / segs),
                                                   r * math.sin(2 * math.pi * k / segs), z))) for k in range(segs)]
    inner, outer, skirt = pts(r0, lift), pts(r1, lift), pts(r1 * 1.02, lift - drop)
    for a, b_ in ((inner, outer), (outer, skirt)):
        for k in range(segs):
            bm.faces.new((a[k], a[(k + 1) % segs], b_[(k + 1) % segs], b_[k])).material_index = mat


def tube(bm, centre, axis, r, depth, mat, segs=40):
    """Open cylinder running back from `centre` along -axis, faces pointing inwards."""
    mtx = frame(centre, axis)
    front = [bm.verts.new(mtx @ Vector((r * math.cos(2 * math.pi * k / segs), r * math.sin(2 * math.pi * k / segs), 0)))
             for k in range(segs)]
    back = [bm.verts.new(mtx @ Vector((r * math.cos(2 * math.pi * k / segs), r * math.sin(2 * math.pi * k / segs), -depth)))
            for k in range(segs)]
    for k in range(segs):
        bm.faces.new((front[k], back[k], back[(k + 1) % segs], front[(k + 1) % segs])).material_index = mat


# Facelift-style tail lamp: a red lozenge with four round "eyes" in a row,
# measured from the inner end (u = 0) to the outer end (u = 1) of the lamp:
# reversing light, two red tail/brake eyes, indicator.
# The tailgate takes the larger, inner part of each lamp: its edge runs nearly
# straight down from the rear-window corner through the lamp (measured on the
# reference photos at ~60 % of the lamp's width from its inner end).  The gate
# section carries the reversing light near its inner end and two red eyes,
# evenly spaced; the wing section has the indicator centred in it.
TAIL_EYES = (("reverse", 0.120), ("red", 0.315), ("red", 0.505), ("signal", 0.805))
TAIL_BEND = 0.008      # how far the horizontal ridge through the middle of the lens stands out


def bend_lens(bm, sign, out, amount=TAIL_BEND):
    """Fold the lens along a horizontal line through its middle (a shallow ridge),
    fading to nothing at the lens edge so it still meets the bodywork."""
    from mathutils.kdtree import KDTree
    bverts = [v for v in bm.verts if v.is_boundary]
    kd = KDTree(len(bverts))
    for i, v in enumerate(bverts):
        kd.insert(v.co, i)
    kd.balance()
    cache = {}

    def span(x):
        key = round(abs(x) / 0.005)
        if key not in cache:
            zs = [v.co.z for v in bverts if abs(abs(v.co.x) - key * 0.005) < 0.012]
            cache[key] = (min(zs), max(zs)) if len(zs) >= 2 else None
        return cache[key]

    moves = {}
    for v in bm.verts:
        sp = span(v.co.x)
        if sp is None or v.is_boundary:
            continue
        z0, z1 = sp
        h = max(z1 - z0, 1e-3)
        tent = max(1.0 - abs(v.co.z - (z0 + z1) / 2) / (h / 2), 0.0)
        _c, _i, d = kd.find(v.co)
        fade = min(d / 0.02, 1.0)
        moves[v] = out * (amount * tent * fade)
    for v, d in moves.items():
        v.co += d
    bm.normal_update()


def build_taillamp(side, sign, faces, m):
    """Each tail lamp = an inner unit on the tailgate and an outer unit on the wing."""
    x_tg = m.tl_inner + TAIL_SPLIT_U * (m.tl_outer - m.tl_inner)
    bm = copy_faces(faces)
    bmesh.ops.bisect_plane(bm, geom=bm.faces[:] + bm.edges[:] + bm.verts[:], dist=0.0006,
                           plane_co=Vector((sign * x_tg, 0, 0)), plane_no=Vector((1, 0, 0)))
    bm.normal_update()
    out_all = sum((f.normal * f.calc_area() for f in bm.faces), Vector()).normalized()
    bend_lens(bm, sign, out_all)
    full_tree = BVHTree.FromBMesh(bm)

    eyes = []
    for kind, u in TAIL_EYES:
        ax = m.tl_inner + u * (m.tl_outer - m.tl_inner)
        zc, h = lens_slice(bm, ax, sign, half=0.02)
        r = min(0.31 * h, 0.035)
        p, n, _i, _d = full_tree.ray_cast(Vector((sign * ax, HALF + 1.0, zc)), Vector((0, -1, 0)), 5.0)
        if p is None:
            print("[warn] tail eye ray missed", side, kind, u)
            continue
        n = out_all.copy()               # eyes face straight out, not along the bent facet
        if side == "L" and kind == "red" and u == TAIL_EYES[2][1]:
            kind = "fog"                 # rear fog light: driver's side only (LHD, EU rule)
        eyes.append((kind, ax, p, n, r))

    for part, keep in (("Gate", lambda ax: ax < x_tg), ("Wing", lambda ax: ax >= x_tg)):
        sub = bm.copy()
        bmesh.ops.delete(sub, geom=[f for f in sub.faces if not keep(abs(f.calc_center_median().x))], context="FACES")
        if not sub.faces:
            continue
        sub.normal_update()
        mine = [e for e in eyes if keep(e[1])]
        holes = [(p, r) for _k, _ax, p, _n, r in mine]

        def radial(c, p):
            return ((c - p) - out_all * (c - p).dot(out_all)).length

        # Refine the lens round each eye (faces ~3 mm) so the hole cut for it is
        # round enough to hide under the bezel and the dark outline ring.
        near = [e for e in sub.edges if any(abs(radial((e.verts[0].co + e.verts[1].co) / 2, p) - r) < 0.018
                                            for p, r in holes)]
        if near:
            bmesh.ops.subdivide_edges(sub, edges=near, cuts=3, use_grid_fill=True)
        sub.normal_update()

        def lens_keep(f, holes=holes):
            c = f.calc_center_median()
            return all(radial(c, p) > r + 0.004 for p, r in holes)

        name = f"Laguna2_Taillamp{side}{part}_"
        lamp_unit(name, sub, ["laguna2_tail_lens_red"], ["laguna2_tail_reflector"], 0.05,
                  "laguna2_tail_reflector", gasket=0.0045, lens_keep=lens_keep, rim=0.009, outline=0.0035,
                  lens_angle=5.0)
        eb = bmesh.new()
        CHROME, BLACK, REDCHROME, REFL, EYE_RED, CLEAR, REV, SIG, BULB, FOG = range(10)
        for kind, _ax, p, n, r in mine:
            # Every eye: its own lens set into a hole in the red lens, a proud bezel
            # and a dark outline ring, so it reads as a separate round lamp.
            ring(eb, p + n * 0.0014, n, r + 0.006, r + 0.0095, BLACK, drop=0.003)
            if kind in ("reverse", "signal"):
                fn = REV if kind == "reverse" else SIG
                ring(eb, p + n * 0.0024, n, r - 0.003, r + 0.006, CHROME, drop=0.004)       # chrome bezel
                tube(eb, p - n * 0.001, n, r - 0.002, 0.026, fn)
                bowl(eb, p - n * 0.020, n, r - 0.003, 0.012, fn, segs=36)
                dome(eb, p - n * 0.022, n, 0.010, 0.017, fn, segs=16)                      # bulb
                ring(eb, p - n * 0.008, n, r * 0.30, r * 0.62, CHROME, drop=0.0)          # inner reflector ring
                dome(eb, p - n * 0.0002, n, r - 0.002, 0.006, CLEAR, segs=48)             # clear eye lens
            else:
                ring(eb, p + n * 0.0022, n, r - 0.003, r + 0.006, REDCHROME, drop=0.004)    # red-chrome bezel
                tube(eb, p - n * 0.001, n, r - 0.002, 0.026, REFL)
                bowl(eb, p - n * 0.020, n, r - 0.003, 0.010, REFL, segs=36)
                ring(eb, p - n * 0.010, n, r * 0.28, r * 0.55, REDCHROME, drop=0.0)       # inner ring
                dome(eb, p - n * 0.016, n, 0.009, 0.012, BULB, segs=14)
                dome(eb, p - n * 0.0002, n, r - 0.002, 0.007, FOG if kind == "fog" else EYE_RED, segs=48)
        bm_object(name + "Eyes", eb, ["laguna2_lamp_ring", "laguna2_black", "laguna2_tail_tube",
                                      "laguna2_tail_reflector", "laguna2_tail_eye_red", "laguna2_lamp_clear",
                                      "laguna2_reverse", f"laguna2_tail_signal_{side}", "laguna2_bulb",
                                      "laguna2_tail_fog"], angle=40.0)


# --------------------------------------------------------------------------
# Extras the game model does not have
# --------------------------------------------------------------------------
def body_bvh(names):
    bm = bmesh.new()
    for n in names:
        o = bpy.data.objects.get(n)
        if o:
            tmp = bmesh.new()
            tmp.from_mesh(o.data)
            tmp.transform(o.matrix_world)
            me = bpy.data.meshes.new("_tmp")
            tmp.to_mesh(me)
            tmp.free()
            bm.from_mesh(me)
            bpy.data.meshes.remove(me)
    tree = BVHTree.FromBMesh(bm)
    bm.free()
    return tree


def surface(tree, origin, direction):
    hit = tree.ray_cast(Vector(origin), Vector(direction).normalized(), 10.0)
    return hit[0], hit[1]


def build_mirrors(tree, m):
    s = m.axle_f + 0.62
    for sign, tag in ((1.0, "L"), (-1.0, "R")):
        z = m.belt_z + 0.07
        p, n = surface(tree, (sign * 2.0, s - HALF, m.belt_z - 0.04), (-sign, 0, 0))
        if p is None:
            continue
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=28, v_segments=16, radius=1.0)
        for v in bm.verts:
            v.co.x = 0.095 * math.copysign(abs(v.co.x) ** 0.7, v.co.x)
            v.co.y *= 0.07
            v.co.z = 0.056 * math.copysign(abs(v.co.z) ** 0.7, v.co.z)
            if v.co.y > 0.028:
                v.co.y = 0.028
        for f in bm.faces:
            f.material_index = 1 if all(abs(v.co.y - 0.028) < 1e-5 for v in f.verts) else 0
        centre = Vector((p.x + sign * 0.125, s - HALF + 0.02, z))
        bmesh.ops.translate(bm, vec=centre, verts=bm.verts)
        bm_object(f"Laguna2_Mirror_{tag}", bm, ["laguna2_paint", "laguna2_mirror"], angle=50.0)
        foot = bmesh.new()
        bmesh.ops.create_cube(foot, size=1.0, matrix=Matrix.Translation((p.x + sign * 0.04, s - HALF + 0.03, z - 0.01))
                              @ Matrix.Diagonal((0.10, 0.08, 0.045, 1.0)))
        bmesh.ops.bevel(foot, geom=foot.edges[:], offset=0.01, segments=2, affect="EDGES")
        bm_object(f"Laguna2_MirrorFoot_{tag}", foot, ["laguna2_black"], angle=40.0)


def build_liners(m):
    """Black wheel-arch liners: the game model's arches are open to the cabin."""
    bm = bmesh.new()
    for s_axle in (m.axle_f, m.axle_r):
        for sign in (1.0, -1.0):
            x0, x1 = sign * 0.50, sign * (m.half_w - 0.025)
            rows = []
            n = 28
            for i in range(n + 1):
                a = math.radians(-12 + (192 + 12) * i / n)        # from just in front, over the top, to just behind
                r = ARCH_R - 0.015
                y = s_axle - HALF - r * math.cos(a)
                z = refmodel.WHEEL_R + 0.03 + r * math.sin(a)
                rows.append((bm.verts.new((x0, y, z)), bm.verts.new((x1, y, z))))
            for (a0, a1), (b0, b1) in zip(rows[:-1], rows[1:]):
                f = bm.faces.new((a0, a1, b1, b0))
                # Face the wheel (towards the arch centre).
                c = f.calc_center_median()
                to_axis = Vector((0, s_axle - HALF - c.y, refmodel.WHEEL_R + 0.03 - c.z))
                if f.normal.dot(to_axis) < 0:
                    f.normal_flip()
    bm_object("Laguna2_ArchLiners", bm, ["laguna2_black"], angle=60.0)


def build_underbody(m):
    bm = bmesh.new()
    s0, s1 = m.axle_f - 0.38, m.axle_r + 0.38
    w = m.half_w - 0.06
    z = m.floor_z + 0.03
    vs = [bm.verts.new(p) for p in ((-w, s0 - HALF, z), (w, s0 - HALF, z), (w, s1 - HALF, z), (-w, s1 - HALF, z))]
    f = bm.faces.new(vs)
    if f.normal.z > 0:
        f.normal_flip()
    bm_object("Laguna2_Underbody", bm, ["laguna2_black"], angle=60.0)


def build_plates(tree, m):
    specs = (("F", 1, (0.50, 0.47, 0.53, 0.44), "laguna2_plate_white"),
             ("R", -1, (m.rstrip_bottom - 0.075,), "laguna2_plate_white"))
    for tag, s_dir, heights, mat_name in specs:
        for z in heights:
            p, n = surface(tree, (0.0, -s_dir * 4.0, z), (0, s_dir, 0))
            # The ray must land on the near end (not through an intake onto the far bumper).
            if p is not None and (S(p) < 0.5 if s_dir > 0 else S(p) > L - 0.5):
                break
        else:
            print("[warn] no surface for plate", tag)
            continue
        n = Vector((0, n.y, n.z)).normalized()
        if n.y * s_dir > 0:
            n = -n
        fr = frame(p + n * 0.006, n)
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0, matrix=fr @ Matrix.Diagonal((0.52, 0.11, 0.006, 1.0)))
        bmesh.ops.bevel(bm, geom=[e for e in bm.edges], offset=0.0025, segments=2, affect="EDGES")
        # European plate: blue band with the country letter on the left.
        res = bmesh.ops.create_cube(bm, size=1.0, matrix=fr @ Matrix.Translation((-0.26 + 0.022, 0, 0.0032))
                                    @ Matrix.Diagonal((0.042, 0.104, 0.0008, 1.0)))
        for f in {f for v in res["verts"] for f in v.link_faces}:
            f.material_index = 1
        bm_object(f"Laguna2_Plate_{tag}", bm, [mat_name, "laguna2_plate_blue"], angle=30.0)
        proc.text_mesh(f"Laguna2_PlateText_{tag}", "LAGUNA II", 0.066, "laguna2_gap",
                       frame(p + n * 0.0093, n) @ Matrix.Translation((0.02, 0, 0)), extrude=0.0004, spacing=1.1)
        proc.text_mesh(f"Laguna2_PlateCountry_{tag}", "F", 0.03, "laguna2_plate_white",
                       frame(p + n * 0.0098, n) @ Matrix.Translation((-0.238, -0.025, 0)), extrude=0.0003)


def build_badges(logos, tree_f, tree_r, m):
    """Renault diamonds where the game model had flat logos; at the back the diamond
    sits in a dark housing with the tailgate handle pocket under it, and the
    LAGUNA script is centred below, widely spaced (as on the facelift car)."""
    rear_frame = None
    for c, n in logos:
        front = S(c) < HALF
        tree = tree_f if front else tree_r
        d = Vector((0, 1, 0)) if front else Vector((0, -1, 0))
        p, nn = surface(tree, (c.x, c.y - d.y * 1.0, c.z), d)
        if p is None:
            p, nn = c, n
        if nn.dot(d) > 0:
            nn = -nn
        nn = (nn - d * 0.8).normalized()      # badges stand up off the curved surface, facing out
        if front:
            proc.diamond("Laguna2_BadgeFront", 0.078, 0.10, 0.009, frame(p + nn * 0.001, nn))
            continue
        rear_frame = (p, nn)
        hb = bmesh.new()
        fr = frame(p + Vector((0, 0, -0.024)), nn)
        w, h, rad, th = 0.080, 0.150, 0.026, 0.006
        outline = []
        for cx, cy, a0 in ((w / 2 - rad, h / 2 - rad, 0), (-w / 2 + rad, h / 2 - rad, 90),
                           (-w / 2 + rad, -h / 2 + rad, 180), (w / 2 - rad, -h / 2 + rad, 270)):
            for k in range(9):
                a = math.radians(a0 + 90 * k / 8)
                outline.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
        bot = [hb.verts.new(fr @ Vector((x, y, -0.002))) for x, y in outline]
        top = [hb.verts.new(fr @ Vector((x * 0.97, y * 0.985, th))) for x, y in outline]
        hb.faces.new(top)
        for i in range(len(outline)):
            j = (i + 1) % len(outline)
            hb.faces.new((bot[i], bot[j], top[j], top[i]))
        bmesh.ops.recalc_face_normals(hb, faces=hb.faces)
        slot_m = frame(p + nn * (th + 0.0005) + Vector((0, 0, -0.072)), nn)
        res = bmesh.ops.create_cube(hb, size=1.0, matrix=slot_m @ Matrix.Diagonal((0.050, 0.020, 0.002, 1.0)))
        for f in {f for v in res["verts"] for f in v.link_faces}:
            f.material_index = 1
        bm_object("Laguna2_BadgeHousing", hb, ["laguna2_badge_housing", "laguna2_black"], angle=35.0)
        proc.diamond("Laguna2_BadgeRear", 0.058, 0.078, 0.007, frame(p + nn * 0.0062, nn))
    if rear_frame is not None:
        p0 = rear_frame[0]
        z = p0.z - 0.125
        p, nn = surface(tree_r, (0.0, HALF + 1.0, z), (0, -1, 0))
        if p is not None:
            if nn.y < 0:
                nn = -nn
            proc.text_mesh("Laguna2_Lettering", "LAGUNA", 0.022, "laguna2_chrome", frame(p + nn * 0.0006, nn),
                           extrude=0.001, spacing=2.6)


def build_fog_lamps(tree, m, recesses):
    """Round fog lamps in the black pockets at the bottom corners of the front bumper."""
    bm = bmesh.new()
    CHROME, LENS_, BULB = range(3)
    for c, h in recesses:
        p, n = surface(tree, (c.x, -HALF - 1.0, c.z), (0, 1, 0))
        if p is None:
            continue
        if n.y > 0:
            n = -n
        n = (n + Vector((0, -1, 0))).normalized()
        r = min(0.42 * h, 0.04)
        cc = p + n * 0.003
        bowl(bm, cc, n, r * 1.18, 0.006, CHROME, segs=32, rim=0.004)     # bezel
        bowl(bm, cc - n * 0.004, n, r, r * 0.6, BULB, segs=32)            # reflector (lights up)
        dome(bm, cc - n * r * 0.25, n, 0.008, 0.012, BULB, segs=12)
        dome(bm, cc - n * 0.002, n, r, r * 0.12, LENS_, segs=32)          # clear lens
    bm_object("Laguna2_FogLamps", bm, ["laguna2_lamp_ring", "laguna2_lamp_clear", "laguna2_fog"], angle=40.0)


def build_parking_sensors(tree, m):
    bm = bmesh.new()
    z = (m.rstrip_bottom + m.rstrip_top) / 2
    for x in (-0.50, -0.17, 0.17, 0.50):
        p, n = surface(tree, (x, HALF + 1.0, z), (0, -1, 0))
        if p is None or S(p) < L - 0.4:
            continue
        if n.y < 0:
            n = -n
        bmesh.ops.create_cone(bm, cap_ends=True, segments=20, radius1=0.0105, radius2=0.0100, depth=0.004,
                              matrix=frame(p + n * 0.0012, n))
    bm_object("Laguna2_ParkingSensors", bm, ["laguna2_sensor"], angle=40.0)
    # Number-plate lights: two small clear lenses in the strip right above the plate.
    lb = bmesh.new()
    for x in (-0.13, 0.13):
        p, n = surface(tree, (x, HALF + 1.0, m.rstrip_bottom + 0.010), (0, -1, 0))
        if p is None or S(p) < L - 0.4:
            continue
        if n.y < 0:
            n = -n
        fr = frame(p + n * 0.0008, n)
        res = bmesh.ops.create_cube(lb, size=1.0, matrix=fr @ Matrix.Diagonal((0.050, 0.014, 0.0016, 1.0)))
        bmesh.ops.bevel(lb, geom=list({e for v in res["verts"] for e in v.link_edges}), offset=0.0006,
                        segments=1, affect="EDGES", clamp_overlap=True)
        res = bmesh.ops.create_cube(lb, size=1.0, matrix=fr @ Matrix.Translation((0, 0, 0.0012))
                                    @ Matrix.Diagonal((0.044, 0.009, 0.0008, 1.0)))
        for f in {f for v in res["verts"] for f in v.link_faces}:
            f.material_index = 1
    bm_object("Laguna2_PlateLights", lb, ["laguna2_lamp_ring", "laguna2_platelight"], angle=40.0)


def build_grille_backing(m):
    """Black panel behind the grille and lower intake so the nose is not see-through."""
    bm = bmesh.new()
    s = 0.36
    w = 0.64
    z0, z1 = m.floor_z + 0.08, m.hl_top - 0.02
    vs = [bm.verts.new(p) for p in ((-w, s - HALF, z0), (w, s - HALF, z0), (w, s - HALF, z1), (-w, s - HALF, z1))]
    f = bm.faces.new(vs)
    if f.normal.y > 0:
        f.normal_flip()
    bm_object("Laguna2_GrilleBacking", bm, ["laguna2_black"], angle=60.0)


# --------------------------------------------------------------------------
def make_light_materials():
    """One material per light function (see lights.py); emission off by default.

    The look here is the unlit lamp; the export adds the lit variants for BeamNG,
    render_lights.py turns the emission up for the night renders."""
    chrome = dict(color=(0.90, 0.90, 0.92), rough=0.06, metal=1.0)
    looks = {
        "laguna2_hl_low": chrome,
        "laguna2_hl_low_lens": dict(color=(0.55, 0.62, 0.70), rough=0.02, metal=0.3, alpha=0.85),
        "laguna2_hl_position": dict(color=(0.95, 0.95, 0.92), rough=0.05),
        "laguna2_hl_high": chrome,
        "laguna2_hl_signal_L": dict(color=(0.92, 0.86, 0.74), rough=0.08, metal=1.0),
        "laguna2_hl_signal_R": dict(color=(0.92, 0.86, 0.74), rough=0.08, metal=1.0),
        "laguna2_fog": chrome,
        "laguna2_repeater_L": dict(color=(0.95, 0.38, 0.02), rough=0.15, coat=1.0),
        "laguna2_repeater_R": dict(color=(0.95, 0.38, 0.02), rough=0.15, coat=1.0),
        "laguna2_tail_lens_red": dict(color=(0.78, 0.010, 0.018), rough=0.04, alpha=0.93, coat=1.0, idle=0.3),
        "laguna2_tail_reflector": dict(color=(0.75, 0.03, 0.04), rough=0.18, metal=0.6),
        "laguna2_tail_eye_red": dict(color=(0.42, 0.0, 0.01), rough=0.03, alpha=0.9, coat=1.0, idle=0.2),
        "laguna2_tail_fog": dict(color=(0.42, 0.0, 0.01), rough=0.03, alpha=0.9, coat=1.0, idle=0.2),
        "laguna2_tail_lens_smoked": dict(color=(0.16, 0.012, 0.016), rough=0.03, alpha=0.95, coat=1.0, idle=0.1),
        "laguna2_brake3": dict(color=(0.55, 0.008, 0.012), rough=0.05, coat=1.0),
        "laguna2_reverse": chrome,
        "laguna2_tail_signal_L": chrome,
        "laguna2_tail_signal_R": chrome,
        "laguna2_platelight": dict(color=(0.9, 0.9, 0.88), rough=0.1),
    }
    for name, (_fn, glow, _s1, _s2) in lights.GLOW.items():
        lk = looks[name]
        proc.mat(name, lk["color"], lk.get("rough", 0.3), lk.get("metal", 0.0), alpha=lk.get("alpha", 1.0),
                 coat=lk.get("coat", 0.0), emit=glow, emit_strength=lk.get("idle", 0.0))


def main():
    for block in (bpy.data.objects, bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
        for item in list(block):
            block.remove(item)
    proc.make_materials()
    proc.mat("laguna2_lamp_clear", (0.85, 0.88, 0.92), 0.02, 0.0, alpha=0.16, spec=0.8)
    proc.MATS["laguna2_lamp_housing"].node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.45
    proc.MATS["laguna2_lamp_housing"].node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.35
    proc.mat("laguna2_chrome_brushed", (0.80, 0.81, 0.83), 0.16, 1.0)
    proc.mat("laguna2_grille", (0.012, 0.012, 0.013), 0.35, spec=0.4)
    proc.mat("laguna2_grille_slat", (0.02, 0.02, 0.022), 0.22, spec=0.5)
    proc.mat("laguna2_projector", (0.55, 0.62, 0.70), 0.02, 0.3, alpha=0.85, spec=0.9)
    proc.mat("laguna2_bulb", (0.95, 0.95, 0.92), 0.05, 0.0, emit=(1.0, 0.97, 0.9), emit_strength=0.3)
    proc.mat("laguna2_tail_rim", (0.30, 0.0, 0.008), 0.06, 0.0, coat=1.0, emit=(0.4, 0.0, 0.0), emit_strength=0.1)
    proc.mat("laguna2_plate_blue", (0.01, 0.07, 0.45), 0.4)
    proc.mat("laguna2_tail_tube", (0.80, 0.04, 0.05), 0.12, 0.9, emit=(0.5, 0.0, 0.0), emit_strength=0.25)
    proc.mat("laguna2_badge_housing", (0.03, 0.03, 0.033), 0.15, 0.4, coat=1.0)
    proc.mat("laguna2_tail_lens_clear", (0.92, 0.90, 0.90), 0.05, 0.0, alpha=0.30, coat=1.0)
    proc.mat("laguna2_sensor", (0.02, 0.02, 0.022), 0.45, spec=0.3)

    make_light_materials()

    bm, slots = load_clean()
    slot = {name: i for i, name in enumerate(slots)}
    m = landmarks(bm, slot)
    prepare_paint(bm, slot, m)
    bm = subdivide_master(bm, slot)
    names = label_parts(bm, slot, m)
    build_panels(bm, slot, names)
    recesses, logos = build_details(bm, slot, m)
    bm.free()

    paint_parts = [o.name for o in bpy.data.objects if o.name.startswith("Laguna2_")
                   and o.data.materials and o.data.materials[0].name == "laguna2_paint"]
    tree = body_bvh(paint_parts)
    build_mirrors(tree, m)
    build_liners(m)
    build_underbody(m)
    build_plates(tree, m)
    build_grille_backing(m)
    build_badges(logos, body_bvh(paint_parts + ["Laguna2_Grille"]), tree, m)
    build_fog_lamps(body_bvh(["Laguna2_Trim", "Laguna2_Bumper_F"]), m, recesses)
    build_parking_sensors(body_bvh(["Laguna2_Trim"]), m)
    proc.build_interior()
    proc.build_wheels()

    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    tris = sum(len(p.vertices) - 2 for o in bpy.data.objects if o.type == "MESH" for p in o.data.polygons)
    print(f"[laguna2-ref] saved {BLEND_PATH}  objects={len(bpy.data.objects)} tris~{tris}")


if __name__ == "__main__":
    main()
