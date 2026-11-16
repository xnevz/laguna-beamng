"""
Setup Master Scene for Renault Laguna Mod in Blender
Prepares collections, units, and blueprint guide planes with accurate Laguna dimensions.
"""

import bpy
import os

def setup_laguna_scene(output_blend_path):
    # Ensure in Object Mode
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Clean existing default objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    # Set scene units to Metric / Meters
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = 'METERS'

    # Master Collections Hierarchy
    collections_to_create = [
        "00_References_Blueprints",
        "01_Laguna_I_1994",
        "02_Laguna_II_2001",
        "03_Laguna_III_2007",
        "04_Engines_Powertrain",
        "05_Suspension_RunningGear",
        "06_Wheels_Tires",
        "07_JBeam_Collision_Proxies"
    ]

    existing_collections = {c.name: c for c in bpy.data.collections}
    created_cols = {}

    for col_name in collections_to_create:
        if col_name in existing_collections:
            created_cols[col_name] = existing_collections[col_name]
        else:
            new_col = bpy.data.collections.new(col_name)
            bpy.context.scene.collection.children.link(new_col)
            created_cols[col_name] = new_col

    # Create Dimension Guides / Bounding Wireframes for each generation
    # Orientations: BeamNG Front = +Y, Up = +Z, Right = +X or Left = +X (Standard +Y forward)
    # Laguna I: L=4.508m, W=1.752m, H=1.433m, Wheelbase=2.670m
    # Laguna II: L=4.580m, W=1.750m, H=1.430m, Wheelbase=2.741m
    # Laguna III: L=4.695m, W=1.811m, H=1.445m, Wheelbase=2.756m

    specs = {
        "Laguna_I_Bounds": {"col": created_cols["01_Laguna_I_1994"], "size": (1.752, 4.508, 1.433), "color": (0.2, 0.6, 1.0)},
        "Laguna_II_Bounds": {"col": created_cols["02_Laguna_II_2001"], "size": (1.750, 4.580, 1.430), "color": (1.0, 0.6, 0.2)},
        "Laguna_III_Bounds": {"col": created_cols["03_Laguna_III_2007"], "size": (1.811, 4.695, 1.445), "color": (0.2, 1.0, 0.4)}
    }

    for name, data in specs.items():
        w, l, h = data["size"]
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(0.0, 0.0, h / 2.0)
        )
        box = bpy.context.active_object
        box.name = name
        box.scale = (w, l, h)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        box.display_type = 'WIRE'
        box.show_all_edges = True
        
        # Move to appropriate collection
        for col in box.users_collection:
            col.objects.unlink(box)
        data["col"].objects.link(box)

    # Create Blueprint Reference Planes in 00_References_Blueprints
    ref_col = created_cols["00_References_Blueprints"]
    
    # Side Blueprint Plane (Laguna II / average reference)
    # Placed slightly offset on X (-1.2m)
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(-1.2, 0.0, 1.43/2.0), rotation=(1.570796, 0.0, 1.570796))
    side_plane = bpy.context.active_object
    side_plane.name = "Ref_Plane_Side"
    side_plane.scale = (1.43, 4.58, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    for col in side_plane.users_collection:
        col.objects.unlink(side_plane)
    ref_col.objects.link(side_plane)

    # Top Blueprint Plane
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0.0, 0.0, -0.05), rotation=(0.0, 0.0, 0.0))
    top_plane = bpy.context.active_object
    top_plane.name = "Ref_Plane_Top"
    top_plane.scale = (1.75, 4.58, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    for col in top_plane.users_collection:
        col.objects.unlink(top_plane)
    ref_col.objects.link(top_plane)

    # Save to file
    os.makedirs(os.path.dirname(output_blend_path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=output_blend_path)
    print(f"[Setup Scene] Master file created successfully at: {output_blend_path}")

if __name__ == "__main__":
    blend_path = os.path.abspath(r"blender\laguna_master.blend")
    setup_laguna_scene(blend_path)
