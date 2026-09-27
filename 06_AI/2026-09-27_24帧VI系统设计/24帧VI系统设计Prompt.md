---
type: ai-draft
name: 24帧 VI 系统设计 Prompt
status: draft
editable: true
audience: owner
created: 2026-09-27
updated: 2026-09-27
based_on: "现有公众号头像 logo（黑底白字版）"
---

> AI 草稿。Logo 已定稿，本文件只出 VI 系统，不重做 logo。定稿后回填 `04_灵感/品牌策略/品牌手册.md` §视觉规范。

# 24帧 VI 系统设计 Prompt

## 一、现有 Logo 分析

### 核心元素

| 元素 | 构成 | 含义 |
|---|---|---|
| 主图形 | 斜45°电影票根：右上齿孔缺口 + 右侧3齿 + 票面3横线 | "买票看电影"，直接好懂 |
| 文字标 | 24FRAMES 白色粗黑无衬线 | 品牌名，识别度最高 |
| 布局 | 图形上、文字下，居中垂直排列 | 竖版构图，适合头像/贴纸 |
| 现有版本 | 黑底白字（反白） | 公众号头像在用 |

### 已有变体
- 反白版：黑底白字（当前用）
- 正版：白底黑字（推断存在）
- 待补充：单图形版、横版、水印版

## 二、色彩系统

### 主色（必用）

| 角色 | 颜色 | Hex | 用途 |
|---|---|---|---|
| 主色-黑 | 纯黑 | `#000000` | Logo主色、正文、深色背景 |
| 主色-白 | 纯白 | `#FFFFFF` | Logo反白、正文、浅色背景 |

### 辅助色（二选一，品牌点缀）

| 方案 | 颜色 | Hex | 理由 | 适合场景 |
|---|---|---|---|---|
| **A · 银幕红** ⭐ | 深红 | `#C44536` | 呼应放映厅红座椅/银幕，电影感强 | 电影社群气质 |
| B · 放映灯琥珀 | 暖琥珀 | `#E8A838` | 呼应放映灯暖光，情感温度 | 文艺温暖气质 |

**推荐 A · 银幕红**：logo 本身是黑白的工业感，银幕红能压住，不会显得太暖太文艺，符合独立电影放映社群的冷感气质。

### 中性色（配套）

| 角色 | 颜色 | Hex | 用途 |
|---|---|---|---|
| 深灰 | 深灰 | `#1A1A1A` | 正文次级、按钮 |
| 中灰 | 中灰 | `#6B7280` | 辅助文字、分割线 |
| 浅暖灰 | 暖灰 | `#F5F1EA` | 底色、卡片背景（不是纯灰，胶片纸质感） |

### 会员卡等级色（独立于品牌色）

现有会员卡已用橙/蓝/绿分色，建议保留作为"等级标识色"，不参与品牌VI，只在会员卡场景使用：

| 等级 | 颜色 | Hex | 备注 |
|---|---|---|---|
| 创始会员 | 橙 | `#FF6B1A` | 现有 |
| 年度会员 | 蓝 | `#1E40AF` | 现有 |
| 半年会员 | 绿 | `#16A34A` | 现有 |
| 咸淡卡 | 蓝（浅） | `#3B82F6` | 现有 |

## 三、字体系统

| 用途 | 中文字体 | 英文/数字字体 | 字重 |
|---|---|---|---|
| Logo 文字 | — | Space Grotesk（或 Inter） | Bold 700 |
| 大标题 | 思源黑体 | Space Grotesk | Bold 700 |
| 小标题 | 思源黑体 | Inter | SemiBold 600 |
| 正文 | 思源黑体 | Inter | Regular 400 |
| 数字/价格 | 思源黑体 | Inter | Medium 500 |
| 引文/金句 | 思源宋体 | Cormorant Garamond | Italic |
| 注释/版权 | 思源黑体 | Inter | Light 300 |

**字体获取**
- 思源黑体 / 思源宋体：Google Fonts 免费商用，或 https://github.com/adobe-fonts/source-han-sans
- Space Grotesk：Google Fonts 免费商用
- Inter：Rasmus Andersson 免费商用
- Cormorant Garamond：Google Fonts 免费商用
- 方正兰亭黑：方正字库，商用需授权，不建议

**核心原则**：全品牌只用 2 套字体——思源黑体（中文）+ Space Grotesk / Inter（英文）。不堆字体，不混用。

## 四、Logo 使用规范

### 必备变体（6种）

| 变体 | 用途 | 交付 |
|---|---|---|
| 横版主标 | 海报顶栏、网页 header | SVG + PNG |
| 竖版主标 | 公众号头像、App icon | SVG + PNG |
| 单图形（icon only） | 缩略图、水印、胸针 | SVG + PNG |
| 反白版 | 深色背景 | SVG + PNG |
| 单色版（黑） | 印刷单色、浅背景 | SVG |
| 水印版 | 海报/视频水印 | SVG（透明度 15-20%） |

### 使用规则

**允许**
- 等比缩放
- 黑白两色之间切换
- 在深色/浅色背景之间切换

**禁止**
- 变形、拉伸、压扁
- 改颜色（除黑白切换外）
- 加阴影、描边、渐变、发光
- 在彩色背景上使用（除非该颜色是辅助色银幕红，且logo为反白）
- 旋转角度（除已设计的45°票根外）
- 与背景图案重叠导致识别不清

### 安全区域

- 四周留白 ≥ logo 高度的 25%
- 不与任何其他图形/文字贴边

### 最小尺寸

- 竖版主标：宽 ≥ 80px（屏幕）/ 30mm（印刷）
- 单图形 icon：宽 ≥ 24px（屏幕）/ 8mm（印刷）

## 五、应用场景清单

### 必做（7类）

| # | 场景 | 具体内容 | 数量 |
|---|---|---|---|
| 1 | Logo 变体 | 6种必备变体 | 6 |
| 2 | 会员卡 | 创始/年度/半年/咸淡卡 | 4 |
| 3 | 名片 | 正反面 | 2 |
| 4 | 公众号/微信头像 | 1:1 头像版 | 1 |
| 5 | 海报/角标 | 放映海报模板 + 水印 | 2 |
| 6 | 社交媒体 | 小红书封面、微信封面、微博头像 | 3 |
| 7 | 周边 | 帆布袋、贴纸、马克杯、票根 | 4 |

### 选做（3类）

| # | 场景 | 具体内容 |
|---|---|---|
| 8 | 放映厅物料 | 座位卡、节目单、胸牌、场务贴纸 |
| 9 | 数字物料 | 公众号文章模板、视频号封面、直播背景板 |
| 10 | 联合出品物料 | 合作片单海报、联合出品片头板 |

## 六、完整 Prompt（给 AI VI 设计师）

### 6.1 中文 Brief（给 Claude / GPT / Kimi / 元宝）

```
你是一位资深品牌视觉识别(VI)设计师。请基于 24FRAMES 现有 logo，设计一套完整的 VI 系统。

【重要】Logo 已定稿，不要再改。你的任务是围绕这个 logo 推导 VI 规范和应用场景。

【现有 Logo】
- 主图形：斜45°电影票根（右上齿孔缺口 + 右侧3齿 + 票面3横线），白色线条
- 文字标：24FRAMES，白色粗黑无衬线（Space Grotesk 或 Inter Bold 风格）
- 布局：图形上、文字下，居中垂直排列
- 现有版本：黑底白字（反白版，公众号头像在用）
- 视觉风格：极简、扁平、现代、独立电影气质

【品牌背景】
24帧 / 24FRAMES PROJECT 是2014年在成都成立的独立电影放映与影迷社群品牌，运营4年，办过220+场放映。核心业务：独立放映 + 主题策展 + 映后交流 + 影迷社群。

品牌魂："不确定性的浪漫"。我们相信电影是情感的出口，不是消遣的工具。

【色彩系统（已定，请遵守）】
- 主色：黑 #000000 + 白 #FFFFFF
- 辅助色：银幕红 #C44536（品牌点缀，少量使用）
- 中性：深灰 #1A1A1A / 中灰 #6B7280 / 浅暖灰 #F5F1EA
- 会员卡等级色（仅会员卡场景）：橙 #FF6B1A（创始）/ 蓝 #1E40AF（年度）/ 绿 #16A34A（半年）/ 蓝浅 #3B82F6（咸淡卡）

【字体系统（已定，请遵守）】
- 中文：思源黑体（免费商用）
- 英文/数字：Space Grotesk（标题）+ Inter（正文）
- 引文：思源宋体 + Cormorant Garamond Italic
- 全品牌只用这2-3套字体，不混用

【Logo 使用规范（已定）】
- 6种必备变体：横版、竖版、单图形、反白、单色、水印
- 禁止变形/改色/加阴影/渐变/在彩色背景使用
- 四周留白 ≥ logo 高度 25%
- 最小尺寸：竖版 ≥ 80px / 30mm

【你的任务：设计以下应用场景】

1. Logo 变体（6种）
   - 横版主标：图形在左，文字在右
   - 竖版主标：图形上，文字下（现有风格）
   - 单图形 icon：仅电影票根
   - 反白版：浅字深底
   - 单色版：纯黑/纯白
   - 水印版：透明度 15-20%

2. 会员卡（4张）
   - 创始会员卡：橙色 #FF6B1A 主色，金色点缀
   - 年度会员卡：蓝色 #1E40AF 主色
   - 半年会员卡：绿色 #16A34A 主色
   - 咸淡卡：浅蓝 #3B82F6 主色
   - 每张卡包含：logo、会员卡名、权益列表、价格、活动时间、二维码
   - 尺寸：85.6×54mm（标准信用卡尺寸）

3. 名片（正反面）
   - 正面：logo + 姓名 + 职位 + 联系方式
   - 反面：品牌 slogan "如果有一部电影会让我们相遇"
   - 尺寸：90×54mm

4. 公众号头像
   - 1:1 方形，黑底白字 logo
   - 300×300px

5. 海报模板
   - 放映海报：顶部 logo 水印 + 底部 logo 单色
   - 片名、导演、时间、地点、票务信息层级清晰
   - 尺寸：60×80cm（标准海报）

6. 社交媒体模板（3套）
   - 小红书封面：3:4 竖版，logo 在右下角
   - 微信封面：21:9 横幅
   - 微博头像：1:1

7. 周边（4件）
   - 帆布袋：logo 居中，单色印
   - 贴纸：圆形/方形，多尺寸
   - 马克杯：logo 环形或正面
   - 票根：复刻 logo 中的电影票根，做成实体票根

【输出要求】

请给出：
1. 完整 VI 规范手册（markdown 格式，含色彩/字体/logo规范/应用场景）
2. 每个应用场景的具体设计描述（视觉构成、布局、尺寸、字体）
3. SVG 路径代码（能给的尽量给，方便直接用）
4. 每张 mockup 的 HTML/CSS 代码（能用浏览器预览）
5. 交付物清单 + 格式要求

【避免】
- 不要改 logo（图形、字体、布局都不动）
- 不要用大红大绿大紫的饱和色（除会员卡等级色）
- 不要用装饰体、书法体
- 不要加渐变、阴影、3D、发光
- 不要"院线感"、"奥斯卡感"、"电影节感"
```

### 6.2 英文 Prompt（给 Midjourney / 即梦 / Flux 出 mockup）

**会员卡 mockup：**
```
mockup of a membership card design for "24FRAMES" independent film community,
minimalist flat design, card front showing logo (tilted 45-degree film ticket stub icon + "24FRAMES" bold text) centered at top,
membership tier name and benefits list below, deep navy #1E40AF background version,
warm off-white #F5F1EA card face, cinematic red #C44536 accent line,
standard credit card size 85.6x54mm,
flat vector, editorial, Swiss design, high negative space,
no photo, no 3d, no gradient --ar 16:9 --style raw --v 6
```

**名片 mockup：**
```
business card mockup for "24FRAMES" film screening community,
minimalist design, front: logo centered, name and contact info below,
back: brand slogan in cursive script,
black #000000 card with white #FFFFFF text,
size 90x54mm, flat vector, editorial, Swiss design,
photorealistic mockup on dark wooden desk --ar 3:2 --style raw --v 6
```

**海报 mockup：**
```
film screening poster mockup for "24FRAMES" community,
minimalist design, film title and director info in large typography,
small "24FRAMES" logo watermark at top-left corner,
full logo at bottom-center,
deep navy #1E40AF background, warm off-white #F5F1EA text,
cinematic red #C44536 accent,
size 60x80cm, flat vector, editorial, Swiss design,
photorealistic mockup on cinema wall --ar 3:4 --style raw --v 6
```

**帆布袋 mockup：**
```
canvas tote bag mockup with "24FRAMES" logo centered,
black logo on natural beige canvas bag,
tilted 45-degree film ticket stub icon above "24FRAMES" bold text,
photorealistic, cinematic lighting,
no other text, no decorations, minimalist --ar 3:4 --style raw --v 6
```

## 七、交付清单

| # | 交付物 | 格式 | 尺寸/规格 | 用途 |
|---|---|---|---|---|
| 1 | Logo 横版主标 | SVG + PNG | 4000×1000 | 海报顶栏、网页 header |
| 2 | Logo 竖版主标 | SVG + PNG | 2000×2000 | 公众号头像、App icon |
| 3 | Logo 单图形 | SVG + PNG | 2000×2000 | 缩略图、水印、胸针 |
| 4 | Logo 反白版 | SVG + PNG | 2000×2000 | 深色背景 |
| 5 | Logo 单色版（黑） | SVG | 2000×2000 | 印刷单色 |
| 6 | Logo 水印版 | SVG | 2000×2000 | 海报/视频水印（透明度 15-20%） |
| 7 | 创始会员卡 | PDF + PNG | 85.6×54mm / 300dpi | 印刷 |
| 8 | 年度会员卡 | PDF + PNG | 85.6×54mm / 300dpi | 印刷 |
| 9 | 半年会员卡 | PDF + PNG | 85.6×54mm / 300dpi | 印刷 |
| 10 | 咸淡卡 | PDF + PNG | 85.6×54mm / 300dpi | 印刷 |
| 11 | 名片（正面） | PDF | 90×54mm / 300dpi | 印刷 |
| 12 | 名片（反面） | PDF | 90×54mm / 300dpi | 印刷 |
| 13 | 公众号头像 | PNG | 300×300 | 微信头像 |
| 14 | 海报模板 | PDF + AI | 60×80cm / 300dpi | 放映海报 |
| 15 | 小红书封面模板 | PNG | 1080×1440 (3:4) | 社交媒体 |
| 16 | 微信封面模板 | PNG | 2100×900 (21:9) | 公众号 |
| 17 | 微博头像 | PNG | 400×400 | 微博 |
| 18 | 帆布袋印稿 | AI + PDF | 38×42cm / 300dpi | 周边 |
| 19 | 贴纸（多尺寸） | SVG + PNG | 圆形/方形多尺寸 | 周边 |
| 20 | 马克杯印稿 | AI + PDF | 环形展开图 / 300dpi | 周边 |
| 21 | 票根（实体） | PDF | 实际尺寸 / 300dpi | 周边 |
| 22 | VI 规范手册 | PDF + MD | — | 内部使用 + 合作方可用 |

## 八、和 AI 设计师的对齐流程

1. **第一次对话**：发 6.1 完整 brief，让它出 VI 规范手册 + 6种logo变体 SVG 代码
2. **第二次对话**：让它出 4 张会员卡的 HTML/CSS mockup（浏览器能看）
3. **第三次对话**：让它出名片、海报、社交媒体的 HTML/CSS mockup
4. **第四次对话**：让它出周边（帆布袋/贴纸/马克杯/票根）的设计描述 + SVG 印稿
5. **出图验证**：拿 6.2 的英文 prompt 去 MJ/即梦出 mockup 候选图，挑最满意的反哺给 AI 精修
6. **最终交付**：让 AI 把所有 SVG 代码 + PDF 印稿整理成一份压缩包

## 九、给宇航员的决策点

1. **辅助色选哪个？** A · 银幕红 #C44536（推荐，冷感独立）/ B · 放映灯琥珀 #E8A838（暖感文艺）
2. **会员卡分色保留还是统一？** 保留橙/蓝/绿（现状）/ 统一用银幕红的不同明度
3. **要不要做联合出品物料？**（选做第10类，给《浮生若丽》用的）
4. **数字物料要不要做？**（公众号文章模板、视频号封面等，选做第9类）

决策后我可以更新 prompt，让 AI 设计师按最终决策出全套。

## 关联

- 品牌基础：[[品牌手册]]、[[品牌目标]]
- Logo 设计思路（历史参考，logo 已定稿）：`../2026-09-27_24帧logo设计prompt/24帧Logo设计Prompt.md`
- 现有 logo 图片：`05_档案/俱乐部/24帧俱乐部LOGO.jpg`、公众号头像 `公众号头像（黑底白字）.png`
