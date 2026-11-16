"""
Package Renault Laguna Mod into a BeamNG-ready ZIP file.
"""

import os
import zipfile
import shutil

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VEHICLES_DIR = os.path.join(PROJECT_ROOT, "vehicles")
OUTPUT_ZIP = os.path.join(PROJECT_ROOT, "renault_laguna.zip")

def package():
    print(f"[Package] Packaging Renault Laguna mod from {VEHICLES_DIR}...")
    if os.path.exists(OUTPUT_ZIP):
        os.remove(OUTPUT_ZIP)

    with zipfile.ZipFile(OUTPUT_ZIP, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(VEHICLES_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, PROJECT_ROOT)
                zipf.write(file_path, rel_path)
                print(f"  + Added {rel_path}")

    print(f"\n[Package] Done! Mod packaged to: {OUTPUT_ZIP} ({os.path.getsize(OUTPUT_ZIP)} bytes)")
    print("Drag and drop this .zip file directly into your BeamNG mods folder: %LOCALAPPDATA%\\BeamNG.drive\\<version>\\mods\\")

if __name__ == "__main__":
    package()
