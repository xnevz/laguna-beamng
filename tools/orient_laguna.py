"""
Clean and properly orient imported Sketchfab/GLB models for BeamNG
"""

import bpy
import math
import mathutils
import os

def clean_and_orient_laguna():
    print("[Clean & Orient] Processing imported model hierarchy...")

    # Clear parent with keep transform on all meshes
    mesh_objs = [o for o in bpy.data.objects if o.type == 'MESH' and not o.name.startswith("Studio_") and not o.name.startswith("Ref_") and not o.name.endswith("_Bounds")]
    
    for o in mesh_objs:
        if o.parent:
            # Clear parent keeping global transform
            mw = o.matrix_world.copy()
            o.parent = None
            o.matrix_world = mw

    # Remove non-mesh empty nodes (like Sketchfab_model)
    for o in list(bpy.data.objects):
        if o.type == 'EMPTY' and "Sketchfab" in o.name:
            bpy.data.objects.remove(o, do_unlink=True)

    # Apply all current transforms
    for o in mesh_objs:
        bpy.context.view_layer.objects.active = o
        o.select_set(True)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        o.select_set(False)

    # Calculate global bounding box
    all_verts = [v.co for o in mesh_objs for v in o.data.vertices]
    dx = max(v.x for v in all_verts) - min(v.x for v in all_verts)
    dy = max(v.y for v in all_verts) - min(v.y for v in all_verts)
    dz = max(v.z for v in all_verts) - min(v.z for v in all_verts)
    print(f"Current extents: X={dx:.2f}m, Y={dy:.2f}m, Z={dz:.2f}m")

    # Target: Length (~4.5m) should be on Y, Width (~1.8-2.0m) on X, Height (~1.3-1.4m) on Z
    # If Z is ~4.5m and Y is ~1.3m: we need to rotate 90 deg around X
    if dz > dy and dz > dx:
        print("Length is currently on Z! Rotating -90 deg on X...")
        for o in mesh_objs:
            o.rotation_euler.x -= math.radians(90)
            bpy.context.view_layer.objects.active = o
            o.select_set(True)
            bpy.ops.object.transform_apply(rotation=True)
            o.select_set(False)
    elif dx > dy and dx > dz:
        print("Length is currently on X! Rotating 90 deg on Z...")
        for o in mesh_objs:
            o.rotation_euler.z += math.radians(90)
            bpy.context.view_layer.objects.active = o
            o.select_set(True)
            bpy.ops.object.transform_apply(rotation=True)
            o.select_set(False)

    # Recalculate after alignment
    all_verts = [v.co for o in mesh_objs for v in o.data.vertices]
    min_x, max_x = min(v.x for v in all_verts), max(v.x for v in all_verts)
    min_y, max_y = min(v.y for v in all_verts), max(v.y for v in all_verts)
    min_z, max_z = min(v.z for v in all_verts), max(v.z for v in all_verts)
    print(f"Aligned extents: Width(X)={max_x-min_x:.2f}m, Length(Y)={max_y-min_y:.2f}m, Height(Z)={max_z-min_z:.2f}m")

    # Center at X=0, Y=0, and place bottom at Z=0
    shift_x = -(min_x + max_x) / 2.0
    shift_y = -(min_y + max_y) / 2.0
    shift_z = -min_z

    for o in mesh_objs:
        o.location.x += shift_x
        o.location.y += shift_y
        o.location.z += shift_z
        bpy.context.view_layer.objects.active = o
        o.select_set(True)
        bpy.ops.object.transform_apply(location=True)
        o.select_set(False)

    print(f"[Clean & Orient] Successfully aligned! Car is upright on ground plane Z=0.")

if __name__ == "__main__":
    clean_and_orient_laguna()
