# Python 抓取工具链（2026-10-05 新增）

> 与 Node.js 脚本（`scripts/`）并行的 Python 方案，基于 Playwright。
> 核心优势：短链无需 chksm，抓取更稳定；支持批量命令行调用。

## 脚本清单

所有脚本在 `00_系统/agent/`（vault 根目录）：

| 脚本 | 用途 | 依赖 |
|------|------|------|
| `wxmp-list.py` | 扫码登录 → 后台拉文章列表 → JSON | Playwright, 微信登录 |
| `wxmp-fetch.py` | 批量抓取文章 → Markdown → 年份目录 | Playwright, iPhone UA |
| `wxmp-verify.py` | 存档完整性校验：比对线上 DOM vs 归档 MD | Playwright |
| `wxmp-probe.py` | 诊断工具：探查文章页面结构 | Playwright |

### wxmp-list.py

```bash
python3 00_系统/agent/wxmp-list.py
```

1. 弹出 Chromium 窗口 → 扫码登录公众号后台
2. 自动翻页遍历 `appmsgpublish`（`type=101_1_102_103`，每页 20 条）
3. 解析两层嵌套 JSON，提取 `content_url`（短链）+ 标题 + 日期
4. 输出到 `/tmp/wxmp-articles.json`

**注意**：`content_url` 是短链格式 `/s/XXXXX`，不需要 chksm。日期从 `publish_info.create_time` 取（unix timestamp，加 8 小时转 CST）。

### wxmp-fetch.py

```bash
# 单篇
python3 00_系统/agent/wxmp-fetch.py "https://mp.weixin.qq.com/s/XXXXX"

# 批量
python3 00_系统/agent/wxmp-fetch.py URL1 URL2 URL3

# 指定日期（页面取不到时用）
python3 00_系统/agent/wxmp-fetch.py --date 2026-09-20 URL
```

**输出格式**：`ARCH/YYYY/YYYY-MM-DD-safe_title.md`

已存在同名文件时自动追加时间戳后缀。

## 核心发现（2026-10 实测）

### 1. 短链不需要 chksm

后台 `appmsgpublish` 返回的短链格式 `/s/XXXXX`，不需要 `chksm` 参数即可完整访问。

- 短链页面 4.5MB 完整 DOM，`js_content` 正常渲染，零降级
- 之前误以为"必须带 chksm"是因为只测了存档里的 `__biz=...&mid=...&sn=...&chksm=...` 长链格式
- 那批长链 11 个里 9 个缺 chksm，9 月能抓到纯属微信当时不校验

### 2. 后台列表需要登录

- `appmsgpublish` 接口必须扫码登录，拿 token
- token 只存在于 URL query 里，过期即失效
- 登录态有时效，不能断中间状态

### 3. 两层嵌套 JSON

后台接口返回结构：

```json
{
  "base_resp": {"err_msg": "ok", "ret": 0},
  "is_admin": true,
  "publish_page": "{\"total_count\":324,...}"   // ← JSON 字符串！
}
```

`publish_page` 本身是字符串，里面的 `publish_list[].publish_info` 也是字符串。需要两次 `json.loads`。

### 4. type 参数是复合值

- 不是单个数字，是 `101_1_102_103`
- 单个数字（9/1/2/3/4）全部返回空

### 5. 存档匹配必须搜两个位置

**2026-10-05 踩坑**：匹配时只搜了年份目录（`2023/`、`2024/`...），漏掉了 `.github-pages/articles/`。导致 19 篇已有文章被误判为"缺失"，重复抓取后才发现。

**存档有两套并存**：
| 位置 | 来源 | 标题格式 |
|------|------|----------|
| 年份目录/ | 按需抓取 | 后台短标题（片名） |
| .github-pages/articles/ | 9 月批量抓取 | 页面完整标题（活动名） |

同一篇文章标题不同：
- 年份目录：`2023-03-22-鲸.md`
- .github-pages：`2023-03-22-放映本周日鲸大源.html`

**匹配时必须同时搜索两个位置**，用标题关键词 grep。

## wxmp-fetch.py 的 7 条踩坑（已写进脚本注释）

1. 短链不需要 chksm
2. `#img_swiper` 在 `#js_content` 之外，必须单独取
3. 同一张图有多个 URL 变体，按 mmbiz 图片 ID 去重
4. 排除 `pic_blank.gif`、`video_player_tmpl`、二维码
5. 内容类型看"有无"而非"等于几"：贴图类才有 `window.item_show_type='8'`
6. 短链页面 `document.title` 为空，标题从 `og:title` meta 取
7. 日期从 JS 变量 `create_time` 或 `ct` 取

## 完整流程

```
1. 拉列表          wxmp-list.py（扫码）
   ↓
   /tmp/wxmp-articles.json（324 篇，含短链）

2. 交叉比对        对比存档已有文章（两个位置都要搜）
   ↓
   找出真正缺失的 URL

3. 批量抓取        wxmp-fetch.py URL1 URL2 ...
   ↓
   年份目录/YYYY-MM-DD-标题.md

4. 校验            wxmp-verify.py
   ↓
   确认图文完整
```

## 常见错误与修复

### 错误 1：以为需要 chksm

**症状**：短链访问返回降级页
**原因**：用了 `__biz` 长链格式，那个确实需要 chksm
**修复**：用短链 `/s/XXXXX`，不需要任何参数

### 错误 2：匹配时只搜年份目录

**症状**：明明存档有的文章被报为"缺失"，抓取后发现重复
**原因**：`.github-pages/articles/` 里还有 294 篇
**修复**：匹配时同时搜索：
```python
# 年份目录
find . -maxdepth 2 -name "*.md" ! -path "*/_skill/*" ! -path "*/.github-pages/*"
# .github-pages
find .github-pages/articles -name "*.html" -o -name "*.md"
```

### 错误 3：tempkey URL 过期

**症状**：后台部分文章返回的是 `__biz=...&tempkey=...&chksm=...` 格式
**原因**：tempkey 是临时 token，过期后无法访问
**修复**：这 6 篇只能从页面手动复制短链，或放弃

### 错误 4：publish_page 解析报错

**症状**：`AttributeError: 'str' object has no attribute 'get'`
**原因**：`publish_page` 是 JSON 字符串不是 dict
**修复**：`wxmp-list.py` 的 `unwrap()` 函数自动解包

### 错误 5：日期为空

**症状**：后台 324 篇里 304 篇 `create_time` 为空
**原因**：后台 API 本身不给日期
**修复**：从文章页面的 JS 变量 `create_time` 取日期（页面有，后台没有）

## 依赖

```
Playwright (Python)
  - 路径: ~/Python/3.9/lib/python/site-packages/playwright
  - 浏览器: ~/Library/Caches/ms-playwright/chromium-1200
  - iPhone WeChat UA:
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)
     AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.40"
```
