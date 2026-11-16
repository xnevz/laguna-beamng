"""
Apply authentic tinted glass, headlights, taillights, and body shaders to Renault Laguna
"""

import bpy
import mathutils
import math
import os
import shutil

def setup_perfect_laguna_shaders():
    print("[Shaders] Creating authentic tinted glass, headlights, taillights, and paint...")

    # 1. SHADER MATERIALS
    def make_material(name):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        return mat

    # A) Tinted Automotive Glass
    mat_glass = make_material("Laguna_Glass_Tinted")
    bsdf_glass = mat_glass.node_tree.nodes.get("Principled BSDF")
    if bsdf_glass:
        # Smoky dark tint
        bsdf_glass.inputs['Base Color'].default_value = (0.04, 0.05, 0.07, 1.0)
        bsdf_glass.inputs['Roughness'].default_value = 0.03
        bsdf_glass.inputs['Metallic'].default_value = 0.1
        bsdf_glass.inputs['Alpha'].default_value = 0.45  # Sleek dark tint
        bsdf_glass.inputs['IOR'].default_value = 1.52
    mat_glass.blend_method = 'BLEND'

    # B) Headlight Glass Lens
    mat_headlight_lens = make_material("Laguna_Headlight_Lens")
    bsdf_hl = mat_headlight_lens.node_tree.nodes.get("Principled BSDF")
    if bsdf_hl:
        bsdf_hl.inputs['Base Color'].default_value = (0.95, 0.98, 1.0, 1.0)
        bsdf_hl.inputs['Roughness'].default_value = 0.02
        bsdf_hl.inputs['Metallic'].default_value = 0.15
        bsdf_hl.inputs['Alpha'].default_value = 0.40  # Transparent crystalline glass
        bsdf_hl.inputs['IOR'].default_value = 1.48
    mat_headlight_lens.blend_method = 'BLEND'

    # C) Headlight Reflector (Mirrored Chrome Bowl inside)
    mat_chrome_reflector = make_material("Laguna_Chrome_Reflector")
    bsdf_ref = mat_chrome_reflector.node_tree.nodes.get("Principled BSDF")
    if bsdf_ref:
        bsdf_ref.inputs['Base Color'].default_value = (0.95, 0.95, 0.98, 1.0)
        bsdf_ref.inputs['Metallic'].default_value = 1.0
        bsdf_ref.inputs['Roughness'].default_value = 0.02

    # D) Taillight Ruby Red Lens
    mat_taillight_red = make_material("Laguna_Taillight_Red")
    bsdf_tl = mat_taillight_red.node_tree.nodes.get("Principled BSDF")
    if bsdf_tl:
        bsdf_tl.inputs['Base Color'].default_value = (0.85, 0.015, 0.015, 1.0) # Deep automotive red
        bsdf_tl.inputs['Roughness'].default_value = 0.05
        bsdf_tl.inputs['Metallic'].default_value = 0.1
        bsdf_tl.inputs['Alpha'].default_value = 0.75  # Translucent ruby
        bsdf_tl.inputs['IOR'].default_value = 1.48
    mat_taillight_red.blend_method = 'BLEND'

    # E) Taillight White / Reverse Lamp
    mat_taillight_white = make_material("Laguna_Taillight_White")
    bsdf_tw = mat_taillight_white.node_tree.nodes.get("Principled BSDF")
    if bsdf_tw:
        bsdf_tw.inputs['Base Color'].default_value = (0.92, 0.92, 0.95, 1.0)
        bsdf_tw.inputs['Roughness'].default_value = 0.08
        bsdf_tw.inputs['Alpha'].default_value = 0.70
    mat_taillight_white.blend_method = 'BLEND'

    # F) Window Rubber Trim / Weatherstripping
    mat_rubber_trim = make_material("Laguna_Rubber_Trim")
    bsdf_rub = mat_rubber_trim.node_tree.nodes.get("Principled BSDF")
    if bsdf_rub:
        bsdf_rub.inputs['Base Color'].default_value = (0.025, 0.025, 0.028, 1.0)
        bsdf_rub.inputs['Roughness'].default_value = 0.70
        bsdf_rub.inputs['Metallic'].default_value = 0.0

    # G) Car Paint (Renault Sport Metallic Blue)
    mat_paint = make_material("Laguna_Sport_Blue")
    bsdf_paint = mat_paint.node_tree.nodes.get("Principled BSDF")
    if bsdf_paint:
        bsdf_paint.inputs['Base Color'].default_value = (0.02, 0.10, 0.50, 1.0)
        bsdf_paint.inputs['Metallic'].default_value = 0.88
        bsdf_paint.inputs['Roughness'].default_value = 0.18

    # H) Wheels (Tires & Rims)
    mat_tire = make_material("Laguna_Tire")
    bsdf_tire = mat_tire.node_tree.nodes.get("Principled BSDF")
    if bsdf_tire:
        bsdf_tire.inputs['Base Color'].default_value = (0.02, 0.02, 0.025, 1.0)
        bsdf_tire.inputs['Roughness'].default_value = 0.85

    mat_rim = make_material("Laguna_Rim")
    bsdf_rim = mat_rim.node_tree.nodes.get("Principled BSDF")
    if bsdf_rim:
        bsdf_rim.inputs['Base Color'].default_value = (0.92, 0.93, 0.95, 1.0)
        bsdf_rim.inputs['Metallic'].default_value = 0.80
        bsdf_rim.inputs['Roughness'].default_value = 0.15

    # 2. ASSIGN MATERIALS TO OBJECTS
    objs = [o for o in bpy.data.objects if o.type == 'MESH' and not o.name.startswith("Studio_") and not o.name.startswith("Ref_")]

    # Glass objects (identifying the windshield, rear glass, and side window panels)
    # Glass meshes in this model: unnamed.021, unnamed.022, unnamed.163, unnamed.190, unnamed.237, etc.
    glass_assigned = 0
    headlight_assigned = 0
    taillight_assigned = 0
    wheel_assigned = 0

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
            wheel_assigned += 1

        # B) Headlights (Front: Y > 1.85m, Z between 0.50m and 0.88m, |X| > 0.35m or spanning front)
        elif cy > 1.85 and 0.48 < cz < 0.92:
            # Check if outer glass lens or reflector
            if o.name in ['unnamed.016', 'unnamed.018', 'unnamed.020'] or (abs(cx) > 0.45 and dz < 0.25 and dy < 0.25):
                o.data.materials.append(mat_headlight_lens)
            elif o.name in ['unnamed.010', 'unnamed.015']:
                o.data.materials.append(mat_chrome_reflector)
            else:
                # Surrounding trim or lens
                o.data.materials.append(mat_headlight_lens)
            headlight_assigned += 1

        # C) Taillights (Rear: Y < -1.85m, Z between 0.45m and 0.75m)
        elif cy < -1.85 and 0.45 < cz < 0.75:
            # Check if reverse lamp (center white) or red lens
            if o.name in ['unnamed.013', 'unnamed.014', 'unnamed.012']:
                o.data.materials.append(mat_taillight_white)
            else:
                o.data.materials.append(mat_taillight_red)
            taillight_assigned += 1

        # D) Glass / Windshield / Side Windows
        # Any greenhouse panel with Z > 0.80m, |Y| < 1.7m that forms the windows
        # Specifically unnamed.021, unnamed.022, unnamed.023, unnamed.163, unnamed.190, unnamed.237, unnamed.241, unnamed.247
        elif cz > 0.80 and -1.7 < cy < 1.6:
            # Check if this object is a window panel
            if o.name in [
                'unnamed.021', 'unnamed.022', 'unnamed.023', 'unnamed.027', 'unnamed.029', 'unnamed.030',
                'unnamed.150', 'unnamed.152', 'unnamed.155', 'unnamed.163', 'unnamed.164', 'unnamed.190',
                'unnamed.196', 'unnamed.199', 'unnamed.213', 'unnamed.214', 'unnamed.216', 'unnamed.219',
                'unnamed.237', 'unnamed.238', 'unnamed.241', 'unnamed.247'
            ] or (dx > 0.8 and dy > 0.6 and dz < 0.6 and cz > 0.90):
                o.data.materials.append(mat_glass)
                glass_assigned += 1
            # Window frames and rubber pillars
            elif o.name in ['unnamed.034', 'unnamed.035', 'unnamed.036', 'unnamed.058', 'unnamed.064', 'unnamed.060', 'unnamed.066']:
                o.data.materials.append(mat_rubber_trim)
            else:
                o.data.materials.append(mat_paint)

        # E) Aerodynamic Splitter & Underbody (Z < 0.12m)
        elif cz < 0.12:
            o.data.materials.append(mat_rubber_trim)

        # F) Main Body Panels
        else:
            o.data.materials.append(mat_paint)

    print(f"[Shaders] Assigned: {glass_assigned} glass objects, {headlight_assigned} headlight objects, {taillight_assigned} taillight objects, {wheel_assigned} wheel objects.")

    # 3. STUDIO LIGHTING ENHANCEMENT FOR GLASS & LIGHTS
    # We add an overhead fill and front rim to catch crisp reflections on the windshield and headlight glass
    col_studio = bpy.data.collections.get("Studio_Presentation")
    if col_studio:
        light_glass_boost = bpy.data.objects.get("Studio_Glass_Reflection_Light")
        if not light_glass_boost:
            light_d = bpy.data.lights.new("Studio_Glass_Light_Data", type='AREA')
            light_d.energy = 1800.0
            light_d.size = 5.0
            light_d.size_y = 3.0
            light_d.color = (1.0, 1.0, 1.0)
            light_glass_boost = bpy.data.objects.new("Studio_Glass_Reflection_Light", light_d)
            light_glass_boost.location = (-1.5, 2.5, 3.2)
            light_glass_boost.rotation_euler = (math.radians(45), math.radians(10), math.radians(-30))
            col_studio.objects.link(light_glass_boost)

    # 4. RENDER FRONT 3/4 & REAR 3/4
    scene = bpy.context.scene
    cam = scene.camera
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080

    out_front = os.path.abspath(r"c:\Users\abdelkarim\Documents\laguna-beamng\laguna_front.png")
    out_rear = os.path.abspath(r"c:\Users\abdelkarim\Documents\laguna-beamng\laguna_rear.png")
    out_pres = os.path.abspath(r"c:\Users\abdelkarim\Documents\laguna-beamng\laguna_presentation.png")

    # Front 3/4 Camera (showing headlights, grille, hood, windshield glass, and front wheel)
    cam.location = mathutils.Vector((-4.3, 4.2, 1.40))
    target_front = mathutils.Vector((0.0, 0.4, 0.60))
    cam.rotation_euler = (target_front - cam.location).to_track_quat('-Z', 'Y').to_euler()

    print("[Render] Rendering Front 3/4 with glass and headlights...")
    scene.render.filepath = out_front
    bpy.ops.render.render(write_still=True)
    shutil.copyfile(out_front, out_pres)

    # Rear 3/4 Camera (showing taillights, spoiler, rear tinted glass, and rear wheel)
    cam.location = mathutils.Vector((-4.3, -4.2, 1.40))
    target_rear = mathutils.Vector((0.0, -0.4, 0.60))
    cam.rotation_euler = (target_rear - cam.location).to_track_quat('-Z', 'Y').to_euler()

    print("[Render] Rendering Rear 3/4 with taillights and rear glass...")
    scene.render.filepath = out_rear
    bpy.ops.render.render(write_still=True)

    # Copy to artifact folder
    artifact_dir = r"C:\Users\abdelkarim\.gemini\antigravity\brain\fa1588ad-d9ab-4eb3-9303-e3e476714ebd"
    if os.path.exists(artifact_dir):
        shutil.copyfile(out_front, os.path.join(artifact_dir, "laguna_front.png"))
        shutil.copyfile(out_front, os.path.join(artifact_dir, "laguna_presentation.png"))
        shutil.copyfile(out_rear, os.path.join(artifact_dir, "laguna_rear.png"))
        print("[Render] Updated all images in artifact directory.")

if __name__ == "__main__":
    setup_perfect_laguna_shaders()
