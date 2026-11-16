"""
Fast & High-Quality Studio Presentation Render for Renault Laguna II
Uses Blender EEVEE for instantaneous real-time ray-traced presentation rendering.
"""

import bpy
import math
import os
import shutil

def setup_studio_and_render():
    print("[Presentation] Setting up studio environment, lighting, and camera...")

    scene = bpy.context.scene

    # 1. Hide helper / reference objects from render
    for obj in bpy.data.objects:
        if obj.name.startswith("Ref_") or obj.name.endswith("_Bounds"):
            obj.hide_render = True
        else:
            obj.hide_render = False

    # 2. Studio Lighting & Camera Collection
    col_studio = bpy.data.collections.get("Studio_Presentation")
    if not col_studio:
        col_studio = bpy.data.collections.new("Studio_Presentation")
        scene.collection.children.link(col_studio)

    # Clean previous studio objects if any
    for name in ["Studio_Floor", "Studio_KeyLight", "Studio_FillLight", "Studio_RimLight", "Studio_Cam_Front34"]:
        if name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)

    # 3. Studio Ground / Floor (Sleek dark showroom floor with subtle reflection)
    bpy.ops.mesh.primitive_plane_add(
        size=40.0,
        location=(0.0, 0.0, 0.0)
    )
    floor = bpy.context.active_object
    floor.name = "Studio_Floor"
    for col in floor.users_collection:
        col.objects.unlink(floor)
    col_studio.objects.link(floor)

    mat_floor = bpy.data.materials.get("Studio_Floor_Mat")
    if not mat_floor:
        mat_floor = bpy.data.materials.new("Studio_Floor_Mat")
        mat_floor.use_nodes = True
    bsdf_f = mat_floor.node_tree.nodes.get("Principled BSDF")
    if bsdf_f:
        bsdf_f.inputs['Base Color'].default_value = (0.02, 0.02, 0.025, 1.0)
        bsdf_f.inputs['Roughness'].default_value = 0.20 # Polished showroom reflection
        bsdf_f.inputs['Metallic'].default_value = 0.3
    floor.data.materials.append(mat_floor)

    # 4. Realistic Studio Lighting
    # A) Key Softbox Light
    light_key_data = bpy.data.lights.new(name="Studio_KeyLight_Data", type='AREA')
    light_key_data.energy = 550.0
    light_key_data.shape = 'RECTANGLE'
    light_key_data.size = 6.0
    light_key_data.size_y = 3.0
    light_key_data.color = (1.0, 0.98, 0.95)
    light_key = bpy.data.objects.new("Studio_KeyLight", light_key_data)
    light_key.location = (0.0, 0.5, 4.0)
    col_studio.objects.link(light_key)

    # B) Front 3/4 Fill Light
    light_fill_data = bpy.data.lights.new(name="Studio_FillLight_Data", type='AREA')
    light_fill_data.energy = 280.0
    light_fill_data.shape = 'RECTANGLE'
    light_fill_data.size = 4.0
    light_fill_data.size_y = 2.5
    light_fill_data.color = (0.95, 0.98, 1.0)
    light_fill = bpy.data.objects.new("Studio_FillLight", light_fill_data)
    light_fill.location = (-4.2, 4.0, 2.2)
    light_fill.rotation_euler = (math.radians(65), math.radians(15), math.radians(-50))
    col_studio.objects.link(light_fill)

    # C) Rear Rim / Accent Light
    light_rim_data = bpy.data.lights.new(name="Studio_RimLight_Data", type='AREA')
    light_rim_data.energy = 240.0
    light_rim_data.shape = 'RECTANGLE'
    light_rim_data.size = 4.0
    light_rim_data.size_y = 2.0
    light_rim_data.color = (0.9, 0.95, 1.0)
    light_rim = bpy.data.objects.new("Studio_RimLight", light_rim_data)
    light_rim.location = (4.0, -3.5, 2.5)
    light_rim.rotation_euler = (math.radians(70), math.radians(-20), math.radians(135))
    col_studio.objects.link(light_rim)

    # 5. Studio Camera (Classic 3/4 Automotive Telephoto Perspective)
    cam_data = bpy.data.cameras.new("Studio_Cam_Data")
    cam_data.lens = 65.0
    cam_obj = bpy.data.objects.new("Studio_Cam_Front34", cam_data)
    cam_obj.location = (-4.20, 4.40, 1.45)
    cam_obj.rotation_euler = (math.radians(78), math.radians(0), math.radians(-46))
    col_studio.objects.link(cam_obj)
    scene.camera = cam_obj

    # 6. Render Settings: EEVEE for fast high-quality output
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100

    if scene.world:
        scene.world.use_nodes = True
        bg = scene.world.node_tree.nodes.get("Background")
        if bg:
            bg.inputs['Color'].default_value = (0.015, 0.015, 0.02, 1.0)
            bg.inputs['Strength'].default_value = 0.6

    out_dir = os.path.abspath(r"c:\Users\abdelkarim\Documents\laguna-beamng")
    output_png = os.path.join(out_dir, "laguna_presentation.png")
    scene.render.filepath = output_png
    scene.render.image_settings.file_format = 'PNG'

    print("[Presentation] Rendering image with EEVEE...")
    bpy.ops.render.render(write_still=True)
    print(f"[Presentation] Render completed! Saved to: {output_png}")

    artifact_dir = r"C:\Users\abdelkarim\.gemini\antigravity\brain\fa1588ad-d9ab-4eb3-9303-e3e476714ebd"
    if os.path.exists(artifact_dir):
        artifact_png = os.path.join(artifact_dir, "laguna_presentation.png")
        shutil.copyfile(output_png, artifact_png)
        print(f"[Presentation] Copied to artifact directory: {artifact_png}")

if __name__ == "__main__":
    setup_studio_and_render()
