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
    """调用高德地理编码 API，返回 (lng, lat, level) 或 (None, None, error_msg)"""
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
            return None, None, data.get("info", "unknown error")

        geocodes = data.get("geocodes", [])
        if not geocodes:
            return None, None, "no results"

        loc = geocodes[0].get("location", "")
        if not loc:
            return None, None, "empty location"

        parts = loc.split(",")
        if len(parts) != 2:
            return None, None, "bad location format"

        level = geocodes[0].get("level", "")
        return (round(float(parts[0]), 4), round(float(parts[1]), 4)), level, None

    except Exception as e:
        return None, None, str(e)


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
        "type": field_map.get('景点类型', ''),
        "old_lat": old_lat,
        "old_lng": old_lng,
    }


def resolve_city_name(document_city, directory_city):
    """Return the document city, falling back to its scanned city directory."""
    return document_city.strip() or directory_city.strip()


def update_md_coords(md_path, new_lng, new_lat):
    """更新 Markdown 文件中的经纬度"""
    content = md_path.read_text(encoding='utf-8')

    # 替换经纬度行
    new_coord_line = f'{new_lat}°N, {new_lng}°E'
    content = re.sub(
        r'(\*\*经纬度\*\*[：:]\s*).+?$',
        rf'\g<1>{new_coord_line}',
        content,
        count=1,
        flags=re.MULTILINE,
    )

    md_path.write_text(content, encoding='utf-8')


def main():
    filter_city = None
    filter_name = None
    skip_cities = []
    args_list = sys.argv[1:]
    for arg in args_list:
        if arg.startswith('--city='):
            filter_city = arg.split('=', 1)[1]
        elif arg.startswith('--name='):
            filter_name = arg.split('=', 1)[1]
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

    # 按景点名筛选
    if filter_name:
        matched = []
        for city, city_dir, fname in all_files:
            content = (city_dir / fname).read_text(encoding='utf-8')
            name_match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
            if name_match and name_match.group(1).strip() == filter_name:
                matched.append((city, city_dir, fname))
        all_files = matched
        if not all_files:
            print(f"未找到名称为 '{filter_name}' 的景点")
            sys.exit(1)

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
        city_name = resolve_city_name(fields["city"], city)
        old_lat = fields["old_lat"]
        old_lng = fields["old_lng"]

        # 构造查询字符串：优先使用景点名称（POI 兴趣点级别），
        # 辅以城市名避免重名（如"广州市莲花山" vs "汕尾市莲花山"）
        name_query = f"{city_name}{name}"
        addr_query = f"{city_name}{addr}" if addr else None

        # 如果标题不含特征词，用"景点类型"字段拼接完整名称
        full_name_query = None
        type_suffixes = {'风景区','名胜区','景区','公园','广场','博物馆','故居','祠堂','寺庙','园林','展览馆','纪念馆','美术馆','图书馆','遗址','古镇'}
        if not any(name.endswith(s) for s in type_suffixes):
            ftype = fields.get('type', '')
            if ftype:
                full_name_query = f"{city_name}{name}{ftype}"

        # 好的 level 关键词：指向具体地点的级别
        good_levels = {'兴趣点', '风景名胜区', '景点', '景区', '旅游景点', '公园',
                       '博物馆', '展览馆', '纪念馆', '美术馆', '图书馆',
                       '广场', '寺庙', '教堂', '古建筑', '文物保护单位'}

        def is_good_level(lvl):
            return lvl in good_levels or any(kw in lvl for kw in good_levels)

        # 依次尝试多种查询策略，取级别最好的结果
        candidates = []  # [(result, level, source), ...]

        # 1. 景点名称（如"广州市白云山"）
        r1, l1, _ = geocode(name_query, city_name)
        if r1:
            candidates.append((r1, l1, '名称'))

        # 2. 地址（如"广州市白云区广园中路"）
        if addr_query:
            r2, l2, _ = geocode(addr_query, city_name)
            if r2:
                candidates.append((r2, l2, '地址'))

        # 3. 完整名称（如"广州市白云山风景名胜区"）
        if full_name_query:
            r3, l3, _ = geocode(full_name_query, city_name)
            if r3:
                candidates.append((r3, l3, '完整名称'))

        if not candidates:
            print(f"[{idx:4d}/{total}] {name:<20s}  FAILED: all queries returned no result")
            failed += 1
            time.sleep(1.0 / RATE_LIMIT)
            continue

        # 从候选中择优：优先 good level，再选第一个
        good = [c for c in candidates if is_good_level(c[1])]
        best = good[0] if good else candidates[0]
        result, level, src = best

        new_lng, new_lat = result

        # 对比新旧坐标
        if old_lat is not None and old_lng is not None:
            dlat = round(new_lat - old_lat, 4)
            dlng = round(new_lng - old_lng, 4)
            dist = round((dlat**2 + dlng**2)**0.5 * 111000)
            if abs(dlat) < 0.0001 and abs(dlng) < 0.0001:
                print(f"[{idx:4d}/{total}] {name:<20s}  SAME ({new_lat}, {new_lng})  [{level}]  src={src}")
                same += 1
                time.sleep(1.0 / RATE_LIMIT)
                continue
        else:
            dlat, dlng, dist = "?", "?", "?"

        # 更新文件
        update_md_coords(fpath, new_lng, new_lat)
        print(f"[{idx:4d}/{total}] {name:<20s}  ({old_lat}, {old_lng}) -> ({new_lat}, {new_lng})  dlat={dlat}, dlng={dlng}, ~{dist}m  [{level}]  src={src}")
        success += 1

        time.sleep(1.0 / RATE_LIMIT)

    print(f"\n{'='*50}")
    print(f"Done!  total={total}, updated={success}, same={same}, failed={failed}")


if __name__ == '__main__':
    main()
