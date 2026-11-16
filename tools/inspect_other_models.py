"""
Inspect MK3 Estate and ST TCC in Blender
"""

import bpy
import os

def inspect_model(path, title):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=path)
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    print(f"\n--- {title} ---")
    print(f"Total objects: {len(objs)}")
    for o in objs[:10]:
        print(f"  {o.name}: verts={len(o.data.vertices)}, mat={[m.name for m in o.data.materials if m]}")
    # Bounding box
    all_verts = [o.matrix_world @ v.co for o in objs for v in o.data.vertices]
    xs = [v.x for v in all_verts]
    ys = [v.y for v in all_verts]
    zs = [v.z for v in all_verts]
    print(f"Total bounds: X=[{min(xs):.2f}, {max(xs):.2f}] ({max(xs)-min(xs):.2f}), Y=[{min(ys):.2f}, {max(ys):.2f}] ({max(ys)-min(ys):.2f}), Z=[{min(zs):.2f}, {max(zs):.2f}] ({max(zs)-min(zs):.2f})")

p_mk3 = os.path.abspath(r"blender\references\Renault_Laguna_MK3_Estate_2007-2015-c80e45fe\Renault_Laguna_MK3_Estate_2007-2015.glb")
inspect_model(p_mk3, "MK3 Estate")

p_tcc = os.path.abspath(r"blender\references\Renault_Laguna_ST_TCC_1995-1999-6d7d4044\Renault_Laguna_ST_TCC_1995-1999.glb")
inspect_model(p_tcc, "Laguna I Touring Car (ST TCC)")
