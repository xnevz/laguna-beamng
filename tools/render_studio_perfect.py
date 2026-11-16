"""Render clean front and rear previews from the Laguna II master scene."""

import os
import shutil

import bpy
import mathutils


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create_area_light(name, location, target, power, color, size, size_y):
    light_data = bpy.data.lights.new(name + "_Data", type="AREA")
    light_data.energy = power
    light_data.color = color
    light_data.shape = "RECTANGLE"
    light_data.size = size
    light_data.size_y = size_y
    light = bpy.data.objects.new(name, light_data)
    bpy.context.scene.collection.objects.link(light)
    light.location = location
    light.rotation_euler = (
        mathutils.Vector(target) - light.location
    ).to_track_quat("-Z", "Y").to_euler()
    return light


def render_previews():
    scene = bpy.context.scene
    for obj in bpy.data.objects:
        if (
            obj.name.startswith(("Studio_", "Preview_", "Ref_"))
            or obj.name.endswith("_Bounds")
            or obj.name == "Hood_Nose_Beak"
        ):
            obj.hide_render = True

    for material_name in ("Laguna_Factory_Solarglass", "Laguna_Glass_Tinted"):
        glass = bpy.data.materials.get(material_name)
        shader = (
            glass.node_tree.nodes.get("Principled BSDF")
            if glass and glass.use_nodes
            else None
        )
        if shader:
            shader.inputs["Base Color"].default_value = (0.09, 0.13, 0.16, 1.0)
            shader.inputs["Alpha"].default_value = 0.66
            shader.inputs["Metallic"].default_value = 0.0
            shader.inputs["Roughness"].default_value = 0.12
            glass.surface_render_method = "BLENDED"

    paint = bpy.data.materials.get("Laguna_Champagne_Silver")
    if paint and paint.use_nodes:
        shader = paint.node_tree.nodes.get("Principled BSDF")
        if shader:
            shader.inputs["Base Color"].default_value = (0.62, 0.60, 0.56, 1.0)
            shader.inputs["Metallic"].default_value = 0.48
            shader.inputs["Roughness"].default_value = 0.30
            shader.inputs["Coat Weight"].default_value = 0.7
            shader.inputs["Coat Roughness"].default_value = 0.06

    for material_name, color in (
        ("Laguna_Front_Plate_White", (0.94, 0.94, 0.9, 1.0)),
        ("Laguna_Rear_Plate_Yellow", (0.9, 0.66, 0.24, 1.0)),
    ):
        plate_material = bpy.data.materials.get(material_name)
        if not plate_material or not plate_material.use_nodes:
            continue
        shader = plate_material.node_tree.nodes.get("Principled BSDF")
        if shader:
            base_color = shader.inputs.get("Base Color")
            if base_color and not base_color.is_linked:
                base_color.default_value = color
            shader.inputs["Roughness"].default_value = 0.5

    floor_material = bpy.data.materials.new("Preview_Floor_Material")
    floor_material.diffuse_color = (0.055, 0.065, 0.08, 1.0)
    floor_material.use_nodes = True
    floor_shader = floor_material.node_tree.nodes.get("Principled BSDF")
    floor_shader.inputs["Base Color"].default_value = floor_material.diffuse_color
    floor_shader.inputs["Roughness"].default_value = 0.48

    floor_mesh = bpy.data.meshes.new("Preview_Floor_Mesh")
    floor_mesh.from_pydata(
        [(-500, -500, 0), (500, -500, 0), (500, 500, 0), (-500, 500, 0)],
        [],
        [(0, 1, 2, 3)],
    )
    floor_mesh.materials.append(floor_material)
    floor = bpy.data.objects.new("Preview_Floor", floor_mesh)
    scene.collection.objects.link(floor)

    world = scene.world
    if world is None:
        world = bpy.data.worlds.new("Preview_World")
        scene.world = world
    world.use_nodes = True
    world.node_tree.nodes.clear()
    background = world.node_tree.nodes.new("ShaderNodeBackground")
    background.inputs["Color"].default_value = (0.24, 0.27, 0.32, 1.0)
    background.inputs["Strength"].default_value = 0.32
    world_output = world.node_tree.nodes.new("ShaderNodeOutputWorld")
    world.node_tree.links.new(background.outputs["Background"], world_output.inputs["Surface"])

    target = (0.0, 0.0, 0.68)
    create_area_light(
        "Preview_Key",
        (-3.5, -4.5, 5.2),
        target,
        1400,
        (1.0, 0.91, 0.79),
        5.0,
        3.0,
    )
    create_area_light(
        "Preview_Fill",
        (4.5, -0.5, 3.1),
        target,
        900,
        (0.76, 0.85, 1.0),
        4.0,
        2.5,
    )
    create_area_light(
        "Preview_Rim",
        (-2.5, 4.0, 4.2),
        target,
        1200,
        (1.0, 1.0, 1.0),
        4.5,
        2.5,
    )

    camera_data = bpy.data.cameras.new("Preview_Camera_Data")
    camera_data.lens = 42
    camera_data.clip_start = 0.1
    camera_data.clip_end = 100
    camera = bpy.data.objects.new("Preview_Camera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera

    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = 64
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.35
    scene.view_settings.gamma = 1.0
    scene.camera.data.dof.use_dof = False

    front_path = os.path.join(PROJECT_ROOT, "laguna_front.png")
    rear_path = os.path.join(PROJECT_ROOT, "laguna_rear.png")
    camera.location = (3.7, -5.5, 1.68)
    camera.rotation_euler = (
        mathutils.Vector(target) - camera.location
    ).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = front_path
    bpy.ops.render.render(write_still=True)

    camera.location = (-3.8, 5.7, 1.72)
    camera.rotation_euler = (
        mathutils.Vector(target) - camera.location
    ).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = rear_path
    bpy.ops.render.render(write_still=True)

    side_path = os.path.join(PROJECT_ROOT, "laguna_side.png")
    camera.location = (7.5, 0.0, 1.45)
    camera.data.lens = 55
    camera.rotation_euler = (
        mathutils.Vector((0.0, 0.0, 0.68)) - camera.location
    ).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = side_path
    bpy.ops.render.render(write_still=True)

    for filename in (
        "laguna_presentation.png",
        "preview_laguna2_framed.png",
        "preview_laguna2_raw.png",
    ):
        shutil.copy2(front_path, os.path.join(PROJECT_ROOT, filename))
    shutil.copy2(rear_path, os.path.join(PROJECT_ROOT, "laguna_rear_view.png"))
    print(f"[Preview] Front and rear renders saved in {PROJECT_ROOT}")


if __name__ == "__main__":
    render_previews()
