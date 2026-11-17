# 24帧公众号文章存档

独立放映组织「24帧」公众号文章全库，共 331 篇，时间跨度 2022-04 至 2026-11。

本地保存在 vault 的 `档案/公众号存档/`；GitHub 仓库根目录直接对应本目录内容，仓库内只有公众号存档。

数据看板：Obsidian 里直接打开 `_数据/数据看板.md`（图表为 `_数据/图表/*.png`，GitHub 上同样可见），交互版是 `_数据/数据看板.html`。

非贴图文章保留公众号封面图（306 篇）；贴图类首图即封面，不重复存（25 篇，含原页面无封面的《取消放映通知》），正文顶部保留「公众号原文」链接（331/331），映射表见 `_meta/source-links.json`。

正文图片统一使用微信外链（`mmbiz.qpic.cn`，`referrerpolicy="no-referrer"` 防盗链），**不做本地镜像**（2026-11-06 决定）。

## 目录结构

仓库根目录 = 本目录（GitHub 上无 `档案/公众号存档` 层级）：

```
2022/ … 2026/            # 文章 Markdown，按年份
_meta/                   # 语料统计、移除记录、原文链接映射
_skill/                  # SKILL.md、抓取/数据/推送脚本
_数据/                   # 阅读量等运营数据
README.md
```

## 更新方式

换机器或换 agent 先跑 `bash _skill/setup.sh` 自检依赖（缺则 `bash _skill/setup.sh install`）。

```bash
cd 档案/公众号存档

# 1. 拉后台全量列表（登录态失效才弹窗扫码）
python3 _skill/scripts/wxmp-list.py

# 2. 抓新文章（自动写封面图 + 公众号原文链接）
python3 _skill/scripts/wxmp-fetch.py URL [URL...]
python3 _skill/scripts/wxmp-fetch.py --date 2026-11-05 URL   # 贴图类页面取不到日期时

# 3. 刷新 _数据/（排行榜 + 当日快照 + 数据看板）
python3 _skill/scripts/update-data.py

# 4. 发布存档到 GitHub（仓库根目录 = 本目录内容，只上传存档本身）
bash _skill/scripts/push-archive.sh "更新公众号存档"
```

> 站点已下线并从仓库移除；文章以 Markdown 为准。

## 仓库

- **主仓库**：https://github.com/yhy2049/wechat-articles
- **主分支**：`main`（仓库根目录即存档内容：文章 + 脚本 + 站点源码）
- **网站分支**：`gh-pages`（2026-10-28 起为下线占位页）
