# 公众号文章存档 Skill

> 完整流程：公众号 → 本地存档 → 校对验证 → GitHub 同步 → 网站生成

## 目录结构

```
wechat-articles/
├── articles/          # 文章存档（按年份）
│   ├── 2022/
│   ├── 2023/
│   ├── 2024/
│   ├── 2025/
│   └── 2026/
├── _skill/            # 自动化脚本
│   ├── SKILL.md       # 主文档
│   ├── README.md      # 使用说明
│   ├── package.json   # npm 脚本
│   ├── scripts/
│   │   ├── fetch-articles.js         # 抓取文章
│   │   ├── verify-articles.js        # 校对验证
│   │   ├── update-meta.js            # 生成统计报告
│   │   ├── sync-to-github.sh         # 同步到 GitHub
│   │   ├── generate-site.js          # 生成网站页面
│   │   └── generate-article-html.js  # 生成文章 HTML
│   └── docs/
│       ├── workflow.md               # 详细文档
│       └── python-fetching.md        # Python 工具链（wxmp-list/fetch/verify/probe）
└── README.md
```

> **Python 工具链**：`00_系统/agent/wxmp-*.py`，基于 Playwright，见 `docs/python-fetching.md`。
> 核心优势：短链无需 chksm，抓取更稳定，支持命令行批量调用。

## 快速开始

### 前置要求

1. **Node.js** >= 18
2. **Playwright**（用于抓取）
3. **GitHub CLI**（用于同步）
4. **微信登录**（首次需要扫码）

```bash
# 安装依赖
npm install -g playwright
npx playwright install chromium

# 安装 GitHub CLI
brew install gh
gh auth login
```

### 完整流程

```bash
# 1. 抓取最新文章
node scripts/fetch-articles.js

# 2. 校对验证
node scripts/verify-articles.js

# 3. 同步到 GitHub
./scripts/sync-to-github.sh

# 4. 生成网站（首页、年份、API）
node scripts/generate-site.js

# 5. 生成文章 HTML（渲染 Markdown）
node scripts/generate-article-html.js

# 6. 推送到 GitHub Pages
cd .github-pages
git add -A
git commit -m "更新网站"
git push origin gh-pages
```

## 核心流程

### 1. 抓取文章（公众号 → 本地）

**脚本：** `scripts/fetch-articles.js`

**功能：**
- 自动打开微信公众号后台
- 遍历历史消息列表
- 下载文章正文（Markdown 格式）
- 下载封面图（screenshots 目录）
- 保存元数据（标题、作者、日期、阅读量）

**输出：**
```
~/Documents/async-communication/wechat-data/
├── articles/          # Markdown 文章
├── screenshots/       # 封面图截图
├── meta.json          # 元数据索引
└── auto.log           # 运行日志
```

**使用方法：**
```bash
# 首次运行（需要扫码登录）
node scripts/fetch-articles.js --login

# 后续运行（自动登录）
node scripts/fetch-articles.js
```

### 2. 校对验证（本地检查）

**脚本：** `scripts/verify-articles.js`

**检查项：**

| 检查项 | 说明 | 通过标准 |
|--------|------|----------|
| 封面图重复 | 检查 screenshots 目录是否有重复图片 | 0 重复 |
| 文章数量 | 与公众号后台数量对比 | 差异 < 5% |
| 文件完整性 | 检查所有 .md 文件是否有内容 | 100% 有内容 |
| 文件名规范 | 检查文件名是否符合 `YYYY-MM-DD-标题.md` | 100% 规范 |
| 元数据完整性 | 检查 meta.json 是否完整 | 100% 匹配 |

**输出：**
```json
{
  "summary": {
    "total_articles": 298,
    "total_screenshots": 298,
    "duplicate_screenshots": 0,
    "missing_metadata": 0
  },
  "checks": {
    "cover_duplicates": "✅ PASS",
    "article_count": "✅ PASS (298/298)",
    "file_integrity": "✅ PASS",
    "filename_format": "✅ PASS",
    "metadata_completeness": "✅ PASS"
  }
}
```

**使用方法：**
```bash
# 完整校对
node scripts/verify-articles.js

# 只检查封面图重复
node scripts/verify-articles.js --check covers

# 输出 JSON 报告
node scripts/verify-articles.js --json
```

### 3. 同步到 GitHub（本地 → GitHub）

**脚本：** `scripts/sync-to-github.sh`

**功能：**
- 检测已上传文件（跳过重复）
- 显示实时进度
- 失败重试机制
- 生成同步报告

**使用方法：**
```bash
# 完整同步
./scripts/sync-to-github.sh

# 只同步新文件
./scripts/sync-to-github.sh --new-only

# 指定仓库
./scripts/sync-to-github.sh --repo yhy2049/wechat-articles
```

### 4. 生成网站（GitHub Pages）

**脚本：** `scripts/generate-site.js` + `scripts/generate-article-html.js`

**功能：**
- 生成首页（index.html）
- 生成年份页面（2022.html ~ 2026.html）
- 生成 API 文档（api.html）
- 为每篇文章生成渲染后的 HTML（类 Obsidian 风格）
- 生成 JSON API（index.json, stats.json, 按年份）
- 自动处理微信图片热链保护（referrerpolicy="no-referrer"）

**使用方法：**
```bash
# 生成网站页面（首页、年份、API）
node scripts/generate-site.js

# 生成文章 HTML（渲染 Markdown）
node scripts/generate-article-html.js

# 或直接运行两个脚本
node scripts/generate-site.js && node scripts/generate-article-html.js

# 然后推送到 gh-pages 分支
cd .github-pages
git add -A
git commit -m "更新网站"
git push origin gh-pages
```

**网站地址：** https://yhy2049.github.io/wechat-articles/

**JSON API：**
| 接口 | 说明 |
|------|------|
| `/api/stats.json` | 统计信息 |
| `/api/index.json` | 所有文章列表 |
| `/api/2026.json` | 按年份获取 |

**图片热链保护：**
微信图片有 Referer 检查，外部网站访问会显示"未经允许"。
解决：`<img>` 标签添加 `referrerpolicy="no-referrer"`，不发送 Referer。

## 数据格式

### 文章文件（Markdown）

```markdown
# 文章标题

**作者**: 作者名  
**日期**: 2024-01-15  
**阅读量**: 1234  
**分享数**: 56

---

![封面图](https://mmbiz.qpic.cn/...)

正文内容...
```

### 元数据索引（meta.json）

```json
{
  "last_updated": "2024-01-15T10:00:00Z",
  "total_articles": 298,
  "articles": [
    {
      "id": "2024-01-15-标题",
      "title": "文章标题",
      "author": "作者名",
      "date": "2024-01-15",
      "file": "2024-01-15-标题.md",
      "cover": "screenshots/2024-01-15-标题.jpg",
      "views": 1234,
      "shares": 56
    }
  ]
}
```

## 常见问题

### Q: 抓取失败怎么办？
A: 检查网络、重新扫码登录、查看 `auto.log` 日志

### Q: 如何检查数量是否一致？
A: 运行 `node scripts/verify-articles.js`，对比本地和后台数量

### Q: 同步失败如何重试？
A: 重新运行同步脚本，已上传的文件会自动跳过

### Q: 如何添加新的公众号？
A: 修改 `fetch-articles.js` 中的 `ACCOUNT_NAME` 配置

### Q: 图片显示"未经允许不可引用"怎么办？
A: 这是微信热链保护。生成文章 HTML 时已自动添加 `referrerpolicy="no-referrer"`，重新生成即可。

### Q: 如何更新网站？
A: 运行 `node scripts/generate-site.js && node scripts/generate-article-html.js`，然后推送到 `gh-pages` 分支。

### Q: 其他 AI/Agent 如何访问数据？
A: 访问 JSON API：`https://yhy2049.github.io/wechat-articles/api/index.json` 或读取 `.md` 文件。

## 维护说明

- 每月运行一次完整校对
- 每季度清理重复截图
- 同步后检查 GitHub 仓库文件数

## 许可证

MIT License
