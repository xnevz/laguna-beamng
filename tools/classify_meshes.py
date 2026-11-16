"""
Inspect all meshes in the Laguna I model and map them to accurate automotive shaders.
"""

import bpy

def inspect_and_classify():
    objs = [o for o in bpy.data.objects if o.type == 'MESH' and not o.name.startswith("Studio_") and not o.name.startswith("Ref_")]
    print(f"Total meshes to classify: {len(objs)}")

    for o in sorted(objs, key=lambda x: x.name):
        verts = [o.matrix_world @ v.co for v in o.data.vertices]
        if not verts: continue
        cx = sum(v.x for v in verts) / len(verts)
        cy = sum(v.y for v in verts) / len(verts)
        cz = sum(v.z for v in verts) / len(verts)
        dx = max(v.x for v in verts) - min(v.x for v in verts)
        dy = max(v.y for v in verts) - min(v.y for v in verts)
        dz = max(v.z for v in verts) - min(v.z for v in verts)
        
        # Identify key parts
        part_type = "BODY"
        
        # Wheels
        if cz < 0.45 and abs(cx) > 0.60:
            if max(dy, dz) > 0.45 and dx > 0.15:
                part_type = "TIRE"
            else:
                part_type = "RIM"
                
        # Front lights
        elif cy < -1.80 and 0.45 < cz < 0.75:
            if abs(cx) > 0.69:
                part_type = "FRONT_INDICATOR"
            elif abs(cx) > 0.58:
                part_type = "HEADLIGHT_LENS"
            else:
                part_type = "FRONT_GRILLE"
                
        # Rear lights
        elif cy > 1.80 and 0.65 < cz < 0.92:
            if abs(cx) > 0.62 and dy < 0.20 and dz < 0.15:
                part_type = "TAILLIGHT_OUTER_LENS" # Reverse/indicator
            elif abs(cx) < 0.65 and dy < 0.15 and dz < 0.25 and cz > 0.72:
                # Is it the lens strip or the trunk panel?
                if dx > 1.4:
                    part_type = "TAILLIGHT_RED_BAR"
                else:
                    part_type = "REAR_TRUNK_PANEL"
                    
        # Badges
        elif abs(cx) < 0.10 and (cy < -1.95 or cy > 2.05) and 0.50 < cz < 0.70 and dx < 0.15 and dy < 0.10:
            part_type = "BADGE_CHROME"
            
        # Interior
        elif -1.3 < cy < 0.9 and 0.35 < cz < 1.15 and abs(cx) < 0.58:
            if cz > 0.65 and -0.85 < cy < -0.45:
                part_type = "DASHBOARD"
            elif -0.55 < cy < -0.25 and 0.68 < cz < 0.88 and abs(cx - 0.35) < 0.15:
                part_type = "STEERING_WHEEL"
            elif 0.0 < cy < 0.40 and 0.38 < cz < 0.95 and abs(cx - 0.35) < 0.25:
                part_type = "SEAT"
            elif "135" in o.name:
                part_type = "ROLLCAGE"
            else:
                part_type = "INTERIOR_OTHER"
                
        # Glass
        elif cz > 0.75 and -1.75 < cy < 1.75 and (
            abs(cx) > 0.55 or (dx > 0.7 and dy > 0.4 and dz < 0.65 and cz > 0.85)
        ):
            part_type = "GLASS_TINT"
            
        # Splitter / underbody
        elif cz < 0.12:
            part_type = "SPLITTER"
            
        print(f"[{part_type:18s}] {o.name:15s} verts={len(verts):5d} c=({cx:6.2f}, {cy:6.2f}, {cz:6.2f}) dims=({dx:5.2f}, {dy:5.2f}, {dz:5.2f})")

inspect_and_classify()
