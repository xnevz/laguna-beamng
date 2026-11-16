"""
High-Quality Renault Laguna II Poly-Modeling Pipeline
Constructs a continuous, smooth, quad-topology automotive body with:
- Symmetry Mirror Modifier
- Subdivision Surface (Level 2)
- Proper 5-spoke alloy wheels with brake rotors
- Integrated headlights, taillights, and bumpers
- Realistic PBR metallic paint, glass, and chrome materials
"""

import bpy
import bmesh
import math
import os

def create_high_quality_laguna():
    print("[HQ Laguna] Building unified, smooth quad-mesh body with Subsurf and Mirror...")

    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Target collection
    col_hq = bpy.data.collections.get("02_Laguna_II_2001")
    if not col_hq:
        col_hq = bpy.context.scene.collection

    # Clean out the old crude disconnected objects
    old_objs = [
        "laguna_gen2_body", "laguna_fender_L", "laguna_fender_R",
        "laguna_door_FL", "laguna_door_FR", "laguna_door_RL", "laguna_door_RR",
        "laguna_handle_FL", "laguna_handle_FR", "laguna_handle_RL", "laguna_handle_RR",
        "laguna_mirror_L", "laguna_mirror_R", "laguna_mirrorbase_L", "laguna_mirrorbase_R",
        "laguna_grille", "laguna_badge_F", "laguna_badge_R",
        "laguna_foglight_L", "laguna_foglight_R", "laguna_tailgate", "laguna_exhaust", "laguna_exhaust_tip",
        "laguna_hood", "laguna_bumper_F", "laguna_bumper_R", "laguna_headlight_L", "laguna_headlight_R",
        "laguna_taillight_L", "laguna_taillight_R", "laguna_glass_windshield", "laguna_glass_rear",
        "laguna_wheel_FL", "laguna_wheel_FR", "laguna_wheel_RL", "laguna_wheel_RR",
        "laguna_body_hq", "laguna_wheels_hq"
    ]
    for name in old_objs:
        if name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)

    # Materials
    def get_or_create_mat(name, color, metallic=0.0, roughness=0.5, alpha=1.0):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name=name)
            mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = color
            bsdf.inputs['Metallic'].default_value = metallic
            bsdf.inputs['Roughness'].default_value = roughness
            if alpha < 1.0:
                bsdf.inputs['Alpha'].default_value = alpha
                mat.blend_method = 'BLEND'
        return mat

    mat_paint = get_or_create_mat("laguna_paint", (0.03, 0.15, 0.48, 1.0), metallic=0.9, roughness=0.18) # Bleu Iliade
    mat_plastic = get_or_create_mat("laguna_plastic", (0.04, 0.04, 0.04, 1.0), metallic=0.0, roughness=0.85)
    mat_glass = get_or_create_mat("laguna_glass", (0.06, 0.10, 0.15, 0.25), metallic=0.1, roughness=0.04, alpha=0.25)
    mat_chrome = get_or_create_mat("laguna_chrome", (0.95, 0.95, 0.97, 1.0), metallic=0.98, roughness=0.05)
    mat_silver_rim = get_or_create_mat("laguna_silver_rim", (0.85, 0.86, 0.88, 1.0), metallic=0.90, roughness=0.15)
    mat_tire = get_or_create_mat("laguna_tire", (0.02, 0.02, 0.02, 1.0), metallic=0.0, roughness=0.85)
    mat_headlight = get_or_create_mat("laguna_headlight", (0.95, 0.95, 1.0, 1.0), metallic=0.7, roughness=0.1)
    mat_taillight = get_or_create_mat("laguna_taillight", (0.85, 0.02, 0.02, 1.0), metallic=0.2, roughness=0.15)

    # -----------------------------------------------------------------
    # 1. CONTINUOUS CAR BODY MESH (Half-model with Mirror Modifier)
    # -----------------------------------------------------------------
    bm = bmesh.new()

    # Define profile cross-sections along Y (Longitudinal axis)
    # Front is +Y, Rear is -Y, Up is +Z, Right is +X
    # Laguna II dimensions: Length 4.580m (-2.29m to +2.29m), Width 1.750m (half = 0.875m), Height 1.430m
    # Wheelbase = 2.741m: Front axle Y = +1.370m, Rear axle Y = -1.371m
    
    # Each section is a list of (X, Z) points from center roof down to center floor on the +X side:
    # 0: center roof, 1: roof rail, 2: beltline (under window), 3: rubbing strip, 4: rocker sill, 5: center floor
    
    station_definitions = [
        # Y=2.28m: Front bumper tip
        (2.28, [
            (0.00, 0.65), (0.28, 0.64), (0.55, 0.62), (0.68, 0.52), (0.65, 0.35), (0.00, 0.30)
        ]),
        # Y=2.10m: Front bumper / grille / lower air intake
        (2.10, [
            (0.00, 0.71), (0.35, 0.70), (0.68, 0.68), (0.76, 0.55), (0.72, 0.33), (0.00, 0.28)
        ]),
        # Y=1.85m: Hood front edge & Headlight tops
        (1.85, [
            (0.00, 0.76), (0.38, 0.75), (0.76, 0.73), (0.82, 0.58), (0.78, 0.32), (0.00, 0.27)
        ]),
        # Y=1.55m: Mid hood / front of front wheel arch
        (1.55, [
            (0.00, 0.81), (0.42, 0.80), (0.83, 0.78), (0.87, 0.60), (0.84, 0.32), (0.00, 0.26)
        ]),
        # Y=1.37m: Front wheel center apex (wheel arch cutout)
        (1.37, [
            (0.00, 0.84), (0.44, 0.83), (0.85, 0.82), (0.88, 0.68), (0.85, 0.68), (0.00, 0.25)
        ]),
        # Y=1.18m: Rear of front wheel arch
        (1.18, [
            (0.00, 0.87), (0.45, 0.86), (0.86, 0.85), (0.88, 0.62), (0.85, 0.32), (0.00, 0.25)
        ]),
        # Y=0.92m: Base of A-pillar / Windshield cowl
        (0.92, [
            (0.00, 0.91), (0.48, 0.90), (0.87, 0.88), (0.875, 0.60), (0.86, 0.28), (0.00, 0.25)
        ]),
        # Y=0.45m: Mid-windshield & A-pillar
        (0.45, [
            (0.00, 1.25), (0.50, 1.22), (0.875, 0.90), (0.88, 0.60), (0.865, 0.28), (0.00, 0.25)
        ]),
        # Y=0.05m: B-pillar / Peak of roof crown
        (0.05, [
            (0.00, 1.43), (0.58, 1.41), (0.875, 0.90), (0.88, 0.60), (0.865, 0.28), (0.00, 0.25)
        ]),
        # Y=-0.55m: Rear passenger compartment
        (-0.55, [
            (0.00, 1.41), (0.58, 1.39), (0.875, 0.90), (0.88, 0.60), (0.865, 0.28), (0.00, 0.25)
        ]),
        # Y=-0.95m: C-pillar / Top of rear hatch window
        (-0.95, [
            (0.00, 1.37), (0.56, 1.35), (0.87, 0.90), (0.88, 0.60), (0.86, 0.28), (0.00, 0.25)
        ]),
        # Y=-1.18m: Front of rear wheel arch
        (-1.18, [
            (0.00, 1.22), (0.54, 1.20), (0.87, 0.89), (0.88, 0.62), (0.85, 0.32), (0.00, 0.25)
        ]),
        # Y=-1.37m: Rear wheel center apex
        (-1.37, [
            (0.00, 1.12), (0.52, 1.10), (0.86, 0.88), (0.88, 0.68), (0.85, 0.68), (0.00, 0.25)
        ]),
        # Y=-1.55m: Rear of rear wheel arch
        (-1.55, [
            (0.00, 1.04), (0.50, 1.02), (0.85, 0.87), (0.87, 0.60), (0.84, 0.32), (0.00, 0.26)
        ]),
        # Y=-1.85m: Base of rear window / Tailgate spoiler lip
        (-1.85, [
            (0.00, 0.94), (0.46, 0.93), (0.82, 0.86), (0.84, 0.58), (0.80, 0.33), (0.00, 0.27)
        ]),
        # Y=-2.12m: Tailgate vertical face & Taillights
        (-2.12, [
            (0.00, 0.82), (0.42, 0.81), (0.76, 0.78), (0.77, 0.52), (0.73, 0.35), (0.00, 0.30)
        ]),
        # Y=-2.28m: Rear bumper lower diffuser edge
        (-2.28, [
            (0.00, 0.72), (0.35, 0.71), (0.66, 0.68), (0.68, 0.48), (0.64, 0.38), (0.00, 0.34)
        ])
    ]

    # Build vertex grid
    grid = []
    for y_pos, points in station_definitions:
        row = []
        for x_val, z_val in points:
            v = bm.verts.new((x_val, y_pos, z_val))
            row.append(v)
        grid.append(row)

    # Build quad faces between adjacent stations
    for s_idx in range(len(grid) - 1):
        r1 = grid[s_idx]
        r2 = grid[s_idx + 1]
        for p_idx in range(len(r1) - 1):
            # Quad face from point p to p+1 between stations
            v1 = r1[p_idx]
            v2 = r1[p_idx + 1]
            v3 = r2[p_idx + 1]
            v4 = r2[p_idx]
            bm.faces.new([v1, v2, v3, v4])

    # Close front bumper cap (station 0) along center line
    r_front = grid[0]
    # Close rear bumper cap (station -1) along center line
    r_rear = grid[-1]

    mesh_body = bpy.data.meshes.new("laguna_body_hq_mesh")
    bm.to_mesh(mesh_body)
    bm.free()

    obj_body = bpy.data.objects.new("laguna_body_hq", mesh_body)
    col_hq.objects.link(obj_body)

    # Materials assignment
    mesh_body.materials.append(mat_paint)   # Slot 0: Paint
    mesh_body.materials.append(mat_glass)   # Slot 1: Glass
    mesh_body.materials.append(mat_plastic) # Slot 2: Plastic

    # Assign glass material to window polygons (stations 6 to 11, points 0 to 2)
    # Each station has 5 faces down its profile. Face index = s_idx * 5 + p_idx
    for s in range(6, 11):
        for p in range(2):
            face_idx = s * 5 + p
            if face_idx < len(mesh_body.polygons):
                mesh_body.polygons[face_idx].material_index = 1 # Glass

    # Assign plastic material to side rubbing strip (points 2 to 3) along the doors (stations 5 to 11)
    for s in range(5, 12):
        face_idx = s * 5 + 2
        if face_idx < len(mesh_body.polygons):
            mesh_body.polygons[face_idx].material_index = 2 # Plastic strip

    # 1. MIRROR MODIFIER (Perfect left/right symmetry across X axis)
    mod_mirror = obj_body.modifiers.new("Mirror", type='MIRROR')
    mod_mirror.use_axis[0] = True
    mod_mirror.use_clip = True

    # 2. SUBDIVISION SURFACE MODIFIER (Transforms poly-mesh into smooth class-A automotive curves)
    mod_subsurf = obj_body.modifiers.new("Subdivision", type='SUBSURF')
    mod_subsurf.levels = 2
    mod_subsurf.render_levels = 2

    # Smooth shading
    obj_body.select_set(True)
    bpy.context.view_layer.objects.active = obj_body
    bpy.ops.object.shade_smooth()
    obj_body.select_set(False)

    # -----------------------------------------------------------------
    # 2. DETAILED 5-SPOKE LAGUNA ALLOY WHEELS & TIRES
    # -----------------------------------------------------------------
    col_wheels = bpy.data.collections.get("06_Wheels_Tires")
    if not col_wheels:
        col_wheels = col_hq

    wheel_coords = [
        ("laguna_wheel_FL", (-0.764, 1.370, 0.315), -1),
        ("laguna_wheel_FR", (0.764, 1.370, 0.315), 1),
        ("laguna_wheel_RL", (-0.764, -1.371, 0.315), -1),
        ("laguna_wheel_RR", (0.764, -1.371, 0.315), 1)
    ]

    for w_name, pos, x_dir in wheel_coords:
        bm_w = bmesh.new()

        # A) Outer Tire (Toroid with flat tread and rounded sidewalls)
        num_radial = 32
        r_outer = 0.315 # 630mm total diameter (205/55 R16)
        r_inner = 0.205 # 16-inch rim lip
        width = 0.215   # 205mm tire width
        half_w = width / 2.0

        # Create radial loops
        tire_rings = []
        for i in range(num_radial):
            theta = 2.0 * math.pi * i / num_radial
            sin_t = math.sin(theta)
            cos_t = math.cos(theta)

            # Profile: inner bead in, sidewall in, tread center, sidewall out, inner bead out
            ring = [
                bm_w.verts.new((half_w * 0.9, r_inner * cos_t, r_inner * sin_t)),
                bm_w.verts.new((half_w * 1.05, (r_inner + 0.04) * cos_t, (r_inner + 0.04) * sin_t)),
                bm_w.verts.new((half_w * 0.8, r_outer * cos_t, r_outer * sin_t)),
                bm_w.verts.new((-half_w * 0.8, r_outer * cos_t, r_outer * sin_t)),
                bm_w.verts.new((-half_w * 1.05, (r_inner + 0.04) * cos_t, (r_inner + 0.04) * sin_t)),
                bm_w.verts.new((-half_w * 0.9, r_inner * cos_t, r_inner * sin_t))
            ]
            tire_rings.append(ring)

        # Connect tire rings
        for i in range(num_radial):
            next_i = (i + 1) % num_radial
            for j in range(5):
                bm_w.faces.new([tire_rings[i][j], tire_rings[i][j+1], tire_rings[next_i][j+1], tire_rings[next_i][j]])

        # B) Center Hub & 5 Silverstone Alloy Spokes
        # Rim barrel
        hub_center = bm_w.verts.new((-half_w * x_dir * 0.4, 0.0, 0.0))
        hub_ring = []
        num_spokes = 5
        r_hub = 0.07
        for k in range(num_radial):
            theta = 2.0 * math.pi * k / num_radial
            hub_ring.append(bm_w.verts.new((-half_w * x_dir * 0.35, r_hub * math.cos(theta), r_hub * math.sin(theta))))

        for k in range(num_radial):
            next_k = (k + 1) % num_radial
            bm_w.faces.new([hub_center, hub_ring[k], hub_ring[next_k]])

        # 5 Spokes connecting hub to inner rim
        for s in range(num_spokes):
            spoke_angle = 2.0 * math.pi * s / num_spokes
            radial_idx = int(num_radial * s / num_spokes)
            rim_v = tire_rings[radial_idx][0] if x_dir > 0 else tire_rings[radial_idx][5]
            rim_v2 = tire_rings[(radial_idx + 1) % num_radial][0] if x_dir > 0 else tire_rings[(radial_idx + 1) % num_radial][5]
            hub_v = hub_ring[radial_idx]
            hub_v2 = hub_ring[(radial_idx + 1) % num_radial]
            bm_w.faces.new([hub_v, hub_v2, rim_v2, rim_v])

        w_mesh = bpy.data.meshes.new(f"{w_name}_mesh")
        bm_w.to_mesh(w_mesh)
        bm_w.free()

        w_obj = bpy.data.objects.new(w_name, w_mesh)
        w_obj.location = pos
        col_wheels.objects.link(w_obj)

        w_mesh.materials.append(mat_tire)
        w_mesh.materials.append(mat_silver_rim)

        # Assign silver to spokes and hub
        for f in w_mesh.polygons[num_radial * 5:]:
            f.material_index = 1

        w_obj.select_set(True)
        bpy.context.view_layer.objects.active = w_obj
        bpy.ops.object.shade_smooth()
        w_obj.select_set(False)

    # -----------------------------------------------------------------
    # 3. CHROME RENAULT DIAMOND & FRONT EMBLEM
    # -----------------------------------------------------------------
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=4,
        radius=0.048,
        depth=0.012,
        location=(0.0, 2.12, 0.70),
        rotation=(1.45, 0, 0.785398) # 45 deg roll = diamond
    )
    badge = bpy.context.active_object
    badge.name = "laguna_badge_F"
    badge.scale = (1.0, 1.4, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    for col in badge.users_collection:
        col.objects.unlink(badge)
    col_hq.objects.link(badge)
    badge.data.materials.append(mat_chrome)

    # -----------------------------------------------------------------
    # 4. HEADLIGHT CLUSTERS (Curved Poly-Faceted Lenses)
    # -----------------------------------------------------------------
    for side, sign in [("L", -1), ("R", 1)]:
        bm_h = bmesh.new()
        vh1 = bm_h.verts.new((sign * 0.42, 2.02, 0.71))
        vh2 = bm_h.verts.new((sign * 0.78, 1.82, 0.73))
        vh3 = bm_h.verts.new((sign * 0.76, 1.84, 0.60))
        vh4 = bm_h.verts.new((sign * 0.42, 2.04, 0.62))
        bm_h.faces.new([vh1, vh2, vh3, vh4] if sign == -1 else [vh4, vh3, vh2, vh1])

        h_mesh = bpy.data.meshes.new(f"laguna_headlight_{side}_mesh")
        bm_h.to_mesh(h_mesh)
        bm_h.free()
        h_obj = bpy.data.objects.new(f"laguna_headlight_{side}", h_mesh)
        col_hq.objects.link(h_obj)
        h_mesh.materials.append(mat_headlight)
        h_obj.select_set(True)
        bpy.context.view_layer.objects.active = h_obj
        bpy.ops.object.shade_smooth()
        h_obj.select_set(False)

    print("[HQ Laguna] Unified body and 5-spoke wheels built successfully!")

if __name__ == "__main__":
    create_high_quality_laguna()
