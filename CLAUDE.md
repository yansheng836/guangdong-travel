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

### 图片来源
优先从以下来源获取图片（按优先级）：
1. **Wikimedia Commons**（首选，CC BY-SA 许可证）
2. 景点官方网站
3. 其他开放许可图片源

### 图片格式
```markdown
![景点名称](图片URL)

> 图片来源：[来源名称](来源页面URL) · 许可证：许可证类型
```

### 验证要求
- **必须验证图片 URL 可访问**：使用 `curl -sI <URL>` 检查返回 HTTP 200
- **避免 404 链接**：禁止使用未经验证的图片 URL
- **优先使用缩略图**：Wikimedia Commons 图片优先使用缩略图 URL（如 `/800px-filename.jpg`），减少加载时间

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

```
## 南山区
| 景点名称 | 景点等级 | 景点类型 | 文件 |
|----------|----------|----------|------|
| 欢乐谷 | 5A | 主题公园 | ... |
| 世界之窗 | 4A | 主题公园 | ... |
| 锦绣中华民俗村 | 4A | 主题公园 | ... |
| 海上世界 | - | 综合性滨海休闲区 | ... |
| 华侨城创意文化园 | - | 文化创意园区 | ... |
```

## Sibling Project

The `guangdong-schools` project in the same workspace follows the same structural pattern — reference it for conventions when unsure.
