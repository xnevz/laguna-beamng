"""
Download high-resolution reference images for Renault Laguna I, II, and III
Directly into blender/references/
"""

import urllib.request
import json
import os
import time

HEADERS = {"User-Agent": "AntigravityBeamNGModder/1.0 (https://github.com/AntigravityBeamNG; creative mod development)"}

TARGETS = [
    ("File:2005_Renault_Laguna_Dynamique_DCi_120_1.9_Front.jpg", "laguna2_front.jpg"),
    ("File:2005_Renault_Laguna_Dynamique_DCi_120_1.9_Rear.jpg", "laguna2_rear.jpg"),
    ("File:2005_Renault_Laguna_Dynamique_DCi_120_1.9_Side.jpg", "laguna2_side.jpg"),
    ("File:Renault_Laguna_I_front_20080215.jpg", "laguna1_front.jpg"),
    ("File:Renault_Laguna_I_Phase_I_RT_Heck.JPG", "laguna1_rear.jpg"),
    ("File:Renault_Laguna_III_Phase_I_front.JPG", "laguna3_front.jpg"),
    ("File:Renault_Laguna_III_Phase_I_rear.JPG", "laguna3_rear.jpg"),
    ("File:Renault_Laguna_III_Coupé_China_2012-05-06.jpg", "laguna3_coupe.jpg")
]

def fetch_image_url(file_title):
    api_url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(file_title)}&prop=imageinfo&iiprop=url&format=json"
    req = urllib.request.Request(api_url, headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        pages = data.get("query", {}).get("pages", {})
        for k, v in pages.items():
            if "imageinfo" in v and len(v["imageinfo"]) > 0:
                return v["imageinfo"][0]["url"]
    return None

def download_all():
    out_dir = os.path.abspath(r"blender\references")
    os.makedirs(out_dir, exist_ok=True)
    print(f"[References] Downloading Laguna references to {out_dir}...")

    for file_title, out_name in TARGETS:
        out_path = os.path.join(out_dir, out_name)
        if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
            print(f"  * Already downloaded: {out_name}")
            continue

        print(f"  -> Fetching URL for {file_title}...")
        try:
            url = fetch_image_url(file_title)
            if url:
                time.sleep(2.0)
                req = urllib.request.Request(url, headers=HEADERS)
                with urllib.request.urlopen(req) as resp, open(out_path, "wb") as f:
                    f.write(resp.read())
                print(f"  + Saved {out_name} ({os.path.getsize(out_path)} bytes)")
            else:
                print(f"  ! Could not find URL for {file_title}")
        except Exception as e:
            print(f"  ! Error downloading {file_title}: {e}")
        time.sleep(2.5)

if __name__ == "__main__":
    download_all()
