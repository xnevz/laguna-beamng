"""
Autonomous Visual Loop - Renault Laguna II Phase 1 Authentic Realism
Refines materials, eliminates track distortions, sets raytracing + Nishita sky,
and renders front and rear views.
"""

import bpy
import bmesh
import mathutils
import math
import os
import shutil

def run_visual_overhaul():
    print("==================================================")
    print("[Autonomous Loop] Starting Full Visual Overhaul...")
    print("==================================================")

    scene = bpy.context.scene

    # ----------------------------------------------------
    # 1. ENGINE & RAYTRACING SETTINGS (EEVEE-Next in 5.3)
    # ----------------------------------------------------
    scene.render.engine = 'BLENDER_EEVEE'
    eevee = scene.eevee
    eevee.use_raytracing = True
    if hasattr(eevee, 'ray_tracing_options'):
        eevee.ray_tracing_options.screen_trace_quality = 1.0
        eevee.ray_tracing_options.trace_max_roughness = 1.0
        eevee.ray_tracing_options.use_denoise = True
    eevee.use_fast_gi = True
    if hasattr(eevee, 'fast_gi_quality'):
        eevee.fast_gi_quality = 1.0
    eevee.taa_render_samples = 128
    eevee.use_shadows = True

    # Color management: AgX High Contrast
    scene.view_settings.view_transform = 'AgX'
    try:
        scene.view_settings.look = 'AgX - High Contrast'
    except Exception:
        scene.view_settings.look = 'None'

    # ----------------------------------------------------
    # 2. OUTDOOR WORLD LIGHTING (Nishita Sky Texture)
    # ----------------------------------------------------
    world = scene.world
    if not world:
        world = bpy.data.worlds.new("Laguna_Sky_World")
        scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()

    node_out = nt.nodes.new("ShaderNodeOutputWorld")
    node_bg = nt.nodes.new("ShaderNodeBackground")
    node_sky = nt.nodes.new("ShaderNodeTexSky")
    node_sky.sky_type = 'MULTIPLE_SCATTERING'
    node_sky.sun_elevation = math.radians(38.0)
    node_sky.sun_rotation = math.radians(-35.0)
    node_sky.altitude = 60.0
    node_sky.air_density = 1.0
    if hasattr(node_sky, 'aerosol_density'):
        node_sky.aerosol_density = 0.8
    elif hasattr(node_sky, 'dust_density'):
        node_sky.dust_density = 0.8
    node_sky.ozone_density = 2.0
    node_sky.sun_disc = True

    node_bg.inputs['Strength'].default_value = 1.15
    nt.links.new(node_sky.outputs['Color'], node_bg.inputs['Color'])
    nt.links.new(node_bg.outputs['Background'], node_out.inputs['Surface'])

    # ----------------------------------------------------
    # 3. ASPHALT ROADWAY PAVEMENT
    # ----------------------------------------------------
    pavement = bpy.data.objects.get("Studio_Pavement")
    if not pavement:
        bpy.ops.mesh.primitive_plane_add(size=300.0, location=(0, 0, 0))
        pavement = bpy.context.active_object
        pavement.name = "Studio_Pavement"

    mat_road = bpy.data.materials.get("Laguna_Road_Asphalt")
    if not mat_road:
        mat_road = bpy.data.materials.new("Laguna_Road_Asphalt")
        mat_road.use_nodes = True
    r_bsdf = mat_road.node_tree.nodes.get("Principled BSDF")
    if r_bsdf:
        r_bsdf.inputs['Base Color'].default_value = (0.12, 0.12, 0.13, 1.0)
        r_bsdf.inputs['Roughness'].default_value = 0.88
        r_bsdf.inputs['Specular IOR Level'].default_value = 0.35
    pavement.data.materials.clear()
    pavement.data.materials.append(mat_road)
    pavement.location.z = -0.005 # flush with ground

    # ----------------------------------------------------
    # 4. MATERIALS SETUP
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
        b_bsdf.inputs['Base Color'].default_value = (0.76, 0.73, 0.64, 1.0)
        b_bsdf.inputs['Metallic'].default_value = 0.85
        b_bsdf.inputs['Roughness'].default_value = 0.16
        b_bsdf.inputs['Coat Weight'].default_value = 1.0
        b_bsdf.inputs['Coat Roughness'].default_value = 0.02
        b_bsdf.inputs['Coat IOR'].default_value = 1.50
        b_bsdf.inputs['Specular IOR Level'].default_value = 0.60

    # Solarglass: Pale green heat-rejecting factory glass
    mat_glass = get_or_create_mat("Laguna_Factory_Solarglass")
    g_bsdf = mat_glass.node_tree.nodes.get("Principled BSDF")
    if g_bsdf:
        g_bsdf.inputs['Base Color'].default_value = (0.82, 0.94, 0.88, 1.0)
        g_bsdf.inputs['Roughness'].default_value = 0.008
        g_bsdf.inputs['Alpha'].default_value = 0.32
        g_bsdf.inputs['IOR'].default_value = 1.52
        g_bsdf.inputs['Coat Weight'].default_value = 1.0
        g_bsdf.inputs['Coat Roughness'].default_value = 0.01
    mat_glass.blend_method = 'BLEND'

    # Door & Bumper Protective Rub Strips: Dark Charcoal
    mat_trim = get_or_create_mat("Laguna_Trim_Charcoal")
    t_bsdf = mat_trim.node_tree.nodes.get("Principled BSDF")
    if t_bsdf:
        t_bsdf.inputs['Base Color'].default_value = (0.055, 0.055, 0.06, 1.0)
        t_bsdf.inputs['Metallic'].default_value = 0.0
        t_bsdf.inputs['Roughness'].default_value = 0.78

    # Window B-Pillars & Surrounds: Satin Black
    mat_pillar = get_or_create_mat("Laguna_Pillar_Black")
    p_bsdf = mat_pillar.node_tree.nodes.get("Principled BSDF")
    if p_bsdf:
        p_bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.022, 1.0)
        p_bsdf.inputs['Metallic'].default_value = 0.0
        p_bsdf.inputs['Roughness'].default_value = 0.52

    # Amber Side Repeaters:
    mat_amber = get_or_create_mat("Laguna_Amber_Indicator")
    a_bsdf = mat_amber.node_tree.nodes.get("Principled BSDF")
    if a_bsdf:
        a_bsdf.inputs['Base Color'].default_value = (0.98, 0.45, 0.02, 1.0)
        a_bsdf.inputs['Alpha'].default_value = 0.85
        a_bsdf.inputs['Roughness'].default_value = 0.05

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

    # Wheels: Renault OEM Silver Alloys
    mat_alloy = get_or_create_mat("Laguna_Factory_Alloy")
    al_bsdf = mat_alloy.node_tree.nodes.get("Principled BSDF")
    if al_bsdf:
        al_bsdf.inputs['Base Color'].default_value = (0.88, 0.90, 0.92, 1.0)
        al_bsdf.inputs['Metallic'].default_value = 0.78
        al_bsdf.inputs['Roughness'].default_value = 0.16
        al_bsdf.inputs['Coat Weight'].default_value = 0.8
        al_bsdf.inputs['Coat Roughness'].default_value = 0.03

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
    # 5. PERMANENTLY HIDE ALL RACE TRACK & DISTORTION PARTS
    # ----------------------------------------------------
    unwanted_objects = [
        'unnamed.069',       # Track headlight blanking plate (caused black right headlight!)
        'unnamed.034',       # Race single windshield wiper
        'unnamed.035',       # Race windshield wiper blade
        'unnamed.036',       # Race windshield wiper arm
        'unnamed.005',       # Race flat undertray & front tow hook
        'unnamed.009',       # Race front splitter
        'unnamed.135',       # Full roll cage
        'unnamed.136',       # Clipping inner tub (black triangle on fender)
        'unnamed.194',       # Inner tub bracket
        'Laguna_Race_Wing',  # Giant TCC rear wing
        'unnamed.125',       # Race interior net / bracket
        'unnamed.184',       # Race bracket
        'unnamed.128',       # Race wiper motor
    ]

    for name in unwanted_objects:
        o = bpy.data.objects.get(name)
        if o:
            o.hide_render = True
            o.hide_viewport = True
            print(f"  [Artifact Fix] Hidden {name}")

    # Remove hood pins from unnamed.007
    o7 = bpy.data.objects.get('unnamed.007')
    if o7:
        bm = bmesh.new()
        bm.from_mesh(o7.data)
        # Select and remove pin faces (Y < -1.80 and Z > 0.65)
        to_del = [f for f in bm.faces if any(v.co.y < -1.85 and v.co.z > 0.66 for v in f.verts)]
        if to_del:
            bmesh.ops.delete(bm, geom=to_del, context='FACES')
            bm.to_mesh(o7.data)
            o7.data.update()
            print(f"  [Artifact Fix] Deleted {len(to_del)} hood pin faces from unnamed.007!")
        bm.free()

    # ----------------------------------------------------
    # 6. DUAL PROJECTOR HEADLIGHTS IN BOTH SIDES
    # ----------------------------------------------------
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
                py = center.y - 0.020
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

    # Ensure headlight lenses are crystal clear
    for hl_lens_name in ['unnamed.017', 'unnamed.019', 'unnamed.070', 'unnamed.071']:
        o = bpy.data.objects.get(hl_lens_name)
        if o:
            o.data.materials.clear()
            o.data.materials.append(mat_hl_lens)
            o.hide_render = False

    # ----------------------------------------------------
    # 7. MULTI-TONE BODY AND TRIM (unnamed.004)
    # ----------------------------------------------------
    o4 = bpy.data.objects.get('unnamed.004')
    if o4:
        o4.data.materials.clear()
        o4.data.materials.append(mat_body)      # Slot 0: Body Champagne Silver
        o4.data.materials.append(mat_trim)      # Slot 1: Moulding Dark Charcoal
        o4.data.materials.append(mat_pillar)    # Slot 2: B-Pillar Satin Black
        o4.data.materials.append(mat_amber)     # Slot 3: Amber Side Repeater
        m4 = o4.data
        for p in m4.polygons:
            pts = [m4.vertices[v].co for v in p.vertices]
            cx = sum(pt.x for pt in pts) / len(pts)
            cy = sum(pt.y for pt in pts) / len(pts)
            cz = sum(pt.z for pt in pts) / len(pts)

            # Amber repeater marker on front fender
            if abs(cx) > 0.82 and -1.30 < cy < -1.10 and 0.58 < cz < 0.68:
                p.material_index = 3
            # B-Pillar and window surround satin black
            elif abs(cx) > 0.65 and -0.65 < cy < 0.75 and 0.85 < cz < 1.35:
                # Vertical B-pillar faces
                if abs(p.normal.x) > 0.5 or abs(p.normal.y) > 0.5:
                    p.material_index = 2
            # Door rubbing strips along the flanks
            elif abs(cx) > 0.72 and 0.48 < cz < 0.60 and -1.05 < cy < 1.10:
                p.material_index = 1
            # Rear bumper impact strip
            elif cy > 2.05 and 0.58 < cz < 0.72:
                p.material_index = 1
            else:
                p.material_index = 0

    # Taillight gap objects: assign to body paint
    for n in ['unnamed.149', 'unnamed.213', 'unnamed.150', 'unnamed.214']:
        o = bpy.data.objects.get(n)
        if o:
            o.data.materials.clear()
            o.data.materials.append(mat_body)
            o.hide_render = False

    # Taillight lenses: ruby red & clear reverse
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

    # Trunk lid: clean production integrated spoiler
    o25 = bpy.data.objects.get('unnamed.025')
    if o25:
        o25.data.materials.clear()
        o25.data.materials.append(mat_body)
        o25.hide_render = False

    # ----------------------------------------------------
    # 8. RENAULT OEM WHEEL CENTER CAPS WITH CHROME DIAMOND
    # ----------------------------------------------------
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
        verts = []
        faces = []
        c_pt = mathutils.Vector((wx + side * 0.015, wy, wz))
        verts.append(c_pt)
        num_pts = 24
        radius = 0.065
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

    # ----------------------------------------------------
    # 9. CAMERAS & PHOTOREALISTIC 1080P RENDERS
    # ----------------------------------------------------
    cam = scene.camera
    if not cam:
        cam_data = bpy.data.cameras.new("Main_Camera_Data")
        cam = bpy.data.objects.new("Main_Camera", cam_data)
        bpy.context.collection.objects.link(cam)
        scene.camera = cam

    cam.data.lens = 52.0 # 52mm realistic automotive portrait lens
    cam.data.sensor_width = 36.0
    cam.hide_render = False

    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080

    out_front = os.path.abspath(r"laguna_front.png")
    out_rear = os.path.abspath(r"laguna_rear.png")
    out_pres = os.path.abspath(r"laguna_presentation.png")

    # Front 3/4 View: matching reference 2
    print("[Render] Rendering Front 3/4 (laguna_front.png)...")
    cam.location = mathutils.Vector((-4.10, -4.35, 1.25))
    target_front = mathutils.Vector((0.0, -0.60, 0.58))
    cam.rotation_euler = (target_front - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    scene.render.filepath = out_front
    bpy.ops.render.render(write_still=True)

    # Rear 3/4 View: matching reference 1
    print("[Render] Rendering Rear 3/4 (laguna_rear.png)...")
    cam.location = mathutils.Vector((3.80, 4.30, 1.35))
    target_rear = mathutils.Vector((0.0, 0.40, 0.65))
    cam.rotation_euler = (target_rear - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    scene.render.filepath = out_rear
    bpy.ops.render.render(write_still=True)

    # Copy to artifacts directory
    shutil.copy2(out_front, out_pres)
    art_dir = r"C:\Users\abdelkarim\.gemini\antigravity\brain\fa1588ad-d9ab-4eb3-9303-e3e476714ebd"
    shutil.copy2(out_front, os.path.join(art_dir, "laguna_front.png"))
    shutil.copy2(out_rear, os.path.join(art_dir, "laguna_rear.png"))
    shutil.copy2(out_pres, os.path.join(art_dir, "laguna_presentation.png"))
    print("[Autonomous Loop] Complete! Renders saved to artifacts and workspace.")

if __name__ == "__main__":
    run_visual_overhaul()
