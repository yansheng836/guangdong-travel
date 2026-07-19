#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Repair broken attraction image references by re-downloading via Bing."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from fill_missing_images import (  # type: ignore
    bing_candidates,
    download,
    pick,
    source_label,
    update_md,
)


def broken_pages(city: str) -> list[tuple[Path, str]]:
    city_dir = ROOT / city
    out: list[tuple[Path, str]] = []
    for path in sorted(city_dir.glob(f"{city}-*.md")):
        text = path.read_text(encoding="utf-8")
        refs = re.findall(r"!\[[^\]]*\]\((images/[^)]+)\)", text)
        if not refs:
            continue
        bad = False
        for rel in refs:
            p = city_dir / rel.replace("%28", "(").replace("%29", ")")
            if not p.exists():
                bad = True
                break
        if not bad:
            continue
        title_match = re.search(r"^#\s+(.+)$", text, re.M)
        name = title_match.group(1).strip() if title_match else path.stem
        out.append((path, name))
    return out


def clear_image_section(md_path: Path) -> None:
    text = md_path.read_text(encoding="utf-8")
    section = re.search(r"(## 景点图片\s*\n)([\s\S]*?)(\n## )", text)
    if not section:
        return
    updated = text[: section.start(2)] + "\n" + text[section.end(2) :]
    md_path.write_text(updated, encoding="utf-8")


def repair_city(city: str, max_n: int = 50) -> list[str]:
    pages = broken_pages(city)
    print(f"=== {city} broken={len(pages)} process={min(max_n, len(pages))} ===")
    ok: list[str] = []
    for index, (md_path, name) in enumerate(pages[:max_n], 1):
        base = md_path.stem
        orig = ROOT / city / "images" / f"{base}.jpg"
        query = f"{city} {name}"
        print(f"[{index}] {name} | {query}")
        clear_image_section(md_path)
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
    print("DONE", len(ok), ok)
    return ok


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/repair_broken_images.py <城市> [max_n]")
        sys.exit(1)
    city = sys.argv[1]
    max_n = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    repair_city(city, max_n)


if __name__ == "__main__":
    main()
