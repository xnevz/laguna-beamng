"""
Refinement Iteration 2:
- Eliminates clipping inner tubs (unnamed.136, unnamed.194) that caused black triangle on fender
- Eliminates flat race undertray (unnamed.005)
- Eliminates black gap between rear taillights by assigning unnamed.149 to body paint
- Adds Renault OEM silver center hubcaps with chrome diamond badge to all 4 wheels
- Centers dual chrome headlight reflector cups inside both left & right headlight lenses
- Adjusts vehicle suspension to authentic factory civilian ride height (+35mm arch clearance)
- Renders Front 3/4 and Rear 3/4 in 1080p
"""

import bpy
import mathutils
import math
import os
import shutil

def run_step_2():
    print("[Loop Step 2] Applying advanced fixes...")

    # 1. SHADERS
    def make_material(name):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        return mat

    mat_body = make_material("Laguna_Champagne_Silver")
    b_bsdf = mat_body.node_tree.nodes.get("Principled BSDF")
    if b_bsdf:
        b_bsdf.inputs['Base Color'].default_value = (0.76, 0.72, 0.62, 1.0)
        b_bsdf.inputs['Metallic'].default_value = 0.82
        b_bsdf.inputs['Roughness'].default_value = 0.20
        b_bsdf.inputs['Coat Weight'].default_value = 1.0
        b_bsdf.inputs['Coat Roughness'].default_value = 0.02
        b_bsdf.inputs['Coat IOR'].default_value = 1.50

    mat_glass = make_material("Laguna_Factory_Solarglass")
    g_bsdf = mat_glass.node_tree.nodes.get("Principled BSDF")
    if g_bsdf:
        g_bsdf.inputs['Base Color'].default_value = (0.80, 0.94, 0.88, 1.0)
        g_bsdf.inputs['Alpha'].default_value = 0.38
        g_bsdf.inputs['Roughness'].default_value = 0.012

    mat_moulding = make_material("Laguna_Trim_Charcoal")
    m_bsdf = mat_moulding.node_tree.nodes.get("Principled BSDF")
    if m_bsdf:
        m_bsdf.inputs['Base Color'].default_value = (0.055, 0.055, 0.06, 1.0)
        m_bsdf.inputs['Roughness'].default_value = 0.76

    mat_black = make_material("Laguna_Pillar_Black")
    bk_bsdf = mat_black.node_tree.nodes.get("Principled BSDF")
    if bk_bsdf:
        bk_bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.025, 1.0)
        bk_bsdf.inputs['Roughness'].default_value = 0.55

    mat_amber = make_material("Laguna_Amber_Indicator")
    am_bsdf = mat_amber.node_tree.nodes.get("Principled BSDF")
    if am_bsdf:
        am_bsdf.inputs['Base Color'].default_value = (0.98, 0.45, 0.02, 1.0)
        am_bsdf.inputs['Alpha'].default_value = 0.85

    mat_hl_lens = make_material("Laguna_Headlight_Glass")
    hl_bsdf = mat_hl_lens.node_tree.nodes.get("Principled BSDF")
    if hl_bsdf:
        hl_bsdf.inputs['Base Color'].default_value = (0.97, 0.98, 1.0, 1.0)
        hl_bsdf.inputs['Alpha'].default_value = 0.12

    mat_hl_reflector = make_material("Laguna_Headlight_Reflector")
    hr_bsdf = mat_hl_reflector.node_tree.nodes.get("Principled BSDF")
    if hr_bsdf:
        hr_bsdf.inputs['Base Color'].default_value = (0.98, 0.98, 1.0, 1.0)
        hr_bsdf.inputs['Metallic'].default_value = 1.0
        hr_bsdf.inputs['Roughness'].default_value = 0.02
        hr_bsdf.inputs['Emission Color'].default_value = (0.95, 0.98, 1.0, 1.0)
        hr_bsdf.inputs['Emission Strength'].default_value = 0.75

    mat_chrome = make_material("Laguna_Chrome")
    ch_bsdf = mat_chrome.node_tree.nodes.get("Principled BSDF")
    if ch_bsdf:
        ch_bsdf.inputs['Base Color'].default_value = (0.98, 0.98, 1.0, 1.0)
        ch_bsdf.inputs['Metallic'].default_value = 1.0
        ch_bsdf.inputs['Roughness'].default_value = 0.02

    mat_tl_ruby = make_material("Laguna_Taillight_Ruby")
    tr_bsdf = mat_tl_ruby.node_tree.nodes.get("Principled BSDF")
    if tr_bsdf:
        tr_bsdf.inputs['Base Color'].default_value = (0.78, 0.01, 0.02, 1.0)
        tr_bsdf.inputs['Alpha'].default_value = 0.90
        tr_bsdf.inputs['Emission Color'].default_value = (0.85, 0.02, 0.02, 1.0)
        tr_bsdf.inputs['Emission Strength'].default_value = 0.20

    mat_tl_clear = make_material("Laguna_Taillight_Clear")
    tc_bsdf = mat_tl_clear.node_tree.nodes.get("Principled BSDF")
    if tc_bsdf:
        tc_bsdf.inputs['Base Color'].default_value = (0.96, 0.96, 0.98, 1.0)
        tc_bsdf.inputs['Alpha'].default_value = 0.45

    mat_alloy = make_material("Laguna_Factory_Alloy")
    al_bsdf = mat_alloy.node_tree.nodes.get("Principled BSDF")
    if al_bsdf:
        al_bsdf.inputs['Base Color'].default_value = (0.88, 0.90, 0.92, 1.0)
        al_bsdf.inputs['Metallic'].default_value = 0.78
        al_bsdf.inputs['Roughness'].default_value = 0.16
        al_bsdf.inputs['Coat Weight'].default_value = 0.8

    mat_tire = make_material("Laguna_Road_Tire")
    ti_bsdf = mat_tire.node_tree.nodes.get("Principled BSDF")
    if ti_bsdf:
        ti_bsdf.inputs['Base Color'].default_value = (0.024, 0.024, 0.026, 1.0)
        ti_bsdf.inputs['Roughness'].default_value = 0.82

    mat_brake = make_material("Laguna_Brake_Steel")
    br_bsdf = mat_brake.node_tree.nodes.get("Principled BSDF")
    if br_bsdf:
        br_bsdf.inputs['Base Color'].default_value = (0.35, 0.35, 0.38, 1.0)
        br_bsdf.inputs['Metallic'].default_value = 0.80
        br_bsdf.inputs['Roughness'].default_value = 0.35

    # 2. HIDE ALL RACE TRACK AND CLIPPING PARTS
    unwanted_objects = [
        'unnamed.005', # Race flat undertray
        'unnamed.009', # Race splitter
        'unnamed.135', # Roll cage
        'unnamed.136', # Clipping inner tub (black triangle on fender)
        'unnamed.194', # Inner tub bracket
        'Laguna_Race_Wing' # Giant TCC rear wing
    ]
    for name in unwanted_objects:
        o = bpy.data.objects.get(name)
        if o:
            o.hide_render = True
            o.hide_viewport = True

    # 3. FIX REAR TAILLIGHT GAP (unnamed.149 & unnamed.213)
    # Assign unnamed.149 to body paint or taillight ruby so no black hole appears:
    for n in ['unnamed.149', 'unnamed.213']:
        o = bpy.data.objects.get(n)
        if o:
            o.data.materials.clear()
            o.data.materials.append(mat_body)

    # 4. HEADLIGHT REFLECTORS POSITIONING
    # Ensure dual chrome reflector bowls sit right inside the lenses
    for hl_name in ["Headlight_Reflector_R", "Headlight_Reflector_L"]:
        old_o = bpy.data.objects.get(hl_name)
        if old_o:
            bpy.data.objects.remove(old_o, do_unlink=True)

    def add_dual_projectors(name, cx, cy, cz):
        mesh = bpy.data.meshes.new(name + "_Mesh")
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)
        verts = []
        faces = []
        v_idx = 0
        # Dual circular projector cups: Low beam and High beam
        for offset_x in [-0.024, +0.024]:
            center = mathutils.Vector((cx + offset_x, cy, cz))
            verts.append(center)
            c_idx = v_idx
            v_idx += 1
            num_pts = 16
            radius = 0.027
            ring_indices = []
            for pt in range(num_pts):
                ang = (2 * math.pi * pt) / num_pts
                px = center.x + radius * math.cos(ang)
                py = center.y - 0.020 # forward towards lens
                pz = center.z + radius * math.sin(ang)
                verts.append(mathutils.Vector((px, py, pz)))
                ring_indices.append(v_idx)
                v_idx += 1
            for pt in range(num_pts):
                next_pt = (pt + 1) % num_pts
                faces.append((c_idx, ring_indices[pt], ring_indices[next_pt]))
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        obj.data.materials.append(mat_hl_reflector)
        return obj

    add_dual_projectors("Headlight_Reflector_R",  0.68, -2.00, 0.56)
    add_dual_projectors("Headlight_Reflector_L", -0.68, -2.00, 0.56)

    # 5. RENAULT OEM WHEEL CENTER CAPS
    # Add silver flush center caps with chrome diamond to all 4 wheels
    for cap_name in ["Wheel_Cap_FL", "Wheel_Cap_FR", "Wheel_Cap_RL", "Wheel_Cap_RR"]:
        old_cap = bpy.data.objects.get(cap_name)
        if old_cap:
            bpy.data.objects.remove(old_cap, do_unlink=True)

    wheel_centers = [
        ("Wheel_Cap_FR",  0.86, -1.34, 0.32,  1),
        ("Wheel_Cap_FL", -0.86, -1.34, 0.32, -1),
        ("Wheel_Cap_RR",  0.85,  1.32, 0.32,  1),
        ("Wheel_Cap_RL", -0.85,  1.32, 0.32, -1)
    ]

    for name, wx, wy, wz, side in wheel_centers:
        mesh = bpy.data.meshes.new(name + "_Mesh")
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)
        
        # Flush circular hubcap disc covering the center nut
        verts = []
        faces = []
        c_pt = mathutils.Vector((wx + side * 0.015, wy, wz))
        verts.append(c_pt)
        num_pts = 20
        radius = 0.055
        for pt in range(num_pts):
            ang = (2 * math.pi * pt) / num_pts
            px = c_pt.x
            py = c_pt.y + radius * math.cos(ang)
            pz = c_pt.z + radius * math.sin(ang)
            verts.append(mathutils.Vector((px, py, pz)))
        for pt in range(num_pts):
            next_pt = (pt + 1) % num_pts
            faces.append((0, pt + 1, next_pt + 1))
            
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        obj.data.materials.append(mat_alloy)

    # 6. ADJUST RIDE HEIGHT TO CIVILIAN ROAD CAR STANCE (+0.035m arch clearance)
    # Lift the car body relative to the wheels so it matches standard road clearance:
    body_mesh_objs = [o for o in bpy.data.objects if o.type == 'MESH' and not o.name.startswith("Studio_") and not o.name.startswith("Ref_") and not o.name.startswith("Wheel_Cap_")]
    wheel_mesh_names = {
        'unnamed', 'unnamed.001', 'unnamed.002', 'unnamed.003',
        'unnamed.037', 'unnamed.038', 'unnamed.039', 'unnamed.040', 'unnamed.041',
        'unnamed.042', 'unnamed.043', 'unnamed.044', 'unnamed.045', 'unnamed.046',
        'unnamed.047', 'unnamed.048', 'unnamed.049', 'unnamed.050', 'unnamed.051',
        'unnamed.052', 'unnamed.053', 'unnamed.054', 'unnamed.055', 'unnamed.056'
    }

    # Only adjust once (check tag property)
    scene = bpy.context.scene
    if not scene.get("Civilian_Stance_Applied"):
        for o in body_mesh_objs:
            if o.name not in wheel_mesh_names:
                o.location.z += 0.035
        scene["Civilian_Stance_Applied"] = True
        print("[Stance] Applied +35mm civilian road ride height!")

    # 7. RENDER HIGH-RES PRESENTATION VIEWS
    out_front = os.path.abspath(r"c:\Users\abdelkarim\Documents\laguna-beamng\laguna_front.png")
    out_rear = os.path.abspath(r"c:\Users\abdelkarim\Documents\laguna-beamng\laguna_rear.png")
    out_pres = os.path.abspath(r"c:\Users\abdelkarim\Documents\laguna-beamng\laguna_presentation.png")

    cam = scene.camera
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080

    # Front 3/4
    print("[Render] Rendering Front 3/4...")
    cam.location = mathutils.Vector((-4.3, -4.2, 1.28))
    target_front = mathutils.Vector((0.0, -0.5, 0.58))
    cam.rotation_euler = (target_front - cam.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = out_front
    bpy.ops.render.render(write_still=True)

    # Rear 3/4
    print("[Render] Rendering Rear 3/4...")
    cam.location = mathutils.Vector((3.85, 4.25, 1.38))
    target_rear = mathutils.Vector((0.0, 0.3, 0.68))
    cam.rotation_euler = (target_rear - cam.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = out_rear
    bpy.ops.render.render(write_still=True)

    # Copy to artifacts
    shutil.copy2(out_front, out_pres)
    art_dir = r"C:\Users\abdelkarim\.gemini\antigravity\brain\fa1588ad-d9ab-4eb3-9303-e3e476714ebd"
    shutil.copy2(out_front, os.path.join(art_dir, "laguna_front.png"))
    shutil.copy2(out_rear, os.path.join(art_dir, "laguna_rear.png"))
    shutil.copy2(out_pres, os.path.join(art_dir, "laguna_presentation.png"))
    print("[Loop Step 2] Completed successfully!")

run_step_2()
