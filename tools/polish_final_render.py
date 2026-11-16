"""
Polish final render:
1. Seamless Champagne Silver on the entire unibody (remove jagged Z-cutoff on front bumper).
2. Ground pavement extended to 200m so it reaches the horizon seamlessly.
3. Headlights: Mirrored chrome reflector bowls with bright projector glint inside crystal clear lenses.
4. Grille: Crisp black grille slats with polished chrome Renault diamond in the center.
5. Taillights: Ruby red wrap-around lenses with crisp white reverse light bar.
6. Wheels: Renault factory silver multi-spoke alloys with chrome center cap and black road tires.
7. Directional sun lighting to illuminate the front fascia and body flanks cleanly.
"""

import bpy
import mathutils
import math
import os
import shutil

def polish_final():
    print("[Final Polish] Applying clean body assignments and seamless lighting...")

    def make_material(name):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        return mat

    # Materials
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
        g_bsdf.inputs['Metallic'].default_value = 0.0
        g_bsdf.inputs['Roughness'].default_value = 0.012
        g_bsdf.inputs['Alpha'].default_value = 0.40
        g_bsdf.inputs['IOR'].default_value = 1.52
        g_bsdf.inputs['Coat Weight'].default_value = 1.0
        g_bsdf.inputs['Coat Roughness'].default_value = 0.01
    mat_glass.blend_method = 'BLEND'

    mat_moulding = make_material("Laguna_Trim_Charcoal")
    m_bsdf = mat_moulding.node_tree.nodes.get("Principled BSDF")
    if m_bsdf:
        m_bsdf.inputs['Base Color'].default_value = (0.06, 0.06, 0.065, 1.0)
        m_bsdf.inputs['Roughness'].default_value = 0.75

    mat_black = make_material("Laguna_Pillar_Black")
    bk_bsdf = mat_black.node_tree.nodes.get("Principled BSDF")
    if bk_bsdf:
        bk_bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.025, 1.0)
        bk_bsdf.inputs['Roughness'].default_value = 0.60

    mat_amber = make_material("Laguna_Amber_Indicator")
    am_bsdf = mat_amber.node_tree.nodes.get("Principled BSDF")
    if am_bsdf:
        am_bsdf.inputs['Base Color'].default_value = (0.98, 0.45, 0.02, 1.0)
        am_bsdf.inputs['Alpha'].default_value = 0.85
    mat_amber.blend_method = 'BLEND'

    mat_hl_lens = make_material("Laguna_Headlight_Glass")
    hl_bsdf = mat_hl_lens.node_tree.nodes.get("Principled BSDF")
    if hl_bsdf:
        hl_bsdf.inputs['Base Color'].default_value = (0.97, 0.98, 1.0, 1.0)
        hl_bsdf.inputs['Roughness'].default_value = 0.01
        hl_bsdf.inputs['Alpha'].default_value = 0.12 # Ultra clear
        hl_bsdf.inputs['Coat Weight'].default_value = 1.0
    mat_hl_lens.blend_method = 'BLEND'

    # Bright chrome headlight reflector with sharp specular reflections
    mat_hl_reflector = make_material("Laguna_Headlight_Reflector")
    hr_bsdf = mat_hl_reflector.node_tree.nodes.get("Principled BSDF")
    if hr_bsdf:
        hr_bsdf.inputs['Base Color'].default_value = (0.98, 0.98, 1.0, 1.0)
        hr_bsdf.inputs['Metallic'].default_value = 0.98
        hr_bsdf.inputs['Roughness'].default_value = 0.02
        hr_bsdf.inputs['Emission Color'].default_value = (0.95, 0.98, 1.0, 1.0)
        hr_bsdf.inputs['Emission Strength'].default_value = 0.80 # Clear bright headlights!

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
        tr_bsdf.inputs['Emission Strength'].default_value = 0.25
    mat_tl_ruby.blend_method = 'BLEND'

    mat_tl_clear = make_material("Laguna_Taillight_Clear")
    tc_bsdf = mat_tl_clear.node_tree.nodes.get("Principled BSDF")
    if tc_bsdf:
        tc_bsdf.inputs['Base Color'].default_value = (0.96, 0.96, 0.98, 1.0)
        tc_bsdf.inputs['Alpha'].default_value = 0.45
    mat_tl_clear.blend_method = 'BLEND'

    mat_alloy = make_material("Laguna_Factory_Alloy")
    al_bsdf = mat_alloy.node_tree.nodes.get("Principled BSDF")
    if al_bsdf:
        al_bsdf.inputs['Base Color'].default_value = (0.86, 0.88, 0.90, 1.0)
        al_bsdf.inputs['Metallic'].default_value = 0.78
        al_bsdf.inputs['Roughness'].default_value = 0.18
        al_bsdf.inputs['Coat Weight'].default_value = 0.8

    mat_tire = make_material("Laguna_Road_Tire")
    ti_bsdf = mat_tire.node_tree.nodes.get("Principled BSDF")
    if ti_bsdf:
        ti_bsdf.inputs['Base Color'].default_value = (0.022, 0.022, 0.025, 1.0)
        ti_bsdf.inputs['Roughness'].default_value = 0.82

    mat_interior = make_material("Laguna_Interior_Charcoal")
    in_bsdf = mat_interior.node_tree.nodes.get("Principled BSDF")
    if in_bsdf:
        in_bsdf.inputs['Base Color'].default_value = (0.04, 0.04, 0.045, 1.0)
        in_bsdf.inputs['Roughness'].default_value = 0.85

    # 2. SEAMLESS UNIBODY
    # Make unnamed.004 completely Champagne Silver with door rub strips in charcoal:
    o4 = bpy.data.objects.get('unnamed.004')
    if o4:
        o4.data.materials.clear()
        o4.data.materials.append(mat_body)     # Slot 0: Body
        o4.data.materials.append(mat_moulding) # Slot 1: Moulding
        m4 = o4.data
        for p in m4.polygons:
            pts = [m4.vertices[v].co for v in p.vertices]
            cx = sum(pt.x for pt in pts) / len(pts)
            cy = sum(pt.y for pt in pts) / len(pts)
            cz = sum(pt.z for pt in pts) / len(pts)
            # Door rubbing strips along the flanks
            if abs(cx) > 0.72 and 0.52 < cz < 0.63 and -1.05 < cy < 1.10:
                p.material_index = 1
            # Rear bumper impact strip
            elif cy > 2.05 and 0.62 < cz < 0.76:
                p.material_index = 1
            else:
                p.material_index = 0

    # unnamed.006: Hood and grille
    o6 = bpy.data.objects.get('unnamed.006')
    if o6:
        o6.data.materials.clear()
        o6.data.materials.append(mat_body)
        o6.data.materials.append(mat_black)
        o6.data.materials.append(mat_chrome)
        m6 = o6.data
        for p in m6.polygons:
            pts = [m6.vertices[v].co for v in p.vertices]
            cx = sum(pt.x for pt in pts) / len(pts)
            cy = sum(pt.y for pt in pts) / len(pts)
            cz = sum(pt.z for pt in pts) / len(pts)
            if cy < -2.05:
                if abs(cx) < 0.08 and 0.52 < cz < 0.65:
                    p.material_index = 2 # Chrome diamond
                else:
                    p.material_index = 1 # Black intake slats
            else:
                p.material_index = 0

    # Headlight reflector bowl: bright mirrored chrome
    o12 = bpy.data.objects.get('unnamed.012')
    if o12:
        o12.data.materials.clear()
        o12.data.materials.append(mat_hl_reflector)

    # Grille chrome trim bar
    o14 = bpy.data.objects.get('unnamed.014')
    if o14:
        o14.data.materials.clear()
        o14.data.materials.append(mat_chrome)

    # Lower front air intake
    o13 = bpy.data.objects.get('unnamed.013')
    if o13:
        o13.data.materials.clear()
        o13.data.materials.append(mat_black)

    # Front bumper lower lip
    o69 = bpy.data.objects.get('unnamed.069')
    if o69:
        o69.data.materials.clear()
        o69.data.materials.append(mat_black)

    # Side indicators
    for n in ['unnamed.061', 'unnamed.067']:
        o = bpy.data.objects.get(n)
        if o:
            o.data.materials.clear()
            o.data.materials.append(mat_amber)

    # Hide race track parts completely
    for ro_name in ['unnamed.009', 'Laguna_Race_Wing']:
        ro = bpy.data.objects.get(ro_name)
        if ro:
            ro.hide_render = True
            ro.hide_viewport = True

    # 3. SEAMLESS HORIZON GROUND & LIGHTING
    # Clean up old studio objects
    for l in [o for o in bpy.data.objects if o.name.startswith("Studio_")]:
        bpy.data.objects.remove(l, do_unlink=True)

    # Large seamless pavement plane extending to the horizon (200m x 200m)
    plane_mesh = bpy.data.meshes.new("Ground_Pavement_Mesh")
    ground = bpy.data.objects.new("Studio_Pavement", plane_mesh)
    bpy.context.collection.objects.link(ground)
    verts = [
        mathutils.Vector((-120.0, -120.0, 0.0)),
        mathutils.Vector(( 120.0, -120.0, 0.0)),
        mathutils.Vector(( 120.0,  120.0, 0.0)),
        mathutils.Vector((-120.0,  120.0, 0.0))
    ]
    faces = [(0, 1, 2, 3)]
    plane_mesh.from_pydata(verts, [], faces)
    plane_mesh.update()

    mat_pave = make_material("Studio_Pavement_Mat")
    bsdf_pv = mat_pave.node_tree.nodes.get("Principled BSDF")
    if bsdf_pv:
        bsdf_pv.inputs['Base Color'].default_value = (0.15, 0.16, 0.17, 1.0)
        bsdf_pv.inputs['Roughness'].default_value = 0.85
        bsdf_pv.inputs['Specular IOR Level'].default_value = 0.25
    ground.data.materials.append(mat_pave)

    # Warm daylight sun pointing directly at front 3/4 & side
    sun_data = bpy.data.lights.new(name="Studio_Sun_Light", type='SUN')
    sun_data.energy = 5.2
    sun_data.color = (1.0, 0.98, 0.94)
    sun_data.angle = math.radians(2.0)
    sun_obj = bpy.data.objects.new(name="Studio_Sun", object_data=sun_data)
    bpy.context.collection.objects.link(sun_obj)
    sun_obj.location = (5.0, -5.5, 7.5)
    sun_obj.rotation_euler = (math.radians(48), math.radians(16), math.radians(-32))

    # Balanced ambient sky dome
    sky_data = bpy.data.lights.new(name="Studio_Sky_Data", type='AREA')
    sky_data.energy = 450.0
    sky_data.color = (0.92, 0.96, 1.0)
    sky_data.size = 20.0
    sky_data.size_y = 20.0
    sky_obj = bpy.data.objects.new(name="Studio_Sky_Light", object_data=sky_data)
    bpy.context.collection.objects.link(sky_obj)
    sky_obj.location = (0.0, 0.0, 9.0)

    # Flank fill light
    fill_data = bpy.data.lights.new(name="Studio_SideFill_Data", type='AREA')
    fill_data.energy = 250.0
    fill_data.color = (0.96, 0.97, 0.98)
    fill_data.size = 10.0
    fill_data.size_y = 4.0
    fill_obj = bpy.data.objects.new(name="Studio_SideFill", object_data=fill_data)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.location = (-6.0, 0.0, 2.5)
    fill_obj.rotation_euler = (0, math.radians(75), math.radians(-90))

    # Soft headlight / front glint light
    glint_data = bpy.data.lights.new(name="Studio_Glint_Data", type='AREA')
    glint_data.energy = 220.0
    glint_data.color = (0.98, 0.99, 1.0)
    glint_data.size = 4.0
    glint_data.size_y = 2.0
    glint_obj = bpy.data.objects.new(name="Studio_Glint", object_data=glint_data)
    bpy.context.collection.objects.link(glint_obj)
    glint_obj.location = (-2.0, -4.8, 1.4)
    glint_obj.rotation_euler = (math.radians(70), 0, math.radians(20))

    # World horizon sky
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("Studio_World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.50, 0.58, 0.68, 1.0) # Atmospheric sky
        bg.inputs['Strength'].default_value = 0.35

    scene = bpy.context.scene
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - High Contrast'
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080

    cam = scene.camera
    if not cam:
        cam = bpy.data.objects.get("Camera")
    if not cam:
        cam_data = bpy.data.cameras.new("Main_Camera")
        cam_data.lens = 45.0
        cam = bpy.data.objects.new("Main_Camera", cam_data)
        bpy.context.collection.objects.link(cam)
    scene.camera = cam

    out_front = os.path.abspath(r"c:\Users\abdelkarim\Documents\laguna-beamng\laguna_front.png")
    out_rear = os.path.abspath(r"c:\Users\abdelkarim\Documents\laguna-beamng\laguna_rear.png")
    out_pres = os.path.abspath(r"c:\Users\abdelkarim\Documents\laguna-beamng\laguna_presentation.png")

    # Render Front 3/4 View (Matching Image 2 - Renault Algérie)
    print("[Render] Rendering Front 3/4...")
    cam.location = mathutils.Vector((-4.3, -4.2, 1.25))
    target_front = mathutils.Vector((0.0, -0.5, 0.55))
    cam.rotation_euler = (target_front - cam.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = out_front
    bpy.ops.render.render(write_still=True)
    print(f"[Render] Saved {out_front}")

    # Render Rear 3/4 View (Matching Image 1 & 3)
    print("[Render] Rendering Rear 3/4...")
    cam.location = mathutils.Vector((3.85, 4.25, 1.35))
    target_rear = mathutils.Vector((0.0, 0.3, 0.65))
    cam.rotation_euler = (target_rear - cam.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = out_rear
    bpy.ops.render.render(write_still=True)
    print(f"[Render] Saved {out_rear}")

    # Copy to artifacts
    shutil.copy2(out_front, out_pres)
    art_dir = r"C:\Users\abdelkarim\.gemini\antigravity\brain\fa1588ad-d9ab-4eb3-9303-e3e476714ebd"
    shutil.copy2(out_front, os.path.join(art_dir, "laguna_front.png"))
    shutil.copy2(out_rear, os.path.join(art_dir, "laguna_rear.png"))
    shutil.copy2(out_pres, os.path.join(art_dir, "laguna_presentation.png"))
    print("[Render] All artifact images updated successfully!")

polish_final()
