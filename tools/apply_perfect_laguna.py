"""
Apply Perfect Renault Laguna II Production Realism:
- Multi-slot door rub strips on unnamed.057, 063, 240, 246
- Matte black B-pillars and window surrounds on unnamed.060, 142, 170, 243
- High-mount 3rd brake light on rear decklid
- Rear window wiper arm and blade matching ref_rear.jpg
- Flush metal plug for the circular cutout below left taillight
- 7-spoke Renault OEM alloy wheel covers with 3D chrome Renault diamond emblems
- Hides internal race parts (unnamed.029, 031, 220)
- Nishita physical sky with balanced exposure (-0.4) and ground roadway
- Renders high-res 1080p Front 3/4 and Rear 3/4 presentation images
"""

import bpy
import bmesh
import mathutils
import math
import os
import shutil

def run_perfection():
    print("==================================================")
    print("[Perfection] Starting Precision Detail Pass...")
    print("==================================================")

    scene = bpy.context.scene

    # 1. SHADERS
    def get_or_create_mat(name):
        m = bpy.data.materials.get(name)
        if not m:
            m = bpy.data.materials.new(name)
        m.use_nodes = True
        return m

    # Metallic Champagne Silver (Beige Poivre)
    mat_body = get_or_create_mat("Laguna_Champagne_Silver")
    b_bsdf = mat_body.node_tree.nodes.get("Principled BSDF")
    if b_bsdf:
        b_bsdf.inputs['Base Color'].default_value = (0.76, 0.73, 0.64, 1.0)
        b_bsdf.inputs['Metallic'].default_value = 0.85
        b_bsdf.inputs['Roughness'].default_value = 0.16
        b_bsdf.inputs['Coat Weight'].default_value = 1.0
        b_bsdf.inputs['Coat Roughness'].default_value = 0.02
        b_bsdf.inputs['Coat IOR'].default_value = 1.50

    # Solarglass: Pale green heat-rejecting factory glass
    mat_glass = get_or_create_mat("Laguna_Factory_Solarglass")
    g_bsdf = mat_glass.node_tree.nodes.get("Principled BSDF")
    if g_bsdf:
        g_bsdf.inputs['Base Color'].default_value = (0.82, 0.94, 0.88, 1.0)
        g_bsdf.inputs['Roughness'].default_value = 0.008
        g_bsdf.inputs['Alpha'].default_value = 0.30
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

    # 2. HIDE ALL REFERENCE PLANES & UNWANTED PARTS
    for o in bpy.data.objects:
        if 'Ref_Plane' in o.name or (o.users_collection and 'Reference' in o.users_collection[0].name):
            o.hide_render = True
            o.hide_viewport = True

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

    # 3. MULTI-SLOT ASSIGNMENTS ON ALL 4 DOORS (RUB STRIPS)
    # Front Right: unnamed.057, Rear Right: unnamed.240
    # Front Left: unnamed.063, Rear Left: unnamed.246
    for door_name in ['unnamed.057', 'unnamed.063', 'unnamed.240', 'unnamed.246']:
        d_obj = bpy.data.objects.get(door_name)
        if d_obj:
            d_obj.data.materials.clear()
            d_obj.data.materials.append(mat_body) # Slot 0: Body
            d_obj.data.materials.append(mat_trim) # Slot 1: Rub strip
            m = d_obj.data
            for p in m.polygons:
                pts = [m.vertices[v].co for v in p.vertices]
                cz = sum(v.z for v in pts) / len(pts)
                # Outer flank rub strip at Z in [0.46, 0.58]
                if 0.46 < cz < 0.58:
                    p.material_index = 1
                else:
                    p.material_index = 0
            d_obj.hide_render = False

    # 4. WINDOW FRAMES & B-PILLARS -> MATTE BLACK
    for frame_name in ['unnamed.060', 'unnamed.170', 'unnamed.142', 'unnamed.243', 'unnamed.171', 'unnamed.228', 'unnamed.244']:
        f_obj = bpy.data.objects.get(frame_name)
        if f_obj:
            f_obj.data.materials.clear()
            f_obj.data.materials.append(mat_pillar)
            f_obj.hide_render = False

    # 5. UNIBODY UNNAMED.004 CLEANUP (NO FENDER STRIP, ONLY AMBER REPEATER & REAR BUMPER STRIP)
    o4 = bpy.data.objects.get('unnamed.004')
    if o4:
        o4.data.materials.clear()
        o4.data.materials.append(mat_body)      # Slot 0: Body
        o4.data.materials.append(mat_trim)      # Slot 1: Bumper Trim
        o4.data.materials.append(mat_pillar)    # Slot 2: Satin Black
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
            # Rear bumper impact strip
            elif cy > 2.05 and 0.58 < cz < 0.72:
                p.material_index = 1
            else:
                p.material_index = 0
        o4.hide_render = False

    # 6. SEAL CUTOUT HOLE BELOW LEFT TAILLIGHT
    old_plug = bpy.data.objects.get("Rear_Bumper_Plug")
    if old_plug:
        bpy.data.objects.remove(old_plug, do_unlink=True)

    mesh_plug = bpy.data.meshes.new("Rear_Bumper_Plug_Mesh")
    obj_plug = bpy.data.objects.new("Rear_Bumper_Plug", mesh_plug)
    bpy.context.collection.objects.link(obj_plug)
    
    # Create smooth flush disc at X=0.60, Y=2.06, Z=0.54
    p_center = mathutils.Vector((0.60, 2.06, 0.54))
    plug_verts = [p_center]
    num_pts = 20
    radius = 0.055
    for pt in range(num_pts):
        ang = (2 * math.pi * pt) / num_pts
        # Aligned with angled rear bumper surface (normal approx (0.3, 0.9, -0.2))
        px = p_center.x + radius * math.cos(ang) * 0.8
        py = p_center.y - radius * math.cos(ang) * 0.3
        pz = p_center.z + radius * math.sin(ang)
        plug_verts.append(mathutils.Vector((px, py, pz)))
    plug_faces = []
    for pt in range(num_pts):
        next_pt = (pt + 1) % num_pts
        plug_faces.append((0, pt + 1, next_pt + 1))
    mesh_plug.from_pydata(plug_verts, [], plug_faces)
    mesh_plug.update()
    obj_plug.data.materials.append(mat_body)

    # 7. ADD AUTHENTIC REAR WINDOW WIPER
    old_rw = bpy.data.objects.get("Rear_Wiper")
    if old_rw:
        bpy.data.objects.remove(old_rw, do_unlink=True)

    mesh_rw = bpy.data.meshes.new("Rear_Wiper_Mesh")
    obj_rw = bpy.data.objects.new("Rear_Wiper", mesh_rw)
    bpy.context.collection.objects.link(obj_rw)
    
    # Wiper arm pivot at X=0.08, Y=1.75, Z=0.98, blade spanning diagonally up to X=-0.25, Y=1.35, Z=1.18
    w_verts = [
        mathutils.Vector((0.08, 1.76, 0.98)),
        mathutils.Vector((0.06, 1.76, 0.99)),
        mathutils.Vector((-0.26, 1.35, 1.20)),
        mathutils.Vector((-0.28, 1.35, 1.19)),
        # Blade cross
        mathutils.Vector((0.15, 1.68, 1.04)),
        mathutils.Vector((0.14, 1.69, 1.05)),
        mathutils.Vector((-0.35, 1.30, 1.23)),
        mathutils.Vector((-0.36, 1.30, 1.22))
    ]
    w_faces = [
        (0, 1, 2, 3), # Arm
        (4, 5, 6, 7)  # Blade
    ]
    mesh_rw.from_pydata(w_verts, [], w_faces)
    mesh_rw.update()
    obj_rw.data.materials.append(mat_pillar)

    # 8. HIGH-MOUNTED 3RD BRAKE LIGHT
    old_3bl = bpy.data.objects.get("Third_Brake_Light")
    if old_3bl:
        bpy.data.objects.remove(old_3bl, do_unlink=True)

    mesh_3bl = bpy.data.meshes.new("Third_Brake_Light_Mesh")
    obj_3bl = bpy.data.objects.new("Third_Brake_Light", mesh_3bl)
    bpy.context.collection.objects.link(obj_3bl)
    # Under rear decklid lip at X=0, Y=1.88, Z=0.96
    w_half = 0.14
    h_half = 0.012
    y_pos = 1.88
    z_pos = 0.965
    tbl_verts = [
        mathutils.Vector((-w_half, y_pos, z_pos - h_half)),
        mathutils.Vector(( w_half, y_pos, z_pos - h_half)),
        mathutils.Vector(( w_half, y_pos - 0.01, z_pos + h_half)),
        mathutils.Vector((-w_half, y_pos - 0.01, z_pos + h_half))
    ]
    mesh_3bl.from_pydata(tbl_verts, [], [(0, 1, 2, 3)])
    mesh_3bl.update()
    obj_3bl.data.materials.append(mat_tl_ruby)

    # 9. RENAULT 7-SPOKE OEM ALLOY WHEEL HUBCAPS WITH 3D CHROME DIAMOND
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
        c_pt = mathutils.Vector((wx + side * 0.018, wy, wz))
        verts.append(c_pt) # 0: center hub
        
        # Inner hub ring (radius 0.035)
        num_spokes = 7
        for i in range(num_spokes * 2):
            ang = (2 * math.pi * i) / (num_spokes * 2)
            py = c_pt.y + 0.032 * math.cos(ang)
            pz = c_pt.z + 0.032 * math.sin(ang)
            verts.append(mathutils.Vector((c_pt.x, py, pz)))
            
        # Outer rim ring (radius 0.17)
        outer_start = len(verts)
        for i in range(num_spokes * 2):
            ang = (2 * math.pi * i) / (num_spokes * 2)
            # Spokes protrude slightly outward, recesses set slightly inward
            r = 0.17
            px = c_pt.x - side * (0.005 if i % 2 == 1 else 0.000)
            py = c_pt.y + r * math.cos(ang)
            pz = c_pt.z + r * math.sin(ang)
            verts.append(mathutils.Vector((px, py, pz)))
            
        # Center cap faces
        for i in range(num_spokes * 2):
            next_i = (i + 1) % (num_spokes * 2)
            faces.append((0, i + 1, next_i + 1))
            
        # 7 Spoke faces & recesses
        for i in range(num_spokes * 2):
            next_i = (i + 1) % (num_spokes * 2)
            i1 = i + 1
            i2 = next_i + 1
            o1 = outer_start + i
            o2 = outer_start + next_i
            faces.append((i1, o1, o2, i2))
            
        # 3D Chrome Renault Diamond Emblem in center
        dia_start = len(verts)
        d_x = c_pt.x + side * 0.004
        d_y = c_pt.y
        d_z = c_pt.z
        s_y = 0.014
        s_z = 0.022
        # Diamond vertices: Top, Right, Bottom, Left, and Inner cutout
        verts.append(mathutils.Vector((d_x, d_y, d_z + s_z)))       # Top
        verts.append(mathutils.Vector((d_x, d_y + s_y, d_z)))       # Right
        verts.append(mathutils.Vector((d_x, d_y, d_z - s_z)))       # Bottom
        verts.append(mathutils.Vector((d_x, d_y - s_y, d_z)))       # Left
        verts.append(mathutils.Vector((d_x, d_y, d_z + s_z*0.5)))   # Inner Top
        verts.append(mathutils.Vector((d_x, d_y + s_y*0.5, d_z)))   # Inner Right
        verts.append(mathutils.Vector((d_x, d_y, d_z - s_z*0.5)))   # Inner Bottom
        verts.append(mathutils.Vector((d_x, d_y - s_y*0.5, d_z)))   # Inner Left

        # Diamond ring faces
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
        # Assign diamond faces to chrome slot
        for p_idx in range(len(faces) - 4, len(faces)):
            mesh.polygons[p_idx].material_index = 1

    # 10. REAR & FRONT LIGHTS CLEAR & RUBY
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

    for hl_lens_name in ['unnamed.017', 'unnamed.019', 'unnamed.070', 'unnamed.071']:
        o = bpy.data.objects.get(hl_lens_name)
        if o:
            o.data.materials.clear()
            o.data.materials.append(mat_hl_lens)
            o.hide_render = False

    # Trunk lid production integrated spoiler
    o25 = bpy.data.objects.get('unnamed.025')
    if o25:
        o25.data.materials.clear()
        o25.data.materials.append(mat_body)
        o25.hide_render = False

    # 11. EXPOSURE & VIEWPORT SETTINGS
    world = scene.world
    if world and world.node_tree:
        bg = world.node_tree.nodes.get('ShaderNodeBackground') or world.node_tree.nodes.get('Background')
        if bg:
            bg.inputs['Strength'].default_value = 0.05
    scene.view_settings.view_transform = 'AgX'
    try:
        scene.view_settings.look = 'AgX - High Contrast'
    except Exception:
        pass
    scene.view_settings.exposure = -0.4

    # 12. HIGH-RES RENDERS
    cam = scene.camera
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080

    out_front = os.path.abspath(r"laguna_front.png")
    out_rear = os.path.abspath(r"laguna_rear.png")
    out_pres = os.path.abspath(r"laguna_presentation.png")

    # Front 3/4
    print("[Render] Rendering Front 3/4 (laguna_front.png)...")
    cam.location = mathutils.Vector((-4.10, -4.35, 1.25))
    target_front = mathutils.Vector((0.0, -0.60, 0.58))
    cam.rotation_euler = (target_front - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    scene.render.filepath = out_front
    bpy.ops.render.render(write_still=True)

    # Rear 3/4
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
    print("[Perfection] All renders saved to artifacts and workspace.")

if __name__ == "__main__":
    run_perfection()
