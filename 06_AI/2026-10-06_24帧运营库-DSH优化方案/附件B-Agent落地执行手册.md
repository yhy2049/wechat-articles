---
type: reference
name: 附件B-Agent落地执行手册
status: review
editable: true
audience: agent
created: 2026-10-06
updated: 2026-10-06
source: ai-generated
tags: [基建, 可抄模板]
---

# 附件B · Agent 落地执行手册

> 配套 [[24帧运营库-DSH优化方案]]、[[附件A-规范修订对照表]]。
> **本文件里的每一段都是可以直接落盘的内容**。复制 → 改路径 → 建文件 → 记 changelog → commit。
> 落盘位置在每个小节标题下写明。

---

## B1 · `00_系统/_schema.md`（P0-2）

**落盘到**：`00_系统/_schema.md`

````markdown
---
type: reference
name: _schema
status: final
editable: true
audience: both
created: 2026-10-06
updated: 2026-10-06
---

# 24帧运营库 · frontmatter Schema（单一事实源）

> 全库所有 md 文件的 frontmatter 取值以本文件为准。
> `运营手册.md`、`归档操作规范.md`、各 skill **只引用本文件，不再各写一份枚举**。
> 新增取值 = 改本文件 + 记 changelog。不许在别的文件里私自定义。

## 1. 通用字段（所有文件必填）

| 字段 | 说明 | 取值 |
|---|---|---|
| `type` | 文件类型 | 见 §2 |
| `status` | 文档生命周期 | `draft` / `review` / `final` / `archive` |
| `audience` | 给谁看 | `owner` / `agent` / `both` / `public` |
| `editable` | agent 能否改 | `true` / `false` |
| `created` | 创建日 | `YYYY-MM-DD` |
| `updated` | 最后修改日 | `YYYY-MM-DD` |
| `name` | 文件名（不含 .md） | 文本 |

**可选补充字段**：`source`（`ai-generated` / `human`）、`tags`、`direction`、`related_projects`、`related_people`、`supersedes`。

### status 四值的确切含义

| 值 | 含义 | 谁负责推进 |
|---|---|---|
| `draft` | 未定稿，agent 可以随便改 | agent |
| `review` | 等宇航员拍板，**必须同时出现在 `HOME.md` 的「等我拍板」段** | 宇航员 |
| `final` | 已定稿，agent 只做维护不做改写 | 宇航员 |
| `archive` | 归档，只读 | 无人 |

### audience 四值的确切含义

| 值 | 含义 |
|---|---|
| `owner` | 只给宇航员看（如 `HOME.md`） |
| `agent` | agent 工作记忆，对宇航员隐藏（如 `00_系统/agent/`） |
| `both` | 双方都看（绝大多数文件） |
| `public` | 内容已定稿且不含内部信息，**可以直接给合作方看**（对外计划书、媒体介绍） |

## 2. type 取值表（10 个合法值）

| type | 用在哪 | 必填专属字段 | 落盘位置 |
|---|---|---|---|
| `meeting` | 会议 / 通话 / 访谈 / 录音存档 | `title`, `date`, `participants`, `direction`, `related_projects`, `related_people` | `05_档案/会议存档/` |
| `person` | 人物档案 | `aka`, `relation`, `category` | `03_人物/` |
| `project` | 项目概况页 | `direction`, `goal`, `progress`, `priority` | `02_项目/[项目名]/` |
| `direction` | 业务方向 | `status` 固定 `final` | `01_方向/[方向名]/` |
| `inspiration` | 灵感 | `stage`, `captured`, `source` | `04_灵感/AI加工区/` |
| `reference` | 可复用的参考 / 研究 / 规范 / 方法 | — | `00_系统/`、`04_灵感/知识库/`、`01_参考文档/` |
| `draft` | AI 草稿 / 半成品 | — | `06_AI/YYYY-MM-DD_主题/` |
| `output` | 已成稿待发或已发布文案 | — | `06_AI/`（未发）或 `05_档案/公众号存档/`（已发） |
| `media` | 对外媒体材料 | — | `05_档案/媒体/` |
| `task` | **历史遗留，不再新建** | — | — |

### 24 种历史取值 → 10 个合法值的映射

| 出现过但不合法 | 归到 |
|---|---|
| `影评`、`公众号文章`、`游戏推荐`、`评分`、`analysis`、`guide`、`report` | `draft`（未定稿）或 `output`（已发布） |
| `项目会议`、`非正式饭局谈话` | `meeting` |
| `direction-reference`、`brand-resource`、`project_plan`、`concept`、`external-submission` | `reference` |
| `ai-draft` | `draft` |
| `task` | `project`（并入项目页的 `## 待办` 段） |

> 迁移原则：**旧文件不强行批量改**，下次动到哪个文件就顺手把 `type` 改成合法值。

## 3. 枚举字段

| 字段 | 用在哪 | 取值 |
|---|---|---|
| `progress` | `type: project` | `待办` / `进行中` / `等待中` / `已完成` / `已取消` / `已终止` |
| `stage` | `type: inspiration` | `新捕获` / `已加工` / `预启动` / `已转项目` / `已归档` |
| `priority` | `project` | `high` / `medium` / `low` |
| `category` | `person` | `internal` / `external` |
| `direction` | 多处 | 必须是 `01_方向/` 下真实存在的 5 个之一：观影团 / 策展人 / 影视创作 / 宣发平台 / AI影像 |

> ⚠️ `status` 和 `progress` 是**两个维度**：`status` 管文档状态（草稿→定稿→归档），`progress` 管事情状态（在做→做完）。不要用 `status: active` 或 `status: 进行中`——那是 `progress` 的活。

## 4. 三条硬规则

1. **新建文件必查本表**，`type`/`status`/`audience` 三个字段落不进枚举 = 不许建。
2. **改 `status` 为 `review` 时，必须同时把该文件加到 `HOME.md` 的「等我拍板」段**。否则它会像现在那 4 个文件一样挂 114 天没人管。
3. **`updated` 必须在每次实质性修改时更新**，不能只靠 git 时间（Obsidian 和 agent 读的是 frontmatter）。

## 关联

- [[运营手册]] ｜ [[_index]] ｜ [[归档操作规范]]
````

---

## B2 · 三份嵌套 `AGENTS.md`（P0-5）

> DSH 的机制：agent 每次 `read`/`write`/`edit` 到一个更深目录，**下一次请求就会带上那层的 `AGENTS.md`**。所以局部规则只在该用的时候才进上下文，不占无关任务的预算。
> 出处：本机 `~/.dsh/profiles/node_modules/@deepseek-ai/dsh-agent-instructions/README.md`。

### B2-0 根 `AGENTS.md` 的三处增补（不重写整个文件）

> **硬约束**：根 `AGENTS.md` **压到 150 行以内**。规则：**能放局部就不放根**。
> 依据：Claude Code 官方文档要求单文件 "target under 200 lines per file. Longer files consume more context and reduce adherence."（[docs.claude.com/…/memory](https://docs.claude.com/en/docs/claude-code/memory)）
> 另外：Anthropic 上下文工程明确说"目录层级和命名本身就是给 agent 的信号"，所以局部规则放对应目录，比堆在根文件里效果更好。

**增补 1** —— 在 `## 2. 目录速览` 之后插入：

```markdown
## 2.5 局部规则自动加载

进入以下目录时 DSH 会自动把该目录的 `AGENTS.md` 追加进上下文，不需要手动读：
- `02_项目/` —— 写项目页前
- `06_AI/` —— 写 AI 产出前
- `05_档案/会议存档/` —— 归档前

**新增目录级规则就放对应目录的 `AGENTS.md`，不要往根文件里堆。本文件上限 150 行。**
```

**增补 2** —— 在 `## 3. 硬规则` 的 8 条后追加 3 条：

```markdown
9. **raw 层只读**：`05_档案/` 是原始层（会议存档 / 公众号存档 / 媒体 / 放映数据）。
   agent **只能读**——不得改写、不得移动、不得重命名。
   唯一例外：按 `00_系统/归档操作规范.md` 在 `05_档案/会议存档/` **新建**文件。
   所有加工产物只能写 `06_AI/` 与 `04_灵感/`。

10. **查库先读 `_index.md`**：任何"找某个项目/人物/资料"的请求，第一步读
    `00_系统/_index.md`，再按行里的摘要钻取具体文件。不要一上来就全库 grep。
    新建 / 改名 / 删除内容文件时，同步更新 `_index.md`。

11. **回答要落库**：任何一次对话里产出的**分析、对比表、判断、方案**，只要宇航员认可
    （说"可以""就这样""存下来"，或没有反对），必须落成 `06_AI/<日期>_<主题>/` 下的
    页面并在 `_index.md` 登记。禁止只留在聊天里。

12. **改已有文件用定点改，不用整文件重写**：先读，再只改目标段落 / 字段
    （借鉴 mcp-obsidian 的 `patch_content` 语义：按 heading、block ref 或
    frontmatter 字段插入）。整文件重写会吃掉别人的内容。
```

**增补 3** —— 在 `## 3. 硬规则` 后加一节「日志用法」：

```markdown
## 3.5 `_changelog.md` 用法（格式即接口）

每条必须是 `## [YYYY-MM-DD HH:mm] 操作类型 | 文件名`。
这个前缀是给人和其他 agent 用的接口，不要改：

    grep "^## \[" 00_系统/_changelog.md | tail -10     # 最近 10 次操作
```

### B2-1 `02_项目/AGENTS.md`

**落盘到**：`02_项目/AGENTS.md`

```markdown
# 02_项目 · 局部规则

> 写任何项目页之前读这一页。总纲见根 `AGENTS.md`，frontmatter 取值见 `00_系统/_schema.md`。

## 一个项目一个文件夹

```
02_项目/[项目名]/
├── [项目名].md        # 项目概况页（type: project）—— 唯一入口
├── 01_参考文档/       # 背景调研、协议、群聊对齐信息
├── 02_归档文件/       # 项目原始素材（剧本、排期）
├── 03_AI文档/         # AI 生成的方案 / 初稿
└── 04_草稿/           # 草稿
```

子目录**按需建**，不预建空壳。

## 三条硬规则

1. **会议不放这里**。所有会议 / 通话 / 访谈 / 录音 → `05_档案/会议存档/YYYY-MM-DD_主题.md`，项目页用 `[[文件名]]` 引用。
2. **不建 task 文件**。待办写在项目页正文的 `## 待办` 段，格式：`- [ ] 事项 — @执行人 — 截止 YYYY-MM-DD`。
3. **项目页必须有的段落**：一句话定位 / 关键参数表 / 排期 / 待办 / 决策记录 / 风险 / 关联。

## 写完必做

- [ ] frontmatter 六个通用字段齐全（见 `_schema.md` §1）
- [ ] `direction` 填 `01_方向/` 下真实存在的方向名
- [ ] `progress` 反映真实状态（`进行中` 的项目才出现在 `HOME.md` 的「在推什么」段）
- [ ] `HOME.md` 的项目表格同步更新
- [ ] `_changelog.md` 追加一条
```

### B2-2 `06_AI/AGENTS.md`

**落盘到**：`06_AI/AGENTS.md`

```markdown
# 06_AI · 局部规则

> 写任何 AI 产出之前读这一页。frontmatter 取值见 `00_系统/_schema.md`。

## 一个任务一个子目录

```
06_AI/YYYY-MM-DD_主题/
├── 主文件.md              # 正文（未校准）
├── 00_原始素材/           # ★原始层：转写稿、截图、json、抓取结果，只读不改写
├── attachments/           # 配图
└── 其他版本.md            # 排版版 / 小红书版 / 公众号版
```

## 三态生命周期

| 状态 | 位置 | 标记 |
|---|---|---|
| ① 未校准 | `06_AI/` | 文件名不加后缀 |
| ② 已校准·待发 | `06_AI/` | 文件名加 `_已校准` |
| ③ 已发布 | `05_档案/公众号存档/` | 文件名完整 |

## 三条硬规则

1. **原始素材和成品分层**。whisper 的 `.json`/`.txt`、网页抓取的 HTML、下载的图片 → 一律进 `00_原始素材/`，不许和正文并排放在主题目录根下。
2. **库里只留 md**。docx / pdf / 大图不进 `06_AI/`；要发给合作方的 Word 放库外（如 `~/Downloads/`），库内只留 md 正本。
3. **单张图 > 5 MB 就别进库**。用路径引用或压缩后再放。

## 写完必做

- [ ] 正文 frontmatter：`type: draft`、`audience`、`source: ai-generated`
- [ ] 目录名符合 `YYYY-MM-DD_主题`
- [ ] `## 关联` 段有 wikilink（不能是孤岛）
- [ ] `_changelog.md` 追加一条
```

### B2-3 `05_档案/会议存档/AGENTS.md`

**落盘到**：`05_档案/会议存档/AGENTS.md`

```markdown
# 05_档案/会议存档 · 局部规则

> 归档之前读这一页。完整 SOP 见 `00_系统/归档操作规范.md`，frontmatter 取值见 `00_系统/_schema.md`。

## 这里是原始层

会议 / 通话 / 访谈 / 录音转写的**唯一归属**。项目目录里不放会议。

**原始层规则**：本目录文件**不加出站 wikilink**。靠 frontmatter 的 `direction` / `related_projects` / `related_people` 被其他笔记反向索引。

## 命名

`YYYY-MM-DD_主题.md`——**日期后必须是下划线**，不是连字符。主题里需要停顿用 `-`：

```
✅ 2026-10-06_孙义与宇航员沟通-银发戏剧工作坊与定制短片.md
❌ 2026-05-17-24帧策展团队暨多项目启动会.md
```

## frontmatter 必填

`type: meeting`、`title`、`date`、`participants`、`direction`、`related_projects`、`related_people`、`tags`、`status: archive`、`editable: false`、`audience`、`created`、`updated`、`source`。

## 归档完必须做的三件事（缺一件 = 没归档完）

- [ ] 更新参会人物页（`03_人物/`）：行为记录 + 画像速写
- [ ] 更新项目和方向（新项目要立项，老项目补决策记录）
- [ ] 记 `_changelog.md`

## 口误审计（Step 1 必做）

- 音误：人名 / 地名 / 机构名 / 专业术语逐个核实，不确定的查证后改
- 矛盾：前后矛盾的事实**列出来问宇航员**，不要自己选一个写进去
- 口癖（然后、就是、我觉得）**保留**——这是访谈存档的真实性特征
- 转写噪音（"1号讲话人"）删除
```

---

## B3 · `dsh headless` + 定时任务（P1-3）

> **本节配置已在本机实测跑通**（2026-10-06）：`dsh --profile headless --patch /tmp/dsh-headless-patch.yml "只回答两个字：可用"` → 返回 `可用`，退出码 0。
> 不配这一步，`dsh --profile headless "…"` 会报 `MISSING_CREDENTIAL: llm-deepseek: no API key for provider route "deepseek-official"`。

### B3-1 `~/.dsh/profiles/headless/cordis.patch.yml`（库外文件）

**落盘到**：`~/.dsh/profiles/headless/cordis.patch.yml`

```yaml
# headless profile 的模型路由。desktop profile 已经配了，headless 没有，所以默认路由
# deepseek-official 找不到 key。这里指向 sensenova（key 已在 ~/.dsh/.credentials.yaml）。
- id: llm-pi-ai
  name: "@deepseek-ai/dsh-llm-pi-ai"
  config:
    providers:
      sensenova:
        displayName: sensenova
        apiKeyEnv: SENSENOVA_API_KEY
        api: openai-completions
        baseURL: https://token.sensenova.cn/v1/
        models:
          - id: deepseek-v4-flash
            name: deepseek-v4-flash
            contextWindow: 1048576
- id: agent-default-model
  name: "@deepseek-ai/dsh-agent-default-model"
  config:
    provider: sensenova
    model: deepseek-v4-flash
```

**验证**：

```bash
cd ~/Documents/24帧运营库
dsh --profile headless "回答两个字：可用"; echo "exit=$?"
# 期望：输出「可用」，exit=0
```

> 注意：`dsh-schedule`（会话内提醒）**不能**用来做"每天定时跑库维护"——它要求有一个活着的 session 才会投递，最小间隔 5 分钟，且不支持日历式规则（"每个工作日 9 点"）。跨 session 定时只能走 `dsh headless` + launchd/cron。

### B3-2 `00_系统/agent/vault-lint.sh`

**落盘到**：`00_系统/agent/vault-lint.sh`，`chmod +x`

```bash
#!/usr/bin/env bash
# 24帧运营库 · 一键体检 + 日志
# 用法：00_系统/agent/vault-lint.sh [--quiet]
set -uo pipefail
VAULT="$(cd "$(dirname "$0")/../.." && pwd)"
LOG_DIR="$VAULT/00_系统/agent/lint-logs"
STAMP="$(date +%Y-%m-%d_%H%M)"
mkdir -p "$LOG_DIR"

cd "$VAULT" || exit 1
OUT="$LOG_DIR/$STAMP.md"

{
  echo "# 库体检 $STAMP"
  echo
  echo '## 健康检查'
  echo '```'
  python3 "$VAULT/00_系统/agent/vault-health-check.py" --detail 2>&1
  echo '```'
  echo
  echo '## 工作区状态'
  echo '```'
  git status --short | head -30
  echo '```'
  echo
  echo '## 最近 24h 改动'
  echo '```'
  find "$VAULT" -name '*.md' -newermt '-1 day' -not -path '*/.git/*' \
       -not -path '*/公众号存档/*' | sed "s|$VAULT/||" | head -30
  echo '```'
} > "$OUT"

ERRORS=$(python3 "$VAULT/00_系统/agent/vault-health-check.py" 2>&1 | grep -c '🔴' || true)
if [ "${1:-}" != "--quiet" ]; then
  echo "体检完成 → $OUT"
  echo "错误项：$ERRORS"
fi
[ "$ERRORS" -eq 0 ]
```

### B3-3 launchd 定时（每天 09:00）

**落盘到**：`~/Library/LaunchAgents/com.24frames.vault-lint.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.24frames.vault-lint</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>-lc</string>
    <string>~/Documents/24帧运营库/00_系统/agent/vault-lint.sh --quiet</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict><key>Hour</key><integer>9</integer><key>Minute</key><integer>0</integer></dict>
  <key>StandardOutPath</key><string>/tmp/24frames-vault-lint.log</string>
  <key>StandardErrorPath</key><string>/tmp/24frames-vault-lint.err</string>
</dict>
</plist>
```

安装与检查：

```bash
launchctl unload ~/Library/LaunchAgents/com.24frames.vault-lint.plist 2>/dev/null
launchctl load  ~/Library/LaunchAgents/com.24frames.vault-lint.plist
launchctl list | grep 24frames        # 期望看到 com.24frames.vault-lint
```

> **纪律**：定时任务**只报告，不改内容**。agent 想改任何东西，走人确认。

### B3-4 每周一次 LLM 周报（可选，消耗 token）

```bash
cd ~/Documents/24帧运营库
LATEST=$(ls -t 00_系统/agent/lint-logs/*.md | head -1)
dsh --profile headless "$(cat <<EOF
你是24帧运营库的维护 agent。读这份体检日志，做三件事：
1. 找出本周新出现的问题（对比 00_系统/agent/经验沉淀.md 里已沉淀的经验，重复出现的不算新问题）
2. 每个新问题压缩成一句「问题 + 一个 action」
3. 输出 Markdown，写入 06_AI/\$(date +%Y-%m-%d)_库健康周报/周报.md，并把新经验追加到 00_系统/agent/经验沉淀.md

体检日志：
$(cat "$LATEST")
EOF
)"
```

---

## B4 · 新版 `.agents/skills/24frames-vault/SKILL.md`（P0-4）

**落盘到**：`24帧运营库/.agents/skills/24frames-vault/SKILL.md`

> DSH 会扫项目根（含 `.git` 的最近祖先）下的 `.agents/skills/`，优先级 **rank 200**，高于用户级 `~/.agents/skills/`（rank 500）。
> 出处：本机 `@deepseek-ai/dsh-skill-filesystem/README.md`「Roots and priority」。
> 好处：skill 跟着库走、进 git、Claude Code / Codex 也能读，改库=改 skill，不会再出现"skill 说 6 个方向、库里只有 5 个"这种脱节。

```markdown
---
name: 24frames-vault
description: "24FRAMES 运营库入口。5+1 目录结构、frontmatter schema、归档/灵感/项目工作流。TRIGGER: 24帧, 运营库, 归档, 会议, 项目, 人物, 灵感, 知识库, 放映, 公众号草稿"
---

# 24帧运营库 · 入口

库根：`~/Documents/24帧运营库`（git 仓库）。**规范在库内，本 skill 只做路由，不复制规范内容。**

## 进场三步（不许跳）

1. 读库根 `AGENTS.md` —— 入口 + 硬规则 + 决策灯
2. 读 `00_系统/_schema.md` —— frontmatter 唯一枚举表
3. 按下面的路由表读对应规范，再动手

## 路由表

| 要做什么 | 读哪一份 | 落盘位置 |
|---|---|---|
| 归档 / 存储音 / 会议转写 | `00_系统/归档操作规范.md` | `05_档案/会议存档/YYYY-MM-DD_主题.md` |
| 写 / 更新项目页 | `02_项目/AGENTS.md` | `02_项目/[项目名]/` |
| 写 AI 产出 / 公众号草稿 | `06_AI/AGENTS.md` | `06_AI/YYYY-MM-DD_主题/` |
| 灵感捕获与加工 | `04_灵感/README.md` | `04_灵感/AI加工区/` |
| 建 / 更新人物 | `00_系统/_schema.md` §2 | `03_人物/[人名].md` |
| 改库结构 / 加枚举值 | `00_系统/运营手册.md`（**红灯，先问宇航员**） | — |
| 库体检 | 跑 `python3 00_系统/agent/vault-health-check.py --detail` | 报告写 `00_系统/agent/lint-logs/` |
| 找文件 | `python3 00_系统/agent/vault-search.py "关键词"` | — |

## 目录速览

```
00_系统/   手册、_schema、索引、changelog、agent 脚本     ← 受控
01_方向/   5 个方向：观影团 / 策展人 / 影视创作 / 宣发平台 / AI影像
02_项目/   一项目一文件夹（项目 + 待办 + 素材），★会议不放这里
03_人物/   每人一篇
04_灵感/   AI加工区 + 知识库 + 品牌策略 + 归档
05_档案/   会议存档（★唯一归属）+ 公众号存档 + 媒体 + 放映数据   ← 只读
06_AI/     AI 草稿/半成品，YYYY-MM-DD_主题/ 子目录
```

## 硬规则

1. 不读不动：任何带名称的动作前先读对应规范。
2. 会议唯一归属 `05_档案/会议存档/`，命名 `YYYY-MM-DD_主题.md`（下划线）。
3. 新文件必须有 frontmatter，取值必须在 `_schema.md` 枚举内。
4. 新文件必须有 `## 关联` 段（不许有孤岛文件）。
5. 每次动手后记 `_changelog.md`：`## [YYYY-MM-DD HH:mm] 操作类型 | 文件名`。
6. 改动后 `git add -A && git commit`。
7. 不虚构：信息缺失标"待补充"，找不到依据就明说。
8. **发现规范自相矛盾 → 停下改规范，不要写"已知陷阱"绕过。**

## 决策灯

- 🔴 **红灯（先问宇航员）**：涉及钱 / 对外发布 / 删文件 / 新建人物或项目 / 改运营手册或 `_schema.md`
- 🟡 **黄灯（做完记 changelog）**：可逆编辑、归档、整理、lint 修复、灵感加工、画像更新
- 🟢 **绿灯（直接做）**：按模板生成、查询、数据快照、体检

> 两套口径要统一：本库的"红灯"= **先问**；`astronaut` preset 里写的"红灯=先说明再执行"以本库为准，preset 侧需同步改。

## 关联

- 库内规范：`00_系统/运营手册.md`、`00_系统/_schema.md`、`00_系统/归档操作规范.md`
- 归档细分：`.agents/skills/vault-archiving/SKILL.md`
```

**同时做**：`~/.agents/skills/24frames-vault/` 改名加 `.bak-20261006` 后缀，观察两周再删。

---

## B5 · `00_系统/agent/vault-search.py`（P1-4）

> **本脚本已实测跑通**：索引 214 个文件（`00_系统`–`04_灵感` + `06_AI`，跳过公众号存档与 attachments），检索"苏宁"返回 5 个文件并带命中片段，检索"票价"返回 3 个。
> 中文用 SQLite FTS5 的 **trigram** 分词器（本机 SQLite 3.51.0 支持），不需要额外装分词器，也不需要 qmd。

**落盘到**：`00_系统/agent/vault-search.py`；`.gitignore` 追加一行 `00_系统/agent/vault-index.db`

````python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""24帧运营库 · 全文检索（FTS5 trigram，中文友好）

用法：
  python3 00_系统/agent/vault-search.py "苏宁"            # 检索
  python3 00_系统/agent/vault-search.py "票价" -n 20      # 最多 20 条
  python3 00_系统/agent/vault-search.py --rebuild         # 重建索引
  python3 00_系统/agent/vault-search.py --rebuild --all   # 连公众号存档一起索引

设计：
  - 默认索引 00_系统 / 01_方向 / 02_项目 / 03_人物 / 04_灵感 / 06_AI
  - trigram 分词，中文无需额外分词器
  - 每条命中返回：文件路径 + 命中次数 + 上下文片段
"""
import os, re, sqlite3, sys, argparse
from pathlib import Path

VAULT = Path(os.environ.get("VAULT_DIR") or Path(__file__).resolve().parents[2])
DB = VAULT / "00_系统/agent/vault-index.db"
DEFAULT_DIRS = ["00_系统", "01_方向", "02_项目", "03_人物", "04_灵感", "06_AI"]
ARCHIVE_DIR = "05_档案/公众号存档"
SKIP = {".git", "node_modules", "attachments", "images", ".obsidian", "_archive"}


def collect(dirs):
    for d in dirs:
        root = VAULT / d
        if not root.is_dir():
            continue
        for p in root.rglob("*.md"):
            rel = p.relative_to(VAULT)
            if any(part in SKIP for part in rel.parts):
                continue
            yield p, str(rel)


def rebuild(dirs):
    DB.unlink(missing_ok=True)
    con = sqlite3.connect(DB)
    con.execute("CREATE VIRTUAL TABLE doc USING fts5(path UNINDEXED, body, tokenize='trigram')")
    n = 0
    for p, rel in collect(dirs):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        con.execute("INSERT INTO doc (path, body) VALUES (?, ?)", (rel, text))
        n += 1
    con.commit(); con.close()
    return n


def search(query, limit):
    if not DB.exists():
        print("索引不存在，先跑一次 --rebuild", file=sys.stderr)
        return 1
    con = sqlite3.connect(DB)
    if len(query) < 3:                      # trigram 需要 >=3 字符，短词退化为 LIKE
        rows = con.execute("SELECT path, body FROM doc WHERE body LIKE ? LIMIT ?",
                           (f"%{query}%", limit)).fetchall()
        hits = [(p, b.count(query), b) for p, b in rows]
    else:
        rows = con.execute(
            "SELECT path, body FROM doc WHERE doc MATCH ? ORDER BY bm25(doc) LIMIT ?",
            (f'"{query}"', limit)).fetchall()
        hits = [(p, b.count(query), b) for p, b in rows]
    if not hits:
        print(f"无命中：{query}")
        return 0
    print(f"命中 {len(hits)} 个文件（关键词：{query}）\n")
    for path, cnt, body in hits:
        i = body.find(query)
        seg = re.sub(r"\s+", " ", body[max(0, i - 30): i + 60]).strip()
        print(f"  {cnt:>3}×  {path}")
        print(f"        … {seg} …")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="?")
    ap.add_argument("-n", "--limit", type=int, default=15)
    ap.add_argument("--rebuild", action="store_true")
    ap.add_argument("--all", action="store_true", help="连公众号存档一起索引")
    a = ap.parse_args()
    dirs = DEFAULT_DIRS + ([ARCHIVE_DIR] if a.all else [])
    if a.rebuild:
        print(f"索引重建完成：{rebuild(dirs)} 个文件 → {DB.relative_to(VAULT)}")
        sys.exit(0)
    sys.exit(search(a.query or "", a.limit))
````

**实测输出样本**：

```
$ python3 00_系统/agent/vault-search.py --rebuild
索引重建完成：214 个文件 → 00_系统/agent/vault-index.db

$ python3 00_系统/agent/vault-search.py "苏宁" -n 3
命中 3 个文件（关键词：苏宁）
    9×  00_系统/_changelog.md
        … ## [2026-06-11 12:35] 归档 | 苏宁影城路演合作 - 新建项目：`02_项目/苏宁影城路演合作/` …
   10×  02_项目/苏宁影城路演合作/自我审计清单.md
        … # 苏宁影城路演合作 - 自我审计清单 **审计时间**：2026-06-11 …
    5×  02_项目/苏宁影城路演合作/苏宁影城路演合作.md
        … type: project name: 苏宁影城路演合作 status: exploring …
```

**维护**：把 `vault-index.db` 加进 `.gitignore`（生成物不进 git），在 `vault-lint.sh` 里加一行 `--rebuild`。

---

## B6 · 模板集

> 建新文件时直接抄，避免每次重新决定结构。

### B6-1 项目页

```markdown
---
type: project
name: <项目名>
direction: "[[观影团]]"   # ← 改成实际方向：观影团/策展人/影视创作/宣发平台/AI影像
goal: <一句话目标>
progress: 进行中
status: draft
editable: true
priority: medium
related_people: ["[[人物名]]"]   # ← 改成真实人物页名
created: YYYY-MM-DD
updated: YYYY-MM-DD
audience: both
---

# <项目名>

## 一句话定位
<说人话，一句话>

## 关键参数

| 项 | 内容 | 状态 |
|---|---|---|

## 排期

## 待办
- [ ] <事项> — @<执行人> — 截止 YYYY-MM-DD

## 决策记录

## 风险

## 关联
- 方向：[[观影团]] ｜ 人物：[[人物名]]
- 会议：[[会议文件名]]
```

### B6-2 人物页

```markdown
---
type: person
name: <人名>
aka: <别名>
relation: <怎么认识的 / 什么关系>
category: external
status: final
editable: true
audience: both
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# <人名>

## 身份

## 关系

## 行为记录
| 日期 | 事 | 出处 |
|---|---|---|

## 画像速写
<3–5 句，写人话，不写形容词堆砌>

## 待观察

## 关联
```

### B6-3 灵感页

```markdown
---
type: inspiration
stage: 新捕获
direction: 待定
captured: YYYY-MM-DD
source: "[[来源文件名]]"
status: draft
editable: true
audience: both
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# <灵感名>

## 原始想法
<原话，不加工>

## AI 视角可行性
成本 / 资源 / 时间 / 风险 各一行

## 潜在关联

## 升格建议
<要不要转项目，理由>
```

---

## 附：所有落盘文件一览（照这个清单建，不会漏）

| # | 路径 | 来自 |
|---|---|---|
| 1 | `00_系统/_schema.md` | B1 |
| 2 | `02_项目/AGENTS.md` | B2-1 |
| 3 | `06_AI/AGENTS.md` | B2-2 |
| 4 | `05_档案/会议存档/AGENTS.md` | B2-3 |
| 5 | 根 `AGENTS.md` 加「2.5 局部规则」节 | B2-0 |
| 6 | `.agents/skills/24frames-vault/SKILL.md` | B4 |
| 7 | `.agents/skills/vault-archiving/SKILL.md` | 附件A §A4-3 |
| 8 | `00_系统/agent/vault-lint.sh` | B3-2 |
| 9 | `00_系统/agent/vault-search.py` | B5 |
| 10 | `00_系统/agent/verify-p0.sh` | 附件A §A10 |
| 11 | `~/.dsh/profiles/headless/cordis.patch.yml`（库外） | B3-1 |
| 12 | `~/Library/LaunchAgents/com.24frames.vault-lint.plist`（库外） | B3-3 |
| 13 | `.base/项目看板.base`、`.base/待拍板.base` | 附件A §A6-4 |
| 14 | `.gitignore` 追加 `00_系统/agent/vault-index.db`、`.hermes/` | B3/B5 |

## 关联

- [[24帧运营库-DSH优化方案]]
- [[附件A-规范修订对照表]]
- [[运营手册]] ｜ [[_index]] ｜ [[经验沉淀]]
