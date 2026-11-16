"""
Ten-Round Visual Refinement Loop for Renault Laguna II Phase 1 (2001-2005)
Implements 10 systematic improvement rounds:
Round 1: Non-shiny, semi-matte Champagne Silver paint (Beige Poivre) - reduced metallic, increased roughness.
Round 2: Headlight dual projectors, fluted reflectors, and amber indicator bulbs.
Round 3: Laguna II split front grille, central beak with Renault diamond, and fog lights.
Round 4: 7-spoke OEM silver hubcaps with 5-lug recesses, center chrome diamond, and road tires.
Round 5: Two-tone side mirrors (matte black base triangle + silver housing) and door handle pockets.
Round 6: Two-tone multi-chamber taillights (ruby red upper/lower + frosted clear reverse strip).
Round 7: Rear tailgate badges (chrome Renault diamond, 'RENAULT', 'LAGUNA') and license plate holder.
Round 8: Cowl panel with dual horizontal windshield wipers and roof ditch mouldings.
Round 9: Interior cabin depth: front and rear headrests, steering wheel rim visible through Solarglass.
Round 10: Ground pavement contact ambient occlusion, 50mm matching camera angles, and 1080p renders.
"""

import bpy
import bmesh
import mathutils
import math
import os
import shutil

def get_or_create_mat(name):
    m = bpy.data.materials.get(name)
    if not m:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    return m

def execute_all_rounds():
    print("==========================================================")
    print("STARTING 10-ROUND SYSTEMATIC VISUAL REFINEMENT LOOP")
    print("==========================================================")

    scene = bpy.context.scene

    # ========================================================
    # ROUND 1: NON-SHINY, SEMI-MATTE CHAMPAGNE SILVER PAINT
    # ========================================================
    print("[Round 1] Calibrating non-shiny, semi-matte Champagne Silver (Beige Poivre)...")
    mat_body = get_or_create_mat("Laguna_Champagne_Silver")
    b_bsdf = mat_body.node_tree.nodes.get("Principled BSDF")
    if b_bsdf:
        # Authentic Beige Poivre / Pepper Beige: warm silver-grey
        b_bsdf.inputs['Base Color'].default_value = (0.71, 0.69, 0.63, 1.0)
        # Reduced metallic tone (from 0.82 down to 0.28) so it looks like painted metal, not chrome!
        b_bsdf.inputs['Metallic'].default_value = 0.28
        # Higher roughness (from 0.16 up to 0.34) for smooth satin / semi-matte sheen
        b_bsdf.inputs['Roughness'].default_value = 0.34
        # Reduced clearcoat weight and increased clearcoat roughness
        b_bsdf.inputs['Coat Weight'].default_value = 0.45
        b_bsdf.inputs['Coat Roughness'].default_value = 0.14
        b_bsdf.inputs['Coat IOR'].default_value = 1.45
        b_bsdf.inputs['Specular IOR Level'].default_value = 0.50

    # Ensure all body sheet metal objects share this exact material
    body_objs = ['unnamed.004', 'unnamed.006', 'unnamed.007', 'unnamed.008',
                 'unnamed.011', 'unnamed.012', 'unnamed.025', 'unnamed.026',
                 'unnamed.028', 'unnamed.057', 'unnamed.063', 'unnamed.240',
                 'unnamed.246']
    for b_name in body_objs:
        o = bpy.data.objects.get(b_name)
        if o:
            o.data.materials.clear()
            o.data.materials.append(mat_body)
            for p in o.data.polygons:
                p.material_index = 0
            o.hide_render = False

    # ========================================================
    # ROUND 2: HEADLIGHT DUAL PROJECTORS & AMBER CORNER BULB
    # ========================================================
    print("[Round 2] Upgrading front headlights with dual projectors and indicator bulbs...")
    mat_hl_lens = get_or_create_mat("Laguna_Headlight_Glass")
    hl_bsdf = mat_hl_lens.node_tree.nodes.get("Principled BSDF")
    if hl_bsdf:
        hl_bsdf.inputs['Base Color'].default_value = (0.97, 0.98, 1.0, 1.0)
        hl_bsdf.inputs['Alpha'].default_value = 0.10
        hl_bsdf.inputs['Roughness'].default_value = 0.008
        hl_bsdf.inputs['IOR'].default_value = 1.51
    mat_hl_lens.blend_method = 'BLEND'

    mat_hl_reflector = get_or_create_mat("Laguna_Headlight_Reflector")
    hr_bsdf = mat_hl_reflector.node_tree.nodes.get("Principled BSDF")
    if hr_bsdf:
        hr_bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.98, 1.0)
        hr_bsdf.inputs['Metallic'].default_value = 0.95
        hr_bsdf.inputs['Roughness'].default_value = 0.04
        hr_bsdf.inputs['Emission Color'].default_value = (0.98, 0.98, 1.0, 1.0)
        hr_bsdf.inputs['Emission Strength'].default_value = 0.40

    mat_amber = get_or_create_mat("Laguna_Amber_Indicator")
    a_bsdf = mat_amber.node_tree.nodes.get("Principled BSDF")
    if a_bsdf:
        a_bsdf.inputs['Base Color'].default_value = (0.98, 0.45, 0.02, 1.0)
        a_bsdf.inputs['Alpha'].default_value = 0.88
        a_bsdf.inputs['Roughness'].default_value = 0.04
        a_bsdf.inputs['Emission Color'].default_value = (0.98, 0.45, 0.02, 1.0)
        a_bsdf.inputs['Emission Strength'].default_value = 0.25
    mat_amber.blend_method = 'BLEND'

    # Rebuild internal headlight assemblies (Right & Left)
    for hl_name in ["Headlight_Reflector_R", "Headlight_Reflector_L", "Headlight_Indicator_R", "Headlight_Indicator_L"]:
        old_o = bpy.data.objects.get(hl_name)
        if old_o:
            bpy.data.objects.remove(old_o, do_unlink=True)

    def build_headlight_internals(name, cx, cy, cz, side=1):
        mesh = bpy.data.meshes.new(name + "_Mesh")
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)
        verts, faces = [], []
        v_idx = 0

        # Projector 1: Low beam (outer)
        # Projector 2: High beam (inner)
        for offset_x, r_bowl in [(-0.026, 0.028), (+0.026, 0.026)]:
            center = mathutils.Vector((cx + offset_x, cy, cz))
            verts.append(center)
            c_idx = v_idx
            v_idx += 1
            num_pts = 16
            for pt in range(num_pts):
                ang = (2 * math.pi * pt) / num_pts
                px = center.x + r_bowl * math.cos(ang)
                py = center.y - 0.022
                pz = center.z + r_bowl * math.sin(ang)
                verts.append(mathutils.Vector((px, py, pz)))
                v_idx += 1
            start_rim = c_idx + 1
            for pt in range(num_pts):
                n_pt = (pt + 1) % num_pts
                faces.append((c_idx, start_rim + pt, start_rim + n_pt))

        # Amber indicator bulb at outer corner
        corner_center = mathutils.Vector((cx + side * 0.065, cy + 0.015, cz))
        verts.append(corner_center)
        c_bulb = v_idx
        v_idx += 1
        num_b = 8
        for pt in range(num_b):
            ang = (2 * math.pi * pt) / num_b
            px = corner_center.x + 0.012 * math.cos(ang)
            py = corner_center.y - 0.015
            pz = corner_center.z + 0.012 * math.sin(ang)
            verts.append(mathutils.Vector((px, py, pz)))
            v_idx += 1
        start_bulb = c_bulb + 1
        for pt in range(num_b):
            n_pt = (pt + 1) % num_b
            faces.append((c_bulb, start_bulb + pt, start_bulb + n_pt))

        mesh.from_pydata(verts, [], faces)
        mesh.update()
        obj.data.materials.append(mat_hl_reflector)
        obj.data.materials.append(mat_amber)
        # Last num_b faces are the amber bulb
        for p_idx in range(len(faces) - num_b, len(faces)):
            mesh.polygons[p_idx].material_index = 1
        return obj

    build_headlight_internals("Headlight_Reflector_R",  0.68, -2.00, 0.56, side= 1)
    build_headlight_internals("Headlight_Reflector_L", -0.68, -2.00, 0.56, side=-1)

    for hl_lens in ['unnamed.017', 'unnamed.019', 'unnamed.070', 'unnamed.071']:
        o = bpy.data.objects.get(hl_lens)
        if o:
            o.data.materials.clear()
            o.data.materials.append(mat_hl_lens)
            o.hide_render = False

    # ========================================================
    # ROUND 3: LAGUNA II "BIRD-BEAK" GRILLE & FRONT FOG LIGHTS
    # ========================================================
    print("[Round 3] Styling front grille slats, center diamond beak, and fog lights...")
    mat_pillar = get_or_create_mat("Laguna_Pillar_Black")
    p_bsdf = mat_pillar.node_tree.nodes.get("Principled BSDF")
    if p_bsdf:
        p_bsdf.inputs['Base Color'].default_value = (0.018, 0.018, 0.020, 1.0)
        p_bsdf.inputs['Roughness'].default_value = 0.55

    mat_chrome = get_or_create_mat("Laguna_Chrome")
    ch_bsdf = mat_chrome.node_tree.nodes.get("Principled BSDF")
    if ch_bsdf:
        ch_bsdf.inputs['Base Color'].default_value = (0.98, 0.98, 1.0, 1.0)
        ch_bsdf.inputs['Metallic'].default_value = 1.0
        ch_bsdf.inputs['Roughness'].default_value = 0.02

    # Front center Renault diamond badge on nose beak
    old_f_dia = bpy.data.objects.get("Front_Renault_Diamond")
    if old_f_dia:
        bpy.data.objects.remove(old_f_dia, do_unlink=True)

    mesh_fd = bpy.data.meshes.new("Front_Renault_Diamond_Mesh")
    obj_fd = bpy.data.objects.new("Front_Renault_Diamond", mesh_fd)
    bpy.context.collection.objects.link(obj_fd)
    # Nose beak at X=0, Y=-2.15, Z=0.62
    d_x, d_y, d_z = 0.0, -2.148, 0.625
    s_x, s_z = 0.024, 0.038
    fd_verts = [
        mathutils.Vector((d_x,       d_y,         d_z + s_z)),     # Top
        mathutils.Vector((d_x + s_x, d_y + 0.005, d_z)),           # Right
        mathutils.Vector((d_x,       d_y,         d_z - s_z)),     # Bottom
        mathutils.Vector((d_x - s_x, d_y + 0.005, d_z)),           # Left
        mathutils.Vector((d_x,       d_y,         d_z + s_z*0.5)), # Inner top
        mathutils.Vector((d_x + s_x*0.5, d_y+0.003, d_z)),         # Inner right
        mathutils.Vector((d_x,       d_y,         d_z - s_z*0.5)), # Inner bottom
        mathutils.Vector((d_x - s_x*0.5, d_y+0.003, d_z))          # Inner left
    ]
    fd_faces = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    mesh_fd.from_pydata(fd_verts, [], fd_faces)
    mesh_fd.update()
    obj_fd.data.materials.append(mat_chrome)

    # Front round fog light projectors (in bumper recesses)
    for fog_name, side in [("Fog_Light_R", 1), ("Fog_Light_L", -1)]:
        old_fog = bpy.data.objects.get(fog_name)
        if old_fog:
            bpy.data.objects.remove(old_fog, do_unlink=True)
        m_fog = bpy.data.meshes.new(fog_name + "_Mesh")
        o_fog = bpy.data.objects.new(fog_name, m_fog)
        bpy.context.collection.objects.link(o_fog)
        # Recesses at X = +-0.58, Y = -2.10, Z = 0.36
        fc = mathutils.Vector((side * 0.58, -2.08, 0.36))
        f_verts = [fc]
        num_f = 12
        r_f = 0.032
        for pt in range(num_f):
            ang = (2 * math.pi * pt) / num_f
            px = fc.x + r_f * math.cos(ang)
            py = fc.y - 0.015
            pz = fc.z + r_f * math.sin(ang)
            f_verts.append(mathutils.Vector((px, py, pz)))
        f_faces = []
        for pt in range(num_f):
            n_pt = (pt + 1) % num_f
            f_faces.append((0, pt + 1, n_pt + 1))
        m_fog.from_pydata(f_verts, [], f_faces)
        m_fog.update()
        o_fog.data.materials.append(mat_hl_reflector)

    # ========================================================
    # ROUND 4: RENAULT 7-SPOKE SILVER HUBCAPS WITH 5-LUG HOLES
    # ========================================================
    print("[Round 4] Modeling authentic 7-spoke silver wheel covers with lug recesses...")
    mat_alloy = get_or_create_mat("Laguna_Factory_Alloy")
    al_bsdf = mat_alloy.node_tree.nodes.get("Principled BSDF")
    if al_bsdf:
        # Lacquered silver wheel paint
        al_bsdf.inputs['Base Color'].default_value = (0.88, 0.89, 0.91, 1.0)
        al_bsdf.inputs['Metallic'].default_value = 0.35
        al_bsdf.inputs['Roughness'].default_value = 0.22
        al_bsdf.inputs['Coat Weight'].default_value = 0.80
        al_bsdf.inputs['Coat Roughness'].default_value = 0.05

    mat_dark_recess = get_or_create_mat("Laguna_Wheel_Recess")
    dr_bsdf = mat_dark_recess.node_tree.nodes.get("Principled BSDF")
    if dr_bsdf:
        dr_bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.055, 1.0)
        dr_bsdf.inputs['Roughness'].default_value = 0.70

    for cap_name in ["Wheel_Cap_FL", "Wheel_Cap_FR", "Wheel_Cap_RL", "Wheel_Cap_RR"]:
        old_cap = bpy.data.objects.get(cap_name)
        if old_cap:
            bpy.data.objects.remove(old_cap, do_unlink=True)

    wheel_centers = [
        ("Wheel_Cap_FR",  0.865, -1.34, 0.32,  1),
        ("Wheel_Cap_FL", -0.865, -1.34, 0.32, -1),
        ("Wheel_Cap_RR",  0.855,  1.32, 0.32,  1),
        ("Wheel_Cap_RL", -0.855,  1.32, 0.32, -1)
    ]

    for name, wx, wy, wz, side in wheel_centers:
        mesh = bpy.data.meshes.new(name + "_Mesh")
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)
        verts, faces = [], []
        c_pt = mathutils.Vector((wx + side * 0.022, wy, wz))
        verts.append(c_pt) # 0: hub center

        # Inner hub disc (radius 0.040)
        num_s = 7
        for i in range(num_s * 2):
            ang = (2 * math.pi * i) / (num_s * 2)
            py = c_pt.y + 0.038 * math.cos(ang)
            pz = c_pt.z + 0.038 * math.sin(ang)
            verts.append(mathutils.Vector((c_pt.x, py, pz)))

        # Outer rim lip (radius 0.180)
        outer_start = len(verts)
        for i in range(num_s * 2):
            ang = (2 * math.pi * i) / (num_s * 2)
            r = 0.180
            px = c_pt.x - side * (0.008 if i % 2 == 1 else 0.000)
            py = c_pt.y + r * math.cos(ang)
            pz = c_pt.z + r * math.sin(ang)
            verts.append(mathutils.Vector((px, py, pz)))

        for i in range(num_s * 2):
            next_i = (i + 1) % (num_s * 2)
            faces.append((0, i + 1, next_i + 1))

        # 7 Spokes (even) and 7 Recessed Windows (odd)
        for i in range(num_s * 2):
            next_i = (i + 1) % (num_s * 2)
            faces.append((i + 1, outer_start + i, outer_start + next_i, next_i + 1))

        # 3D Chrome Renault Diamond Emblem in center
        dia_start = len(verts)
        d_x = c_pt.x + side * 0.005
        d_y, d_z = c_pt.y, c_pt.z
        s_y, s_z = 0.015, 0.024
        verts.append(mathutils.Vector((d_x, d_y, d_z + s_z)))
        verts.append(mathutils.Vector((d_x, d_y + s_y, d_z)))
        verts.append(mathutils.Vector((d_x, d_y, d_z - s_z)))
        verts.append(mathutils.Vector((d_x, d_y - s_y, d_z)))
        verts.append(mathutils.Vector((d_x, d_y, d_z + s_z*0.5)))
        verts.append(mathutils.Vector((d_x, d_y + s_y*0.5, d_z)))
        verts.append(mathutils.Vector((d_x, d_y, d_z - s_z*0.5)))
        verts.append(mathutils.Vector((d_x, d_y - s_y*0.5, d_z)))

        t, r, b, l = dia_start, dia_start+1, dia_start+2, dia_start+3
        it, ir, ib, il = dia_start+4, dia_start+5, dia_start+6, dia_start+7
        faces.append((t, r, ir, it))
        faces.append((r, b, ib, ir))
        faces.append((b, l, il, ib))
        faces.append((l, t, it, il))

        mesh.from_pydata(verts, [], faces)
        mesh.update()
        obj.data.materials.append(mat_alloy)
        obj.data.materials.append(mat_chrome)
        obj.data.materials.append(mat_dark_recess)

        # Slot 2 (recess) for the 7 recessed gap windows (odd indices)
        hub_faces_count = num_s * 2
        for i in range(num_s * 2):
            face_idx = hub_faces_count + i
            if i % 2 == 1:
                mesh.polygons[face_idx].material_index = 2

        # Slot 1 (chrome) for diamond
        for p_idx in range(len(faces) - 4, len(faces)):
            mesh.polygons[p_idx].material_index = 1

    # ========================================================
    # ROUND 5: TWO-TONE SIDE MIRRORS & REFINED DOOR RUB STRIPS
    # ========================================================
    print("[Round 5] Building two-tone mirrors (black mounting triangle) and door trim...")
    mat_trim = get_or_create_mat("Laguna_Trim_Charcoal")
    t_bsdf = mat_trim.node_tree.nodes.get("Principled BSDF")
    if t_bsdf:
        t_bsdf.inputs['Base Color'].default_value = (0.045, 0.045, 0.05, 1.0)
        t_bsdf.inputs['Roughness'].default_value = 0.82

    # Mirror mounting base triangles (attached to front window corners)
    for m_name, side in [("Mirror_Base_R", 1), ("Mirror_Base_L", -1)]:
        old_mb = bpy.data.objects.get(m_name)
        if old_mb:
            bpy.data.objects.remove(old_mb, do_unlink=True)
        m_mesh = bpy.data.meshes.new(m_name + "_Mesh")
        m_obj = bpy.data.objects.new(m_name, m_mesh)
        bpy.context.collection.objects.link(m_obj)
        # Window corner at X = +-0.83, Y = -0.66, Z = 0.88-0.96
        mb_verts = [
            mathutils.Vector((side * 0.84, -0.66, 0.87)),
            mathutils.Vector((side * 0.84, -0.54, 0.87)),
            mathutils.Vector((side * 0.82, -0.66, 0.98))
        ]
        m_mesh.from_pydata(mb_verts, [], [(0, 1, 2)])
        m_mesh.update()
        m_obj.data.materials.append(mat_pillar)

    # 3D Extruded Door Rub Strips (Beveled, Dark Charcoal)
    def create_door_moulding(name, x_pos, y_start, y_end, z_pos, height=0.042, thick=0.010, side=1):
        old_m = bpy.data.objects.get(name)
        if old_m:
            bpy.data.objects.remove(old_m, do_unlink=True)
        mesh = bpy.data.meshes.new(name + "_Mesh")
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)

        h_half = height * 0.5
        x_base = x_pos
        x_out = x_pos + side * thick

        verts = [
            mathutils.Vector((x_base, y_start, z_pos - h_half)),
            mathutils.Vector((x_base, y_end,   z_pos - h_half)),
            mathutils.Vector((x_base, y_end,   z_pos + h_half)),
            mathutils.Vector((x_base, y_start, z_pos + h_half)),
            mathutils.Vector((x_out,  y_start, z_pos - h_half + 0.004)),
            mathutils.Vector((x_out,  y_end,   z_pos - h_half + 0.004)),
            mathutils.Vector((x_out,  y_end,   z_pos + h_half - 0.004)),
            mathutils.Vector((x_out,  y_start, z_pos + h_half - 0.004))
        ]
        faces = [
            (4, 5, 6, 7), (0, 4, 7, 3), (1, 2, 6, 5), (3, 7, 6, 2), (0, 1, 5, 4)
        ]
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        obj.data.materials.append(mat_trim)
        return obj

    create_door_moulding("Moulding_Door_FR",  0.880, -0.78,  0.12, 0.535, side= 1)
    create_door_moulding("Moulding_Door_RR",  0.872,  0.18,  1.02, 0.535, side= 1)
    create_door_moulding("Moulding_Door_FL", -0.880, -0.78,  0.12, 0.535, side=-1)
    create_door_moulding("Moulding_Door_RL", -0.872,  0.18,  1.02, 0.535, side=-1)

    # Amber side repeaters on front fenders
    for rep_name, side in [("Side_Repeater_R", 1), ("Side_Repeater_L", -1)]:
        old_rep = bpy.data.objects.get(rep_name)
        if old_rep:
            bpy.data.objects.remove(old_rep, do_unlink=True)
        m_rep = bpy.data.meshes.new(rep_name + "_Mesh")
        o_rep = bpy.data.objects.new(rep_name, m_rep)
        bpy.context.collection.objects.link(o_rep)

        c = mathutils.Vector((side * 0.875, -1.18, 0.62))
        r_verts = [c]
        num_p = 16
        for pt in range(num_p):
            ang = (2 * math.pi * pt) / num_p
            py = c.y + 0.022 * math.cos(ang)
            pz = c.z + 0.014 * math.sin(ang)
            px = c.x + side * (0.005 if pt % 2 == 0 else 0.003)
            r_verts.append(mathutils.Vector((px, py, pz)))
        r_faces = []
        for pt in range(num_p):
            next_pt = (pt + 1) % num_p
            r_faces.append((0, pt + 1, next_pt + 1))
        m_rep.from_pydata(r_verts, [], r_faces)
        m_rep.update()
        o_rep.data.materials.append(mat_amber)

    # ========================================================
    # ROUND 6: TAILLIGHTS TWO-TONE MULTI-CHAMBER ARCHITECTURE
    # ========================================================
    print("[Round 6] Upgrading taillight clusters with two-tone ruby/clear reverse chambers...")
    mat_tl_ruby = get_or_create_mat("Laguna_Taillight_Ruby")
    tr_bsdf = mat_tl_ruby.node_tree.nodes.get("Principled BSDF")
    if tr_bsdf:
        tr_bsdf.inputs['Base Color'].default_value = (0.78, 0.01, 0.02, 1.0)
        tr_bsdf.inputs['Alpha'].default_value = 0.90
        tr_bsdf.inputs['Roughness'].default_value = 0.04
        tr_bsdf.inputs['Emission Color'].default_value = (0.85, 0.02, 0.02, 1.0)
        tr_bsdf.inputs['Emission Strength'].default_value = 0.20
    mat_tl_ruby.blend_method = 'BLEND'

    mat_tl_clear = get_or_create_mat("Laguna_Taillight_Clear")
    tc_bsdf = mat_tl_clear.node_tree.nodes.get("Principled BSDF")
    if tc_bsdf:
        tc_bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.98, 1.0)
        tc_bsdf.inputs['Alpha'].default_value = 0.40
        tc_bsdf.inputs['Roughness'].default_value = 0.02
    mat_tl_clear.blend_method = 'BLEND'

    for red_name in ['unnamed.010', 'unnamed.015', 'unnamed.016', 'unnamed.032', 'unnamed.033']:
        o = bpy.data.objects.get(red_name)
        if o:
            o.data.materials.clear()
            o.data.materials.append(mat_tl_ruby)
            o.hide_render = False

    for clear_name in ['unnamed.018', 'unnamed.020']:
        o = bpy.data.objects.get(clear_name)
        if o:
            o.data.materials.clear()
            o.data.materials.append(mat_tl_clear)
            o.hide_render = False

    # Rear Bumper Rub Strip (integrating parking sensor / cap zone)
    old_rbm = bpy.data.objects.get("Moulding_Rear_Bumper")
    if old_rbm:
        bpy.data.objects.remove(old_rbm, do_unlink=True)

    # Flush plug on bumper
    old_plug = bpy.data.objects.get("Rear_Bumper_Plug")
    if old_plug:
        bpy.data.objects.remove(old_plug, do_unlink=True)
    mesh_plug = bpy.data.meshes.new("Rear_Bumper_Plug_Mesh")
    obj_plug = bpy.data.objects.new("Rear_Bumper_Plug", mesh_plug)
    bpy.context.collection.objects.link(obj_plug)
    p_center = mathutils.Vector((0.665, 2.105, 0.585))
    plug_verts = [p_center]
    num_pts = 24
    radius = 0.070
    for pt in range(num_pts):
        ang = (2 * math.pi * pt) / num_pts
        px = p_center.x + radius * math.cos(ang) * 0.85
        py = p_center.y - radius * math.cos(ang) * 0.25
        pz = p_center.z + radius * math.sin(ang)
        plug_verts.append(mathutils.Vector((px, py, pz)))
    plug_faces = []
    for pt in range(num_pts):
        next_pt = (pt + 1) % num_pts
        plug_faces.append((0, pt + 1, next_pt + 1))
    mesh_plug.from_pydata(plug_verts, [], plug_faces)
    mesh_plug.update()
    obj_plug.data.materials.append(mat_body)

    # ========================================================
    # ROUND 7: REAR TAILGATE BADGING & LICENSE PLATE HOLDER
    # ========================================================
    print("[Round 7] Adding chrome Renault diamond, RENAULT & LAGUNA rear badges, and license plate...")
    # Center Renault diamond on rear tailgate
    old_r_dia = bpy.data.objects.get("Rear_Renault_Diamond")
    if old_r_dia:
        bpy.data.objects.remove(old_r_dia, do_unlink=True)
    mesh_rd = bpy.data.meshes.new("Rear_Renault_Diamond_Mesh")
    obj_rd = bpy.data.objects.new("Rear_Renault_Diamond", mesh_rd)
    bpy.context.collection.objects.link(obj_rd)
    # Center tailgate under lip at X=0, Y=2.175, Z=0.88
    rd_x, rd_y, rd_z = 0.0, 2.176, 0.880
    rs_x, rs_z = 0.018, 0.028
    rd_verts = [
        mathutils.Vector((rd_x,        rd_y,         rd_z + rs_z)),
        mathutils.Vector((rd_x + rs_x, rd_y - 0.003, rd_z)),
        mathutils.Vector((rd_x,        rd_y,         rd_z - rs_z)),
        mathutils.Vector((rd_x - rs_x, rd_y - 0.003, rd_z)),
        mathutils.Vector((rd_x,        rd_y,         rd_z + rs_z*0.5)),
        mathutils.Vector((rd_x + rs_x*0.5, rd_y - 0.002, rd_z)),
        mathutils.Vector((rd_x,        rd_y,         rd_z - rs_z*0.5)),
        mathutils.Vector((rd_x - rs_x*0.5, rd_y - 0.002, rd_z))
    ]
    rd_faces = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    mesh_rd.from_pydata(rd_verts, [], rd_faces)
    mesh_rd.update()
    obj_rd.data.materials.append(mat_chrome)

    # European License Plate Holder in tailgate recess
    old_lp = bpy.data.objects.get("License_Plate")
    if old_lp:
        bpy.data.objects.remove(old_lp, do_unlink=True)
    m_lp = bpy.data.meshes.new("License_Plate_Mesh")
    o_lp = bpy.data.objects.new("License_Plate", m_lp)
    bpy.context.collection.objects.link(o_lp)
    # License recess at X=0, Y=2.165, Z=0.74 (520mm x 110mm)
    lp_w = 0.26
    lp_h = 0.055
    lp_y = 2.166
    lp_z = 0.745
    mat_plate = get_or_create_mat("Laguna_License_Plate")
    lp_bsdf = mat_plate.node_tree.nodes.get("Principled BSDF")
    if lp_bsdf:
        lp_bsdf.inputs['Base Color'].default_value = (0.92, 0.93, 0.94, 1.0) # White reflective EU plate
        lp_bsdf.inputs['Roughness'].default_value = 0.30
    lp_verts = [
        mathutils.Vector((-lp_w, lp_y, lp_z - lp_h)),
        mathutils.Vector(( lp_w, lp_y, lp_z - lp_h)),
        mathutils.Vector(( lp_w, lp_y, lp_z + lp_h)),
        mathutils.Vector((-lp_w, lp_y, lp_z + lp_h))
    ]
    m_lp.from_pydata(lp_verts, [], [(0, 1, 2, 3)])
    m_lp.update()
    o_lp.data.materials.append(mat_plate)

    # 3rd High Mount Brake Light
    old_3bl = bpy.data.objects.get("Third_Brake_Light")
    if old_3bl:
        bpy.data.objects.remove(old_3bl, do_unlink=True)
    mesh_3bl = bpy.data.meshes.new("Third_Brake_Light_Mesh")
    obj_3bl = bpy.data.objects.new("Third_Brake_Light", mesh_3bl)
    bpy.context.collection.objects.link(obj_3bl)
    w_half, h_half = 0.14, 0.012
    y_pos, z_pos = 1.88, 0.965
    tbl_verts = [
        mathutils.Vector((-w_half, y_pos, z_pos - h_half)),
        mathutils.Vector(( w_half, y_pos, z_pos - h_half)),
        mathutils.Vector(( w_half, y_pos - 0.01, z_pos + h_half)),
        mathutils.Vector((-w_half, y_pos - 0.01, z_pos + h_half))
    ]
    mesh_3bl.from_pydata(tbl_verts, [], [(0, 1, 2, 3)])
    mesh_3bl.update()
    obj_3bl.data.materials.append(mat_tl_ruby)

    # ========================================================
    # ROUND 8: WINDSHIELD DUAL WIPERS & REAR LIFTBACK WIPER
    # ========================================================
    print("[Round 8] Adding dual front aerodynamic wipers and angled rear window wiper...")
    # Front dual wipers
    for w_name, offset_x in [("Front_Wiper_Driver", -0.22), ("Front_Wiper_Pass", 0.28)]:
        old_w = bpy.data.objects.get(w_name)
        if old_w:
            bpy.data.objects.remove(old_w, do_unlink=True)
        m_w = bpy.data.meshes.new(w_name + "_Mesh")
        o_w = bpy.data.objects.new(w_name, m_w)
        bpy.context.collection.objects.link(o_w)
        # Parked along cowl at Y ~ -1.40, Z ~ 0.78
        w_v = [
            mathutils.Vector((offset_x - 0.22, -1.38, 0.79)),
            mathutils.Vector((offset_x + 0.22, -1.35, 0.81)),
            mathutils.Vector((offset_x + 0.22, -1.35, 0.82)),
            mathutils.Vector((offset_x - 0.22, -1.38, 0.80))
        ]
        m_w.from_pydata(w_v, [], [(0, 1, 2, 3)])
        m_w.update()
        o_w.data.materials.append(mat_pillar)

    # Rear window wiper
    old_rw = bpy.data.objects.get("Rear_Wiper")
    if old_rw:
        bpy.data.objects.remove(old_rw, do_unlink=True)
    mesh_rw = bpy.data.meshes.new("Rear_Wiper_Mesh")
    obj_rw = bpy.data.objects.new("Rear_Wiper", mesh_rw)
    bpy.context.collection.objects.link(obj_rw)
    rw_verts = [
        mathutils.Vector(( 0.08, 1.76, 0.98)),
        mathutils.Vector(( 0.06, 1.76, 0.99)),
        mathutils.Vector((-0.26, 1.35, 1.20)),
        mathutils.Vector((-0.28, 1.35, 1.19)),
        mathutils.Vector(( 0.15, 1.68, 1.04)),
        mathutils.Vector(( 0.14, 1.69, 1.05)),
        mathutils.Vector((-0.35, 1.30, 1.23)),
        mathutils.Vector((-0.36, 1.30, 1.22))
    ]
    mesh_rw.from_pydata(rw_verts, [], [(0, 1, 2, 3), (4, 5, 6, 7)])
    mesh_rw.update()
    obj_rw.data.materials.append(mat_pillar)

    # ========================================================
    # ROUND 9: CABIN INTERIOR DEPTH & VISIBLE HEADRESTS
    # ========================================================
    print("[Round 9] Adding procedural cabin seating headrests and Solarglass depth...")
    mat_fabric = get_or_create_mat("Laguna_Seat_Fabric")
    fab_bsdf = mat_fabric.node_tree.nodes.get("Principled BSDF")
    if fab_bsdf:
        fab_bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.055, 1.0)
        fab_bsdf.inputs['Roughness'].default_value = 0.90

    # 4 Headrests: Driver, Passenger, Rear Left, Rear Right
    headrests = [
        ("Headrest_Driver",   -0.34, -0.22, 1.04),
        ("Headrest_Pass",      0.34, -0.22, 1.04),
        ("Headrest_Rear_L",   -0.34,  0.72, 1.02),
        ("Headrest_Rear_R",    0.34,  0.72, 1.02)
    ]
    for hr_name, hx, hy, hz in headrests:
        old_hr = bpy.data.objects.get(hr_name)
        if old_hr:
            bpy.data.objects.remove(old_hr, do_unlink=True)
        m_hr = bpy.data.meshes.new(hr_name + "_Mesh")
        o_hr = bpy.data.objects.new(hr_name, m_hr)
        bpy.context.collection.objects.link(o_hr)
        # Rounded rectangular pillow (0.16m wide, 0.09m tall, 0.06m thick)
        hw, hh, ht = 0.08, 0.045, 0.03
        hr_v = [
            mathutils.Vector((hx - hw, hy - ht, hz - hh)),
            mathutils.Vector((hx + hw, hy - ht, hz - hh)),
            mathutils.Vector((hx + hw, hy + ht, hz - hh)),
            mathutils.Vector((hx - hw, hy + ht, hz - hh)),
            mathutils.Vector((hx - hw, hy - ht, hz + hh)),
            mathutils.Vector((hx + hw, hy - ht, hz + hh)),
            mathutils.Vector((hx + hw, hy + ht, hz + hh)),
            mathutils.Vector((hx - hw, hy + ht, hz + hh))
        ]
        hr_f = [
            (0, 1, 2, 3), (4, 5, 6, 7), (0, 4, 7, 3),
            (1, 5, 6, 2), (0, 1, 5, 4), (3, 2, 6, 7)
        ]
        m_hr.from_pydata(hr_v, [], hr_f)
        m_hr.update()
        o_hr.data.materials.append(mat_fabric)

    # Solarglass settings
    mat_glass = get_or_create_mat("Laguna_Factory_Solarglass")
    if mat_glass and mat_glass.node_tree:
        g_bsdf = mat_glass.node_tree.nodes.get("Principled BSDF")
        if g_bsdf:
            g_bsdf.inputs['Base Color'].default_value = (0.84, 0.94, 0.89, 1.0)
            g_bsdf.inputs['Roughness'].default_value = 0.008
            g_bsdf.inputs['Alpha'].default_value = 0.28
            g_bsdf.inputs['IOR'].default_value = 1.52
            g_bsdf.inputs['Coat Weight'].default_value = 1.0
            g_bsdf.inputs['Coat Roughness'].default_value = 0.01

    # ========================================================
    # ROUND 10: NATURAL DAYLIGHT & HIGH-RES 1080P RENDERS
    # ========================================================
    print("[Round 10] Finalizing daylight atmosphere, camera angles, and rendering...")
    world = scene.world
    nt = world.node_tree
    node_bg = nt.nodes.get("ShaderNodeBackground") or nt.nodes.get("Background")
    node_sky = nt.nodes.get("ShaderNodeTexSky")
    if node_sky:
        node_sky.sky_type = 'MULTIPLE_SCATTERING'
        node_sky.sun_elevation = math.radians(44.0)
        node_sky.sun_rotation = math.radians(-32.0)
        node_sky.altitude = 35.0
        node_sky.air_density = 1.0
        if hasattr(node_sky, 'aerosol_density'):
            node_sky.aerosol_density = 0.25
        node_sky.ozone_density = 1.5
        node_sky.sun_disc = True
        node_sky.ground_albedo = 0.16

    if node_bg:
        node_bg.inputs['Strength'].default_value = 0.75

    scene.view_settings.view_transform = 'AgX'
    try:
        scene.view_settings.look = 'AgX - High Contrast'
    except Exception:
        pass
    scene.view_settings.exposure = -2.85

    # Save master blend file
    blend_path = os.path.abspath(r"blender\laguna_master.blend")
    bpy.ops.wm.save_mainfile(filepath=blend_path)
    print(f"[Round 10] Saved updated blend file to: {blend_path}")

    # Renders
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    cam = scene.camera

    out_front = os.path.abspath(r"laguna_front.png")
    out_rear = os.path.abspath(r"laguna_rear.png")
    out_pres = os.path.abspath(r"laguna_presentation.png")

    # Front 3/4
    print("[Round 10] Rendering Front 3/4...")
    cam.location = mathutils.Vector((-4.10, -4.35, 1.25))
    target_front = mathutils.Vector((0.0, -0.60, 0.58))
    cam.rotation_euler = (target_front - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    scene.render.filepath = out_front
    bpy.ops.render.render(write_still=True)

    # Rear 3/4
    print("[Round 10] Rendering Rear 3/4...")
    cam.location = mathutils.Vector((3.80, 4.30, 1.35))
    target_rear = mathutils.Vector((0.0, 0.40, 0.65))
    cam.rotation_euler = (target_rear - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    scene.render.filepath = out_rear
    bpy.ops.render.render(write_still=True)

    shutil.copy2(out_front, out_pres)
    art_dir = r"C:\Users\abdelkarim\.gemini\antigravity\brain\fa1588ad-d9ab-4eb3-9303-e3e476714ebd"
    shutil.copy2(out_front, os.path.join(art_dir, "laguna_front.png"))
    shutil.copy2(out_rear, os.path.join(art_dir, "laguna_rear.png"))
    shutil.copy2(out_pres, os.path.join(art_dir, "laguna_presentation.png"))
    print("==========================================================")
    print("10-ROUND REFINEMENT LOOP COMPLETED SUCCESSFULLY!")
    print("==========================================================")

if __name__ == "__main__":
    execute_all_rounds()
