"""
Generate Base Laguna 3D Chassis Mesh & Export to BeamNG Collada (.dae)
"""

import bpy
import bmesh
import math
import os

def create_base_car_mesh(output_dae_path, save_blend_path):
    # Ensure Object Mode
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Load master file if it exists, otherwise clean scene
    if os.path.exists(save_blend_path):
        bpy.ops.wm.open_mainfile(filepath=save_blend_path)
    else:
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)

    # Helper to get or create material
    def get_or_create_material(name, diffuse_color, metallic=0.0, roughness=0.5):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name=name)
            mat.use_nodes = True
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if bsdf:
                bsdf.inputs['Base Color'].default_value = diffuse_color
                bsdf.inputs['Metallic'].default_value = metallic
                bsdf.inputs['Roughness'].default_value = roughness
        return mat

    mat_paint = get_or_create_material("laguna_paint", (0.1, 0.25, 0.65, 1.0), metallic=0.7, roughness=0.3)
    mat_glass = get_or_create_material("laguna_glass", (0.1, 0.15, 0.2, 0.4), metallic=0.1, roughness=0.1)
    mat_plastic = get_or_create_material("laguna_plastic", (0.05, 0.05, 0.05, 1.0), roughness=0.8)
    mat_lights = get_or_create_material("laguna_lights", (0.9, 0.9, 0.95, 1.0), roughness=0.1)

    # Get target collection for Laguna II
    col_target = bpy.data.collections.get("02_Laguna_II_2001")
    if not col_target:
        col_target = bpy.context.scene.collection

    # Remove previous generated objects if any
    for obj in list(bpy.data.objects):
        if obj.name in ["laguna_gen2_body", "laguna_subframe_F", "laguna_axle_R"]:
            bpy.data.objects.remove(obj, do_unlink=True)

    # 1. Main Body Mesh (Sleek 5-door Hatchback silhouette)
    # Dimensions: Length 4.58m (-2.29 to +2.29 on Y), Width 1.75m (-0.875 to +0.875 on X), Height 1.43m (0.28 to 1.43 on Z)
    body_mesh = bpy.data.meshes.new("laguna_gen2_body_mesh")
    body_obj = bpy.data.objects.new("laguna_gen2_body", body_mesh)
    col_target.objects.link(body_obj)

    bm = bmesh.new()

    # Create key profile vertices (profile cross-sections along Y)
    # Y-axis: +Y is front bumper, -Y is rear bumper
    # Z-axis: 0.0 is ground, wheels at ~0.31m radius
    sections = [
        # Y, [ (X_half, Z_floor, Z_belt, Z_roof, X_roof_half) ]
        # 0: Front bumper (+2.29m)
        (2.29, 0.70, 0.35, 0.65, 0.65, 0.0),
        # 1: Hood front (+1.85m)
        (1.85, 0.85, 0.32, 0.75, 0.75, 0.0),
        # 2: Windshield base / A-pillar base (+0.80m)
        (0.80, 0.87, 0.30, 0.88, 0.95, 0.60),
        # 3: B-pillar / Mid roof (0.00m)
        (0.00, 0.875, 0.30, 0.90, 1.43, 0.62),
        # 4: C-pillar / Rear roof (-0.95m)
        (-0.95, 0.87, 0.30, 0.90, 1.41, 0.62),
        # 5: Rear hatch tailgate edge (-1.80m)
        (-1.80, 0.84, 0.32, 0.92, 1.05, 0.58),
        # 6: Rear bumper (-2.29m)
        (-2.29, 0.75, 0.38, 0.78, 0.78, 0.0)
    ]

    # Create boxy aerodynamic lofted vertices for each section
    v_rings = []
    for y, w_body, z_floor, z_belt, z_roof, w_roof in sections:
        # 8 vertices per ring:
        # 0: floor right, 1: belt right, 2: roof right, 3: roof center
        # 4: roof left,  5: belt left,  6: floor left,  7: floor center
        ring = [
            bm.verts.new((w_body, y, z_floor)),
            bm.verts.new((w_body, y, z_belt)),
            bm.verts.new((w_roof if w_roof > 0 else w_body*0.8, y, z_roof)),
            bm.verts.new((0.0, y, z_roof + 0.03 if w_roof > 0 else z_roof)),
            bm.verts.new((-w_roof if w_roof > 0 else -w_body*0.8, y, z_roof)),
            bm.verts.new((-w_body, y, z_belt)),
            bm.verts.new((-w_body, y, z_floor)),
            bm.verts.new((0.0, y, z_floor - 0.02))
        ]
        v_rings.append(ring)

    # Connect rings into faces
    for i in range(len(v_rings) - 1):
        r1 = v_rings[i]
        r2 = v_rings[i+1]
        for j in range(8):
            next_j = (j + 1) % 8
            bm.faces.new([r1[j], r2[j], r2[next_j], r1[next_j]])

    # Close front cap (section 0)
    front_r = v_rings[0]
    bm.faces.new([front_r[0], front_r[7], front_r[6], front_r[5], front_r[4], front_r[3], front_r[2], front_r[1]])

    # Close rear cap (section 6)
    rear_r = v_rings[-1]
    bm.faces.new([rear_r[1], rear_r[2], rear_r[3], rear_r[4], rear_r[5], rear_r[6], rear_r[7], rear_r[0]])

    bm.to_mesh(body_mesh)
    bm.free()

    # Assign materials
    body_mesh.materials.append(mat_paint)
    body_mesh.materials.append(mat_glass)
    body_mesh.materials.append(mat_plastic)

    # Smooth shading & Subdivision Surface modifier for clean curvature
    body_obj.select_set(True)
    bpy.context.view_layer.objects.active = body_obj
    bpy.ops.object.shade_smooth()

    subsurf = body_obj.modifiers.new("Subsurf", type='SUBSURF')
    subsurf.levels = 1
    subsurf.render_levels = 2

    # Save to blend
    bpy.ops.wm.save_as_mainfile(filepath=save_blend_path)
    print(f"[Generate] Saved mesh to {save_blend_path}")

    # Export to Collada DAE for BeamNG
    os.makedirs(os.path.dirname(output_dae_path), exist_ok=True)
    
    # BeamNG Collada export settings
    bpy.ops.wm.collada_export(
        filepath=output_dae_path,
        apply_modifiers=True,
        selected=False,
        include_children=True,
        triangulate=True
    )
    print(f"[Export] Exported Collada (.dae) to {output_dae_path}")

if __name__ == "__main__":
    blend_path = os.path.abspath(r"blender\laguna_master.blend")
    dae_path = os.path.abspath(r"vehicles\renault_laguna\renault_laguna.dae")
    create_base_car_mesh(dae_path, blend_path)
