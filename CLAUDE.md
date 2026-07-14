# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a structured Markdown data repository — not a code project. It catalogs tourist attractions in Guangdong Province, China across categories: A级景区, 名胜古迹, 博物馆, 艺术馆, 图书馆, 名山, 著名公园, etc. There is no build system, no tests, and no runtime code.

## Repository Structure

Attraction data files live under `<市级目录>/` directories (e.g. `广州市/`, `深圳市/`). Each city directory has its own `README.md` serving as an index/navigation page for that city.

Covered regions: all 21 prefecture-level cities in Guangdong (广州市, 深圳市, 珠海市, 汕头市, 佛山市, 韶关市, 河源市, 梅州市, 惠州市, 汕尾市, 东莞市, 中山市, 江门市, 阳江市, 湛江市, 茂名市, 肇庆市, 清远市, 潮州市, 揭阳市, 云浮市).

## File Naming Convention

Attraction files: `{市}-{区县}-{景点名}.md` under the city directory，其中 `景点名` **必须使用官方全称**。

```markdown
<!-- ✅ 正确：文件名为官方全称 -->
广州市/广州市-白云区-广州市白云山风景名胜区.md
广州市/广州市-海珠区-广州塔.md

<!-- ❌ 错误：使用简称 -->
广州市/广州市-白云区-白云山.md
```

> 文件重命名后，必须同步更新对应的 README 链接、`attractions-geo.json` 和搜索索引。

## 景点名称规范

基本信息表中的 `景点名称` 字段必须使用**官方全称**，避免歧义：

```markdown
<!-- ✅ 正确：使用官方全称 -->
| 景点名称 | 广州市白云山风景名胜区 |
| 景点名称 | 广州塔 |

<!-- ❌ 错误：使用简称可能导致重名 -->
| 景点名称 | 白云山 |    <!-- 其他城市也可能有"白云山" -->
| 景点名称 | 莲花山 |    <!-- 广州和汕尾都有莲花山 -->
```

**规则说明：**
- `景点名称` 字段 → 使用官方全称（如 "广州市白云山风景名胜区"）
- 文件标题 `# 景点名称` → **也使用官方全称**（如 `# 广州市白云山风景名胜区`）
- **文件名** → 也使用官方全称（如 `广州市-白云区-广州市白云山风景名胜区.md`）
- 文档正文中的描述 → 不拘泥，按语境使用简称或常用名即可（如景点介绍中可写"白云山位于广州市白云区..."）

> 为什么要这样做：高德地理编码 API 查询时优先使用 `景点名称` 作为查询词，全称能有效避免重名景点之间的混淆，确保返回精确的 POI 级坐标。

## Creating a New Attraction Entry

1. Use `TEMPLATE.md` as the starting point (create it if it doesn't exist)
2. Place the file under the correct `<城市>/` directory, named `{市}-{区}-{景点名}.md`（景点名使用官方全称）
3. Fill all required fields (景点名称, 所在城市, 所在区县, 景点介绍, 景点特点, 位置, 交通)
4. Add the attraction to the city directory's `README.md` index
5. Update the progress table in the root `README.md`

## README 同步规则

对景点文件进行任何新增、删除、重命名操作后，必须同步更新相关 README 文件：

1. **新增景点**：在对应城市目录的 `README.md` 中添加该景点的表格行，同时递增根目录 `README.md` 中的景点总数
2. **删除景点**：从对应城市目录的 `README.md` 中移除该景点的表格行，同时递减根目录 `README.md` 中的景点总数
3. **重命名景点**：同时更新对应城市目录 `README.md` 中的景点名称（显示文本）和文件链接，根目录 `README.md` 中的数量统计不变

### 景点链接格式

城市 `README.md` 中景点详情的链接**必须包含目录前缀**，格式为 `{城市}/{城市}-{区县}-{景点名}.md`（景点名使用官方全称）：

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

# 只更新指定景点（精确匹配景点名称）
python scripts/geocode_update.py --name=花城广场
python scripts/geocode_update.py --name=白云山

# 跳过已处理的城市（配合全量使用）
python scripts/geocode_update.py --skip=广州市,深圳市
```

> 注意：免费 API Key 每日调用上限 5000 次，项目 701 个景点可一天内完成全量更新。

### 脚本查询策略

`geocode_update.py` 对每个景点依次尝试三种查询策略，择优选用：

1. **景点名称**（如 `广州市白云山`）→ 大部分景点直接命中兴趣点（POI）级别
2. **地址**（如 `广州市白云区广园中路`）→ 名称级别不理想时尝试
3. **完整名称**（如 `广州市白云山风景名胜区`）→ 名称+地址都不够精确时的兜底策略，由景点名称和景点类型拼接而成

优先选择级别为 `兴趣点` / `风景名胜区` / `景点` / `景区` / `公园` / `广场` / `博物馆` 等具体地点级别的结果。输出会显示命中策略（`src=名称/地址/完整名称`）和级别（`[兴趣点]` 等）。

### 按景点名筛选的兼容模式

如需处理重名景点（如"莲花山"在广州市和汕尾市均有），先用 `--name=景点名` 查看匹配数量，确认后再执行：

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

## 数据来源链接有效性规则

景点文件 `数据来源` 章节中引用的所有外部链接**必须能够正常访问**：

- **写入前必须验证**：添加或修改数据来源链接前，用 `curl` 测试确认返回 HTTP 状态码 **200**（或 301/302 等正常重定向）：

  ```bash
  curl -sS -o /dev/null -w "%{http_code}" --max-time 10 "链接地址"
  ```

- **禁止构造虚假链接**：不能凭记忆或猜测编写网址（如 `http://www.byslp.com/` 这类已失效的域名）。所有链接必须是从浏览器实际访问确认过的真实可访问 URL。

- **链接文本与 URL 必须一致**：链接文本描述的内容必须与超链接指向的实际页面内容相符。禁止出现「挂羊头卖狗肉」的情况，例如：
  - ❌ `[东莞市文化广电旅游体育局](https://baike.baidu.com/item/东莞市)` — 文本写的是文体旅游局，链接却是东莞市百度百科
  - ✅ `[东莞市文化广电旅游体育局](https://www.dg.gov.cn/whgdlytyj/)` — 文本和链接均为文体旅游局官网

- **禁止使用首页/根路径**：链接必须指向**介绍该景点的具体页面**，而不是网站根目录（首页）。例如：
  - ❌ `[全国重点文物保护单位名录](http://www.ncha.gov.cn/)` — 链接是 ncha.gov.cn 首页，非具体页面
  - ✅ `[全国重点文物保护单位名录](https://www.ncha.gov.cn/col/col2267/index.html)` — 链接指向文物保护单位的具体列表页面

- **链接失效处理**：如果发现已有景点的数据来源链接失效（curl 返回非 2xx/3xx，或域名无法解析），**必须替换为有效链接**后再保存文件。可用百度百科、维基百科、景点官方公众号文章等替代来源。

- **无法找到有效链接时**：如果实在找不到可访问的外部来源，**直接删除该条目**，不要留空或保留死链。

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
