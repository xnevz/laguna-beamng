"""Load the reference Laguna II game model (blender/references/3d-model.fbx) at real scale.

The FBX is a ~2k-vertex low-poly liftback with correct proportions.  This
module imports it, drops the helper dummies, scales it so the body is the real
4.576 m long, levels its rake and moves it so its axles sit on the axles that
the jbeam (and tools/laguna2/build.py) uses.  The result is one bmesh in
project coordinates: car faces -Y, +X is the car's left, Z up, ground at 0.

FBX material slots (by what the faces turned out to be):
    #4  body paint             #8  glass
    #10 grille surround        #11 headlamp / clear tail lenses
    #12 dark trim              #13 black recesses (grille, fog lamp pockets)
    #14 amber side repeater    #15 badges / bright bits
    #16 tail lamps (red)       #2  steering wheel
"""

import os

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(HERE))
FBX_PATH = os.path.join(PROJECT_ROOT, "blender", "references", "3d-model.fbx")

L = 4.576            # real body length (m)
AXLE_F = 0.965       # front axle, metres behind the front bumper tip (build.py / jbeam)
AXLE_R = 0.985 + 2.748
WHEEL_R = 0.317      # real 205/55 R16 rolling radius

DUMMIES = ("bump_rear", "sentinel", "wheel_rb_d", "wing_lf_du")


def _bbox(points):
    lo = Vector([min(p[i] for p in points) for i in range(3)])
    hi = Vector([max(p[i] for p in points) for i in range(3)])
    return lo, hi


def load():
    """Import the FBX -> (chassis bmesh, steering bmesh, slot names, info dict), all in project space."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=FBX_PATH)
    new = [o for o in bpy.data.objects if o not in before]
    chassis = next(o for o in new if o.name.startswith("chassis"))
    steering = next((o for o in new if o.name.startswith("rul")), None)
    wheels = [o for o in new if o.name.startswith("wheel_rf")]

    world = [chassis.matrix_world @ v.co for v in chassis.data.vertices]
    lo, hi = _bbox(world)
    k = L / (hi.y - lo.y)

    centres = []
    for w in wheels:
        wlo, whi = _bbox([w.matrix_world @ v.co for v in w.data.vertices])
        centres.append((wlo + whi) / 2)
    front = [c for c in centres if c.y < (lo.y + hi.y) / 2]
    rear = [c for c in centres if c.y >= (lo.y + hi.y) / 2]
    fz = sum(c.z for c in front) / len(front)
    rz = sum(c.z for c in rear) / len(rear)
    fy = sum(c.y for c in front) / len(front)
    ry = sum(c.y for c in rear) / len(rear)

    # FBX space -> project space:
    #   1. level the rake (rotate about X so both axle centres are at the same height),
    #   2. scale to real length,
    #   3. put the axle midpoint on the jbeam axle midpoint and the axle line at WHEEL_R.
    import math
    pitch = math.atan2(rz - fz, ry - fy)
    mid = Vector((0.0, (fy + ry) / 2, (fz + rz) / 2))
    m = Matrix.Translation(-mid)
    m = Matrix.Rotation(-pitch, 4, "X") @ m
    m = Matrix.Scale(k, 4) @ m
    target_mid_y = (AXLE_F + AXLE_R) / 2 - L / 2   # project Y of the axle midpoint (car centred on L/2)
    m = Matrix.Translation((0.0, target_mid_y, WHEEL_R)) @ m

    def grab(obj):
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.transform(m @ obj.matrix_world)
        return bm

    bm = grab(chassis)
    slots = [s.name if s else "" for s in chassis.data.materials]
    sbm = grab(steering) if steering else None

    wheel_r_fbx = sum(((_bbox([w.matrix_world @ v.co for v in w.data.vertices])[1].z
                        - _bbox([w.matrix_world @ v.co for v in w.data.vertices])[0].z) / 2) for w in wheels) / len(wheels)
    info = {
        "scale": k,
        "pitch_deg": math.degrees(pitch),
        "wheelbase": (ry - fy) * k,
        "fbx_wheel_r": wheel_r_fbx * k,
        "fbx_track": (max(c.x for c in front) - min(c.x for c in front)) * k,
    }

    for o in new:
        data = o.data if o.type == "MESH" else None
        bpy.data.objects.remove(o, do_unlink=True)
        if data is not None and data.users == 0:
            bpy.data.meshes.remove(data)
    return bm, sbm, slots, info
