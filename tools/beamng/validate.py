"""Static checks for the Laguna II BeamNG vehicle (no game needed).

Run:  python tools/beamng/validate.py

For every configuration (.pc) it resolves the part tree from the main part
exactly as the parts selector would (configured part, else the slot default)
and checks the result.  Exit code 1 if anything is wrong.
"""

import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
VEH = os.path.join(ROOT, "vehicles", "renault_laguna")
ERRORS, WARNINGS = [], []


def err(msg):
    ERRORS.append(msg)


def warn(msg):
    WARNINGS.append(msg)


def load_jbeam(path):
    text = open(path, encoding="utf-8").read()
    text = re.sub(r"//[^\n]*", "", text)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    return json.loads(text)


def table_rows(section):
    """jbeam table -> (header, [(row, props_in_effect)]) ; dict rows are property modifiers."""
    if not section:
        return [], []
    header = section[0]
    rows, props = [], {}
    for r in section[1:]:
        if isinstance(r, dict):
            props.update(r)
        elif isinstance(r, list):
            extra = r[len(header):] if len(r) > len(header) else []
            p = dict(props)
            for e in extra:
                if isinstance(e, dict):
                    p.update(e)
            rows.append((r, p))
    return header, rows


def dae_meshes_and_materials():
    tree = ET.parse(os.path.join(VEH, "renault_laguna.dae"))
    ns = {"c": "http://www.collada.org/2005/11/COLLADASchema"}
    meshes = {}
    for g in tree.getroot().iterfind(".//c:geometry", ns):
        mats = {t.get("material") for t in g.iterfind(".//c:triangles", ns)}
        meshes[g.get("name")] = mats
    return meshes


def main():
    parts, where = {}, {}
    for f in sorted(glob.glob(os.path.join(VEH, "*.jbeam"))):
        try:
            data = load_jbeam(f)
        except Exception as exc:
            err(f"{os.path.basename(f)}: does not parse: {exc}")
            continue
        for name, p in data.items():
            if name in parts:
                err(f"part {name} defined twice ({where[name]}, {os.path.basename(f)})")
            parts[name] = p
            where[name] = os.path.basename(f)
    materials = json.load(open(os.path.join(VEH, "materials.json"), encoding="utf-8"))
    meshes = dae_meshes_and_materials()
    info = json.load(open(os.path.join(VEH, "info.json"), encoding="utf-8"))
    mains = [n for n, p in parts.items() if p.get("slotType") == "main"]
    if len(mains) != 1:
        err(f"expected exactly one main part, found {mains}")
        return
    by_slot = {}
    for n, p in parts.items():
        by_slot.setdefault(p.get("slotType"), []).append(n)

    # Static per-part checks.
    for n, p in parts.items():
        for row in (p.get("slots") or [])[1:]:
            if isinstance(row, list):
                st, default = row[0], row[1]
                if st not in by_slot:
                    if default:
                        err(f"{n}: slot {st} has no parts at all")
                    else:
                        warn(f"{n}: slot {st} has no parts here (expected from BeamNG's common folder)")
                if default and default not in by_slot.get(st, []):
                    err(f"{n}: slot {st} default {default} is not a part of that slot type")
        _h, rows = table_rows(p.get("flexbodies"))
        for r, _pp in rows:
            if r[0] not in meshes:
                err(f"{n}: flexbody mesh {r[0]} is not in renault_laguna.dae")
        for mat, e in (p.get("glowMap") or {}).items():
            for k in ("off", "on", "on_intense"):
                if e.get(k) and e[k] not in materials:
                    err(f"{n}: glowMap {mat}.{k} -> {e[k]} missing from materials.json")
    for m, mats in meshes.items():
        for mt in mats:
            if mt not in materials:
                err(f"mesh {m} uses material {mt} missing from materials.json")

    # Per configuration: resolve and check the assembled vehicle.
    pcs = sorted(glob.glob(os.path.join(VEH, "*.pc")))
    if info.get("default_pc") and not os.path.exists(os.path.join(VEH, info["default_pc"] + ".pc")):
        err(f"info.json default_pc {info['default_pc']} has no .pc file")
    for pc_path in pcs:
        cfg = os.path.basename(pc_path)[:-3]
        pc = json.load(open(pc_path, encoding="utf-8"))
        if not os.path.exists(os.path.join(VEH, f"info_{cfg}.json")):
            err(f"{cfg}: no info_{cfg}.json")
        chosen = pc.get("parts", {})
        for st, pn in chosen.items():
            if pn and pn not in parts:
                err(f"{cfg}: part {pn} (slot {st}) does not exist")
            elif pn and parts[pn].get("slotType") != st:
                err(f"{cfg}: part {pn} has slotType {parts[pn].get('slotType')}, configured for {st}")
        active, seen_slots = [], set()

        def walk(pn):
            active.append(pn)
            for row in (parts[pn].get("slots") or [])[1:]:
                if not isinstance(row, list):
                    continue
                st, default = row[0], row[1]
                seen_slots.add(st)
                pick = chosen.get(st, default)
                if pick:
                    if pick not in parts:
                        err(f"{cfg}: slot {st} -> {pick} does not exist")
                        continue
                    walk(pick)

        walk(mains[0])
        for st in chosen:
            if st not in seen_slots:
                err(f"{cfg}: configures slot {st}, which is not in its part tree")
        nodes, variables, used_vars, devices = {}, {}, set(), {}
        for pn in active:
            p = parts[pn]
            _h, rows = table_rows(p.get("nodes"))
            for r, _pp in rows:
                if r[0] in nodes:
                    err(f"{cfg}: node {r[0]} defined twice ({nodes[r[0]]}, {pn})")
                nodes[r[0]] = pn
            _h, rows = table_rows(p.get("variables"))
            for r, _pp in rows:
                variables[r[0]] = pn
        for pn in active:
            p = parts[pn]
            for sec, cols in (("beams", 2), ("triangles", 3), ("hydros", 2)):
                _h, rows = table_rows(p.get(sec))
                for r, _pp in rows:
                    for nid in r[:cols]:
                        if nid not in nodes:
                            err(f"{cfg}: {pn}.{sec} uses unknown node {nid}")
                    if sec == "beams" and r[0] == r[1]:
                        err(f"{cfg}: {pn} beam from {r[0]} to itself")
            _h, rows = table_rows(p.get("pressureWheels"))
            for r, _pp in rows:
                for nid in (r[3], r[4], r[6]):
                    if nid not in nodes:
                        err(f"{cfg}: wheel {r[0]} uses unknown node {nid}")
            for row in (p.get("refNodes") or [])[1:]:
                for nid in row:
                    if nid not in nodes:
                        err(f"{cfg}: refNode {nid} unknown")
            eng = p.get("mainEngine", {})
            for nid in eng.get("torqueReactionNodes:", []):
                if nid not in nodes:
                    err(f"{cfg}: torqueReactionNode {nid} unknown")
            _h, rows = table_rows(p.get("powertrain"))
            for r, _pp in rows:
                devices[r[1]] = (r[2], pn)
            blob = json.dumps({k: v for k, v in p.items() if k != "variables"})
            used_vars |= set(re.findall(r"\$[A-Za-z_][A-Za-z0-9_]*", blob))
        for v in sorted(used_vars):
            if v not in variables:
                err(f"{cfg}: variable {v} used but not defined by any active part")
        for dev, (inp, pn) in devices.items():
            if inp != "dummy" and inp not in devices:
                err(f"{cfg}: powertrain device {dev} ({pn}) takes input from missing {inp}")
        for need in ("mainEngine", "gearbox", "differential_F", "wheelaxleFL", "wheelaxleFR"):
            if need not in devices:
                err(f"{cfg}: powertrain has no {need}")
        wheels = set()
        for pn in active:
            _h, rows = table_rows(parts[pn].get("pressureWheels"))
            wheels |= {r[0] for r, _pp in rows}
        if wheels != {"FL", "FR", "RL", "RR"}:
            err(f"{cfg}: wheels are {sorted(wheels)}")
        for pn in active:
            _h, rows = table_rows(parts[pn].get("powertrain"))
            for r, _pp in rows:
                if len(r) > 4 and isinstance(r[4], dict) and r[4].get("connectedWheel") not in (None, *wheels):
                    err(f"{cfg}: shaft {r[1]} drives unknown wheel {r[4]['connectedWheel']}")
        dof_check(cfg, parts, active)
        print(f"[validate] {cfg}: {len(active)} parts, {len(nodes)} nodes, {len(variables)} variables, "
              f"{len(devices)} powertrain devices")
    if not pcs:
        err("no .pc configurations")


def dof_check(cfg, parts, active):
    """Each suspension corner's knuckle must keep exactly one degree of freedom (wheel travel)."""
    beams = []
    for pn in active:
        if not pn.startswith("laguna2_suspension"):
            continue
        _h, rows = table_rows(parts[pn].get("beams"))
        for r, pp in rows:
            beams.append((r[0], r[1], pp.get("beamSpring")))
        _h, rows = table_rows(parts[pn].get("hydros"))
        for r, pp in rows:
            beams.append((r[0], r[1], "hydro"))
    for axle in "fr":
        for s in "lr":
            knuckle = {f"{axle}{k}{s}" for k in ("w1", "w2", "h1", "h2", "k1")}
            links = [b for b in beams if (b[0] in knuckle) != (b[1] in knuckle)
                     and not str(b[2]).startswith("$spring")]
            if len(links) != 5:
                err(f"{cfg}: corner {axle}{s} has {len(links)} rigid links to the body (need 5 for one DOF)")


if __name__ == "__main__":
    main()
    for w in WARNINGS:
        print("[warn]", w)
    for e in ERRORS:
        print("[ERROR]", e)
    print(f"[validate] {len(ERRORS)} errors, {len(WARNINGS)} warnings")
    sys.exit(1 if ERRORS else 0)
