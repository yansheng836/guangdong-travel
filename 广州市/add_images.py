#!/usr/bin/env python
"""Add images to Guangzhou attraction files from Wikimedia Commons."""

import os
import json
import time
import re
import urllib.request
import urllib.parse
import hashlib
import sys

WORK_DIR = r"F:\workspace\plain-project\guangdong-travel\广州市"
SKIP_FILES = {"README.md", "_sidebar.md", "TEMPLATE.md", "add_images.sh", "add_images.py"}

USER_AGENT = "Mozilla/5.0 (compatible; GuangdongTravelBot/1.0; educational project)"

success_count = 0
fail_count = 0
skip_count = 0


def api_request(url):
    """Make a request to Wikimedia API."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"    API error: {e}")
        return None


def search_commons(name):
    """Search Wikimedia Commons for an image of the attraction."""
    # Try multiple search strategies
    search_terms = [
        name,
        name.replace("公园", "").replace("景区", "").replace("博物馆", "").strip(),
    ]

    for term in search_terms:
        if len(term) < 2:
            continue

        encoded = urllib.parse.quote(term)
        url = (
            f"https://commons.wikimedia.org/w/api.php?"
            f"action=query&list=search&srsearch={encoded}"
            f"&srnamespace=6&format=json&utf8=1&srlimit=5"
        )

        data = api_request(url)
        if not data:
            continue

        results = data.get("query", {}).get("search", [])
        for r in results:
            title = r.get("title", "")
            if title.startswith("File:"):
                return title

        time.sleep(1)

    return None


def get_image_url(file_title):
    """Get the direct image URL from a Wikimedia Commons file title."""
    encoded = urllib.parse.quote(file_title)
    url = (
        f"https://commons.wikimedia.org/w/api.php?"
        f"action=query&titles={encoded}"
        f"&prop=imageinfo&iiprop=url&format=json&utf8=1"
    )

    data = api_request(url)
    if not data:
        return None

    pages = data.get("query", {}).get("pages", {})
    for pid, page in pages.items():
        imageinfo = page.get("imageinfo", [])
        if imageinfo:
            return imageinfo[0].get("url")

    return None


def verify_url(url):
    """Verify a URL returns HTTP 200."""
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status == 200
    except Exception:
        return False


def add_image_to_file(filepath, name, image_url, commons_page):
    """Insert image section into the file after the first heading."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    new_lines = []
    inserted = False

    for i, line in enumerate(lines):
        new_lines.append(line)
        if not inserted and line.startswith("# ") and i == 0:
            new_lines.append("")
            new_lines.append("## 景点图片")
            new_lines.append("")
            new_lines.append(f"![{name}]({image_url})")
            new_lines.append("")
            new_lines.append(f"> 图片来源：[Wikimedia Commons]({commons_page}) · 许可证：CC BY-SA 4.0")
            new_lines.append("")
            inserted = True

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))


def add_placeholder(filepath):
    """Insert placeholder section into the file after the first heading."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    new_lines = []
    inserted = False

    for i, line in enumerate(lines):
        new_lines.append(line)
        if not inserted and line.startswith("# ") and i == 0:
            new_lines.append("")
            new_lines.append("## 景点图片")
            new_lines.append("")
            new_lines.append("> 📷 暂未找到照片")
            new_lines.append("")
            inserted = True

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))


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
    total = len(files)

    print(f"Found {total} attraction files to process")
    print("=" * 50)

    processed = 0
    for filename in files:
        filepath = os.path.join(WORK_DIR, filename)

        # Check if already has image or placeholder
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        if "![" in content or "暂未找到照片" in content:
            skip_count += 1
            continue

        processed += 1
        name = extract_name(filepath)
        if not name:
            print(f"[{processed}] SKIP (no name): {filename}")
            add_placeholder(filepath)
            fail_count += 1
            time.sleep(2.5)
            continue

        print(f"[{processed}] Processing: {name}")

        # Search Wikimedia Commons
        file_title = search_commons(name)

        if file_title:
            print(f"    Found: {file_title}")
            image_url = get_image_url(file_title)

            if image_url:
                print(f"    URL: {image_url}")
                # Verify URL
                if verify_url(image_url):
                    commons_page = f"https://commons.wikimedia.org/wiki/{urllib.parse.quote(file_title)}"
                    add_image_to_file(filepath, name, image_url, commons_page)
                    print(f"    -> SUCCESS")
                    success_count += 1
                else:
                    print(f"    -> FAIL: URL not accessible")
                    add_placeholder(filepath)
                    fail_count += 1
            else:
                print(f"    -> FAIL: Could not get image URL")
                add_placeholder(filepath)
                fail_count += 1
        else:
            print(f"    -> FAIL: No results found")
            add_placeholder(filepath)
            fail_count += 1

        # Wait 2-3 seconds between requests
        time.sleep(2.5)

    print()
    print("=" * 50)
    print("Processing complete!")
    print(f"Total processed: {processed}")
    print(f"Successfully added images: {success_count}")
    print(f"Placeholder (no photo): {fail_count}")
    print(f"Already had images (skipped): {skip_count}")
    print("=" * 50)


if __name__ == "__main__":
    main()
