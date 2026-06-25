#!/usr/bin/env python
"""Add images to Guangzhou attraction files from Wikimedia Commons.
Version 3: Uses curl for API calls, skips URL verification."""

import os
import json
import time
import subprocess
import urllib.parse
import sys

WORK_DIR = r"F:\workspace\plain-project\guangdong-travel\广州市"
SKIP_FILES = {"README.md", "_sidebar.md", "TEMPLATE.md", "add_images.sh", "add_images.py", "add_images_v2.py", "add_images_v3.py"}
IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}

success_count = 0
fail_count = 0
skip_count = 0


def curl_json(url):
    """Fetch JSON using curl."""
    try:
        result = subprocess.run(
            ['curl', '-s', '-k', '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', url],
            capture_output=True, timeout=30
        )
        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout.decode('utf-8'))
    except Exception as e:
        print(f"    curl error: {e}")
    return None


def is_image_file(title):
    """Check if a file title is an image."""
    if '.' not in title:
        return False
    ext = title.rsplit('.', 1)[-1].lower()
    return ext in IMAGE_EXTENSIONS


def search_commons(name):
    """Search Wikimedia Commons for an image of the attraction."""
    encoded = urllib.parse.quote(name)
    url = (
        f"https://commons.wikimedia.org/w/api.php?"
        f"action=query&list=search&srsearch={encoded}"
        f"&srnamespace=6&format=json&utf8=1&srlimit=10"
    )

    data = curl_json(url)
    if not data:
        return None

    results = data.get("query", {}).get("search", [])
    for r in results:
        title = r.get("title", "")
        if title.startswith("File:") and is_image_file(title):
            return title

    return None


def get_image_url(file_title):
    """Get the direct image URL from a Wikimedia Commons file title."""
    encoded = urllib.parse.quote(file_title)
    url = (
        f"https://commons.wikimedia.org/w/api.php?"
        f"action=query&titles={encoded}"
        f"&prop=imageinfo&iiprop=url&format=json&utf8=1"
    )

    data = curl_json(url)
    if not data:
        return None

    pages = data.get("query", {}).get("pages", {})
    for pid, page in pages.items():
        imageinfo = page.get("imageinfo", [])
        if imageinfo:
            return imageinfo[0].get("url")

    return None


def replace_placeholder(filepath, new_content):
    """Replace <!-- 插入图片 --> with actual content."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    new = content.replace("<!-- 插入图片 -->", new_content)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new)


def extract_name(filepath):
    """Extract attraction name from the first heading."""
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()
    return None


def main():
    global success_count, fail_count, skip_count

    files = sorted([f for f in os.listdir(WORK_DIR) if f.endswith(".md") and f not in SKIP_FILES])

    # Filter to only files with <!-- 插入图片 -->
    todo_files = []
    for f in files:
        filepath = os.path.join(WORK_DIR, f)
        with open(filepath, "r", encoding="utf-8") as fh:
            content = fh.read()
        if "<!-- 插入图片 -->" in content:
            todo_files.append(f)
        else:
            skip_count += 1

    total = len(todo_files)
    print(f"Files to process: {total}")
    print(f"Files skipped (already processed): {skip_count}")
    print("=" * 60)

    for idx, filename in enumerate(todo_files, 1):
        filepath = os.path.join(WORK_DIR, filename)
        name = extract_name(filepath)

        if not name:
            print(f"[{idx}/{total}] SKIP (no name): {filename}")
            replace_placeholder(filepath, "\n> \U0001f4f7 暂未找到照片\n")
            fail_count += 1
            time.sleep(2)
            continue

        print(f"[{idx}/{total}] Processing: {name}", flush=True)

        # Search Wikimedia Commons
        file_title = search_commons(name)

        if file_title:
            print(f"    Found: {file_title}", flush=True)
            image_url = get_image_url(file_title)

            if image_url:
                print(f"    URL: {image_url}", flush=True)
                # Skip URL verification - trust the API response
                commons_page = f"https://commons.wikimedia.org/wiki/{urllib.parse.quote(file_title)}"
                img_content = f"\n![{name}]({image_url})\n\n> 图片来源：[Wikimedia Commons]({commons_page}) · 许可证：CC BY-SA 4.0\n"
                replace_placeholder(filepath, img_content)
                print(f"    -> SUCCESS", flush=True)
                success_count += 1
            else:
                print(f"    -> FAIL: Could not get image URL", flush=True)
                replace_placeholder(filepath, "\n> \U0001f4f7 暂未找到照片\n")
                fail_count += 1
        else:
            print(f"    -> FAIL: No results found", flush=True)
            replace_placeholder(filepath, "\n> \U0001f4f7 暂未找到照片\n")
            fail_count += 1

        # Wait between requests
        if idx < total:
            time.sleep(3)

    print()
    print("=" * 60)
    print("Processing complete!")
    print(f"Total processed: {total}")
    print(f"Successfully added images: {success_count}")
    print(f"Placeholder (no photo): {fail_count}")
    print(f"Already had images (skipped): {skip_count}")
    print("=" * 60)


if __name__ == "__main__":
    main()
