"""Render every BeamNG configuration (.pc) of the Laguna II as the game would assemble it.

Run:  blender --background blender/laguna2_liftback.blend --python tools/laguna2/render_configs.py -- [--draft]

For each .pc file: resolve its part tree (configured part, else slot default),
collect the flexbody meshes those parts load, show exactly the Blender objects
behind those meshes (export_dae.MESHES), put the chosen wheel on all four
corners, apply the configuration's paint, and render front and rear
three-quarter views.  Also renders the halogen / xenon low beam at night.

Writes renders/config_<name>_front34.png / _rear34.png, renders/configs_sheet.png
and renders/option_headlights_halogen_vs_xenon.png.
"""

import glob
import json
import os
import re
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "beamng"))
import export_dae  # noqa: E402
import lights  # noqa: E402
import render as stage  # noqa: E402
import render_lights  # noqa: E402
import validate  # noqa: E402

VEH = os.path.join(ROOT, "vehicles", "renault_laguna")
WHEEL_MESH_OBJECT = {"laguna2_wheel_alloy17": "Laguna2_WheelAlloy", "laguna2_wheel_steel15": "Laguna2_WheelSteel"}


def load_parts():
    parts = {}
    for f in glob.glob(os.path.join(VEH, "*.jbeam")):
        parts.update(validate.load_jbeam(f))
    return parts


def resolve(parts, chosen):
    main = next(n for n, p in parts.items() if p.get("slotType") == "main")
    active = []

    def walk(pn):
        active.append(pn)
        for row in (parts[pn].get("slots") or [])[1:]:
            if isinstance(row, list):
                pick = chosen.get(row[0], row[1])
                if pick and pick in parts:
                    walk(pick)

    walk(main)
    return active


def meshes_of(parts, active):
    out = []
    for pn in active:
        _h, rows = validate.table_rows(parts[pn].get("flexbodies"))
        out += [r[0] for r, _p in rows]
    return out


def objects_for(mesh):
    pats = export_dae.MESHES[mesh]
    return [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("Laguna2_")
            and any(re.fullmatch(p, o.name[len("Laguna2_"):]) for p in pats)]


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def apply_config(parts, pc):
    active = resolve(parts, pc.get("parts", {}))
    meshes = meshes_of(parts, active)
    show = set()
    wheel_mesh = None
    for m in meshes:
        if m in WHEEL_MESH_OBJECT:
            wheel_mesh = m
            continue
        show |= {o.name for o in objects_for(m)}
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith("Laguna2_"):
            continue
        if re.fullmatch(r"Laguna2_Wheel_(FL|FR|RL|RR)", o.name):
            o.hide_render = wheel_mesh is None
            if wheel_mesh:
                o.data = bpy.data.objects[WHEEL_MESH_OBJECT[wheel_mesh]].data
            continue
        o.hide_render = o.name not in show
    p = pc["paints"][0]
    sh = bpy.data.materials["laguna2_paint"].node_tree.nodes.get("Principled BSDF")
    sh.inputs["Base Color"].default_value = tuple(srgb_to_linear(c) for c in p["baseColor"][:3]) + (1.0,)
    sh.inputs["Metallic"].default_value = p.get("metallic", 0.5)
    sh.inputs["Roughness"].default_value = p.get("roughness", 0.35)
    return active


def contact_sheet(paths, out_path, cols=4):
    render_lights.contact_sheet(paths, out_path, cols)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    draft = "--draft" in argv
    parts = load_parts()
    cam = stage.setup(draft)
    scene = bpy.context.scene
    os.makedirs(stage.OUT_DIR, exist_ok=True)
    paths = []
    for pc_path in sorted(glob.glob(os.path.join(VEH, "*.pc"))):
        name = os.path.basename(pc_path)[:-3]
        pc = json.load(open(pc_path, encoding="utf-8"))
        info = json.load(open(os.path.join(VEH, f"info_{name}.json"), encoding="utf-8"))
        active = apply_config(parts, pc)
        print(f"[configs] {name}: {info['Configuration']} ({len(active)} parts)")
        for view in ("front34", "rear34"):
            loc, target, lens = stage.VIEWS[view]
            cam.location = loc
            cam.data.lens = lens
            stage.look_at(cam, target)
            path = os.path.join(stage.OUT_DIR, f"config_{name.replace('laguna2_', '')}_{view}.png")
            scene.render.filepath = path
            bpy.ops.render.render(write_still=True)
            paths.append(path)
    contact_sheet(paths, os.path.join(stage.OUT_DIR, "configs_sheet.png"), cols=4)

    # Halogen vs xenon low beam at night (same lamp, different lit colour).
    render_lights.dim_studio(scene)
    render_lights.add_glare(scene)
    rig = render_lights.build_light_rig(render_lights.light_positions())
    label = render_lights.add_label(cam)
    loc, target, lens = render_lights.CAMS["front"]
    cam.location = loc
    cam.data.lens = lens
    stage.look_at(cam, target)
    pair = []
    for variant in ("halogen", "xenon"):
        render_lights.set_state(lights.STATES["lowbeam"], rig)
        if variant == "xenon":
            for m, col in lights.XENON.items():
                sh = bpy.data.materials[m].node_tree.nodes.get("Principled BSDF")
                sh.inputs["Emission Color"].default_value = (*col, 1.0)
            for obj, mat, _w1, _w2 in rig:
                if mat in lights.XENON:
                    obj.data.color = lights.XENON[mat]
        label.body = f"LOW BEAM  -  {variant}"
        path = os.path.join(stage.OUT_DIR, f"_tmp_{variant}.png")
        scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
        pair.append(path)
    contact_sheet(pair, os.path.join(stage.OUT_DIR, "option_headlights_halogen_vs_xenon.png"), cols=2)
    for pth in pair:
        os.remove(pth)


if __name__ == "__main__":
    main()
