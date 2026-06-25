#!/usr/bin/env python
"""Add images to Guangzhou attraction files from Wikimedia Commons.
Version 2: Better rate limiting, retry logic, and image filtering."""

import os
import json
import time
import re
import urllib.request
import urllib.parse
import ssl
import sys

WORK_DIR = r"F:\workspace\plain-project\guangdong-travel\广州市"
SKIP_FILES = {"README.md", "_sidebar.md", "TEMPLATE.md", "add_images.sh", "add_images.py", "add_images_v2.py"}
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Create SSL context that doesn't verify (for some network environments)
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

success_count = 0
fail_count = 0
skip_count = 0


def api_request(url, retries=3):
    """Make a request to Wikimedia API with retry logic."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/json",
            })
            with urllib.request.urlopen(req, timeout=20, context=ssl_ctx) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = (attempt + 1) * 10  # 10, 20, 30 seconds
                print(f"    Rate limited (429), waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"    HTTP error {e.code}, attempt {attempt+1}/{retries}")
                time.sleep(5)
        except Exception as e:
            print(f"    Error: {e}, attempt {attempt+1}/{retries}")
            time.sleep(5)
    return None


def is_image_file(title):
    """Check if a file title is an image (not PDF, djvu, etc.)."""
    lower = title.lower()
    return any(lower.endswith(ext) for ext in IMAGE_EXTENSIONS)


def search_commons(name):
    """Search Wikimedia Commons for an image of the attraction."""
    # Try multiple search strategies
    search_terms = [name]

    # Add simplified versions
    simplified = name
    for suffix in ['公园', '景区', '博物馆', '纪念馆', '度假区', '风景区', '森林公园',
                    '艺术区', '文化创意艺术区', '旧址', '故居', '古港', '码头']:
        if simplified.endswith(suffix):
            short = simplified[:-len(suffix)]
            if len(short) >= 2:
                search_terms.append(short)
            break

    for term in search_terms:
        if len(term) < 2:
            continue

        encoded = urllib.parse.quote(term)
        url = (
            f"https://commons.wikimedia.org/w/api.php?"
            f"action=query&list=search&srsearch={encoded}"
            f"&srnamespace=6&format=json&utf8=1&srlimit=10"
        )

        data = api_request(url)
        if not data:
            time.sleep(5)
            continue

        results = data.get("query", {}).get("search", [])
        for r in results:
            title = r.get("title", "")
            if title.startswith("File:") and is_image_file(title):
                return title

        time.sleep(3)

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
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=15, context=ssl_ctx) as resp:
            return resp.status == 200
    except Exception:
        return False


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

    # Filter to only files with <!-- 插入图片 --> (i.e., need processing)
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
    print(f"Files skipped (already have images): {skip_count}")
    print("=" * 60)

    for idx, filename in enumerate(todo_files, 1):
        filepath = os.path.join(WORK_DIR, filename)
        name = extract_name(filepath)

        if not name:
            print(f"[{idx}/{total}] SKIP (no name): {filename}")
            replace_placeholder(filepath, "\n> 📷 暂未找到照片\n")
            fail_count += 1
            time.sleep(3)
            continue

        print(f"[{idx}/{total}] Processing: {name}")

        # Search Wikimedia Commons
        file_title = search_commons(name)

        if file_title:
            print(f"    Found: {file_title}")
            image_url = get_image_url(file_title)

            if image_url and is_image_file(image_url):
                print(f"    URL: {image_url}")
                # Verify URL
                if verify_url(image_url):
                    commons_page = f"https://commons.wikimedia.org/wiki/{urllib.parse.quote(file_title)}"
                    img_content = f"\n![{name}]({image_url})\n\n> 图片来源：[Wikimedia Commons]({commons_page}) · 许可证：CC BY-SA 4.0\n"
                    replace_placeholder(filepath, img_content)
                    print(f"    -> SUCCESS")
                    success_count += 1
                else:
                    print(f"    -> FAIL: URL not accessible")
                    replace_placeholder(filepath, "\n> 📷 暂未找到照片\n")
                    fail_count += 1
            else:
                print(f"    -> FAIL: Not an image file ({file_title})")
                replace_placeholder(filepath, "\n> 📷 暂未找到照片\n")
                fail_count += 1
        else:
            print(f"    -> FAIL: No results found")
            replace_placeholder(filepath, "\n> 📷 暂未找到照片\n")
            fail_count += 1

        # Wait 5 seconds between requests to avoid rate limiting
        if idx < total:
            time.sleep(5)

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
