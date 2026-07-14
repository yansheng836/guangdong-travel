# Repository Guidelines

## Project Overview

This repository is a structured Markdown data collection and Docsify/GitHub
Pages site for attractions in all 21 prefecture-level cities of Guangdong. It
does not have a traditional application build or unit-test suite, but it does
include Python data-processing tools, Docsify configuration, and a deployment
workflow.

Treat this file as the single source of truth for repository-wide contributor
and agent instructions. Tool-specific instruction files should reference this
file instead of duplicating these rules.

## Project Structure

The root `README.md` is the public index, `index.html` contains Docsify
configuration, `_sidebar.md` and `_coverpage.md` control navigation, and
`DEPLOY.md` documents publishing. Attraction pages live in city directories
such as `广州市/` and `深圳市/`; each city has a `README.md` index and an
`images/` directory when it contains local images. Shared data and tooling live
in `attractions-geo.json`, `css/`, `scripts/`, and `.github/workflows/`.

## Attraction File Requirements

- Start new attraction pages from the existing `TEMPLATE.md`. If the template
  is missing, report the problem instead of recreating it from memory.
- Name attraction files `{市}-{区县}-{景点官方全称}.md` and place them under
  the corresponding city directory.
- Use the official full attraction name in the filename, H1 title, and
  `景点名称` field. Descriptive prose may use an unambiguous common name or
  abbreviation.
- Write content in Simplified Chinese and use UTF-8 encoding.
- Fill the required template content, including `景点名称`, `所在城市`,
  `所在区县`, `景点介绍`, `景点特点`, `位置`, and `交通`.
- Keep sections in the order defined by `TEMPLATE.md`: `景点图片`, `基本信息`,
  `景点介绍`, `景点特点`, `位置`, `交通`, `数据来源`, and `最后更新时间`.
- End each attraction page with a `最后更新时间` value in `YYYY-MM-DD` format.
- Project content is licensed under CC BY-NC-SA 4.0.

## Index and Generated-Data Synchronization

After adding, deleting, renaming, or moving an attraction page, keep all
dependent files synchronized:

| Change | City `README.md` | Root `README.md` | Search paths | Coordinates |
| :--- | :--- | :--- | :--- | :--- |
| Add | Add and correctly sort its row | Increase the total | Regenerate | Regenerate when coordinates are present |
| Delete | Remove its row | Decrease the total | Regenerate | Regenerate |
| Rename or move | Update link text and target | Total is unchanged | Regenerate | Regenerate |
| Address or coordinate edit | No change unless displayed data changed | No change | No change | Regenerate |

City README attraction links must include the city-directory prefix because
Docsify resolves them from the site root, for example
`[广州塔](广州市/广州市-海珠区-广州塔.md)`.

Run `python scripts/generate_search_paths.py` to rebuild Docsify search paths
in `index.html`. Run `python scripts/extract_coords.py` to rebuild
`attractions-geo.json`. Review generated diffs and ensure they contain only the
expected changes.

All stored map coordinates use GCJ-02 to match Amap tiles. When coordinates are
missing or inaccurate, set `AMAP_KEY` only in the shell environment and use
`python scripts/geocode_update.py --city=<城市>` or its other documented CLI
options. Never commit API keys. Check `python scripts/geocode_update.py --help`
instead of copying potentially stale option descriptions into documentation.

## Data Source Rules

- Every attraction page must include a `数据来源` section with sources that
  support the page content.
- Never invent or guess a URL. Link text must accurately describe the final
  destination, and the link should point to a relevant detail page rather than
  an unrelated home page or search/disambiguation page.
- Before adding or changing a source, verify that its final destination is
  reachable and contains the claimed information. Normal redirects are
  acceptable; HTTP errors, login or verification barriers, DNS failures, and
  redirects to unrelated content are not.
- A command such as
  `curl -L -sS -o /dev/null -w "%{http_code}" --max-time 10 <URL>` can check
  the final HTTP status, but inspect rendered content when status alone cannot
  establish relevance.
- Replace confirmed dead or misleading links with reliable sources. If no
  reliable replacement can be found, report the unresolved entry; do not
  fabricate a source or delete an existing attraction without explicit user
  approval.

## Image and Licensing Rules

- Prefer Wikimedia Commons, an attraction's official site, or another source
  with a compatible open license. Confirm usage rights for every non-original
  image, including images supplied by a user.
- Download local images into the relevant city `images/` directory. Match the
  attraction Markdown basename and add `_compressed` to the compressed file,
  for example `广州市-海珠区-广州塔_compressed.jpg`.
- Use `python scripts/compress.py <城市>/images` to compress images. Use
  `--dry-run` before broad changes and `--update` to update Markdown image
  references. The script defaults to JPEG quality 75 and a maximum width of
  1920 pixels; use `--help` for current options.
- Reference the compressed image with a relative path, retain the original
  image, and do not delete existing source assets solely because a compressed
  copy exists.
- Where a license requires attribution, record the source page, author when
  available, and license. User-provided images are not automatically exempt
  from copyright or attribution requirements.

## City README Ordering

- Group districts according to administrative-division order, with municipal
  districts before counties and county-level cities. Sort peers by Chinese
  pinyin when no established project order applies.
- Within a district, order attractions by: 5A scenic areas, 4A scenic areas,
  national key cultural relic protection units, provincial cultural relic
  protection units or provincial historic villages, and then other
  attractions.
- Sort attractions at the same priority by the pinyin of their official full
  names.

## Development and Validation Commands

- `docsify serve .`: preview the site at `http://localhost:3000`.
- `python scripts/generate_search_paths.py`: rebuild Docsify search paths.
- `python scripts/extract_coords.py`: regenerate `attractions-geo.json`.
- `python scripts/geocode_update.py --city=广州市`: update coordinates through
  the Amap API after setting `AMAP_KEY`.
- `python scripts/compress.py --dry-run <城市>/images`: preview image
  compression changes.
- `markdownlint <edited-files> --config .markdownlint.json`: validate edited
  Markdown files.

There is no dedicated test suite. For content changes, lint edited Markdown
and preview affected navigation with Docsify when practical. For scripts or
generated data, run the relevant command and inspect the resulting diff.

## Commit and Pull Request Guidelines

Keep commits focused and use `type: 中文描述`, for example
`fix: 修复景点文件数据来源链接` or
`feat: 优化 geocode_update.py 查询策略`. Common types include `feat`, `fix`,
`docs`, `refactor`, `test`, `ci`, and `chore`.

Pull requests should identify the changed cities or scripts, list regenerated
files, link related issues, and include screenshots when navigation, styling,
or Docsify behavior changes.

## Security and Change-Safety Rules

- Keep `AMAP_KEY` and all other secrets in the local environment only.
- Inspect generated changes before saving or committing because scripts can
  touch many Markdown files, `index.html`, and `attractions-geo.json`.
- Do not delete attractions, original images, or source data merely to make a
  validation check pass. Report ambiguous content and request confirmation for
  destructive cleanup.
