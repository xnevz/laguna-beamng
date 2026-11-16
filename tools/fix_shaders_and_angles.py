"""
Fix orientation of headlights, taillights, tinted glass, and camera angles.
Front is at -Y, Rear is at +Y.
"""

import bpy
import mathutils
import math
import os
import shutil

def fix_all_shaders():
    print("[Shaders] Re-mapping front/rear lights and uniform window tint...")

    def make_material(name):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        return mat

    # 1. SHADERS
    # A) Dark Automotive Window Tint (Sleek, glossy, privacy dark)
    mat_tint = make_material("Laguna_Dark_Tint_Glass")
    bsdf_t = mat_tint.node_tree.nodes.get("Principled BSDF")
    if bsdf_t:
        bsdf_t.inputs['Base Color'].default_value = (0.015, 0.018, 0.022, 1.0)
        bsdf_t.inputs['Metallic'].default_value = 0.35 # Glossy reflective surface
        bsdf_t.inputs['Roughness'].default_value = 0.01 # Mirror-like reflections
        bsdf_t.inputs['Alpha'].default_value = 0.75   # Dark tint
        bsdf_t.inputs['IOR'].default_value = 1.55
    mat_tint.blend_method = 'BLEND'

    # B) Front Headlights: Crystal Clear Glass
    mat_hl_lens = make_material("Laguna_Headlight_Glass")
    bsdf_hl = mat_hl_lens.node_tree.nodes.get("Principled BSDF")
    if bsdf_hl:
        bsdf_hl.inputs['Base Color'].default_value = (0.95, 0.98, 1.0, 1.0)
        bsdf_hl.inputs['Metallic'].default_value = 0.1
        bsdf_hl.inputs['Roughness'].default_value = 0.01
        bsdf_hl.inputs['Alpha'].default_value = 0.30
        bsdf_hl.inputs['IOR'].default_value = 1.48
    mat_hl_lens.blend_method = 'BLEND'

    # C) Front Headlights: Mirrored Chrome Reflector Bowls
    mat_hl_chrome = make_material("Laguna_Headlight_Chrome")
    bsdf_ch = mat_hl_chrome.node_tree.nodes.get("Principled BSDF")
    if bsdf_ch:
        bsdf_ch.inputs['Base Color'].default_value = (0.98, 0.98, 1.0, 1.0)
        bsdf_ch.inputs['Metallic'].default_value = 1.0
        bsdf_ch.inputs['Roughness'].default_value = 0.02

    # D) Rear Taillights: Deep Ruby Red Lens
    mat_tl_ruby = make_material("Laguna_Taillight_Ruby")
    bsdf_tr = mat_tl_ruby.node_tree.nodes.get("Principled BSDF")
    if bsdf_tr:
        bsdf_tr.inputs['Base Color'].default_value = (0.85, 0.01, 0.01, 1.0)
        bsdf_tr.inputs['Metallic'].default_value = 0.1
        bsdf_tr.inputs['Roughness'].default_value = 0.04
        bsdf_tr.inputs['Alpha'].default_value = 0.85
        bsdf_tr.inputs['IOR'].default_value = 1.50
    mat_tl_ruby.blend_method = 'BLEND'

    # E) Rear Taillights: Clear Reverse Lamp
    mat_tl_clear = make_material("Laguna_Taillight_Clear")
    bsdf_tw = mat_tl_clear.node_tree.nodes.get("Principled BSDF")
    if bsdf_tw:
        bsdf_tw.inputs['Base Color'].default_value = (0.95, 0.95, 0.98, 1.0)
        bsdf_tw.inputs['Metallic'].default_value = 0.1
        bsdf_tw.inputs['Roughness'].default_value = 0.04
        bsdf_tw.inputs['Alpha'].default_value = 0.50
    mat_tl_clear.blend_method = 'BLEND'

    # F) Car Paint
    mat_paint = make_material("Laguna_Sport_Blue")
    bsdf_p = mat_paint.node_tree.nodes.get("Principled BSDF")
    if bsdf_p:
        bsdf_p.inputs['Base Color'].default_value = (0.02, 0.10, 0.50, 1.0)
        bsdf_p.inputs['Metallic'].default_value = 0.88
        bsdf_p.inputs['Roughness'].default_value = 0.18

    # G) Wheels
    mat_tire = make_material("Laguna_Tire")
    bsdf_ti = mat_tire.node_tree.nodes.get("Principled BSDF")
    if bsdf_ti:
        bsdf_ti.inputs['Base Color'].default_value = (0.02, 0.02, 0.025, 1.0)
        bsdf_ti.inputs['Roughness'].default_value = 0.85

    mat_rim = make_material("Laguna_Rim")
    bsdf_ri = mat_rim.node_tree.nodes.get("Principled BSDF")
    if bsdf_ri:
        bsdf_ri.inputs['Base Color'].default_value = (0.92, 0.93, 0.95, 1.0)
        bsdf_ri.inputs['Metallic'].default_value = 0.85
        bsdf_ri.inputs['Roughness'].default_value = 0.15

    # H) Black Trim
    mat_trim = make_material("Laguna_Trim_Black")
    bsdf_tr = mat_trim.node_tree.nodes.get("Principled BSDF")
    if bsdf_tr:
        bsdf_tr.inputs['Base Color'].default_value = (0.03, 0.03, 0.035, 1.0)
        bsdf_tr.inputs['Roughness'].default_value = 0.70

    # 2. SCAN AND ASSIGN WITH TRUE AXIS CONVENTIONS
    # Front: Y < -1.8m
    # Rear:  Y > +1.8m
    # Cabin: -1.7m < Y < +1.7m
    objs = [o for o in bpy.data.objects if o.type == 'MESH' and not o.name.startswith("Studio_") and not o.name.startswith("Ref_")]

    glass_count = 0
    headlight_count = 0
    taillight_count = 0

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

        # Wheels (Z < 0.45m and |X| > 0.60m)
        if cz < 0.45 and abs(cx) > 0.60:
            if max(dy, dz) > 0.45 and dx > 0.15:
                o.data.materials.append(mat_tire)
            else:
                o.data.materials.append(mat_rim)

        # FRONT HEADLIGHTS (cy < -1.80m, Z between 0.48m and 0.85m)
        elif cy < -1.80 and 0.48 < cz < 0.85:
            # Outer glass lens vs chrome reflector
            if dy < 0.15 or dz < 0.22:
                o.data.materials.append(mat_hl_lens)
            else:
                o.data.materials.append(mat_hl_chrome)
            headlight_count += 1

        # REAR TAILLIGHTS (cy > +1.80m, Z between 0.45m and 0.85m)
        elif cy > +1.80 and 0.45 < cz < 0.85:
            # Check if clear reverse / indicator or ruby red
            if o.name in ['unnamed.018', 'unnamed.020', 'unnamed.013', 'unnamed.014']:
                o.data.materials.append(mat_tl_clear)
            else:
                o.data.materials.append(mat_tl_ruby)
            taillight_count += 1

        # TINTED WINDOW GLASS (cz > 0.76m, within cabin -1.75m < cy < +1.75m)
        # Includes side windows, windshield, rear hatch glass, and all internal glass sub-meshes
        elif cz > 0.76 and -1.75 < cy < 1.75 and (
            abs(cx) > 0.55 or (dx > 0.7 and dy > 0.4 and dz < 0.65 and cz > 0.85) or
            o.name in [
                'unnamed.021', 'unnamed.022', 'unnamed.023', 'unnamed.027', 'unnamed.029', 'unnamed.030',
                'unnamed.058', 'unnamed.059', 'unnamed.060', 'unnamed.062', 'unnamed.064', 'unnamed.065',
                'unnamed.066', 'unnamed.068', 'unnamed.142', 'unnamed.148', 'unnamed.150', 'unnamed.152',
                'unnamed.155', 'unnamed.159', 'unnamed.161', 'unnamed.163', 'unnamed.164', 'unnamed.170',
                'unnamed.171', 'unnamed.172', 'unnamed.177', 'unnamed.178', 'unnamed.179', 'unnamed.190',
                'unnamed.196', 'unnamed.199', 'unnamed.206', 'unnamed.212', 'unnamed.213', 'unnamed.214',
                'unnamed.216', 'unnamed.219', 'unnamed.227', 'unnamed.228', 'unnamed.229', 'unnamed.234',
                'unnamed.235', 'unnamed.236', 'unnamed.237', 'unnamed.238', 'unnamed.241', 'unnamed.242',
                'unnamed.243', 'unnamed.244', 'unnamed.245', 'unnamed.247', 'unnamed.248', 'unnamed.249',
                'unnamed.250', 'unnamed.251'
            ]
        ):
            # Window frames and rubber pillars
            if o.name in ['unnamed.034', 'unnamed.035', 'unnamed.036']:
                o.data.materials.append(mat_trim)
            else:
                o.data.materials.append(mat_tint)
                glass_count += 1

        # Front Splitter & Underbody (cz < 0.12m)
        elif cz < 0.12:
            o.data.materials.append(mat_trim)

        # Body Panels
        else:
            o.data.materials.append(mat_paint)

    print(f"[Shaders] Completed! Glass: {glass_count}, Headlights: {headlight_count}, Taillights: {taillight_count}")

    # 3. RENDER FRONT 3/4 & REAR 3/4 WITH CORRECTED CAMERA POSITIONS
    scene = bpy.context.scene
    cam = scene.camera
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080

    out_front = os.path.abspath(r"c:\Users\abdelkarim\Documents\laguna-beamng\laguna_front.png")
    out_rear = os.path.abspath(r"c:\Users\abdelkarim\Documents\laguna-beamng\laguna_rear.png")
    out_pres = os.path.abspath(r"c:\Users\abdelkarim\Documents\laguna-beamng\laguna_presentation.png")

    # Front is at -Y: Camera at (-4.2, -4.2, 1.40) looking at (0.0, -0.4, 0.60)
    cam.location = mathutils.Vector((-4.3, -4.2, 1.40))
    target_front = mathutils.Vector((0.0, -0.4, 0.60))
    cam.rotation_euler = (target_front - cam.location).to_track_quat('-Z', 'Y').to_euler()

    print("[Render] Rendering TRUE FRONT 3/4 (Headlights, Grille, Tinted Windshield)...")
    scene.render.filepath = out_front
    bpy.ops.render.render(write_still=True)
    shutil.copyfile(out_front, out_pres)

    # Rear is at +Y: Camera at (-4.2, +4.2, 1.40) looking at (0.0, +0.4, 0.60)
    cam.location = mathutils.Vector((-4.3, 4.2, 1.40))
    target_rear = mathutils.Vector((0.0, 0.4, 0.60))
    cam.rotation_euler = (target_rear - cam.location).to_track_quat('-Z', 'Y').to_euler()

    print("[Render] Rendering TRUE REAR 3/4 (Ruby Red Taillights, Rear Spoiler, Tinted Rear Window)...")
    scene.render.filepath = out_rear
    bpy.ops.render.render(write_still=True)

    # Copy to artifact folder
    artifact_dir = r"C:\Users\abdelkarim\.gemini\antigravity\brain\fa1588ad-d9ab-4eb3-9303-e3e476714ebd"
    if os.path.exists(artifact_dir):
        shutil.copyfile(out_front, os.path.join(artifact_dir, "laguna_front.png"))
        shutil.copyfile(out_front, os.path.join(artifact_dir, "laguna_presentation.png"))
        shutil.copyfile(out_rear, os.path.join(artifact_dir, "laguna_rear.png"))
        print("[Render] Updated all artifact images.")

if __name__ == "__main__":
    fix_all_shaders()
