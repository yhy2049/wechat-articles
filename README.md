# 24帧公众号文章存档

独立放映组织「24帧」公众号文章全库，共 325 篇，时间跨度 2022-04 至 2026-11。

本地保存在 vault 的 `05_档案/公众号存档/`；GitHub 仓库根目录直接对应本目录内容，仓库内只有公众号存档（2026-11-06 起 `05_档案` 下的会议存档等已从仓库移除）。

每篇开头保留公众号封面图（324/325；《取消放映通知》原页面无封面），正文顶部保留「公众号原文」链接（325/325，含此前缺失的《无名》《关于莉莉周的一切》），映射表见 `_meta/source-links.json`。

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

仓库根目录 = 本目录（GitHub 上无 `05_档案/公众号存档` 层级）：

```
2022/ … 2026/            # 文章 Markdown，按年份
.github-pages/           # 静态站点源码（文章 md/html、年份页、API）
_meta/                   # 语料统计、移除记录、原文链接映射
_skill/                  # SKILL.md、generate-site.js、抓取说明
_数据/                   # 阅读量等运营数据
README.md
```

## 更新方式

```bash
cd 05_档案/公众号存档

# 1. 拉后台全量列表（登录态失效才弹窗扫码）
python3 _skill/scripts/wxmp-list.py

# 2. 抓新文章（自动写封面图 + 公众号原文链接）
python3 _skill/scripts/wxmp-fetch.py URL [URL...]
python3 _skill/scripts/wxmp-fetch.py --date 2026-11-05 URL   # 贴图类页面取不到日期时

# 3. 发布存档到 GitHub（仓库根目录 = 本目录内容）
bash _skill/scripts/push-archive.sh "更新公众号存档"
```

> 静态站点已随 gh-pages 下线，日常更新不必重建；需要时用 `node _skill/scripts/generate-site.js` 重建 `.github-pages/`。

## 仓库

- **主仓库**：https://github.com/yhy2049/wechat-articles
- **主分支**：`main`（仓库根目录即存档内容：文章 + 脚本 + 站点源码）
- **网站分支**：`gh-pages`（2026-10-28 起为下线占位页）
