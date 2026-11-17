"""Overlay the model on the reference photos with a matched camera.

Run:  blender --background blender/laguna2_liftback.blend --python tools/laguna2/compare.py -- side [front] [rear]

Writes renders/compare_<view>.png: the photo with the model's outline (green)
and its dark parts - glass, trim, tyres - (cyan edge) drawn on top, and
renders/compare_<view>_blend.png, a 50/50 mix.
"""

import math
import os
import sys

import bpy
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render as stage  # noqa: E402

PROJECT_ROOT = os.path.dirname(os.path.dirname(HERE))
REF_DIR = os.path.join(PROJECT_ROOT, "blender", "references")
OUT_DIR = os.path.join(PROJECT_ROOT, "renders")
W = 2000

# photo, camera location, look-at target, lens (mm, 36 mm sensor), roll (deg), shift_x, shift_y
VIEWS = {
    "side": ("laguna2_side.jpg", (7.69, 0.04, 1.35), (0.0, 0.04, 0.80), 55.5, 0.65, 0.0, -0.0125),
    "front": ("laguna2_front.jpg", (5.429, -6.109, 1.452), (0.546, -0.920, 0.749), 67.9, 2.14, 0.0, 0.0),
    "side2": ("C:/Users/abdelkarim/Documents/laguna-beamng/scratch/ref_side_phase2.png", (16.724, -0.341, 1.920), (-1.346, 0.054, 0.691), 113.3, -0.62, 0.0, 0.0),
    "rear2": ("C:/Users/abdelkarim/Documents/laguna-beamng/scratch/ref_rear_phase2.png", (12.657, 22.773, 2.905), (0.369, 0.556, 0.884), 178.5, -2.73, 0.0, 0.0),
    "rear": ("laguna2_rear.jpg", (9.129, 12.590, 2.071), (-3.396, -4.337, 0.123), 145.5, 0.52, 0.0, 0.0),
}


def load_photo(name, height):
    img = bpy.data.images.load(os.path.join(REF_DIR, name))
    img.scale(W, height)
    arr = np.array(img.pixels[:], dtype=np.float32).reshape(height, W, 4)
    bpy.data.images.remove(img)
    return arr


def save(arr, path):
    h, w = arr.shape[:2]
    img = bpy.data.images.new("out", w, h, alpha=False)
    out = np.ones((h, w, 4), dtype=np.float32)
    out[..., :3] = np.clip(arr[..., :3], 0, 1)
    img.pixels = out.ravel().tolist()
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)
    print("[compare]", path)


def edge(mask):
    e = np.zeros_like(mask, dtype=bool)
    e[1:, :] |= mask[1:, :] != mask[:-1, :]
    e[:, 1:] |= mask[:, 1:] != mask[:, :-1]
    for _ in range(1):
        g = e.copy()
        g[1:, :] |= e[:-1, :]
        g[:-1, :] |= e[1:, :]
        g[:, 1:] |= e[:, :-1]
        g[:, :-1] |= e[:, 1:]
        e = g
    return e


def render_array(scene, path):
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    img = bpy.data.images.load(path)
    h = scene.render.resolution_y
    arr = np.array(img.pixels[:], dtype=np.float32).reshape(h, W, 4)
    bpy.data.images.remove(img)
    return arr


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    names = [a for a in argv if not a.startswith("--")] or ["side"]
    override = {}
    for a in argv:
        if a.startswith("--cam="):  # --cam=x,y,z,tx,ty,tz,lens,roll,shx,shy
            v = [float(t) for t in a.split("=", 1)[1].split(",")]
            override = dict(loc=v[0:3], target=v[3:6], lens=v[6], roll=v[7], shx=v[8], shy=v[9])
    cam = stage.setup(True)
    scene = bpy.context.scene
    floor = bpy.data.objects.get("Stage_Floor")
    if floor:
        floor.hide_render = True
    scene.render.film_transparent = True
    scene.render.image_settings.color_mode = "RGBA"
    scene.eevee.taa_render_samples = 8
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "_compare_tmp.png")

    for name in names:
        photo_name, loc, target, lens, roll, shx, shy = VIEWS[name]
        if override:
            loc, target, lens, roll, shx, shy = (override[k] for k in ("loc", "target", "lens", "roll", "shx", "shy"))
        probe = bpy.data.images.load(os.path.join(REF_DIR, photo_name))
        height = int(round(W * probe.size[1] / probe.size[0]))
        bpy.data.images.remove(probe)
        photo = load_photo(photo_name, height)
        scene.render.resolution_x = W
        scene.render.resolution_y = height
        cam.location = loc
        cam.data.lens = lens
        cam.data.sensor_width = 36.0
        cam.data.shift_x = shx
        cam.data.shift_y = shy
        quat = (Vector(target) - cam.location).to_track_quat("-Z", "Y")
        cam.rotation_euler = quat.to_euler()
        cam.rotation_euler.rotate_axis("Z", math.radians(roll))

        # Pass 1: normal render (for the blend and the outline).
        full = render_array(scene, tmp)
        body_mask = full[..., 3] > 0.5
        # Pass 2: everything painted white except the dark parts -> dark-part mask.
        saved = {}
        dark = {"laguna2_glass", "laguna2_black", "laguna2_trim", "laguna2_tire", "laguna2_gap"}
        for m in bpy.data.materials:
            if not m.name.startswith("laguna2_"):
                continue
            sh = m.node_tree.nodes.get("Principled BSDF")
            saved[m.name] = (tuple(sh.inputs["Base Color"].default_value), sh.inputs["Alpha"].default_value,
                             sh.inputs["Emission Strength"].default_value, tuple(sh.inputs["Emission Color"].default_value))
            col = (0, 0, 0, 1) if m.name in dark else (1, 1, 1, 1)
            sh.inputs["Base Color"].default_value = col
            sh.inputs["Alpha"].default_value = 1.0
            sh.inputs["Emission Color"].default_value = col
            sh.inputs["Emission Strength"].default_value = 3.0
        flat = render_array(scene, tmp)
        for m in bpy.data.materials:
            if m.name in saved:
                sh = m.node_tree.nodes.get("Principled BSDF")
                col, alpha, es, ec = saved[m.name]
                sh.inputs["Base Color"].default_value = col
                sh.inputs["Alpha"].default_value = alpha
                sh.inputs["Emission Strength"].default_value = es
                sh.inputs["Emission Color"].default_value = ec
        dark_mask = body_mask & (flat[..., :3].mean(axis=2) < 0.25)

        lines = photo[..., :3].copy()
        lines[edge(dark_mask)] = (0.0, 1.0, 1.0)
        lines[edge(body_mask)] = (0.1, 1.0, 0.1)
        save(lines, os.path.join(OUT_DIR, f"compare_{name}.png"))
        mix = photo[..., :3].copy()
        a = full[..., 3:4]
        mix = mix * (1 - 0.5 * a) + full[..., :3] * 0.5 * a
        save(mix, os.path.join(OUT_DIR, f"compare_{name}_blend.png"))
    if os.path.exists(tmp):
        os.remove(tmp)


if __name__ == "__main__":
    main()
