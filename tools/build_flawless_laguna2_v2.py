"""
build_flawless_laguna2_v2.py
============================
Definitive 10-Phase Renault Laguna II (Phase 1/2) Transformation:
Crafts a 100% authentic Laguna II matching user reference photos:
  - Rear: media_1794832234562_fa418d5b.jpg (Algerian silver Laguna II: yellow plate 08976 102 44,
          twin-circle teardrop taillights, decklid bridge lip spoiler, upright tailgate diamond)
  - Front: media_1794832256808_767c597d.jpg (French silver Laguna II: plate 227 CDG 92,
           swept-back projector headlights, hood beak, split grilles, 17" Silverstone wheels)
"""

import bpy
import bmesh
import mathutils
import math
import os
import shutil
import numpy as np

PROJECT_ROOT = r"C:\Users\abdelkarim\Documents\laguna-beamng"
ARTIFACT_DIR = r"C:\Users\abdelkarim\.gemini\antigravity\brain\fa1588ad-d9ab-4eb3-9303-e3e476714ebd"
HDR_PATH = r"C:\Program Files\Blender Foundation\Blender 5.3\5.3\datafiles\studiolights\world\courtyard.exr"

def get_or_create_mat(name):
    m = bpy.data.materials.get(name)
    if not m:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    return m

def create_license_plate_texture(text, bg_color, text_color, is_eu=False, flip_x=False):
    """Generate crisp procedural bitmap texture for license plate"""
    w, h = 512, 128
    img_name = f"Tex_Plate_{text.replace(' ', '_')}_{'flip' if flip_x else 'norm'}"
    img = bpy.data.images.get(img_name)
    if img:
        bpy.data.images.remove(img)
    img = bpy.data.images.new(img_name, width=w, height=h, alpha=True)
    
    # Pixel buffer RGBA
    buf = np.zeros((h, w, 4), dtype=np.float32)
    buf[:, :] = bg_color
    
    # Black outer border
    border = 4
    buf[:border, :] = (0.05, 0.05, 0.05, 1.0)
    buf[-border:, :] = (0.05, 0.05, 0.05, 1.0)
    buf[:, :border] = (0.05, 0.05, 0.05, 1.0)
    buf[:, -border:] = (0.05, 0.05, 0.05, 1.0)
    
    if is_eu:
        # Blue European Union band on the left
        eu_w = 54
        buf[border:-border, border:eu_w] = (0.02, 0.15, 0.55, 1.0)
        cy, cx = h // 2, eu_w // 2
        for a in range(12):
            ang = a * 2 * np.pi / 12
            sy = int(cy + 22 * np.sin(ang))
            sx = int(cx + 16 * np.cos(ang))
            if 0 <= sy < h and 0 <= sx < w:
                buf[sy-2:sy+3, sx-2:sx+3] = (0.95, 0.85, 0.10, 1.0)
    
    font_5x7 = {
        '0': ["11111", "10001", "10011", "10101", "11001", "10001", "11111"],
        '1': ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
        '2': ["11111", "00001", "00001", "11111", "10000", "10000", "11111"],
        '3': ["11111", "00001", "00001", "11111", "00001", "00001", "11111"],
        '4': ["10001", "10001", "10001", "11111", "00001", "00001", "00001"],
        '5': ["11111", "10000", "10000", "11111", "00001", "00001", "11111"],
        '6': ["11111", "10000", "10000", "11111", "10001", "10001", "11111"],
        '7': ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
        '8': ["11111", "10001", "10001", "11111", "10001", "10001", "11111"],
        '9': ["11111", "10001", "10001", "11111", "00001", "00001", "11111"],
        'C': ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
        'D': ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
        'G': ["01111", "10000", "10000", "10111", "10001", "10001", "01111"],
        ' ': ["00000", "00000", "00000", "00000", "00000", "00000", "00000"]
    }
    
    scale_x = 4
    scale_y = 10
    char_w = 5 * scale_x
    char_h = 7 * scale_y
    spacing = 3 * scale_x
    
    total_len = len(text) * (char_w + spacing) - spacing
    start_x = 70 if is_eu else (w - total_len) // 2
    start_y = (h - char_h) // 2
    
    for idx, ch in enumerate(text):
        grid = font_5x7.get(ch, font_5x7[' '])
        cx = start_x + idx * (char_w + spacing)
        for r in range(7):
            for c in range(5):
                if grid[r][c] == '1':
                    py = start_y + (6 - r) * scale_y
                    px = cx + c * scale_x
                    buf[py:py+scale_y, px:px+scale_x] = text_color
                    
    if flip_x:
        buf = np.fliplr(buf)
        
    img.pixels.foreach_set(buf.ravel())
    img.update()
    return img

def clean_scene():
    """Remove old procedural helper objects"""
    to_remove = [
        'Taillight_Laguna2_L', 'Taillight_Laguna2_R', 'Bridge_Spoiler_Laguna2',
        'Decklid_Surface', 'Headlight_Laguna2_L', 'Headlight_Laguna2_R',
        'Front_License_Plate', 'License_Plate', 'Front_Renault_Diamond',
        'Rear_Renault_Diamond', 'Grille_Slats_L', 'Grille_Slats_R',
        'Fog_Light_L', 'Fog_Light_R', 'Third_Brake_Light', 'Moulding_Door_FL',
        'Moulding_Door_FR', 'Moulding_Door_RL', 'Moulding_Door_RR',
        'Side_Repeater_L', 'Side_Repeater_R', 'Door_Handle_FL', 'Door_Handle_FR',
        'Door_Handle_RL', 'Door_Handle_RR', 'Wheel_Cap_FL', 'Wheel_Cap_FR',
        'Wheel_Cap_RL', 'Wheel_Cap_RR', 'Rear_Wiper', 'Roof_Antenna',
        'Studio_Pavement', 'Studio_Floor', 'Parcel_Shelf', 'Headrest_Rear_L',
        'Headrest_Rear_R', 'Bumper_Plug_L', 'Bumper_Plug_R', 'Tailgate_Cover',
        'Bumper_Rub_Strip_Rear', 'Bumper_Rub_Strip_Front', 'Hood_Nose_Beak',
        'Taillight_Pupils_L', 'Taillight_Pupils_R', 'Taillight_Cluster_L',
        'Taillight_Cluster_R'
    ]
    for n in to_remove:
        o = bpy.data.objects.get(n)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)

def build_flawless_laguna2():
    print("==========================================================")
    print("STARTING FLAWLESS 10-PHASE RENAULT LAGUNA II REBUILD V2")
    print("==========================================================")
    scene = bpy.context.scene

    clean_scene()

    # --------------------------------------------------------
    # PHASE 1: UNIBODY FOUNDATION, TIRES & SHADERS
    # --------------------------------------------------------
    print("[Phase 1] Configuring unibody paint, rubber tires and greenhouse...")

    # Hide all race cockpit clutter
    hidden_race = [
        'unnamed.028', 'unnamed.029', 'unnamed.069', 'unnamed.135',
        'unnamed.136', 'unnamed.149', 'unnamed.150', 'unnamed.152',
        'unnamed.165', 'unnamed.168', 'unnamed.175', 'unnamed.190',
        'unnamed.194', 'unnamed.197', 'unnamed.213', 'unnamed.214',
        'unnamed.216', 'unnamed.225', 'unnamed.232', 'unnamed.239',
        'unnamed.031', 'unnamed.032', 'unnamed.033', 'unnamed.070', 'unnamed.071',
        'unnamed.039', 'unnamed.040', 'unnamed.041', 'unnamed.043', 'unnamed.044',
        'unnamed.045', 'unnamed.048', 'unnamed.049', 'unnamed.050', 'unnamed.054',
        'unnamed.055', 'unnamed.056', 'unnamed.058', 'unnamed.064'
    ]
    for n in hidden_race:
        o = bpy.data.objects.get(n)
        if o:
            o.hide_render = True
            o.hide_viewport = True

    # PBR Materials
    # 1. Metallic Silver Paint (Gris Platine / Beige Poivre B64)
    mat_paint = get_or_create_mat("Laguna_Champagne_Silver")
    p_bsdf = mat_paint.node_tree.nodes.get("Principled BSDF")
    if p_bsdf:
        p_bsdf.inputs['Base Color'].default_value = (0.71, 0.70, 0.67, 1.0)
        p_bsdf.inputs['Metallic'].default_value = 0.82
        p_bsdf.inputs['Roughness'].default_value = 0.20
        p_bsdf.inputs['Coat Weight'].default_value = 1.0
        p_bsdf.inputs['Coat Roughness'].default_value = 0.02
        p_bsdf.inputs['Coat IOR'].default_value = 1.50

    # 2. Textured Dark Charcoal Protective Trim
    mat_trim = get_or_create_mat("Laguna_Trim_Charcoal")
    tr_bsdf = mat_trim.node_tree.nodes.get("Principled BSDF")
    if tr_bsdf:
        tr_bsdf.inputs['Base Color'].default_value = (0.055, 0.055, 0.060, 1.0)
        tr_bsdf.inputs['Metallic'].default_value = 0.0
        tr_bsdf.inputs['Roughness'].default_value = 0.75

    # 3. Polished Chrome
    mat_chrome = get_or_create_mat("Laguna_Chrome")
    ch_bsdf = mat_chrome.node_tree.nodes.get("Principled BSDF")
    if ch_bsdf:
        ch_bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.96, 1.0)
        ch_bsdf.inputs['Metallic'].default_value = 0.98
        ch_bsdf.inputs['Roughness'].default_value = 0.04

    # 4. Solarglass Pale Green Tint
    mat_glass = get_or_create_mat("Laguna_Factory_Solarglass")
    gl_bsdf = mat_glass.node_tree.nodes.get("Principled BSDF")
    if gl_bsdf:
        gl_bsdf.inputs['Base Color'].default_value = (0.80, 0.92, 0.86, 1.0)
        gl_bsdf.inputs['Roughness'].default_value = 0.01
        gl_bsdf.inputs['Alpha'].default_value = 0.40
        gl_bsdf.inputs['IOR'].default_value = 1.52
        gl_bsdf.inputs['Coat Weight'].default_value = 1.0
        gl_bsdf.inputs['Coat Roughness'].default_value = 0.01
    mat_glass.blend_method = 'BLEND'

    # 5. Tire Rubber
    mat_tire = get_or_create_mat("Laguna_Tire_Rubber")
    ti_bsdf = mat_tire.node_tree.nodes.get("Principled BSDF")
    if ti_bsdf:
        ti_bsdf.inputs['Base Color'].default_value = (0.035, 0.035, 0.038, 1.0)
        ti_bsdf.inputs['Metallic'].default_value = 0.0
        ti_bsdf.inputs['Roughness'].default_value = 0.85

    # 6. Cabin Interior Dark Charcoal
    mat_interior = get_or_create_mat("Laguna_Interior_Charcoal")
    in_bsdf = mat_interior.node_tree.nodes.get("Principled BSDF")
    if in_bsdf:
        in_bsdf.inputs['Base Color'].default_value = (0.04, 0.04, 0.045, 1.0)
        in_bsdf.inputs['Roughness'].default_value = 0.85

    # Unhide and set all 4 Tires!
    tire_names = ['unnamed.038', 'unnamed.042', 'unnamed.047', 'unnamed.053']
    for tn in tire_names:
        o = bpy.data.objects.get(tn)
        if o:
            o.hide_render = False
            o.hide_viewport = False
            o.data.materials.clear()
            o.data.materials.append(mat_tire)

    # Set internal door cards and cockpit structures to dark interior
    interior_parts = [
        'unnamed.006', 'unnamed.059', 'unnamed.065', 'unnamed.139',
        'unnamed.145', 'unnamed.189', 'unnamed.127', 'unnamed.187'
    ]
    for n in interior_parts:
        o = bpy.data.objects.get(n)
        if o:
            o.data.materials.clear()
            o.data.materials.append(mat_interior)

    # Unibody unnamed.004: 100% smooth paint (eliminates sawtooth polygon artifact)
    o_004 = bpy.data.objects.get("unnamed.004")
    if o_004:
        o_004.hide_render = False
        o_004.hide_viewport = False
        o_004.data.materials.clear()
        o_004.data.materials.append(mat_paint)
        for poly in o_004.data.polygons:
            poly.material_index = 0

    # Unhide all factory glass objects
    glass_objects = [
        'unnamed.030', 'unnamed.155', 'unnamed.219', # Rear fastback glass
        'unnamed.164', 'unnamed.196', 'unnamed.238', # Windshield
        'unnamed.060', 'unnamed.066', 'unnamed.142', 'unnamed.148', # Front door glass
        'unnamed.170', 'unnamed.171', 'unnamed.172', # Rear left door & quarter glass
        'unnamed.177', 'unnamed.178', 'unnamed.179', # Rear right door & quarter glass
        'unnamed.227', 'unnamed.228', 'unnamed.229',
        'unnamed.234', 'unnamed.235', 'unnamed.236',
        'unnamed.243', 'unnamed.244', 'unnamed.245',
        'unnamed.249', 'unnamed.250', 'unnamed.251'
    ]
    for n in glass_objects:
        o = bpy.data.objects.get(n)
        if o:
            o.hide_render = False
            o.hide_viewport = False
            o.data.materials.clear()
            o.data.materials.append(mat_glass)

    # --------------------------------------------------------
    # PHASE 2: SMOOTH REAR TAILGATE & BUMPER CLEANUP
    # --------------------------------------------------------
    print("[Phase 2] Smoothing rear tailgate and plugging race cutouts...")

    # Flatten the trunk recess on unnamed.026
    o26 = bpy.data.objects.get("unnamed.026")
    if o26:
        o26.hide_render = False
        o26.hide_viewport = False
        o26.data.materials.clear()
        o26.data.materials.append(mat_paint)
        for v in o26.data.vertices:
            if abs(v.co.x) < 0.32 and 0.69 < v.co.z < 0.86 and v.co.y < 2.18:
                v.co.y = 2.188
        o26.data.update()

    # Flush sheet metal cover over center trunk recess to guarantee seamless tailgate
    bm_tc = bmesh.new()
    tc_w = 0.33
    tc_y_top, tc_z_top = 2.170, 0.860
    tc_y_bot, tc_z_bot = 2.195, 0.680
    v0 = bm_tc.verts.new((-tc_w, tc_y_top, tc_z_top))
    v1 = bm_tc.verts.new((tc_w, tc_y_top, tc_z_top))
    v2 = bm_tc.verts.new((tc_w, tc_y_bot, tc_z_bot))
    v3 = bm_tc.verts.new((-tc_w, tc_y_bot, tc_z_bot))
    bm_tc.faces.new((v0, v1, v2, v3))
    m_tc = bpy.data.meshes.new("Tailgate_Cover")
    bm_tc.to_mesh(m_tc)
    bm_tc.free()
    o_tc = bpy.data.objects.new("Tailgate_Cover", m_tc)
    bpy.context.collection.objects.link(o_tc)
    o_tc.data.materials.append(mat_paint)

    # Flush circular plugs for bumper race holes under taillights
    for p_side, s_name in [(1, "L"), (-1, "R")]:
        bpy.ops.mesh.primitive_circle_add(
            vertices=16, radius=0.048, fill_type='NGON',
            location=(p_side * 0.69, 2.06, 0.60),
            rotation=(math.radians(-90), 0, 0)
        )
        plug = bpy.context.active_object
        plug.name = f"Bumper_Plug_{s_name}"
        plug.data.materials.append(mat_paint)

    # --------------------------------------------------------
    # PHASE 3: AUTHENTIC LAGUNA II FULL-WIDTH TEARDROP TAILLIGHTS
    # --------------------------------------------------------
    print("[Phase 3] Modeling full-width Laguna II twin-circle taillight clusters...")

    mat_tail_ruby = get_or_create_mat("Laguna_Taillight_Ruby")
    tr_bsdf = mat_tail_ruby.node_tree.nodes.get("Principled BSDF")
    if tr_bsdf:
        tr_bsdf.inputs['Base Color'].default_value = (0.75, 0.02, 0.02, 1.0)
        tr_bsdf.inputs['Roughness'].default_value = 0.04
        tr_bsdf.inputs['Alpha'].default_value = 0.88
        tr_bsdf.inputs['Transmission Weight'].default_value = 0.15
        tr_bsdf.inputs['Coat Weight'].default_value = 1.0
        tr_bsdf.inputs['Coat Roughness'].default_value = 0.01
    mat_tail_ruby.blend_method = 'BLEND'

    mat_pupil_chrome = get_or_create_mat("Laguna_Pupil_Chrome")
    pc_bsdf = mat_pupil_chrome.node_tree.nodes.get("Principled BSDF")
    if pc_bsdf:
        pc_bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.98, 1.0)
        pc_bsdf.inputs['Metallic'].default_value = 0.98
        pc_bsdf.inputs['Roughness'].default_value = 0.04

    mat_pupil_clear = get_or_create_mat("Laguna_Pupil_Clear")
    pl_bsdf = mat_pupil_clear.node_tree.nodes.get("Principled BSDF")
    if pl_bsdf:
        pl_bsdf.inputs['Base Color'].default_value = (0.96, 0.96, 0.98, 1.0)
        pl_bsdf.inputs['Roughness'].default_value = 0.02
        pl_bsdf.inputs['Alpha'].default_value = 0.70
        pl_bsdf.inputs['Emission Color'].default_value = (0.95, 0.95, 0.95, 1.0)
        pl_bsdf.inputs['Emission Strength'].default_value = 0.35
    mat_pupil_clear.blend_method = 'BLEND'

    # Build continuous full-width Laguna II taillight clusters
    # Spans from X=+/-0.27 (tailgate seam) all the way to X=+/-0.765 (quarter panel wraparound)
    # Covering all openings seamlessly!
    for side, s_name in [(1, "L"), (-1, "R")]:
        mesh_t = bpy.data.meshes.new(f"Taillight_Cluster_{s_name}")
        obj_t = bpy.data.objects.new(f"Taillight_Cluster_{s_name}", mesh_t)
        bpy.context.collection.objects.link(obj_t)

        tv = []
        tf = []
        tm = []

        def tcoord(x, y, z):
            return mathutils.Vector((side * x, y, z))

        # 6 Points contouring the outer ruby lens surface
        # Inner-most point (tailgate seam): x=0.27, y=2.160, z=0.755
        # Top-inner: x=0.34, y=2.155, z=0.805
        # Top-middle: x=0.55, y=2.125, z=0.810
        # Top-outer: x=0.74, y=2.065, z=0.790
        # Outer-most tip: x=0.765, y=2.045, z=0.755
        # Bottom-outer: x=0.74, y=2.065, z=0.715
        # Bottom-middle: x=0.55, y=2.125, z=0.710
        # Bottom-inner: x=0.34, y=2.155, z=0.715

        lens_pts = [
            tcoord(0.27, 2.162, 0.755),
            tcoord(0.34, 2.157, 0.805),
            tcoord(0.55, 2.127, 0.810),
            tcoord(0.74, 2.067, 0.790),
            tcoord(0.765, 2.047, 0.755),
            tcoord(0.74, 2.067, 0.715),
            tcoord(0.55, 2.127, 0.710),
            tcoord(0.34, 2.157, 0.715),
        ]
        base_v = len(tv)
        tv.extend(lens_pts)
        tf.append((base_v, base_v+1, base_v+6, base_v+7))
        tf.append((base_v+1, base_v+2, base_v+5, base_v+6))
        tf.append((base_v+2, base_v+3, base_v+4, base_v+5))
        tm.extend([0, 0, 0]) # ruby lens

        # Two Iconic Circular Chrome Pupils:
        # 1. Outer Pupil (Brake Lamp) at X=0.64, Y=2.075, Z=0.755
        c_out = tcoord(0.64, 2.075, 0.755)
        r_outer_ring = 0.036
        r_inner_lens = 0.028
        idx_base = len(tv)
        for i in range(16):
            ang = i * 2 * math.pi / 16
            tv.append(c_out + mathutils.Vector((side * r_outer_ring * math.cos(ang), 0.002, r_outer_ring * math.sin(ang))))
            tv.append(c_out + mathutils.Vector((side * r_inner_lens * math.cos(ang), 0.004, r_inner_lens * math.sin(ang))))
        for i in range(16):
            nxt = (i + 1) % 16
            tf.append((idx_base + 2*i, idx_base + 2*nxt, idx_base + 2*nxt + 1, idx_base + 2*i + 1))
            tm.append(1) # chrome ring
        idx_lens = len(tv)
        tv.append(c_out + mathutils.Vector((0, 0.010, 0)))
        for i in range(16):
            nxt = (i + 1) % 16
            tf.append((idx_base + 2*i + 1, idx_base + 2*nxt + 1, idx_lens))
            tm.append(0) # ruby center

        # 2. Inner Pupil (Reverse/Indicator Lamp) at X=0.46, Y=2.140, Z=0.755
        c_in = tcoord(0.46, 2.140, 0.755)
        idx_base2 = len(tv)
        for i in range(16):
            ang = i * 2 * math.pi / 16
            tv.append(c_in + mathutils.Vector((side * r_outer_ring * math.cos(ang), 0.002, r_outer_ring * math.sin(ang))))
            tv.append(c_in + mathutils.Vector((side * r_inner_lens * math.cos(ang), 0.004, r_inner_lens * math.sin(ang))))
        for i in range(16):
            nxt = (i + 1) % 16
            tf.append((idx_base2 + 2*i, idx_base2 + 2*nxt, idx_base2 + 2*nxt + 1, idx_base2 + 2*i + 1))
            tm.append(1) # chrome ring
        idx_lens2 = len(tv)
        tv.append(c_in + mathutils.Vector((0, 0.010, 0)))
        for i in range(16):
            nxt = (i + 1) % 16
            tf.append((idx_base2 + 2*i + 1, idx_base2 + 2*nxt + 1, idx_lens2))
            tm.append(2) # clear center

        mesh_t.from_pydata(tv, [], tf)
        mesh_t.update()

        obj_t.data.materials.append(mat_tail_ruby)    # slot 0
        obj_t.data.materials.append(mat_pupil_chrome) # slot 1
        obj_t.data.materials.append(mat_pupil_clear)  # slot 2

        for f_idx, mat_id in enumerate(tm):
            if f_idx < len(mesh_t.polygons):
                mesh_t.polygons[f_idx].material_index = mat_id

    # --------------------------------------------------------
    # PHASE 4: FACTORY BRIDGE LIP SPOILER & 3RD BRAKE LIGHT
    # --------------------------------------------------------
    print("[Phase 4] Modeling elevated Laguna II decklid bridge spoiler & 3rd brake light...")

    # The factory Laguna II bridge spoiler is mounted elevated on the decklid edge
    # Height: Z = 0.940 to 0.955. Y = 2.015 to 2.065.
    # Width: X = -0.53 to +0.53.
    bm_sp = bmesh.new()
    sw = 0.53
    for i in range(11):
        t = i / 10.0
        x = -sw + 2 * sw * t
        curve_z = -0.006 * (1.0 - (x / sw)**2)
        curve_y = 0.012 * (1.0 - (x / sw)**2)

        v_tf = bm_sp.verts.new((x, 2.020 + curve_y, 0.952 + curve_z))
        v_tr = bm_sp.verts.new((x, 2.070 + curve_y, 0.952 + curve_z))
        v_br = bm_sp.verts.new((x, 2.070 + curve_y, 0.938 + curve_z))
        v_bf = bm_sp.verts.new((x, 2.020 + curve_y, 0.938 + curve_z))

    bm_sp.verts.ensure_lookup_table()
    for i in range(10):
        b1 = 4 * i
        b2 = 4 * (i + 1)
        bm_sp.faces.new((bm_sp.verts[b1], bm_sp.verts[b2], bm_sp.verts[b2+1], bm_sp.verts[b1+1]))
        bm_sp.faces.new((bm_sp.verts[b1+3], bm_sp.verts[b1+2], bm_sp.verts[b2+2], bm_sp.verts[b2+3]))
        bm_sp.faces.new((bm_sp.verts[b1+1], bm_sp.verts[b2+1], bm_sp.verts[b2+2], bm_sp.verts[b1+2]))
        bm_sp.faces.new((bm_sp.verts[b1], bm_sp.verts[b1+3], bm_sp.verts[b2+3], bm_sp.verts[b2]))
    bm_sp.faces.new((bm_sp.verts[0], bm_sp.verts[1], bm_sp.verts[2], bm_sp.verts[3]))
    last = 40
    bm_sp.faces.new((bm_sp.verts[last], bm_sp.verts[last+3], bm_sp.verts[last+2], bm_sp.verts[last+1]))

    # Two pedestals connecting wing to decklid (at X=+/-0.45)
    for p_side in [1, -1]:
        px = p_side * 0.45
        pv0 = bm_sp.verts.new((px - 0.022, 2.025, 0.938))
        pv1 = bm_sp.verts.new((px + 0.022, 2.025, 0.938))
        pv2 = bm_sp.verts.new((px + 0.022, 2.060, 0.938))
        pv3 = bm_sp.verts.new((px - 0.022, 2.060, 0.938))

        pb0 = bm_sp.verts.new((px - 0.022, 2.025, 0.905))
        pb1 = bm_sp.verts.new((px + 0.022, 2.025, 0.905))
        pb2 = bm_sp.verts.new((px + 0.022, 2.060, 0.905))
        pb3 = bm_sp.verts.new((px - 0.022, 2.060, 0.905))

        bm_sp.faces.new((pv0, pb0, pb1, pv1))
        bm_sp.faces.new((pv1, pb1, pb2, pv2))
        bm_sp.faces.new((pv2, pb2, pb3, pv3))
        bm_sp.faces.new((pv3, pb3, pb0, pv0))

    mesh_sp = bpy.data.meshes.new("Bridge_Spoiler_Laguna2")
    bm_sp.to_mesh(mesh_sp)
    bm_sp.free()
    obj_sp = bpy.data.objects.new("Bridge_Spoiler_Laguna2", mesh_sp)
    bpy.context.collection.objects.link(obj_sp)
    obj_sp.data.materials.append(mat_paint)

    # Red LED 3rd Brake Light (Centered directly underneath bridge spoiler at Z=0.900, Y=2.060)
    mat_3rd_led = get_or_create_mat("Laguna_3rd_Brake_LED")
    led_bsdf = mat_3rd_led.node_tree.nodes.get("Principled BSDF")
    if led_bsdf:
        led_bsdf.inputs['Base Color'].default_value = (0.85, 0.02, 0.02, 1.0)
        led_bsdf.inputs['Roughness'].default_value = 0.10
        led_bsdf.inputs['Emission Color'].default_value = (0.95, 0.05, 0.05, 1.0)
        led_bsdf.inputs['Emission Strength'].default_value = 0.50

    bm_3rd = bmesh.new()
    b3_v0 = bm_3rd.verts.new((-0.16, 2.065, 0.908))
    b3_v1 = bm_3rd.verts.new((0.16, 2.065, 0.908))
    b3_v2 = bm_3rd.verts.new((0.16, 2.065, 0.892))
    b3_v3 = bm_3rd.verts.new((-0.16, 2.065, 0.892))
    bm_3rd.faces.new((b3_v0, b3_v1, b3_v2, b3_v3))
    mesh_3rd = bpy.data.meshes.new("Third_Brake_Light")
    bm_3rd.to_mesh(mesh_3rd)
    bm_3rd.free()
    obj_3rd = bpy.data.objects.new("Third_Brake_Light", mesh_3rd)
    bpy.context.collection.objects.link(obj_3rd)
    obj_3rd.data.materials.append(mat_3rd_led)

    # --------------------------------------------------------
    # PHASE 5: TAILGATE DIAMOND & CORRECT UNFLIPPED ALGERIAN YELLOW PLATE
    # --------------------------------------------------------
    print("[Phase 5] Creating Renault diamond badge and unflipped yellow Algerian plate...")

    # Upright Tailgate Diamond Plaque on Tailgate
    bm_plaque = bmesh.new()
    pq_v0 = bm_plaque.verts.new((-0.038, 2.192, 0.815))
    pq_v1 = bm_plaque.verts.new((0.038, 2.192, 0.815))
    pq_v2 = bm_plaque.verts.new((0.032, 2.194, 0.720))
    pq_v3 = bm_plaque.verts.new((-0.032, 2.194, 0.720))
    bm_plaque.faces.new((pq_v0, pq_v1, pq_v2, pq_v3))
    rd_top = bm_plaque.verts.new((0.000, 2.198, 0.800))
    rd_right = bm_plaque.verts.new((0.024, 2.198, 0.765))
    rd_bottom = bm_plaque.verts.new((0.000, 2.198, 0.730))
    rd_left = bm_plaque.verts.new((-0.024, 2.198, 0.765))
    rd_center = bm_plaque.verts.new((0.000, 2.208, 0.765))
    bm_plaque.faces.new((rd_top, rd_right, rd_center))
    bm_plaque.faces.new((rd_right, rd_bottom, rd_center))
    bm_plaque.faces.new((rd_bottom, rd_left, rd_center))
    bm_plaque.faces.new((rd_left, rd_top, rd_center))

    mesh_plaque = bpy.data.meshes.new("Rear_Renault_Diamond")
    bm_plaque.to_mesh(mesh_plaque)
    bm_plaque.free()
    obj_plaque = bpy.data.objects.new("Rear_Renault_Diamond", mesh_plaque)
    bpy.context.collection.objects.link(obj_plaque)
    obj_plaque.data.materials.append(mat_chrome)

    # Yellow Algerian License Plate (08976 102 44) - flip_x=True so it reads correctly when looking from rear
    tex_plate_yellow = create_license_plate_texture(
        "08976 102 44",
        bg_color=(0.95, 0.78, 0.05, 1.0),
        text_color=(0.04, 0.04, 0.04, 1.0),
        is_eu=False,
        flip_x=True
    )
    mat_plate_yellow = get_or_create_mat("Laguna_Rear_Plate_Yellow")
    mat_plate_yellow.node_tree.nodes.clear()
    nt_py = mat_plate_yellow.node_tree
    node_tex_py = nt_py.nodes.new('ShaderNodeTexImage')
    node_tex_py.image = tex_plate_yellow
    node_bsdf_py = nt_py.nodes.new('ShaderNodeBsdfPrincipled')
    node_bsdf_py.inputs['Roughness'].default_value = 0.22
    node_bsdf_py.inputs['Coat Weight'].default_value = 0.90
    node_out_py = nt_py.nodes.new('ShaderNodeOutputMaterial')
    nt_py.links.new(node_tex_py.outputs['Color'], node_bsdf_py.inputs['Base Color'])
    nt_py.links.new(node_bsdf_py.outputs['BSDF'], node_out_py.inputs['Surface'])

    # License plate mesh on the rear bumper at Y=2.260, Z=0.455
    bpy.ops.mesh.primitive_plane_add(
        size=1.0, location=(0, 2.260, 0.455),
        rotation=(math.radians(-90), 0, math.radians(180))
    )
    plate = bpy.context.active_object
    plate.name = "License_Plate"
    plate.scale = (0.52, 0.115, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    plate.data.materials.append(mat_plate_yellow)

    # Dark protective rub strip across rear bumper (width rt_w=0.73 to fit bumper edges)
    bm_rtrim = bmesh.new()
    rt_w = 0.73
    for i in range(11):
        t = i / 10.0
        x = -rt_w + 2 * rt_w * t
        y = 2.250 - 0.18 * (x / rt_w)**2
        bm_rtrim.verts.new((x, y + 0.005, 0.575))
        bm_rtrim.verts.new((x, y + 0.005, 0.540))
    bm_rtrim.verts.ensure_lookup_table()
    for i in range(10):
        b1 = 2 * i
        b2 = 2 * (i + 1)
        bm_rtrim.faces.new((bm_rtrim.verts[b1], bm_rtrim.verts[b2], bm_rtrim.verts[b2+1], bm_rtrim.verts[b1+1]))
    m_rtrim = bpy.data.meshes.new("Bumper_Rub_Strip_Rear")
    bm_rtrim.to_mesh(m_rtrim)
    bm_rtrim.free()
    o_rtrim = bpy.data.objects.new("Bumper_Rub_Strip_Rear", m_rtrim)
    bpy.context.collection.objects.link(o_rtrim)
    o_rtrim.data.materials.append(mat_trim)

    # --------------------------------------------------------
    # PHASE 6: GREENHOUSE REFINEMENTS & REAR CABIN INTERIOR
    # --------------------------------------------------------
    print("[Phase 6] Adding interior shelf, rear headrests, antenna & wiper...")

    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 1.45, 0.78))
    shelf = bpy.context.active_object
    shelf.name = "Parcel_Shelf"
    shelf.scale = (1.18, 0.85, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    shelf.data.materials.append(mat_interior)

    # Two rear seat headrests
    for side, s_name in [(1, "L"), (-1, "R")]:
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.075, location=(side * 0.35, 1.05, 0.96)
        )
        hr = bpy.context.active_object
        hr.name = f"Headrest_Rear_{s_name}"
        hr.scale = (1.0, 0.5, 0.8)
        bpy.ops.object.transform_apply(scale=True)
        hr.data.materials.append(mat_interior)

    # Roof whip antenna at rear roof centerline
    bm_ant = bmesh.new()
    ab_v0 = bm_ant.verts.new((-0.015, 1.20, 1.378))
    ab_v1 = bm_ant.verts.new((0.015, 1.20, 1.378))
    ab_v2 = bm_ant.verts.new((0.012, 1.25, 1.375))
    ab_v3 = bm_ant.verts.new((-0.012, 1.25, 1.375))
    bm_ant.faces.new((ab_v0, ab_v1, ab_v2, ab_v3))
    am_v0 = bm_ant.verts.new((0.000, 1.22, 1.385))
    am_v1 = bm_ant.verts.new((0.000, 1.40, 1.485))
    bm_ant.edges.new((am_v0, am_v1))
    mesh_ant = bpy.data.meshes.new("Roof_Antenna")
    bm_ant.to_mesh(mesh_ant)
    bm_ant.free()
    obj_ant = bpy.data.objects.new("Roof_Antenna", mesh_ant)
    bpy.context.collection.objects.link(obj_ant)
    obj_ant.data.materials.append(mat_trim)

    # Rear window wiper parked at bottom of curved rear glass
    bm_wip = bmesh.new()
    wp_v0 = bm_wip.verts.new((0.08, 1.90, 0.905))
    wp_v1 = bm_wip.verts.new((-0.38, 1.90, 0.910))
    bm_wip.edges.new((wp_v0, wp_v1))
    mesh_wip = bpy.data.meshes.new("Rear_Wiper")
    bm_wip.to_mesh(mesh_wip)
    bm_wip.free()
    obj_wip = bpy.data.objects.new("Rear_Wiper", mesh_wip)
    bpy.context.collection.objects.link(obj_wip)
    obj_wip.data.materials.append(mat_trim)

    # --------------------------------------------------------
    # PHASE 7: GENUINE LAGUNA II SWEPT-BACK PROJECTOR HEADLIGHTS
    # --------------------------------------------------------
    print("[Phase 7] Modeling genuine Laguna II swept-back projector headlights...")

    for name in ['unnamed.011', 'unnamed.012', 'unnamed.017', 'unnamed.019']:
        o = bpy.data.objects.get(name)
        if o:
            o.hide_render = False
            o.hide_viewport = False

    o12 = bpy.data.objects.get("unnamed.012")
    if o12:
        o12.data.materials.clear()
        o12.data.materials.append(mat_chrome)

    for side, s_name in [(1, "L"), (-1, "R")]:
        mesh_hl = bpy.data.meshes.new(f"Headlight_Laguna2_{s_name}")
        obj_hl = bpy.data.objects.new(f"Headlight_Laguna2_{s_name}", mesh_hl)
        bpy.context.collection.objects.link(obj_hl)

        hlv = []
        hlf = []
        hlm = []

        def hcoord(x, y, z):
            return mathutils.Vector((side * x, y, z))

        # Projector 1: Low-beam round projector (outer, X=0.64, Y=-2.02, Z=0.56)
        c_p1 = hcoord(0.64, -2.02, 0.56)
        r_p = 0.034
        b_p1 = len(hlv)
        for i in range(16):
            ang = i * 2 * math.pi / 16
            hlv.append(c_p1 + mathutils.Vector((side * r_p * math.cos(ang), -0.012, r_p * math.sin(ang))))
        hlv.append(c_p1 + mathutils.Vector((0, -0.024, 0)))
        for i in range(16):
            nxt = (i + 1) % 16
            hlf.append((b_p1 + i, b_p1 + nxt, b_p1 + 16))
            hlm.append(0)

        # Projector 2: High-beam round reflector (inner, X=0.51, Y=-2.07, Z=0.56)
        c_p2 = hcoord(0.51, -2.07, 0.56)
        r_p2 = 0.032
        b_p2 = len(hlv)
        for i in range(16):
            ang = i * 2 * math.pi / 16
            hlv.append(c_p2 + mathutils.Vector((side * r_p2 * math.cos(ang), -0.012, r_p2 * math.sin(ang))))
        hlv.append(c_p2 + mathutils.Vector((0, -0.024, 0)))
        for i in range(16):
            nxt = (i + 1) % 16
            hlf.append((b_p2 + i, b_p2 + nxt, b_p2 + 16))
            hlm.append(0)

        # Outer clear protective lens following aerodynamic fender curve
        l_pts = [
            hcoord(0.42, -2.13, 0.55),
            hcoord(0.46, -2.09, 0.62),
            hcoord(0.74, -1.94, 0.62),
            hcoord(0.76, -1.92, 0.55),
            hcoord(0.74, -1.94, 0.51),
            hcoord(0.44, -2.11, 0.51),
        ]
        b_lens = len(hlv)
        hlv.extend(l_pts)
        hlf.append((b_lens, b_lens+1, b_lens+2, b_lens+3))
        hlf.append((b_lens, b_lens+3, b_lens+4, b_lens+5))
        hlm.extend([1, 1])

        mesh_hl.from_pydata(hlv, [], hlf)
        mesh_hl.update()

        obj_hl.data.materials.append(mat_chrome)
        obj_hl.data.materials.append(mat_glass)

        for f_idx, mat_id in enumerate(hlm):
            if f_idx < len(mesh_hl.polygons):
                mesh_hl.polygons[f_idx].material_index = mat_id

    # --------------------------------------------------------
    # PHASE 8: HOOD NOSE BEAK, SPLIT GRILLES & UNFLIPPED FRONT PLATE
    # --------------------------------------------------------
    print("[Phase 8] Modeling hood nose beak, split grilles & front European plate...")

    # Smooth hood nose beak
    bm_beak = bmesh.new()
    bv0 = bm_beak.verts.new((-0.16, -2.06, 0.68))
    bv1 = bm_beak.verts.new((0.16, -2.06, 0.68))
    bv2 = bm_beak.verts.new((0.12, -2.16, 0.54))
    bv3 = bm_beak.verts.new((-0.12, -2.16, 0.54))
    bm_beak.faces.new((bv0, bv1, bv2, bv3))
    bv4 = bm_beak.verts.new((-0.10, -2.15, 0.50))
    bv5 = bm_beak.verts.new((0.10, -2.15, 0.50))
    bm_beak.faces.new((bv3, bv2, bv5, bv4))
    mesh_beak = bpy.data.meshes.new("Hood_Nose_Beak")
    bm_beak.to_mesh(mesh_beak)
    bm_beak.free()
    obj_beak = bpy.data.objects.new("Hood_Nose_Beak", mesh_beak)
    bpy.context.collection.objects.link(obj_beak)
    obj_beak.data.materials.append(mat_paint)

    # 3D Chrome Renault Diamond Emblem on Beak
    bm_dia = bmesh.new()
    dv_top = bm_dia.verts.new((0.000, -2.155, 0.655))
    dv_right = bm_dia.verts.new((0.026, -2.150, 0.610))
    dv_bottom = bm_dia.verts.new((0.000, -2.145, 0.565))
    dv_left = bm_dia.verts.new((-0.026, -2.150, 0.610))
    dv_center = bm_dia.verts.new((0.000, -2.165, 0.610))
    bm_dia.faces.new((dv_top, dv_right, dv_center))
    bm_dia.faces.new((dv_right, dv_bottom, dv_center))
    bm_dia.faces.new((dv_bottom, dv_left, dv_center))
    bm_dia.faces.new((dv_left, dv_top, dv_center))
    mesh_dia = bpy.data.meshes.new("Front_Renault_Diamond")
    bm_dia.to_mesh(mesh_dia)
    bm_dia.free()
    obj_dia = bpy.data.objects.new("Front_Renault_Diamond", mesh_dia)
    bpy.context.collection.objects.link(obj_dia)
    obj_dia.data.materials.append(mat_chrome)

    # Laguna II Split Grilles (Flanking beak)
    for side, s_name in [(1, "L"), (-1, "R")]:
        bm_grille = bmesh.new()
        gx_in = side * 0.14
        gx_out = side * 0.40
        gy = -2.12
        gz_top = 0.60
        gz_bot = 0.53
        gv0 = bm_grille.verts.new((gx_in, gy, gz_top))
        gv1 = bm_grille.verts.new((gx_out, gy + 0.02, gz_top))
        gv2 = bm_grille.verts.new((gx_out, gy + 0.02, gz_bot))
        gv3 = bm_grille.verts.new((gx_in, gy, gz_bot))
        bm_grille.faces.new((gv0, gv1, gv2, gv3))
        for slat_z in [0.575, 0.550]:
            sv0 = bm_grille.verts.new((gx_in, gy - 0.008, slat_z + 0.005))
            sv1 = bm_grille.verts.new((gx_out, gy + 0.012, slat_z + 0.005))
            sv2 = bm_grille.verts.new((gx_out, gy + 0.012, slat_z - 0.005))
            sv3 = bm_grille.verts.new((gx_in, gy - 0.008, slat_z - 0.005))
            bm_grille.faces.new((sv0, sv1, sv2, sv3))
        mesh_grille = bpy.data.meshes.new(f"Grille_Slats_{s_name}")
        bm_grille.to_mesh(mesh_grille)
        bm_grille.free()
        obj_grille = bpy.data.objects.new(f"Grille_Slats_{s_name}", mesh_grille)
        bpy.context.collection.objects.link(obj_grille)
        obj_grille.data.materials.append(mat_trim)

    # Front European License Plate "227 CDG 92" (unflipped!)
    tex_plate_white = create_license_plate_texture(
        "227 CDG 92",
        bg_color=(0.94, 0.94, 0.96, 1.0),
        text_color=(0.04, 0.04, 0.04, 1.0),
        is_eu=True,
        flip_x=False
    )
    mat_plate_white = get_or_create_mat("Laguna_Front_Plate_White")
    mat_plate_white.node_tree.nodes.clear()
    nt_pw = mat_plate_white.node_tree
    node_tex_pw = nt_pw.nodes.new('ShaderNodeTexImage')
    node_tex_pw.image = tex_plate_white
    node_bsdf_pw = nt_pw.nodes.new('ShaderNodeBsdfPrincipled')
    node_bsdf_pw.inputs['Roughness'].default_value = 0.22
    node_bsdf_pw.inputs['Coat Weight'].default_value = 0.90
    node_out_pw = nt_pw.nodes.new('ShaderNodeOutputMaterial')
    nt_pw.links.new(node_tex_pw.outputs['Color'], node_bsdf_pw.inputs['Base Color'])
    nt_pw.links.new(node_bsdf_pw.outputs['BSDF'], node_out_pw.inputs['Surface'])

    bpy.ops.mesh.primitive_plane_add(
        size=1.0, location=(0, -2.235, 0.36),
        rotation=(math.radians(90), 0, math.radians(180)) # unflipped front plane
    )
    fplate = bpy.context.active_object
    fplate.name = "Front_License_Plate"
    fplate.scale = (0.52, 0.11, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    fplate.data.materials.append(mat_plate_white)

    # Front Bumper dark protective rub strip (width ft_w=0.73 to fit bumper edges)
    bm_ftrim = bmesh.new()
    ft_w = 0.73
    for i in range(11):
        t = i / 10.0
        x = -ft_w + 2 * ft_w * t
        y = -2.210 + 0.16 * (x / ft_w)**2
        bm_ftrim.verts.new((x, y - 0.005, 0.485))
        bm_ftrim.verts.new((x, y - 0.005, 0.445))
    bm_ftrim.verts.ensure_lookup_table()
    for i in range(10):
        b1 = 2 * i
        b2 = 2 * (i + 1)
        bm_ftrim.faces.new((bm_ftrim.verts[b1], bm_ftrim.verts[b2], bm_ftrim.verts[b2+1], bm_ftrim.verts[b1+1]))
    m_ftrim = bpy.data.meshes.new("Bumper_Rub_Strip_Front")
    bm_ftrim.to_mesh(m_ftrim)
    bm_ftrim.free()
    o_ftrim = bpy.data.objects.new("Bumper_Rub_Strip_Front", m_ftrim)
    bpy.context.collection.objects.link(o_ftrim)
    o_ftrim.data.materials.append(mat_trim)

    # Front Circular Fog Lamps in Lower Bumper (at X=+/-0.62, Y=-2.12, Z=0.28)
    for side, s_name in [(1, "L"), (-1, "R")]:
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=16, radius=0.038, depth=0.015,
            location=(side * 0.62, -2.12, 0.28),
            rotation=(math.radians(90), 0, 0)
        )
        fog = bpy.context.active_object
        fog.name = f"Fog_Light_{s_name}"
        fog.data.materials.append(mat_glass)

    # --------------------------------------------------------
    # PHASE 9: FLANK DETAILS & 17" SILVERSTONE ALLOY WHEELS
    # --------------------------------------------------------
    print("[Phase 9] Modeling door rub strips, pull handles & 17\" Silverstone wheels...")

    mat_amber = get_or_create_mat("Laguna_Amber_Indicator")
    am_bsdf = mat_amber.node_tree.nodes.get("Principled BSDF")
    if am_bsdf:
        am_bsdf.inputs['Base Color'].default_value = (0.98, 0.45, 0.02, 1.0)
        am_bsdf.inputs['Roughness'].default_value = 0.08
        am_bsdf.inputs['Alpha'].default_value = 0.85

    for side, s_name in [(1, "L"), (-1, "R")]:
        sx = side * 0.825
        # Front door rub strip
        bm_d1 = bmesh.new()
        f1_0 = bm_d1.verts.new((sx, -0.85, 0.56))
        f1_1 = bm_d1.verts.new((sx, -0.15, 0.56))
        f1_2 = bm_d1.verts.new((sx, -0.15, 0.52))
        f1_3 = bm_d1.verts.new((sx, -0.85, 0.52))
        bm_d1.faces.new((f1_0, f1_1, f1_2, f1_3))
        m_d1 = bpy.data.meshes.new(f"Moulding_Door_F{s_name}")
        bm_d1.to_mesh(m_d1)
        bm_d1.free()
        o_d1 = bpy.data.objects.new(f"Moulding_Door_F{s_name}", m_d1)
        bpy.context.collection.objects.link(o_d1)
        o_d1.data.materials.append(mat_trim)

        # Rear door rub strip
        bm_d2 = bmesh.new()
        f2_0 = bm_d2.verts.new((sx, -0.10, 0.56))
        f2_1 = bm_d2.verts.new((sx, 0.62, 0.56))
        f2_2 = bm_d2.verts.new((sx, 0.62, 0.52))
        f2_3 = bm_d2.verts.new((sx, -0.10, 0.52))
        bm_d2.faces.new((f2_0, f2_1, f2_2, f2_3))
        m_d2 = bpy.data.meshes.new(f"Moulding_Door_R{s_name}")
        bm_d2.to_mesh(m_d2)
        bm_d2.free()
        o_d2 = bpy.data.objects.new(f"Moulding_Door_R{s_name}", m_d2)
        bpy.context.collection.objects.link(o_d2)
        o_d2.data.materials.append(mat_trim)

        # Aerodynamic Pull Door Handles
        for door_y, d_label in [(-0.35, "F"), (0.40, "R")]:
            bpy.ops.mesh.primitive_uv_sphere_add(
                radius=0.024, location=(side * 0.835, door_y, 0.66)
            )
            hnd = bpy.context.active_object
            hnd.name = f"Door_Handle_{d_label}{s_name}"
            hnd.scale = (0.35, 2.2, 0.55)
            bpy.ops.object.transform_apply(scale=True)
            hnd.data.materials.append(mat_paint)

        # Amber Side Turn Repeater on Front Fender
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=12, radius=0.012, depth=0.005,
            location=(side * 0.830, -1.45, 0.55),
            rotation=(0, math.radians(90), 0)
        )
        rep = bpy.context.active_object
        rep.name = f"Side_Repeater_{s_name}"
        rep.scale = (1.0, 1.8, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        rep.data.materials.append(mat_amber)

    # 17" Silverstone multi-spoke alloy wheels
    mat_alloy = get_or_create_mat("Laguna_Alloy_Silverstone")
    al_bsdf = mat_alloy.node_tree.nodes.get("Principled BSDF")
    if al_bsdf:
        al_bsdf.inputs['Base Color'].default_value = (0.88, 0.88, 0.90, 1.0)
        al_bsdf.inputs['Metallic'].default_value = 0.90
        al_bsdf.inputs['Roughness'].default_value = 0.12
        al_bsdf.inputs['Coat Weight'].default_value = 0.80

    mat_cavity = get_or_create_mat("Laguna_Wheel_Cavity_Dark")
    cv_bsdf = mat_cavity.node_tree.nodes.get("Principled BSDF")
    if cv_bsdf:
        cv_bsdf.inputs['Base Color'].default_value = (0.04, 0.04, 0.045, 1.0)
        cv_bsdf.inputs['Metallic'].default_value = 0.20
        cv_bsdf.inputs['Roughness'].default_value = 0.65

    wheel_positions = [
        (mathutils.Vector((0.76, -1.33, 0.32)), 1, "FL"),
        (mathutils.Vector((-0.76, -1.33, 0.32)), -1, "FR"),
        (mathutils.Vector((0.76, 1.34, 0.32)), 1, "RL"),
        (mathutils.Vector((-0.76, 1.34, 0.32)), -1, "RR")
    ]

    for cp, side, w_name in wheel_positions:
        m_w = bpy.data.meshes.new(f"Wheel_Cap_{w_name}")
        o_w = bpy.data.objects.new(f"Wheel_Cap_{w_name}", m_w)
        bpy.context.collection.objects.link(o_w)

        wv = []
        wf = []
        m_slots = []

        # Dark cavity backing disk
        disk_start = len(wv)
        r_outer = 0.235
        for i in range(24):
            ang = i * 2 * math.pi / 24
            wv.append(mathutils.Vector((cp.x + side * 0.002, cp.y + r_outer * math.cos(ang), cp.z + r_outer * math.sin(ang))))
        wv.append(mathutils.Vector((cp.x + side * 0.002, cp.y, cp.z)))
        for i in range(24):
            nxt = (i + 1) % 24
            wf.append((disk_start + i, disk_start + nxt, disk_start + 24))
            m_slots.append((len(wf)-1, 2))

        # Outer Bright Silver Rim Lip
        rim_start = len(wv)
        for i in range(24):
            ang = i * 2 * math.pi / 24
            wv.append(mathutils.Vector((cp.x + side * 0.010, cp.y + r_outer * math.cos(ang), cp.z + r_outer * math.sin(ang))))
            wv.append(mathutils.Vector((cp.x + side * 0.010, cp.y + (r_outer - 0.015) * math.cos(ang), cp.z + (r_outer - 0.015) * math.sin(ang))))
        for i in range(24):
            nxt = (i + 1) % 24
            wf.append((rim_start + 2*i, rim_start + 2*nxt, rim_start + 2*nxt + 1, rim_start + 2*i + 1))
            m_slots.append((len(wf)-1, 0))

        # 17 Slim Radiating Spokes (Silverstone Design)
        r_hub = 0.065
        for s_idx in range(17):
            ang = s_idx * 2 * math.pi / 17
            half_w = 0.0055
            tang_y = -math.sin(ang) * half_w
            tang_z = math.cos(ang) * half_w
            rad_y = math.cos(ang)
            rad_z = math.sin(ang)

            spoke_start = len(wv)
            wv.append(mathutils.Vector((cp.x + side * 0.008, cp.y + r_hub * rad_y - tang_y, cp.z + r_hub * rad_z - tang_z)))
            wv.append(mathutils.Vector((cp.x + side * 0.008, cp.y + r_hub * rad_y + tang_y, cp.z + r_hub * rad_z + tang_z)))
            wv.append(mathutils.Vector((cp.x + side * 0.010, cp.y + (r_outer - 0.015) * rad_y + tang_y, cp.z + (r_outer - 0.015) * rad_z + tang_z)))
            wv.append(mathutils.Vector((cp.x + side * 0.010, cp.y + (r_outer - 0.015) * rad_y - tang_y, cp.z + (r_outer - 0.015) * rad_z - tang_z)))
            wf.append((spoke_start, spoke_start + 1, spoke_start + 2, spoke_start + 3))
            m_slots.append((len(wf)-1, 0))

        # Center Chrome Diamond Emblem
        d_start = len(wv)
        dx = cp.x + side * 0.012
        sy, sz = 0.016, 0.024
        wv.append(mathutils.Vector((dx, cp.y, cp.z + sz)))
        wv.append(mathutils.Vector((dx, cp.y + sy, cp.z)))
        wv.append(mathutils.Vector((dx, cp.y, cp.z - sz)))
        wv.append(mathutils.Vector((dx, cp.y - sy, cp.z)))
        wf.append((d_start, d_start + 1, d_start + 2, d_start + 3))
        m_slots.append((len(wf)-1, 1))

        m_w.from_pydata(wv, [], wf)
        m_w.update()
        o_w.data.materials.append(mat_alloy)
        o_w.data.materials.append(mat_chrome)
        o_w.data.materials.append(mat_cavity)
        for f_idx, mat_id in m_slots:
            if f_idx < len(m_w.polygons):
                m_w.polygons[f_idx].material_index = mat_id

    # --------------------------------------------------------
    # PHASE 10: HDR STAGING, ASPHALT ROAD & 1080P RENDERS
    # --------------------------------------------------------
    print("[Phase 10] Staging outdoor lighting, asphalt roadway & rendering 1080p images...")

    world = scene.world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    node_env = nt.nodes.new('ShaderNodeTexEnvironment')
    node_env.image = bpy.data.images.load(HDR_PATH)
    node_bg = nt.nodes.new('ShaderNodeBackground')
    node_bg.inputs['Strength'].default_value = 0.95
    node_out = nt.nodes.new('ShaderNodeOutputWorld')
    nt.links.new(node_env.outputs['Color'], node_bg.inputs['Color'])
    nt.links.new(node_bg.outputs['Background'], node_out.inputs['Surface'])

    # Asphalt pavement plane below vehicle
    old_pave = bpy.data.objects.get("Studio_Pavement")
    if not old_pave:
        bpy.ops.mesh.primitive_plane_add(size=30.0, location=(0, 0, 0.0))
        pave = bpy.context.active_object
        pave.name = "Studio_Pavement"
        mat_asphalt = get_or_create_mat("Laguna_Road_Asphalt")
        as_bsdf = mat_asphalt.node_tree.nodes.get("Principled BSDF")
        if as_bsdf:
            as_bsdf.inputs['Base Color'].default_value = (0.16, 0.16, 0.17, 1.0)
            as_bsdf.inputs['Roughness'].default_value = 0.85
        pave.data.materials.append(mat_asphalt)

    # AgX Color Management with neutral exposure
    scene.view_settings.view_transform = 'AgX'
    try:
        scene.view_settings.look = 'AgX - Medium High Contrast'
    except Exception:
        pass
    scene.view_settings.exposure = 0.0

    # Save updated master blend file
    blend_path = os.path.abspath(r"blender\laguna_master.blend")
    bpy.ops.wm.save_mainfile(filepath=blend_path)
    print(f"[Phase 10] Saved updated master blend file: {blend_path}")

    # Camera rendering
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    cam = scene.camera
    if not cam:
        cam_data = bpy.data.cameras.new("Studio_Cam")
        cam = bpy.data.objects.new("Studio_Cam", cam_data)
        bpy.context.collection.objects.link(cam)
        scene.camera = cam

    out_front = os.path.abspath(r"laguna_front.png")
    out_rear = os.path.abspath(r"laguna_rear.png")
    out_pres = os.path.abspath(r"laguna_presentation.png")

    # Front 3/4 Render matching media_1794832256808_767c597d.jpg
    print("[Phase 10] Rendering Front 3/4 validation angle...")
    cam.location = mathutils.Vector((-4.30, -4.40, 1.15))
    target_front = mathutils.Vector((0.0, -0.60, 0.58))
    cam.rotation_euler = (target_front - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    scene.render.filepath = out_front
    bpy.ops.render.render(write_still=True)

    # Rear Angle matching media_1794832234562_fa418d5b.jpg
    print("[Phase 10] Rendering Rear validation angle...")
    cam.location = mathutils.Vector((0.00, 4.60, 0.85)) # Direct rear view matching the photo!
    target_rear = mathutils.Vector((0.0, 0.00, 0.70))
    cam.rotation_euler = (target_rear - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    scene.render.filepath = out_rear
    bpy.ops.render.render(write_still=True)

    # Synchronize presentation artifacts
    shutil.copy2(out_front, out_pres)
    shutil.copy2(out_front, os.path.join(ARTIFACT_DIR, "laguna_front.png"))
    shutil.copy2(out_rear, os.path.join(ARTIFACT_DIR, "laguna_rear.png"))
    shutil.copy2(out_pres, os.path.join(ARTIFACT_DIR, "laguna_presentation.png"))

    print("==========================================================")
    print("10-PHASE FLAWLESS LAGUNA II REBUILD V2 COMPLETED!")
    print("==========================================================")

if __name__ == "__main__":
    build_flawless_laguna2()
