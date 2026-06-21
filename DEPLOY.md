# GitHub Pages 部署说明

## 配置步骤

### 1. 推送代码到 GitHub

```bash
git add .
git commit -m "feat: 添加 Docsify 配置"
git push origin main
```

### 2. 启用 GitHub Pages

1. 进入 GitHub 仓库页面
2. 点击 **Settings** → **Pages**
3. 在 **Source** 部分选择：
   - Branch: `main`
   - Folder: `/ (root)`
4. 点击 **Save**

### 3. 访问网站

部署完成后，访问：`https://<你的用户名>.github.io/guangdong-travel/`

## Docsify 功能说明

### 搜索功能

- 点击左侧边栏顶部的搜索框
- 输入景点名称或关键词
- 支持中文搜索

### 侧边栏导航

- 按城市分类显示所有景点
- 点击城市名称展开该城市的景点列表

### 快捷键

- `Ctrl + K` 或 `Cmd + K`：快速打开搜索
- `←` / `→`：上一篇/下一篇

## 自定义配置

编辑 `index.html` 中的 `window.$docsify` 对象可以修改：

- `name`：站点名称
- `search.placeholder`：搜索框提示文字
- `search.noData`：无搜索结果时的提示
- `theme-color`：主题颜色（修改 CSS 变量 `--theme-color`）

## 本地预览

安装 docsify-cli：

```bash
npm i docsify-cli -g
```

启动本地服务器：

```bash
docsify serve .
```

访问 `http://localhost:3000` 预览。
