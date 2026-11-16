"""
build_pure_laguna2.py
=====================
Definitive 10-Phase Renault Laguna II Phase 1 (2001-2005) Transformation:
Focuses 100% on the genuine Renault Laguna II design, eliminating all Laguna 1 touring car cues:
  Phase 1: Pure Laguna II fastback arch profile, unibody cleanup, and roofline alignment.
  Phase 2: Sleek aerodynamic wraparound headlights with dual chrome projectors & amber corners.
  Phase 3: Laguna II central nose beak, chrome diamond, split grille horizontal slats & fog lights.
  Phase 4: Iconic Laguna II twin-circle teardrop taillight clusters (two round lamps with chrome rings per side).
  Phase 5: Factory Laguna II aerodynamic bridge lip spoiler & high-mounted horizontal 3rd brake light.
  Phase 6: Upright tailgate Renault diamond on silver plaque & recessed yellow plate (08976 102 44).
  Phase 7: Fastback greenhouse Solarglass, black ceramic frit, roof antenna, and rear parcel shelf.
  Phase 8: Flank detailing: dark door rub strips, aerodynamic pull handles & amber side repeaters.
  Phase 9: Authentic 17" Renault "Silverstone" 17-spoke alloy wheels with 5-lug pockets & road tires.
  Phase 10: Calibrated satin matte Beige Poivre / Platinum Silver paint, HDR staging & 1080p renders.
"""

import bpy
import bmesh
import mathutils
import math
import os
import shutil

PROJECT_ROOT = r"C:\Users\abdelkarim\Documents\laguna-beamng"
ARTIFACT_DIR = r"C:\Users\abdelkarim\.gemini\antigravity\brain\fa1588ad-d9ab-4eb3-9303-e3e476714ebd"
HDR_PATH = r"C:\Program Files\Blender Foundation\Blender 5.3\5.3\datafiles\studiolights\world\courtyard.exr"

def get_or_create_mat(name):
    m = bpy.data.materials.get(name)
    if not m:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
    return m

def build_laguna2():
    print("==========================================================")
    print("STARTING 10-PHASE PURE RENAULT LAGUNA II REBUILD")
    print("==========================================================")
    scene = bpy.context.scene

    # --------------------------------------------------------
    # PHASE 1: UNIBODY & CHASSIS CLEANUP (LAGUNA II FASTBACK ARCH)
    # --------------------------------------------------------
    print("[Phase 1] Aligning fastback unibody and removing all legacy race components...")
    # Hide all Laguna 1 / touring car race remnants
    legacy_parts = [
        'unnamed.028', 'unnamed.029', 'unnamed.030', 'unnamed.069',
        'unnamed.010', 'unnamed.011', 'unnamed.012', 'unnamed.013', 'unnamed.014',
        'unnamed.015', 'unnamed.016', 'unnamed.017', 'unnamed.018', 'unnamed.019',
        'unnamed.020', 'unnamed.032', 'unnamed.033', 'unnamed.070', 'unnamed.071',
        'unnamed.135', 'unnamed.136', 'unnamed.149', 'unnamed.150', 'unnamed.152',
        'unnamed.153', 'unnamed.155', 'unnamed.156', 'unnamed.157', 'unnamed.158',
        'unnamed.159', 'unnamed.160', 'unnamed.161', 'unnamed.162', 'unnamed.165',
        'unnamed.168', 'unnamed.175', 'unnamed.190', 'unnamed.194', 'unnamed.197',
        'unnamed.213', 'unnamed.214', 'unnamed.216', 'unnamed.217', 'unnamed.219',
        'unnamed.221', 'unnamed.222', 'unnamed.225', 'unnamed.232', 'unnamed.239',
        'Bumper_Trim_Patch_R', 'Rub_Strip_Rear_Bumper', 'Rub_Strip_Front_L', 'Rub_Strip_Front_R',
        'Rear_Bumper_Plug'
    ]
    for n in legacy_parts:
        o = bpy.data.objects.get(n)
        if o:
            o.hide_render = True
            o.hide_viewport = True

    # PBR Materials setup
    mat_paint = get_or_create_mat("Laguna_Champagne_Silver")
    mat_paint.use_nodes = True
    p_bsdf = mat_paint.node_tree.nodes.get("Principled BSDF")
    if p_bsdf:
        # Authentic Renault Laguna II Beige Poivre / Gris Platine (B64)
        p_bsdf.inputs['Base Color'].default_value = (0.50, 0.46, 0.39, 1.0)
        p_bsdf.inputs['Metallic'].default_value = 0.10
        p_bsdf.inputs['Roughness'].default_value = 0.40
        p_bsdf.inputs['Coat Weight'].default_value = 0.12
        p_bsdf.inputs['Coat Roughness'].default_value = 0.30

    mat_trim = get_or_create_mat("Laguna_Trim_Charcoal")
    tr_bsdf = mat_trim.node_tree.nodes.get("Principled BSDF")
    if tr_bsdf:
        tr_bsdf.inputs['Base Color'].default_value = (0.065, 0.065, 0.070, 1.0)
        tr_bsdf.inputs['Metallic'].default_value = 0.0
        tr_bsdf.inputs['Roughness'].default_value = 0.72

    mat_chrome = get_or_create_mat("Laguna_Chrome")
    ch_bsdf = mat_chrome.node_tree.nodes.get("Principled BSDF")
    if ch_bsdf:
        ch_bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.96, 1.0)
        ch_bsdf.inputs['Metallic'].default_value = 0.98
        ch_bsdf.inputs['Roughness'].default_value = 0.04

    # Ensure unibody unnamed.004 has clean paint
    o_004 = bpy.data.objects.get("unnamed.004")
    if o_004:
        o_004.hide_render = False
        o_004.hide_viewport = False
        o_004.data.materials.clear()
        o_004.data.materials.append(mat_paint)
        o_004.data.materials.append(mat_trim)
        # Assign bumper moulding band across rear and front
        for poly in o_004.data.polygons:
            verts = [o_004.matrix_world @ o_004.data.vertices[v_idx].co for v_idx in poly.vertices]
            # Rear bumper horizontal rub strip
            if all(v.y > 1.84 and 0.57 < v.z < 0.63 for v in verts):
                poly.material_index = 1
            # Front bumper corner rub strip
            elif all(v.y < -1.86 and 0.44 < v.z < 0.49 and abs(v.x) > 0.50 for v in verts):
                poly.material_index = 1
            else:
                poly.material_index = 0
        o_004.data.update()

    # Smooth fastback Decklid Surface connecting rear glass down to trunk lip
    old_deck = bpy.data.objects.get("Decklid_Surface")
    if old_deck:
        bpy.data.objects.remove(old_deck, do_unlink=True)
    m_deck = bpy.data.meshes.new("Decklid_Surface_Mesh")
    o_deck = bpy.data.objects.new("Decklid_Surface", m_deck)
    bpy.context.collection.objects.link(o_deck)

    xs = [-0.62, -0.46, -0.30, -0.15, 0.0, 0.15, 0.30, 0.46, 0.62]
    ys = [1.955, 1.995, 2.035, 2.075, 2.095]
    dv, df = [], []
    for y_idx, py in enumerate(ys):
        for px in xs:
            crown = 0.012 * (1.0 - (px / 0.62)**2)
            t = y_idx / (len(ys) - 1)
            pz = (1.0 - t) * 0.965 + t * 0.898 + crown
            dv.append(mathutils.Vector((px, py, pz)))
    nx, ny = len(xs), len(ys)
    for j in range(ny - 1):
        for i in range(nx - 1):
            i0 = j * nx + i
            df.append((i0, i0 + 1, (j + 1) * nx + (i + 1), (j + 1) * nx + i))
    m_deck.from_pydata(dv, [], df)
    m_deck.update()
    o_deck.data.materials.append(mat_paint)

    # --------------------------------------------------------
    # PHASE 2: SLEEK LAGUNA II WRAPAROUND HEADLIGHT ASSEMBLIES
    # --------------------------------------------------------
    print("[Phase 2] Modeling genuine Laguna II swept-back projector headlights...")
    mat_hl_glass = get_or_create_mat("Laguna_Headlight_Glass")
    hlg_bsdf = mat_hl_glass.node_tree.nodes.get("Principled BSDF")
    if hlg_bsdf:
        hlg_bsdf.inputs['Base Color'].default_value = (0.95, 0.97, 1.0, 1.0)
        hlg_bsdf.inputs['Roughness'].default_value = 0.02
        hlg_bsdf.inputs['Transmission Weight'].default_value = 0.88
        hlg_bsdf.inputs['Alpha'].default_value = 0.35
        hlg_bsdf.inputs['IOR'].default_value = 1.51
        hlg_bsdf.inputs['Coat Weight'].default_value = 1.0

    mat_reflector = get_or_create_mat("Laguna_Headlight_Reflector")
    ref_bsdf = mat_reflector.node_tree.nodes.get("Principled BSDF")
    if ref_bsdf:
        ref_bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.96, 1.0)
        ref_bsdf.inputs['Metallic'].default_value = 0.98
        ref_bsdf.inputs['Roughness'].default_value = 0.04

    mat_amber = get_or_create_mat("Laguna_Amber_Indicator")
    amb_bsdf = mat_amber.node_tree.nodes.get("Principled BSDF")
    if amb_bsdf:
        amb_bsdf.inputs['Base Color'].default_value = (1.0, 0.45, 0.03, 1.0)
        amb_bsdf.inputs['Roughness'].default_value = 0.15
        if 'Emission Color' in amb_bsdf.inputs:
            amb_bsdf.inputs['Emission Color'].default_value = (1.0, 0.40, 0.02, 1.0)
            amb_bsdf.inputs['Emission Strength'].default_value = 0.8

    for hl_name in ["Headlight_Laguna2_L", "Headlight_Laguna2_R", "Headlight_Reflector_L", "Headlight_Reflector_R"]:
        oh = bpy.data.objects.get(hl_name)
        if oh:
            bpy.data.objects.remove(oh, do_unlink=True)

    for side_name, s_sign in [("Headlight_Laguna2_L", -1), ("Headlight_Laguna2_R", 1)]:
        m_hl = bpy.data.meshes.new(side_name + "_Mesh")
        o_hl = bpy.data.objects.new(side_name, m_hl)
        bpy.context.collection.objects.link(o_hl)

        hv, hf = [], []
        # Outer lens wrapping around from front center to side fender
        # (x from 0.40 to 0.82, y from -2.16 back to -1.90, z ~ 0.51 to 0.62)
        lens_profile = [
            (s_sign * 0.42, -2.160, 0.520),
            (s_sign * 0.56, -2.140, 0.518),
            (s_sign * 0.68, -2.100, 0.525),
            (s_sign * 0.78, -2.020, 0.540),
            (s_sign * 0.82, -1.900, 0.560)
        ]
        h_lens = 0.095
        for px, py, pz in lens_profile:
            hv.append(mathutils.Vector((px, py, pz)))
            hv.append(mathutils.Vector((px, py + 0.015, pz + h_lens)))
        for i in range(len(lens_profile) - 1):
            i0 = i * 2
            hf.append((i0, i0 + 2, i0 + 3, i0 + 1))

        # Projector 1 (low beam): center (s_sign * 0.58, -2.05, 0.565), radius 0.038
        cp1 = mathutils.Vector((s_sign * 0.58, -2.05, 0.565))
        c1_idx = len(hv)
        hv.append(cp1 - mathutils.Vector((0, 0.025, 0)))
        for i in range(12):
            a = 2 * math.pi * i / 12
            hv.append(cp1 + mathutils.Vector((0.038 * math.cos(a), 0.005, 0.038 * math.sin(a))))
        for i in range(12):
            hf.append((c1_idx, c1_idx + 1 + i, c1_idx + 1 + (i + 1) % 12))

        # Projector 2 (high beam): center (s_sign * 0.48, -2.07, 0.565), radius 0.034
        cp2 = mathutils.Vector((s_sign * 0.48, -2.07, 0.565))
        c2_idx = len(hv)
        hv.append(cp2 - mathutils.Vector((0, 0.022, 0)))
        for i in range(12):
            a = 2 * math.pi * i / 12
            hv.append(cp2 + mathutils.Vector((0.034 * math.cos(a), 0.005, 0.034 * math.sin(a))))
        for i in range(12):
            hf.append((c2_idx, c2_idx + 1 + i, c2_idx + 1 + (i + 1) % 12))

        # Amber turn indicator bulb in outer fender sweep
        cp3 = mathutils.Vector((s_sign * 0.74, -1.98, 0.575))
        c3_idx = len(hv)
        hv.append(cp3)
        for i in range(8):
            a = 2 * math.pi * i / 8
            hv.append(cp3 + mathutils.Vector((0.016 * math.cos(a), 0.005, 0.016 * math.sin(a))))
        for i in range(8):
            hf.append((c3_idx, c3_idx + 1 + i, c3_idx + 1 + (i + 1) % 8))

        m_hl.from_pydata(hv, [], hf)
        m_hl.update()
        o_hl.data.materials.append(mat_hl_glass)    # 0
        o_hl.data.materials.append(mat_reflector)   # 1
        o_hl.data.materials.append(mat_amber)       # 2

        # Assign materials: lens faces = 0, projectors = 1, amber bulb = 2
        n_lens_faces = len(lens_profile) - 1
        for poly_idx in range(len(m_hl.polygons)):
            if poly_idx < n_lens_faces:
                m_hl.polygons[poly_idx].material_index = 0
            elif poly_idx < n_lens_faces + 24:
                m_hl.polygons[poly_idx].material_index = 1
            else:
                m_hl.polygons[poly_idx].material_index = 2

    # --------------------------------------------------------
    # PHASE 3: LAGUNA II NOSE BEAK, SPLIT GRILLE SLATS & FOGS
    # --------------------------------------------------------
    print("[Phase 3] Modeling central hood nose beak, chrome diamond, split grilles & fog lights...")
    # Front Renault Diamond on beak
    old_fd = bpy.data.objects.get("Front_Renault_Diamond")
    if old_fd:
        bpy.data.objects.remove(old_fd, do_unlink=True)
    m_fd = bpy.data.meshes.new("Front_Renault_Diamond_Mesh")
    o_fd = bpy.data.objects.new("Front_Renault_Diamond", m_fd)
    bpy.context.collection.objects.link(o_fd)
    c_fd = mathutils.Vector((0.0, -2.170, 0.605))
    sy, sz = 0.026, 0.044
    fd_v = [
        c_fd + mathutils.Vector((0, -0.012, sz)),
        c_fd + mathutils.Vector((sy, -0.010, 0)),
        c_fd + mathutils.Vector((0, -0.012, -sz)),
        c_fd + mathutils.Vector((-sy, -0.010, 0)),
        c_fd + mathutils.Vector((0, -0.018, 0))
    ]
    m_fd.from_pydata(fd_v, [], [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)])
    m_fd.update()
    o_fd.data.materials.append(mat_chrome)

    # Split grille horizontal slats flanking the beak
    for g_name in ["Grille_Slats_L", "Grille_Slats_R"]:
        og = bpy.data.objects.get(g_name)
        if og:
            bpy.data.objects.remove(og, do_unlink=True)

    for g_name, s_sign in [("Grille_Slats_L", -1), ("Grille_Slats_R", 1)]:
        m_gr = bpy.data.meshes.new(g_name + "_Mesh")
        o_gr = bpy.data.objects.new(g_name, m_gr)
        bpy.context.collection.objects.link(o_gr)
        gv, gf = [], []
        for slat_i in range(3):
            z_slat = 0.505 + slat_i * 0.018
            p_in = mathutils.Vector((s_sign * 0.09, -2.165, z_slat))
            p_out = mathutils.Vector((s_sign * 0.35, -2.125, z_slat))
            gv.append(p_in - mathutils.Vector((0, 0, 0.004)))
            gv.append(p_out - mathutils.Vector((0, 0, 0.004)))
            gv.append(p_out + mathutils.Vector((0, 0, 0.004)))
            gv.append(p_in + mathutils.Vector((0, 0, 0.004)))
            b_v = slat_i * 4
            gf.append((b_v, b_v + 1, b_v + 2, b_v + 3))
        m_gr.from_pydata(gv, [], gf)
        m_gr.update()
        o_gr.data.materials.append(mat_trim)

    # Circular fog lights in lower bumper pods
    for f_name in ["Fog_Light_L", "Fog_Light_R"]:
        of = bpy.data.objects.get(f_name)
        if of:
            bpy.data.objects.remove(of, do_unlink=True)
    for f_name, s_sign in [("Fog_Light_L", -1), ("Fog_Light_R", 1)]:
        m_fog = bpy.data.meshes.new(f_name + "_Mesh")
        o_fog = bpy.data.objects.new(f_name, m_fog)
        bpy.context.collection.objects.link(o_fog)
        fv, ff = [], []
        cp_fog = mathutils.Vector((s_sign * 0.62, -2.09, 0.36))
        fv.append(cp_fog)
        for i in range(12):
            a = 2 * math.pi * i / 12
            fv.append(cp_fog + mathutils.Vector((0.038 * math.cos(a), 0.008, 0.038 * math.sin(a))))
        for i in range(12):
            ff.append((0, i + 1, (i + 1) % 12 + 1))
        m_fog.from_pydata(fv, [], ff)
        m_fog.update()
        o_fog.data.materials.append(mat_reflector)

    # Front European License plate (227 CDG 92)
    old_fp = bpy.data.objects.get("Front_License_Plate")
    if old_fp:
        bpy.data.objects.remove(old_fp, do_unlink=True)
    m_fp = bpy.data.meshes.new("Front_License_Plate_Mesh")
    o_fp = bpy.data.objects.new("Front_License_Plate", m_fp)
    bpy.context.collection.objects.link(o_fp)
    mat_plate_w = get_or_create_mat("Laguna_License_Plate_White")
    pw_bsdf = mat_plate_w.node_tree.nodes.get("Principled BSDF")
    if pw_bsdf:
        pw_bsdf.inputs['Base Color'].default_value = (0.92, 0.93, 0.95, 1.0)
        pw_bsdf.inputs['Roughness'].default_value = 0.22
    # 520mm x 110mm plate on front bumper recess
    fp_v = [
        mathutils.Vector((-0.26, -2.185, 0.455)),
        mathutils.Vector(( 0.26, -2.185, 0.455)),
        mathutils.Vector(( 0.26, -2.185, 0.510)),
        mathutils.Vector((-0.26, -2.185, 0.510))
    ]
    m_fp.from_pydata(fp_v, [], [(0, 1, 2, 3)])
    m_fp.update()
    o_fp.data.materials.append(mat_plate_w)

    # --------------------------------------------------------
    # PHASE 4: ICONIC LAGUNA II TWIN-CIRCLE TEARDROP TAILLIGHTS
    # --------------------------------------------------------
    print("[Phase 4] Modeling authentic Laguna II twin-circle teardrop taillight clusters...")
    mat_ruby = get_or_create_mat("Laguna_Taillight_Ruby")
    rb_bsdf = mat_ruby.node_tree.nodes.get("Principled BSDF")
    if rb_bsdf:
        rb_bsdf.inputs['Base Color'].default_value = (0.75, 0.03, 0.03, 1.0)
        rb_bsdf.inputs['Roughness'].default_value = 0.04
        rb_bsdf.inputs['Transmission Weight'].default_value = 0.65
        rb_bsdf.inputs['Alpha'].default_value = 0.85
        rb_bsdf.inputs['Coat Weight'].default_value = 1.0
        if 'Emission Color' in rb_bsdf.inputs:
            rb_bsdf.inputs['Emission Color'].default_value = (0.80, 0.02, 0.02, 1.0)
            rb_bsdf.inputs['Emission Strength'].default_value = 0.5

    mat_tl_clear = get_or_create_mat("Laguna_Taillight_Clear")
    tlc_bsdf = mat_tl_clear.node_tree.nodes.get("Principled BSDF")
    if tlc_bsdf:
        tlc_bsdf.inputs['Base Color'].default_value = (0.94, 0.95, 0.97, 1.0)
        tlc_bsdf.inputs['Roughness'].default_value = 0.06
        tlc_bsdf.inputs['Transmission Weight'].default_value = 0.82
        tlc_bsdf.inputs['Alpha'].default_value = 0.65

    # Remove any old taillight objects
    for tl_old in ["Taillight_Laguna2_L", "Taillight_Laguna2_R"]:
        ot = bpy.data.objects.get(tl_old)
        if ot:
            bpy.data.objects.remove(ot, do_unlink=True)

    # Rebuild authentic Laguna II taillights:
    # Outer elongated teardrop cluster with TWO circular chrome-bezel internal lamps!
    for side_name, s_sign in [("Taillight_Laguna2_L", -1), ("Taillight_Laguna2_R", 1)]:
        m_tl = bpy.data.meshes.new(side_name + "_Mesh")
        o_tl = bpy.data.objects.new(side_name, m_tl)
        bpy.context.collection.objects.link(o_tl)

        tv, tf = [], []
        # Teardrop outer housing contour:
        # Inward point near tailgate: x ~ 0.28, y ~ 2.18, z ~ 0.76
        # Outward curve on quarter panel: x ~ 0.80, y ~ 2.02, z ~ 0.77
        cluster_pts = [
            (s_sign * 0.28, 2.185, 0.760),
            (s_sign * 0.44, 2.170, 0.765),
            (s_sign * 0.62, 2.135, 0.770),
            (s_sign * 0.78, 2.050, 0.775),
            (s_sign * 0.82, 1.950, 0.780)
        ]
        h_tl = 0.090
        for px, py, pz in cluster_pts:
            tv.append(mathutils.Vector((px, py, pz - h_tl * 0.5)))
            tv.append(mathutils.Vector((px, py + 0.012, pz + h_tl * 0.5)))
        for i in range(len(cluster_pts) - 1):
            i0 = i * 2
            tf.append((i0, i0 + 2, i0 + 3, i0 + 1))

        # Circle 1: Outer circular brake lamp (center at x ~ 0.64, y ~ 2.13, z ~ 0.77), radius 0.036
        cp_c1 = mathutils.Vector((s_sign * 0.64, 2.130, 0.770))
        c1_idx = len(tv)
        tv.append(cp_c1 + mathutils.Vector((0, 0.016, 0)))
        for i in range(16):
            a = 2 * math.pi * i / 16
            tv.append(cp_c1 + mathutils.Vector((0.036 * math.cos(a), 0.012, 0.036 * math.sin(a))))
        for i in range(16):
            tf.append((c1_idx, c1_idx + 1 + i, c1_idx + 1 + (i + 1) % 16))

        # Circle 2: Inner circular reverse/indicator lamp (center at x ~ 0.42, y ~ 2.165, z ~ 0.765), radius 0.032
        cp_c2 = mathutils.Vector((s_sign * 0.42, 2.165, 0.765))
        c2_idx = len(tv)
        tv.append(cp_c2 + mathutils.Vector((0, 0.016, 0)))
        for i in range(16):
            a = 2 * math.pi * i / 16
            tv.append(cp_c2 + mathutils.Vector((0.032 * math.cos(a), 0.012, 0.032 * math.sin(a))))
        for i in range(16):
            tf.append((c2_idx, c2_idx + 1 + i, c2_idx + 1 + (i + 1) % 16))

        m_tl.from_pydata(tv, [], tf)
        m_tl.update()
        o_tl.data.materials.append(mat_ruby)       # 0: ruby red outer
        o_tl.data.materials.append(mat_chrome)     # 1: chrome bezel
        o_tl.data.materials.append(mat_tl_clear)   # 2: clear inner reverse lamp

        # Assign per-face material: outer shell = ruby, circle 1 = ruby, circle 2 = clear
        n_shell = len(cluster_pts) - 1
        for poly_idx in range(len(m_tl.polygons)):
            if poly_idx < n_shell + 16:
                m_tl.polygons[poly_idx].material_index = 0
            else:
                m_tl.polygons[poly_idx].material_index = 2

    # --------------------------------------------------------
    # PHASE 5: FACTORY BRIDGE LIP SPOILER & HIGH-MOUNT BRAKE LIGHT
    # --------------------------------------------------------
    print("[Phase 5] Modeling factory Laguna II bridge spoiler & 3rd brake light...")
    for sp_name in ["Bridge_Spoiler_Laguna2", "Third_Brake_Light"]:
        osp = bpy.data.objects.get(sp_name)
        if osp:
            bpy.data.objects.remove(osp, do_unlink=True)

    # Aerodynamic bridge spoiler blade spanning across decklid (x in [-0.74, 0.74], y ~ 2.05, z ~ 0.94)
    m_sp = bpy.data.meshes.new("Bridge_Spoiler_Laguna2_Mesh")
    o_sp = bpy.data.objects.new("Bridge_Spoiler_Laguna2", m_sp)
    bpy.context.collection.objects.link(o_sp)

    sv, sf = [], []
    # Aerodynamic blade profile: leading edge y = 2.02, trailing edge y = 2.09, z = 0.940
    sp_xs = [-0.74, -0.55, -0.30, 0.0, 0.30, 0.55, 0.74]
    for px in sp_xs:
        # Slight aerodynamic curve
        sv.append(mathutils.Vector((px, 2.020, 0.942)))
        sv.append(mathutils.Vector((px, 2.090, 0.938)))
        sv.append(mathutils.Vector((px, 2.090, 0.952)))
        sv.append(mathutils.Vector((px, 2.020, 0.954)))
    for i in range(len(sp_xs) - 1):
        i0 = i * 4
        i1 = i0 + 1
        i2 = i0 + 2
        i3 = i0 + 3
        j0 = (i + 1) * 4
        j1 = j0 + 1
        j2 = j0 + 2
        j3 = j0 + 3
        sf.append((i0, j0, j1, i1)) # bottom
        sf.append((i3, i2, j2, j3)) # top
        sf.append((i0, i3, j3, j0)) # front
        sf.append((i1, j1, j2, i2)) # rear

    # Two side mounting pedestals connecting spoiler to decklid at x ~ +-0.60
    for ped_x in [-0.60, 0.60]:
        base_idx = len(sv)
        sv.append(mathutils.Vector((ped_x - 0.025, 2.040, 0.900)))
        sv.append(mathutils.Vector((ped_x + 0.025, 2.040, 0.900)))
        sv.append(mathutils.Vector((ped_x + 0.025, 2.070, 0.900)))
        sv.append(mathutils.Vector((ped_x - 0.025, 2.070, 0.900)))
        sv.append(mathutils.Vector((ped_x - 0.025, 2.040, 0.940)))
        sv.append(mathutils.Vector((ped_x + 0.025, 2.040, 0.940)))
        sv.append(mathutils.Vector((ped_x + 0.025, 2.070, 0.940)))
        sv.append(mathutils.Vector((ped_x - 0.025, 2.070, 0.940)))
        sf.append((base_idx, base_idx + 1, base_idx + 5, base_idx + 4))
        sf.append((base_idx + 1, base_idx + 2, base_idx + 6, base_idx + 5))
        sf.append((base_idx + 2, base_idx + 3, base_idx + 7, base_idx + 6))
        sf.append((base_idx + 3, base_idx + 0, base_idx + 4, base_idx + 7))

    m_sp.from_pydata(sv, [], sf)
    m_sp.update()
    o_sp.data.materials.append(mat_paint)

    # Red LED 3rd Brake Light centered directly underneath the bridge spoiler on the decklid edge
    m_3b = bpy.data.meshes.new("Third_Brake_Light_Mesh")
    o_3b = bpy.data.objects.new("Third_Brake_Light", m_3b)
    bpy.context.collection.objects.link(o_3b)
    b3_w = 0.18 # 36cm wide
    b3_v = [
        mathutils.Vector((-b3_w, 2.070, 0.910)),
        mathutils.Vector(( b3_w, 2.070, 0.910)),
        mathutils.Vector(( b3_w, 2.070, 0.925)),
        mathutils.Vector((-b3_w, 2.070, 0.925))
    ]
    m_3b.from_pydata(b3_v, [], [(0, 1, 2, 3)])
    m_3b.update()
    o_3b.data.materials.append(mat_ruby)

    # --------------------------------------------------------
    # PHASE 6: TAILGATE UPRIGHT DIAMOND PLAQUE & YELLOW ALGERIAN PLATE
    # --------------------------------------------------------
    print("[Phase 6] Modeling upright Renault diamond plaque and yellow license plate (08976 102 44)...")
    old_rd = bpy.data.objects.get("Rear_Renault_Diamond")
    if old_rd:
        bpy.data.objects.remove(old_rd, do_unlink=True)
    m_rd = bpy.data.meshes.new("Rear_Renault_Diamond_Mesh")
    o_rd = bpy.data.objects.new("Rear_Renault_Diamond", m_rd)
    bpy.context.collection.objects.link(o_rd)

    # Stylized silver trapezoidal plaque behind diamond (matching media_1794832234562_fa418d5b.jpg)
    rd_v, rd_f = [], []
    c_plaque = mathutils.Vector((0.0, 2.185, 0.810))
    # Plaque backing: width ~ 0.08, height ~ 0.11
    rd_v.append(c_plaque + mathutils.Vector((-0.038, 0.003, -0.050)))
    rd_v.append(c_plaque + mathutils.Vector(( 0.038, 0.003, -0.050)))
    rd_v.append(c_plaque + mathutils.Vector(( 0.042, 0.003,  0.050)))
    rd_v.append(c_plaque + mathutils.Vector((-0.042, 0.003,  0.050)))
    rd_f.append((0, 1, 2, 3))

    # Chrome Diamond on plaque
    d_base = len(rd_v)
    ry, rz = 0.024, 0.040
    rd_v.append(c_plaque + mathutils.Vector((0, 0.010, rz)))
    rd_v.append(c_plaque + mathutils.Vector((ry, 0.008, 0)))
    rd_v.append(c_plaque + mathutils.Vector((0, 0.010, -rz)))
    rd_v.append(c_plaque + mathutils.Vector((-ry, 0.008, 0)))
    rd_v.append(c_plaque + mathutils.Vector((0, 0.016, 0))) # central peak
    rd_f.append((d_base, d_base + 1, d_base + 4))
    rd_f.append((d_base + 1, d_base + 2, d_base + 4))
    rd_f.append((d_base + 2, d_base + 3, d_base + 4))
    rd_f.append((d_base + 3, d_base, d_base + 4))

    m_rd.from_pydata(rd_v, [], rd_f)
    m_rd.update()
    o_rd.data.materials.append(mat_chrome)

    # Recessed Yellow License Plate (08976 102 44) matching media_1794832234562_fa418d5b.jpg
    old_lp = bpy.data.objects.get("License_Plate")
    if old_lp:
        bpy.data.objects.remove(old_lp, do_unlink=True)
    m_lp = bpy.data.meshes.new("License_Plate_Mesh")
    o_lp = bpy.data.objects.new("License_Plate", m_lp)
    bpy.context.collection.objects.link(o_lp)

    mat_plate_y = get_or_create_mat("Laguna_License_Plate_Yellow")
    py_bsdf = mat_plate_y.node_tree.nodes.get("Principled BSDF")
    if py_bsdf:
        # Authentic yellow registration plate color
        py_bsdf.inputs['Base Color'].default_value = (0.92, 0.65, 0.05, 1.0)
        py_bsdf.inputs['Roughness'].default_value = 0.25
        py_bsdf.inputs['Coat Weight'].default_value = 0.80

    # 520mm x 110mm European/Algerian plate recessed in bumper center
    pw, ph = 0.26, 0.055
    lp_v = [
        mathutils.Vector((-pw, 2.185, 0.620 - ph)),
        mathutils.Vector(( pw, 2.185, 0.620 - ph)),
        mathutils.Vector(( pw, 2.185, 0.620 + ph)),
        mathutils.Vector((-pw, 2.185, 0.620 + ph))
    ]
    m_lp.from_pydata(lp_v, [], [(0, 1, 2, 3)])
    m_lp.update()
    o_lp.data.materials.append(mat_plate_y)

    # --------------------------------------------------------
    # PHASE 7: FASTBACK SOLARGLASS, ROOF ANTENNA & PARCEL SHELF
    # --------------------------------------------------------
    print("[Phase 7] Refining Solarglass tint, roof antenna, and rear parcel shelf...")
    mat_solar = get_or_create_mat("Laguna_Factory_Solarglass")
    sg_bsdf = mat_solar.node_tree.nodes.get("Principled BSDF")
    if sg_bsdf:
        sg_bsdf.inputs['Base Color'].default_value = (0.84, 0.93, 0.89, 1.0)
        sg_bsdf.inputs['Roughness'].default_value = 0.015
        sg_bsdf.inputs['Transmission Weight'].default_value = 0.75
        sg_bsdf.inputs['Alpha'].default_value = 0.50
        sg_bsdf.inputs['IOR'].default_value = 1.52
        sg_bsdf.inputs['Coat Weight'].default_value = 1.0
        sg_bsdf.inputs['Coat Roughness'].default_value = 0.005

    for g_name in ['unnamed.021', 'unnamed.027']:
        og = bpy.data.objects.get(g_name)
        if og:
            og.hide_render = False
            og.hide_viewport = False
            og.data.materials.clear()
            og.data.materials.append(mat_solar)

    # Black center roof antenna
    old_ant = bpy.data.objects.get("Roof_Antenna")
    if old_ant:
        bpy.data.objects.remove(old_ant, do_unlink=True)
    m_ant = bpy.data.meshes.new("Roof_Antenna_Mesh")
    o_ant = bpy.data.objects.new("Roof_Antenna", m_ant)
    bpy.context.collection.objects.link(o_ant)
    mat_black = get_or_create_mat("Laguna_Pillar_Black")
    # Base at (0, 0.98, 1.42), whip angling back to (0, 1.15, 1.50)
    ant_v = [
        mathutils.Vector((-0.015, 0.96, 1.415)),
        mathutils.Vector(( 0.015, 0.96, 1.415)),
        mathutils.Vector(( 0.015, 1.02, 1.415)),
        mathutils.Vector((-0.015, 1.02, 1.415)),
        mathutils.Vector(( 0.000, 1.16, 1.520)) # whip tip
    ]
    ant_f = [(0, 1, 2, 3), (0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)]
    m_ant.from_pydata(ant_v, [], ant_f)
    m_ant.update()
    o_ant.data.materials.append(mat_black)

    # Carpeted rear parcel shelf
    old_shelf = bpy.data.objects.get("Parcel_Shelf")
    if old_shelf:
        bpy.data.objects.remove(old_shelf, do_unlink=True)
    m_sh = bpy.data.meshes.new("Parcel_Shelf_Mesh")
    o_sh = bpy.data.objects.new("Parcel_Shelf", m_sh)
    bpy.context.collection.objects.link(o_sh)
    mat_interior = get_or_create_mat("Laguna_Interior_Charcoal")
    sh_v = [
        mathutils.Vector((-0.58, 1.05, 0.89)),
        mathutils.Vector(( 0.58, 1.05, 0.89)),
        mathutils.Vector(( 0.58, 1.94, 0.89)),
        mathutils.Vector((-0.58, 1.94, 0.89))
    ]
    m_sh.from_pydata(sh_v, [], [(0, 1, 2, 3)])
    m_sh.update()
    o_sh.data.materials.append(mat_interior)

    # Horizontal rear liftback wiper parked along bottom edge of rear glass
    old_rw = bpy.data.objects.get("Rear_Wiper")
    if old_rw:
        bpy.data.objects.remove(old_rw, do_unlink=True)
    m_rw = bpy.data.meshes.new("Rear_Wiper_Mesh")
    o_rw = bpy.data.objects.new("Rear_Wiper", m_rw)
    bpy.context.collection.objects.link(o_rw)
    # Pivot near motor (0.24, 1.88, 0.98), blade parked horizontally across (x from -0.22 to 0.24, y ~ 1.88, z ~ 0.98)
    rw_v = [
        mathutils.Vector((-0.24, 1.875, 0.985)),
        mathutils.Vector(( 0.24, 1.875, 0.985)),
        mathutils.Vector(( 0.24, 1.875, 0.995)),
        mathutils.Vector((-0.24, 1.875, 0.995))
    ]
    m_rw.from_pydata(rw_v, [], [(0, 1, 2, 3)])
    m_rw.update()
    o_rw.data.materials.append(mat_black)

    # --------------------------------------------------------
    # PHASE 8: FLANK DETAILS — DOOR MOULDINGS, HANDLES & REPEATERS
    # --------------------------------------------------------
    print("[Phase 8] Refining continuous door rub strips, pull handles & amber side repeaters...")
    # Clean continuous 3D door mouldings along flanks
    moulding_coords = [
        ("Moulding_Door_FR",  0.880, -0.65, 0.05, 0.55, 0.68),
        ("Moulding_Door_FL", -0.880, -0.65, 0.05, 0.55, 0.68),
        ("Moulding_Door_RR",  0.875,  0.10, 0.82, 0.55, 0.70),
        ("Moulding_Door_RL", -0.875,  0.10, 0.82, 0.55, 0.70)
    ]
    h_mould = 0.024
    for m_name, mx, y_start, y_end, mz, length in moulding_coords:
        old_m = bpy.data.objects.get(m_name)
        if old_m:
            bpy.data.objects.remove(old_m, do_unlink=True)
        m_mesh = bpy.data.meshes.new(m_name + "_Mesh")
        o_m = bpy.data.objects.new(m_name, m_mesh)
        bpy.context.collection.objects.link(o_m)
        s_dir = 1 if mx > 0 else -1
        mv = [
            mathutils.Vector((mx, y_start, mz - h_mould)),
            mathutils.Vector((mx + s_dir * 0.012, y_start + 0.01, mz - h_mould * 0.7)),
            mathutils.Vector((mx + s_dir * 0.012, y_start + 0.01, mz + h_mould * 0.7)),
            mathutils.Vector((mx, y_start, mz + h_mould)),
            mathutils.Vector((mx, y_end, mz - h_mould)),
            mathutils.Vector((mx + s_dir * 0.012, y_end - 0.01, mz - h_mould * 0.7)),
            mathutils.Vector((mx + s_dir * 0.012, y_end - 0.01, mz + h_mould * 0.7)),
            mathutils.Vector((mx, y_end, mz + h_mould))
        ]
        mf = [
            (0, 1, 2, 3), (4, 7, 6, 5),
            (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)
        ]
        m_mesh.from_pydata(mv, [], mf)
        m_mesh.update()
        o_m.data.materials.append(mat_trim)

    # Amber side repeaters on front fenders
    for r_name in ["Side_Repeater_L", "Side_Repeater_R"]:
        old_r = bpy.data.objects.get(r_name)
        if old_r:
            bpy.data.objects.remove(old_r, do_unlink=True)
    for r_name, s_sign in [("Side_Repeater_L", -1), ("Side_Repeater_R", 1)]:
        m_sr = bpy.data.meshes.new(r_name + "_Mesh")
        o_sr = bpy.data.objects.new(r_name, m_sr)
        bpy.context.collection.objects.link(o_sr)
        cp_rep = mathutils.Vector((s_sign * 0.885, -1.05, 0.62))
        srv, srf = [], []
        # Oval repeater: 0.035m long, 0.018m tall
        srv.append(cp_rep + mathutils.Vector((s_sign * 0.005, 0, 0)))
        for i in range(12):
            a = 2 * math.pi * i / 12
            srv.append(cp_rep + mathutils.Vector((0, 0.018 * math.cos(a), 0.010 * math.sin(a))))
        for i in range(12):
            srf.append((0, i + 1, (i + 1) % 12 + 1))
        m_sr.from_pydata(srv, [], srf)
        m_sr.update()
        o_sr.data.materials.append(mat_amber)

    # --------------------------------------------------------
    # PHASE 9: AUTHENTIC 17" RENAULT "SILVERSTONE" ALLOY WHEELS
    # --------------------------------------------------------
    print("[Phase 9] Modeling genuine 17\" Renault Silverstone 17-spoke alloy wheels...")
    mat_alloy = get_or_create_mat("Laguna_Factory_Alloy")
    al_bsdf = mat_alloy.node_tree.nodes.get("Principled BSDF")
    if al_bsdf:
        # Polished metallic silver alloy
        al_bsdf.inputs['Base Color'].default_value = (0.78, 0.79, 0.81, 1.0)
        al_bsdf.inputs['Metallic'].default_value = 0.55
        al_bsdf.inputs['Roughness'].default_value = 0.18
        al_bsdf.inputs['Coat Weight'].default_value = 0.60
        al_bsdf.inputs['Coat Roughness'].default_value = 0.08

    mat_cavity = get_or_create_mat("Laguna_Wheel_Cavity")
    c_bsdf = mat_cavity.node_tree.nodes.get("Principled BSDF")
    if c_bsdf:
        c_bsdf.inputs['Base Color'].default_value = (0.015, 0.015, 0.018, 1.0)
        c_bsdf.inputs['Metallic'].default_value = 0.05
        c_bsdf.inputs['Roughness'].default_value = 0.85

    for w_name in ["Wheel_Cap_FL", "Wheel_Cap_FR", "Wheel_Cap_RL", "Wheel_Cap_RR"]:
        ow = bpy.data.objects.get(w_name)
        if ow:
            bpy.data.objects.remove(ow, do_unlink=True)

    wheel_locs = [
        ("Wheel_Cap_FR",  0.865, -1.34, 0.32,  1),
        ("Wheel_Cap_FL", -0.865, -1.34, 0.32, -1),
        ("Wheel_Cap_RR",  0.855,  1.32, 0.32,  1),
        ("Wheel_Cap_RL", -0.855,  1.32, 0.32, -1)
    ]

    for name, wx, wy, wz, side in wheel_locs:
        m_w = bpy.data.meshes.new(name + "_Mesh")
        o_w = bpy.data.objects.new(name, m_w)
        bpy.context.collection.objects.link(o_w)

        wv, wf = [], []
        m_slots = []
        cp = mathutils.Vector((wx + side * 0.024, wy, wz))

        # 1. Dark backing disc at radius 0.245m (completely covers tire cavity)
        b_c = len(wv)
        wv.append(cp - mathutils.Vector((side * 0.018, 0, 0)))
        n_pts = 34
        b_ring = len(wv)
        for i in range(n_pts):
            a = 2 * math.pi * i / n_pts
            wv.append(cp - mathutils.Vector((side * 0.018, 0, 0)) + mathutils.Vector((0, 0.245 * math.cos(a), 0.245 * math.sin(a))))
        for i in range(n_pts):
            f_idx = len(wf)
            wf.append((b_c, b_ring + i, b_ring + (i + 1) % n_pts))
            m_slots.append((f_idx, 2)) # cavity

        # 2. Outer silver rim flange (radius 0.200 to 0.218)
        rim_start = len(wv)
        for i in range(n_pts):
            a = 2 * math.pi * i / n_pts
            wv.append(cp + mathutils.Vector((0, 0.198 * math.cos(a), 0.198 * math.sin(a))))
            wv.append(cp + mathutils.Vector((0, 0.218 * math.cos(a), 0.218 * math.sin(a))))
        for i in range(n_pts):
            i0 = rim_start + i * 2
            i1 = i0 + 1
            next_i = (i + 1) % n_pts
            i2 = rim_start + next_i * 2 + 1
            i3 = rim_start + next_i * 2
            f_idx = len(wf)
            wf.append((i0, i1, i2, i3))
            m_slots.append((f_idx, 0)) # silver alloy

        # 3. Inner Hub (radius 0.065 m) with 5 lug nut recesses
        hub_c = len(wv)
        wv.append(cp + mathutils.Vector((side * 0.006, 0, 0)))
        n_spokes = 17 # Iconic 17-spoke Silverstone design!
        n_hub_pts = n_spokes * 2 # 34 points
        hub_ring = len(wv)
        for i in range(n_hub_pts):
            a = 2 * math.pi * i / n_hub_pts
            wv.append(cp + mathutils.Vector((side * 0.003, 0.065 * math.cos(a), 0.065 * math.sin(a))))
        for i in range(n_hub_pts):
            f_idx = len(wf)
            wf.append((hub_c, hub_ring + i, hub_ring + (i + 1) % n_hub_pts))
            m_slots.append((f_idx, 0)) # silver alloy

        # 4. Seventeen thin, sculpted silver radiating spokes
        for s in range(n_spokes):
            h_i0 = hub_ring + s * 2
            h_i1 = hub_ring + s * 2 + 1
            r_i0 = rim_start + (s * 2) * 2
            r_i1 = rim_start + (s * 2 + 1) * 2
            f_idx = len(wf)
            wf.append((h_i0, h_i1, r_i1, r_i0))
            m_slots.append((f_idx, 0)) # silver alloy

        # 5. Center Polished Chrome Renault Diamond
        d_start = len(wv)
        dx = cp.x + side * 0.009
        sy, sz = 0.015, 0.024
        wv.append(mathutils.Vector((dx, cp.y, cp.z + sz)))
        wv.append(mathutils.Vector((dx, cp.y + sy, cp.z)))
        wv.append(mathutils.Vector((dx, cp.y, cp.z - sz)))
        wv.append(mathutils.Vector((dx, cp.y - sy, cp.z)))
        f_idx = len(wf)
        wf.append((d_start, d_start + 1, d_start + 2, d_start + 3))
        m_slots.append((f_idx, 1)) # chrome

        m_w.from_pydata(wv, [], wf)
        m_w.update()
        o_w.data.materials.append(mat_alloy)
        o_w.data.materials.append(mat_chrome)
        o_w.data.materials.append(mat_cavity)
        for f_idx, mat_id in m_slots:
            if f_idx < len(m_w.polygons):
                m_w.polygons[f_idx].material_index = mat_id

    # --------------------------------------------------------
    # PHASE 10: SATIN MATTE PAINT, HDR OUTDOOR STAGING & 1080P RENDERS
    # --------------------------------------------------------
    print("[Phase 10] Finalizing outdoor HDR lighting, camera angles & rendering 1080p images...")
    world = scene.world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    node_env = nt.nodes.new('ShaderNodeTexEnvironment')
    node_env.image = bpy.data.images.load(HDR_PATH)
    node_bg = nt.nodes.new('ShaderNodeBackground')
    node_bg.inputs['Strength'].default_value = 1.05
    node_out = nt.nodes.new('ShaderNodeOutputWorld')
    nt.links.new(node_env.outputs['Color'], node_bg.inputs['Color'])
    nt.links.new(node_bg.outputs['Background'], node_out.inputs['Surface'])

    # Asphalt pavement plane below vehicle for realistic grounding & ambient contact shadows
    old_pave = bpy.data.objects.get("Studio_Pavement")
    if not old_pave:
        bpy.ops.mesh.primitive_plane_add(size=30.0, location=(0, 0, 0.0))
        pave = bpy.context.active_object
        pave.name = "Studio_Pavement"
        mat_asphalt = get_or_create_mat("Laguna_Road_Asphalt")
        pave.data.materials.append(mat_asphalt)

    # AgX Color Management with neutral exposure
    scene.view_settings.view_transform = 'AgX'
    try:
        scene.view_settings.look = 'AgX - Medium High Contrast'
    except Exception:
        pass
    scene.view_settings.exposure = -0.05

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
    cam.location = mathutils.Vector((-4.30, -4.40, 1.20))
    target_front = mathutils.Vector((0.0, -0.60, 0.58))
    cam.rotation_euler = (target_front - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    scene.render.filepath = out_front
    bpy.ops.render.render(write_still=True)

    # Rear Angle matching media_1794832234562_fa418d5b.jpg
    print("[Phase 10] Rendering Rear validation angle...")
    cam.location = mathutils.Vector((0.00, 4.80, 0.85)) # Direct rear view matching the photo!
    target_rear = mathutils.Vector((0.0, 0.00, 0.72))
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
    print("10-PHASE PURE LAGUNA II REBUILD COMPLETED SUCCESSFULLY!")
    print("==========================================================")

if __name__ == "__main__":
    build_laguna2()
