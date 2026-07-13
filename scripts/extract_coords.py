"""
提取所有景点文件中经纬度坐标，生成 attractions-geo.json
"""
import json
import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = BASE_DIR / 'attractions-geo.json'

# 自动发现城市目录（以"市"结尾的一级目录）
CITY_DIRS = sorted(
    d.name for d in BASE_DIR.iterdir()
    if d.is_dir() and d.name.endswith('市') and not d.name.startswith('.')
)

# 字段提取通用方法
def _extract_field(content, field_name):
    m = re.search(
        rf'\*\*{re.escape(field_name)}\*\*[：:]\s*(.+?)$', content, re.MULTILINE
    )
    return m.group(1).strip() if m else ''

# 匹配经纬度格式：- **经纬度**：23.1066°N, 113.3245°E
COORD_PATTERN = re.compile(
    r'\*\*经纬度\*\*[：:]\s*([\d.]+)°?[NS]?[,，\s]\s*([\d.]+)°?[EW]?'
)

attractions = []

for city in CITY_DIRS:
    city_dir = BASE_DIR / city
    for fname in sorted(os.listdir(city_dir)):
        if not fname.endswith('.md') or fname == 'README.md':
            continue

        fpath = city_dir / fname
        try:
            content = fpath.read_text(encoding='utf-8')
        except Exception:
            continue

        # 提取景点名称（第一个 # 标题）
        name_match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
        if not name_match:
            continue

        # 提取经纬度
        coord_match = COORD_PATTERN.search(content)
        if not coord_match:
            continue

        attractions.append({
            'name': name_match.group(1).strip(),
            'city': city,
            'district': _extract_field(content, '所在区县'),
            'level': _extract_field(content, '景点级别'),
            'type': _extract_field(content, '景点类型'),
            'lat': float(coord_match.group(1)),
            'lng': float(coord_match.group(2)),
            'file': fname,
            'path': f'{city}/{fname}',
        })

OUTPUT_FILE.write_text(
    json.dumps({'attractions': attractions}, ensure_ascii=False, indent=2),
    encoding='utf-8',
)

print(f'共提取 {len(attractions)} 个景点坐标')
print(f'已保存到 {OUTPUT_FILE}')