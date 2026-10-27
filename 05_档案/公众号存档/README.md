# 24帧公众号文章存档

独立放映组织「24帧」公众号文章全库，共 302 篇，时间跨度 2022-04 至 2026-10。

## 网站

GitHub Pages 站点已于 2026-10-28 下线（`gh-pages` 分支清空为占位页）。站点源码仍完整保留在 `.github-pages/`，需要恢复时推送该目录到 `gh-pages` 即可。

## 静态站点（.github-pages/）

| 路径 | 说明 |
|------|------|
| `api/stats.json` | 统计信息（总数、年度分布、字符数） |
| `api/index.json` | 所有文章列表（标题、日期、URL） |
| `api/YYYY.json` | 按年份获取文章列表 |
| `articles/YYYY/YYYY-MM-DD-标题.md` | 文章 Markdown 原文 |
| `articles/YYYY/YYYY-MM-DD-标题.html` | 文章渲染后 HTML |

## 目录结构

```
articles/
├── 2022/    # 48 篇
├── 2023/    # 63 篇
├── 2024/    # 72 篇
├── 2025/    # 66 篇
└── 2026/    # 53 篇
_skill/
├── SKILL.md           # Skill 主文档
├── scripts/
│   └── generate-site.js     # 由年份目录重建 .github-pages
└── docs/python-fetching.md  # 抓取工具链（wxmp-*.py）说明
```

## 更新方式

```bash
# 1. 抓取新文章（扫码登录，工具在 vault 的 00_系统/agent/）
python3 00_系统/agent/wxmp-list.py                 # → /tmp/wxmp-articles.json
python3 00_系统/agent/wxmp-fetch.py URL [URL...]   # → YYYY/YYYY-MM-DD-标题.md
python3 00_系统/agent/wxmp-fetch.py --date 2026-10-26 URL   # 贴图类无页面时间时手动指定

# 2. 审核
python3 00_系统/agent/wxmp-audit.py

# 3. 重建站点
node _skill/scripts/generate-site.js

# 4. 发布存档到 GitHub（远端 main 只保留 05_档案/公众号存档）
git fetch origin main
git checkout -B archive-sync origin/main
git checkout main -- "05_档案/公众号存档"
git commit -m "更新公众号存档"
git push origin archive-sync:main
git checkout main
```

## 仓库

- **主仓库**：https://github.com/yhy2049/wechat-articles
- **主分支**：`main`（文章 + 脚本 + 站点源码）
- **网站分支**：`gh-pages`（2026-10-28 起为下线占位页）
