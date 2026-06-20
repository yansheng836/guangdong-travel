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

## Sibling Project

The `guangdong-schools` project in the same workspace follows the same structural pattern — reference it for conventions when unsure.
