"""Render the Laguna II liftback from the reference-photo angles.

Run:  blender --background blender/laguna2_liftback.blend --python tools/laguna2/render.py -- [views] [--draft] [--paint=silver]
"""

import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(HERE))
OUT_DIR = os.path.join(PROJECT_ROOT, "renders")

# name: (camera location, target, lens mm)
VIEWS = {
    "front34": ((4.6, -6.2, 1.0), (-0.1, 0.1, 0.62), 50),
    "rear34": ((6.2, 5.2, 1.1), (0.0, 0.1, 0.62), 50),
    "rear_high": ((-3.3, 5.4, 2.0), (0.0, 0.5, 0.62), 50),
    "rear_low": ((-4.6, 6.3, 0.75), (0.0, 0.1, 0.64), 50),
    "side": ((11.0, 0.0, 1.2), (0.0, 0.0, 0.70), 68),
    "ref_front": ((4.4, -6.6, 1.45), (-0.1, 0.1, 0.62), 55),
    "ref_rear": ((-3.6, 6.6, 1.5), (0.1, 0.0, 0.66), 55),
    "front": ((0.0, -9.0, 0.9), (0.0, 0.0, 0.70), 120),
    "rear": ((0.0, 9.0, 0.9), (0.0, 0.0, 0.70), 120),
    "top": ((0.0, 0.01, 12.0), (0.0, 0.0, 0.0), 110),
    "wheel": ((2.4, -2.6, 0.55), (0.80, -1.30, 0.33), 85),
    "tail_close": ((-1.0, 4.6, 1.15), (-0.15, 2.15, 0.75), 45),
    "tail34_close": ((-2.6, 4.4, 1.25), (-0.3, 1.9, 0.8), 50),
    "head_close": ((1.9, -4.3, 1.05), (0.45, -2.05, 0.70), 55),
}

PAINTS = {
    "champagne": (0.44, 0.385, 0.27),
    "red": (0.33, 0.012, 0.03),
    "silver": (0.58, 0.60, 0.62),
    "grey": (0.115, 0.125, 0.135),
}


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def area(name, loc, target, power, size, size_y, color=(1, 1, 1)):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = power
    data.shape = "RECTANGLE"
    data.size = size
    data.size_y = size_y
    data.color = color
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    data.specular_factor = 0.35
    obj.location = loc
    look_at(obj, target)
    return obj


def setup(draft):
    scene = bpy.context.scene
    for obj in list(bpy.data.objects):
        if obj.name.startswith("Stage_"):
            bpy.data.objects.remove(obj, do_unlink=True)

    world = bpy.data.worlds.new("Stage_World")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    coord = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    bg = nt.nodes.new("ShaderNodeBackground")
    out = nt.nodes.new("ShaderNodeOutputWorld")
    mapr = nt.nodes.new("ShaderNodeMapRange")
    mapr.inputs[1].default_value = -0.15
    mapr.inputs[2].default_value = 1.0
    nt.links.new(coord.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs[2], mapr.inputs[0])
    nt.links.new(mapr.outputs[0], ramp.inputs[0])
    els = ramp.color_ramp.elements
    els[0].position = 0.0
    els[0].color = (0.20, 0.19, 0.18, 1)
    els[1].position = 1.0
    els[1].color = (0.30, 0.44, 0.68, 1)
    for pos, col in ((0.13, (0.92, 0.93, 0.95, 1)), (0.22, (0.78, 0.84, 0.92, 1)), (0.55, (0.48, 0.62, 0.82, 1))):
        e = els.new(pos)
        e.color = col
    nt.links.new(ramp.outputs[0], bg.inputs[0])
    bg.inputs[1].default_value = 0.75
    nt.links.new(bg.outputs[0], out.inputs[0])

    floor_mat = bpy.data.materials.new("Stage_Floor")
    floor_mat.use_nodes = True
    sh = floor_mat.node_tree.nodes.get("Principled BSDF")
    sh.inputs["Base Color"].default_value = (0.20, 0.20, 0.205, 1)
    sh.inputs["Roughness"].default_value = 0.55
    mesh = bpy.data.meshes.new("Stage_Floor")
    mesh.from_pydata([(-80, -80, 0), (80, -80, 0), (80, 80, 0), (-80, 80, 0)], [], [(0, 1, 2, 3)])
    mesh.materials.append(floor_mat)
    floor = bpy.data.objects.new("Stage_Floor", mesh)
    scene.collection.objects.link(floor)

    sun_data = bpy.data.lights.new("Stage_Sun", "SUN")
    sun_data.energy = 3.2
    sun_data.angle = math.radians(12)
    sun_data.color = (1.0, 0.96, 0.9)
    sun = bpy.data.objects.new("Stage_Sun", sun_data)
    scene.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(52), 0, math.radians(35))

    area("Stage_Top", (0, 0, 6.5), (0, 0, 0), 900, 9.0, 3.5)
    area("Stage_SideL", (7.5, -1.0, 2.6), (0, 0, 0.7), 500, 7.0, 2.0)
    area("Stage_SideR", (-7.5, 1.0, 2.6), (0, 0, 0.7), 500, 7.0, 2.0)

    cam_data = bpy.data.cameras.new("Stage_Camera")
    cam = bpy.data.objects.new("Stage_Camera", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam

    scene.render.engine = "BLENDER_EEVEE"
    try:
        scene.eevee.taa_render_samples = 24 if draft else 96
        scene.eevee.use_raytracing = True
        scene.eevee.use_shadows = True
    except Exception as exc:
        print("[warn] eevee settings:", exc)
    scene.render.resolution_x = 1280 if draft else 1920
    scene.render.resolution_y = 720 if draft else 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    try:
        scene.view_settings.view_transform = "AgX"
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception as exc:
        print("[warn] view settings:", exc)
    scene.view_settings.exposure = -0.1
    return cam


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    draft = "--draft" in argv
    paint = next((a.split("=", 1)[1] for a in argv if a.startswith("--paint=")), None)
    suffix = next((a.split("=", 1)[1] for a in argv if a.startswith("--suffix=")), "")
    names = [a for a in argv if not a.startswith("--")] or ["front34", "rear34", "rear_high", "rear_low", "side"]
    if paint:
        sh = bpy.data.materials["laguna2_paint"].node_tree.nodes.get("Principled BSDF")
        c = PAINTS[paint]
        sh.inputs["Base Color"].default_value = (c[0], c[1], c[2], 1.0)
    cam = setup(draft)
    os.makedirs(OUT_DIR, exist_ok=True)
    for name in names:
        loc, target, lens = VIEWS[name]
        cam.location = loc
        cam.data.lens = lens
        look_at(cam, target)
        path = os.path.join(OUT_DIR, f"laguna2_{name}{suffix}.png")
        bpy.context.scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
        print("[render]", path)


if __name__ == "__main__":
    main()
