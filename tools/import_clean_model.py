"""
Clean, mathematically perfect importer for the real Renault Laguna model
Uses root parenting to rotate and position the entire 252-object vehicle seamlessly.
"""

import bpy
import math
import mathutils
import os
import shutil

def import_clean_laguna():
    print("[Clean Importer] Removing old geometry...")

    # Remove non-studio objects
    for o in list(bpy.data.objects):
        if not o.name.startswith("Studio_") and not o.name.startswith("Ref_") and not o.name.endswith("_Bounds"):
            bpy.data.objects.remove(o, do_unlink=True)

    col_target = bpy.data.collections.get("01_Laguna_I_1994")
    if not col_target:
        col_target = bpy.data.collections.new("01_Laguna_I_1994")
        bpy.context.scene.collection.children.link(col_target)

    # 1. Import ST TCC GLB
    tcc_path = os.path.abspath(r"blender\references\Renault_Laguna_ST_TCC_1995-1999-6d7d4044\Renault_Laguna_ST_TCC_1995-1999.glb")
    before_objs = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=tcc_path)
    imported = [o for o in bpy.data.objects if o not in before_objs]
    mesh_objs = [o for o in imported if o.type == 'MESH']
    print(f"[Clean Importer] Imported {len(mesh_objs)} mesh objects.")

    # 2. Clear initial Sketchfab parent hierarchy
    for o in mesh_objs:
        if o.parent:
            mw = o.matrix_world.copy()
            o.parent = None
            o.matrix_world = mw

    # Remove any empty nodes from glTF
    for o in imported:
        if o.type != 'MESH':
            bpy.data.objects.remove(o, do_unlink=True)

    # 3. Create a single root empty to control orientation of the entire car
    root = bpy.data.objects.new("Temp_Car_Root", None)
    bpy.context.scene.collection.objects.link(root)
    root.location = (0, 0, 0)
    root.rotation_euler = (0, 0, 0)

    for o in mesh_objs:
        o.parent = root

    # Calculate initial extents
    bpy.context.view_layer.update()
    all_verts = [o.matrix_world @ v.co for o in mesh_objs for v in o.data.vertices]
    dx = max(v.x for v in all_verts) - min(v.x for v in all_verts)
    dy = max(v.y for v in all_verts) - min(v.y for v in all_verts)
    dz = max(v.z for v in all_verts) - min(v.z for v in all_verts)
    print(f"Initial dimensions: X={dx:.2f}m, Y={dy:.2f}m, Z={dz:.2f}m")

    # In raw model: X is width (2.05m), Y is height (1.33m), Z is length (4.51m)
    # We want: Length along Y, Height along Z, Width along X
    # Rotating root by +90 deg around X:
    # new Y = -Z (length along Y)
    # new Z = Y (height along Z)
    root.rotation_euler = (math.radians(90), 0, 0)
    bpy.context.view_layer.update()

    # Recheck dimensions
    all_verts = [o.matrix_world @ v.co for o in mesh_objs for v in o.data.vertices]
    min_x, max_x = min(v.x for v in all_verts), max(v.x for v in all_verts)
    min_y, max_y = min(v.y for v in all_verts), max(v.y for v in all_verts)
    min_z, max_z = min(v.z for v in all_verts), max(v.z for v in all_verts)
    print(f"After rotation: Width(X)={max_x-min_x:.2f}m, Length(Y)={max_y-min_y:.2f}m, Height(Z)={max_z-min_z:.2f}m")

    # Center horizontally and place tires on ground Z=0
    shift_x = -(min_x + max_x) / 2.0
    shift_y = -(min_y + max_y) / 2.0
    shift_z = -min_z
    root.location = (shift_x, shift_y, shift_z)
    bpy.context.view_layer.update()

    # Unparent and bake world transform
    for o in mesh_objs:
        mw = o.matrix_world.copy()
        o.parent = None
        o.matrix_world = mw

    bpy.data.objects.remove(root, do_unlink=True)

    # Apply transform so all objects have origin at 0,0,0 and scale 1,1,1
    for o in mesh_objs:
        bpy.context.view_layer.objects.active = o
        o.select_set(True)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        o.select_set(False)

        # Move to Laguna collection
        for c in o.users_collection:
            c.objects.unlink(o)
        col_target.objects.link(o)

    print("[Clean Importer] Car successfully oriented and placed on ground!")

    # 4. Check & Enhance Materials
    # Assign authentic Renault Sport Metallic Blue to body panels
    mat_blue = bpy.data.materials.get("Laguna_Sport_Blue")
    if not mat_blue:
        mat_blue = bpy.data.materials.new("Laguna_Sport_Blue")
        mat_blue.use_nodes = True
        bsdf = mat_blue.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.02, 0.12, 0.55, 1.0)
            bsdf.inputs['Metallic'].default_value = 0.85
            bsdf.inputs['Roughness'].default_value = 0.20

    # Find the largest body meshes and assign car paint
    mesh_objs.sort(key=lambda o: len(o.data.vertices), reverse=True)
    # The largest mesh is the unibody shell
    if mesh_objs:
        body_obj = mesh_objs[0]
        body_obj.data.materials.clear()
        body_obj.data.materials.append(mat_blue)
        print(f"Assigned Laguna_Sport_Blue to main body shell: {body_obj.name}")

    # 5. Position Studio Camera at standard 3/4 perspective
    scene = bpy.context.scene
    cam = scene.camera
    if not cam:
        cam_data = bpy.data.cameras.new("Studio_Cam_Data")
        cam = bpy.data.objects.new("Studio_Cam", cam_data)
        bpy.context.scene.collection.objects.link(cam)
        scene.camera = cam

    cam.location = mathutils.Vector((-4.2, 4.0, 1.40))
    target = mathutils.Vector((0.0, 0.2, 0.65))
    cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()

    # 6. Render presentation image
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    out_png = os.path.abspath(r"c:\Users\abdelkarim\Documents\laguna-beamng\laguna_presentation.png")
    scene.render.filepath = out_png

    for obj in bpy.data.objects:
        if obj.name.startswith("Ref_") or obj.name.endswith("_Bounds"):
            obj.hide_render = True
        else:
            obj.hide_render = False

    print(f"[Render] Rendering real Laguna presentation to {out_png}...")
    bpy.ops.render.render(write_still=True)
    print(f"[Render] Render complete! File size: {os.path.getsize(out_png)} bytes")

    artifact_dir = r"C:\Users\abdelkarim\.gemini\antigravity\brain\fa1588ad-d9ab-4eb3-9303-e3e476714ebd"
    if os.path.exists(artifact_dir):
        shutil.copyfile(out_png, os.path.join(artifact_dir, "laguna_presentation.png"))
        print(f"[Render] Copied to artifact directory.")

if __name__ == "__main__":
    import_clean_laguna()
