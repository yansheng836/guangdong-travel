# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a structured Markdown data repository — not a code project. It catalogs tourist attractions in Guangdong Province, China across categories: A级景区, 名胜古迹, 博物馆, 艺术馆, 图书馆, 名山, 著名公园, etc. There is no build system, no tests, and no runtime code.

## Repository Structure

Attraction data files live under `<市级目录>/` directories (e.g. `广州市/`, `深圳市/`). Each city directory has its own `README.md` serving as an index/navigation page for that city.

Covered regions: all 21 prefecture-level cities in Guangdong (广州市, 深圳市, 珠海市, 汕头市, 佛山市, 韶关市, 河源市, 梅州市, 惠州市, 汕尾市, 东莞市, 中山市, 江门市, 阳江市, 湛江市, 茂名市, 肇庆市, 清远市, 潮州市, 揭阳市, 云浮市).

## File Naming Convention

Attraction files: `{市}-{区县}-{景点名}.md` under the city directory — e.g. `广州市/广州市-海珠区-广州塔.md`

## Creating a New Attraction Entry

1. Use `TEMPLATE.md` as the starting point (create it if it doesn't exist)
2. Place the file under the correct `<城市>/` directory, named `{市}-{区}-{景点名}.md`
3. Fill all required fields (景点名称, 所在城市, 所在区县, 景点介绍, 景点特点, 位置, 交通)
4. Add the attraction to the city directory's `README.md` index
5. Update the progress table in the root `README.md`

## README 同步规则

对景点文件进行任何新增、删除、重命名操作后，必须同步更新相关 README 文件：

1. **新增景点**：在对应城市目录的 `README.md` 中添加该景点的表格行，同时递增根目录 `README.md` 中的景点总数
2. **删除景点**：从对应城市目录的 `README.md` 中移除该景点的表格行，同时递减根目录 `README.md` 中的景点总数
3. **重命名景点**：同时更新对应城市目录 `README.md` 中的景点名称（显示文本）和文件链接，根目录 `README.md` 中的数量统计不变

### 景点链接格式

城市 `README.md` 中景点详情的链接**必须包含目录前缀**，格式为 `{城市}/{城市}-{区县}-{景点名}.md`：

```markdown
<!-- ✅ 正确：包含目录前缀 -->
[广州塔](广州市/广州市-海珠区-广州塔.md)

<!-- ❌ 错误：缺少目录前缀（Docsify 作为 SPA，链接从站点根目录解析，不加目录会导致 404） -->
[广州塔](广州市-海珠区-广州塔.md)
```

## 地图坐标数据同步规则

`attractions-geo.json` 是 Leaflet 地图展示附近景点所需的坐标数据文件。

### 坐标系说明

- 所有景点坐标使用 **GCJ-02（火星坐标系）**，以匹配高德地图瓦片
- 由 `scripts/geocode_update.py` 通过高德地理编码 API 获取，无需手动转换
- 如需对比：WGS-84（国际标准）在广东地区偏移 GCJ-02 约 200-700m

### 数据更新场景

1. **修改地址或经纬度**：当景点文件的地址或经纬度信息发生变更时，必须重新生成 `attractions-geo.json`
2. **新增景点**（含经纬度）：新增景点文件后，必须重新生成 `attractions-geo.json`
3. **删除景点**：删除景点文件后，必须重新生成 `attractions-geo.json`

### 从地址重新获取坐标

当新增景点或发现坐标不准确时，使用高德地理编码 API 批量获取：

```bash
# 设置环境变量（高德开放平台 Web 服务 API Key）
# Linux/Mac:
export AMAP_KEY='你的API Key'
# Windows CMD:
set AMAP_KEY=你的API Key
# Windows PowerShell:
$env:AMAP_KEY='你的API Key'

# 全量更新所有城市
python scripts/geocode_update.py

# 只更新指定城市
python scripts/geocode_update.py --city=广州市
python scripts/geocode_update.py --city=深圳市

# 跳过已处理的城市（配合全量使用）
python scripts/geocode_update.py --skip=广州市,深圳市
```

> 注意：免费 API Key 每日调用上限 5000 次，项目 701 个景点可一天内完成全量更新。

### 重新生成坐标数据文件

```bash
python scripts/extract_coords.py
```

## 搜索索引同步规则

`index.html` 中的 Docsify 搜索 `paths` 数组必须包含所有景点文件的路径，否则搜索功能无法索引到新增景点。

1. **新增景点**：新增景点文件后，必须重新生成搜索路径列表
2. **删除景点**：删除景点文件后，必须重新生成搜索路径列表
3. **重命名景点**：重命名景点文件后，必须重新生成搜索路径列表

### 手动重新生成

```bash
python scripts/generate_search_paths.py
```

### 自动生成

每次推送到 `main` 分支时，GitHub Actions 部署流程会自动运行此脚本，无需手动操作。

## Key Conventions

- All content is in Chinese (Simplified)
- Each attraction file must include a 数据来源 section citing where the information came from
- Each attraction file ends with a 最后更新时间 timestamp
- Include images where possible (景点图片)
- License: CC BY-NC-SA 4.0

## 景点文件章节顺序

景点文件的章节必须按以下顺序排列：

```markdown
# 景点名称
## 景点图片        ← 紧跟标题之后
## 基本信息
## 景点介绍
## 景点特点
## 位置
## 交通
## 数据来源
## 最后更新时间
```

## 景点图片规范

### 图片来源（按优先级）

1. **Wikimedia Commons**（首选，CC BY-SA 许可证）
2. 景点官方网站
3. 其他开放许可图片源

### 图片下载与存储

- 图片必须下载到该城市目录下的 `images/` 目录（如 `广州市/images/`）
- **文件名必须与景点 Markdown 文件命名一致**，例如：
  - `广州市-海珠区-广州塔.md` → `images/广州市-海珠区-广州塔.jpg`
  - `广州市-越秀区-白云山.md` → `images/广州市-越秀区-白云山.jpg`
- 压缩后的图片文件名保持相同规则，添加 `_compressed` 后缀：
  - `images/广州市-海珠区-广州塔.jpg` → `images/广州市-海珠区-广州塔_compressed.jpg`
- 引用路径使用相对路径：`images/广州市-海珠区-广州塔_compressed.jpg`

### 图片压缩

所有本地图片必须经过压缩，使用项目根目录的 `scripts/compress.py` 脚本：

```bash
# 压缩指定城市 images/ 目录下的所有图片
python scripts/compress.py 广州市/images

# 压缩后自动更新景点文件引用（使用 _compressed.jpg）
python scripts/compress.py --update 广州市/images

# 预览模式，显示将执行的操作但不实际执行
python scripts/compress.py --dry-run 广州市/images

# 调整压缩质量（1-100，默认 75）
python scripts/compress.py --quality 85 广州市/images

# 调整最大宽度（默认 1920）
python scripts/compress.py --max-w 1600 广州市/images
```

- 压缩后保存为 `原文件名_compressed.jpg`（如 `广州市-海珠区-广州塔_compressed.jpg`）
- **保留原图**：已存在对应压缩文件的原始图片不要删除，原图和压缩版同时保留
- 已存在对应压缩文件的图片自动跳过
- 引用路径使用相对路径（如 `images/广州市-海珠区-广州塔_compressed.jpg`），**必须引用压缩后的 `_compressed.jpg` 文件**
- 依赖 Pillow，无其他第三方库

### 图片格式

```markdown
![景点名称](images/景点名称_compressed.jpg)
```

- **图片来源行（可选）**：仅当图片来自 Wikimedia Commons 等需要版权声明的来源时，才添加 `> 图片来源` 行，格式如下：

  ```markdown
  > 图片来源：[来源名称](来源页面URL) · 许可证：许可证类型
  ```

- 手动提供的照片（如用户指定 URL、百度图片等）**不需要** `> 图片来源` 行

### 原有在线图片迁移

对于已有 Wikimedia Commons 在线图片的景点：

1. 下载原图到 `images/` 目录
2. 运行 `python scripts/compress.py --update <城市>/images` 压缩并更新引用
3. 保留 `> 图片来源：` 行（指向 Wikimedia Commons 页面，仅用于版权说明）

## 城市 README 排序规则

各城市 `README.md` 中的景点表格必须遵循以下排序规则：

### 区县分组顺序

- 按行政区划顺序排列（市辖区在前，县/县级市在后）
- 同级区县按名称拼音排序

### 区县内景点排序

同一区县内的景点按以下优先级排序，同级景点按景点名称拼音排序：

1. **5A级景区**
2. **4A级景区**
3. **全国重点文物保护单位**
4. **省级文物保护单位 / 省级历史文化名村**
5. **其他景点**（按名称拼音排序）

### 示例

```markdown
## 南山区
| 景点名称 | 景点等级 | 景点类型 | 景点详情 |
|----------|----------|----------|------|
| 欢乐谷 | 5A | 主题公园 | ... |
| 世界之窗 | 4A | 主题公园 | ... |
| 锦绣中华民俗村 | 4A | 主题公园 | ... |
| 海上世界 | - | 综合性滨海休闲区 | ... |
| 华侨城创意文化园 | - | 文化创意园区 | ... |
```

## Sibling Project

The `guangdong-schools` project in the same workspace follows the same structural pattern — reference it for conventions when unsure.
