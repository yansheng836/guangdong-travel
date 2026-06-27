"""
批量压缩项目图片，可选自动更新景点文件引用。

用法:
    python compress.py                        # 默认只压缩图片
    python compress.py --update               # 压缩 + 更新景点文件引用
    python compress.py 广州市/ 深圳市/         # 指定目录
    python compress.py --quality 85            # 自定义质量
    python compress.py --max-w 1600            # 自定义最大宽度
    python compress.py --dry-run               # 预览，不写入

参数:
    --update          同时扫描景点 .md 文件，自动替换图片引用链接
    --quality N       JPEG 质量 1-100 (默认 75)
    --max-w N         最大宽度像素 (默认 1920)
    --dry-run         预览模式，不实际写入
"""

import argparse
import os
import re
from pathlib import Path

from PIL import Image

# ── 常量 ──────────────────────────────────────────────
SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
DEFAULT_QUALITY = 75
DEFAULT_MAX_WIDTH = 1920
COMPRESSION_SUFFIX = "_compressed"


# ── 核心函数 ──────────────────────────────────────────

def compress_image(filepath: Path, quality: int, max_width: int, dry_run: bool = False) -> dict | None:
    """压缩单张图片。

    返回 {file, original_size, compressed_size, reduction, output}。
    dry_run=True 时通过 BytesIO 计算大小但不落盘。
    """
    try:
        img = Image.open(filepath)
    except Exception as e:
        return {"file": filepath.name, "error": str(e)}

    original_format = img.format
    if img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")

    width, height = img.size
    if width > max_width:
        ratio = max_width / width
        new_size = (int(width * ratio), int(height * ratio))
        img = img.resize(Image.LANCZOS, new_size)
        width, height = img.size

    out_format = "JPEG" if original_format and original_format.upper() in ("JPEG", "JPG") else "JPEG"
    out_ext = ".jpg" if out_format == "JPEG" else ".webp"
    out_path = filepath.with_stem(filepath.stem + COMPRESSION_SUFFIX).with_suffix(out_ext)

    save_kwargs: dict = {"optimize": True} if out_format == "JPEG" else {}
    save_kwargs["quality"] = quality

    if dry_run:
        from io import BytesIO
        buf = BytesIO()
        img.save(buf, format=out_format, **save_kwargs)
        compressed_size = len(buf.getvalue())
        buf.close()
    else:
        img.save(out_path, **save_kwargs)
        compressed_size = out_path.stat().st_size

    original_size = filepath.stat().st_size
    reduction = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0

    return {
        "file": filepath.name,
        "original_size": original_size,
        "compressed_size": compressed_size,
        "reduction": reduction,
        "output": str(out_path),
    }


def update_md_links(md_path: Path, old_rel: str, new_rel: str) -> bool:
    """将 markdown 文件中的图片链接从 old_rel 替换为 new_rel。"""
    content = md_path.read_text(encoding="utf-8")
    if old_rel not in content:
        return False
    new_content = re.sub(
        rf'!\[([^\]]*)\]\({re.escape(old_rel)}\)',
        rf'![\1]({new_rel})',
        content,
    )
    md_path.write_text(new_content, encoding="utf-8")
    return True


def find_image_ref(md_path: Path, image_filename: str) -> tuple[str | None, str | None]:
    """在 md 文件中查找图片引用，返回 (relative_path, alt_text)。"""
    content = md_path.read_text(encoding="utf-8")
    pattern = rf'!\[([^\]]*)\]\((images/{re.escape(image_filename)})\)'
    m = re.search(pattern, content)
    if m:
        return m.group(2), m.group(1)
    return None, None


def scan_md_files(dirs: list[Path]) -> list[Path]:
    """扫描所有景点 .md 文件（排除 README.md）。"""
    files = []
    for root in dirs:
        if not root.is_dir():
            continue
        for md in root.rglob("*.md"):
            if md.name == "README.md":
                continue
            files.append(md)
    return sorted(files)


def collect_images(dirs: list[Path]) -> list[Path]:
    """收集待压缩的图片文件，排除已有压缩文件的和图片本身是压缩产物。"""
    files = []
    for d in dirs:
        if not d.is_dir():
            continue
        for ext in SUPPORTED_EXTS:
            files.extend(d.rglob(f"*{ext}"))
            files.extend(d.rglob(f"*{ext.upper()}"))
    files = sorted(set(files))

    result = []
    for f in files:
        # 跳过压缩产物
        if COMPRESSION_SUFFIX in f.stem:
            continue
        # 跳过已有对应压缩文件的
        out = f.with_stem(f.stem + COMPRESSION_SUFFIX)
        if out.suffix.lower() in (".jpg", ".jpeg"):
            out = out.with_suffix(".jpg")
        elif out.suffix.lower() == ".webp":
            out = out.with_suffix(".webp")
        if out.exists():
            continue
        result.append(f)
    return result


# ── 辅助 ──────────────────────────────────────────────

def _size_str(b: int) -> str:
    if b < 1024 * 1024:
        return f"{b / 1024:.1f}KB"
    return f"{b / (1024*1024):.2f}MB"


# ── 主流程 ────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="批量压缩项目图片，可选自动更新景点文件引用。",
        epilog="默认只压缩图片；加 --update 才会更新引用链接。",
    )
    parser.add_argument("dirs", nargs="*", default=[Path(".")], type=Path, help="扫描目录 (默认当前目录)")
    parser.add_argument("--update", action="store_true", help="压缩的同时更新景点 .md 文件中的图片引用")
    parser.add_argument("--quality", type=int, default=DEFAULT_QUALITY, help=f"JPEG 质量 1-100 (默认 {DEFAULT_QUALITY})")
    parser.add_argument("--max-w", type=int, default=DEFAULT_MAX_WIDTH, help=f"最大宽度 px (默认 {DEFAULT_MAX_WIDTH})")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不实际写入")
    args = parser.parse_args()

    quality = max(1, min(100, args.quality))
    max_width = args.max_w
    mode = "引用更新" if args.update else "仅压缩"
    flag = "[预览]" if args.dry_run else "[写入]"

    # 1. 收集图片
    image_files = collect_images(args.dirs)
    if not image_files:
        print("未找到待压缩的图片。")
        return

    # 2. 如需更新引用，收集景点文件
    md_files = scan_md_files(args.dirs) if args.update else []

    print(f"发现 {len(image_files)} 张图片, {len(md_files)} 个景点文件")
    print(f"模式={mode}, 质量={quality}, 最大宽={max_width}px, {flag}")
    print("=" * 70)

    total_original = 0
    total_compressed = 0
    updated_files = 0
    failed = 0

    for img_file in image_files:
        result = compress_image(img_file, quality, max_width, dry_run=args.dry_run)
        if result is None or "error" in result:
            print(f"  [失败] {img_file.relative_to(args.dirs[0])}")
            failed += 1
            continue

        total_original += result["original_size"]
        total_compressed += result["compressed_size"]
        reduction = result["reduction"]

        print(f"  [{_size_str(result['original_size'])} -> {_size_str(result['compressed_size'])}] "
              f"{img_file.relative_to(Path('.'))} ({reduction:.1f}%)")

        # 3. 更新景点文件引用
        if args.update:
            for md in md_files:
                ref_path, _alt = find_image_ref(md, img_file.name)
                if ref_path is None:
                    continue
                md_dir = md.parent.resolve()
                new_rel = Path(os.path.relpath(result["output"], md_dir))
                if update_md_links(md, ref_path, str(new_rel)):
                    updated_files += 1
                    print(f"    ↳ {md.relative_to(Path('.'))}: {ref_path} -> {new_rel}")

    print("=" * 70)
    total_reduction = (1 - total_compressed / total_original) * 100 if total_original > 0 else 0
    print(f"完成: {len(image_files)} 张压缩, {updated_files} 个引用已更新, {failed} 失败")
    print(f"节省: {_size_str(total_original - total_compressed)} ({total_reduction:.1f}%)")


if __name__ == "__main__":
    main()
