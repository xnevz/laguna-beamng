"""
Model Laguna II Interior (Seats, Center Console, Shifter) & Engine Bay Components
Executes in live Blender 5.3 session.
"""

import bpy
import bmesh
import math
import os

def model_interior_and_mechanics():
    print("[Interior & Mechanics] Modeling seats, console, shifter, and engine bay...")

    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    col_interior = bpy.data.collections.get("02_Laguna_II_2001")
    if not col_interior:
        col_interior = bpy.context.scene.collection

    col_engine = bpy.data.collections.get("04_Engines_Powertrain")
    if not col_engine:
        col_engine = bpy.context.scene.collection

    def get_or_create_mat(name, color, metallic=0.0, roughness=0.5):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name=name)
            mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = color
            bsdf.inputs['Metallic'].default_value = metallic
            bsdf.inputs['Roughness'].default_value = roughness
        return mat

    mat_fabric = get_or_create_mat("laguna_seat_fabric", (0.12, 0.12, 0.13, 1.0), metallic=0.0, roughness=0.9)
    mat_console = get_or_create_mat("laguna_interior_dark", (0.08, 0.08, 0.09, 1.0), metallic=0.05, roughness=0.8)
    mat_leather = get_or_create_mat("laguna_leather", (0.05, 0.05, 0.05, 1.0), metallic=0.1, roughness=0.4)
    mat_chrome = get_or_create_mat("laguna_chrome", (0.95, 0.95, 0.97, 1.0), metallic=0.98, roughness=0.06)
    mat_engine_cover = get_or_create_mat("laguna_engine_cover", (0.06, 0.06, 0.06, 1.0), metallic=0.1, roughness=0.7)
    mat_metal_cast = get_or_create_mat("laguna_metal_cast", (0.45, 0.45, 0.47, 1.0), metallic=0.7, roughness=0.5)

    # 1. FRONT SEATS (Driver & Passenger)
    # LHD: Driver at X = -0.38m, Passenger at X = +0.38m. Y = 0.05m
    for seat_name, sx in [("laguna_seat_FL", -0.38), ("laguna_seat_FR", 0.38)]:
        if seat_name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[seat_name], do_unlink=True)

        # Seat cushion base
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(sx, 0.05, 0.45)
        )
        base = bpy.context.active_object
        base.name = seat_name
        base.scale = (0.48, 0.52, 0.14)
        bpy.ops.object.transform_apply(scale=True)
        for col in base.users_collection:
            col.objects.unlink(base)
        col_interior.objects.link(base)
        base.data.materials.append(mat_fabric)

        # Seat backrest (slanted back ~15 degrees)
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(sx, -0.22, 0.76),
            rotation=(0.26, 0, 0)
        )
        back = bpy.context.active_object
        back.name = f"{seat_name}_back"
        back.scale = (0.46, 0.12, 0.55)
        bpy.ops.object.transform_apply(scale=True)
        for col in back.users_collection:
            col.objects.unlink(back)
        col_interior.objects.link(back)
        back.data.materials.append(mat_fabric)

        # Headrest
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(sx, -0.30, 1.10),
            rotation=(0.26, 0, 0)
        )
        head = bpy.context.active_object
        head.name = f"{seat_name}_headrest"
        head.scale = (0.24, 0.10, 0.16)
        bpy.ops.object.transform_apply(scale=True)
        for col in head.users_collection:
            col.objects.unlink(head)
        col_interior.objects.link(head)
        head.data.materials.append(mat_fabric)

    # 2. REAR SEAT BENCH
    if "laguna_seat_R" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["laguna_seat_R"], do_unlink=True)

    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0.0, -0.95, 0.48)
    )
    rear_base = bpy.context.active_object
    rear_base.name = "laguna_seat_R"
    rear_base.scale = (1.36, 0.50, 0.16)
    bpy.ops.object.transform_apply(scale=True)
    for col in rear_base.users_collection:
        col.objects.unlink(rear_base)
    col_interior.objects.link(rear_base)
    rear_base.data.materials.append(mat_fabric)

    # Rear backrest
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0.0, -1.22, 0.78),
        rotation=(0.30, 0, 0)
    )
    rear_back = bpy.context.active_object
    rear_back.name = "laguna_seat_R_back"
    rear_back.scale = (1.34, 0.12, 0.54)
    bpy.ops.object.transform_apply(scale=True)
    for col in rear_back.users_collection:
        col.objects.unlink(rear_back)
    col_interior.objects.link(rear_back)
    rear_back.data.materials.append(mat_fabric)

    # 3. CENTER CONSOLE & GEAR SHIFTER
    if "laguna_console" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["laguna_console"], do_unlink=True)

    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0.0, 0.15, 0.48)
    )
    console = bpy.context.active_object
    console.name = "laguna_console"
    console.scale = (0.24, 0.85, 0.22)
    bpy.ops.object.transform_apply(scale=True)
    for col in console.users_collection:
        col.objects.unlink(console)
    col_interior.objects.link(console)
    console.data.materials.append(mat_console)

    # Gear shift stick + leather gaiter
    if "laguna_shifter" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["laguna_shifter"], do_unlink=True)

    bpy.ops.mesh.primitive_cone_add(
        vertices=16,
        radius1=0.06,
        radius2=0.018,
        depth=0.12,
        location=(0.0, 0.32, 0.64)
    )
    gaiter = bpy.context.active_object
    gaiter.name = "laguna_shifter"
    for col in gaiter.users_collection:
        col.objects.unlink(gaiter)
    col_interior.objects.link(gaiter)
    gaiter.data.materials.append(mat_leather)

    # Gear shift knob with 6-speed chrome cap
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=16,
        ring_count=12,
        radius=0.028,
        location=(0.0, 0.32, 0.72)
    )
    knob = bpy.context.active_object
    knob.name = "laguna_shifter_knob"
    for col in knob.users_collection:
        col.objects.unlink(knob)
    col_interior.objects.link(knob)
    knob.data.materials.append(mat_chrome)

    # 4. ENGINE BAY: RENAULT 1.9 dCi / 2.0 16V TRANSVERSE BLOCK & COVER
    if "laguna_engine_bay" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["laguna_engine_bay"], do_unlink=True)

    # Cast alloy cylinder block & transmission bellhousing (transverse layout)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(-0.05, 1.42, 0.52)
    )
    eng_block = bpy.context.active_object
    eng_block.name = "laguna_engine_bay"
    eng_block.scale = (0.68, 0.48, 0.38)
    bpy.ops.object.transform_apply(scale=True)
    for col in eng_block.users_collection:
        col.objects.unlink(eng_block)
    col_engine.objects.link(eng_block)
    eng_block.data.materials.append(mat_metal_cast)

    # Molded plastic acoustic top cover (embossed Renault styling)
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(-0.05, 1.42, 0.73)
    )
    cover = bpy.context.active_object
    cover.name = "laguna_engine_cover"
    cover.scale = (0.58, 0.42, 0.06)
    bpy.ops.object.transform_apply(scale=True)
    for col in cover.users_collection:
        col.objects.unlink(cover)
    col_engine.objects.link(cover)
    cover.data.materials.append(mat_engine_cover)

    # Radiator & dual cooling fan cowl
    if "laguna_radiator" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["laguna_radiator"], do_unlink=True)

    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0.0, 1.82, 0.55)
    )
    rad = bpy.context.active_object
    rad.name = "laguna_radiator"
    rad.scale = (0.72, 0.08, 0.40)
    bpy.ops.object.transform_apply(scale=True)
    for col in rad.users_collection:
        col.objects.unlink(rad)
    col_engine.objects.link(rad)
    rad.data.materials.append(mat_metal_cast)

    # Battery & air filter box
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0.42, 1.35, 0.65)
    )
    airbox = bpy.context.active_object
    airbox.name = "laguna_airbox"
    airbox.scale = (0.22, 0.28, 0.22)
    bpy.ops.object.transform_apply(scale=True)
    for col in airbox.users_collection:
        col.objects.unlink(airbox)
    col_engine.objects.link(airbox)
    airbox.data.materials.append(mat_engine_cover)

    print("[Interior & Mechanics] Generation completed successfully!")

if __name__ == "__main__":
    model_interior_and_mechanics()
