# Repository Guidelines

## Project Structure & Module Organization

This repository is a Docsify/GitHub Pages site for Guangdong attraction data. The root `README.md` is the public index, `index.html` contains Docsify configuration, `_sidebar.md` and `_coverpage.md` control navigation, and `DEPLOY.md` documents publishing. Attraction pages live in city directories such as `广州市/` and `深圳市/`; each city has a `README.md` index plus files named `{市}-{区县}-{景点官方全称}.md`. Shared data and tooling live in `attractions-geo.json`, `css/`, `scripts/`, and `.github/workflows/deploy.yml`.

## Build, Test, and Development Commands

- `docsify serve .`: preview the site locally at `http://localhost:3000`.
- `python scripts/generate_search_paths.py`: rebuild Docsify search paths in `index.html` after adding, deleting, or renaming attraction files.
- `python scripts/extract_coords.py`: regenerate `attractions-geo.json` from Markdown coordinates.
- `python scripts/geocode_update.py --city=广州市`: update coordinates through the Amap API; set `AMAP_KEY` first.
- `markdownlint AGENTS.md --config .markdownlint.json`: validate Markdown formatting.

## Coding Style & Naming Conventions

Use UTF-8 Markdown and keep headings hierarchical. Attraction titles, `景点名称`, and filenames must use the official full attraction name. City README links must include the city directory prefix, for example `[广州塔](广州市/广州市-海珠区-广州塔.md)`. When renaming or moving attraction files, update the city README, root README counts, search paths, and coordinate JSON together.

## Testing Guidelines

There is no dedicated test suite. Validate content changes by running `markdownlint` on edited Markdown files and previewing with `docsify serve .`. For data changes, rerun the relevant Python scripts and check that generated files only contain expected updates.

## Commit & Pull Request Guidelines

Recent history uses `type: 中文描述`, for example `fix: 修复景点文件数据来源链接` and `feat: 优化 geocode_update.py 查询策略`. Keep commits focused and use `feat`, `fix`, `chore`, or similar prefixes. Pull requests should describe changed cities or scripts, list regenerated files, link related issues, and include screenshots when navigation, styling, or Docsify behavior changes.

## Security & Configuration Tips

Do not commit API keys. Keep `AMAP_KEY` in your shell environment only. Check generated diffs before committing because scripts can touch many Markdown files, `index.html`, or `attractions-geo.json`.
