"""
Finalize Photorealistic Renault Laguna II Phase 1 (2001-2005)
Eliminates sawtooth artifacts, adds 3D clean door mouldings & repeaters,
fixes window frames & inner panels, seals bumper cutout, adds rear wiper & 3rd brake light,
and renders final 1080p presentation images.
"""

import bpy
import bmesh
import mathutils
import math
import os
import shutil

def run_finalization():
    print("==================================================")
    print("[Finalization] Starting Precision Model Pass...")
    print("==================================================")

    scene = bpy.context.scene

    # ----------------------------------------------------
    # 1. SHADERS
    # ----------------------------------------------------
    def get_or_create_mat(name):
        m = bpy.data.materials.get(name)
        if not m:
            m = bpy.data.materials.new(name)
        m.use_nodes = True
        return m

    # Body: Metallic Champagne Silver (Beige Poivre / Gris Angora)
    mat_body = get_or_create_mat("Laguna_Champagne_Silver")
    b_bsdf = mat_body.node_tree.nodes.get("Principled BSDF")
    if b_bsdf:
        b_bsdf.inputs['Base Color'].default_value = (0.76, 0.73, 0.65, 1.0)
        b_bsdf.inputs['Metallic'].default_value = 0.82
        b_bsdf.inputs['Roughness'].default_value = 0.16
        b_bsdf.inputs['Coat Weight'].default_value = 1.0
        b_bsdf.inputs['Coat Roughness'].default_value = 0.02
        b_bsdf.inputs['Coat IOR'].default_value = 1.50
        b_bsdf.inputs['Specular IOR Level'].default_value = 0.55

    # Solarglass: Pale green heat-rejecting factory glass
    mat_glass = get_or_create_mat("Laguna_Factory_Solarglass")
    g_bsdf = mat_glass.node_tree.nodes.get("Principled BSDF")
    if g_bsdf:
        g_bsdf.inputs['Base Color'].default_value = (0.82, 0.94, 0.88, 1.0)
        g_bsdf.inputs['Roughness'].default_value = 0.008
        g_bsdf.inputs['Alpha'].default_value = 0.28
        g_bsdf.inputs['IOR'].default_value = 1.52
        g_bsdf.inputs['Coat Weight'].default_value = 1.0
        g_bsdf.inputs['Coat Roughness'].default_value = 0.01
    mat_glass.blend_method = 'BLEND'

    # Door & Bumper Moulding Trim: Textured Dark Charcoal
    mat_trim = get_or_create_mat("Laguna_Trim_Charcoal")
    t_bsdf = mat_trim.node_tree.nodes.get("Principled BSDF")
    if t_bsdf:
        t_bsdf.inputs['Base Color'].default_value = (0.045, 0.045, 0.05, 1.0)
        t_bsdf.inputs['Metallic'].default_value = 0.0
        t_bsdf.inputs['Roughness'].default_value = 0.82

    # Window B-Pillars & Frames: Satin Black
    mat_pillar = get_or_create_mat("Laguna_Pillar_Black")
    p_bsdf = mat_pillar.node_tree.nodes.get("Principled BSDF")
    if p_bsdf:
        p_bsdf.inputs['Base Color'].default_value = (0.015, 0.015, 0.018, 1.0)
        p_bsdf.inputs['Metallic'].default_value = 0.0
        p_bsdf.inputs['Roughness'].default_value = 0.50

    # Amber Side Repeaters:
    mat_amber = get_or_create_mat("Laguna_Amber_Indicator")
    a_bsdf = mat_amber.node_tree.nodes.get("Principled BSDF")
    if a_bsdf:
        a_bsdf.inputs['Base Color'].default_value = (0.98, 0.45, 0.02, 1.0)
        a_bsdf.inputs['Alpha'].default_value = 0.88
        a_bsdf.inputs['Roughness'].default_value = 0.04
        a_bsdf.inputs['Emission Color'].default_value = (0.98, 0.45, 0.02, 1.0)
        a_bsdf.inputs['Emission Strength'].default_value = 0.15
    mat_amber.blend_method = 'BLEND'

    # Headlight Outer Lens: Crystal Clear
    mat_hl_lens = get_or_create_mat("Laguna_Headlight_Glass")
    hl_bsdf = mat_hl_lens.node_tree.nodes.get("Principled BSDF")
    if hl_bsdf:
        hl_bsdf.inputs['Base Color'].default_value = (0.98, 0.99, 1.0, 1.0)
        hl_bsdf.inputs['Alpha'].default_value = 0.08
        hl_bsdf.inputs['Roughness'].default_value = 0.005
    mat_hl_lens.blend_method = 'BLEND'

    # Headlight Reflectors: Chrome Parabolic Bowls
    mat_hl_reflector = get_or_create_mat("Laguna_Headlight_Reflector")
    hr_bsdf = mat_hl_reflector.node_tree.nodes.get("Principled BSDF")
    if hr_bsdf:
        hr_bsdf.inputs['Base Color'].default_value = (0.98, 0.98, 1.0, 1.0)
        hr_bsdf.inputs['Metallic'].default_value = 1.0
        hr_bsdf.inputs['Roughness'].default_value = 0.015
        hr_bsdf.inputs['Emission Color'].default_value = (0.98, 0.98, 1.0, 1.0)
        hr_bsdf.inputs['Emission Strength'].default_value = 0.65

    # Chrome Emblems & Diamonds:
    mat_chrome = get_or_create_mat("Laguna_Chrome")
    ch_bsdf = mat_chrome.node_tree.nodes.get("Principled BSDF")
    if ch_bsdf:
        ch_bsdf.inputs['Base Color'].default_value = (0.98, 0.98, 1.0, 1.0)
        ch_bsdf.inputs['Metallic'].default_value = 1.0
        ch_bsdf.inputs['Roughness'].default_value = 0.015

    # Taillight Ruby Red:
    mat_tl_ruby = get_or_create_mat("Laguna_Taillight_Ruby")
    tr_bsdf = mat_tl_ruby.node_tree.nodes.get("Principled BSDF")
    if tr_bsdf:
        tr_bsdf.inputs['Base Color'].default_value = (0.78, 0.01, 0.02, 1.0)
        tr_bsdf.inputs['Alpha'].default_value = 0.90
        tr_bsdf.inputs['Roughness'].default_value = 0.04
        tr_bsdf.inputs['Emission Color'].default_value = (0.85, 0.02, 0.02, 1.0)
        tr_bsdf.inputs['Emission Strength'].default_value = 0.25
    mat_tl_ruby.blend_method = 'BLEND'

    # Taillight Clear Reverse:
    mat_tl_clear = get_or_create_mat("Laguna_Taillight_Clear")
    tc_bsdf = mat_tl_clear.node_tree.nodes.get("Principled BSDF")
    if tc_bsdf:
        tc_bsdf.inputs['Base Color'].default_value = (0.96, 0.96, 0.98, 1.0)
        tc_bsdf.inputs['Alpha'].default_value = 0.35
        tc_bsdf.inputs['Roughness'].default_value = 0.02
    mat_tl_clear.blend_method = 'BLEND'

    # Wheels: Renault Lacquered Silver Metallic
    mat_alloy = get_or_create_mat("Laguna_Factory_Alloy")
    al_bsdf = mat_alloy.node_tree.nodes.get("Principled BSDF")
    if al_bsdf:
        al_bsdf.inputs['Base Color'].default_value = (0.90, 0.91, 0.93, 1.0)
        al_bsdf.inputs['Metallic'].default_value = 0.45 # Lacquered metallic paint
        al_bsdf.inputs['Roughness'].default_value = 0.14
        al_bsdf.inputs['Coat Weight'].default_value = 1.0
        al_bsdf.inputs['Coat Roughness'].default_value = 0.02

    # Tires: Road Rubber
    mat_tire = get_or_create_mat("Laguna_Road_Tire")
    ti_bsdf = mat_tire.node_tree.nodes.get("Principled BSDF")
    if ti_bsdf:
        ti_bsdf.inputs['Base Color'].default_value = (0.024, 0.024, 0.026, 1.0)
        ti_bsdf.inputs['Roughness'].default_value = 0.82

    # Interior: Dark Charcoal
    mat_interior = get_or_create_mat("Laguna_Interior_Charcoal")
    in_bsdf = mat_interior.node_tree.nodes.get("Principled BSDF")
    if in_bsdf:
        in_bsdf.inputs['Base Color'].default_value = (0.04, 0.04, 0.045, 1.0)
        in_bsdf.inputs['Roughness'].default_value = 0.85

    # ----------------------------------------------------
    # 2. PURGE ALL SAWTOOTH ARTIFACTS: UNIFY BODY SHELLS
    # ----------------------------------------------------
    # Set unibody and all outer doors to 100% Champagne Silver
    clean_body_objs = ['unnamed.004', 'unnamed.006', 'unnamed.007', 'unnamed.008',
                       'unnamed.011', 'unnamed.012', 'unnamed.025', 'unnamed.026',
                       'unnamed.028', 'unnamed.057', 'unnamed.063', 'unnamed.240',
                       'unnamed.246', 'unnamed.149', 'unnamed.150', 'unnamed.213', 'unnamed.214']
    for b_name in clean_body_objs:
        bo = bpy.data.objects.get(b_name)
        if bo:
            bo.data.materials.clear()
            bo.data.materials.append(mat_body)
            # Reset all polygon material indices to 0
            for p in bo.data.polygons:
                p.material_index = 0
            bo.hide_render = False

    # ----------------------------------------------------
    # 3. FIX INNER DOOR PANELS & WINDOW FRAMES
    # ----------------------------------------------------
    # Inner door structures -> Interior Charcoal
    for inner_name in ['unnamed.058', 'unnamed.064', 'unnamed.241', 'unnamed.247']:
        io = bpy.data.objects.get(inner_name)
        if io:
            io.data.materials.clear()
            io.data.materials.append(mat_interior)
            io.hide_render = False

    # Window B-pillars, seals, and frames -> Satin Black
    pillar_objs = ['unnamed.060', 'unnamed.170', 'unnamed.142', 'unnamed.243',
                   'unnamed.066', 'unnamed.148', 'unnamed.171', 'unnamed.177',
                   'unnamed.178', 'unnamed.206', 'unnamed.212', 'unnamed.227',
                   'unnamed.228', 'unnamed.234', 'unnamed.235', 'unnamed.244',
                   'unnamed.249']
    for p_name in pillar_objs:
        po = bpy.data.objects.get(p_name)
        if po:
            po.data.materials.clear()
            po.data.materials.append(mat_pillar)
            po.hide_render = False

    # True Window Glass: Windshield, Rear Liftback, and Side Windows
    true_glass = ['unnamed.021', 'unnamed.027', 'unnamed.059', 'unnamed.065', 'unnamed.242', 'unnamed.248']
    for g_name in true_glass:
        go = bpy.data.objects.get(g_name)
        if go:
            go.data.materials.clear()
            go.data.materials.append(mat_glass)
            go.hide_render = False

    # ----------------------------------------------------
    # 4. HIDE ALL TRACK RESIDUALS & FLOATING NETS
    # ----------------------------------------------------
    unwanted = [
        'unnamed.069', 'unnamed.034', 'unnamed.035', 'unnamed.036',
        'unnamed.005', 'unnamed.009', 'unnamed.135', 'unnamed.136',
        'unnamed.194', 'Laguna_Race_Wing', 'unnamed.125', 'unnamed.184',
        'unnamed.128', 'unnamed.029', 'unnamed.031', 'unnamed.220',
        'unnamed.165', 'unnamed.195', 'unnamed.197', 'unnamed.239'
    ]
    for n in unwanted:
        o = bpy.data.objects.get(n)
        if o:
            o.hide_render = True
            o.hide_viewport = True

    # ----------------------------------------------------
    # 5. PROCEDURAL 3D DOOR RUB STRIPS (CLEAN & SHARP)
    # ----------------------------------------------------
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
            # Base (against door skin)
            mathutils.Vector((x_base, y_start, z_pos - h_half)),
            mathutils.Vector((x_base, y_end,   z_pos - h_half)),
            mathutils.Vector((x_base, y_end,   z_pos + h_half)),
            mathutils.Vector((x_base, y_start, z_pos + h_half)),
            # Outer face (protruding)
            mathutils.Vector((x_out,  y_start, z_pos - h_half + 0.004)),
            mathutils.Vector((x_out,  y_end,   z_pos - h_half + 0.004)),
            mathutils.Vector((x_out,  y_end,   z_pos + h_half - 0.004)),
            mathutils.Vector((x_out,  y_start, z_pos + h_half - 0.004))
        ]
        faces = [
            (4, 5, 6, 7), # Outer face
            (0, 4, 7, 3), # Front bevel
            (1, 2, 6, 5), # Rear bevel
            (3, 7, 6, 2), # Top bevel
            (0, 1, 5, 4)  # Bottom bevel
        ]
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        obj.data.materials.append(mat_trim)
        return obj

    # Right side door mouldings
    create_door_moulding("Moulding_Door_FR",  0.880, -0.78,  0.12, 0.535, side= 1)
    create_door_moulding("Moulding_Door_RR",  0.872,  0.18,  1.02, 0.535, side= 1)

    # Left side door mouldings
    create_door_moulding("Moulding_Door_FL", -0.880, -0.78,  0.12, 0.535, side=-1)
    create_door_moulding("Moulding_Door_RL", -0.872,  0.18,  1.02, 0.535, side=-1)

    # Rear Bumper Impact Rub Strip: Curved wrap-around strip
    old_rbm = bpy.data.objects.get("Moulding_Rear_Bumper")
    if old_rbm:
        bpy.data.objects.remove(old_rbm, do_unlink=True)
    mesh_rbm = bpy.data.meshes.new("Moulding_Rear_Bumper_Mesh")
    obj_rbm = bpy.data.objects.new("Moulding_Rear_Bumper", mesh_rbm)
    bpy.context.collection.objects.link(obj_rbm)

    rb_pts = [
        (-0.84, 1.80, 0.64), (-0.85, 1.95, 0.65), (-0.80, 2.10, 0.66),
        (-0.55, 2.18, 0.66), ( 0.00, 2.20, 0.66), ( 0.55, 2.18, 0.66),
        ( 0.80, 2.10, 0.66), ( 0.85, 1.95, 0.65), ( 0.84, 1.80, 0.64)
    ]
    rb_verts = []
    rb_faces = []
    h = 0.022
    for pt in rb_pts:
        rb_verts.append(mathutils.Vector((pt[0], pt[1], pt[2] - h)))
        rb_verts.append(mathutils.Vector((pt[0], pt[1], pt[2] + h)))
    for i in range(len(rb_pts) - 1):
        b1 = i * 2
        t1 = b1 + 1
        b2 = (i + 1) * 2
        t2 = b2 + 1
        rb_faces.append((b1, b2, t2, t1))
    mesh_rbm.from_pydata(rb_verts, [], rb_faces)
    mesh_rbm.update()
    obj_rbm.data.materials.append(mat_trim)

    # ----------------------------------------------------
    # 6. OVAL AMBER SIDE REPEATERS (ON FRONT FENDERS)
    # ----------------------------------------------------
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

    # ----------------------------------------------------
    # 7. SEAL HOLE BELOW TAILLIGHT (EXACT COORDS: 0.665, 2.105, 0.585)
    # ----------------------------------------------------
    old_plug = bpy.data.objects.get("Rear_Bumper_Plug")
    if old_plug:
        bpy.data.objects.remove(old_plug, do_unlink=True)

    mesh_plug = bpy.data.meshes.new("Rear_Bumper_Plug_Mesh")
    obj_plug = bpy.data.objects.new("Rear_Bumper_Plug", mesh_plug)
    bpy.context.collection.objects.link(obj_plug)

    p_center = mathutils.Vector((0.665, 2.105, 0.585))
    plug_verts = [p_center]
    num_pts = 24
    radius = 0.068
    for pt in range(num_pts):
        ang = (2 * math.pi * pt) / num_pts
        # Follow bumper surface slope
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

    # ----------------------------------------------------
    # 8. REAR WINDOW WIPER & 3RD BRAKE LIGHT
    # ----------------------------------------------------
    old_rw = bpy.data.objects.get("Rear_Wiper")
    if old_rw:
        bpy.data.objects.remove(old_rw, do_unlink=True)
    mesh_rw = bpy.data.meshes.new("Rear_Wiper_Mesh")
    obj_rw = bpy.data.objects.new("Rear_Wiper", mesh_rw)
    bpy.context.collection.objects.link(obj_rw)
    w_verts = [
        mathutils.Vector(( 0.08, 1.76, 0.98)),
        mathutils.Vector(( 0.06, 1.76, 0.99)),
        mathutils.Vector((-0.26, 1.35, 1.20)),
        mathutils.Vector((-0.28, 1.35, 1.19)),
        mathutils.Vector(( 0.15, 1.68, 1.04)),
        mathutils.Vector(( 0.14, 1.69, 1.05)),
        mathutils.Vector((-0.35, 1.30, 1.23)),
        mathutils.Vector((-0.36, 1.30, 1.22))
    ]
    mesh_rw.from_pydata(w_verts, [], [(0, 1, 2, 3), (4, 5, 6, 7)])
    mesh_rw.update()
    obj_rw.data.materials.append(mat_pillar)

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

    # ----------------------------------------------------
    # 9. RENAULT WHEEL HUBCAPS WITH CHROME DIAMONDS
    # ----------------------------------------------------
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
        verts = []
        faces = []
        c_pt = mathutils.Vector((wx + side * 0.022, wy, wz))
        verts.append(c_pt)

        num_spokes = 7
        # Hub ring
        for i in range(num_spokes * 2):
            ang = (2 * math.pi * i) / (num_spokes * 2)
            py = c_pt.y + 0.038 * math.cos(ang)
            pz = c_pt.z + 0.038 * math.sin(ang)
            verts.append(mathutils.Vector((c_pt.x, py, pz)))

        # Outer rim ring
        outer_start = len(verts)
        for i in range(num_spokes * 2):
            ang = (2 * math.pi * i) / (num_spokes * 2)
            r = 0.18
            px = c_pt.x - side * (0.008 if i % 2 == 1 else 0.000)
            py = c_pt.y + r * math.cos(ang)
            pz = c_pt.z + r * math.sin(ang)
            verts.append(mathutils.Vector((px, py, pz)))

        for i in range(num_spokes * 2):
            next_i = (i + 1) % (num_spokes * 2)
            faces.append((0, i + 1, next_i + 1))

        for i in range(num_spokes * 2):
            next_i = (i + 1) % (num_spokes * 2)
            faces.append((i + 1, outer_start + i, outer_start + next_i, next_i + 1))

        # Chrome Diamond
        dia_start = len(verts)
        d_x = c_pt.x + side * 0.005
        d_y = c_pt.y
        d_z = c_pt.z
        s_y, s_z = 0.016, 0.025
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
        for p_idx in range(len(faces) - 4, len(faces)):
            mesh.polygons[p_idx].material_index = 1

    # ----------------------------------------------------
    # 10. HIGH RESOLUTION 1080P RENDERS
    # ----------------------------------------------------
    cam = scene.camera
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080

    out_front = os.path.abspath(r"laguna_front.png")
    out_rear = os.path.abspath(r"laguna_rear.png")
    out_pres = os.path.abspath(r"laguna_presentation.png")

    # Front 3/4
    print("[Render] Rendering Final Front 3/4 (laguna_front.png)...")
    cam.location = mathutils.Vector((-4.10, -4.35, 1.25))
    target_front = mathutils.Vector((0.0, -0.60, 0.58))
    cam.rotation_euler = (target_front - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    scene.render.filepath = out_front
    bpy.ops.render.render(write_still=True)

    # Rear 3/4
    print("[Render] Rendering Final Rear 3/4 (laguna_rear.png)...")
    cam.location = mathutils.Vector((3.80, 4.30, 1.35))
    target_rear = mathutils.Vector((0.0, 0.40, 0.65))
    cam.rotation_euler = (target_rear - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    scene.render.filepath = out_rear
    bpy.ops.render.render(write_still=True)

    # Copy to artifacts
    shutil.copy2(out_front, out_pres)
    art_dir = r"C:\Users\abdelkarim\.gemini\antigravity\brain\fa1588ad-d9ab-4eb3-9303-e3e476714ebd"
    shutil.copy2(out_front, os.path.join(art_dir, "laguna_front.png"))
    shutil.copy2(out_rear, os.path.join(art_dir, "laguna_rear.png"))
    shutil.copy2(out_pres, os.path.join(art_dir, "laguna_presentation.png"))
    print("[Finalization] Complete! Photorealistic renders saved.")

if __name__ == "__main__":
    run_finalization()
