# Python 工具链

全部基于 Playwright + 持久登录（`~/.wechat-automation/browser-profile`）。

## wxmp-list.py

```bash
python3 _skill/scripts/wxmp-list.py            # 有登录态则 headless
python3 _skill/scripts/wxmp-list.py --force-ui # 强制扫码
```
输出 `~/Library/Caches/wxmp/articles.json`（含标题、短链、阅读/分享、`item_show_type`）。
注意：一次推送可含多条图文，脚本已展开；后台列表 total 是「推送数」不是文章数。

## wxmp-fetch.py

```bash
python3 _skill/scripts/wxmp-fetch.py URL [URL...]
python3 _skill/scripts/wxmp-fetch.py --date 2026-11-05 URL
```
- 正文抓公开短链，不需要登录；tempkey 长链过期后无法补抓。
- 自动写封面（贴图除外）、公众号原文链接、去重图片、去掉重复标题 H1。
- 输出 `YYYY/YYYY-MM-DD-标题.md`；贴图类页面无 `create_time` 时用 `--date`。

## update-data.py / build-dashboard.py

```bash
python3 _skill/scripts/update-data.py
```
读取 articles.json + 年份目录，按标题去重（同篇短链/tempkey 只算一次），生成：
`_数据/数据看板.md` 与 `_数据/图表/*.png`（唯一数据出口，不再生成排行榜/日报快照/HTML）。

## wxmp-audit.py

```bash
python3 _skill/scripts/wxmp-audit.py
```
后台总数 vs 存档总数、重复、缺失；关键词匹配会高报，缺失项需人工核对。
