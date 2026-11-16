"""
Inspect uploaded GLB models in Blender
"""

import bpy
import os

MODELS = {
    "Laguna_I": r"blender\references\Renault_Laguna_I-3518f4bd\Renault_Laguna_I.glb",
    "Laguna_II": r"blender\references\Renault_Laguna_II-c33a6040\Renault_Laguna_II.glb",
    "Laguna_MK3_Estate": r"blender\references\Renault_Laguna_MK3_Estate_2007-2015-c80e45fe\Renault_Laguna_MK3_Estate_2007-2015.glb",
    "Laguna_ST_TCC": r"blender\references\Renault_Laguna_ST_TCC_1995-1999-6d7d4044\Renault_Laguna_ST_TCC_1995-1999.glb",
    "Steering_Wheel": r"blender\references\Renault_Steeringwheel-38ec5e4c\Renault_Steeringwheel.glb"
}

def inspect_models():
    for name, rel_path in MODELS.items():
        abs_path = os.path.abspath(rel_path)
        if not os.path.exists(abs_path):
            print(f"[Inspect] Missing: {name} at {abs_path}")
            continue

        # Clean scene temporarily to inspect
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)

        print(f"\n==========================================")
        print(f"MODEL: {name}")
        print(f"Path: {abs_path} (Size: {os.path.getsize(abs_path)} bytes)")

        try:
            bpy.ops.import_scene.gltf(filepath=abs_path)
            imported_objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
            total_verts = sum(len(o.data.vertices) for o in imported_objs)
            total_faces = sum(len(o.data.polygons) for o in imported_objs)

            # Calculate total bounding box
            min_x = min(min((o.matrix_world @ v.co).x for v in o.data.vertices) for o in imported_objs)
            max_x = max(max((o.matrix_world @ v.co).x for v in o.data.vertices) for o in imported_objs)
            min_y = min(min((o.matrix_world @ v.co).y for v in o.data.vertices) for o in imported_objs)
            max_y = max(max((o.matrix_world @ v.co).y for v in o.data.vertices) for o in imported_objs)
            min_z = min(min((o.matrix_world @ v.co).z for v in o.data.vertices) for o in imported_objs)
            max_z = max(max((o.matrix_world @ v.co).z for v in o.data.vertices) for o in imported_objs)

            size_x = max_x - min_x
            size_y = max_y - min_y
            size_z = max_z - min_z

            print(f"Objects: {len(imported_objs)} | Total Verts: {total_verts:,} | Faces: {total_faces:,}")
            print(f"Bounding Size: X={size_x:.3f}m, Y={size_y:.3f}m, Z={size_z:.3f}m")
            print(f"Sample Objects: {[o.name for o in imported_objs[:8]]}")
        except Exception as e:
            print(f"Error importing {name}: {e}")

if __name__ == "__main__":
    inspect_models()
