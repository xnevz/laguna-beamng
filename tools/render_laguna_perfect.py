"""
Final Polish: Replicate the user reference images with exact part colors,
materials, and bright, high-contrast automotive photography lighting.
"""

import bpy
import mathutils
import math
import os
import shutil

def render_laguna_perfect():
    print("[Laguna Polish] Configuring exact part colors, multi-slot assignments, and lighting...")

    def make_material(name):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        return mat

    # 1. SHADERS
    # A) Renault Champagne Silver / Beige Poivre Metallic
    mat_body = make_material("Laguna_Champagne_Silver")
    b_bsdf = mat_body.node_tree.nodes.get("Principled BSDF")
    if b_bsdf:
        b_bsdf.inputs['Base Color'].default_value = (0.76, 0.72, 0.62, 1.0)
        b_bsdf.inputs['Metallic'].default_value = 0.82
        b_bsdf.inputs['Roughness'].default_value = 0.20
        b_bsdf.inputs['Coat Weight'].default_value = 1.0
        b_bsdf.inputs['Coat Roughness'].default_value = 0.02
        b_bsdf.inputs['Coat IOR'].default_value = 1.50
        b_bsdf.inputs['Specular IOR Level'].default_value = 0.55

    # B) Solarglass (Authentic Renault green heat-rejecting automotive glass)
    mat_glass = make_material("Laguna_Factory_Solarglass")
    g_bsdf = mat_glass.node_tree.nodes.get("Principled BSDF")
    if g_bsdf:
        g_bsdf.inputs['Base Color'].default_value = (0.82, 0.94, 0.88, 1.0)
        g_bsdf.inputs['Metallic'].default_value = 0.0
        g_bsdf.inputs['Roughness'].default_value = 0.012
        g_bsdf.inputs['Alpha'].default_value = 0.40
        g_bsdf.inputs['IOR'].default_value = 1.52
        g_bsdf.inputs['Coat Weight'].default_value = 1.0
        g_bsdf.inputs['Coat Roughness'].default_value = 0.01
    mat_glass.blend_method = 'BLEND'

    # C) Textured Dark Charcoal Plastic (Door mouldings & bumper impact strips)
    mat_moulding = make_material("Laguna_Trim_Charcoal")
    m_bsdf = mat_moulding.node_tree.nodes.get("Principled BSDF")
    if m_bsdf:
        m_bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.055, 1.0)
        m_bsdf.inputs['Metallic'].default_value = 0.0
        m_bsdf.inputs['Roughness'].default_value = 0.78

    # D) Satin Black (Pillars, wipers, lower grille intakes)
    mat_black = make_material("Laguna_Pillar_Black")
    bk_bsdf = mat_black.node_tree.nodes.get("Principled BSDF")
    if bk_bsdf:
        bk_bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.025, 1.0)
        bk_bsdf.inputs['Metallic'].default_value = 0.0
        bk_bsdf.inputs['Roughness'].default_value = 0.60

    # E) Amber Side Repeaters & Turn Indicators
    mat_amber = make_material("Laguna_Amber_Indicator")
    am_bsdf = mat_amber.node_tree.nodes.get("Principled BSDF")
    if am_bsdf:
        am_bsdf.inputs['Base Color'].default_value = (0.98, 0.45, 0.02, 1.0)
        am_bsdf.inputs['Metallic'].default_value = 0.05
        am_bsdf.inputs['Roughness'].default_value = 0.03
        am_bsdf.inputs['Alpha'].default_value = 0.85
        am_bsdf.inputs['IOR'].default_value = 1.50
    mat_amber.blend_method = 'BLEND'

    # F) Headlight Clear Lens
    mat_hl_lens = make_material("Laguna_Headlight_Glass")
    hl_bsdf = mat_hl_lens.node_tree.nodes.get("Principled BSDF")
    if hl_bsdf:
        hl_bsdf.inputs['Base Color'].default_value = (0.97, 0.98, 1.0, 1.0)
        hl_bsdf.inputs['Metallic'].default_value = 0.0
        hl_bsdf.inputs['Roughness'].default_value = 0.01
        hl_bsdf.inputs['Alpha'].default_value = 0.15
        hl_bsdf.inputs['IOR'].default_value = 1.50
        hl_bsdf.inputs['Coat Weight'].default_value = 1.0
        hl_bsdf.inputs['Coat Roughness'].default_value = 0.01
    mat_hl_lens.blend_method = 'BLEND'

    # G) Headlight Reflector Chrome (Mirrored with subtle headlight glow)
    mat_hl_chrome = make_material("Laguna_Headlight_Reflector")
    hc_bsdf = mat_hl_chrome.node_tree.nodes.get("Principled BSDF")
    if hc_bsdf:
        hc_bsdf.inputs['Base Color'].default_value = (0.95, 0.97, 1.0, 1.0)
        hc_bsdf.inputs['Metallic'].default_value = 0.95
        hc_bsdf.inputs['Roughness'].default_value = 0.05
        hc_bsdf.inputs['Emission Color'].default_value = (0.98, 0.99, 1.0, 1.0)
        hc_bsdf.inputs['Emission Strength'].default_value = 0.45 # Crisp headlight reflector glow

    # H) Emblems & Badges (Pure Chrome)
    mat_chrome = make_material("Laguna_Chrome")
    ch_bsdf = mat_chrome.node_tree.nodes.get("Principled BSDF")
    if ch_bsdf:
        ch_bsdf.inputs['Base Color'].default_value = (0.98, 0.98, 1.0, 1.0)
        ch_bsdf.inputs['Metallic'].default_value = 1.0
        ch_bsdf.inputs['Roughness'].default_value = 0.02

    # I) Taillights: Deep Ruby Red Lens
    mat_tl_ruby = make_material("Laguna_Taillight_Ruby")
    tr_bsdf = mat_tl_ruby.node_tree.nodes.get("Principled BSDF")
    if tr_bsdf:
        tr_bsdf.inputs['Base Color'].default_value = (0.78, 0.01, 0.02, 1.0)
        tr_bsdf.inputs['Metallic'].default_value = 0.05
        tr_bsdf.inputs['Roughness'].default_value = 0.03
        tr_bsdf.inputs['Alpha'].default_value = 0.90
        tr_bsdf.inputs['IOR'].default_value = 1.52
        tr_bsdf.inputs['Coat Weight'].default_value = 1.0
        tr_bsdf.inputs['Coat Roughness'].default_value = 0.02
        tr_bsdf.inputs['Emission Color'].default_value = (0.85, 0.02, 0.02, 1.0)
        tr_bsdf.inputs['Emission Strength'].default_value = 0.25 # Authentic internal red taillight glow
    mat_tl_ruby.blend_method = 'BLEND'

    # J) Taillights: Clear Reverse Lamp Strip
    mat_tl_clear = make_material("Laguna_Taillight_Clear")
    tc_bsdf = mat_tl_clear.node_tree.nodes.get("Principled BSDF")
    if tc_bsdf:
        tc_bsdf.inputs['Base Color'].default_value = (0.96, 0.96, 0.98, 1.0)
        tc_bsdf.inputs['Metallic'].default_value = 0.05
        tc_bsdf.inputs['Roughness'].default_value = 0.03
        tc_bsdf.inputs['Alpha'].default_value = 0.45
        tc_bsdf.inputs['IOR'].default_value = 1.50
    mat_tl_clear.blend_method = 'BLEND'

    # K) Wheels: Renault Factory Silver Alloy
    mat_alloy = make_material("Laguna_Factory_Alloy")
    al_bsdf = mat_alloy.node_tree.nodes.get("Principled BSDF")
    if al_bsdf:
        al_bsdf.inputs['Base Color'].default_value = (0.86, 0.88, 0.90, 1.0)
        al_bsdf.inputs['Metallic'].default_value = 0.78
        al_bsdf.inputs['Roughness'].default_value = 0.18
        al_bsdf.inputs['Coat Weight'].default_value = 0.8
        al_bsdf.inputs['Coat Roughness'].default_value = 0.03

    # L) Wheels: Road Rubber Tires
    mat_tire = make_material("Laguna_Road_Tire")
    ti_bsdf = mat_tire.node_tree.nodes.get("Principled BSDF")
    if ti_bsdf:
        ti_bsdf.inputs['Base Color'].default_value = (0.022, 0.022, 0.025, 1.0)
        ti_bsdf.inputs['Metallic'].default_value = 0.0
        ti_bsdf.inputs['Roughness'].default_value = 0.82

    # M) Brake Discs & Calipers
    mat_brake = make_material("Laguna_Brake_Steel")
    br_bsdf = mat_brake.node_tree.nodes.get("Principled BSDF")
    if br_bsdf:
        br_bsdf.inputs['Base Color'].default_value = (0.35, 0.35, 0.38, 1.0)
        br_bsdf.inputs['Metallic'].default_value = 0.80
        br_bsdf.inputs['Roughness'].default_value = 0.35

    # N) Interior Cockpit
    mat_interior = make_material("Laguna_Interior_Charcoal")
    in_bsdf = mat_interior.node_tree.nodes.get("Principled BSDF")
    if in_bsdf:
        in_bsdf.inputs['Base Color'].default_value = (0.04, 0.04, 0.045, 1.0)
        in_bsdf.inputs['Metallic'].default_value = 0.0
        in_bsdf.inputs['Roughness'].default_value = 0.85

    # ==========================================
    # 2. MULTI-SLOT ASSIGNMENT ON MAIN BODY MESH
    # ==========================================
    # unnamed.004 contains the entire body unibody, door outer skins, and lower valance.
    # We assign multiple material slots and map polygons by their function:
    o4 = bpy.data.objects.get('unnamed.004')
    if o4:
        o4.data.materials.clear()
        o4.data.materials.append(mat_body)      # Slot 0: Champagne Silver body
        o4.data.materials.append(mat_moulding)  # Slot 1: Dark Charcoal door rub strips & rear bumper strip
        o4.data.materials.append(mat_black)     # Slot 2: Satin Black lower air intake & underbody
        o4.data.materials.append(mat_amber)     # Slot 3: Amber side repeater

        m4 = o4.data
        for p in m4.polygons:
            pts = [m4.vertices[v].co for v in p.vertices]
            cx = sum(pt.x for pt in pts) / len(pts)
            cy = sum(pt.y for pt in pts) / len(pts)
            cz = sum(pt.z for pt in pts) / len(pts)

            # A) Side door rubbing strips (running along both doors)
            if abs(cx) > 0.70 and 0.52 < cz < 0.63 and -1.05 < cy < 1.10:
                p.material_index = 1
            # B) Rear bumper impact strip
            elif cy > 2.05 and 0.62 < cz < 0.76:
                p.material_index = 1
            # C) Lower front air intake & underbody
            elif cy < -1.85 and cz < 0.45:
                p.material_index = 2
            # D) Amber side repeater indicator
            elif abs(cx) > 0.75 and 0.54 < cz < 0.60 and -0.90 < cy < -0.75:
                p.material_index = 3
            # E) Everything else: Body paint
            else:
                p.material_index = 0

    # unnamed.006 contains the hood and front grille:
    o6 = bpy.data.objects.get('unnamed.006')
    if o6:
        o6.data.materials.clear()
        o6.data.materials.append(mat_body)      # Slot 0: Hood
        o6.data.materials.append(mat_black)     # Slot 1: Grille intake slots
        o6.data.materials.append(mat_chrome)    # Slot 2: Renault Diamond emblem
        m6 = o6.data
        for p in m6.polygons:
            pts = [m6.vertices[v].co for v in p.vertices]
            cx = sum(pt.x for pt in pts) / len(pts)
            cy = sum(pt.y for pt in pts) / len(pts)
            cz = sum(pt.z for pt in pts) / len(pts)
            if cy < -2.05:
                if abs(cx) < 0.08 and 0.52 < cz < 0.65:
                    p.material_index = 2 # Renault diamond
                else:
                    p.material_index = 1 # Black grille slots
            else:
                p.material_index = 0     # Hood body paint

    # ==========================================
    # 3. ASSIGN ALL OTHER OBJECTS
    # ==========================================
    # Specific maps
    body_panel_names = {
        'unnamed.005', 'unnamed.007', 'unnamed.008',
        'unnamed.011', 'unnamed.025', 'unnamed.026', 'unnamed.028',
        'unnamed.057', 'unnamed.063', 'unnamed.083', 'unnamed.137',
        'unnamed.139', 'unnamed.140', 'unnamed.143', 'unnamed.145',
        'unnamed.146', 'unnamed.150', 'unnamed.166', 'unnamed.167',
        'unnamed.173', 'unnamed.174', 'unnamed.223', 'unnamed.224',
        'unnamed.230', 'unnamed.231', 'unnamed.240', 'unnamed.246'
    }

    moulding_names = {
        'unnamed.141', 'unnamed.147', 'unnamed.205', 'unnamed.211',
        'unnamed.024', 'unnamed.151', 'unnamed.215'
    }

    amber_names = {'unnamed.061', 'unnamed.067'}

    chrome_names = {
        'unnamed.014', 'unnamed.154', 'unnamed.218',
        'unnamed.168', 'unnamed.175', 'unnamed.225', 'unnamed.232'
    }

    headlight_lens_names = {'unnamed.017', 'unnamed.019', 'unnamed.070', 'unnamed.071'}
    headlight_reflector_names = {'unnamed.012'}

    taillight_ruby_names = {
        'unnamed.010', 'unnamed.015', 'unnamed.016',
        'unnamed.031', 'unnamed.220', # 3rd brake light on decklid
        'unnamed.032', 'unnamed.033'  # Inner taillight lenses on tailgate!
    }
    taillight_clear_names = {'unnamed.018', 'unnamed.020'}

    solarglass_names = {
        'unnamed.021', 'unnamed.022', 'unnamed.023', 'unnamed.027', 'unnamed.029', 'unnamed.030',
        'unnamed.058', 'unnamed.059', 'unnamed.060', 'unnamed.062', 'unnamed.064', 'unnamed.065',
        'unnamed.066', 'unnamed.068', 'unnamed.142', 'unnamed.148', 'unnamed.152',
        'unnamed.155', 'unnamed.159', 'unnamed.161', 'unnamed.163', 'unnamed.164', 'unnamed.170',
        'unnamed.171', 'unnamed.172', 'unnamed.177', 'unnamed.178', 'unnamed.179', 'unnamed.190',
        'unnamed.196', 'unnamed.199', 'unnamed.206', 'unnamed.212', 'unnamed.216', 'unnamed.219',
        'unnamed.221', 'unnamed.222', 'unnamed.227', 'unnamed.228', 'unnamed.229', 'unnamed.234',
        'unnamed.235', 'unnamed.236', 'unnamed.238', 'unnamed.241', 'unnamed.242', 'unnamed.243',
        'unnamed.244', 'unnamed.245', 'unnamed.247', 'unnamed.248', 'unnamed.249', 'unnamed.250',
        'unnamed.251'
    }

    black_trim_names = {
        'unnamed.013', 'unnamed.069', 'unnamed.034', 'unnamed.035',
        'unnamed.036', 'unnamed.149', 'unnamed.213', 'unnamed.237',
        'unnamed.239', 'unnamed.169', 'unnamed.176', 'unnamed.226', 'unnamed.233'
    }

    brake_names = {
        'unnamed.038', 'unnamed.042', 'unnamed.047', 'unnamed.053',
        'unnamed.037', 'unnamed.046', 'unnamed.051', 'unnamed.052'
    }

    objs = [o for o in bpy.data.objects if o.type == 'MESH' and o.name not in ['unnamed.004', 'unnamed.006'] and not o.name.startswith("Studio_") and not o.name.startswith("Ref_") and not o.name.endswith("_Bounds")]
    for o in objs:
        o.hide_render = False
        o.data.materials.clear()

        if o.name in body_panel_names:
            o.data.materials.append(mat_body)
        elif o.name in moulding_names:
            o.data.materials.append(mat_moulding)
        elif o.name in amber_names:
            o.data.materials.append(mat_amber)
        elif o.name in chrome_names:
            o.data.materials.append(mat_chrome)
        elif o.name in headlight_lens_names:
            o.data.materials.append(mat_hl_lens)
        elif o.name in headlight_reflector_names:
            o.data.materials.append(mat_hl_chrome)
        elif o.name in taillight_ruby_names:
            o.data.materials.append(mat_tl_ruby)
        elif o.name in taillight_clear_names:
            o.data.materials.append(mat_tl_clear)
        elif o.name in solarglass_names:
            o.data.materials.append(mat_glass)
        elif o.name in black_trim_names:
            o.data.materials.append(mat_black)
        elif o.name in brake_names:
            o.data.materials.append(mat_brake)
        else:
            verts = [o.matrix_world @ v.co for v in o.data.vertices]
            if not verts: continue
            cx = sum(v.x for v in verts) / len(verts)
            cy = sum(v.y for v in verts) / len(verts)
            cz = sum(v.z for v in verts) / len(verts)
            dx = max(v.x for v in verts) - min(v.x for v in verts)
            dy = max(v.y for v in verts) - min(v.y for v in verts)
            dz = max(v.z for v in verts) - min(v.z for v in verts)

            if cz < 0.45 and abs(cx) > 0.60:
                if max(dy, dz) > 0.45 and dx > 0.15:
                    o.data.materials.append(mat_tire)
                else:
                    o.data.materials.append(mat_alloy)
            elif -1.35 < cy < 0.95 and 0.28 < cz < 1.15 and abs(cx) < 0.58:
                o.data.materials.append(mat_interior)
            else:
                o.data.materials.append(mat_body)

    # Hide race track accessories
    for ro_name in ['unnamed.009', 'Laguna_Race_Wing']:
        ro = bpy.data.objects.get(ro_name)
        if ro:
            ro.hide_render = True

    # ==========================================
    # 4. BALANCED DAYLIGHT LIGHTING & EXPOSURE
    # ==========================================
    for l in [o for o in bpy.data.objects if o.name.startswith("Studio_")]:
        bpy.data.objects.remove(l, do_unlink=True)

    # A) Dark road asphalt ground plane for high contrast
    plane_mesh = bpy.data.meshes.new("Ground_Pavement_Mesh")
    ground = bpy.data.objects.new("Studio_Pavement", plane_mesh)
    bpy.context.collection.objects.link(ground)
    verts = [
        mathutils.Vector((-30.0, -30.0, 0.0)),
        mathutils.Vector(( 30.0, -30.0, 0.0)),
        mathutils.Vector(( 30.0,  30.0, 0.0)),
        mathutils.Vector((-30.0,  30.0, 0.0))
    ]
    faces = [(0, 1, 2, 3)]
    plane_mesh.from_pydata(verts, [], faces)
    plane_mesh.update()

    mat_pave = make_material("Studio_Pavement_Mat")
    bsdf_pv = mat_pave.node_tree.nodes.get("Principled BSDF")
    if bsdf_pv:
        bsdf_pv.inputs['Base Color'].default_value = (0.16, 0.17, 0.19, 1.0) # Real dark asphalt road
        bsdf_pv.inputs['Roughness'].default_value = 0.85
        bsdf_pv.inputs['Specular IOR Level'].default_value = 0.25
    ground.data.materials.append(mat_pave)

    # B) Main Sun: Warm natural sunlight
    sun_data = bpy.data.lights.new(name="Studio_Sun_Light", type='SUN')
    sun_data.energy = 4.8
    sun_data.color = (1.0, 0.98, 0.94)
    sun_data.angle = math.radians(2.5)
    sun_obj = bpy.data.objects.new(name="Studio_Sun", object_data=sun_data)
    bpy.context.collection.objects.link(sun_obj)
    sun_obj.location = (4.5, -4.5, 7.0)
    sun_obj.rotation_euler = (math.radians(45), math.radians(15), math.radians(-35))

    # C) Ambient Sky Fill (Balanced, no blowout)
    sky_data = bpy.data.lights.new(name="Studio_Sky_Data", type='AREA')
    sky_data.energy = 500.0 # Clean, balanced fill
    sky_data.color = (0.92, 0.96, 1.0)
    sky_data.size = 14.0
    sky_data.size_y = 14.0
    sky_obj = bpy.data.objects.new(name="Studio_Sky_Light", object_data=sky_data)
    bpy.context.collection.objects.link(sky_obj)
    sky_obj.location = (0.0, 0.0, 7.5)
    sky_obj.rotation_euler = (0, 0, 0)

    # D) Side / Flank Fill
    fill_data = bpy.data.lights.new(name="Studio_SideFill_Data", type='AREA')
    fill_data.energy = 300.0
    fill_data.color = (0.96, 0.97, 0.98)
    fill_data.size = 8.0
    fill_data.size_y = 3.0
    fill_obj = bpy.data.objects.new(name="Studio_SideFill", object_data=fill_data)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.location = (-5.5, 0.0, 2.5)
    fill_obj.rotation_euler = (0, math.radians(75), math.radians(-90))

    # E) Headlight & Grille Glint Light
    glint_data = bpy.data.lights.new(name="Studio_Glint_Data", type='AREA')
    glint_data.energy = 250.0
    glint_data.color = (1.0, 1.0, 1.0)
    glint_data.size = 3.0
    glint_data.size_y = 1.5
    glint_obj = bpy.data.objects.new(name="Studio_Glint", object_data=glint_data)
    bpy.context.collection.objects.link(glint_obj)
    glint_obj.location = (-1.5, -5.0, 1.2)
    glint_obj.rotation_euler = (math.radians(75), 0, math.radians(15))

    # F) World Environment & Color Management
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("Studio_World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.55, 0.62, 0.72, 1.0) # Balanced daylight sky
        bg.inputs['Strength'].default_value = 0.40

    # Color Management: AgX with high contrast
    scene = bpy.context.scene
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - High Contrast'

    # ==========================================
    # 5. RENDER FRONT 3/4 & REAR 3/4
    # ==========================================
    cam = scene.camera
    if not cam:
        cam = bpy.data.objects.get("Camera")
    if not cam:
        cam_data = bpy.data.cameras.new("Main_Camera")
        cam_data.lens = 45.0
        cam = bpy.data.objects.new("Main_Camera", cam_data)
        bpy.context.collection.objects.link(cam)
    scene.camera = cam
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080

    out_front = os.path.abspath(r"c:\Users\abdelkarim\Documents\laguna-beamng\laguna_front.png")
    out_rear = os.path.abspath(r"c:\Users\abdelkarim\Documents\laguna-beamng\laguna_rear.png")
    out_pres = os.path.abspath(r"c:\Users\abdelkarim\Documents\laguna-beamng\laguna_presentation.png")

    # VIEW 1: FRONT 3/4 (Matching User Image 2 - Renault Algérie angle)
    # Camera at (-4.3, -4.2, 1.25) looking at front (0.0, -0.5, 0.55)
    print("[Render] Rendering Front 3/4...")
    cam.location = mathutils.Vector((-4.3, -4.2, 1.25))
    target_front = mathutils.Vector((0.0, -0.5, 0.55))
    cam.rotation_euler = (target_front - cam.location).to_track_quat('-Z', 'Y').to_euler()

    scene.render.filepath = out_front
    bpy.ops.render.render(write_still=True)
    print(f"[Render] Saved {out_front}")

    # VIEW 2: REAR 3/4 (Matching User Image 1 & 3 angle)
    # Camera at (+3.85, +4.25, 1.35) looking at rear (0.0, +0.3, 0.65)
    print("[Render] Rendering Rear 3/4...")
    cam.location = mathutils.Vector((3.85, 4.25, 1.35))
    target_rear = mathutils.Vector((0.0, 0.3, 0.65))
    cam.rotation_euler = (target_rear - cam.location).to_track_quat('-Z', 'Y').to_euler()

    scene.render.filepath = out_rear
    bpy.ops.render.render(write_still=True)
    print(f"[Render] Saved {out_rear}")

    # Copy to presentation and artifacts
    shutil.copy2(out_front, out_pres)
    art_dir = r"C:\Users\abdelkarim\.gemini\antigravity\brain\fa1588ad-d9ab-4eb3-9303-e3e476714ebd"
    shutil.copy2(out_front, os.path.join(art_dir, "laguna_front.png"))
    shutil.copy2(out_rear, os.path.join(art_dir, "laguna_rear.png"))
    shutil.copy2(out_pres, os.path.join(art_dir, "laguna_presentation.png"))
    print("[Render] All artifact images updated successfully!")

render_laguna_perfect()
