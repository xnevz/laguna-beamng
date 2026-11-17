"""Customisation variants for the Laguna II (run after build_from_ref.py).

Run:  blender --background blender/laguna2_liftback.blend --python tools/laguna2/variants.py

Splits the parts that become separate BeamNG options out of the shared meshes
and creates the alternative versions the parts selector can swap in:

    Laguna2_RearWiper            rear wiper (optional)            <- from Laguna2_Trim
    Laguna2_Mouldings            black side rubbing strips        <- from Laguna2_Trim
    Laguna2_Mouldings_Body       the same strips in body colour   (variant)
    Laguna2_Windscreen           always factory glass             <- from Laguna2_Glass
    Laguna2_Glass                side + rear glass, factory tint
    Laguna2_Glass_Privacy        darker rear / side glass          (variant)
    Laguna2_Glass_Dark           aftermarket dark film             (variant)
    Laguna2_Taillamp*_LensSmoked aftermarket smoked tail lenses    (variant)
    Laguna2_WheelAlloy           17" alloy + tyre at the origin    (wheel template)
    Laguna2_WheelSteel           15" steel wheel + Renault hubcap  (wheel template)

Variants and templates are hidden from renders (hide_render) so render.py
keeps showing the default car.  Saves the .blend in place.
"""

import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build as proc  # noqa: E402

VARIANT_OBJECTS = []


def mat(name, *args, **kw):
    """Get or create a material through build.py's helper (so look and export stay consistent)."""
    if name in bpy.data.materials:
        proc.MATS[name] = bpy.data.materials[name]
        return bpy.data.materials[name]
    return proc.mat(name, *args, **kw)


def link_mats(mesh, names):
    mesh.materials.clear()
    for n in names:
        mesh.materials.append(bpy.data.materials[n])


def split_faces(obj, test, new_name):
    """Move the faces of obj for which test(centre, normal) is true into a new object."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    keep = bmesh.new()
    keep.from_mesh(obj.data)
    take = [f for f in bm.faces if test(f.calc_center_median(), f.normal)]
    drop = [f for f in keep.faces if test(f.calc_center_median(), f.normal)]
    take_set = set(take)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f not in take_set], context="FACES")
    bmesh.ops.delete(keep, geom=drop, context="FACES")
    me = bpy.data.meshes.new(new_name)
    bm.to_mesh(me)
    bm.free()
    keep.to_mesh(obj.data)
    keep.free()
    for m in obj.data.materials:
        me.materials.append(m)
    new = bpy.data.objects.new(new_name, me)
    bpy.context.scene.collection.objects.link(new)
    new.matrix_world = obj.matrix_world.copy()
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    try:
        me.set_sharp_from_angle(angle=math.radians(35))
    except Exception:
        pass
    print(f"[variants] {new_name}: {len(take)} faces from {obj.name}")
    return new


def variant_copy(obj, new_name, remap):
    """Hidden copy of obj with some materials replaced ({old: new})."""
    me = obj.data.copy()
    me.name = new_name
    for i, m in enumerate(me.materials):
        if m is not None and m.name in remap:
            me.materials[i] = bpy.data.materials[remap[m.name]]
    new = bpy.data.objects.new(new_name, me)
    bpy.context.scene.collection.objects.link(new)
    new.matrix_world = obj.matrix_world.copy()
    new.hide_render = True
    VARIANT_OBJECTS.append(new)
    return new


# --------------------------------------------------------------------------
# Wheels
# --------------------------------------------------------------------------
def lathe(bm, profile, segs, mat_index, close_centre=False):
    rings = []
    for x, r in profile:
        if r <= 1e-6:
            rings.append([bm.verts.new((x, 0.0, 0.0))])
            continue
        rings.append([bm.verts.new((x, r * math.cos(2 * math.pi * i / segs), r * math.sin(2 * math.pi * i / segs)))
                      for i in range(segs)])
    for a, b in zip(rings[:-1], rings[1:]):
        if len(a) == 1:
            for i in range(segs):
                bm.faces.new((a[0], b[(i + 1) % segs], b[i])).material_index = mat_index
        elif len(b) == 1:
            for i in range(segs):
                bm.faces.new((a[i], a[(i + 1) % segs], b[0])).material_index = mat_index
        else:
            for i in range(segs):
                bm.faces.new((a[i], a[(i + 1) % segs], b[(i + 1) % segs], b[i])).material_index = mat_index
    return rings


def build_steel_wheel():
    """15" steel wheel, 195/65 R15 tyre, Renault plastic hubcap.  Axis = X, outer face = +X."""
    TIRE, STEEL, CAP, VENT, CHROME = range(5)
    bm = bmesh.new()
    R, hw, rr = 0.3175, 0.0975, 0.1905           # rolling radius, half tread width, bead seat radius
    tread = [(-0.074, R)]
    for gx in (-0.048, -0.016, 0.016, 0.048):
        tread += [(gx - 0.004, R), (gx - 0.0028, R - 0.007), (gx + 0.0028, R - 0.007), (gx + 0.004, R)]
    tread.append((0.074, R))
    prof = [(-0.086, rr), (-0.094, rr + 0.012), (-hw, rr + 0.05), (-0.097, R - 0.035), (-0.088, R - 0.012),
            (-0.078, R - 0.003)] + tread + [(0.078, R - 0.003), (0.088, R - 0.012), (0.097, R - 0.035),
                                             (hw, rr + 0.05), (0.094, rr + 0.012), (0.086, rr)]
    lathe(bm, prof, 72, TIRE)
    # Steel rim: flange, barrel, the pressed centre disc behind the hubcap.
    lathe(bm, [(0.086, rr), (0.092, rr + 0.004), (0.095, rr - 0.004), (0.088, rr - 0.012), (0.06, rr - 0.016),
               (-0.075, rr - 0.016), (-0.088, rr - 0.008), (-0.086, rr)], 64, STEEL)
    lathe(bm, [(0.02, rr - 0.016), (0.035, 0.12), (0.03, 0.06), (0.03, 0.0)], 48, STEEL)
    # Hubcap: shallow silver dome covering the rim face up to the flange.
    cap = [(0.090, 0.186), (0.096, 0.180), (0.100, 0.150), (0.104, 0.110), (0.107, 0.070), (0.109, 0.035),
           (0.110, 0.0)]
    lathe(bm, cap, 64, CAP)

    def cap_x(r):
        for (x0, r0), (x1, r1) in zip(cap[:-1], cap[1:]):
            if r1 <= r <= r0:
                t = (r0 - r) / (r0 - r1)
                return x0 + (x1 - x0) * t
        return cap[-1][0]

    # Ring of 14 dark cooling slots and a raised outer rim ring.
    for k in range(14):
        a0 = 2 * math.pi * k / 14 + 0.04
        a1 = a0 + 2 * math.pi / 14 * 0.55
        pts = []
        for r, a in ((0.112, a0), (0.112, a1), (0.165, a1 + 0.02), (0.165, a0 + 0.02)):
            pts.append(bm.verts.new((cap_x(r) + 0.0012, r * math.cos(a), r * math.sin(a))))
        bm.faces.new(pts).material_index = VENT
    lathe(bm, [(cap_x(0.172) + 0.0008, 0.172), (cap_x(0.172) + 0.004, 0.176), (cap_x(0.180) + 0.002, 0.180)],
          64, CAP)
    # Renault diamond in the centre.
    x = cap_x(0.0) + 0.0015
    outer = [(0, 0.030), (-0.022, 0), (0, -0.030), (0.022, 0)]
    vo = [bm.verts.new((x, y, z)) for y, z in outer]
    vi = [bm.verts.new((x + 0.002, y * 0.5, z * 0.5)) for y, z in outer]
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((vo[i], vo[j], vi[j], vi[i])).material_index = CHROME
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:                      # hubcap, slots and badge face outwards (+X)
        if f.material_index in (CAP, VENT, CHROME) and f.normal.x < 0:
            f.normal_flip()
    me = bpy.data.meshes.new("Laguna2_WheelSteel")
    link_mats(me, ["laguna2_tire", "laguna2_steelwheel", "laguna2_hubcap", "laguna2_black", "laguna2_chrome"])
    bm.to_mesh(me)
    bm.free()
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    me.set_sharp_from_angle(angle=math.radians(32))
    obj = bpy.data.objects.new("Laguna2_WheelSteel", me)
    bpy.context.scene.collection.objects.link(obj)
    obj.hide_render = True
    VARIANT_OBJECTS.append(obj)
    return obj


# --------------------------------------------------------------------------
def main():
    scene = bpy.context.scene
    objs = bpy.data.objects
    for o in [o for o in objs if o.name.startswith(("Laguna2_RearWiper", "Laguna2_Mouldings", "Laguna2_Windscreen",
                                                       "Laguna2_Glass_", "Laguna2_WheelAlloy", "Laguna2_WheelSteel"))
              or o.name.endswith("_LensSmoked")]:
        raise SystemExit("variants.py must run on a fresh build (variants already present: %s)" % o.name)

    mat("laguna2_glass_privacy", (0.003, 0.005, 0.005), 0.02, 0.0, alpha=0.92, spec=0.6)
    mat("laguna2_glass_dark", (0.001, 0.001, 0.0012), 0.02, 0.0, alpha=0.97, spec=0.6)
    mat("laguna2_steelwheel", (0.08, 0.08, 0.085), 0.45, 0.6)
    mat("laguna2_hubcap", (0.62, 0.64, 0.66), 0.32, 0.55, coat=0.4)
    mat("laguna2_tail_lens_smoked", (0.16, 0.012, 0.016), 0.03, 0.0, alpha=0.95, coat=1.0,
        emit=(1.0, 0.02, 0.02), emit_strength=0.1)

    trim = objs["Laguna2_Trim"]
    split_faces(trim, lambda c, n: c.y > 1.15 and c.z > 1.0 and abs(c.x) < 0.56, "Laguna2_RearWiper")
    moulding = split_faces(trim, lambda c, n: abs(c.x) > 0.80 and 0.45 < c.z < 0.75 and -1.0 < c.y < 1.1,
                           "Laguna2_Mouldings")
    variant_copy(moulding, "Laguna2_Mouldings_Body", {"laguna2_trim": "laguna2_paint", "laguna2_black": "laguna2_paint"})

    glass = objs["Laguna2_Glass"]
    split_faces(glass, lambda c, n: c.y < -0.15 and abs(c.x) < 0.66 and abs(n.x) < 0.6, "Laguna2_Windscreen")
    variant_copy(glass, "Laguna2_Glass_Privacy", {"laguna2_glass": "laguna2_glass_privacy"})
    variant_copy(glass, "Laguna2_Glass_Dark", {"laguna2_glass": "laguna2_glass_dark"})

    for o in [o for o in objs if o.name.startswith("Laguna2_Taillamp") and o.name.endswith("_Lens")]:
        variant_copy(o, o.name + "Smoked", {"laguna2_tail_lens_red": "laguna2_tail_lens_smoked"})

    # Wheel templates at the origin (the four placed wheels stay for the renders).
    alloy = bpy.data.objects.new("Laguna2_WheelAlloy", objs["Laguna2_Wheel_FL"].data)
    scene.collection.objects.link(alloy)
    alloy.hide_render = True
    VARIANT_OBJECTS.append(alloy)
    build_steel_wheel()

    bpy.ops.wm.save_mainfile()
    print(f"[variants] saved; {len(VARIANT_OBJECTS)} hidden variant/template objects")


if __name__ == "__main__":
    main()
