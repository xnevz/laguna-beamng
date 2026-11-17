"""Night renders of every light state of the Laguna II (what BeamNG's glowMap will switch).

Run:  blender --background blender/laguna2_liftback.blend --python tools/laguna2/render_lights.py -- [--draft]

Dims the studio from render.py to near darkness, then for each state in
lights.STATES sets every light material to off / on / on_intense exactly as the
glowMap would (lights.level), adds real light sources so the lamps throw light
(headlamp and fog beams, red / amber / white spill) and a glare pass for glow.

Writes renders/lights_front_<state>.png, renders/lights_rear_<state>.png and a
labelled contact sheet for each end: renders/lights_front_sheet.png, lights_rear_sheet.png.
"""

import math
import os
import sys

import bpy
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lights  # noqa: E402
import render as stage  # noqa: E402

OUT_DIR = stage.OUT_DIR
FRONT_STATES = ["off", "sidelights", "lowbeam", "highbeam", "fog", "signal_left", "hazards"]
REAR_STATES = ["off", "sidelights", "lights_and_brake", "brake", "reverse", "signal_left", "hazards"]
CAMS = {
    "front": ((3.6, -7.4, 1.55), (0.15, -2.6, 0.40), 34),
    "rear": ((-3.3, 7.2, 1.55), (-0.1, 2.4, 0.45), 34),
}
LABELS = {
    "off": "lights off", "sidelights": "sidelights / tail lights", "lowbeam": "low beam",
    "highbeam": "high beam", "fog": "low beam + fog lamps", "signal_left": "left indicator",
    "hazards": "hazard lights", "lights_and_brake": "tail lights + brake", "brake": "brake (lights off)",
    "reverse": "reversing lights",
}


# --------------------------------------------------------------------------
def light_positions():
    """(material, side) -> (centre, outward normal) of the faces using that light material."""
    acc = {}
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH" or not obj.name.startswith("Laguna2_") or obj.hide_render:
            continue
        mw = obj.matrix_world
        nm = mw.to_3x3().inverted().transposed()
        for poly in obj.data.polygons:
            if poly.material_index >= len(obj.material_slots):
                continue
            mat = obj.material_slots[poly.material_index].material
            if mat is None or mat.name not in lights.GLOW:
                continue
            c = mw @ poly.center
            side = "L" if c.x > 0.15 else ("R" if c.x < -0.15 else "C")
            a = poly.area
            s = acc.setdefault((mat.name, side), [Vector(), Vector(), 0.0])
            s[0] += c * a
            s[1] += (nm @ poly.normal) * a
            s[2] += a
    return {k: (v[0] / v[2], v[1].normalized()) for k, v in acc.items() if v[2] > 0}


def add_light(name, kind, loc, aim, color, size_deg=60.0, radius=0.02):
    data = bpy.data.lights.new(name, kind)
    data.color = color
    data.energy = 0.0
    if kind == "SPOT":
        data.spot_size = math.radians(size_deg)
        data.spot_blend = 0.6
    data.shadow_soft_size = radius
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = Vector(aim).to_track_quat("-Z", "Y").to_euler()
    return obj


def build_light_rig(pos):
    """Real lamps for the scene; returns [(light object, material, energy on, energy intense)]."""
    rig = []
    fwd, back = Vector((0, -1, -0.045)), Vector((0, 1, -0.10))
    for side in ("L", "R"):
        for mat, aim, w, size in (("laguna2_hl_low_lens", fwd, 220.0, 55.0), ("laguna2_hl_high", Vector((0, -1, -0.02)), 350.0, 30.0),
                                  ("laguna2_fog", Vector((0, -1, -0.05)), 160.0, 85.0)):
            if (mat, side) in pos:
                c, _n = pos[(mat, side)]
                rig.append((add_light(f"Night_{mat}_{side}", "SPOT", c + Vector((0, -0.08, 0)), aim,
                                      lights.GLOW[mat][1], size), mat, w, w))
        for mat, w1, w2 in (("laguna2_tail_lens_red", 1.5, 6.0), ("laguna2_tail_signal_" + side, 4.0, 4.0),
                            ("laguna2_hl_signal_" + side, 4.0, 4.0), ("laguna2_repeater_" + side, 1.5, 1.5),
                            ("laguna2_hl_position", 0.6, 0.6)):
            key = (mat, side)
            if key in pos:
                c, n = pos[key]
                rig.append((add_light(f"Night_{mat}_{side}", "POINT", c + n * 0.10, n, lights.GLOW[mat][1]), mat, w1, w2))
        if ("laguna2_reverse", side) in pos:
            c, _n = pos[("laguna2_reverse", side)]
            rig.append((add_light(f"Night_reverse_{side}", "SPOT", c + Vector((0, 0.08, 0)), back,
                                  lights.GLOW["laguna2_reverse"][1], 80.0), "laguna2_reverse", 90.0, 90.0))
    for key, w in ((("laguna2_brake3", "C"), 3.0), (("laguna2_platelight", "C"), 0.6),
                   (("laguna2_platelight", "L"), 0.4), (("laguna2_platelight", "R"), 0.4)):
        if key in pos:
            c, n = pos[key]
            rig.append((add_light(f"Night_{key[0]}_{key[1]}", "POINT", c + n * 0.08, n, lights.GLOW[key[0]][1]),
                        key[0], w, w))
    return rig


def dim_studio(scene):
    world = scene.world
    for node in world.node_tree.nodes:
        if node.type == "BACKGROUND":
            node.inputs[1].default_value = 0.035
    for obj in scene.objects:
        if obj.type == "LIGHT" and obj.name.startswith("Stage_"):
            obj.data.energy = 0.0          # night: no studio lights, no sun (its disc glints off the glass)
    scene.view_settings.exposure = 0.6


def add_glare(scene):
    """Bloom on the bright lamp surfaces (compositor)."""
    try:
        ng = bpy.data.node_groups.new("Night_Glare", "CompositorNodeTree")
        ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        rl = ng.nodes.new("CompositorNodeRLayers")
        gl = ng.nodes.new("CompositorNodeGlare")
        out = ng.nodes.new("NodeGroupOutput")
        for key, val in (("glare_type", "BLOOM"), ("quality", "HIGH")):
            try:
                setattr(gl, key, val)
            except Exception:
                pass
        for sock, val in (("Type", "Bloom"), ("Quality", "High"), ("Threshold", 1.5), ("Strength", 0.6),
                          ("Size", 0.6)):
            if sock in gl.inputs:
                try:
                    gl.inputs[sock].default_value = val
                except Exception:
                    pass
        ng.links.new(rl.outputs["Image"], gl.inputs["Image"])
        ng.links.new(gl.outputs[0], out.inputs[0])
        scene.compositing_node_group = ng
        scene.render.use_compositing = True
    except Exception as exc:  # pragma: no cover
        print("[warn] glare not available:", exc)


def add_label(cam):
    cu = bpy.data.curves.new("Night_Label", "FONT")
    cu.size = 0.022
    obj = bpy.data.objects.new("Night_Label", cu)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = cam
    obj.location = (-0.095, -0.05, -0.5)
    mat = bpy.data.materials.new("Night_Label")
    mat.use_nodes = True
    sh = mat.node_tree.nodes.get("Principled BSDF")
    sh.inputs["Base Color"].default_value = (1, 1, 1, 1)
    sh.inputs["Emission Color"].default_value = (1, 1, 1, 1)
    sh.inputs["Emission Strength"].default_value = 0.9     # below the glare threshold
    cu.materials.append(mat)
    return cu


def set_state(electrics, rig):
    for name, (_fn, glow, s1, s2) in lights.GLOW.items():
        mat = bpy.data.materials.get(name)
        if mat is None:
            continue
        sh = mat.node_tree.nodes.get("Principled BSDF")
        lv = lights.level(name, electrics)
        sh.inputs["Emission Color"].default_value = (glow[0], glow[1], glow[2], 1.0)
        sh.inputs["Emission Strength"].default_value = (0.0, s1, s2)[lv]
    for obj, mat, w1, w2 in rig:
        obj.data.energy = (0.0, w1, w2)[lights.level(mat, electrics)]


def contact_sheet(paths, out_path, cols=4):
    imgs = []
    for p in paths:
        im = bpy.data.images.load(p)
        w, h = im.size
        imgs.append(np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4))
        bpy.data.images.remove(im)
    h, w = imgs[0].shape[:2]
    h2, w2 = h // 2, w // 2
    rows = (len(imgs) + cols - 1) // cols
    sheet = np.zeros((rows * h2, cols * w2, 4), np.float32)
    sheet[..., 3] = 1.0
    for i, im in enumerate(imgs):
        small = im[::2, ::2][:h2, :w2]
        r, c = i // cols, i % cols
        y0 = (rows - 1 - r) * h2           # Blender images are stored bottom-up
        sheet[y0:y0 + h2, c * w2:(c + 1) * w2] = small
    out = bpy.data.images.new("sheet", sheet.shape[1], sheet.shape[0], alpha=False)
    out.pixels = sheet.ravel().tolist()
    out.filepath_raw = out_path
    out.file_format = "PNG"
    out.save()
    bpy.data.images.remove(out)
    print("[lights]", out_path)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    draft = "--draft" in argv
    cam = stage.setup(draft)
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = (1280, 720) if draft else (1600, 900)
    try:
        scene.eevee.taa_render_samples = 32 if draft else 64
    except Exception:
        pass
    dim_studio(scene)
    add_glare(scene)
    rig = build_light_rig(light_positions())
    label = add_label(cam)
    os.makedirs(OUT_DIR, exist_ok=True)
    for end, states in (("front", FRONT_STATES), ("rear", REAR_STATES)):
        loc, target, lens = CAMS[end]
        cam.location = loc
        cam.data.lens = lens
        stage.look_at(cam, target)
        paths = []
        for state in states:
            set_state(lights.STATES[state], rig)
            label.body = f"{end.upper()}  -  {LABELS[state]}"
            path = os.path.join(OUT_DIR, f"lights_{end}_{state}.png")
            scene.render.filepath = path
            bpy.ops.render.render(write_still=True)
            print("[lights]", path)
            paths.append(path)
        contact_sheet(paths, os.path.join(OUT_DIR, f"lights_{end}_sheet.png"))


if __name__ == "__main__":
    main()
