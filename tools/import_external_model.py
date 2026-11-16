"""
Import and Prepare External 3D Models for BeamNG Laguna Pipeline
Supports: .obj, .fbx, .gltf, .glb, .blend
"""

import bpy
import os
import sys
import argparse

def import_model(filepath, target_generation="gen2", scale_factor=1.0):
    blend_master = os.path.abspath(r"blender\laguna_master.blend")
    if os.path.exists(blend_master):
        bpy.ops.wm.open_mainfile(filepath=blend_master)

    ext = os.path.splitext(filepath)[1].lower()
    print(f"[Import] Importing {filepath} (format: {ext})...")

    # Determine collection
    col_map = {
        "gen1": "01_Laguna_I_1994",
        "gen2": "02_Laguna_II_2001",
        "gen3": "03_Laguna_III_2007"
    }
    target_col_name = col_map.get(target_generation, "02_Laguna_II_2001")
    target_col = bpy.data.collections.get(target_col_name)
    if not target_col:
        target_col = bpy.context.scene.collection

    # Track objects before import
    before_objs = set(bpy.data.objects)

    if ext == '.fbx':
        bpy.ops.import_scene.fbx(filepath=filepath)
    elif ext == '.obj':
        bpy.ops.wm.obj_import(filepath=filepath)
    elif ext in ['.gltf', '.glb']:
        bpy.ops.import_scene.gltf(filepath=filepath)
    else:
        print(f"[Import] Unsupported extension: {ext}")
        return False

    imported = list(set(bpy.data.objects) - before_objs)
    print(f"[Import] Imported {len(imported)} objects.")

    for obj in imported:
        # Move to target collection
        for col in obj.users_collection:
            col.objects.unlink(obj)
        target_col.objects.link(obj)

        if scale_factor != 1.0:
            obj.scale = (obj.scale[0] * scale_factor, obj.scale[1] * scale_factor, obj.scale[2] * scale_factor)
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy.ops.object.transform_apply(scale=True)
            obj.select_set(False)

    bpy.ops.wm.save_as_mainfile(filepath=blend_master)
    print(f"[Import] Saved updated master scene to {blend_master}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to 3D model file (.obj, .fbx, .gltf)")
    parser.add_argument("--gen", default="gen2", choices=["gen1", "gen2", "gen3"], help="Target generation")
    parser.add_argument("--scale", type=float, default=1.0, help="Uniform scale multiplier")
    args = parser.parse_args()

    import_model(args.file, args.gen, args.scale)
