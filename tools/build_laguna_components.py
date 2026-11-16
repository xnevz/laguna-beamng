"""
Build Modular Renault Laguna II 3D Components in Blender (Live Viewport)
Creates separated body panels, hood, bumpers, glass, lights, interior, and wheels.
"""

import bpy
import bmesh
import math
import os

def build_laguna_parts():
    print("[Laguna Builder] Starting procedural part generation for Renault Laguna II...")

    # Ensure Object Mode
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Get target collection
    col_target = bpy.data.collections.get("02_Laguna_II_2001")
    if not col_target:
        col_target = bpy.context.scene.collection

    col_wheels = bpy.data.collections.get("06_Wheels_Tires")
    if not col_wheels:
        col_wheels = bpy.context.scene.collection

    col_interior = bpy.data.collections.get("02_Laguna_II_2001")

    # Materials
    def get_or_create_mat(name, color, metallic=0.0, roughness=0.5, alpha=1.0):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name=name)
            mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = color
            bsdf.inputs['Metallic'].default_value = metallic
            bsdf.inputs['Roughness'].default_value = roughness
            if alpha < 1.0:
                bsdf.inputs['Alpha'].default_value = alpha
                mat.blend_method = 'BLEND'
        return mat

    mat_paint = get_or_create_mat("laguna_paint", (0.05, 0.20, 0.55, 1.0), metallic=0.8, roughness=0.25) # Bleu Iliade
    mat_plastic = get_or_create_mat("laguna_plastic", (0.04, 0.04, 0.04, 1.0), metallic=0.0, roughness=0.85) # Black bumpers/trim
    mat_glass = get_or_create_mat("laguna_glass", (0.1, 0.15, 0.2, 0.35), metallic=0.1, roughness=0.05, alpha=0.35)
    mat_lights_f = get_or_create_mat("laguna_lights_F", (0.95, 0.95, 1.0, 1.0), metallic=0.2, roughness=0.1)
    mat_lights_r = get_or_create_mat("laguna_lights_R", (0.8, 0.02, 0.02, 1.0), metallic=0.1, roughness=0.2)
    mat_chrome = get_or_create_mat("laguna_chrome", (0.9, 0.9, 0.92, 1.0), metallic=0.98, roughness=0.05)
    mat_tire = get_or_create_mat("laguna_tire", (0.03, 0.03, 0.03, 1.0), metallic=0.0, roughness=0.9)
    mat_interior = get_or_create_mat("laguna_interior", (0.15, 0.15, 0.16, 1.0), metallic=0.05, roughness=0.8)

    # Clean existing generated parts
    existing_parts = [
        "laguna_body_unibody", "laguna_hood", "laguna_bumper_F", "laguna_bumper_R",
        "laguna_door_FL", "laguna_door_FR", "laguna_door_RL", "laguna_door_RR",
        "laguna_glass_windshield", "laguna_glass_rear", "laguna_glass_sides",
        "laguna_headlight_L", "laguna_headlight_R", "laguna_taillight_L", "laguna_taillight_R",
        "laguna_wheel_FL", "laguna_wheel_FR", "laguna_wheel_RL", "laguna_wheel_RR",
        "laguna_dash", "laguna_steeringwheel", "laguna_seats"
    ]
    for obj_name in existing_parts:
        if obj_name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[obj_name], do_unlink=True)

    # 1. FRONT HOOD / BONNET
    # Laguna II has a prominent aerodynamic sloping hood with center crease
    bm_hood = bmesh.new()
    # Profile grid for hood: length 1.0m to 1.85m Y, width +/-0.72m X
    hood_y = [1.05, 1.30, 1.55, 1.85]
    hood_rings = []
    for y in hood_y:
        progress = (y - 1.05) / 0.80
        z = 0.88 - progress * 0.14
        w = 0.72 - progress * 0.06
        ring = [
            bm_hood.verts.new((-w, y, z)),
            bm_hood.verts.new((-w * 0.5, y, z + 0.02)),
            bm_hood.verts.new((0.0, y, z + 0.035)),  # Center ridge
            bm_hood.verts.new((w * 0.5, y, z + 0.02)),
            bm_hood.verts.new((w, y, z))
        ]
        hood_rings.append(ring)
    for i in range(len(hood_rings) - 1):
        for j in range(4):
            bm_hood.faces.new([hood_rings[i][j], hood_rings[i+1][j], hood_rings[i+1][j+1], hood_rings[i][j+1]])

    hood_mesh = bpy.data.meshes.new("laguna_hood_mesh")
    bm_hood.to_mesh(hood_mesh)
    bm_hood.free()
    hood_obj = bpy.data.objects.new("laguna_hood", hood_mesh)
    col_target.objects.link(hood_obj)
    hood_mesh.materials.append(mat_paint)

    # 2. FRONT BUMPER with lower intake & badge surround
    bm_bf = bmesh.new()
    bf_z = [0.28, 0.45, 0.65, 0.75]
    bf_rings = []
    for z in bf_z:
        prog = (z - 0.28) / 0.47
        y = 2.25 - prog * 0.38
        w = 0.78 + prog * 0.06
        r = [
            bm_bf.verts.new((-w, y - 0.20, z)),
            bm_bf.verts.new((-w * 0.7, y, z)),
            bm_bf.verts.new((0.0, y + 0.04, z)),
            bm_bf.verts.new((w * 0.7, y, z)),
            bm_bf.verts.new((w, y - 0.20, z))
        ]
        bf_rings.append(r)
    for i in range(len(bf_rings) - 1):
        for j in range(4):
            bm_bf.faces.new([bf_rings[i][j], bf_rings[i+1][j], bf_rings[i+1][j+1], bf_rings[i][j+1]])

    bf_mesh = bpy.data.meshes.new("laguna_bumper_F_mesh")
    bm_bf.to_mesh(bf_mesh)
    bm_bf.free()
    bf_obj = bpy.data.objects.new("laguna_bumper_F", bf_mesh)
    col_target.objects.link(bf_obj)
    bf_mesh.materials.append(mat_paint)
    bf_mesh.materials.append(mat_plastic)

    # 3. REAR BUMPER
    bm_br = bmesh.new()
    br_z = [0.32, 0.50, 0.68, 0.78]
    br_rings = []
    for z in br_z:
        prog = (z - 0.32) / 0.46
        y = -2.28 + prog * 0.40
        w = 0.78 + prog * 0.05
        r = [
            bm_br.verts.new((-w, y + 0.22, z)),
            bm_br.verts.new((-w * 0.7, y, z)),
            bm_br.verts.new((0.0, y - 0.03, z)),
            bm_br.verts.new((w * 0.7, y, z)),
            bm_br.verts.new((w, y + 0.22, z))
        ]
        br_rings.append(r)
    for i in range(len(br_rings) - 1):
        for j in range(4):
            bm_br.faces.new([br_rings[i][j], br_rings[i+1][j], br_rings[i+1][j+1], br_rings[i][j+1]])

    br_mesh = bpy.data.meshes.new("laguna_bumper_R_mesh")
    bm_br.to_mesh(br_mesh)
    bm_br.free()
    br_obj = bpy.data.objects.new("laguna_bumper_R", br_mesh)
    col_target.objects.link(br_obj)
    br_mesh.materials.append(mat_paint)
    br_mesh.materials.append(mat_plastic)

    # 4. HEADLIGHTS (Distinctive sharp triangular/trapezoid Laguna II clusters)
    for side, sign in [("L", -1), ("R", 1)]:
        bm_hl = bmesh.new()
        v1 = bm_hl.verts.new((sign * 0.45, 1.86, 0.74))
        v2 = bm_hl.verts.new((sign * 0.78, 1.70, 0.73))
        v3 = bm_hl.verts.new((sign * 0.76, 1.72, 0.65))
        v4 = bm_hl.verts.new((sign * 0.46, 1.87, 0.64))
        bm_hl.faces.new([v1, v2, v3, v4] if sign == -1 else [v4, v3, v2, v1])
        hl_mesh = bpy.data.meshes.new(f"laguna_headlight_{side}_mesh")
        bm_hl.to_mesh(hl_mesh)
        bm_hl.free()
        hl_obj = bpy.data.objects.new(f"laguna_headlight_{side}", hl_mesh)
        col_target.objects.link(hl_obj)
        hl_mesh.materials.append(mat_lights_f)

    # 5. TAILLIGHTS (High mounted vertical/horizontal wraparound)
    for side, sign in [("L", -1), ("R", 1)]:
        bm_tl = bmesh.new()
        v1 = bm_tl.verts.new((sign * 0.50, -1.90, 0.88))
        v2 = bm_tl.verts.new((sign * 0.82, -1.82, 0.87))
        v3 = bm_tl.verts.new((sign * 0.83, -1.84, 0.76))
        v4 = bm_tl.verts.new((sign * 0.52, -1.92, 0.77))
        bm_tl.faces.new([v1, v2, v3, v4] if sign == 1 else [v4, v3, v2, v1])
        tl_mesh = bpy.data.meshes.new(f"laguna_taillight_{side}_mesh")
        bm_tl.to_mesh(tl_mesh)
        bm_tl.free()
        tl_obj = bpy.data.objects.new(f"laguna_taillight_{side}", tl_mesh)
        col_target.objects.link(tl_obj)
        tl_mesh.materials.append(mat_lights_r)

    # 6. GLASS (Windshield, Rear Hatch Window, Side Windows)
    # Windshield
    bm_ws = bmesh.new()
    v_ws = [
        bm_ws.verts.new((-0.68, 0.98, 0.89)),
        bm_ws.verts.new((0.68, 0.98, 0.89)),
        bm_ws.verts.new((0.58, 0.35, 1.36)),
        bm_ws.verts.new((-0.58, 0.35, 1.36))
    ]
    bm_ws.faces.new(v_ws)
    ws_mesh = bpy.data.meshes.new("laguna_glass_windshield_mesh")
    bm_ws.to_mesh(ws_mesh)
    bm_ws.free()
    ws_obj = bpy.data.objects.new("laguna_glass_windshield", ws_mesh)
    col_target.objects.link(ws_obj)
    ws_mesh.materials.append(mat_glass)

    # Rear Hatch Window
    bm_rw = bmesh.new()
    v_rw = [
        bm_rw.verts.new((-0.58, -0.92, 1.35)),
        bm_rw.verts.new((0.58, -0.92, 1.35)),
        bm_rw.verts.new((0.65, -1.75, 1.02)),
        bm_rw.verts.new((-0.65, -1.75, 1.02))
    ]
    bm_rw.faces.new(v_rw)
    rw_mesh = bpy.data.meshes.new("laguna_glass_rear_mesh")
    bm_rw.to_mesh(rw_mesh)
    bm_rw.free()
    rw_obj = bpy.data.objects.new("laguna_glass_rear", rw_mesh)
    col_target.objects.link(rw_obj)
    rw_mesh.materials.append(mat_glass)

    # 7. WHEELS & TIRES (Factory 16" / 17" Silverstone Laguna alloys)
    # Wheelbase = 2.741m: Front axle at Y = +1.370m, Rear axle at Y = -1.371m
    # Track width = 1.528m (X = +/- 0.764m), Ground radius = 0.315m (Z = 0.315m)
    wheel_positions = [
        ("laguna_wheel_FL", (-0.764, 1.370, 0.315)),
        ("laguna_wheel_FR", (0.764, 1.370, 0.315)),
        ("laguna_wheel_RL", (-0.764, -1.371, 0.315)),
        ("laguna_wheel_RR", (0.764, -1.371, 0.315))
    ]

    for name, pos in wheel_positions:
        # Create cylinder for wheel
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=20,
            radius=0.315,
            depth=0.215,
            location=pos,
            rotation=(0, 1.570796, 0)
        )
        wheel_obj = bpy.context.active_object
        wheel_obj.name = name
        # Move to wheels collection
        for col in wheel_obj.users_collection:
            col.objects.unlink(wheel_obj)
        col_wheels.objects.link(wheel_obj)

        wheel_obj.data.materials.append(mat_tire)
        wheel_obj.data.materials.append(mat_chrome)

    # 8. INTERIOR DASHBOARD & STEERING WHEEL
    # Dashboard binnacle
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0.0, 0.45, 0.85)
    )
    dash_obj = bpy.context.active_object
    dash_obj.name = "laguna_dash"
    dash_obj.scale = (1.30, 0.40, 0.25)
    bpy.ops.object.transform_apply(scale=True)
    for col in dash_obj.users_collection:
        col.objects.unlink(dash_obj)
    col_interior.objects.link(dash_obj)
    dash_obj.data.materials.append(mat_interior)

    # Steering Wheel (Left hand drive, X = -0.38m, Y = 0.32m, Z = 0.82m)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.18,
        minor_radius=0.022,
        location=(-0.38, 0.32, 0.82),
        rotation=(0.4, 0, 0)
    )
    steer_obj = bpy.context.active_object
    steer_obj.name = "laguna_steeringwheel"
    for col in steer_obj.users_collection:
        col.objects.unlink(steer_obj)
    col_interior.objects.link(steer_obj)
    steer_obj.data.materials.append(mat_interior)
    steer_obj.data.materials.append(mat_chrome)

    # Apply smooth shading to all parts
    all_created = [hood_obj, bf_obj, br_obj, ws_obj, rw_obj, dash_obj, steer_obj]
    for obj in all_created:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.shade_smooth()
        obj.select_set(False)

    print("[Laguna Builder] All components generated and linked to scene successfully!")

if __name__ == "__main__":
    build_laguna_parts()
