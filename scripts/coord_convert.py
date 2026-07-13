"""
WGS-84 转 GCJ-02 坐标转换（火星坐标系）
用于校准景点经纬度以匹配高德地图瓦片
"""
import json
import math
import re
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Krasovsky 1940 椭球参数
A = 6378245.0          # 半长轴
EE = 0.00669342162296594323  # 第一偏心率平方

def _is_out_of_china(lat, lng):
    """粗略判断是否不在中国境内"""
    return not (0.8293 <= lat <= 55.8271 and 72.004 <= lng <= 137.8347)

def _transform_lat(x, y):
    ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))
    ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(y * math.pi) + 40.0 * math.sin(y / 3.0 * math.pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(y / 12.0 * math.pi) + 320.0 * math.sin(y * math.pi / 30.0)) * 2.0 / 3.0
    return ret

def _transform_lng(x, y):
    ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
    ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(x * math.pi) + 40.0 * math.sin(x / 3.0 * math.pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(x / 12.0 * math.pi) + 300.0 * math.sin(x / 30.0 * math.pi)) * 2.0 / 3.0
    return ret

def wgs84_to_gcj02(wgs_lat, wgs_lng):
    """
    WGS-84 转 GCJ-02（火星坐标）
    返回 (gcj_lat, gcj_lng)
    """
    if _is_out_of_china(wgs_lat, wgs_lng):
        return wgs_lat, wgs_lng

    dlat = _transform_lat(wgs_lng - 105.0, wgs_lat - 35.0)
    dlng = _transform_lng(wgs_lng - 105.0, wgs_lat - 35.0)

    radlat = wgs_lat / 180.0 * math.pi
    magic = math.sin(radlat)
    magic = 1.0 - EE * magic * magic
    sqrtmagic = math.sqrt(magic)

    dlat = (dlat * 180.0) / ((A * (1.0 - EE)) / (magic * sqrtmagic) * math.pi)
    dlng = (dlng * 180.0) / (A / sqrtmagic * math.cos(radlat) * math.pi)

    gcj_lat = wgs_lat + dlat
    gcj_lng = wgs_lng + dlng

    return round(gcj_lat, 4), round(gcj_lng, 4)


def convert_file(md_path):
    """
    转换单个景点 Markdown 文件的经纬度为 GCJ-02
    返回 (old_coord, new_coord) 或 None
    """
    content = md_path.read_text(encoding='utf-8')

    # 匹配经纬度格式：- **经纬度**：23.1066°N, 113.3245°E
    coord_pattern = re.compile(
        r'(\*\*经纬度\*\*[：:]\s*)([\d.]+)°?[NS]?[,，\s]\s*([\d.]+)°?[EW]?'
    )

    match = coord_pattern.search(content)
    if not match:
        return None

    prefix = match.group(1)
    old_lat = float(match.group(2))
    old_lng = float(match.group(3))

    new_lat, new_lng = wgs84_to_gcj02(old_lat, old_lng)

    # 替换经纬度行
    old_line = f'{prefix}{old_lat}°N, {old_lng}°E'
    new_line = f'{prefix}{new_lat}°N, {new_lng}°E'
    content = content.replace(old_line, new_line, 1)

    md_path.write_text(content, encoding='utf-8')

    return (old_lat, old_lng), (new_lat, new_lng)


def update_geo_json():
    """重新生成 attractions-geo.json"""
    import subprocess
    result = subprocess.run(
        ['python', 'scripts/extract_coords.py'],
        cwd=BASE_DIR,
        capture_output=True, text=True
    )
    print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip())


if __name__ == '__main__':
    # 测试转换
    print("WGS-84 → GCJ-02 转换测试")
    print("=" * 50)

    test_points = [
        ("广州塔", 23.1066, 113.3245),
        ("广东省博物馆", 23.1174, 113.3190),
        ("越秀公园", 23.1385, 113.2637),
        ("白云山", 23.1847, 113.2839),
    ]

    for name, lat, lng in test_points:
        new_lat, new_lng = wgs84_to_gcj02(lat, lng)
        dlat = round(new_lat - lat, 4)
        dlng = round(new_lng - lng, 4)
        print(f"\n{name}:")
        print(f"  WGS-84: {lat}°N, {lng}°E")
        print(f"  GCJ-02: {new_lat}°N, {new_lng}°E")
        print(f"  偏移:   Δlat={dlat:+}, Δlng={dlng:+} (~{round(math.sqrt(dlat**2 + dlng**2) * 111000)}m)")