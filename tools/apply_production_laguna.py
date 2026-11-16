"""
Apply authentic Renault Laguna II / Phase 1 production materials, colors, and lighting:
- Champagne Silver (Gris Angora / Beige Poivre) metallic body paint with clearcoat
- Contrast dark charcoal door rubbing strips & bumper impact strips
- Amber side repeaters on front door/fender
- Satin black B-pillars and window frame surrounds
- Renault Solarglass (pale green-tinted automotive glass with high specular reflection)
- Renault OEM silver alloy wheels with black road rubber tires and chrome center badge
- Two-tone red & clear reverse taillights + 3rd brake light on decklid
- Crystal clear headlights with chrome internal reflector bowls
- Polished chrome Renault diamond emblems and badges
- Natural bright daylight photography lighting so every part of the car is crisp and visible
"""

import bpy
import mathutils
import math
import os
import shutil

def apply_production_laguna():
    print("[Production Laguna] Setting up materials matching reference images...")

    def make_material(name):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        return mat

    # ==========================================
    # 1. PBR SHADERS
    # ==========================================

    # A) Renault Champagne Silver / Beige Poivre Metallic
    # Warm metallic platinum-silver with high-gloss automotive clearcoat
    mat_body = make_material("Laguna_Champagne_Silver")
    bsdf_body = mat_body.node_tree.nodes.get("Principled BSDF")
    if bsdf_body:
        bsdf_body.inputs['Base Color'].default_value = (0.72, 0.69, 0.61, 1.0)
        bsdf_body.inputs['Metallic'].default_value = 0.78
        bsdf_body.inputs['Roughness'].default_value = 0.22
        bsdf_body.inputs['Coat Weight'].default_value = 1.0
        bsdf_body.inputs['Coat Roughness'].default_value = 0.02
        bsdf_body.inputs['Coat IOR'].default_value = 1.50
        bsdf_body.inputs['Specular IOR Level'].default_value = 0.5

    # B) Factory Renault Solarglass (Green-tinted automotive safety glass)
    # Subtle green tint, high specular reflection, transparent to interior
    mat_glass = make_material("Laguna_Factory_Solarglass")
    bsdf_g = mat_glass.node_tree.nodes.get("Principled BSDF")
    if bsdf_g:
        bsdf_g.inputs['Base Color'].default_value = (0.80, 0.94, 0.88, 1.0)
        bsdf_g.inputs['Metallic'].default_value = 0.0
        bsdf_g.inputs['Roughness'].default_value = 0.015
        bsdf_g.inputs['Alpha'].default_value = 0.40 # Authentic transparency
        bsdf_g.inputs['IOR'].default_value = 1.52
        bsdf_g.inputs['Coat Weight'].default_value = 1.0
        bsdf_g.inputs['Coat Roughness'].default_value = 0.01
    mat_glass.blend_method = 'BLEND'

    # C) Protective Side Mouldings & Bumper Impact Strips (Dark Charcoal Plastic)
    mat_moulding = make_material("Laguna_Trim_Charcoal")
    bsdf_m = mat_moulding.node_tree.nodes.get("Principled BSDF")
    if bsdf_m:
        bsdf_m.inputs['Base Color'].default_value = (0.08, 0.08, 0.085, 1.0)
        bsdf_m.inputs['Metallic'].default_value = 0.0
        bsdf_m.inputs['Roughness'].default_value = 0.78

    # D) B-Pillars, Window Rubber & Wiper Blades (Satin Black)
    mat_black_trim = make_material("Laguna_Pillar_Black")
    bsdf_bt = mat_black_trim.node_tree.nodes.get("Principled BSDF")
    if bsdf_bt:
        bsdf_bt.inputs['Base Color'].default_value = (0.035, 0.035, 0.04, 1.0)
        bsdf_bt.inputs['Metallic'].default_value = 0.0
        bsdf_bt.inputs['Roughness'].default_value = 0.60

    # E) Amber Side Repeaters & Front Turn Indicators
    mat_amber = make_material("Laguna_Amber_Indicator")
    bsdf_amb = mat_amber.node_tree.nodes.get("Principled BSDF")
    if bsdf_amb:
        bsdf_amb.inputs['Base Color'].default_value = (0.95, 0.42, 0.02, 1.0)
        bsdf_amb.inputs['Metallic'].default_value = 0.05
        bsdf_amb.inputs['Roughness'].default_value = 0.03
        bsdf_amb.inputs['Alpha'].default_value = 0.75
        bsdf_amb.inputs['IOR'].default_value = 1.50
    mat_amber.blend_method = 'BLEND'

    # F) Front Headlight Outer Clear Lens
    mat_hl_lens = make_material("Laguna_Headlight_Glass")
    bsdf_hl = mat_hl_lens.node_tree.nodes.get("Principled BSDF")
    if bsdf_hl:
        bsdf_hl.inputs['Base Color'].default_value = (0.96, 0.98, 1.0, 1.0)
        bsdf_hl.inputs['Metallic'].default_value = 0.0
        bsdf_hl.inputs['Roughness'].default_value = 0.01
        bsdf_hl.inputs['Alpha'].default_value = 0.18
        bsdf_hl.inputs['IOR'].default_value = 1.50
        bsdf_hl.inputs['Coat Weight'].default_value = 1.0
        bsdf_hl.inputs['Coat Roughness'].default_value = 0.01
    mat_hl_lens.blend_method = 'BLEND'

    # G) Chrome Reflector Bowls, Badges & Emblems
    mat_chrome = make_material("Laguna_Chrome")
    bsdf_ch = mat_chrome.node_tree.nodes.get("Principled BSDF")
    if bsdf_ch:
        bsdf_ch.inputs['Base Color'].default_value = (0.98, 0.98, 1.0, 1.0)
        bsdf_ch.inputs['Metallic'].default_value = 1.0
        bsdf_ch.inputs['Roughness'].default_value = 0.03

    # H) Taillights: Deep Ruby Red Lens
    mat_tl_ruby = make_material("Laguna_Taillight_Ruby")
    bsdf_tr = mat_tl_ruby.node_tree.nodes.get("Principled BSDF")
    if bsdf_tr:
        bsdf_tr.inputs['Base Color'].default_value = (0.75, 0.01, 0.02, 1.0)
        bsdf_tr.inputs['Metallic'].default_value = 0.05
        bsdf_tr.inputs['Roughness'].default_value = 0.03
        bsdf_tr.inputs['Alpha'].default_value = 0.85
        bsdf_tr.inputs['IOR'].default_value = 1.52
        bsdf_tr.inputs['Coat Weight'].default_value = 1.0
        bsdf_tr.inputs['Coat Roughness'].default_value = 0.02
    mat_tl_ruby.blend_method = 'BLEND'

    # I) Taillights: Clear Reverse Lamp / White Section
    mat_tl_clear = make_material("Laguna_Taillight_Clear")
    bsdf_tw = mat_tl_clear.node_tree.nodes.get("Principled BSDF")
    if bsdf_tw:
        bsdf_tw.inputs['Base Color'].default_value = (0.95, 0.95, 0.98, 1.0)
        bsdf_tw.inputs['Metallic'].default_value = 0.05
        bsdf_tw.inputs['Roughness'].default_value = 0.03
        bsdf_tw.inputs['Alpha'].default_value = 0.50
        bsdf_tw.inputs['IOR'].default_value = 1.50
    mat_tl_clear.blend_method = 'BLEND'

    # J) Wheels: Renault Factory Silver Alloy
    mat_alloy = make_material("Laguna_Factory_Alloy")
    bsdf_al = mat_alloy.node_tree.nodes.get("Principled BSDF")
    if bsdf_al:
        bsdf_al.inputs['Base Color'].default_value = (0.86, 0.88, 0.90, 1.0)
        bsdf_al.inputs['Metallic'].default_value = 0.75
        bsdf_al.inputs['Roughness'].default_value = 0.20
        bsdf_al.inputs['Coat Weight'].default_value = 0.6
        bsdf_al.inputs['Coat Roughness'].default_value = 0.04

    # K) Wheels: Road Tires (Vulcanized Black Rubber)
    mat_tire = make_material("Laguna_Road_Tire")
    bsdf_ti = mat_tire.node_tree.nodes.get("Principled BSDF")
    if bsdf_ti:
        bsdf_ti.inputs['Base Color'].default_value = (0.025, 0.025, 0.028, 1.0)
        bsdf_ti.inputs['Metallic'].default_value = 0.0
        bsdf_ti.inputs['Roughness'].default_value = 0.80

    # L) Brake Discs & Calipers
    mat_brake = make_material("Laguna_Brake_Steel")
    bsdf_br = mat_brake.node_tree.nodes.get("Principled BSDF")
    if bsdf_br:
        bsdf_br.inputs['Base Color'].default_value = (0.35, 0.35, 0.37, 1.0)
        bsdf_br.inputs['Metallic'].default_value = 0.80
        bsdf_br.inputs['Roughness'].default_value = 0.40

    # M) Interior Cockpit (Dark Charcoal Dashboard & Trim)
    mat_interior = make_material("Laguna_Interior_Charcoal")
    bsdf_in = mat_interior.node_tree.nodes.get("Principled BSDF")
    if bsdf_in:
        bsdf_in.inputs['Base Color'].default_value = (0.05, 0.05, 0.055, 1.0)
        bsdf_in.inputs['Metallic'].default_value = 0.0
        bsdf_in.inputs['Roughness'].default_value = 0.85

    # ==========================================
    # 2. SCAN AND ASSIGN ALL MESHES ACCURATELY
    # ==========================================
    objs = [o for o in bpy.data.objects if o.type == 'MESH' and not o.name.startswith("Studio_") and not o.name.startswith("Ref_") and not o.name.startswith("Laguna_Race_Wing") and not o.name.endswith("_Bounds")]

    counts = {
        'body': 0, 'moulding': 0, 'glass': 0, 'wheels': 0, 'lights': 0, 'interior': 0, 'chrome': 0, 'trim': 0
    }

    # Specific known object mappings
    moulding_objs = {'unnamed.141', 'unnamed.147', 'unnamed.205', 'unnamed.211', 'unnamed.166', 'unnamed.173'}
    amber_objs = {'unnamed.061', 'unnamed.067', 'unnamed.070', 'unnamed.071'}
    chrome_objs = {'unnamed.154', 'unnamed.218', 'unnamed.014', 'unnamed.168', 'unnamed.175', 'unnamed.225', 'unnamed.232'}
    reverse_light_objs = {'unnamed.018', 'unnamed.020'}
    taillight_ruby_objs = {'unnamed.010', 'unnamed.015', 'unnamed.016', 'unnamed.031', 'unnamed.220'}
    headlight_lens_objs = {'unnamed.017', 'unnamed.019'}
    headlight_reflector_objs = {'unnamed.012'}
    black_trim_objs = {'unnamed.009', 'unnamed.013', 'unnamed.034', 'unnamed.069', 'unnamed.169', 'unnamed.176', 'unnamed.226', 'unnamed.233'}

    for o in objs:
        o.hide_render = False
        o.hide_viewport = False
        o.data.materials.clear()

        verts = [o.matrix_world @ v.co for v in o.data.vertices]
        if not verts: continue
        cx = sum(v.x for v in verts) / len(verts)
        cy = sum(v.y for v in verts) / len(verts)
        cz = sum(v.z for v in verts) / len(verts)
        dx = max(v.x for v in verts) - min(v.x for v in verts)
        dy = max(v.y for v in verts) - min(v.y for v in verts)
        dz = max(v.z for v in verts) - min(v.z for v in verts)

        # 1. SPECIFIC KNOWN PARTS
        if o.name in moulding_objs:
            o.data.materials.append(mat_moulding)
            counts['moulding'] += 1

        elif o.name in amber_objs:
            o.data.materials.append(mat_amber)
            counts['lights'] += 1

        elif o.name in chrome_objs:
            o.data.materials.append(mat_chrome)
            counts['chrome'] += 1

        elif o.name in reverse_light_objs:
            o.data.materials.append(mat_tl_clear)
            counts['lights'] += 1

        elif o.name in taillight_ruby_objs:
            o.data.materials.append(mat_tl_ruby)
            counts['lights'] += 1

        elif o.name in headlight_lens_objs:
            o.data.materials.append(mat_hl_lens)
            counts['lights'] += 1

        elif o.name in headlight_reflector_objs:
            o.data.materials.append(mat_chrome)
            counts['lights'] += 1

        elif o.name in black_trim_objs:
            o.data.materials.append(mat_black_trim)
            counts['trim'] += 1

        # 2. WHEELS
        elif cz < 0.45 and abs(cx) > 0.60:
            if max(dy, dz) > 0.45 and dx > 0.15:
                o.data.materials.append(mat_tire)
            elif o.name in ['unnamed.038', 'unnamed.042', 'unnamed.047', 'unnamed.053', 'unnamed.037', 'unnamed.046', 'unnamed.051', 'unnamed.052']:
                o.data.materials.append(mat_brake)
            else:
                o.data.materials.append(mat_alloy)
            counts['wheels'] += 1

        # 3. INTERIOR COCKPIT (Floor, seats, dash, rollcage, steering)
        elif -1.35 < cy < 0.95 and 0.30 < cz < 1.15 and abs(cx) < 0.58 and not (
            dx > 0.7 and dy > 0.4 and dz < 0.65 and cz > 0.85
        ):
            o.data.materials.append(mat_interior)
            counts['interior'] += 1

        # 4. WINDOW GLASS (Windshield, side windows, rear hatch glass)
        elif cz > 0.75 and -1.75 < cy < 1.75 and (
            abs(cx) > 0.55 or (dx > 0.7 and dy > 0.4 and dz < 0.65 and cz > 0.85) or
            o.name in [
                'unnamed.021', 'unnamed.022', 'unnamed.023', 'unnamed.027', 'unnamed.029', 'unnamed.030',
                'unnamed.058', 'unnamed.059', 'unnamed.060', 'unnamed.062', 'unnamed.064', 'unnamed.065',
                'unnamed.066', 'unnamed.068', 'unnamed.142', 'unnamed.148', 'unnamed.150', 'unnamed.152',
                'unnamed.155', 'unnamed.159', 'unnamed.161', 'unnamed.163', 'unnamed.164', 'unnamed.170',
                'unnamed.171', 'unnamed.172', 'unnamed.177', 'unnamed.178', 'unnamed.179', 'unnamed.190',
                'unnamed.196', 'unnamed.199', 'unnamed.206', 'unnamed.212', 'unnamed.216', 'unnamed.219',
                'unnamed.221', 'unnamed.222', 'unnamed.227', 'unnamed.228', 'unnamed.229', 'unnamed.234',
                'unnamed.235', 'unnamed.236', 'unnamed.238', 'unnamed.241', 'unnamed.242', 'unnamed.243',
                'unnamed.244', 'unnamed.245', 'unnamed.247', 'unnamed.248', 'unnamed.249', 'unnamed.250',
                'unnamed.251'
            ]
        ):
            # Window pillars (B-pillar between front & rear doors)
            if o.name in ['unnamed.035', 'unnamed.036', 'unnamed.237', 'unnamed.239']:
                o.data.materials.append(mat_black_trim)
                counts['trim'] += 1
            else:
                o.data.materials.append(mat_glass)
                counts['glass'] += 1

        # 5. REAR TRUNK / BUMPER PANELS
        elif cy > 1.80 and 0.50 < cz < 0.95:
            # Impact strip across rear bumper
            if o.name in ['unnamed.024', 'unnamed.032', 'unnamed.033', 'unnamed.151', 'unnamed.215']:
                o.data.materials.append(mat_moulding)
                counts['moulding'] += 1
            elif o.name in ['unnamed.149', 'unnamed.213']:
                o.data.materials.append(mat_black_trim)
                counts['trim'] += 1
            else:
                o.data.materials.append(mat_body)
                counts['body'] += 1

        # 6. BODY PANELS (CHAMPAGNE SILVER)
        else:
            o.data.materials.append(mat_body)
            counts['body'] += 1

    print(f"[Production Laguna] Assignment summary: {counts}")

    # ==========================================
    # 3. DAYLIGHT AUTOMOTIVE STUDIO LIGHTING
    # ==========================================
    # Remove existing studio lights to rebuild clean daylight lighting
    for l in [o for o in bpy.data.objects if o.name.startswith("Studio_")]:
        bpy.data.objects.remove(l, do_unlink=True)

    # A) Ground Plane: Clean paved road surface
    plane_mesh = bpy.data.meshes.new("Ground_Pavement_Mesh")
    ground = bpy.data.objects.new("Studio_Pavement", plane_mesh)
    bpy.context.collection.objects.link(ground)
    
    # Simple large plane
    verts = [
        mathutils.Vector((-20.0, -20.0, 0.0)),
        mathutils.Vector(( 20.0, -20.0, 0.0)),
        mathutils.Vector(( 20.0,  20.0, 0.0)),
        mathutils.Vector((-20.0,  20.0, 0.0))
    ]
    faces = [(0, 1, 2, 3)]
    plane_mesh.from_pydata(verts, [], faces)
    plane_mesh.update()

    mat_pave = make_material("Studio_Pavement_Mat")
    bsdf_pv = mat_pave.node_tree.nodes.get("Principled BSDF")
    if bsdf_pv:
        bsdf_pv.inputs['Base Color'].default_value = (0.38, 0.39, 0.42, 1.0) # Light asphalt road
        bsdf_pv.inputs['Roughness'].default_value = 0.85
        bsdf_pv.inputs['Specular IOR Level'].default_value = 0.2
    ground.data.materials.append(mat_pave)

    # B) Main Sun: Warm natural daylight
    sun_data = bpy.data.lights.new(name="Studio_Sun_Light", type='SUN')
    sun_data.energy = 5.5
    sun_data.color = (1.0, 0.98, 0.95)
    sun_data.angle = math.radians(2.5) # Soft realistic car shadows
    sun_obj = bpy.data.objects.new(name="Studio_Sun", object_data=sun_data)
    bpy.context.collection.objects.link(sun_obj)
    sun_obj.location = (4.0, -5.0, 7.0)
    sun_obj.rotation_euler = (math.radians(50), math.radians(15), math.radians(-35))

    # C) Sky Fill Light: Broad cool sky illumination (prevents dark shadows)
    sky_data = bpy.data.lights.new(name="Studio_Sky_Data", type='AREA')
    sky_data.energy = 2200.0
    sky_data.color = (0.90, 0.95, 1.0)
    sky_data.size = 12.0
    sky_data.size_y = 12.0
    sky_obj = bpy.data.objects.new(name="Studio_Sky_Light", object_data=sky_data)
    bpy.context.collection.objects.link(sky_obj)
    sky_obj.location = (0.0, 0.0, 7.5)
    sky_obj.rotation_euler = (0, 0, 0)

    # D) Side Fill Light: Soft bounce light on vehicle sides
    fill_data = bpy.data.lights.new(name="Studio_SideFill_Data", type='AREA')
    fill_data.energy = 800.0
    fill_data.color = (0.96, 0.96, 0.98)
    fill_data.size = 8.0
    fill_data.size_y = 3.0
    fill_obj = bpy.data.objects.new(name="Studio_SideFill", object_data=fill_data)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.location = (-5.5, 0.0, 2.5)
    fill_obj.rotation_euler = (0, math.radians(75), math.radians(-90))

    # E) Environment World
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("Studio_World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.75, 0.82, 0.92, 1.0) # Bright daylight sky
        bg.inputs['Strength'].default_value = 0.85

    # ==========================================
    # 4. RENDER VIEWS MATCHING USER IMAGES
    # ==========================================
    scene = bpy.context.scene
    cam = scene.camera
    if not cam:
        cam = bpy.data.objects.get("Camera")
    if not cam:
        cam_data = bpy.data.cameras.new("Main_Camera")
        cam_data.lens = 45.0 # Natural 45mm automotive portrait lens
        cam = bpy.data.objects.new("Main_Camera", cam_data)
        bpy.context.collection.objects.link(cam)
    scene.camera = cam
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080

    out_rear = os.path.abspath(r"c:\Users\abdelkarim\Documents\laguna-beamng\laguna_rear.png")
    out_front = os.path.abspath(r"c:\Users\abdelkarim\Documents\laguna-beamng\laguna_front.png")
    out_pres = os.path.abspath(r"c:\Users\abdelkarim\Documents\laguna-beamng\laguna_presentation.png")

    # VIEW 1: REAR 3/4 VIEW (Exact angle of user Image 1 and Image 3)
    # Camera at right-rear quarter: (X=3.8, Y=4.2, Z=1.35), targeting vehicle center (0.0, 0.4, 0.65)
    print("[Render] Rendering Rear 3/4 View (matching Image 1 & 3)...")
    cam.location = mathutils.Vector((3.9, 4.3, 1.35))
    target_rear = mathutils.Vector((0.0, 0.3, 0.65))
    cam.rotation_euler = (target_rear - cam.location).to_track_quat('-Z', 'Y').to_euler()

    scene.render.filepath = out_rear
    bpy.ops.render.render(write_still=True)
    print(f"[Render] Saved {out_rear}")

    # VIEW 2: FRONT 3/4 VIEW (Exact angle of user Image 2 - Renault Algérie ad)
    # Camera at left-front quarter: (X=-4.2, Y=-4.1, Z=1.20), targeting front fascia (0.0, -0.6, 0.55)
    print("[Render] Rendering Front 3/4 View (matching Image 2)...")
    cam.location = mathutils.Vector((-4.3, -4.2, 1.25))
    target_front = mathutils.Vector((0.0, -0.5, 0.55))
    cam.rotation_euler = (target_front - cam.location).to_track_quat('-Z', 'Y').to_euler()

    scene.render.filepath = out_front
    bpy.ops.render.render(write_still=True)
    print(f"[Render] Saved {out_front}")

    # Copy to presentation
    shutil.copy2(out_front, out_pres)

    # Also copy to artifacts directory
    art_dir = r"C:\Users\abdelkarim\.gemini\antigravity\brain\fa1588ad-d9ab-4eb3-9303-e3e476714ebd"
    shutil.copy2(out_rear, os.path.join(art_dir, "laguna_rear.png"))
    shutil.copy2(out_front, os.path.join(art_dir, "laguna_front.png"))
    shutil.copy2(out_pres, os.path.join(art_dir, "laguna_presentation.png"))
    print("[Render] All artifact images updated successfully!")

apply_production_laguna()
