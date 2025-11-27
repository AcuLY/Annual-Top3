import json
import os
import requests

INPUT_FILE = "./src/constant/2025.json"
OUTPUT_DIR = "./src/assets/images"

def download_image(url, path):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        with open(path, "wb") as f:
            f.write(resp.content)
        print(f"✔ Saved: {path}")
    except Exception as e:
        print(f"✘ Failed: {url} ({e})")

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        items = json.load(f)

    for item in items:
        img_url = item.get("image")
        if not img_url:
            continue

        img_id = item.get("id")
        ext = img_url.split("?")[0].split(".")[-1]  # 取扩展名
        if len(ext) > 5:
            ext = "jpg"

        filename = f"{img_id}.{ext}"
        filepath = os.path.join(OUTPUT_DIR, filename)

        download_image(img_url, filepath)

if __name__ == "__main__":
    main()
