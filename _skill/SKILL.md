# 公众号文章存档 Skill

维护 `档案/公众号存档`：拉后台 → 抓文章 → 刷新数据 → 推 GitHub 根部（仓库只放存档）。

## 更新流程

```bash
cd 档案/公众号存档
python3 _skill/scripts/wxmp-list.py          # 后台全量列表（持久登录，失效才扫码）
python3 _skill/scripts/wxmp-fetch.py URL...   # 抓新文章（自动修复排版、过滤转载）
python3 _skill/scripts/update-data.py         # 数据看板（md + png，唯一出口）
bash    _skill/scripts/push-archive.sh "说明"  # 镜像存档树到远端根目录
```

换机器先 `bash _skill/setup.sh install` 自检依赖。

## 核心功能（2026-11 新增）

- **自动排版修复**：微信 HTML 里 `<span>` 标签导致每字/词被拆成独立段落，`wxmp-fetch.py` 现在会自动合并成完整段落
- **转载过滤**：自动检测并跳过转载内容（影展征片、电影资讯等），只保留 24帧 原创内容
- **批量修复历史文章**：如有历史文章需要修复排版，运行 `_skill/scripts/fix-all-formatting.py`

## 不可违背的规则

- **原创优先**：只存档 24帧 原创内容（放映、路演、组讯、回顾等），跳过转载（影展征片、电影资讯）
- **排版修复**：所有文章入库前必须经过 `fix_formatting()` 处理，合并被 `<span>` 拆散的行
- **多图文**：`appmsg_info` 是数组，必须遍历；只取第一条会漏档。翻页遇空页要重试。
- **贴图（`item_show_type=8`）**：首图即封面，不写 `cover_image`；普通文章写封面。
- **图片**：同一文章按 mmbiz 图片 ID 去重（微信 DOM 会重复节点）；只存微信外链，不本地镜像。
- **标题**：正文自带的 `24FRAMES PROJECT` 是微信模板装饰，一律删除；贴图补真实标题 H1，首图放在标题/原文链接之后。
- **数据口径**：分享数 2024 年前异常偏低，不跨年对比；tempkey 长链过期无法补抓，记入 `_meta/removals.md`。
- **推送**：仓库根目录 = 存档内容，只推存档树；直连失败用 `-c http.curloptResolve=github.com:443:140.82.112.3 -c http.version=HTTP/1.1`。

## 转载检测关键词

以下关键词会触发转载过滤（在 `wxmp-fetch.py` 的 `REPOST_KEYWORDS` 中配置）：

- 通用：`转载`、`转发`、`转自`、`来源：`、`via`
- 已知影展：`HiShorts`、`NOWHERE`、`阿凡达`
- 征片类：`征片`、`报名`、`投稿`

## 文件

| 文件 | 作用 |
|---|---|
| `scripts/wxmp-list.py` | 后台全量列表 → `~/Library/Caches/wxmp/articles.json` |
| `scripts/wxmp-fetch.py` | 正文 → 年份目录（封面、原文链接、去重、排版修复、转载过滤） |
| `scripts/update-data.py` | 校验列表并调用看板生成 |
| `scripts/build-dashboard.py` | 单文件看板（SVG + PNG + Markdown） |
| `scripts/push-archive.sh` | 镜像推送到 GitHub |
| `scripts/wxmp-audit.py` | 后台 vs 存档对账 |
| `scripts/fix-all-formatting.py` | 批量修复历史文章排版（如需要） |

详细参数见 `docs/python-fetching.md`。
