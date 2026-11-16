"""
Import real Renault Laguna I Touring Car into master Blender scene and render studio presentation.
"""

import bpy
import math
import mathutils
import os
import shutil

def import_real_laguna1_and_render():
    print("[Import Real Laguna] Loading Laguna I ST TCC (252 objects)...")

    # Clean previous generated crude meshes
    objs_to_delete = [o.name for o in bpy.data.objects if o.name.startswith("laguna_") and not o.name.startswith("Ref_")]
    for name in objs_to_delete:
        if name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)

    col_target = bpy.data.collections.get("01_Laguna_I_1994")
    if not col_target:
        col_target = bpy.data.collections.new("01_Laguna_I_1994")
        bpy.context.scene.collection.children.link(col_target)

    # Path to real GLB model
    tcc_path = os.path.abspath(r"blender\references\Renault_Laguna_ST_TCC_1995-1999-6d7d4044\Renault_Laguna_ST_TCC_1995-1999.glb")

    before_objs = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=tcc_path)
    imported = [o for o in bpy.data.objects if o not in before_objs and o.type == 'MESH']
    print(f"[Import Real Laguna] Successfully imported {len(imported)} objects from GLB!")

    # Check initial bounding box of all imported objects
    all_verts = [o.matrix_world @ v.co for o in imported for v in o.data.vertices]
    min_x, max_x = min(v.x for v in all_verts), max(v.x for v in all_verts)
    min_y, max_y = min(v.y for v in all_verts), max(v.y for v in all_verts)
    min_z, max_z = min(v.z for v in all_verts), max(v.z for v in all_verts)
    print(f"Raw imported bounds: X=[{min_x:.2f}, {max_x:.2f}], Y=[{min_y:.2f}, {max_y:.2f}], Z=[{min_z:.2f}, {max_z:.2f}]")

    # Rotate 90 degrees around X if Y is height and Z is length
    # In raw GLB: Y is 0.0 to 1.33m (height), Z is -2.41 to 2.10m (length), X is -1.02 to 1.02m (width)
    # Rotating X by 90 deg: new Y = -Z (or +Z), new Z = Y
    for o in imported:
        o.rotation_euler.x += math.radians(90)
        bpy.context.view_layer.objects.active = o
        o.select_set(True)
        bpy.ops.object.transform_apply(rotation=True)
        o.select_set(False)

        # Move to Laguna 1 collection
        for col in o.users_collection:
            col.objects.unlink(o)
        col_target.objects.link(o)

    # Re-calculate bounds after rotation
    all_verts = [o.matrix_world @ v.co for o in imported for v in o.data.vertices]
    min_x, max_x = min(v.x for v in all_verts), max(v.x for v in all_verts)
    min_y, max_y = min(v.y for v in all_verts), max(v.y for v in all_verts)
    min_z, max_z = min(v.z for v in all_verts), max(v.z for v in all_verts)
    print(f"Rotated bounds: X=[{min_x:.2f}, {max_x:.2f}], Y=[{min_y:.2f}, {max_y:.2f}], Z=[{min_z:.2f}, {max_z:.2f}]")

    # Center laterally (X=0) and longitudinally, set wheels to ground (Z=0)
    offset_x = -(min_x + max_x) / 2.0
    offset_y = -(min_y + max_y) / 2.0
    offset_z = -min_z  # bottom touches ground Z=0

    for o in imported:
        o.location.x += offset_x
        o.location.y += offset_y
        o.location.z += offset_z
        bpy.context.view_layer.objects.active = o
        o.select_set(True)
        bpy.ops.object.transform_apply(location=True)
        o.select_set(False)

    print(f"[Import Real Laguna] Centered and grounded car successfully!")

    # Set up authentic Renault Bleu Iliade / Racing Yellow materials
    mat_paint = bpy.data.materials.get("laguna_paint")
    if not mat_paint:
        mat_paint = bpy.data.materials.new("laguna_paint")
        mat_paint.use_nodes = True
    bsdf = mat_paint.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.04, 0.18, 0.55, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.85
        bsdf.inputs['Roughness'].default_value = 0.20

    # Ensure studio presentation camera and lights frame the real car
    scene = bpy.context.scene
    cam = scene.camera
    if cam:
        cam.location = mathutils.Vector((-4.3, 4.3, 1.45))
        target = mathutils.Vector((0.0, 0.2, 0.65))
        cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()

    # Render presentation image
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    out_png = os.path.abspath(r"c:\Users\abdelkarim\Documents\laguna-beamng\laguna_presentation.png")
    scene.render.filepath = out_png

    # Hide blueprints/bounds from render
    for obj in bpy.data.objects:
        if obj.name.startswith("Ref_") or obj.name.endswith("_Bounds"):
            obj.hide_render = True
        else:
            obj.hide_render = False

    print(f"[Render] Rendering real Laguna presentation to {out_png}...")
    bpy.ops.render.render(write_still=True)
    print(f"[Render] Done! Size: {os.path.getsize(out_png)} bytes")

    artifact_dir = r"C:\Users\abdelkarim\.gemini\antigravity\brain\fa1588ad-d9ab-4eb3-9303-e3e476714ebd"
    if os.path.exists(artifact_dir):
        shutil.copyfile(out_png, os.path.join(artifact_dir, "laguna_presentation.png"))
        print("[Render] Copied to artifact directory.")

if __name__ == "__main__":
    import_real_laguna1_and_render()
