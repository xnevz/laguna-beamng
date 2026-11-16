"""
High-Fidelity Renault Laguna II Exterior Modeling Script
Executes in live Blender 5.3 to generate authentic body panels, doors,
mirrors, badging, lights, wheel arches, and aero surfaces matching official photos.
"""

import bpy
import bmesh
import math
import os

def model_laguna2_detailed():
    print("[Laguna II Detailed Modeling] Starting high-fidelity geometry generation...")

    # Ensure Object Mode
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    col_target = bpy.data.collections.get("02_Laguna_II_2001")
    if not col_target:
        col_target = bpy.context.scene.collection

    # Materials helper
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

    # Materials
    mat_paint = get_or_create_mat("laguna_paint", (0.04, 0.18, 0.52, 1.0), metallic=0.85, roughness=0.22) # Renault Bleu Iliade
    mat_plastic = get_or_create_mat("laguna_plastic", (0.05, 0.05, 0.05, 1.0), metallic=0.0, roughness=0.85) # Textured black trim
    mat_glass = get_or_create_mat("laguna_glass", (0.08, 0.12, 0.18, 0.35), metallic=0.1, roughness=0.05, alpha=0.35)
    mat_chrome = get_or_create_mat("laguna_chrome", (0.95, 0.95, 0.97, 1.0), metallic=0.98, roughness=0.06)
    mat_headlight_lens = get_or_create_mat("laguna_headlight_lens", (0.95, 0.98, 1.0, 0.85), metallic=0.1, roughness=0.05, alpha=0.85)
    mat_headlight_reflector = get_or_create_mat("laguna_headlight_reflector", (0.95, 0.95, 0.95, 1.0), metallic=0.99, roughness=0.02)
    mat_taillight_red = get_or_create_mat("laguna_taillight_red", (0.85, 0.02, 0.02, 0.90), metallic=0.1, roughness=0.1, alpha=0.9)
    mat_taillight_white = get_or_create_mat("laguna_taillight_white", (0.9, 0.9, 0.9, 0.90), metallic=0.1, roughness=0.1, alpha=0.9)
    mat_mirror_glass = get_or_create_mat("laguna_mirror_glass", (0.9, 0.92, 0.95, 1.0), metallic=1.0, roughness=0.01)

    # List of objects we are refining/replacing
    objects_to_replace = [
        "laguna_gen2_body", "laguna_fender_L", "laguna_fender_R",
        "laguna_door_FL", "laguna_door_FR", "laguna_door_RL", "laguna_door_RR",
        "laguna_mirror_L", "laguna_mirror_R", "laguna_grille", "laguna_badge_F", "laguna_badge_R",
        "laguna_foglight_L", "laguna_foglight_R", "laguna_tailgate", "laguna_exhaust"
    ]
    for name in objects_to_replace:
        if name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)

    # -------------------------------------------------------------
    # 1. FRONT FENDERS (L & R) with flared wheel arches
    # Front wheel center: Y = 1.370m, Z = 0.315m. Arch radius = 0.37m
    # -------------------------------------------------------------
    for side, sign in [("L", -1), ("R", 1)]:
        bm = bmesh.new()
        # Wheel arch rim vertices (semi-circle over wheel)
        arch_pts = []
        num_pts = 7
        for k in range(num_pts):
            angle = math.pi * k / (num_pts - 1)
            ay = 1.370 + 0.37 * math.cos(angle)
            az = 0.315 + 0.37 * math.sin(angle)
            # Slight outward flare on wheel arch lip (X = +/- 0.885m)
            v = bm.verts.new((sign * 0.885, ay, az))
            arch_pts.append(v)

        # Upper fender edge meeting hood & A-pillar
        top_pts = [
            bm.verts.new((sign * 0.83, 1.80, 0.74)), # front corner by headlight
            bm.verts.new((sign * 0.84, 1.55, 0.80)),
            bm.verts.new((sign * 0.85, 1.37, 0.84)), # mid fender
            bm.verts.new((sign * 0.86, 1.20, 0.87)),
            bm.verts.new((sign * 0.87, 0.98, 0.90)), # A-pillar base
            bm.verts.new((sign * 0.87, 0.96, 0.65)), # rear vertical edge
            bm.verts.new((sign * 0.86, 0.96, 0.30))  # lower rocker edge
        ]

        # Inner front by bumper
        f_front_low = bm.verts.new((sign * 0.81, 1.82, 0.38))

        # Build faces between arch and outer contour
        bm.faces.new([arch_pts[0], f_front_low, top_pts[0], top_pts[1], arch_pts[1]])
        bm.faces.new([arch_pts[1], top_pts[1], top_pts[2], arch_pts[2]])
        bm.faces.new([arch_pts[2], top_pts[2], top_pts[3], arch_pts[3]])
        bm.faces.new([arch_pts[3], top_pts[3], top_pts[4], arch_pts[4]])
        bm.faces.new([arch_pts[4], top_pts[4], top_pts[5], arch_pts[5]])
        bm.faces.new([arch_pts[5], top_pts[5], top_pts[6], arch_pts[6]])

        mesh = bpy.data.meshes.new(f"laguna_fender_{side}_mesh")
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new(f"laguna_fender_{side}", mesh)
        col_target.objects.link(obj)
        mesh.materials.append(mat_paint)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth()
        obj.select_set(False)

    # -------------------------------------------------------------
    # 2. DOORS (FL, FR, RL, RR) with Side Mouldings & Handles
    # -------------------------------------------------------------
    door_configs = [
        ("FL", -1, 0.05, 0.95),  # Left front: Y from 0.05m to 0.95m
        ("FR",  1, 0.05, 0.95),  # Right front
        ("RL", -1, -0.80, 0.05), # Left rear: Y from -0.80m to 0.05m
        ("RR",  1, -0.80, 0.05)  # Right rear
    ]

    for d_name, sign, y_start, y_end in door_configs:
        bm = bmesh.new()
        # Lower door panel (below window)
        # Z: 0.30 (rocker), 0.55 (bump strip lower), 0.65 (bump strip upper), 0.90 (belt line)
        v00 = bm.verts.new((sign * 0.86, y_end, 0.30))
        v01 = bm.verts.new((sign * 0.87, y_end, 0.55))
        v02 = bm.verts.new((sign * 0.875, y_end, 0.65)) # bump strip ridge
        v03 = bm.verts.new((sign * 0.865, y_end, 0.90))

        v10 = bm.verts.new((sign * 0.86, y_start, 0.30))
        v11 = bm.verts.new((sign * 0.87, y_start, 0.55))
        v12 = bm.verts.new((sign * 0.875, y_start, 0.65))
        v13 = bm.verts.new((sign * 0.865, y_start, 0.90))

        # Upper window frame & glass area
        v04 = bm.verts.new((sign * 0.62, y_end, 1.38))   # roof line
        v14 = bm.verts.new((sign * 0.62, y_start, 1.41))

        # Lower door face (painted)
        f_lower = bm.faces.new([v00, v10, v11, v01])
        # Rubbing strip face (plastic)
        f_strip = bm.faces.new([v01, v11, v12, v02])
        # Upper door face (painted)
        f_upper = bm.faces.new([v02, v12, v13, v03])
        # Window frame / glass face
        f_window = bm.faces.new([v03, v13, v14, v04])

        # Proper material slot assignments
        mesh = bpy.data.meshes.new(f"laguna_door_{d_name}_mesh")
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new(f"laguna_door_{d_name}", mesh)
        col_target.objects.link(obj)

        mesh.materials.append(mat_paint)
        mesh.materials.append(mat_plastic)
        mesh.materials.append(mat_glass)

        # Assign materials to polygons
        mesh.polygons[0].material_index = 0 # paint
        mesh.polygons[1].material_index = 1 # black rub strip
        mesh.polygons[2].material_index = 0 # paint
        mesh.polygons[3].material_index = 2 # glass

        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth()
        obj.select_set(False)

        # Add door handle
        h_y = (y_start + y_end) * 0.5 + 0.15 if "F" in d_name else (y_start + y_end) * 0.5 - 0.10
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(sign * 0.88, h_y, 0.82)
        )
        h_obj = bpy.context.active_object
        h_obj.name = f"laguna_handle_{d_name}"
        h_obj.scale = (0.025, 0.12, 0.035)
        bpy.ops.object.transform_apply(scale=True)
        for col in h_obj.users_collection:
            col.objects.unlink(h_obj)
        col_target.objects.link(h_obj)
        h_obj.data.materials.append(mat_paint)

    # -------------------------------------------------------------
    # 3. SIDE WING MIRRORS (L & R)
    # Mounted at A-pillar corner (Y ~ 0.90m, Z ~ 0.95m, X ~ +/-0.88m)
    # -------------------------------------------------------------
    for side, sign in [("L", -1), ("R", 1)]:
        # Mirror Housing (aerodynamic tear-drop)
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(sign * 0.96, 0.88, 0.96)
        )
        m_obj = bpy.context.active_object
        m_obj.name = f"laguna_mirror_{side}"
        m_obj.scale = (0.09, 0.16, 0.09)
        bpy.ops.object.transform_apply(scale=True)
        for col in m_obj.users_collection:
            col.objects.unlink(m_obj)
        col_target.objects.link(m_obj)
        m_obj.data.materials.append(mat_paint)
        m_obj.data.materials.append(mat_mirror_glass)

        # Mirror base mounting triangle
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=12,
            radius=0.025,
            depth=0.10,
            location=(sign * 0.89, 0.90, 0.93),
            rotation=(0, sign * 1.2, 0)
        )
        b_obj = bpy.context.active_object
        b_obj.name = f"laguna_mirrorbase_{side}"
        for col in b_obj.users_collection:
            col.objects.unlink(b_obj)
        col_target.objects.link(b_obj)
        b_obj.data.materials.append(mat_plastic)

    # -------------------------------------------------------------
    # 4. FRONT GRILLE & CHROME RENAULT LOSANGE (DIAMOND)
    # -------------------------------------------------------------
    # Twin upper grille slats
    bm_g = bmesh.new()
    # Left grille slot
    v_gl = [
        bm_g.verts.new((-0.10, 1.95, 0.71)),
        bm_g.verts.new((-0.42, 1.89, 0.71)),
        bm_g.verts.new((-0.42, 1.90, 0.66)),
        bm_g.verts.new((-0.10, 1.96, 0.66))
    ]
    bm_g.faces.new(v_gl)
    # Right grille slot
    v_gr = [
        bm_g.verts.new((0.10, 1.96, 0.71)),
        bm_g.verts.new((0.42, 1.89, 0.71)),
        bm_g.verts.new((0.42, 1.90, 0.66)),
        bm_g.verts.new((0.10, 1.95, 0.66))
    ]
    bm_g.faces.new(v_gr)
    g_mesh = bpy.data.meshes.new("laguna_grille_mesh")
    bm_g.to_mesh(g_mesh)
    bm_g.free()
    g_obj = bpy.data.objects.new("laguna_grille", g_mesh)
    col_target.objects.link(g_obj)
    g_mesh.materials.append(mat_plastic)

    # Renault Chrome Diamond Badge (Front)
    # Placed between twin grilles at X=0, Y=1.97m, Z=0.69m
    bm_b = bmesh.new()
    v_b = [
        bm_b.verts.new((0.0, 1.975, 0.74)),    # top point
        bm_b.verts.new((0.045, 1.975, 0.69)),  # right point
        bm_b.verts.new((0.0, 1.975, 0.64)),    # bottom point
        bm_b.verts.new((-0.045, 1.975, 0.69)), # left point
    ]
    # Inner cutout diamond for hollow Renault style
    v_bin = [
        bm_b.verts.new((0.0, 1.978, 0.72)),
        bm_b.verts.new((0.025, 1.978, 0.69)),
        bm_b.verts.new((0.0, 1.978, 0.66)),
        bm_b.verts.new((-0.025, 1.978, 0.69)),
    ]
    # Diamond outline faces
    bm_b.faces.new([v_b[0], v_b[1], v_bin[1], v_bin[0]])
    bm_b.faces.new([v_b[1], v_b[2], v_bin[2], v_bin[1]])
    bm_b.faces.new([v_b[2], v_b[3], v_bin[3], v_bin[2]])
    bm_b.faces.new([v_b[3], v_b[0], v_bin[0], v_bin[3]])

    b_mesh = bpy.data.meshes.new("laguna_badge_F_mesh")
    bm_b.to_mesh(b_mesh)
    bm_b.free()
    b_obj = bpy.data.objects.new("laguna_badge_F", b_mesh)
    col_target.objects.link(b_obj)
    b_mesh.materials.append(mat_chrome)

    # -------------------------------------------------------------
    # 5. FRONT FOG LIGHTS (Round, in lower bumper recesses)
    # -------------------------------------------------------------
    for side, sign in [("L", -1), ("R", 1)]:
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=16,
            radius=0.045,
            depth=0.03,
            location=(sign * 0.58, 2.18, 0.38),
            rotation=(1.570796, 0, 0)
        )
        fog_obj = bpy.context.active_object
        fog_obj.name = f"laguna_foglight_{side}"
        for col in fog_obj.users_collection:
            col.objects.unlink(fog_obj)
        col_target.objects.link(fog_obj)
        fog_obj.data.materials.append(mat_headlight_lens)

    # -------------------------------------------------------------
    # 6. TAILGATE & REAR "L A G U N A" BADGE & EXHAUST
    # -------------------------------------------------------------
    # Tailgate body section (below rear window to bumper)
    bm_tg = bmesh.new()
    v_tg = [
        bm_tg.verts.new((-0.68, -1.75, 1.02)), # top under glass
        bm_tg.verts.new((0.68, -1.75, 1.02)),
        bm_tg.verts.new((0.74, -2.18, 0.88)),  # spoiler lip
        bm_tg.verts.new((0.0, -2.20, 0.885)),  # center peak
        bm_tg.verts.new((-0.74, -2.18, 0.88)),
        bm_tg.verts.new((0.72, -2.24, 0.74)),  # bottom meeting bumper
        bm_tg.verts.new((-0.72, -2.24, 0.74))
    ]
    # Sloping upper hatch surface
    bm_tg.faces.new([v_tg[0], v_tg[1], v_tg[2], v_tg[3], v_tg[4]])
    # Vertical rear face of tailgate (license plate / badging area)
    bm_tg.faces.new([v_tg[4], v_tg[3], v_tg[2], v_tg[5], v_tg[6]])

    tg_mesh = bpy.data.meshes.new("laguna_tailgate_mesh")
    bm_tg.to_mesh(tg_mesh)
    bm_tg.free()
    tg_obj = bpy.data.objects.new("laguna_tailgate", tg_mesh)
    col_target.objects.link(tg_obj)
    tg_mesh.materials.append(mat_paint)
    tg_obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()
    tg_obj.select_set(False)

    # Rear Chrome Badge: "LAGUNA" block
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0.0, -2.22, 0.82)
    )
    badge_r = bpy.context.active_object
    badge_r.name = "laguna_badge_R"
    badge_r.scale = (0.24, 0.015, 0.03)
    bpy.ops.object.transform_apply(scale=True)
    for col in badge_r.users_collection:
        col.objects.unlink(badge_r)
    col_target.objects.link(badge_r)
    badge_r.data.materials.append(mat_chrome)

    # Rear Exhaust (Authentic transverse muffler under rear trunk + chrome tip)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=0.12,
        depth=0.55,
        location=(0.0, -1.90, 0.28),
        rotation=(0, 1.570796, 0)
    )
    muffler_obj = bpy.context.active_object
    muffler_obj.name = "laguna_exhaust"
    for col in muffler_obj.users_collection:
        col.objects.unlink(muffler_obj)
    col_target.objects.link(muffler_obj)
    muffler_obj.data.materials.append(mat_plastic)

    # Exhaust tip on left side (standard dCi / 2.0 16V layout)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=0.038,
        depth=0.20,
        location=(-0.45, -2.25, 0.28),
        rotation=(1.570796, 0, 0)
    )
    tip_obj = bpy.context.active_object
    tip_obj.name = "laguna_exhaust_tip"
    for col in tip_obj.users_collection:
        col.objects.unlink(tip_obj)
    col_target.objects.link(tip_obj)
    tip_obj.data.materials.append(mat_chrome)

    print("[Laguna II Detailed Modeling] Successfully created detailed exterior components!")

if __name__ == "__main__":
    model_laguna2_detailed()
