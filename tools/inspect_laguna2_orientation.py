"""
Inspect Laguna II GLB objects, transforms, and orientations
"""

import bpy
import os

path = os.path.abspath(r"blender\references\Renault_Laguna_II-c33a6040\Renault_Laguna_II.glb")
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

bpy.ops.import_scene.gltf(filepath=path)
objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']

print(f"Laguna II has {len(objs)} mesh objects:")
for o in objs:
    print(f"  - {o.name}: verts={len(o.data.vertices)}, faces={len(o.data.polygons)}, loc={o.location}, rot={o.rotation_euler}, scale={o.scale}")
    bb = [o.matrix_world @ v.co for v in o.data.vertices]
    xs = [v.x for v in bb]
    ys = [v.y for v in bb]
    zs = [v.z for v in bb]
    print(f"    Bounds: X=[{min(xs):.2f}, {max(xs):.2f}] ({max(xs)-min(xs):.2f}m), Y=[{min(ys):.2f}, {max(ys):.2f}] ({max(ys)-min(ys):.2f}m), Z=[{min(zs):.2f}, {max(zs):.2f}] ({max(zs)-min(zs):.2f}m)")
    print(f"    Materials: {[slot.material.name if slot.material else 'None' for slot in o.material_slots]}")
