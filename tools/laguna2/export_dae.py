"""Export the Laguna II to the BeamNG vehicle folder: one COLLADA mesh per customisable part + materials.

Run:  blender --background blender/laguna2_liftback.blend --python tools/laguna2/export_dae.py
      (after build_from_ref.py and variants.py)

Coordinates are written as they are in Blender, which is already BeamNG's
vehicle frame: front of the car towards -Y, +X = the car's left, Z up.

Every Laguna2_* object must belong to at least one mesh in MESHES (the four
placed wheels Laguna2_Wheel_FL.. exist only for renders; the game uses the
wheel templates at the origin, placed by the wheel parts' flexbody "pos").
"""

import json
import os
import re
import sys
import xml.etree.ElementTree as ET

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lights  # noqa: E402

PROJECT_ROOT = os.path.dirname(os.path.dirname(HERE))
VEHICLE_DIR = os.path.join(PROJECT_ROOT, "vehicles", "renault_laguna")
DAE_PATH = os.path.join(VEHICLE_DIR, "renault_laguna.dae")
MATERIALS_PATH = os.path.join(VEHICLE_DIR, "materials.json")

# mesh name -> regexes of the Blender objects that make it up
MESHES = {
    "laguna2_body": [r"Body", r"Fender_[LR]", r"Door_(FL|FR|RL|RR)", r"ShutLines", r"ArchLiners", r"Underbody",
                     r"Exhaust", r"Repeaters", r"Trim"],
    "laguna2_hood": [r"Hood", r"BadgeFront"],
    "laguna2_bumper_F": [r"Bumper_F", r"Grille", r"GrilleInsert", r"GrilleBacking"],
    "laguna2_bumper_R": [r"Bumper_R", r"PlateLights"],
    "laguna2_tailgate": [r"Tailgate", r"BadgeHousing", r"BadgeRear", r"BrakeLight3"],
    "laguna2_lettering": [r"Lettering"],
    "laguna2_windscreen": [r"Windscreen"],
    "laguna2_glass_factory": [r"Glass"],
    "laguna2_glass_privacy": [r"Glass_Privacy"],
    "laguna2_glass_dark": [r"Glass_Dark"],
    "laguna2_headlights": [r"Headlamp[LR]_(Housing|Lens|Reflectors)"],
    "laguna2_taillights": [r"Taillamp[LR](Gate|Wing)_(Housing|Eyes|Lens)"],
    "laguna2_taillights_smoked": [r"Taillamp[LR](Gate|Wing)_(Housing|Eyes|LensSmoked)"],
    "laguna2_foglights": [r"FogLamps"],
    "laguna2_mirrors": [r"Mirror_[LR]", r"MirrorFoot_[LR]"],
    "laguna2_rearwiper": [r"RearWiper"],
    "laguna2_mouldings_black": [r"Mouldings"],
    "laguna2_mouldings_body": [r"Mouldings_Body"],
    "laguna2_parksensors": [r"ParkingSensors"],
    "laguna2_plate_F": [r"Plate_F", r"PlateText_F", r"PlateCountry_F"],
    "laguna2_plate_R": [r"Plate_R", r"PlateText_R", r"PlateCountry_R"],
    "laguna2_interior": [r"Int_.*"],
    "laguna2_wheel_alloy17": [r"WheelAlloy"],
    "laguna2_wheel_steel15": [r"WheelSteel"],
}
RENDER_ONLY = [r"Wheel_(FL|FR|RL|RR)"]

# The body paint takes its colour from the BeamNG paint picker.
PAINTED = {"laguna2_paint"}


def assign_objects():
    objs = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("Laguna2_")]
    groups = {m: [] for m in MESHES}
    for o in objs:
        short = o.name[len("Laguna2_"):]
        hits = [m for m, pats in MESHES.items() if any(re.fullmatch(p, short) for p in pats)]
        if any(re.fullmatch(p, short) for p in RENDER_ONLY):
            continue
        if not hits:
            raise SystemExit(f"[export] object {o.name} belongs to no mesh; add it to MESHES")
        for h in hits:                       # shared parts (e.g. tail-lamp housings) go in every variant
            groups[h].append(o)
    empty = [m for m, g in groups.items() if not g]
    if empty:
        raise SystemExit(f"[export] meshes with no objects: {empty} (did variants.py run?)")
    return groups


def collect(objects):
    """-> {material: (positions, normals)} as flat triangle soups, in world space."""
    out = {}
    dg = bpy.context.evaluated_depsgraph_get()
    for obj in objects:
        ev = obj.evaluated_get(dg)
        mesh = ev.to_mesh()
        mesh.calc_loop_triangles()
        mw = obj.matrix_world
        nm = mw.to_3x3().inverted().transposed()
        for lt in mesh.loop_triangles:
            slot = lt.material_index
            mat_ref = obj.material_slots[slot].material if slot < len(obj.material_slots) else None
            name = mat_ref.name if mat_ref else "laguna2_paint"
            pos, nor = out.setdefault(name, ([], []))
            for vi, n in zip(lt.vertices, lt.split_normals):
                p = mw @ mesh.vertices[vi].co
                nv = (nm @ Vector(n)).normalized()
                pos.extend((p.x, p.y, p.z))
                nor.extend((nv.x, nv.y, nv.z))
        ev.to_mesh_clear()
    return out


def add_geometry(lib, scene_node, name, data):
    gid = name + "-mesh"
    geom = ET.SubElement(lib, "geometry", {"id": gid, "name": name})
    mesh = ET.SubElement(geom, "mesh")
    positions, normals, ranges = [], [], []
    for mat_name in sorted(data):
        pos, nor = data[mat_name]
        ranges.append((mat_name, len(positions) // 3, len(pos) // 3))
        positions.extend(pos)
        normals.extend(nor)
    for sid, arr in (("positions", positions), ("normals", normals)):
        src = ET.SubElement(mesh, "source", {"id": f"{gid}-{sid}"})
        fa = ET.SubElement(src, "float_array", {"id": f"{gid}-{sid}-array", "count": str(len(arr))})
        fa.text = " ".join(f"{v:.5f}" for v in arr)
        acc = ET.SubElement(ET.SubElement(src, "technique_common"), "accessor",
                            {"source": f"#{gid}-{sid}-array", "count": str(len(arr) // 3), "stride": "3"})
        for axis in "XYZ":
            ET.SubElement(acc, "param", {"name": axis, "type": "float"})
    verts = ET.SubElement(mesh, "vertices", {"id": f"{gid}-vertices"})
    ET.SubElement(verts, "input", {"semantic": "POSITION", "source": f"#{gid}-positions"})
    for mat_name, start, count in ranges:
        tris = ET.SubElement(mesh, "triangles", {"count": str(count // 3), "material": mat_name})
        ET.SubElement(tris, "input", {"semantic": "VERTEX", "source": f"#{gid}-vertices", "offset": "0"})
        ET.SubElement(tris, "input", {"semantic": "NORMAL", "source": f"#{gid}-normals", "offset": "0"})
        ET.SubElement(tris, "p").text = " ".join(str(i) for i in range(start, start + count))
    node = ET.SubElement(scene_node, "node", {"id": name, "name": name, "type": "NODE"})
    inst = ET.SubElement(node, "instance_geometry", {"url": "#" + gid, "name": name})
    tc = ET.SubElement(ET.SubElement(inst, "bind_material"), "technique_common")
    for mat_name, _s, _c in ranges:
        ET.SubElement(tc, "instance_material", {"symbol": mat_name, "target": f"#{mat_name}-material"})
    return sum(c for _m, _s, c in ranges) // 3


def principled(material):
    sh = material.node_tree.nodes.get("Principled BSDF")
    get = lambda k, d: sh.inputs[k].default_value if k in sh.inputs else d
    c = get("Base Color", (0.5, 0.5, 0.5, 1))
    return dict(color=(c[0], c[1], c[2]), rough=get("Roughness", 0.5), metal=get("Metallic", 0.0),
                alpha=get("Alpha", 1.0), coat=get("Coat Weight", 0.0),
                emit=get("Emission Strength", 0.0), emit_color=tuple(get("Emission Color", (0, 0, 0, 1)))[:3])


def linear_to_srgb(c):
    return [round(v * 12.92 if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055, 4) for v in c]


def material_entry(name):
    p = principled(bpy.data.materials[name])
    stage = {
        "baseColorFactor": linear_to_srgb(p["color"]) + [round(p["alpha"], 3)],
        "roughnessFactor": round(p["rough"], 3),
        "metallicFactor": round(p["metal"], 3),
    }
    if p["coat"] > 0:
        stage["clearCoatFactor"] = round(p["coat"], 3)
        stage["clearCoatRoughnessFactor"] = 0.04
    if p["emit"] > 0:
        stage["emissiveFactor"] = linear_to_srgb([c * min(p["emit"], 1.0) for c in p["emit_color"]])
    if name in PAINTED:
        # Vehicle paint: white base tinted by the paint picker colour (instanceDiffuse).
        stage["baseColorFactor"] = [1.0, 1.0, 1.0, 1.0]
        stage["instanceDiffuse"] = True
    entry = {"name": name, "mapTo": name, "class": "Material", "Stages": [stage], "version": 1.5}
    if p["alpha"] < 1.0:
        stage["opacityFactor"] = round(p["alpha"], 3)
        entry["translucent"] = True
        entry["translucentBlendOp"] = "LerpAlpha"
        entry["translucentZWrite"] = True
    return entry


def lit(entry, name, glow, gain):
    out = json.loads(json.dumps(entry))
    out["name"] = out["mapTo"] = name
    st = out["Stages"][0]
    st["emissiveFactor"] = linear_to_srgb([c * gain for c in glow])
    st["glow"] = True
    return out


def write_materials(names):
    with open(MATERIALS_PATH, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    data = {k: v for k, v in data.items() if not k.startswith("laguna2_")}
    for name in sorted(names):
        entry = material_entry(name)
        data[name] = entry
        if name in lights.GLOW:
            glow = lights.GLOW[name][1]
            data[name + "_on"] = lit(entry, name + "_on", glow, 0.75)
            data[name + "_on_intense"] = lit(entry, name + "_on_intense", glow, 1.0)
        if name in lights.XENON:
            glow = lights.XENON[name]
            data[name + "_on_xenon"] = lit(entry, name + "_on_xenon", glow, 0.85)
            data[name + "_on_intense_xenon"] = lit(entry, name + "_on_intense_xenon", glow, 1.0)
    missing = [n for n in lights.GLOW if n not in data]
    if missing:
        raise SystemExit(f"[export] light materials used by no mesh: {missing}")
    with open(MATERIALS_PATH, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    return len(data)


def main():
    groups = assign_objects()
    root = ET.Element("COLLADA", {"xmlns": "http://www.collada.org/2005/11/COLLADASchema", "version": "1.4.1"})
    asset = ET.SubElement(root, "asset")
    ET.SubElement(ET.SubElement(asset, "contributor"), "authoring_tool").text = "laguna2 build (tools/laguna2)"
    ET.SubElement(asset, "unit", {"name": "meter", "meter": "1.0"})
    ET.SubElement(asset, "up_axis").text = "Z_UP"
    effects = ET.SubElement(root, "library_effects")
    materials = ET.SubElement(root, "library_materials")
    geoms = ET.SubElement(root, "library_geometries")
    vs = ET.SubElement(ET.SubElement(root, "library_visual_scenes"), "visual_scene", {"id": "Scene", "name": "Scene"})
    all_mats = set()
    report = []
    for mesh_name, objs in groups.items():
        data = collect(objs)
        all_mats |= set(data)
        report.append((mesh_name, add_geometry(geoms, vs, mesh_name, data)))
    for name in sorted(all_mats):
        p = principled(bpy.data.materials[name])
        eff = ET.SubElement(effects, "effect", {"id": name + "-effect"})
        phong = ET.SubElement(ET.SubElement(ET.SubElement(eff, "profile_COMMON"), "technique", {"sid": "common"}), "phong")
        ET.SubElement(ET.SubElement(phong, "diffuse"), "color", {"sid": "diffuse"}).text = " ".join(
            f"{v:.4f}" for v in (*p["color"], p["alpha"]))
        m = ET.SubElement(materials, "material", {"id": name + "-material", "name": name})
        ET.SubElement(m, "instance_effect", {"url": f"#{name}-effect"})
    ET.SubElement(ET.SubElement(root, "scene"), "instance_visual_scene", {"url": "#Scene"})
    ET.indent(root, space=" ")
    ET.ElementTree(root).write(DAE_PATH, encoding="utf-8", xml_declaration=True)
    n_mats = write_materials(all_mats)
    for mesh_name, tris in report:
        print(f"[export]   {mesh_name:28s} {tris:7d} tris")
    print(f"[export] {DAE_PATH}: {len(report)} meshes, {sum(t for _m, t in report)} tris; materials.json {n_mats} entries")
    with open(os.path.join(VEHICLE_DIR, ".mesh_index.json"), "w", encoding="utf-8") as fh:
        json.dump({m: t for m, t in report}, fh, indent=1)


if __name__ == "__main__":
    main()
