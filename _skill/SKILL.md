# 公众号文章存档 Skill

> 公众号 → 本地存档 → 校对 → GitHub 同步（仓库根目录即存档内容）
> 工具链全部在本目录 `_skill/scripts/`，不依赖 vault 其他目录。

## 换机器 / 换 agent 先跑这个

```bash
bash _skill/setup.sh           # 自检：python3、playwright、requests、Pillow、PyMuPDF、chromium、git
bash _skill/setup.sh install   # 缺什么装什么（pip 依赖 + chromium + npm marked）
```

脚本一律按自身位置定位存档目录，clone 到任何路径都能跑。可用环境变量覆盖：

| 变量 | 作用 | 默认 |
|---|---|---|
| `WXMP_HOME` | 列表 JSON 目录 | macOS `~/Library/Caches/wxmp`，其他系统 `~/.cache/wxmp` |
| `WXMP_PROFILE` | 登录态浏览器目录 | `~/.wechat-automation/browser-profile` |
| `WXMP_ARTICLES` | 列表 JSON 文件 | `$WXMP_HOME/articles.json` |
| `WXMP_GIT_RESOLVE` | 推送绕行 IP 列表 | `140.82.112.3 140.82.113.3 140.82.114.3` |
| `GIT_REMOTE` / `GIT_BRANCH` | 推送目标 | `origin` / `main` |

## 目录结构

```
公众号存档/
├── 2022/ … 2026/          # 文章 Markdown（YYYY-MM-DD-标题.md）
├── .github-pages/         # 静态站点源码（可选，Pages 已下线）
├── _meta/                 # corpus-overview.md / removals.md / source-links.json
├── _skill/
│   ├── SKILL.md           # 本文档
│   ├── scripts/
│   │   ├── wxmp-list.py           # 后台全量列表（持久化登录）
│   │   ├── wxmp-fetch.py          # 抓正文 → 年份目录（含封面 + 原文链接）
│   │   ├── wxmp-audit.py          # 后台 vs 存档完整性审核
│   │   ├── update-data.py         # 刷新 _数据/ 排行榜、快照并重建看板
│   │   ├── build-dashboard.py     # 生成单文件数据看板（纯 SVG，无外部依赖）
│   │   ├── wxmp-verify.py         # 线上 DOM vs 归档 MD 校验
│   │   ├── wxmp-probe.py          # 页面结构诊断
│   │   ├── generate-site.js       # 由年份目录重建 .github-pages
│   │   └── push-archive.sh        # 镜像提交推送到 GitHub main
│   └── docs/python-fetching.md
└── README.md
```

## 标准更新流程

```bash
cd 05_档案/公众号存档

# 1. 拉后台全量列表（登录态有效则 headless 直接跑，失效才弹窗扫码）
python3 _skill/scripts/wxmp-list.py
#    → ~/Library/Caches/wxmp/articles.json

# 2. 与年份目录比对，找出未入档文章（标题去标点后归一化匹配）
#    注意：一次推送可含多条图文，必须遍历 appmsg_info 全部条目

# 3. 抓正文（自动写封面图 + 公众号原文链接）
python3 _skill/scripts/wxmp-fetch.py URL [URL...]
python3 _skill/scripts/wxmp-fetch.py --date 2026-11-05 URL   # 贴图类页面取不到日期时

# 4. 补原文链接映射（新文章写进 md 后重建映射表）
#    产物：_meta/source-links.json

# 4.5 刷新 _数据/（排行榜 + 当日快照 + 数据看板，按标题去重取最大阅读量）
python3 _skill/scripts/update-data.py   # 内部会调用 build-dashboard.py

# 5. 校对
python3 _skill/scripts/wxmp-audit.py

# 6. 更新 README 与 _meta/corpus-overview.md 的篇数、年度分布、字符数

# 7.（可选）重建静态站点
node _skill/scripts/generate-site.js

# 8. 提交并推送 GitHub
git add 05_档案/公众号存档 && git commit -m "更新公众号存档"
bash _skill/scripts/push-archive.sh "更新公众号存档"
```

## 抓取要点（实测，别再改回去）

1. **列表接口**：`appmsgpublish?sub=list&begin=N&count=20&type=101_1_102_103`，
   返回的 `publish_page` 是 JSON 字符串，里面的 `publish_info` 还是字符串，要二次 `json.loads`。
2. **多图文**：`appmsg_info` 是数组。只取第 0 条会漏文章——2026-11 实测：取第一条 329 篇，遍历全部 344 篇。
3. **翻页**：偶发空页要重试（连续 3 次空才停），直接 break 会少一整页。
4. **短链**：`/s/XXXXX` 抓正文不需要 chksm，也不需要登录；`tempkey` 长链会过期，过期后无法补抓。
5. **贴图类文章**（`item_show_type=8`）页面没有 `create_time`，日期要从页面可见文本（如「11月5日」）取，或用 `--date` 指定。
6. **标题重复**：正文首行可能自带与标题同名的 H1，`wxmp-fetch.py` 会去掉，避免存档里两行标题。
7. **封面图**：取 `og:image` / `var msg_cdn_url`，写成首行 `![cover_image](...)`。
8. **图片去重**：同一张图有多个 URL 变体，按 `?` 前的 mmbiz 图片 ID 去重；排除 `pic_blank.gif`、`video_player_tmpl`、二维码。
9. **登录态**：`~/.wechat-automation/browser-profile`，扫码一次后 headless 复用；`--force-ui` 强制弹窗。

## 存档格式

```markdown
![cover_image](https://mmbiz.qpic.cn/...)

#  「专场」11.11《海上钢琴师》超前点映

> 公众号原文：<https://mp.weixin.qq.com/s/xxxx>

正文…
```

## 移除规则（见 `_meta/removals.md`）

- 授权转载、转自等转载文
- 24帧未参与的活动（HiShorts、Nowhere 短片展等）
- 同一文章多位置重复时保留年份目录版本

## GitHub

- 仓库：https://github.com/yhy2049/wechat-articles （公开）
- `main` 根目录 = 本目录内容；仓库内只有公众号存档（2026-11-06 起已删除 `05_档案` 下的会议存档等）
- `push-archive.sh` 用镜像提交推送：取本地存档树作为仓库根树，parent 为 `origin/main`；若远端仍有 `05_档案/` 会自动合并保留。先 `bash _skill/scripts/push-archive.sh --dry-run` 可只看算出来的树，不推送。不要用 `git push origin main`（会把 vault 其他目录带上去）
- `gh-pages` 自 2026-10-28 起为下线占位页；恢复站点时把 `.github-pages/` 内容推到 `gh-pages`
- 本机直连 `github.com:443` 常超时，可用：
  `git -c http.curloptResolve=github.com:443:140.82.112.3 -c http.version=HTTP/1.1 …`

## 常见问题

- **数量不一致**：先确认是否漏了多图文的第二条，再看 tempkey 过期项（无法补抓）。
- **抓取失败/降级页**：脚本会自动退避重试 3 次；仍失败多为 tempkey 长链失效。
- **站点数字不对**：`node _skill/scripts/generate-site.js` 重建后核对 `api/stats.json`。
- **给 AI 当语料**：`_skill/scripts/` 之外的 PDF 图文合集生成脚本在会话工作目录，纯文本可由年份目录 md 直接汇总。
