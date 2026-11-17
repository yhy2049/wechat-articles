# 公众号文章存档 Skill

维护 `档案/公众号存档`：拉后台 → 抓文章 → 刷新数据 → 推 GitHub 根部（仓库只放存档）。

## 更新流程

```bash
cd 档案/公众号存档
python3 _skill/scripts/wxmp-list.py          # 后台全量列表（持久登录，失效才扫码）
python3 _skill/scripts/wxmp-fetch.py URL...   # 抓新文章（贴图取不到日期时加 --date）
python3 _skill/scripts/update-data.py         # 排行榜 + 快照 + 数据看板（md/png/html）
bash    _skill/scripts/push-archive.sh "说明"  # 镜像存档树到远端根目录
```

换机器先 `bash _skill/setup.sh install` 自检依赖。

## 不可违背的规则

- **多图文**：`appmsg_info` 是数组，必须遍历；只取第一条会漏档。翻页遇空页要重试。
- **贴图（`item_show_type=8`）**：首图即封面，不写 `cover_image`；普通文章写封面。
- **图片**：同一文章按 mmbiz 图片 ID 去重（微信 DOM 会重复节点）；只存微信外链，不本地镜像。
- **标题**：正文自带同名 H1 或 `24FRAMES PROJECT` 品牌行要去掉；贴图首图放在标题/原文链接之后。
- **数据口径**：分享数 2024 年前异常偏低，不跨年对比；tempkey 长链过期无法补抓，记入 `_meta/removals.md`。
- **推送**：仓库根目录 = 存档内容，只推存档树；直连失败用 `-c http.curloptResolve=github.com:443:140.82.112.3 -c http.version=HTTP/1.1`。

## 文件

| 文件 | 作用 |
|---|---|
| `scripts/wxmp-list.py` | 后台全量列表 → `~/Library/Caches/wxmp/articles.json` |
| `scripts/wxmp-fetch.py` | 正文 → 年份目录（封面、原文链接、去重） |
| `scripts/update-data.py` | 排行榜、日快照、调用看板生成 |
| `scripts/build-dashboard.py` | 单文件看板（SVG + PNG + Markdown） |
| `scripts/push-archive.sh` | 镜像推送到 GitHub |
| `scripts/wxmp-audit.py` | 后台 vs 存档对账 |

详细参数见 `docs/python-fetching.md`。
