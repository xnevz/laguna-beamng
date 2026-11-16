"""Export the Laguna II vehicle mesh as a BeamNG-compatible COLLADA flexbody."""

import os
import re
import xml.etree.ElementTree as ET

import bmesh
import bpy


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = os.path.join(
    PROJECT_ROOT, "vehicles", "renault_laguna", "renault_laguna.dae"
)
FLEXBODY_NAME = "laguna_gen2_body"
DEFAULT_MATERIAL = "Laguna_Champagne_Silver"


def _exportable(obj):
    return (
        obj.type == "MESH"
        and not obj.hide_render
        and not obj.hide_viewport
        and not obj.name.startswith(("Ref_", "Studio_", "Preview_"))
        and not obj.name.endswith("_Bounds")
        and obj.name != "Hood_Nose_Beak"
    )


def _material_id(name):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", name)


def _material_color(material):
    color = tuple(material.diffuse_color)
    if material.use_nodes and material.node_tree:
        shader = material.node_tree.nodes.get("Principled BSDF")
        if shader:
            socket = shader.inputs.get("Base Color")
            if socket:
                color = tuple(socket.default_value)
    return color


def export_dae(filepath=OUTPUT_PATH):
    objects = [obj for obj in bpy.context.scene.objects if _exportable(obj)]
    if not objects:
        raise RuntimeError("No visible vehicle mesh objects were found to export.")

    positions = []
    triangles_by_material = {}
    material_data = {}
    depsgraph = bpy.context.evaluated_depsgraph_get()

    for obj in objects:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            bm = bmesh.new()
            bm.from_mesh(mesh)
            bmesh.ops.triangulate(bm, faces=bm.faces[:])
            bm.to_mesh(mesh)
            bm.free()

            vertex_offset = len(positions) // 3
            for vertex in mesh.vertices:
                world_co = obj.matrix_world @ vertex.co
                # The authored Laguna faces -Y; BeamNG's vehicle forward axis is +Y.
                positions.extend((world_co.x, -world_co.y, world_co.z))

            for polygon in mesh.polygons:
                slot_index = polygon.material_index
                material = (
                    obj.material_slots[slot_index].material
                    if slot_index < len(obj.material_slots)
                    else None
                )
                material_name = material.name if material else DEFAULT_MATERIAL
                material_data[material_name] = material
                indices = list(polygon.vertices)
                for index in range(1, len(indices) - 1):
                    # Mirroring the Y axis reverses winding; swap two vertices.
                    triangle = (
                        vertex_offset + indices[0],
                        vertex_offset + indices[index + 1],
                        vertex_offset + indices[index],
                    )
                    triangles_by_material.setdefault(material_name, []).extend(
                        triangle
                    )
        finally:
            evaluated.to_mesh_clear()

    if not positions or not triangles_by_material:
        raise RuntimeError("The visible vehicle meshes contained no exportable faces.")

    root = ET.Element(
        "COLLADA",
        {
            "xmlns": "http://www.collada.org/2005/11/COLLADASchema",
            "version": "1.4.1",
        },
    )
    asset = ET.SubElement(root, "asset")
    contributor = ET.SubElement(asset, "contributor")
    ET.SubElement(contributor, "author").text = "Antigravity & Abdelkarim"
    ET.SubElement(contributor, "authoring_tool").text = "Blender BeamNG Pipeline"
    ET.SubElement(asset, "unit", {"name": "meter", "meter": "1.0"})
    ET.SubElement(asset, "up_axis").text = "Z_UP"

    effects = ET.SubElement(root, "library_effects")
    materials = ET.SubElement(root, "library_materials")
    geometries = ET.SubElement(root, "library_geometries")
    visual_scenes = ET.SubElement(root, "library_visual_scenes")
    visual_scene = ET.SubElement(
        visual_scenes, "visual_scene", {"id": "Scene", "name": "Scene"}
    )

    material_ids = {}
    for name in sorted(triangles_by_material):
        material_id = _material_id(name)
        material_ids[name] = material_id
        color = _material_color(material_data[name]) if material_data[name] else (
            0.72, 0.70, 0.66, 1.0
        )

        effect = ET.SubElement(effects, "effect", {"id": material_id + "-effect"})
        profile = ET.SubElement(effect, "profile_COMMON")
        technique = ET.SubElement(profile, "technique", {"sid": "common"})
        phong = ET.SubElement(technique, "phong")
        diffuse = ET.SubElement(phong, "diffuse")
        ET.SubElement(diffuse, "color", {"sid": "diffuse"}).text = " ".join(
            f"{value:.6g}" for value in color
        )
        transparency = ET.SubElement(phong, "transparency")
        ET.SubElement(transparency, "float").text = f"{color[3]:.6g}"

        material = ET.SubElement(
            materials, "material", {"id": material_id + "-material", "name": name}
        )
        ET.SubElement(
            material, "instance_effect", {"url": "#" + material_id + "-effect"}
        )

    geometry_id = FLEXBODY_NAME + "-mesh"
    geometry = ET.SubElement(
        geometries, "geometry", {"id": geometry_id, "name": FLEXBODY_NAME}
    )
    mesh_element = ET.SubElement(geometry, "mesh")
    source_id = geometry_id + "-positions"
    source = ET.SubElement(mesh_element, "source", {"id": source_id})
    array = ET.SubElement(
        source,
        "float_array",
        {"id": source_id + "-array", "count": str(len(positions))},
    )
    array.text = " ".join(f"{value:.6f}" for value in positions)
    common = ET.SubElement(source, "technique_common")
    accessor = ET.SubElement(
        common,
        "accessor",
        {"source": "#" + source_id + "-array", "count": str(len(positions) // 3), "stride": "3"},
    )
    for axis in ("X", "Y", "Z"):
        ET.SubElement(accessor, "param", {"name": axis, "type": "float"})

    vertices_id = geometry_id + "-vertices"
    vertices = ET.SubElement(mesh_element, "vertices", {"id": vertices_id})
    ET.SubElement(
        vertices, "input", {"semantic": "POSITION", "source": "#" + source_id}
    )

    for name, indices in sorted(triangles_by_material.items()):
        ET.SubElement(
            mesh_element,
            "triangles",
            {
                "count": str(len(indices) // 3),
                "material": material_ids[name],
            },
        )
        triangles = mesh_element[-1]
        ET.SubElement(
            triangles,
            "input",
            {"semantic": "VERTEX", "source": "#" + vertices_id, "offset": "0"},
        )
        ET.SubElement(triangles, "p").text = " ".join(map(str, indices))

    node = ET.SubElement(
        visual_scene,
        "node",
        {"id": FLEXBODY_NAME, "name": FLEXBODY_NAME, "type": "NODE"},
    )
    instance = ET.SubElement(
        node,
        "instance_geometry",
        {"url": "#" + geometry_id, "name": FLEXBODY_NAME},
    )
    binding = ET.SubElement(instance, "bind_material")
    common_binding = ET.SubElement(binding, "technique_common")
    for name in sorted(triangles_by_material):
        ET.SubElement(
            common_binding,
            "instance_material",
            {
                "symbol": material_ids[name],
                "target": "#" + material_ids[name] + "-material",
            },
        )

    scene = ET.SubElement(root, "scene")
    ET.SubElement(scene, "instance_visual_scene", {"url": "#Scene"})

    ET.indent(root, space="  ")
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    temporary_path = filepath + ".tmp"
    ET.ElementTree(root).write(
        temporary_path, encoding="utf-8", xml_declaration=True
    )
    os.replace(temporary_path, filepath)
    print(
        f"[BeamNG DAE Exporter] Exported {len(objects)} vehicle meshes as "
        f"{FLEXBODY_NAME}: {len(positions) // 3} vertices, "
        f"{sum(len(indices) // 3 for indices in triangles_by_material.values())} "
        f"triangles."
    )


if __name__ == "__main__":
    export_dae()
