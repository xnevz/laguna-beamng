"""
Precise shader mapping for authentic tinted glass and correct headlights/taillights
"""

import bpy
import mathutils
import math
import os
import shutil

def apply_tint_and_lights():
    print("[Shaders] Applying dark automotive glass tint and correct front/rear lights...")

    # 1. SHADER DEFINITIONS
    def get_or_create(name):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        return mat

    # A) Sleek Dark Tinted Glass (Limo / Sport Tint)
    mat_tinted_glass = get_or_create("Laguna_Dark_Tint_Glass")
    bsdf_g = mat_tinted_glass.node_tree.nodes.get("Principled BSDF")
    if bsdf_g:
        bsdf_g.inputs['Base Color'].default_value = (0.015, 0.02, 0.025, 1.0) # Deep charcoal smoke
        bsdf_g.inputs['Metallic'].default_value = 0.25 # Sleek metallic sheen
        bsdf_g.inputs['Roughness'].default_value = 0.02 # High-gloss reflection of studio softbox
        bsdf_g.inputs['Alpha'].default_value = 0.70   # Strong dark privacy tint
        bsdf_g.inputs['IOR'].default_value = 1.55
    mat_tinted_glass.blend_method = 'BLEND'

    # B) Front Headlights: Crystal Clear Glass Lens
    mat_hl_lens = get_or_create("Laguna_Headlight_Glass")
    bsdf_hl = mat_hl_lens.node_tree.nodes.get("Principled BSDF")
    if bsdf_hl:
        bsdf_hl.inputs['Base Color'].default_value = (0.95, 0.98, 1.0, 1.0)
        bsdf_hl.inputs['Metallic'].default_value = 0.2
        bsdf_hl.inputs['Roughness'].default_value = 0.01
        bsdf_hl.inputs['Alpha'].default_value = 0.35 # Pure transparent clear glass
        bsdf_hl.inputs['IOR'].default_value = 1.48
    mat_hl_lens.blend_method = 'BLEND'

    # C) Front Headlights: Chrome Mirrored Reflector Bowls
    mat_hl_chrome = get_or_create("Laguna_Headlight_Chrome")
    bsdf_ch = mat_hl_chrome.node_tree.nodes.get("Principled BSDF")
    if bsdf_ch:
        bsdf_ch.inputs['Base Color'].default_value = (0.98, 0.98, 1.0, 1.0)
        bsdf_ch.inputs['Metallic'].default_value = 1.0
        bsdf_ch.inputs['Roughness'].default_value = 0.02

    # D) Rear Taillights: Deep Ruby Red Translucent
    mat_tl_red = get_or_create("Laguna_Taillight_Ruby")
    bsdf_tr = mat_tl_red.node_tree.nodes.get("Principled BSDF")
    if bsdf_tr:
        bsdf_tr.inputs['Base Color'].default_value = (0.85, 0.01, 0.01, 1.0) # Deep saturated red
        bsdf_tr.inputs['Metallic'].default_value = 0.1
        bsdf_tr.inputs['Roughness'].default_value = 0.06
        bsdf_tr.inputs['Alpha'].default_value = 0.85 # Translucent red lens
        bsdf_tr.inputs['IOR'].default_value = 1.50
    mat_tl_red.blend_method = 'BLEND'

    # E) Rear Taillights: Clear / Amber Accents
    mat_tl_white = get_or_create("Laguna_Taillight_Clear")
    bsdf_tw = mat_tl_white.node_tree.nodes.get("Principled BSDF")
    if bsdf_tw:
        bsdf_tw.inputs['Base Color'].default_value = (0.95, 0.95, 0.98, 1.0)
        bsdf_tw.inputs['Metallic'].default_value = 0.1
        bsdf_tw.inputs['Roughness'].default_value = 0.05
        bsdf_tw.inputs['Alpha'].default_value = 0.60
    mat_tl_white.blend_method = 'BLEND'

    # F) Car Paint (Deep Metallic Renault Sport Blue)
    mat_paint = get_or_create("Laguna_Sport_Blue")
    bsdf_paint = mat_paint.node_tree.nodes.get("Principled BSDF")
    if bsdf_paint:
        bsdf_paint.inputs['Base Color'].default_value = (0.02, 0.10, 0.50, 1.0)
        bsdf_paint.inputs['Metallic'].default_value = 0.88
        bsdf_paint.inputs['Roughness'].default_value = 0.18

    # G) Wheels (Tires & Rims)
    mat_tire = get_or_create("Laguna_Tire")
    bsdf_tire = mat_tire.node_tree.nodes.get("Principled BSDF")
    if bsdf_tire:
        bsdf_tire.inputs['Base Color'].default_value = (0.02, 0.02, 0.025, 1.0)
        bsdf_tire.inputs['Roughness'].default_value = 0.85

    mat_rim = get_or_create("Laguna_Rim")
    bsdf_rim = mat_rim.node_tree.nodes.get("Principled BSDF")
    if bsdf_rim:
        bsdf_rim.inputs['Base Color'].default_value = (0.92, 0.93, 0.95, 1.0)
        bsdf_rim.inputs['Metallic'].default_value = 0.85
        bsdf_rim.inputs['Roughness'].default_value = 0.15

    # H) Black Trim
    mat_trim = get_or_create("Laguna_Trim_Black")
    bsdf_trim = mat_trim.node_tree.nodes.get("Principled BSDF")
    if bsdf_trim:
        bsdf_trim.inputs['Base Color'].default_value = (0.03, 0.03, 0.035, 1.0)
        bsdf_trim.inputs['Roughness'].default_value = 0.70

    # 2. SCAN AND ASSIGN ALL MESH OBJECTS
    objs = [o for o in bpy.data.objects if o.type == 'MESH' and not o.name.startswith("Studio_") and not o.name.startswith("Ref_")]

    for o in objs:
        verts = [o.matrix_world @ v.co for v in o.data.vertices]
        if not verts:
            continue
        cx = sum(v.x for v in verts) / len(verts)
        cy = sum(v.y for v in verts) / len(verts)
        cz = sum(v.z for v in verts) / len(verts)
        dx = max(v.x for v in verts) - min(v.x for v in verts)
        dy = max(v.y for v in verts) - min(v.y for v in verts)
        dz = max(v.z for v in verts) - min(v.z for v in verts)

        o.data.materials.clear()

        # A) Wheels & Tires (Z < 0.45m and |X| > 0.60m)
        if cz < 0.45 and abs(cx) > 0.60:
            if max(dy, dz) > 0.45 and dx > 0.15:
                o.data.materials.append(mat_tire)
            else:
                o.data.materials.append(mat_rim)

        # B) FRONT HEADLIGHTS (Y > 1.80m, Z between 0.48m and 0.85m, |X| > 0.35m or spanning front)
        elif cy > 1.80 and 0.48 < cz < 0.85:
            # Outer glass lens vs chrome reflector:
            if dy < 0.12 or dz < 0.20:
                o.data.materials.append(mat_hl_lens)
            else:
                o.data.materials.append(mat_hl_chrome)

        # C) REAR TAILLIGHTS (Y < -1.80m, Z between 0.45m and 0.85m)
        elif cy < -1.80 and 0.45 < cz < 0.85:
            # Center reverse lamp or main red taillight:
            if o.name in ['unnamed.013', 'unnamed.014', 'unnamed.012']:
                o.data.materials.append(mat_tl_white)
            else:
                o.data.materials.append(mat_tl_red)

        # D) ALL CABIN WINDOWS & TINTED GLASS
        # Any surface in cabin greenhouse area (Z > 0.78m, -1.8m < Y < 1.7m) that is thin glass
        elif cz > 0.78 and -1.8 < cy < 1.7 and (
            o.name in [
                'unnamed.021', 'unnamed.022', 'unnamed.023', 'unnamed.027', 'unnamed.029', 'unnamed.030',
                'unnamed.150', 'unnamed.152', 'unnamed.155', 'unnamed.163', 'unnamed.164', 'unnamed.190',
                'unnamed.196', 'unnamed.199', 'unnamed.213', 'unnamed.214', 'unnamed.216', 'unnamed.219',
                'unnamed.237', 'unnamed.238', 'unnamed.241', 'unnamed.247',
                'unnamed.058', 'unnamed.059', 'unnamed.060', 'unnamed.064', 'unnamed.065', 'unnamed.066'
            ] or (dx > 0.6 and dy > 0.4 and dz < 0.65 and cz > 0.85)
        ):
            o.data.materials.append(mat_tinted_glass)

        # E) Aerodynamic Splitter & Underbody (Z < 0.12m)
        elif cz < 0.12:
            o.data.materials.append(mat_trim)

        # F) Main Painted Body Panels
        else:
            o.data.materials.append(mat_paint)

    print("[Shaders] Assigned tinted glass and headlights/taillights successfully!")

    # 3. RENDER FRONT 3/4 & REAR 3/4
    scene = bpy.context.scene
    cam = scene.camera
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080

    out_front = os.path.abspath(r"c:\Users\abdelkarim\Documents\laguna-beamng\laguna_front.png")
    out_rear = os.path.abspath(r"c:\Users\abdelkarim\Documents\laguna-beamng\laguna_rear.png")
    out_pres = os.path.abspath(r"c:\Users\abdelkarim\Documents\laguna-beamng\laguna_presentation.png")

    # Front 3/4 Camera (aimed at front corner Y = +0.5m)
    cam.location = mathutils.Vector((-4.3, 4.2, 1.40))
    target_front = mathutils.Vector((0.0, 0.4, 0.60))
    cam.rotation_euler = (target_front - cam.location).to_track_quat('-Z', 'Y').to_euler()

    print("[Render] Rendering Front 3/4 (Headlights, Grille, Tinted Windshield)...")
    scene.render.filepath = out_front
    bpy.ops.render.render(write_still=True)
    shutil.copyfile(out_front, out_pres)

    # Rear 3/4 Camera (aimed at rear corner Y = -0.5m)
    cam.location = mathutils.Vector((-4.3, -4.2, 1.40))
    target_rear = mathutils.Vector((0.0, -0.4, 0.60))
    cam.rotation_euler = (target_rear - cam.location).to_track_quat('-Z', 'Y').to_euler()

    print("[Render] Rendering Rear 3/4 (Ruby Red Taillights, Rear Tinted Window, Spoiler)...")
    scene.render.filepath = out_rear
    bpy.ops.render.render(write_still=True)

    # Copy to artifact folder
    artifact_dir = r"C:\Users\abdelkarim\.gemini\antigravity\brain\fa1588ad-d9ab-4eb3-9303-e3e476714ebd"
    if os.path.exists(artifact_dir):
        shutil.copyfile(out_front, os.path.join(artifact_dir, "laguna_front.png"))
        shutil.copyfile(out_front, os.path.join(artifact_dir, "laguna_presentation.png"))
        shutil.copyfile(out_rear, os.path.join(artifact_dir, "laguna_rear.png"))
        print("[Render] Updated artifact images.")

if __name__ == "__main__":
    apply_tint_and_lights()
