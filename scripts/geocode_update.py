"""
使用高德地理编码 API 批量更新景点坐标
从景点 Markdown 文件中提取地址，调用高德 API 获取 GCJ-02 坐标
"""
import json
import os
import re
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
AMAP_KEY = os.environ.get("AMAP_KEY")
if not AMAP_KEY:
    print("错误：未设置环境变量 AMAP_KEY")
    print("请先设置高德 Web 服务 API Key：")
    print("  export AMAP_KEY='你的API Key'  (Linux/Mac)")
    print("  set AMAP_KEY=你的API Key       (Windows CMD)")
    print("  $env:AMAP_KEY='你的API Key'    (Windows PowerShell)")
    sys.exit(1)
RATE_LIMIT = 3  # 每秒请求数


def geocode(address, city=""):
    """调用高德地理编码 API，返回 (lng, lat) 或 None"""
    params = {
        "key": AMAP_KEY,
        "address": address,
        "city": city,
        "output": "JSON",
    }
    url = "https://restapi.amap.com/v3/geocode/geo?" + urllib.parse.urlencode(params)

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if data.get("status") != "1":
            return None, data.get("info", "unknown error")

        geocodes = data.get("geocodes", [])
        if not geocodes:
            return None, "no results"

        loc = geocodes[0].get("location", "")
        if not loc:
            return None, "empty location"

        parts = loc.split(",")
        if len(parts) != 2:
            return None, "bad location format"

        return (round(float(parts[0]), 4), round(float(parts[1]), 4)), None

    except Exception as e:
        return None, str(e)


def extract_fields(content):
    """从 Markdown 内容中提取景点信息"""
    # 景点名称（第一个 # 标题）
    name_match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
    name = name_match.group(1).strip() if name_match else ""

    # 基本信息表格
    table_rows = re.findall(r'\|\s*(.+?)\s*\|\s*(.+?)\s*\|', content)
    field_map = {k.strip(): v.strip() for k, v in table_rows}

    city = field_map.get('所在城市', '')
    district = field_map.get('所在区县', '')

    # 地址
    addr_match = re.search(r'\*\*地址\*\*[：:]\s*(.+?)$', content, re.MULTILINE)
    address = addr_match.group(1).strip() if addr_match else ""

    # 当前经纬度
    coord_match = re.search(
        r'([\d.]+)\s*°?[NS]?[,，]\s*([\d.]+)\s*°?[EW]?',
        content,
    )
    old_lat = float(coord_match.group(1)) if coord_match else None
    old_lng = float(coord_match.group(2)) if coord_match else None

    return {
        "name": name,
        "city": city,
        "district": district,
        "address": address,
        "old_lat": old_lat,
        "old_lng": old_lng,
    }


def update_md_coords(md_path, new_lng, new_lat):
    """更新 Markdown 文件中的经纬度"""
    content = md_path.read_text(encoding='utf-8')

    # 替换经纬度行
    new_coord_line = f'{new_lat}°N, {new_lng}°E'
    content = re.sub(
        r'[\d.]+\s*°?[NS]?[,、\s]\s*[\d.]+\s*°?[EW]?',
        new_coord_line,
        content,
        count=1,
    )

    md_path.write_text(content, encoding='utf-8')


def main():
    filter_city = None
    skip_cities = []
    args_list = sys.argv[1:]
    for arg in args_list:
        if arg.startswith('--city='):
            filter_city = arg.split('=', 1)[1]
        elif arg.startswith('--skip='):
            skip_cities = arg.split('=', 1)[1].split(',')

    # 发现城市目录
    city_dirs = sorted(
        d.name for d in BASE_DIR.iterdir()
        if d.is_dir() and d.name.endswith('市') and not d.name.startswith('.')
    )
    if filter_city:
        city_dirs = [c for c in city_dirs if c == filter_city]
    if skip_cities:
        city_dirs = [c for c in city_dirs if c not in skip_cities]

    # 收集所有景点文件
    all_files = []
    for city in city_dirs:
        city_dir = BASE_DIR / city
        for fname in sorted(os.listdir(city_dir)):
            if not fname.endswith('.md') or fname in ('README.md', '_sidebar.md'):
                continue
            all_files.append((city, city_dir, fname))

    total = len(all_files)
    success = 0
    failed = 0
    skipped = 0
    same = 0

    print(f"Found {total} attractions in {len(city_dirs)} cities")
    if filter_city:
        print(f"  (filtered to: {filter_city})")
    print()

    for idx, (city, city_dir, fname) in enumerate(all_files, 1):
        fpath = city_dir / fname
        content = fpath.read_text(encoding='utf-8')
        fields = extract_fields(content)

        name = fields["name"]
        addr = fields["address"]
        city_name = fields["city"]
        old_lat = fields["old_lat"]
        old_lng = fields["old_lng"]

        # 构造查询字符串
        if addr:
            query = addr
            if not addr.startswith(city_name):
                query = city_name + addr
        else:
            query = f"{city_name}{name}"

        # 调用 API
        result, err = geocode(query, city_name)

        if result is None:
            # 第二次尝试：只用景点名称
            result, err2 = geocode(f"{city_name}{name}", city_name)

        if result is None:
            print(f"[{idx:4d}/{total}] {name:<20s}  FAILED: {err}")
            failed += 1
            time.sleep(1.0 / RATE_LIMIT)
            continue

        new_lng, new_lat = result

        # 对比新旧坐标
        if old_lat is not None and old_lng is not None:
            dlat = round(new_lat - old_lat, 4)
            dlng = round(new_lng - old_lng, 4)
            dist = round((dlat**2 + dlng**2)**0.5 * 111000)
            if abs(dlat) < 0.0001 and abs(dlng) < 0.0001:
                print(f"[{idx:4d}/{total}] {name:<20s}  SAME ({new_lat}, {new_lng})")
                same += 1
                time.sleep(1.0 / RATE_LIMIT)
                continue
        else:
            dlat, dlng, dist = "?", "?", "?"

        # 更新文件
        update_md_coords(fpath, new_lng, new_lat)
        print(f"[{idx:4d}/{total}] {name:<20s}  ({old_lat}, {old_lng}) -> ({new_lat}, {new_lng})  dlat={dlat}, dlng={dlng}, ~{dist}m")
        success += 1

        time.sleep(1.0 / RATE_LIMIT)

    print(f"\n{'='*50}")
    print(f"Done!  total={total}, updated={success}, same={same}, failed={failed}")


if __name__ == '__main__':
    main()