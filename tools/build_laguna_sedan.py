"""Convert the Laguna II hatchback scene into a clean sedan presentation model."""

import math
import os

import bmesh
import bpy


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER_PATH = os.path.join(PROJECT_ROOT, "blender", "laguna_master.blend")


def clamp(value, lower=0.0, upper=1.0):
    return max(lower, min(upper, value))


def smoothstep(edge0, edge1, value):
    t = clamp((value - edge0) / (edge1 - edge0))
    return t * t * (3.0 - 2.0 * t)


def rear_roof_shift(y, z):
    rear = smoothstep(0.25, 0.70, y) * (
        1.0 - smoothstep(1.50, 2.00, y)
    )
    height = smoothstep(0.76, 1.10, z)
    return 0.55 * rear * height


def material(name, color, roughness, metallic=0.0, alpha=1.0):
    result = bpy.data.materials.get(name)
    if result is None:
        result = bpy.data.materials.new(name)
    result.diffuse_color = color
    result.use_nodes = True
    shader = result.node_tree.nodes.get("Principled BSDF")
    if shader:
        shader.inputs["Base Color"].default_value = color
        shader.inputs["Roughness"].default_value = roughness
        shader.inputs["Metallic"].default_value = metallic
        shader.inputs["Alpha"].default_value = alpha
    if alpha < 1.0:
        result.surface_render_method = "BLENDED"
    return result


def mesh_object(name, vertices, faces, mat, smooth=True):
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)

    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    for polygon in mesh.polygons:
        polygon.use_smooth = smooth
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def add_rear_window(glass):
    vertices = []
    rows = 5
    columns = 5
    for row in range(rows):
        t = row / (rows - 1)
        width = 0.50 - 0.045 * t
        base_y = 0.68 + 0.76 * t
        base_z = 1.29 - 0.37 * t
        for column in range(columns):
            u = -1.0 + 2.0 * column / (columns - 1)
            vertices.append(
                (
                    width * u,
                    base_y + 0.028 * (1.0 - u * u),
                    base_z + 0.016 * (1.0 - u * u),
                )
            )

    faces = []
    for row in range(rows - 1):
        for column in range(columns - 1):
            a = row * columns + column
            faces.append((a, a + 1, a + columns + 1, a + columns))
    return mesh_object("Sedan_Rear_Window", vertices, faces, glass)


def add_trunk_lid(paint):
    stations = [
        (1.38, 0.50, 0.967),
        (1.58, 0.55, 0.970),
        (1.80, 0.60, 0.963),
        (2.02, 0.63, 0.951),
        (2.12, 0.62, 0.940),
    ]
    columns = 7
    vertices = []
    for y, width, edge_z in stations:
        for column in range(columns):
            u = -1.0 + 2.0 * column / (columns - 1)
            crown = 0.018 * (1.0 - u * u)
            vertices.append((width * u, y, edge_z + crown))

    faces = []
    for row in range(len(stations) - 1):
        for column in range(columns - 1):
            a = row * columns + column
            faces.append((a, a + columns, a + columns + 1, a + 1))
    return mesh_object("Sedan_Trunk_Lid", vertices, faces, paint)


def add_c_pillars(paint):
    for side, label in ((1.0, "R"), (-1.0, "L")):
        points = [
            (side * 0.49, 0.66, 1.28),
            (side * 0.60, 0.62, 1.28),
            (side * 0.73, 0.78, 1.17),
            (side * 0.75, 1.04, 0.88),
            (side * 0.48, 1.43, 0.91),
        ]
        mesh_object(
            "Sedan_C_Pillar_" + label,
            points,
            [(0, 1, 2, 3, 4)],
            paint,
            smooth=False,
        )


def add_b_pillars(trim):
    for side, label in ((1.0, "R"), (-1.0, "L")):
        x = side * 0.755
        vertices = [
            (x, 0.135, 0.81),
            (x, 0.215, 0.81),
            (x, 0.255, 1.20),
            (x, 0.205, 1.235),
            (x + side * 0.012, 0.135, 0.81),
            (x + side * 0.012, 0.215, 0.81),
            (x + side * 0.012, 0.255, 1.20),
            (x + side * 0.012, 0.205, 1.235),
        ]
        faces = [
            (0, 1, 2, 3),
            (4, 7, 6, 5),
            (0, 4, 5, 1),
            (1, 5, 6, 2),
            (2, 6, 7, 3),
            (3, 7, 4, 0),
        ]
        mesh_object("Sedan_B_Pillar_" + label, vertices, faces, trim)


def add_trunk_seam(trim):
    points = [
        (-0.50, 1.40, 0.990),
        (-0.32, 1.39, 0.995),
        (0.00, 1.385, 0.999),
        (0.32, 1.39, 0.995),
        (0.50, 1.40, 0.990),
    ]
    vertices = []
    faces = []
    half_width = 0.002
    for x, y, z in points:
        vertices.extend(
            [
                (x - half_width, y, z),
                (x + half_width, y, z),
                (x, y + half_width, z),
                (x, y - half_width, z),
            ]
        )
    for i in range(len(points) - 1):
        start = i * 4
        end = (i + 1) * 4
        faces.append((start, end, end + 1, start + 1))
    mesh_object("Sedan_Trunk_Seam", vertices, faces, trim, smooth=False)


def add_rear_lamps(ruby, clear):
    for side, label in ((1.0, "R"), (-1.0, "L")):
        vertices = [
            (side * 0.80, 1.99, 0.69),
            (side * 0.80, 2.20, 0.69),
            (side * 0.80, 2.20, 0.95),
            (side * 0.80, 1.99, 0.91),
            (side * 0.82, 1.99, 0.69),
            (side * 0.82, 2.20, 0.69),
            (side * 0.82, 2.20, 0.95),
            (side * 0.82, 1.99, 0.91),
        ]
        obj = mesh_object(
            "Sedan_Taillight_" + label,
            vertices,
            [(0, 1, 2, 3), (4, 7, 6, 5)],
            ruby,
            smooth=False,
        )
        obj.data.materials.append(clear)
        for polygon in obj.data.polygons:
            polygon.material_index = 0

        rear_vertices = [
            (side * 0.57, 2.155, 0.69),
            (side * 0.80, 2.155, 0.69),
            (side * 0.80, 2.155, 0.95),
            (side * 0.57, 2.155, 0.92),
            (side * 0.62, 2.162, 0.785),
            (side * 0.78, 2.162, 0.79),
            (side * 0.78, 2.162, 0.825),
            (side * 0.62, 2.162, 0.82),
        ]
        rear_obj = mesh_object(
            "Sedan_Taillight_Rear_" + label,
            rear_vertices,
            [(0, 1, 2, 3), (4, 5, 6, 7)],
            ruby,
            smooth=False,
        )
        rear_obj.data.materials.append(clear)
        rear_obj.data.polygons[1].material_index = 1


def build_sedan():
    paint = bpy.data.materials.get("Laguna_Champagne_Silver")
    if paint and paint.use_nodes:
        shader = paint.node_tree.nodes.get("Principled BSDF")
        if shader:
            shader.inputs["Base Color"].default_value = (0.62, 0.60, 0.56, 1.0)
            shader.inputs["Metallic"].default_value = 0.48
            shader.inputs["Roughness"].default_value = 0.30
            shader.inputs["Coat Weight"].default_value = 0.7
            shader.inputs["Coat Roughness"].default_value = 0.06

    if paint is None:
        paint = material(
            "Laguna_Champagne_Silver", (0.62, 0.60, 0.56, 1.0), 0.30, 0.48
        )
    trim = material("Laguna_Trim_Charcoal", (0.035, 0.04, 0.045, 1.0), 0.7)
    glass = material("Laguna_Glass_Tinted", (0.09, 0.13, 0.16, 0.66), 0.12, alpha=0.66)
    ruby = material("Laguna_Taillight_Ruby", (0.62, 0.018, 0.025, 1.0), 0.2)
    clear = material("Laguna_Taillight_Clear", (0.78, 0.82, 0.84, 0.82), 0.16, alpha=0.82)

    shell = bpy.data.objects.get("unnamed.004")
    if shell is None or shell.type != "MESH":
        raise RuntimeError("The Laguna II body shell 'unnamed.004' is missing.")
    for vertex in shell.data.vertices:
        vertex.co.y -= rear_roof_shift(vertex.co.y, vertex.co.z)
    shell.data.update()

    rear_glass_names = {
        "unnamed.027",
        "unnamed.030",
        "unnamed.155",
        "unnamed.219",
        "unnamed.171",
        "unnamed.172",
        "unnamed.178",
        "unnamed.179",
    }
    for name in rear_glass_names:
        obj = bpy.data.objects.get(name)
        if obj:
            obj.hide_render = True
            obj.hide_viewport = True

    for name in ("unnamed.170", "unnamed.177"):
        obj = bpy.data.objects.get(name)
        if obj and obj.type == "MESH":
            for vertex in obj.data.vertices:
                vertex.co.y -= 0.42 * rear_roof_shift(vertex.co.y, vertex.co.z)
            obj.data.update()
            obj.data.materials.clear()
            obj.data.materials.append(glass)

    for name in ("unnamed.060", "unnamed.066", "unnamed.164"):
        obj = bpy.data.objects.get(name)
        if obj:
            obj.data.materials.clear()
            obj.data.materials.append(glass)

    for obj in bpy.data.objects:
        if obj.name.startswith(("Sedan_", "Preview_")):
            bpy.data.objects.remove(obj, do_unlink=True)

    for name in (
        "Hood_Nose_Beak",
        "Bridge_Spoiler_Laguna2",
        "Roof_Antenna",
        "Rear_Wiper",
        "Taillight_Fill_L",
        "Taillight_Fill_R",
        "Taillight_Pupils_L",
        "Taillight_Pupils_R",
        "unnamed.010",
    ):
        obj = bpy.data.objects.get(name)
        if obj:
            obj.hide_render = True
            obj.hide_viewport = True

    for name in (
        "Moulding_Door_FL",
        "Moulding_Door_FR",
        "Moulding_Door_RL",
        "Moulding_Door_RR",
        "Bumper_Rub_Strip_Front",
        "Bumper_Rub_Strip_Rear",
    ):
        obj = bpy.data.objects.get(name)
        if obj:
            obj.data.materials.clear()
            obj.data.materials.append(trim)

    add_rear_window(glass)
    add_c_pillars(paint)
    add_b_pillars(trim)
    add_trunk_lid(paint)
    add_trunk_seam(trim)
    add_rear_lamps(ruby, clear)

    scene = bpy.context.scene
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.2
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=MASTER_PATH)
    print(f"[Sedan] Saved reference-matched Laguna II sedan scene: {MASTER_PATH}")


if __name__ == "__main__":
    build_sedan()
