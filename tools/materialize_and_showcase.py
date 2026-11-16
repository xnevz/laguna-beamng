"""
Categorize and apply realistic PBR materials to the 252-object Renault Laguna model
"""

import bpy
import mathutils
import math
import os
import shutil

def apply_pbr_materials_and_render():
    print("[Materialize] Categorizing objects and assigning realistic automotive materials...")

    objs = [o for o in bpy.data.objects if o.type == 'MESH' and not o.name.startswith("Studio_") and not o.name.startswith("Ref_")]

    # Create Materials
    def get_or_create(name, color, metallic=0.0, roughness=0.5, alpha=1.0, is_glass=False):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name)
            mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = color
            bsdf.inputs['Metallic'].default_value = metallic
            bsdf.inputs['Roughness'].default_value = roughness
            if is_glass or alpha < 1.0:
                bsdf.inputs['Alpha'].default_value = alpha
                mat.blend_method = 'BLEND'
                if is_glass:
                    bsdf.inputs['Roughness'].default_value = 0.05
                    bsdf.inputs['IOR'].default_value = 1.45
        return mat

    mat_paint = get_or_create("Laguna_Metallic_Blue", (0.02, 0.10, 0.48, 1.0), metallic=0.90, roughness=0.18) # Deep French Racing Blue
    mat_glass = get_or_create("Laguna_Glass_Tinted", (0.08, 0.12, 0.16, 0.30), metallic=0.1, roughness=0.05, alpha=0.30, is_glass=True)
    mat_tire = get_or_create("Laguna_Tire_Rubber", (0.02, 0.02, 0.025, 1.0), metallic=0.0, roughness=0.85)
    mat_rim = get_or_create("Laguna_Rim_White", (0.92, 0.93, 0.95, 1.0), metallic=0.85, roughness=0.20) # Classic BTCC white OZ rims
    mat_trim = get_or_create("Laguna_Trim_Black", (0.04, 0.04, 0.04, 1.0), metallic=0.05, roughness=0.75)
    mat_chrome = get_or_create("Laguna_Chrome", (0.95, 0.95, 0.97, 1.0), metallic=0.99, roughness=0.03)
    mat_taillight = get_or_create("Laguna_Taillight_Red", (0.85, 0.01, 0.01, 0.90), metallic=0.1, roughness=0.1, alpha=0.9)
    mat_headlight = get_or_create("Laguna_Headlight_Lens", (0.95, 0.98, 1.0, 0.85), metallic=0.2, roughness=0.05, alpha=0.85)

    # Classification by bounding box and position
    # Vehicle length ~4.51m (-2.25 to +2.25 on Y), width ~2.05m (-1.02 to +1.02 on X), height ~1.33m (0.0 to 1.33 on Z)
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

        # Wheels / Tires (Z center < 0.45m, X > 0.65m or X < -0.65m)
        if cz < 0.45 and (abs(cx) > 0.65):
            # If large outer diameter and dark
            if max(dy, dz) > 0.50 and dx < 0.35:
                # Rim vs Tire:
                if "wheel" in o.name.lower() or "rim" in o.name.lower() or dx < 0.15:
                    o.data.materials.append(mat_rim)
                else:
                    o.data.materials.append(mat_tire)
            else:
                o.data.materials.append(mat_rim)
        # Windows / Glass (Z > 0.82m, within cabin -1.5m < Y < 1.0m, thin panels)
        elif cz > 0.82 and -1.6 < cy < 1.1 and min(dx, dy, dz) < 0.05:
            o.data.materials.append(mat_glass)
        # Taillights (Rear: Y < -2.0m, Z between 0.6m and 0.85m, lateral X > 0.35m)
        elif cy < -2.0 and 0.55 < cz < 0.90 and abs(cx) > 0.35:
            o.data.materials.append(mat_taillight)
        # Headlights (Front: Y > 1.9m, Z between 0.55m and 0.78m, lateral X > 0.35m)
        elif cy > 1.9 and 0.50 < cz < 0.80 and abs(cx) > 0.35:
            o.data.materials.append(mat_headlight)
        # Exhaust tip (Rear: Y < -2.15m, Z < 0.35m)
        elif cy < -2.10 and cz < 0.35:
            o.data.materials.append(mat_chrome)
        # Splitter / Diffuser / Window trims / Rubbing strips (Z < 0.15m or very thin black strips)
        elif cz < 0.15 or (min(dx, dz) < 0.04 and 0.45 < cz < 0.60):
            o.data.materials.append(mat_trim)
        # Default body panels: Renault Sport Metallic Blue!
        else:
            o.data.materials.append(mat_paint)

    print("[Materialize] Assigned all PBR materials successfully!")

    # -------------------------------------------------------------
    # RENDER 1: FRONT 3/4 PRESENTATION
    # -------------------------------------------------------------
    scene = bpy.context.scene
    cam = scene.camera
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080

    out_front = os.path.abspath(r"c:\Users\abdelkarim\Documents\laguna-beamng\laguna_presentation.png")
    out_front_named = os.path.abspath(r"c:\Users\abdelkarim\Documents\laguna-beamng\laguna_front.png")
    scene.render.filepath = out_front

    # Position camera at front-left 3/4
    # Laguna front is +Y, center ~0.2m, height ~0.6m
    cam.location = mathutils.Vector((-4.2, 4.2, 1.35))
    target_front = mathutils.Vector((0.0, 0.4, 0.60))
    cam.rotation_euler = (target_front - cam.location).to_track_quat('-Z', 'Y').to_euler()

    print(f"[Render 1] Rendering front 3/4 presentation to {out_front}...")
    bpy.ops.render.render(write_still=True)
    shutil.copyfile(out_front, out_front_named)

    # -------------------------------------------------------------
    # RENDER 2: REAR 3/4 PRESENTATION
    # -------------------------------------------------------------
    out_rear = os.path.abspath(r"c:\Users\abdelkarim\Documents\laguna-beamng\laguna_rear.png")
    scene.render.filepath = out_rear

    # Position camera at rear-left 3/4
    cam.location = mathutils.Vector((-4.2, -4.2, 1.35))
    target_rear = mathutils.Vector((0.0, -0.4, 0.60))
    cam.rotation_euler = (target_rear - cam.location).to_track_quat('-Z', 'Y').to_euler()

    print(f"[Render 2] Rendering rear 3/4 presentation to {out_rear}...")
    bpy.ops.render.render(write_still=True)

    # Copy to artifact directory
    artifact_dir = r"C:\Users\abdelkarim\.gemini\antigravity\brain\fa1588ad-d9ab-4eb3-9303-e3e476714ebd"
    if os.path.exists(artifact_dir):
        shutil.copyfile(out_front, os.path.join(artifact_dir, "laguna_presentation.png"))
        shutil.copyfile(out_front_named, os.path.join(artifact_dir, "laguna_front.png"))
        shutil.copyfile(out_rear, os.path.join(artifact_dir, "laguna_rear.png"))
        print("[Render] All images copied to artifact directory.")

if __name__ == "__main__":
    apply_pbr_materials_and_render()
