"""Rebuild the whole Renault Laguna II mod, from the reference model to the installable zip.

Run:  python tools/build_all.py [--no-renders] [--draft]

Steps (each one can also be run on its own, see the script headers):
  1. tools/laguna2/build_from_ref.py   body, lamps, details  -> blender/laguna2_liftback.blend
  2. tools/laguna2/variants.py         customisation variants (glass, smoked lamps, steel wheel...)
  3. tools/laguna2/export_dae.py       one mesh per part     -> vehicles/renault_laguna/renault_laguna.dae, materials.json
  4. tools/beamng/gen_laguna2.py       jbeam parts, configurations, paints
  5. tools/beamng/validate.py          static checks of every configuration (stops the build on errors)
  6. renders (renders/ is cleared first): daylight set, photo overlays, night light states, configurations
  7. tools/package_mod.py              -> renault_laguna.zip (drop into BeamNG's mods folder)
"""

import glob
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLENDER = os.environ.get("BLENDER", r"C:\Program Files\Blender Foundation\Blender 5.3\blender.exe")
BLEND = os.path.join(ROOT, "blender", "laguna2_liftback.blend")
T = os.path.join(ROOT, "tools")


def run(args, label):
    print(f"\n=== {label} ===", flush=True)
    r = subprocess.run(args, cwd=ROOT)
    if r.returncode != 0:
        sys.exit(f"[build_all] {label} failed (exit {r.returncode})")


def blender(script, *extra, factory=False):
    args = [BLENDER, "--background"]
    args += ["--factory-startup"] if factory else [BLEND]
    args += ["--python", os.path.join(T, "laguna2", script)]
    if extra:
        args += ["--", *extra]
    return args


def main():
    draft = ["--draft"] if "--draft" in sys.argv else []
    run(blender("build_from_ref.py", factory=True), "build body")
    run(blender("variants.py"), "customisation variants")
    run(blender("export_dae.py"), "export meshes + materials")
    run([sys.executable, os.path.join(T, "beamng", "gen_laguna2.py")], "generate jbeam")
    run([sys.executable, os.path.join(T, "beamng", "validate.py")], "validate")
    if "--no-renders" not in sys.argv:
        for f in glob.glob(os.path.join(ROOT, "renders", "*.png")):
            os.remove(f)
        run(blender("render.py", "front34", "rear34", "side", "rear_low", "head_close", "tail_close",
                    "tail34_close", *draft), "daylight renders")
        run(blender("render.py", "tail_close", "tail34_close", "--paint=silver", "--suffix=_silver", *draft),
            "silver tail renders")
        run(blender("compare.py", "side", "front", "rear"), "photo overlays")
        run(blender("render_lights.py", *draft), "night light states")
        run(blender("render_configs.py", *draft), "configurations")
    run([sys.executable, os.path.join(T, "package_mod.py")], "package")
    print("\n[build_all] done")


if __name__ == "__main__":
    main()
