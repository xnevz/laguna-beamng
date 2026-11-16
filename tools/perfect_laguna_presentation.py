"""
Perfect the Renault Laguna presentation to match the reference images:
- All body panels unified in Renault Champagne Silver / Beige Poivre metallic
- Contrast dark charcoal door rubbing strips on front and rear doors
- Rear bumper impact strip in dark charcoal
- Rear trunk inner taillights in ruby red (completing the full wrap-around taillight assembly)
- Headlights unified in crystal clear polycarbonate lenses with mirrored chrome reflector bowls
- Amber side repeaters on front door/fender mouldings
- Lower front bumper race splitter hidden for clean factory road car appearance
- Solarglass with natural pale green tint, sharp reflections, and visible interior
- Factory Renault silver alloy wheels with black road rubber tires and chrome center caps
- Polished chrome Renault diamond emblems front and rear, and chrome Laguna lettering
- High-contrast road pavement ground with daylight studio automotive lighting
"""

import bpy
import mathutils
import math
import os
import shutil

def perfect_laguna():
    print("[Laguna Master] Applying perfect production materials...")

    def make_material(name):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        return mat

    # ==========================================
    # 1. PBR SHADERS
    # ==========================================

    # A) Renault Champagne Silver (Beige Poivre / Gris Angora Metallic)
    # Warm metallic platinum-silver with high-gloss automotive clearcoat
    mat_body = make_material("Laguna_Champagne_Silver")
    bsdf_b = mat_body.node_tree.nodes.get("Principled BSDF")
    if bsdf_b:
        bsdf_b.inputs['Base Color'].default_value = (0.76, 0.72, 0.62, 1.0) # Rich champagne metallic
        bsdf_b.inputs['Metallic'].default_value = 0.82
        bsdf_b.inputs['Roughness'].default_value = 0.20
        bsdf_b.inputs['Coat Weight'].default_value = 1.0 # High gloss clearcoat
        bsdf_b.inputs['Coat Roughness'].default_value = 0.02
        bsdf_b.inputs['Coat IOR'].default_value = 1.50
        bsdf_b.inputs['Specular IOR Level'].default_value = 0.55

    # B) Factory Renault Solarglass (Pale green heat-absorbing automotive safety glass)
    mat_glass = make_material("Laguna_Factory_Solarglass")
    bsdf_g = mat_glass.node_tree.nodes.get("Principled BSDF")
    if bsdf_g:
        bsdf_g.inputs['Base Color'].default_value = (0.82, 0.94, 0.88, 1.0) # Light green-cyan tint
        bsdf_g.inputs['Metallic'].default_value = 0.0
        bsdf_g.inputs['Roughness'].default_value = 0.015
        bsdf_g.inputs['Alpha'].default_value = 0.42 # High transparency to show cockpit
        bsdf_g.inputs['IOR'].default_value = 1.52
        bsdf_g.inputs['Coat Weight'].default_value = 1.0
        bsdf_g.inputs['Coat Roughness'].default_value = 0.01
    mat_glass.blend_method = 'BLEND'

    # C) Protective Side Mouldings & Bumper Strips (Dark Textured Charcoal Plastic)
    mat_moulding = make_material("Laguna_Trim_Charcoal")
    bsdf_m = mat_moulding.node_tree.nodes.get("Principled BSDF")
    if bsdf_m:
        bsdf_m.inputs['Base Color'].default_value = (0.07, 0.07, 0.075, 1.0) # Contrast dark charcoal
        bsdf_m.inputs['Metallic'].default_value = 0.0
        bsdf_m.inputs['Roughness'].default_value = 0.75

    # D) B-Pillars, Window Rubber & Wipers (Satin Black)
    mat_black = make_material("Laguna_Pillar_Black")
    bsdf_bk = mat_black.node_tree.nodes.get("Principled BSDF")
    if bsdf_bk:
        bsdf_bk.inputs['Base Color'].default_value = (0.03, 0.03, 0.035, 1.0)
        bsdf_bk.inputs['Metallic'].default_value = 0.0
        bsdf_bk.inputs['Roughness'].default_value = 0.60

    # E) Amber Side Repeater Indicators
    mat_amber = make_material("Laguna_Amber_Indicator")
    bsdf_amb = mat_amber.node_tree.nodes.get("Principled BSDF")
    if bsdf_amb:
        bsdf_amb.inputs['Base Color'].default_value = (0.98, 0.45, 0.02, 1.0)
        bsdf_amb.inputs['Metallic'].default_value = 0.05
        bsdf_amb.inputs['Roughness'].default_value = 0.03
        bsdf_amb.inputs['Alpha'].default_value = 0.80
        bsdf_amb.inputs['IOR'].default_value = 1.50
    mat_amber.blend_method = 'BLEND'

    # F) Front Headlight Crystal Clear Outer Polycarbonate Lens
    mat_hl_lens = make_material("Laguna_Headlight_Glass")
    bsdf_hl = mat_hl_lens.node_tree.nodes.get("Principled BSDF")
    if bsdf_hl:
        bsdf_hl.inputs['Base Color'].default_value = (0.97, 0.98, 1.0, 1.0)
        bsdf_hl.inputs['Metallic'].default_value = 0.0
        bsdf_hl.inputs['Roughness'].default_value = 0.01
        bsdf_hl.inputs['Alpha'].default_value = 0.15 # Crystal clear
        bsdf_hl.inputs['IOR'].default_value = 1.50
        bsdf_hl.inputs['Coat Weight'].default_value = 1.0
        bsdf_hl.inputs['Coat Roughness'].default_value = 0.01
    mat_hl_lens.blend_method = 'BLEND'

    # G) Headlight Reflector Bowls, Renault Diamond & Badges (Mirrored Chrome)
    mat_chrome = make_material("Laguna_Chrome")
    bsdf_ch = mat_chrome.node_tree.nodes.get("Principled BSDF")
    if bsdf_ch:
        bsdf_ch.inputs['Base Color'].default_value = (0.98, 0.98, 1.0, 1.0)
        bsdf_ch.inputs['Metallic'].default_value = 1.0
        bsdf_ch.inputs['Roughness'].default_value = 0.02

    # H) Taillights: Deep Ruby Red Lens
    mat_tl_ruby = make_material("Laguna_Taillight_Ruby")
    bsdf_tr = mat_tl_ruby.node_tree.nodes.get("Principled BSDF")
    if bsdf_tr:
        bsdf_tr.inputs['Base Color'].default_value = (0.78, 0.01, 0.02, 1.0)
        bsdf_tr.inputs['Metallic'].default_value = 0.05
        bsdf_tr.inputs['Roughness'].default_value = 0.03
        bsdf_tr.inputs['Alpha'].default_value = 0.88
        bsdf_tr.inputs['IOR'].default_value = 1.52
        bsdf_tr.inputs['Coat Weight'].default_value = 1.0
        bsdf_tr.inputs['Coat Roughness'].default_value = 0.02
    mat_tl_ruby.blend_method = 'BLEND'

    # I) Taillights: Clear Reverse Lamp Strip
    mat_tl_clear = make_material("Laguna_Taillight_Clear")
    bsdf_tw = mat_tl_clear.node_tree.nodes.get("Principled BSDF")
    if bsdf_tw:
        bsdf_tw.inputs['Base Color'].default_value = (0.96, 0.96, 0.98, 1.0)
        bsdf_tw.inputs['Metallic'].default_value = 0.05
        bsdf_tw.inputs['Roughness'].default_value = 0.03
        bsdf_tw.inputs['Alpha'].default_value = 0.45
        bsdf_tw.inputs['IOR'].default_value = 1.50
    mat_tl_clear.blend_method = 'BLEND'

    # J) Wheels: Renault Factory Silver Alloy
    mat_alloy = make_material("Laguna_Factory_Alloy")
    bsdf_al = mat_alloy.node_tree.nodes.get("Principled BSDF")
    if bsdf_al:
        bsdf_al.inputs['Base Color'].default_value = (0.86, 0.88, 0.90, 1.0)
        bsdf_al.inputs['Metallic'].default_value = 0.78
        bsdf_al.inputs['Roughness'].default_value = 0.18
        bsdf_al.inputs['Coat Weight'].default_value = 0.8
        bsdf_al.inputs['Coat Roughness'].default_value = 0.03

    # K) Wheels: Road Rubber Tires
    mat_tire = make_material("Laguna_Road_Tire")
    bsdf_ti = mat_tire.node_tree.nodes.get("Principled BSDF")
    if bsdf_ti:
        bsdf_ti.inputs['Base Color'].default_value = (0.025, 0.025, 0.028, 1.0)
        bsdf_ti.inputs['Metallic'].default_value = 0.0
        bsdf_ti.inputs['Roughness'].default_value = 0.82

    # L) Brake Discs & Calipers
    mat_brake = make_material("Laguna_Brake_Steel")
    bsdf_br = mat_brake.node_tree.nodes.get("Principled BSDF")
    if bsdf_br:
        bsdf_br.inputs['Base Color'].default_value = (0.35, 0.35, 0.38, 1.0)
        bsdf_br.inputs['Metallic'].default_value = 0.80
        bsdf_br.inputs['Roughness'].default_value = 0.35

    # M) Interior Cockpit (Dark Slate Charcoal Dashboard, Seats & Trim)
    mat_interior = make_material("Laguna_Interior_Charcoal")
    bsdf_in = mat_interior.node_tree.nodes.get("Principled BSDF")
    if bsdf_in:
        bsdf_in.inputs['Base Color'].default_value = (0.04, 0.04, 0.045, 1.0)
        bsdf_in.inputs['Metallic'].default_value = 0.0
        bsdf_in.inputs['Roughness'].default_value = 0.85

    # ==========================================
    # 2. OBJECT ASSIGNMENT MAP
    # ==========================================

    # A) Body panels that MUST be Champagne Silver:
    body_panel_names = {
        'unnamed.005', 'unnamed.006', 'unnamed.007', 'unnamed.008',
        'unnamed.011', 'unnamed.025', 'unnamed.026', 'unnamed.028',
        'unnamed.057', 'unnamed.063', 'unnamed.083', 'unnamed.137',
        'unnamed.139', 'unnamed.140', 'unnamed.143', 'unnamed.145',
        'unnamed.146', 'unnamed.150', 'unnamed.166', 'unnamed.167',
        'unnamed.173', 'unnamed.174', 'unnamed.223', 'unnamed.224',
        'unnamed.230', 'unnamed.231', 'unnamed.240', 'unnamed.246'
    }

    # B) Door rubbing strips (side protective mouldings) & rear bumper impact strip:
    moulding_names = {
        'unnamed.141', 'unnamed.147', 'unnamed.205', 'unnamed.211', # Door rub strips
        'unnamed.024', 'unnamed.151', 'unnamed.215'                 # Rear bumper impact strip & plate recess
    }

    # C) Amber indicators (door side repeater):
    amber_names = {'unnamed.061', 'unnamed.067'}

    # D) Chrome accents (Renault diamonds, badges, door handle pulls):
    chrome_names = {
        'unnamed.014', 'unnamed.154', 'unnamed.218',
        'unnamed.168', 'unnamed.175', 'unnamed.225', 'unnamed.232'
    }

    # E) Headlights (outer crystal clear lens + corner lens):
    headlight_lens_names = {'unnamed.017', 'unnamed.019', 'unnamed.070', 'unnamed.071'}
    headlight_reflector_names = {'unnamed.012'}

    # F) Taillights (ruby red lenses including trunk lid inner sections):
    taillight_ruby_names = {
        'unnamed.010', 'unnamed.015', 'unnamed.016',
        'unnamed.031', 'unnamed.220', # 3rd brake light on decklid
        'unnamed.032', 'unnamed.033'  # Inner taillight lenses on tailgate!
    }
    taillight_clear_names = {'unnamed.018', 'unnamed.020'} # Reverse light strip

    # G) Window Glass (Green-tinted solarglass):
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

    # H) Black trim (B-pillars, window surrounds, wiper blade, lower air intake):
    black_trim_names = {
        'unnamed.013', 'unnamed.069', 'unnamed.034', 'unnamed.035',
        'unnamed.036', 'unnamed.149', 'unnamed.213', 'unnamed.237',
        'unnamed.239', 'unnamed.169', 'unnamed.176', 'unnamed.226', 'unnamed.233'
    }

    # I) Brake steel:
    brake_names = {
        'unnamed.038', 'unnamed.042', 'unnamed.047', 'unnamed.053',
        'unnamed.037', 'unnamed.046', 'unnamed.051', 'unnamed.052'
    }

    # Hide race track parts that don't belong on a production car
    for race_obj_name in ['unnamed.009', 'Laguna_Race_Wing']:
        ro = bpy.data.objects.get(race_obj_name)
        if ro:
            ro.hide_render = True
            ro.hide_viewport = True

    # Scan and apply
    objs = [o for o in bpy.data.objects if o.type == 'MESH' and not o.name.startswith("Studio_") and not o.name.startswith("Ref_") and not o.name.endswith("_Bounds")]
    for o in objs:
        o.hide_render = False
        o.hide_viewport = False
        o.data.materials.clear()

        # Priority 1: Known sets
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
            o.data.materials.append(mat_chrome)
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

        # Priority 2: Coordinate heuristics for wheels vs interior vs body
        else:
            verts = [o.matrix_world @ v.co for v in o.data.vertices]
            if not verts: continue
            cx = sum(v.x for v in verts) / len(verts)
            cy = sum(v.y for v in verts) / len(verts)
            cz = sum(v.z for v in verts) / len(verts)
            dx = max(v.x for v in verts) - min(v.x for v in verts)
            dy = max(v.y for v in verts) - min(v.y for v in verts)
            dz = max(v.z for v in verts) - min(v.z for v in verts)

            # Wheels
            if cz < 0.45 and abs(cx) > 0.60:
                if max(dy, dz) > 0.45 and dx > 0.15:
                    o.data.materials.append(mat_tire)
                else:
                    o.data.materials.append(mat_alloy)
            # Interior (Floor, dashboard, seats, roll cage)
            elif -1.35 < cy < 0.95 and 0.28 < cz < 1.15 and abs(cx) < 0.58:
                o.data.materials.append(mat_interior)
            else:
                o.data.materials.append(mat_body)

    # Re-hide the race wing and race splitter
    for ro_name in ['unnamed.009', 'Laguna_Race_Wing']:
        ro = bpy.data.objects.get(ro_name)
        if ro:
            ro.hide_render = True

    # ==========================================
    # 3. HIGH-CONTRAST DAYLIGHT LIGHTING
    # ==========================================
    for l in [o for o in bpy.data.objects if o.name.startswith("Studio_")]:
        bpy.data.objects.remove(l, do_unlink=True)

    # A) Dark road asphalt ground plane for high contrast against champagne paint
    plane_mesh = bpy.data.meshes.new("Ground_Pavement_Mesh")
    ground = bpy.data.objects.new("Studio_Pavement", plane_mesh)
    bpy.context.collection.objects.link(ground)
    verts = [
        mathutils.Vector((-25.0, -25.0, 0.0)),
        mathutils.Vector(( 25.0, -25.0, 0.0)),
        mathutils.Vector(( 25.0,  25.0, 0.0)),
        mathutils.Vector((-25.0,  25.0, 0.0))
    ]
    faces = [(0, 1, 2, 3)]
    plane_mesh.from_pydata(verts, [], faces)
    plane_mesh.update()

    mat_pave = make_material("Studio_Pavement_Mat")
    bsdf_pv = mat_pave.node_tree.nodes.get("Principled BSDF")
    if bsdf_pv:
        bsdf_pv.inputs['Base Color'].default_value = (0.24, 0.25, 0.27, 1.0) # Dark rich asphalt
        bsdf_pv.inputs['Roughness'].default_value = 0.82
        bsdf_pv.inputs['Specular IOR Level'].default_value = 0.3
    ground.data.materials.append(mat_pave)

    # B) Main Sun: Warm natural sun from 45° camera angle
    sun_data = bpy.data.lights.new(name="Studio_Sun_Light", type='SUN')
    sun_data.energy = 6.2
    sun_data.color = (1.0, 0.97, 0.93)
    sun_data.angle = math.radians(2.0)
    sun_obj = bpy.data.objects.new(name="Studio_Sun", object_data=sun_data)
    bpy.context.collection.objects.link(sun_obj)
    sun_obj.location = (5.0, -5.0, 7.5)
    sun_obj.rotation_euler = (math.radians(45), math.radians(18), math.radians(-30))

    # C) Sky Dome Fill Light: Soft natural ambient sky
    sky_data = bpy.data.lights.new(name="Studio_Sky_Data", type='AREA')
    sky_data.energy = 2400.0
    sky_data.color = (0.92, 0.96, 1.0)
    sky_data.size = 14.0
    sky_data.size_y = 14.0
    sky_obj = bpy.data.objects.new(name="Studio_Sky_Light", object_data=sky_data)
    bpy.context.collection.objects.link(sky_obj)
    sky_obj.location = (0.0, 0.0, 8.0)
    sky_obj.rotation_euler = (0, 0, 0)

    # D) Side / Horizon Fill: Clear visibility on shaded door flanks
    fill_data = bpy.data.lights.new(name="Studio_SideFill_Data", type='AREA')
    fill_data.energy = 1000.0
    fill_data.color = (0.96, 0.97, 0.98)
    fill_data.size = 10.0
    fill_data.size_y = 4.0
    fill_obj = bpy.data.objects.new(name="Studio_SideFill", object_data=fill_data)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.location = (-6.0, 0.5, 2.5)
    fill_obj.rotation_euler = (0, math.radians(75), math.radians(-90))

    # E) Environment World
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("Studio_World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.78, 0.84, 0.92, 1.0) # Bright daylight sky
        bg.inputs['Strength'].default_value = 0.90

    # ==========================================
    # 4. RENDER REAR & FRONT PRESENTATION
    # ==========================================
    scene = bpy.context.scene
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

    out_rear = os.path.abspath(r"c:\Users\abdelkarim\Documents\laguna-beamng\laguna_rear.png")
    out_front = os.path.abspath(r"c:\Users\abdelkarim\Documents\laguna-beamng\laguna_front.png")
    out_pres = os.path.abspath(r"c:\Users\abdelkarim\Documents\laguna-beamng\laguna_presentation.png")

    # VIEW 1: REAR 3/4 (User Image 1 & 3 angle)
    # Camera at right-rear quarter: (X=3.8, Y=4.2, Z=1.35)
    print("[Render] Rendering Rear 3/4...")
    cam.location = mathutils.Vector((3.85, 4.25, 1.35))
    target_rear = mathutils.Vector((0.0, 0.3, 0.65))
    cam.rotation_euler = (target_rear - cam.location).to_track_quat('-Z', 'Y').to_euler()

    scene.render.filepath = out_rear
    bpy.ops.render.render(write_still=True)
    print(f"[Render] Saved {out_rear}")

    # VIEW 2: FRONT 3/4 (User Image 2 - Renault Algérie angle)
    # Camera at left-front quarter: (X=-4.2, Y=-4.1, Z=1.20)
    print("[Render] Rendering Front 3/4...")
    cam.location = mathutils.Vector((-4.3, -4.2, 1.25))
    target_front = mathutils.Vector((0.0, -0.5, 0.55))
    cam.rotation_euler = (target_front - cam.location).to_track_quat('-Z', 'Y').to_euler()

    scene.render.filepath = out_front
    bpy.ops.render.render(write_still=True)
    print(f"[Render] Saved {out_front}")

    # Update presentation image and artifacts
    shutil.copy2(out_front, out_pres)
    art_dir = r"C:\Users\abdelkarim\.gemini\antigravity\brain\fa1588ad-d9ab-4eb3-9303-e3e476714ebd"
    shutil.copy2(out_rear, os.path.join(art_dir, "laguna_rear.png"))
    shutil.copy2(out_front, os.path.join(art_dir, "laguna_front.png"))
    shutil.copy2(out_pres, os.path.join(art_dir, "laguna_presentation.png"))
    print("[Render] All artifact images updated successfully!")

perfect_laguna()
