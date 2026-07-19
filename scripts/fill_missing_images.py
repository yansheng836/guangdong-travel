#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fill missing attraction images via Bing image search, one by one."""

from __future__ import annotations

import re
import ssl
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
CTX = ssl.create_default_context()


def http_get(url: str, timeout: int = 25) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept-Language": "zh-CN,zh;q=0.9",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as resp:
        return resp.read()


def list_missing(city: str) -> list[tuple[Path, str]]:
    city_dir = ROOT / city
    missing: list[tuple[Path, str]] = []
    for path in sorted(city_dir.glob(f"{city}-*.md")):
        text = path.read_text(encoding="utf-8")
        if re.search(r"!\[[^\]]*\]\(([^)]+)\)", text):
            continue
        title_match = re.search(r"^#\s+(.+)$", text, re.M)
        name = title_match.group(1).strip() if title_match else path.stem
        missing.append((path, name))
    return missing


def bing_candidates(query: str, limit: int = 12) -> list[tuple[str, int, int]]:
    encoded = urllib.parse.quote(query)
    url = f"https://cn.bing.com/images/search?q={encoded}&form=HDRSC2&first=1"
    try:
        html = http_get(url).decode("utf-8", "ignore")
    except Exception as exc:  # noqa: BLE001
        print(f"search_err {query}: {exc}")
        return []

    out: list[tuple[str, int, int]] = []

    def add(media: str, width: int = 0, height: int = 0) -> None:
        media = urllib.parse.unquote(urllib.parse.unquote(media)).replace("\\u0026", "&").replace("\\/", "/")
        if not media.startswith("http"):
            return
        # Prefer original URL embedded in Bing proxy links.
        if "riu=" in media:
            media = urllib.parse.unquote(media.split("riu=", 1)[1].split("&", 1)[0])
        out.append((media, width, height))

    for match in re.finditer(r"mediaurl=([^&\"']+)", html):
        add(match.group(1))
    for match in re.finditer(r"murl&quot;:&quot;(.*?)&quot;", html):
        add(match.group(1))
    for match in re.finditer(r'"murl":"(.*?)"', html):
        add(match.group(1))
    for match in re.finditer(r"mediaurl=([^&]+)&(?:amp;)?expw=(\d+)&(?:amp;)?exph=(\d+)", html):
        try:
            add(match.group(1), int(match.group(2)), int(match.group(3)))
        except ValueError:
            add(match.group(1))

    seen: set[str] = set()
    unique: list[tuple[str, int, int]] = []
    for item in out:
        if item[0] in seen:
            continue
        seen.add(item[0])
        unique.append(item)
    return unique[:limit]


def pick(cands: list[tuple[str, int, int]]) -> list[tuple[float, str, int, int]]:
    scored: list[tuple[float, str, int, int]] = []
    for url, width, height in cands:
        low = url.lower()
        if any(token in low for token in [".gif", ".svg", "logo", "avatar", "icon", "brand", "favicon"]):
            continue
        if width and height and width < 400:
            continue

        score = 0.0
        if width and height:
            score += min(width, 2000) / 10
            if width >= height:
                score += 200
            if width >= 800:
                score += 100
            if height >= 400:
                score += 50
        else:
            score += 80
        if any(host in low for host in ["ctrip", "qunar", "baidu", "bcebos", "sina", "pconline", "sohu", "oct"]):
            score += 30
        scored.append((score, url, width, height))

    scored.sort(reverse=True)
    return scored[:5]


def download(url: str, dest: Path) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(dest, "ab"):
            pass
    except Exception as exc:  # noqa: BLE001
        print(f"not writable {dest}: {exc}")
        return False

    try:
        data = http_get(url, timeout=30)
    except Exception as exc:  # noqa: BLE001
        print(f"dl_err {url[:100]}: {exc}")
        return False

    if len(data) < 20000:
        return False
    if not (data[:3] == b"\xff\xd8\xff" or data[:8] == b"\x89PNG\r\n\x1a\n" or data.startswith(b"RIFF")):
        if not data.startswith(b"\xff\xd8"):
            return False

    dest.write_bytes(data)
    return True


def source_label(url: str) -> str:
    host = urllib.parse.urlparse(url).netloc.lower()
    if "ctrip" in host:
        return "携程攻略"
    if "qunar" in host:
        return "去哪儿旅行"
    if "baidu" in host or "bcebos" in host:
        return "百度百科"
    if "sina" in host:
        return "新浪网"
    if "pconline" in host:
        return "太平洋摄影部落"
    if "sohu" in host:
        return "搜狐网"
    return host


def update_md(md_path: Path, base: str, label: str, source_url: str) -> bool:
    text = md_path.read_text(encoding="utf-8")
    title_match = re.search(r"^#\s+(.+)$", text, re.M)
    if not title_match:
        print(f"no title {md_path}")
        return False
    name = title_match.group(1).strip()

    section = re.search(r"(## 景点图片\s*\n)([\s\S]*?)(\n## )", text)
    if not section:
        print(f"no section {md_path}")
        return False

    # Parentheses in Markdown destinations must be percent-encoded.
    image_path = f"images/{base}_compressed.jpg".replace("(", "%28").replace(")", "%29")
    img_block = (
        f"![{name}]({image_path})\n\n"
        f"> 图片来源：[{label}]({source_url})\n"
    )
    updated = text[: section.start(2)] + "\n" + img_block + text[section.end(2) :]
    updated = re.sub(
        r"(## 最后更新时间\s*\n)(\d{4}-\d{2}-\d{2}|\s*)",
        r"\g<1>2026-07-19\n",
        updated,
        count=1,
    )
    md_path.write_text(updated, encoding="utf-8")
    return True


def process_city(city: str, max_n: int = 8) -> list[str]:
    missing = list_missing(city)
    count = min(max_n, len(missing))
    print(f"=== {city} missing={len(missing)} process={count} ===")
    ok: list[str] = []

    for index, (md_path, name) in enumerate(missing[:max_n], 1):
        base = md_path.stem
        orig = ROOT / city / "images" / f"{base}.jpg"
        query = f"{city} {name}"
        print(f"[{index}] {name} | {query}")

        candidates = pick(bing_candidates(query))
        if not candidates:
            print("  no candidates")
            continue

        success = False
        for score, url, width, height in candidates:
            print(f"  try score={score:.0f} {width}x{height} {url[:100]}")
            if not download(url, orig):
                continue
            print(f"  saved {orig.stat().st_size}")
            if update_md(md_path, base, source_label(url), url):
                ok.append(base)
                success = True
                break

        if not success:
            print("  all downloads failed")
        time.sleep(0.8)

    return ok


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/fill_missing_images.py <城市> [max_n]")
        sys.exit(1)
    city = sys.argv[1]
    max_n = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    result = process_city(city, max_n)
    print("DONE", len(result), result)


if __name__ == "__main__":
    main()
