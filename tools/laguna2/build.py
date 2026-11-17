"""Renault Laguna II (phase 1) liftback - clean procedural build.

Run:  blender --background --factory-startup --python tools/laguna2/build.py

Authoring coordinates: x = lateral (left of car = +x), s = distance from the
front bumper tip (0..L), z = height above ground.  Blender Y = s - L/2, so
the car faces -Y like the rest of this project.
"""

import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import delaunay_2d_cdt

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(HERE))
BLEND_PATH = os.path.join(PROJECT_ROOT, "blender", "laguna2_liftback.blend")

L = 4.576
HALF = L / 2.0
AXLE_F = 0.965
AXLE_R = 0.985 + 2.748
WHEEL_R = 0.317
ARCH_R = 0.355
TRACK_F = 0.757
TRACK_R = 0.745


def B(x, s, z):
    return Vector((x, s - HALF, z))


# --------------------------------------------------------------------------
# Curves
# --------------------------------------------------------------------------
def pchip(keys):
    xs = np.array([k[0] for k in keys], float)
    ys = np.array([k[1] for k in keys], float)
    h = np.diff(xs)
    d = np.diff(ys) / h
    m = np.zeros_like(xs)
    m[0], m[-1] = d[0], d[-1]
    for i in range(1, len(xs) - 1):
        if d[i - 1] * d[i] <= 0:
            m[i] = 0.0
        else:
            w1 = 2 * h[i] + h[i - 1]
            w2 = h[i] + 2 * h[i - 1]
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])

    def f(x):
        x = float(min(max(x, xs[0]), xs[-1]))
        i = int(min(max(np.searchsorted(xs, x, side="right") - 1, 0), len(xs) - 2))
        t = (x - xs[i]) / h[i]
        return float(
            (2 * t**3 - 3 * t**2 + 1) * ys[i]
            + (t**3 - 2 * t**2 + t) * h[i] * m[i]
            + (-2 * t**3 + 3 * t**2) * ys[i + 1]
            + (t**3 - t**2) * h[i] * m[i + 1]
        )

    return f


def smoothstep(a, b, x):
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3 - 2 * t)


# Silhouette (centreline top), underside, shoulder, plan width.
ZT = pchip([
    (0.0, 0.56), (0.04, 0.59), (0.09, 0.625), (0.17, 0.705), (0.24, 0.745), (0.5, 0.845),
    (0.9, 0.928), (1.05, 0.957), (1.13, 0.978), (1.4, 1.13),
    (1.7, 1.275), (1.95, 1.355), (2.2, 1.405), (2.6, 1.429), (2.9, 1.425),
    (3.2, 1.405), (3.4, 1.37), (3.6, 1.325), (3.8, 1.28), (4.0, 1.225), (4.2, 1.16),
    (4.33, 1.115), (4.40, 1.095), (4.435, 1.082), (4.455, 1.06), (4.49, 0.95),
    (4.52, 0.75), (4.54, 0.665), (4.576, 0.62),
])
ZB = pchip([
    (0.0, 0.27), (0.06, 0.255), (0.3, 0.25), (0.9, 0.24), (1.35, 0.212), (3.3, 0.212),
    (3.75, 0.245), (4.2, 0.258), (4.5, 0.268), (4.576, 0.29),
])
ZBELT = pchip([
    (0.0, 0.52), (0.05, 0.565), (0.15, 0.66), (0.3, 0.74), (0.5, 0.80), (0.9, 0.868),
    (1.25, 0.895), (1.6, 0.905), (2.5, 0.935), (3.4, 0.962), (3.6, 0.978),
    (3.9, 0.985), (4.2, 0.975), (4.4, 0.958), (4.576, 0.94),
])
CROWN = pchip([
    (0.0, 0.02), (0.3, 0.035), (1.0, 0.04), (1.25, 0.045), (1.6, 0.06),
    (2.0, 0.06), (2.5, 0.055), (3.2, 0.06), (3.8, 0.06), (4.2, 0.04),
    (4.576, 0.025),
])
INSET = pchip([
    (0.0, 0.11), (0.95, 0.13), (1.13, 0.15), (1.33, 0.185), (1.6, 0.228),
    (1.95, 0.238), (2.5, 0.242), (3.0, 0.242), (3.4, 0.242), (3.8, 0.235),
    (4.1, 0.21), (4.3, 0.15), (4.576, 0.12),
])
WB = pchip([
    (0.0, 0.855), (0.55, 0.868), (1.0, 0.878), (1.6, 0.886), (2.8, 0.886),
    (3.7, 0.880), (4.2, 0.866), (4.576, 0.852),
])
CAP_F = (0.55, 2.6)
CAP_R = (0.60, 2.6)


def endcap(s):
    a, n = CAP_F
    if s < a:
        return max(1.0 - (1.0 - s / a) ** n, 0.0) ** (1.0 / n)
    a, n = CAP_R
    if s > L - a:
        return max(1.0 - (1.0 - (L - s) / a) ** n, 0.0) ** (1.0 / n)
    return 1.0


def params(s):
    k = endcap(s)
    w = WB(s) * k
    zt, zb = ZT(s), ZB(s)
    zr = zt - CROWN(s) * (0.3 + 0.7 * k)
    zbelt = min(ZBELT(s), zr - 0.012)
    wr = w - INSET(s) * k
    wbelt = w - 0.045 * k
    return dict(k=k, w=w, zt=zt, zb=zb, zr=zr, zbelt=zbelt, wr=wr, wbelt=wbelt)


def zrail(s):
    return params(s)["zr"]


def zbelt(s):
    return params(s)["zbelt"]


def wrail(s):
    return params(s)["wr"]


SEG_COUNTS = [8, 8, 6, 6, 5, 10, 12, 8, 3, 4, 4]
UNDER_FROM = sum(SEG_COUNTS[:9])


def _crseg(p0, p1, p2, p3, n):
    def tj(ti, a, b):
        return ti + max(float(np.linalg.norm(b - a)), 1e-6) ** 0.5

    t0 = 0.0
    t1 = tj(t0, p0, p1)
    t2 = tj(t1, p1, p2)
    t3 = tj(t2, p2, p3)
    t = (t1 + np.linspace(0, 1, n, endpoint=False) * (t2 - t1))[:, None]
    a1 = (t1 - t) / (t1 - t0) * p0 + (t - t0) / (t1 - t0) * p1
    a2 = (t2 - t) / (t2 - t1) * p1 + (t - t1) / (t2 - t1) * p2
    a3 = (t3 - t) / (t3 - t2) * p2 + (t - t2) / (t3 - t2) * p3
    b1 = (t2 - t) / (t2 - t0) * a1 + (t - t0) / (t2 - t0) * a2
    b2 = (t3 - t) / (t3 - t1) * a2 + (t - t1) / (t3 - t1) * a3
    return (t2 - t) / (t2 - t1) * b1 + (t - t1) / (t2 - t1) * b2


def section(s):
    p = params(s)
    k, w, zt, zb, zr, zbl, wr, wbelt = (
        p["k"], p["w"], p["zt"], p["zb"], p["zr"], p["zbelt"], p["wr"], p["wbelt"],
    )
    hside = zbl - zb
    pts = np.array([
        (0.0, zt),
        (0.60 * wr, zt - 0.34 * (zt - zr)),
        (wr, zr),
        (0.5 * (wr + wbelt) + 0.014 * k, 0.5 * (zr + zbl) + 0.004),
        (wbelt, zbl),
        (w - 0.005 * k, zbl - 0.11 * hside),
        (w, zb + 0.50 * hside),
        (w - 0.015 * k, zb + 0.20 * hside),
        (w - 0.05 * k, zb + 0.035),
        (w - 0.13 * k, zb),
        (0.5 * (w - 0.13 * k), zb),
        (0.0, zb),
    ])
    mirror = np.array([-1.0, 1.0])
    q = np.vstack([pts[1] * mirror, pts, pts[-2] * mirror])
    out = [_crseg(q[i], q[i + 1], q[i + 2], q[i + 3], SEG_COUNTS[i]) for i in range(len(pts) - 1)]
    out.append(pts[-1][None])
    arr = np.vstack(out)
    arr[:, 0] = np.maximum(arr[:, 0], 0.0)
    arr[0, 0] = 0.0
    arr[-1, 0] = 0.0
    return arr


def stations():
    out = []
    a, n = CAP_F
    for j in range(46):
        phi = 0.035 + (math.pi / 2 - 0.035) * (j / 45.0) ** 1.15
        out.append(a * (1.0 - math.cos(phi) ** (2.0 / n)))
    a2, n2 = CAP_R
    mid = np.linspace(a, L - a2, 170)
    out.extend(mid[1:-1].tolist())
    for j in range(46):
        phi = 0.035 + (math.pi / 2 - 0.035) * (j / 45.0) ** 1.15
        out.append(L - a2 * (1.0 - math.cos(phi) ** (2.0 / n2)))
    out.extend(np.arange(4.36, 4.56, 0.004).tolist())
    out = sorted(out)
    res = [out[0]]
    for v in out[1:]:
        if v - res[-1] > 0.0022:
            res.append(v)
    return res


# --------------------------------------------------------------------------
# Materials
# --------------------------------------------------------------------------
MATS = {}


def mat(name, color, rough=0.5, metal=0.0, alpha=1.0, coat=0.0, emit=None, emit_strength=0.0, spec=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.diffuse_color = (color[0], color[1], color[2], alpha)
    sh = m.node_tree.nodes.get("Principled BSDF")
    sh.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    sh.inputs["Roughness"].default_value = rough
    sh.inputs["Metallic"].default_value = metal
    sh.inputs["Alpha"].default_value = alpha
    for key, val in (("Coat Weight", coat), ("Coat Roughness", 0.04)):
        if key in sh.inputs:
            sh.inputs[key].default_value = val
    if spec is not None and "Specular IOR Level" in sh.inputs:
        sh.inputs["Specular IOR Level"].default_value = spec
    if emit is not None:
        for key in ("Emission Color", "Emission"):
            if key in sh.inputs:
                sh.inputs[key].default_value = (emit[0], emit[1], emit[2], 1.0)
                break
        if "Emission Strength" in sh.inputs:
            sh.inputs["Emission Strength"].default_value = emit_strength
    if alpha < 1.0:
        try:
            m.surface_render_method = "BLENDED"
        except Exception:
            pass
        try:
            m.use_transparency_overlap = False
        except Exception:
            pass
    MATS[name] = m
    return m


def make_materials():
    mat("laguna2_paint", (0.44, 0.385, 0.27), 0.34, 0.55, coat=1.0)
    mat("laguna2_black", (0.005, 0.005, 0.006), 0.6, spec=0.12)
    mat("laguna2_trim", (0.018, 0.019, 0.021), 0.55, spec=0.3)
    mat("laguna2_gap", (0.003, 0.003, 0.004), 0.9, spec=0.1)
    mat("laguna2_glass", (0.006, 0.014, 0.015), 0.02, 0.0, alpha=0.80, spec=0.6)
    mat("laguna2_interior", (0.035, 0.035, 0.038), 0.85, spec=0.2)
    mat("laguna2_seat", (0.22, 0.20, 0.165), 0.9, spec=0.2)
    mat("laguna2_chrome", (0.92, 0.93, 0.95), 0.06, 1.0)
    mat("laguna2_lamp_housing", (0.70, 0.72, 0.75), 0.30, 0.5)
    mat("laguna2_lamp_ring", (0.9, 0.9, 0.92), 0.08, 1.0)
    mat("laguna2_lamp_lens", (0.30, 0.34, 0.40), 0.12, 0.5)
    mat("laguna2_tail_red", (0.55, 0.008, 0.012), 0.08, 0.0, coat=1.0, emit=(0.6, 0.0, 0.0), emit_strength=0.25)
    mat("laguna2_tail_clear", (0.50, 0.30, 0.30), 0.10, 0.5, coat=1.0)
    mat("laguna2_amber", (0.95, 0.38, 0.02), 0.15, 0.0, coat=1.0)
    mat("laguna2_plate_white", (0.88, 0.88, 0.85), 0.5)
    mat("laguna2_plate_yellow", (0.90, 0.68, 0.05), 0.5)
    mat("laguna2_alloy", (0.78, 0.79, 0.80), 0.22, 1.0, coat=0.6)
    mat("laguna2_alloy_dark", (0.10, 0.10, 0.11), 0.5, 0.8)
    mat("laguna2_tire", (0.012, 0.012, 0.013), 0.8, spec=0.25)
    mat("laguna2_disc", (0.16, 0.16, 0.17), 0.5, 1.0)
    mat("laguna2_mirror", (0.75, 0.80, 0.85), 0.02, 1.0)


# --------------------------------------------------------------------------
# Mesh helpers
# --------------------------------------------------------------------------
def shade(mesh, angle=40.0):
    mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))
    try:
        mesh.set_sharp_from_angle(angle=math.radians(angle))
    except Exception as exc:  # pragma: no cover
        print("[warn] set_sharp_from_angle:", exc)
    mesh.update()


def new_obj(name, verts, faces, mats, face_mats=None, smooth=40.0, recalc=False):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([tuple(v) for v in verts], [], faces)
    for m in mats:
        mesh.materials.append(MATS[m] if isinstance(m, str) else m)
    if face_mats is not None:
        mesh.polygons.foreach_set("material_index", face_mats)
    mesh.update()
    if recalc:
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(mesh)
        bm.free()
    if smooth:
        shade(mesh, smooth)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def bm_obj(name, bm, mats, smooth=40.0):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    for m in mats:
        mesh.materials.append(MATS[m])
    if smooth:
        shade(mesh, smooth)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def box(name, center, size, m, bevel=0.02, rot_x=0.0, segments=3):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=bm.edges[:], offset=bevel, segments=segments, profile=0.5, affect="EDGES")
    if rot_x:
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(rot_x, 3, "X"), verts=bm.verts)
    bmesh.ops.translate(bm, vec=Vector(center), verts=bm.verts)
    return bm_obj(name, bm, [m], smooth=35.0)


# --------------------------------------------------------------------------
# 2D polygon helpers
# --------------------------------------------------------------------------
def pip(pt, poly):
    x, y = pt
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def chaikin(poly, iters=2):
    pts = [tuple(p) for p in poly]
    for _ in range(iters):
        out = []
        n = len(pts)
        for i in range(n):
            a = pts[i]
            b = pts[(i + 1) % n]
            out.append((0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]))
            out.append((0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1]))
        pts = out
    return pts


def densify(poly, seg, closed=True):
    out = []
    n = len(poly)
    last = n if closed else n - 1
    for i in range(last):
        a = poly[i]
        b = poly[(i + 1) % n]
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        k = max(1, int(math.ceil(d / seg)))
        for j in range(k):
            t = j / k
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    if not closed:
        out.append(tuple(poly[-1]))
    # drop near-duplicate points
    res = []
    for p in out:
        if not res or math.hypot(p[0] - res[-1][0], p[1] - res[-1][1]) > 1e-5:
            res.append(p)
    if closed and len(res) > 2 and math.hypot(res[0][0] - res[-1][0], res[0][1] - res[-1][1]) < 1e-5:
        res.pop()
    return res


def area(poly):
    return 0.5 * sum(
        poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
        for i in range(len(poly))
    )


def offset_poly(poly, d):
    """Inset (d > 0) a smooth polygon."""
    pts = densify(poly, 0.02)
    sign = 1.0 if area(pts) > 0 else -1.0
    n = len(pts)
    out = []
    for i in range(n):
        p0 = pts[i - 1]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        tx, ty = p2[0] - p0[0], p2[1] - p0[1]
        ln = math.hypot(tx, ty) or 1.0
        nx, ny = -ty / ln * sign, tx / ln * sign
        out.append((p1[0] + nx * d, p1[1] + ny * d))
    # remove self-intersection artefacts at tight tips: keep points still d inside
    keep = [p for p in out if pip(p, pts) == (d > 0)]
    return keep if len(keep) >= 3 else out


def strip(poly_line, width):
    """Polygon around an open polyline."""
    pts = densify(poly_line, 0.015, closed=False)
    left, right = [], []
    n = len(pts)
    for i in range(n):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, n - 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(tx, ty) or 1.0
        nx, ny = -ty / ln, tx / ln
        left.append((pts[i][0] + nx * width / 2, pts[i][1] + ny * width / 2))
        right.append((pts[i][0] - nx * width / 2, pts[i][1] - ny * width / 2))
    return left + right[::-1]


def rrect(cx, cy, w, h, r, n=6):
    pts = []
    for (sx, sy, a0) in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)):
        ox = cx + sx * (w / 2 - r)
        oy = cy + sy * (h / 2 - r)
        for j in range(n + 1):
            a = math.radians(a0 + 90.0 * j / n)
            pts.append((ox + r * math.cos(a), oy + r * math.sin(a)))
    return pts


def circle(cx, cy, r, n=28):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


# --------------------------------------------------------------------------
# Projectors: 2D feature coordinates -> ray onto the body
# --------------------------------------------------------------------------
R0 = 0.6


def proj_side(sign=1.0):
    return lambda a, b: (Vector((sign * 3.0, a - HALF, b)), Vector((-sign, 0, 0)))


def proj_top():
    return lambda a, b: (Vector((a, b - HALF, 3.0)), Vector((0, 0, -1)))


def proj_front():
    return lambda a, b: (Vector((a, -HALF - 1.0, b)), Vector((0, 1, 0)))


def proj_rear():
    return lambda a, b: (Vector((a, HALF + 1.0, b)), Vector((0, -1, 0)))


def proj_cyl(front=True):
    yc = (0.6 - HALF) if front else (HALF - 0.6)
    sy = -1.0 if front else 1.0

    def f(a, b):
        th = a / R0
        d = Vector((math.sin(th), sy * math.cos(th), 0.0))
        return (Vector((0, yc, b)) + d * 3.0, -d)

    return f


def FX(x):
    return math.atan2(x, 0.58) * R0


def FS(s):
    return math.atan2(0.85, 0.6 - s) * R0


def RX(x):
    return math.atan2(x, 0.535) * R0


def RS(s):
    return math.atan2(0.85, s - (L - 0.6)) * R0


BODY_BVH = None
GATE = {"x": 0.50, "z": 1.09}


def cast(proj, a, b):
    origin, direction = proj(a, b)
    loc, normal, _idx, _dist = BODY_BVH.ray_cast(origin, direction, 10.0)
    if loc is None:
        return None
    if normal.dot(direction) > 0:
        normal = -normal
    return loc, normal


def build_patch(name, outline, proj, mats, zones=(), holes=(), offset=0.003, res=0.03,
                skirt=False, mirror=False, smooth=50.0):
    """Triangulate a 2D outline and drape it onto the body surface.

    zones: [(polygon, material_index or None)] applied in order (None = hole).
    """
    seg = res * 0.6
    loops = [densify(outline, seg)]
    loops += [densify(h, seg) for h in holes]
    loops += [densify(z[0], seg) for z in zones]
    verts, edges = [], []
    for lp in loops:
        base = len(verts)
        verts.extend(lp)
        edges.extend((base + i, base + (i + 1) % len(lp)) for i in range(len(lp)))
    seg_a = np.array([verts[e[0]] for e in edges])
    seg_b = np.array([verts[e[1]] for e in edges])
    xs = [p[0] for p in loops[0]]
    ys = [p[1] for p in loops[0]]
    gx = np.arange(min(xs) + res * 0.5, max(xs), res)
    gy = np.arange(min(ys) + res * 0.5, max(ys), res)
    ab = seg_b - seg_a
    ab2 = np.maximum((ab**2).sum(1), 1e-12)
    for row, y in enumerate(gy):
        shift = res * 0.5 if row % 2 else 0.0
        for x in gx:
            p = np.array((x + shift, y))
            if not pip(p, loops[0]):
                continue
            t = np.clip(((p - seg_a) * ab).sum(1) / ab2, 0, 1)
            dist = np.sqrt((((seg_a + ab * t[:, None]) - p) ** 2).sum(1)).min()
            if dist < res * 0.45:
                continue
            verts.append((float(p[0]), float(p[1])))
    result = delaunay_2d_cdt([Vector(v) for v in verts], edges, [], 0, 1e-7)
    out_verts, out_faces = result[0], result[2]

    hits = [cast(proj, v.x, v.y) for v in out_verts]
    tris, tri_mats = [], []
    for f in out_faces:
        if len(f) != 3 or any(hits[i] is None for i in f):
            continue
        c = (
            (out_verts[f[0]].x + out_verts[f[1]].x + out_verts[f[2]].x) / 3.0,
            (out_verts[f[0]].y + out_verts[f[1]].y + out_verts[f[2]].y) / 3.0,
        )
        if not pip(c, loops[0]) or any(pip(c, h) for h in holes):
            continue
        mi = 0
        for poly, idx in zones:
            if pip(c, poly):
                mi = idx
        if mi is None:
            continue
        p0, p1, p2 = (hits[i][0] for i in f)
        limit = max(0.30, 8.0 * res)
        if max((p1 - p0).length, (p2 - p1).length, (p0 - p2).length) > limit:
            continue
        nrm = (p1 - p0).cross(p2 - p0)
        if nrm.dot(hits[f[0]][1] + hits[f[1]][1] + hits[f[2]][1]) < 0:
            f = (f[0], f[2], f[1])
        tris.append(tuple(f))
        tri_mats.append(mi)

    pos = [(h[0] + h[1] * offset) if h else Vector((0, 0, 0)) for h in hits]
    faces = list(tris)
    fmats = list(tri_mats)
    if skirt:
        count = {}
        for ti, f in enumerate(tris):
            for k in range(3):
                e = (f[k], f[(k + 1) % 3])
                count.setdefault(tuple(sorted(e)), []).append((e, ti))
        base_map = {}
        for key, uses in count.items():
            if len(uses) != 1:
                continue
            (i, j), ti = uses[0]
            for v in (i, j):
                if v not in base_map:
                    base_map[v] = len(pos)
                    pos.append(hits[v][0] - hits[v][1] * 0.002)
            faces.append((j, i, base_map[i], base_map[j]))
            fmats.append(tri_mats[ti])
    if mirror:
        n = len(pos)
        pos = pos + [Vector((-p.x, p.y, p.z)) for p in pos]
        faces = faces + [tuple(n + i for i in reversed(f)) for f in faces]
        fmats = fmats + fmats
    if not faces:
        print("[warn] empty patch", name)
        return None
    return new_obj(name, pos, faces, mats, fmats, smooth=smooth)


# --------------------------------------------------------------------------
# Body
# --------------------------------------------------------------------------
def build_body_mesh():
    st = stations()
    rings = []
    verts = []
    faces = []
    fmats = []
    half_n = None
    for s in st:
        sec = section(s)
        half_n = len(sec)
        ring = [(x, s - HALF, z) for x, z in sec]
        ring += [(-x, s - HALF, z) for x, z in sec[-2:0:-1]]
        rings.append(len(verts))
        verts.extend(ring)
    m = 2 * half_n - 2
    for i in range(len(st) - 1):
        a0, b0 = rings[i], rings[i + 1]
        for j in range(m):
            j2 = (j + 1) % m
            faces.append((a0 + j, a0 + j2, b0 + j2, b0 + j))
            h = min(j, m - 1 - j)
            fmats.append(1 if h >= UNDER_FROM else 0)
    faces.append(tuple(rings[0] + j for j in range(m)))
    fmats.append(0)
    faces.append(tuple(rings[-1] + j for j in reversed(range(m))))
    fmats.append(0)
    return verts, faces, fmats


def prism_side(bm, poly, x0=0.30, x1=1.4):
    for sign in (1.0, -1.0):
        a = [bm.verts.new((sign * x0, s - HALF, z)) for s, z in poly]
        b = [bm.verts.new((sign * x1, s - HALF, z)) for s, z in poly]
        _prism_faces(bm, a, b)


def prism_top(bm, poly, z0=0.62, z1=1.9):
    a = [bm.verts.new((x, s - HALF, z0)) for x, s in poly]
    b = [bm.verts.new((x, s - HALF, z1)) for x, s in poly]
    _prism_faces(bm, a, b)


def _prism_faces(bm, a, b):
    n = len(a)
    bm.faces.new(a)
    bm.faces.new(b)
    for i in range(n):
        bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))


def cutter_object(name, bm):
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def boolean_cut(obj, cutter):
    """Difference with solver fallback; keeps the original if every solver collapses the mesh."""
    n_before = len(obj.data.polygons)
    result = None
    for solver in ("EXACT", "MANIFOLD", "FLOAT"):
        mod = obj.modifiers.new("cut", "BOOLEAN")
        mod.operation = "DIFFERENCE"
        mod.object = cutter
        try:
            mod.solver = solver
        except Exception:
            obj.modifiers.remove(mod)
            continue
        dg = bpy.context.evaluated_depsgraph_get()
        dg.update()
        new_mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
        obj.modifiers.remove(mod)
        if len(new_mesh.polygons) > 0.6 * n_before:
            result = new_mesh
            if solver != "EXACT":
                print(f"[laguna2] boolean fell back to {solver}")
            break
        bpy.data.meshes.remove(new_mesh)
    bpy.data.objects.remove(cutter, do_unlink=True)
    if result is None:
        print("[warn] boolean cut failed with every solver")
        return False
    old = obj.data
    obj.data = result
    bpy.data.meshes.remove(old)
    return True


def far_faces(mesh, bvh, tol=0.003):
    """Faces created by a cutter (walls/caps): they own a vertex that is off the original skin.
    Original skin faces only ever have vertices on original edges, so they never qualify."""
    vdist = []
    for v in mesh.vertices:
        loc, _n, _i, dist = bvh.find_nearest(v.co)
        vdist.append(1.0 if loc is None else dist)
    return [max(vdist[i] for i in poly.vertices) > tol for poly in mesh.polygons]


# --- feature outlines shared by cut-outs and trim -------------------------
DLO_END = 3.54


def band_poly(s0, s1, mb, mt, n=90, slant=None):
    """Side-glass band between the belt and the roof rail.  Behind s=3.1 the
    top edge sweeps down to the belt, giving the small triangular quarter light."""
    shift = (mt - 0.04) * 1.4
    pts_b, pts_t = [], []
    for s in np.linspace(s0, s1, n):
        s = float(s)
        zb_ = zbelt(s) + mb
        zt_ = zrail(s) - mt
        t = min(max((s + shift - 3.27) / (DLO_END - 3.27), 0.0), 1.0) ** 1.15
        zt_ = zt_ + (zb_ + 0.008 - zt_) * t
        if zt_ - zb_ < 0.006:
            continue
        sb_, st_ = s, s
        if slant is not None:
            sb_ = max(s, slant)
            st_ = max(s, slant - 0.55 * (zt_ - zb_))
        pts_b.append((sb_, zb_))
        pts_t.append((st_, zt_))
    return pts_b + pts_t[::-1]


def windscreen_outline():
    def sb(x):
        return 1.15 + 0.20 * (abs(x) / 0.72) ** 2.4

    def st(x):
        return 2.03 - 0.045 * (abs(x) / 0.58) ** 2

    def xmax(s):
        return wrail(s) - 0.035

    lo = next(s for s in np.arange(1.13, 1.7, 0.002) if sb(xmax(s)) <= s)
    hi = next(s for s in np.arange(2.1, 1.7, -0.002) if st(xmax(s)) >= s)
    right = [(xmax(float(s)), float(s)) for s in np.linspace(lo, hi, 24)]
    top = [(x, st(x)) for x in np.linspace(right[-1][0], -right[-1][0], 30)[1:-1]]
    left = [(-x, s) for x, s in right[::-1]]
    bottom = [(x, sb(x)) for x in np.linspace(-right[0][0], right[0][0], 40)[1:-1]]
    return chaikin(right + top + left + bottom, 2), sb


def rear_glass_outline():
    """Wrap-around rear screen (measured from the FBX reference and the side photo).

    Seen from the side it shows as a dark band under the roof line from s~3.55
    down to the tail; its bottom edge is the top of the tailgate face."""
    def st(x):
        return 3.40 + 0.15 * (abs(x) / 0.6) ** 3

    def sb(x):
        return 4.39 - 0.06 * (abs(x) / 0.5) ** 4

    def xmax(s):
        wrap = 0.05 * smoothstep(3.45, 3.80, s)
        x = wrail(s) + wrap
        return x + (0.50 - x) * smoothstep(3.98, 4.34, s)

    lo = next(s for s in np.arange(3.2, 3.8, 0.002) if st(xmax(s)) <= s)
    hi = next(s for s in np.arange(4.5, 3.9, -0.002) if sb(xmax(s)) >= s)
    right = [(xmax(float(s)), float(s)) for s in np.linspace(lo, hi, 40)]
    bottom = [(x, sb(x)) for x in np.linspace(right[-1][0], -right[-1][0], 30)[1:-1]]
    left = [(-x, s) for x, s in right[::-1]]
    top = [(x, st(x)) for x in np.linspace(-right[0][0], right[0][0], 30)[1:-1]]
    return chaikin(right + bottom + left + top, 3), st, sb, xmax


def side_panes():
    front = chaikin(band_poly(1.42, 2.49, 0.022, 0.062, n=40, slant=1.66), 1)
    rear = chaikin(band_poly(2.66, 3.262, 0.022, 0.062, n=40), 1)
    quarter = chaikin(band_poly(3.298, DLO_END, 0.022, 0.062, n=40), 1)
    return [front, rear, quarter]


def build_body():
    global BODY_BVH
    verts, faces, fmats = build_body_mesh()
    shaped = []
    for x, y, z in verts:
        s = y + HALF
        if 0.18 < s < 1.13 and z > zbelt(s) - 0.01:
            xv = 0.07 + 0.50 * smoothstep(0.18, 1.12, s) ** 0.85
            z += 0.014 * smoothstep(xv + 0.028, xv - 0.028, abs(x)) * smoothstep(0.18, 0.30, s) * smoothstep(1.13, 1.02, s)
        taper = smoothstep(L - 0.55, L, s) * smoothstep(0.62, 1.05, z)
        x *= 1.0 - 0.075 * taper
        y -= 0.025 * taper * smoothstep(0.35, 0.85, abs(x))
        shaped.append((x, y, z))
    verts = shaped
    BODY_BVH = BVHTree.FromPolygons([Vector(v) for v in verts], faces)
    body = new_obj(
        "Laguna2_Body", verts, faces,
        ["laguna2_paint", "laguna2_black", "laguna2_interior", "laguna2_trim", "laguna2_black"],
        fmats, smooth=0, recalc=True,
    )

    # Wheel arches: solid difference leaves real wheel wells.
    bm = bmesh.new()
    for s_axle in (AXLE_F, AXLE_R):
        for sign in (1.0, -1.0):
            res = bmesh.ops.create_cone(
                bm, cap_ends=True, segments=72, radius1=ARCH_R, radius2=ARCH_R, depth=1.0,
                matrix=Matrix.Translation((sign * 0.95, s_axle - HALF, WHEEL_R - 0.005))
                @ Matrix.Rotation(math.radians(90), 4, "Y"),
            )
            del res
    boolean_cut(body, cutter_object("cut_arches", bm))
    print("[laguna2] after arches:", len(body.data.polygons))
    far = far_faces(body.data, BODY_BVH)
    for poly, is_far in zip(body.data.polygons, far):
        sc = poly.center.y + HALF
        near_arch = min(abs(sc - AXLE_F), abs(sc - AXLE_R)) < ARCH_R + 0.03 and poly.center.z < 0.72
        if is_far and near_arch:
            poly.material_index = 1

    # Glass openings.
    ws, _sb = windscreen_outline()
    rg = rear_glass_outline()[0]
    cuts = [("windscreen", "top", offset_poly(ws, 0.032)), ("rear glass", "top", offset_poly(rg, 0.038))]
    cuts += [(f"side pane {i}", "side", pane) for i, pane in enumerate(side_panes())]
    for label, kind, poly in cuts:
        bm = bmesh.new()
        (prism_top if kind == "top" else prism_side)(bm, densify(poly, 0.03))
        ok = boolean_cut(body, cutter_object("cut_glass", bm))
        print(f"[laguna2] cut {label}: {'ok' if ok else 'FAILED'} ({len(body.data.polygons)} polys)")
    far = far_faces(body.data, BODY_BVH)
    bm = bmesh.new()
    bm.from_mesh(body.data)
    bm.faces.ensure_lookup_table()
    doomed = [f for f, is_far in zip(bm.faces, far) if is_far and f.material_index != 1]
    bmesh.ops.delete(bm, geom=doomed, context="FACES")
    bm.to_mesh(body.data)
    bm.free()

    # Inner skin so the cabin is dark when seen through the glass.
    mod = body.modifiers.new("inner", "SOLIDIFY")
    mod.thickness = 0.016
    mod.offset = -1.0
    mod.use_rim = True
    mod.use_even_offset = False
    mod.material_offset = 2
    mod.material_offset_rim = 3
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    new_mesh = bpy.data.meshes.new_from_object(body.evaluated_get(dg))
    body.modifiers.remove(mod)
    old = body.data
    body.data = new_mesh
    bpy.data.meshes.remove(old)
    shade(body.data, 38.0)
    return body


# --------------------------------------------------------------------------
# Glass and dark trim
# --------------------------------------------------------------------------
def build_glass():
    top = proj_top()
    ws, sb = windscreen_outline()
    build_patch("Laguna2_Windscreen", ws, top, ["laguna2_black", "laguna2_glass"],
                zones=[(offset_poly(ws, 0.03), 1)], offset=0.003, res=0.035)
    rg, st, rsb, xmax = rear_glass_outline()
    build_patch("Laguna2_RearGlass", rg, top, ["laguna2_black", "laguna2_glass"],
                zones=[(offset_poly(rg, 0.036), 1)], offset=0.003, res=0.035)

    # Cowl panel and wipers.
    cowl = [(x, sb(x) - 0.085) for x in np.linspace(-0.70, 0.70, 40)]
    cowl += [(x, sb(x) + 0.012) for x in np.linspace(0.70, -0.70, 40)]
    build_patch("Laguna2_Cowl", cowl, top, ["laguna2_trim"], offset=0.004, res=0.03)
    for i, line in enumerate((
        [(0.50, sb(0.50) + 0.035), (0.18, sb(0.18) + 0.045), (-0.14, sb(0.14) + 0.07)],
        [(-0.08, sb(0.08) + 0.03), (-0.36, sb(0.36) + 0.04), (-0.62, sb(0.62) + 0.075)],
    )):
        build_patch(f"Laguna2_Wiper_{i}", strip(line, 0.022), top, ["laguna2_black"],
                    offset=0.016, res=0.03, skirt=False)

    # Side daylight opening: black frame + three panes.
    side = proj_side()
    frame = chaikin(band_poly(1.34, DLO_END + 0.02, 0.004, 0.040, n=120), 1)
    panes = side_panes()
    build_patch("Laguna2_WindowFrame", frame, side, ["laguna2_black"], holes=panes,
                offset=0.0025, res=0.03, mirror=True)
    for i, pane in enumerate(panes):
        outer = offset_poly(pane, -0.004)
        build_patch(f"Laguna2_SideGlass_{i}", outer, side, ["laguna2_glass"],
                    offset=0.004, res=0.035, mirror=True)

    # Rear wiper.
    build_patch("Laguna2_RearWiper", strip([(-0.03, rsb(0) - 0.05), (0.20, rsb(0.2) - 0.075), (0.40, rsb(0.4) - 0.07)], 0.022),
                top, ["laguna2_black"], offset=0.016, res=0.03)
    build_patch("Laguna2_RearWiperBoss", circle(-0.03, rsb(0) - 0.05, 0.028, 16), top, ["laguna2_black"],
                offset=0.02, res=0.03, skirt=True)


def build_shutlines():
    top = proj_top()
    side = proj_side()
    ws, sb = windscreen_outline()
    rg, st, rsb, xmax = rear_glass_outline()
    w = 0.006
    g = ["laguna2_gap"]
    # Bonnet.
    hood_back = [(x, sb(x) - 0.092) for x in np.linspace(-0.705, 0.705, 50)]
    build_patch("Laguna2_Gap_HoodRear", strip(hood_back, w), top, g, offset=0.0012, res=0.03)
    hood_side = [(0.705, sb(0.705) - 0.092)] + [(wrail(float(s)) + 0.012, float(s)) for s in np.linspace(1.25, 0.30, 30)]
    build_patch("Laguna2_Gap_HoodSide", strip(hood_side, w), top, g, offset=0.0012, res=0.03, mirror=True)
    # Tailgate.
    gate_top = [(x, st(x) - 0.055) for x in np.linspace(-0.50, 0.50, 40)]
    build_patch("Laguna2_Gap_GateTop", strip(gate_top, w), top, g, offset=0.0012, res=0.03)
    rear = proj_rear()
    corner = rg[min(range(len(rg)), key=lambda k: abs(rg[k][0] - 0.50) + abs(rg[k][1] - 4.6))]
    edge_loc, _n = cast(top, corner[0], corner[1] + 0.01)
    x_gate, z_gate = edge_loc.x, edge_loc.z
    GATE["x"], GATE["z"] = x_gate, z_gate
    face = [(x_gate, z_gate), (x_gate + 0.004, 0.95), (x_gate + 0.008, 0.80), (x_gate + 0.002, 0.70),
            (x_gate - 0.03, 0.658)]
    build_patch("Laguna2_Gap_GateRear", strip(face, w), rear, g, offset=0.0012, res=0.03, mirror=True)
    build_patch("Laguna2_Gap_GateBottom", strip([(-x_gate + 0.03, 0.655), (x_gate - 0.03, 0.655)], w),
                rear, g, offset=0.0012, res=0.03)
    # Doors.
    arc = [(AXLE_R + 0.41 * math.cos(math.radians(a)), 0.312 + 0.41 * math.sin(math.radians(a)))
           for a in (189, 175, 160, 148, 136, 126)]
    lines = {
        "DoorFront": [(1.385, 0.245), (1.37, 0.55), (1.375, 0.78), (1.40, zbelt(1.40) + 0.004)],
        "DoorMid": [(2.50, 0.245), (2.50, zbelt(2.50) + 0.004)],
        "DoorRear": arc + [(3.57, 0.76), (3.625, 0.88), (3.645, zbelt(3.645) + 0.004)],
        "DoorRearTop": [(3.645, zbelt(3.645) + 0.004), (DLO_END + 0.03, zbelt(DLO_END) + 0.03)],
        "Sill": [(1.385, 0.245), (arc[0][0], 0.245)],
        "BumperFront": [(0.60, 0.745), (0.615, 0.62), (0.64, 0.54)],
        "BumperRear": [(4.0, 0.61), (4.12, 0.655), (4.21, 0.75), (4.235, 0.812)],
    }
    for name, line in lines.items():
        build_patch("Laguna2_Gap_" + name, strip(line, w), side, g, offset=0.0012, res=0.03, mirror=True)
    # Fuel flap, right-hand side only.
    flap = rrect(4.00, 0.87, 0.15, 0.135, 0.035)
    build_patch("Laguna2_Gap_FuelFlap", flap, proj_side(-1.0), g, holes=[offset_poly(flap, 0.005)],
                offset=0.0012, res=0.02)


def build_side_trim():
    side = proj_side()
    for name, s0, s1 in (("F", 1.47, 2.485), ("R", 2.515, 3.30)):
        def zc(s):
            return 0.512 + 0.008 * (s - 1.47) / 1.8

        body = [(s0, zc(s0) - 0.03), (s1, zc(s1) - 0.03), (s1, zc(s1) + 0.03), (s0, zc(s0) + 0.03)]
        build_patch(f"Laguna2_Moulding_{name}", chaikin(densify(body, 0.2), 1), side, ["laguna2_trim"],
                    offset=0.011, res=0.03, skirt=True, mirror=True)
    build_patch("Laguna2_Repeater", rrect(1.555, 0.5125, 0.04, 0.05, 0.006), side, ["laguna2_amber"],
                offset=0.0125, res=0.02, skirt=True, mirror=True)
    for name, sc, zc in (("F", 2.33, 0.805), ("R", 3.40, 0.848)):
        build_patch(f"Laguna2_HandleRecess_{name}", rrect(sc, zc - 0.012, 0.21, 0.058, 0.026), side,
                    ["laguna2_gap"], offset=0.0015, res=0.02, mirror=True)
        build_patch(f"Laguna2_Handle_{name}", rrect(sc, zc + 0.006, 0.225, 0.036, 0.016), side,
                    ["laguna2_paint"], offset=0.017, res=0.02, skirt=True, mirror=True)


def build_front():
    cyl = proj_cyl(True)
    lamp = chaikin([
        (FX(0.355), 0.628), (FX(0.36), 0.692), (FX(0.46), 0.738), (FX(0.60), 0.770),
        (FS(0.25), 0.778), (FS(0.42), 0.768), (FS(0.57), 0.725),
        (FS(0.50), 0.672), (FS(0.36), 0.650), (FS(0.22), 0.638), (FX(0.62), 0.630), (FX(0.48), 0.626),
    ], 2)
    cx = 0.5 * (FX(0.62) + FS(0.25))
    build_patch("Laguna2_Headlamp", lamp, cyl,
                ["laguna2_black", "laguna2_lamp_housing", "laguna2_lamp_lens", "laguna2_lamp_ring"],
                zones=[(offset_poly(lamp, 0.008), 1),
                       (circle(cx, 0.700, 0.045), 3), (circle(cx, 0.700, 0.035), 2),
                       (circle(FX(0.47), 0.678, 0.036), 3), (circle(FX(0.47), 0.678, 0.027), 2)],
                offset=0.004, res=0.02, skirt=True, mirror=True)
    top_edge = [(-0.345, 0.672), (-0.18, 0.682), (-0.07, 0.668), (0.0, 0.652), (0.07, 0.668), (0.18, 0.682), (0.345, 0.672)]
    grille = [(FX(-0.33), 0.603), (FX(0.33), 0.603)] + [(FX(x), z) for x, z in reversed(top_edge)]
    build_patch("Laguna2_Grille", chaikin(grille, 1), cyl, ["laguna2_black"], offset=0.002, res=0.02)
    for i, z in enumerate((0.618, 0.634, 0.650)):
        half = 0.30 if i < 2 else 0.26
        build_patch(f"Laguna2_GrilleSlat_{i}", strip([(FX(-half), z), (FX(0.0), z), (FX(half), z)], 0.006), cyl,
                    ["laguna2_trim"], offset=0.005, res=0.02)
    wing_line = [(FX(x), z + 0.014) for x, z in top_edge]
    build_patch("Laguna2_GrilleWing", strip(wing_line, 0.024), cyl, ["laguna2_lamp_ring"], offset=0.004, res=0.015, skirt=True)
    intake = chaikin([(FX(-0.66), 0.305), (FX(0.66), 0.305), (FX(0.76), 0.35), (FX(0.66), 0.405), (FX(-0.66), 0.405), (FX(-0.76), 0.35)], 2)
    build_patch("Laguna2_Intake", intake, cyl, ["laguna2_black"], offset=0.002, res=0.025)
    build_patch("Laguna2_Fog", circle(FX(0.62), 0.355, 0.036), cyl, ["laguna2_lamp_housing"],
                offset=0.004, res=0.02, mirror=True)
    rub = strip([(FX(0.33), 0.478), (FX(0.6), 0.478), (FS(0.35), 0.476), (FS(0.585), 0.474)], 0.036)
    build_patch("Laguna2_RubFront", rub, cyl, ["laguna2_trim"], offset=0.005, res=0.03, skirt=True, mirror=True)
    build_patch("Laguna2_PlateFront", rrect(0.0, 0.478, 0.52, 0.112, 0.008), proj_front(),
                ["laguna2_plate_white"], offset=0.008, res=0.04, skirt=True)


def build_rear():
    cyl = proj_cyl(False)
    lamp = chaikin([
        (RX(0.32), 0.812), (RX(0.32), 0.925), (RX(0.50), 0.940), (RX(0.66), 0.945),
        (RS(4.42), 0.940), (RS(4.34), 0.915), (RS(4.27), 0.862), (RS(4.24), 0.818),
        (RS(4.30), 0.805), (RX(0.66), 0.805), (RX(0.45), 0.805),
    ], 2)
    build_patch("Laguna2_Taillamp", lamp, cyl, ["laguna2_tail_red", "laguna2_tail_clear", "laguna2_black"],
                zones=[(circle(RX(0.40), 0.872, 0.036), 1), (circle(RX(0.40), 0.872, 0.013), 0),
                       (circle(RX(0.64), 0.876, 0.037), 1), (circle(RX(0.64), 0.876, 0.025), 0),
                       (strip([(RX(GATE["x"] + 0.008), 0.70), (RX(GATE["x"] + 0.004), 1.0)], 0.007), 2)],
                offset=0.005, res=0.02, skirt=True, mirror=True)
    rub = strip([(-RS(4.07), 0.585), (-RS(4.35), 0.585), (RX(-0.62), 0.585), (RX(0.0), 0.585),
                 (RX(0.62), 0.585), (RS(4.35), 0.585), (RS(4.07), 0.585)], 0.036)
    build_patch("Laguna2_RubRear", rub, cyl, ["laguna2_trim"], offset=0.005, res=0.03, skirt=True)
    build_patch("Laguna2_PlateRear", rrect(0.0, 0.44, 0.52, 0.112, 0.008), proj_rear(),
                ["laguna2_plate_yellow"], offset=0.008, res=0.04, skirt=True)
    build_patch("Laguna2_BadgePlinth", rrect(0.0, 0.86, 0.115, 0.125, 0.02), proj_rear(),
                ["laguna2_chrome", "laguna2_black"], zones=[(rrect(0.0, 0.86, 0.098, 0.108, 0.016), 1)],
                offset=0.006, res=0.03, skirt=True)
    build_patch("Laguna2_BrakeLight3", rrect(0.0, 1.052, 0.28, 0.022, 0.008), proj_rear(),
                ["laguna2_tail_red"], offset=0.004, res=0.02, skirt=True)


# --------------------------------------------------------------------------
# Badges, lettering, mirrors, antenna
# --------------------------------------------------------------------------
def surface_frame(proj, a, b, lift=0.0):
    loc, n = cast(proj, a, b)
    up = Vector((0, 0, 1))
    xax = up.cross(n)
    if xax.length < 1e-6:
        xax = Vector((1, 0, 0))
    xax.normalize()
    yax = n.cross(xax).normalized()
    m = Matrix((xax, yax, n)).transposed().to_4x4()
    m.translation = loc + n * lift
    return m


def diamond(name, width, height, depth, matrix):
    bm = bmesh.new()
    outer = [(0, height / 2), (-width / 2, 0), (0, -height / 2), (width / 2, 0)]
    k = 0.52
    vo0 = [bm.verts.new((x, y, 0)) for x, y in outer]
    vi0 = [bm.verts.new((x * k, y * k, 0)) for x, y in outer]
    vo1 = [bm.verts.new((x * 0.93, y * 0.93, depth)) for x, y in outer]
    vi1 = [bm.verts.new((x * k * 1.12, y * k * 1.12, depth)) for x, y in outer]
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((vo1[i], vo1[j], vi1[j], vi1[i]))
        bm.faces.new((vo0[i], vo0[j], vo1[j], vo1[i]))
        bm.faces.new((vi0[j], vi0[i], vi1[i], vi1[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = bm_obj(name, bm, ["laguna2_chrome"], smooth=20.0)
    obj.data.transform(matrix)
    return obj


def text_mesh(name, body, size, material, matrix, extrude=0.0015, spacing=1.0):
    cu = bpy.data.curves.new(name + "_cu", "FONT")
    cu.body = body
    cu.size = size
    cu.extrude = extrude
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.space_character = spacing
    tmp = bpy.data.objects.new(name + "_tmp", cu)
    bpy.context.scene.collection.objects.link(tmp)
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    mesh = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp, do_unlink=True)
    mesh.name = name
    mesh.materials.clear()
    mesh.materials.append(MATS[material])
    mesh.transform(matrix)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def build_badges():
    front, rear = proj_front(), proj_rear()
    diamond("Laguna2_BadgeFront", 0.08, 0.104, 0.008, surface_frame(front, 0.0, 0.718, 0.001))
    diamond("Laguna2_BadgeRear", 0.064, 0.084, 0.006, surface_frame(rear, 0.0, 0.86, 0.007))
    text_mesh("Laguna2_Lettering", "LAGUNA", 0.034, "laguna2_chrome", surface_frame(rear, 0.0, 0.772, 0.001), spacing=1.9)
    text_mesh("Laguna2_PlateTextFront", "LAGUNA II", 0.07, "laguna2_gap", surface_frame(front, 0.0, 0.478, 0.0085), extrude=0.0005, spacing=1.1)
    text_mesh("Laguna2_PlateTextRear", "LAGUNA II", 0.07, "laguna2_gap", surface_frame(rear, 0.0, 0.44, 0.0085), extrude=0.0005, spacing=1.1)


def build_mirrors():
    for sign, tag in ((1.0, "L"), (-1.0, "R")):
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=28, v_segments=16, radius=1.0)
        for v in bm.verts:
            v.co.x = 0.115 * math.copysign(abs(v.co.x) ** 0.7, v.co.x)
            v.co.y *= 0.075
            v.co.z = 0.068 * math.copysign(abs(v.co.z) ** 0.7, v.co.z)
            if v.co.y > 0.03:
                v.co.y = 0.03
            if v.co.y < 0:
                v.co.y *= 0.9
                v.co.x *= 1.0 - 0.9 * (v.co.y / 0.075) ** 2 * 0.25
        bm.faces.ensure_lookup_table()
        for f in bm.faces:
            f.material_index = 1 if all(abs(v.co.y - 0.03) < 1e-5 for v in f.verts) else 0
        centre = B(sign * 0.985, 1.56, zbelt(1.56) + 0.045)
        bmesh.ops.translate(bm, vec=centre, verts=bm.verts)
        obj = bm_obj(f"Laguna2_Mirror_{tag}", bm, ["laguna2_paint", "laguna2_mirror"], smooth=50.0)
        del obj
        foot = B(sign * 0.875, 1.535, zbelt(1.535) + 0.035)
        box(f"Laguna2_MirrorFoot_{tag}", foot, (0.09, 0.075, 0.05), "laguna2_black", bevel=0.012)
    # Roof antenna.
    loc, n = cast(proj_top(), 0.0, 3.22)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.005, radius2=0.002, depth=0.20,
                          matrix=Matrix.Translation((0, 0, 0.10)))
    bmesh.ops.create_cone(bm, cap_ends=True, segments=14, radius1=0.022, radius2=0.012, depth=0.02,
                          matrix=Matrix.Translation((0, 0, 0.01)))
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(-52), 3, "X"), verts=bm.verts)
    bmesh.ops.translate(bm, vec=loc, verts=bm.verts)
    bm_obj("Laguna2_Antenna", bm, ["laguna2_black"], smooth=40.0)


# --------------------------------------------------------------------------
# Interior
# --------------------------------------------------------------------------
def build_interior():
    I, S = "laguna2_interior", "laguna2_seat"
    box("Laguna2_Int_Floor", B(0, 2.65, 0.30), (1.50, 2.9, 0.04), I, bevel=0.01)
    box("Laguna2_Int_Dash", B(0, 1.62, 0.84), (1.46, 0.60, 0.30), I, bevel=0.07, segments=4)
    box("Laguna2_Int_Console", B(0, 2.25, 0.50), (0.22, 1.0, 0.30), I, bevel=0.04)
    box("Laguna2_Int_Shelf", B(0, 3.85, 1.03), (1.22, 0.60, 0.03), I, bevel=0.01)
    box("Laguna2_Int_RearMirror", B(0, 2.03, 1.30), (0.22, 0.03, 0.06), I, bevel=0.012)
    for sign, tag in ((1.0, "L"), (-1.0, "R")):
        x = sign * 0.365
        box(f"Laguna2_Int_SeatBase_{tag}", B(x, 2.36, 0.43), (0.50, 0.52, 0.17), S, bevel=0.05, segments=4)
        box(f"Laguna2_Int_SeatBack_{tag}", B(x, 2.66, 0.80), (0.48, 0.13, 0.64), S, bevel=0.05, rot_x=math.radians(-16), segments=4)
        box(f"Laguna2_Int_Headrest_{tag}", B(x, 2.765, 1.175), (0.26, 0.10, 0.17), S, bevel=0.04, rot_x=math.radians(-12), segments=4)
        box(f"Laguna2_Int_RearHeadrest_{tag}", B(sign * 0.36, 3.59, 1.08), (0.25, 0.10, 0.15), S, bevel=0.04, rot_x=math.radians(-18), segments=4)
        box(f"Laguna2_Int_DoorCard_{tag}", B(sign * 0.78, 2.45, 0.66), (0.04, 1.9, 0.55), I, bevel=0.012)
    box("Laguna2_Int_RearBase", B(0, 3.20, 0.45), (1.28, 0.52, 0.17), S, bevel=0.05, segments=4)
    box("Laguna2_Int_RearBack", B(0, 3.48, 0.78), (1.28, 0.13, 0.58), S, bevel=0.05, rot_x=math.radians(-20), segments=4)
    # Steering wheel (left-hand drive).
    bm = bmesh.new()
    seg_major, seg_minor = 36, 10
    rmaj, rmin = 0.185, 0.016
    ring = []
    for i in range(seg_major):
        a = 2 * math.pi * i / seg_major
        row = []
        for j in range(seg_minor):
            b_ = 2 * math.pi * j / seg_minor
            r = rmaj + rmin * math.cos(b_)
            row.append(bm.verts.new((r * math.cos(a), rmin * math.sin(b_), r * math.sin(a))))
        ring.append(row)
    for i in range(seg_major):
        for j in range(seg_minor):
            bm.faces.new((ring[i][j], ring[(i + 1) % seg_major][j], ring[(i + 1) % seg_major][(j + 1) % seg_minor], ring[i][(j + 1) % seg_minor]))
    bmesh.ops.create_cone(bm, cap_ends=True, segments=20, radius1=0.07, radius2=0.06, depth=0.05,
                          matrix=Matrix.Rotation(math.radians(90), 4, "X"))
    for ang in (0, 180, 270):
        res = bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Rotation(math.radians(ang), 4, "Y") @ Matrix.Translation((0.11, 0, 0)) @ Matrix.Diagonal((0.12, 0.018, 0.03, 1.0)))
        del res
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(-24), 3, "X"), verts=bm.verts)
    bmesh.ops.translate(bm, vec=B(0.365, 2.04, 0.985), verts=bm.verts)
    bm_obj("Laguna2_Int_SteeringWheel", bm, [I], smooth=40.0)


# --------------------------------------------------------------------------
# Wheels: 225/45 R17 on ten twin-spoke alloys
# --------------------------------------------------------------------------
def lathe(bm, profile, segs, mat_index):
    rings = []
    for x, r in profile:
        rings.append([bm.verts.new((x, r * math.cos(2 * math.pi * i / segs), r * math.sin(2 * math.pi * i / segs))) for i in range(segs)])
    for a, b_ in zip(rings[:-1], rings[1:]):
        for i in range(segs):
            f = bm.faces.new((a[i], a[(i + 1) % segs], b_[(i + 1) % segs], b_[i]))
            f.material_index = mat_index
    return rings


def disc_face(bm, ring, mat_index, flip=False):
    f = bm.faces.new(ring[::-1] if flip else ring)
    f.material_index = mat_index


def build_wheel_mesh():
    TIRE, ALLOY, DARK, DISC, CHROME = 0, 1, 2, 3, 4
    bm = bmesh.new()
    R, hw, rr = WHEEL_R, 0.1125, 0.2185
    tread = [(-0.072, R)]
    for gx in (-0.052, -0.018, 0.018, 0.052):
        tread += [(gx - 0.0045, R), (gx - 0.003, R - 0.007), (gx + 0.003, R - 0.007), (gx + 0.0045, R)]
    tread.append((0.072, R))
    prof = [(-0.096, rr), (-0.106, rr + 0.012), (-hw, rr + 0.04), (-0.110, R - 0.03), (-0.100, R - 0.011), (-0.088, R - 0.003)]
    prof += tread
    prof += [(0.088, R - 0.003), (0.100, R - 0.011), (0.110, R - 0.03), (hw, rr + 0.04), (0.106, rr + 0.012), (0.096, rr)]
    lathe(bm, prof, 72, TIRE)
    # Rim lip and barrel.
    lathe(bm, [(0.096, rr), (0.103, rr + 0.004), (0.107, rr + 0.001), (0.106, rr - 0.006),
               (0.098, rr - 0.011), (0.088, rr - 0.014)], 72, ALLOY)
    barrel = lathe(bm, [(0.088, rr - 0.014), (0.05, rr - 0.022), (-0.085, rr - 0.024), (-0.096, rr - 0.010), (-0.096, rr)], 72, DARK)
    del barrel
    # Brake disc, hub carrier, caliper.
    rings = lathe(bm, [(0.030, 0.07), (0.030, 0.150), (0.006, 0.150), (0.006, 0.07)], 48, DISC)
    disc_face(bm, rings[0], DISC, flip=True)
    rings = lathe(bm, [(-0.09, 0.10), (0.006, 0.10)], 24, DARK)
    disc_face(bm, rings[0], DARK)
    res = bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0.018, -0.112, 0.062)) @ Matrix.Rotation(math.radians(-29), 4, "X") @ Matrix.Diagonal((0.07, 0.06, 0.13, 1.0)))
    for v in res["verts"]:
        for f in v.link_faces:
            f.material_index = DARK
    # Hub face and centre cap.
    def xface(r):
        t = min(max((r - 0.05) / 0.155, 0.0), 1.0)
        return 0.070 + 0.024 * t ** 1.25

    rings = lathe(bm, [(xface(0.078) - 0.03, 0.082), (xface(0.078) - 0.002, 0.080), (xface(0.06), 0.066), (xface(0.05), 0.034)], 40, ALLOY)
    rings = lathe(bm, [(xface(0.05), 0.034), (xface(0.05) + 0.006, 0.031), (xface(0.05) + 0.009, 0.024)], 40, DARK)
    disc_face(bm, rings[-1], DARK, flip=True)
    for i in range(5):
        a = math.radians(72 * i + 18)
        res = bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.0095, radius2=0.0095, depth=0.012,
                                    matrix=Matrix.Translation((xface(0.054) - 0.001, 0.052 * math.cos(a), 0.052 * math.sin(a))) @ Matrix.Rotation(math.radians(90), 4, "Y"))
        for v in res["verts"]:
            for f in v.link_faces:
                f.material_index = DARK
    # Tiny diamond on the cap.
    cap_x = xface(0.05) + 0.0095
    d = [bm.verts.new((cap_x, y, z)) for y, z in ((0, 0.014), (-0.010, 0), (0, -0.014), (0.010, 0))]
    bm.faces.new(d).material_index = CHROME
    # Ten twin spokes.
    r0, r1, steps = 0.060, 0.2085, 9
    for k in range(10):
        th = math.radians(36 * k)
        u = (math.cos(th), math.sin(th))
        v = (-math.sin(th), math.cos(th))
        for side_sign in (-1.0, 1.0):
            prev = None
            for i in range(steps + 1):
                t = i / steps
                r = r0 + (r1 - r0) * t
                off = side_sign * (0.0105 + 0.0025 * t)
                wt = 0.0085 - 0.0015 * t
                wb = wt + 0.006
                depth = 0.024 - 0.006 * t
                xf = xface(r)
                pts = []
                for dx, lat in ((0.0, off - wt / 2), (0.0, off + wt / 2), (-0.003, off + wt / 2 + 0.002),
                                (-depth, off + wb / 2), (-depth, off - wb / 2), (-0.003, off - wt / 2 - 0.002)):
                    pts.append(bm.verts.new((xf + dx, r * u[0] + lat * v[0], r * u[1] + lat * v[1])))
                if prev:
                    for a in range(6):
                        b_ = (a + 1) % 6
                        f = bm.faces.new((prev[a], prev[b_], pts[b_], pts[a]))
                        f.material_index = ALLOY
                else:
                    bm.faces.new(pts[::-1]).material_index = ALLOY
                prev = pts
            bm.faces.new(prev).material_index = ALLOY
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new("Laguna2_Wheel")
    bm.to_mesh(mesh)
    bm.free()
    for m in ("laguna2_tire", "laguna2_alloy", "laguna2_alloy_dark", "laguna2_disc", "laguna2_chrome"):
        mesh.materials.append(MATS[m])
    shade(mesh, 32.0)
    return mesh


def build_wheels():
    mesh = build_wheel_mesh()
    for tag, s_axle, track in (("F", AXLE_F, TRACK_F), ("R", AXLE_R, TRACK_R)):
        for sign, side in ((1.0, "L"), (-1.0, "R")):
            obj = bpy.data.objects.new(f"Laguna2_Wheel_{tag}{side}", mesh)
            bpy.context.scene.collection.objects.link(obj)
            obj.location = B(sign * track, s_axle, WHEEL_R)
            if sign < 0:
                obj.rotation_euler = (0, 0, math.pi)


# --------------------------------------------------------------------------
def main():
    for block in (bpy.data.objects, bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
        for item in list(block):
            block.remove(item)
    make_materials()
    build_body()
    build_glass()
    build_shutlines()
    build_side_trim()
    build_front()
    build_rear()
    build_badges()
    build_mirrors()
    build_interior()
    build_wheels()
    bpy.context.preferences.filepaths.save_version = 0
    os.makedirs(os.path.dirname(BLEND_PATH), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    tris = sum(len(p.vertices) - 2 for o in bpy.data.objects if o.type == "MESH" for p in o.data.polygons)
    print(f"[laguna2] saved {BLEND_PATH}  objects={len(bpy.data.objects)} tris~{tris}")


if __name__ == "__main__":
    main()
