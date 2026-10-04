# 24帧公众号文章存档

独立放映组织「24帧」公众号文章全库，共 294 篇，时间跨度 2022-04 至 2026-09。

## 网站

- **首页**：https://yhy2049.github.io/wechat-articles/
- **按年份浏览**：https://yhy2049.github.io/wechat-articles/2026.html
- **API 文档**：https://yhy2049.github.io/wechat-articles/api.html

## JSON API

| 接口 | 说明 |
|------|------|
| `/api/stats.json` | 统计信息（总数、年度分布、字符数） |
| `/api/index.json` | 所有文章列表（标题、日期、URL） |
| `/api/2026.json` | 按年份获取文章列表 |
| `/articles/YYYY/YYYY-MM-DD-标题.md` | 文章 Markdown 原文 |
| `/articles/YYYY/YYYY-MM-DD-标题.html` | 文章渲染后 HTML |

## 目录结构

```
articles/
├── 2022/    # 49 篇
├── 2023/    # 62 篇
├── 2024/    # 70 篇
├── 2025/    # 66 篇
└── 2026/    # 47 篇
_skill/
├── SKILL.md           # Skill 主文档
├── scripts/
│   ├── fetch-articles.js    # 从公众号后台抓取文章
│   ├── verify-articles.js   # 校对验证
│   ├── update-meta.js       # 生成统计报告
│   ├── sync-to-github.sh    # 同步到 GitHub
│   ├── generate-site.js     # 生成网站页面
│   └── generate-article-html.js  # 生成文章 HTML
└── docs/workflow.md   # 详细工作流文档
```

## 更新方式

```bash
cd _skill

# 1. 抓取新文章（需要 Playwright + 登录）
npm run fetch

# 2. 校对验证
npm run verify

# 3. 同步到 GitHub 仓库
npm run sync

# 4. 生成网站页面
node scripts/generate-site.js && node scripts/generate-article-html.js
```

## 仓库

- **主仓库**：https://github.com/yhy2049/wechat-articles
- **网站分支**：`gh-pages`
- **主分支**：`main`（文章 + 脚本）
