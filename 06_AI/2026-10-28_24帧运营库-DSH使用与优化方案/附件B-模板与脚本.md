---
type: draft
name: 附件B-模板与脚本
status: review
editable: true
audience: both
created: 2026-10-28
updated: 2026-10-28
summary: 可直接复制的 AGENTS、schema、手册、skill、嵌套规则、页面模板与自动化配置
source: ai-generated
tags: [模板, 可抄, DSH]
---

# 附件B · 模板与脚本

> 配套 [[24帧运营库-DSH使用与优化方案-v2]]、[[附件A-现状复核与执行队列]]、[[附件C-脚本源码]]。
> B1–B5、B9、B12–B14 是可复制的文本；B6–B8、B10、B11、B15 的完整源码在 [[附件C-脚本源码]]，对应关系：

| 编号 | 内容 | 附件C 小节 | 任务卡 |
|---|---|---|---|
| B6 | `vault-index.py` | C1 | P1-1 |
| B7 | `vault-home.py` | C2 | P1-2 |
| B8 | `vault-lint.py` | C3 | P1-3 |
| B10 | `vault-search.py` | C4 | P2-1 |
| B11 | `hooks.json` + 两个 shell 钩子 | C5 | P2-3 |
| B15 | `vault-metrics.py` | C6 | P2-8 |

> 复制后先把占位路径改成实际路径，再跑对应任务卡的 `Verify`。

---

## B1 · 根 `AGENTS.md`

**落盘**：`24帧运营库/AGENTS.md`
**上限**：150 行、8 KB。超了就删细节，移到嵌套 AGENTS 或 `_schema.md`。

````markdown
# 24帧运营库 · Agent 入口

> 24FRAMES 的业务库。人类用 Obsidian 读，agent 用文件工具读写。
> 分工：本文件管边界与红线；`00_系统/_schema.md` 管字段；`00_系统/运营手册.md` 管流程；`00_系统/归档操作规范.md` 管归档。

## 1. 开工前读什么

| 你要做的事 | 必读 | 不必读 |
|---|---|---|
| 任何写操作 | 本文件 + `00_系统/_schema.md` | 全库 |
| 归档会议/录音 | 本文件 + `00_系统/归档操作规范.md` | 历史会议 |
| 写项目页 | 本文件 + `02_项目/AGENTS.md` | 其他项目 |
| 写人物页 | 本文件 + `03_人物/AGENTS.md` | 其他人物 |
| 找资料 | `00_系统/_index.md` → `vault-search.py` | 逐篇 grep |
| 今日待办 | `HOME.md` | 全库 |

一次最多读三份规则。读到旧路径或旧字段，以本文件与 `_schema.md` 为准。

## 2. 四层

| 层 | 路径 | 谁写 | 规则 |
|---|---|---|---|
| raw | `05_档案/` | 人 / 归档流程 | 只读；只能按归档规范新建会议 |
| wiki | `01_方向` `02_项目` `03_人物` `04_灵感` `HOME.md` | agent | 有 schema，写前必读 |
| draft | `06_AI/YYYY-MM-DD_主题/` | agent | 草稿，不进 wiki |
| schema | 根 AGENTS、`_schema.md`、运营手册、归档规范 | 人批准 | 改一条记 changelog |

`05_档案/公众号存档/` 是已发布记录，永远不改。

## 3. 硬规则

1. 先读后写。没读目标文件就改，等于破坏。
2. 会议、通话、访谈只进 `05_档案/会议存档/`，命名 `YYYY-MM-DD_主题.md`。项目目录不放会议。
3. AI 草稿、半成品、研究只进 `06_AI/YYYY-MM-DD_主题/`，不散落根目录。
4. 每次写操作记 `00_系统/_changelog.md`：
   `## [YYYY-MM-DD HH:mm] 操作类型 | 文件名`
5. `05_档案/` 只读。唯一例外：按归档规范新建会议文件。
6. `audience: public` 只表示「已批准对外」，必须同时有 `public_approved` 和 `redacted: true`。
7. 人物页、会议页默认 `audience: owner`。改 public 必须宇航员同意。
8. 不编造。缺信息写「待补充」，不猜金额、日期、人名、关系。
9. 每个 wiki 页必须有 `## 关联`，至少链到方向、项目、人物各一个（不适用时写原因）。
10. 不新建 `03_任务/`。任务写在项目页 `## 待办`，格式见 `_schema.md`。
11. 不装 Dataview。看板用 `HOME.md` 静态表或 Bases。
12. 不 commit、不 push。需要提交时先问宇航员。
13. 单次改动超过 20 个文件，先出计划，等批准。
14. 发现两份规范冲突，停下来报告，不自行选一个。

## 4. 写什么，放哪里

| 内容 | 路径 | type |
|---|---|---|
| 会议 / 通话 / 访谈 | `05_档案/会议存档/` | `meeting` |
| 项目概况 + 待办 | `02_项目/<项目名>/<项目名>.md` | `project` |
| 人物档案 | `03_人物/<姓名>.md` | `person` |
| 业务方向 | `01_方向/<方向>/<方向>.md` | `direction` |
| 灵感 | `04_灵感/AI加工区/` | `inspiration` |
| 可复用方法 / 研究 | `04_灵感/知识库/` 或项目 `01_参考文档/` | `reference` |
| AI 草稿 | `06_AI/YYYY-MM-DD_主题/` | `draft` |
| 成稿待发 / 已发 | `06_AI/...` / `05_档案/公众号存档/` | `output` |
| 对外媒体材料 | `05_档案/媒体/` | `media` |

## 5. 任务语法

项目页 frontmatter：

```yaml
next_action: 跟苏宁确认 11 月排期
next_action_due: 2026-11-02
waiting_for: 苏宁影城回复排期
```

正文：

```markdown
## 待办

- [ ] T-03 跟苏宁确认 11 月排期 ｜ 宇航员 ｜ 2026-11-02 ｜ 进行中
- [x] T-02 拿到场地报价 ｜ 宇航员 ｜ 2026-10-20 ｜ 已完成
```

格式：`- [状态] 任务ID 动作 ｜ 负责人 ｜ 截止日 ｜ 状态`。
一个项目最多 7 条未完成；完成项每周清理。

## 6. 完成前自检

- [ ] frontmatter 能通过 `python3 00_系统/agent/vault-lint.py --file <文件>`
- [ ] 新页面有 `summary` 和 `## 关联`
- [ ] 会议/项目/人物页已互相链接
- [ ] 没有内部金额、关系判断、联系方式进入 `public` 页
- [ ] `_changelog.md` 已记
- [ ] `updated` 已改

## 7. 先问再做

1. 涉及钱、报价、分账、赞助。
2. 对外发布或发给合作方。
3. 删除文件、清空目录、改写历史存档。
4. 新建人物页或项目页（可以先提议）。
5. 修改 `_schema.md`、本文件、运营手册、归档规范。
6. `git push`、改 remote、改仓库可见性。
7. 批量修改超过 20 个文件。
8. 安装插件或改 DSH profile。

## 8. 目录级规则

进入以下目录时，DSH 会自动追加该目录的 `AGENTS.md`，以它为准：

- `00_系统/AGENTS.md`
- `02_项目/AGENTS.md`
- `03_人物/AGENTS.md`
- `05_档案/AGENTS.md`
- `06_AI/AGENTS.md`

## 9. 工具

```bash
cd "$HOME/Documents/24帧运营库"
python3 00_系统/agent/vault-lint.py --file <文件>
python3 00_系统/agent/vault-index.py
python3 00_系统/agent/vault-home.py
python3 00_系统/agent/vault-search.py "关键词"
```

## 10. 报告格式

`TASK / CHANGED / VERIFY / RISK / NEXT`。没有 `VERIFY` 原文的交付视为未完成。
````

---

## B2 · `_schema.md`

**落盘**：`24帧运营库/00_系统/_schema.md`
**作用**：字段唯一事实源。其他文件只链接，不复述。

````markdown
---
type: reference
name: _schema
status: final
editable: true
audience: both
created: 2026-10-28
updated: 2026-10-28
summary: 全库 frontmatter、命名、任务语法的唯一合法值
---

# 24帧运营库 · Schema

> 全库 frontmatter 取值以本文件为准。
> `AGENTS.md`、`运营手册.md`、`归档操作规范.md`、skills 只引用本文件，不再各写一份枚举。
> 新增取值 = 改本文件 + 记 changelog。lint 读本文件的表。

## 1. 通用字段

| 字段 | 必填 | 取值 | 说明 |
|---|---|---|---|
| `type` | 是 | 见 §2 | 文件类型 |
| `name` | 是 | 文本 | 通常等于文件名（不含 .md） |
| `status` | 是 | `draft` / `review` / `final` / `archive` | 文档生命周期 |
| `audience` | 是 | `owner` / `agent` / `both` / `public` | 读者范围 |
| `editable` | 是 | `true` / `false` | agent 能否改 |
| `created` | 是 | `YYYY-MM-DD` | 创建日 |
| `updated` | 是 | `YYYY-MM-DD` | 最后实质修改日 |
| `summary` | wiki 页必填 | ≤40 字 | 供索引与首页使用 |
| `source` | 否 | `human` / `ai-generated` / `external` | 来源 |
| `tags` | 否 | 列表 | 主题标签 |

### status 四值

| 值 | 含义 | 谁推进 |
|---|---|---|
| `draft` | 未定稿，可改 | agent |
| `review` | 等宇航员拍板；必须有 `review_due` | 宇航员 |
| `final` | 定稿，只做维护 | 宇航员 |
| `archive` | 归档只读 | 无人 |

### audience 四值

| 值 | 含义 | 默认用于 |
|---|---|---|
| `owner` | 只给宇航员 | 人物、会议、资金/关系内容 |
| `agent` | agent 工作记忆 | `00_系统/agent/`、草稿 |
| `both` | 宇航员与 agent | 项目、方向、大多数 wiki 页 |
| `public` | **已批准对外** | 对外计划书、媒体介绍 |

`audience: public` 必须同时有：

```yaml
public_approved: 2026-10-28
redacted: true
```

人物页、会议页默认 `owner`。改成 `public` 需要宇航员明确同意并记 changelog。

## 2. type 取值

| type | 用在哪 | 必填专属字段 | 落盘位置 |
|---|---|---|---|
| `meeting` | 会议 / 通话 / 访谈 / 录音 | `date`, `participants`, `direction` | `05_档案/会议存档/` |
| `person` | 人物档案 | `category`, `role` | `03_人物/` |
| `project` | 项目概况 | `direction`, `progress`, `priority`, `next_action` | `02_项目/<项目名>/<项目名>.md` |
| `direction` | 业务方向 | `direction` | `01_方向/<方向>/<方向>.md` |
| `inspiration` | 灵感 | `stage`, `captured` | `04_灵感/` |
| `reference` | 可复用方法 / 研究 / 规范 | — | `00_系统/`、`04_灵感/知识库/`、项目 `01_参考文档/` |
| `draft` | AI 草稿 / 半成品 | — | `06_AI/YYYY-MM-DD_主题/` |
| `output` | 成稿待发 / 已发布 | — | `06_AI/` 或 `05_档案/公众号存档/` |
| `media` | 对外媒体材料 | — | `05_档案/媒体/` |
| `task` | **历史遗留，不新建** | — | 任意（lint 警告） |

### 历史值映射

| 旧值 | 归到 |
|---|---|
| `项目会议`、`非正式饭局谈话` | `meeting` |
| `direction-reference`、`brand-resource`、`project_plan`、`concept`、`external-submission`、`research` | `reference`（在 `06_AI/` 内则 `draft`） |
| `ai-draft` | `draft` |
| `影评`、`公众号文章`、`游戏推荐`、`评分`、`analysis`、`guide`、`report` | 已发布 `output`，未发布 `draft` |
| `task` | 并入项目页 `## 待办` |

旧文件不批量改，动到哪篇改哪篇。

## 3. 枚举字段

| 字段 | 用在哪 | 合法值 |
|---|---|---|
| `progress` | `project` | `待办` / `进行中` / `等待中` / `已完成` / `已取消` / `已终止` |
| `stage` | `inspiration` | `新捕获` / `已加工` / `预启动` / `已转项目` / `已归档` |
| `priority` | `project` | `high` / `medium` / `low` |
| `category` | `person` | `internal` / `external` |
| `direction` | 多处 | `观影团` / `策展人` / `影视创作` / `宣发平台` / `AI影像` |

`direction` 写纯文本，不加 `[[ ]]`；一个文件一个主方向，次要方向放 `secondary_directions` 列表。

`status` 与 `progress` 是两个维度：`status` 管文档，`progress` 管事情。不要写 `status: active` 或 `status: 进行中`。

## 4. 关系字段

| 字段 | 形式 | 用途 |
|---|---|---|
| `related_projects` | 列表，写笔记名，不带方括号 | 反向索引 |
| `related_people` | 列表，写笔记名 | 反向索引 |
| `secondary_directions` | 列表 | 多方向项目 |
| `supersedes` | 笔记名 | 取代旧页 |
| `review_due` | `YYYY-MM-DD` | review 截止日 |
| `public_approved` | `YYYY-MM-DD` | 对外批准日 |
| `redacted` | `true` / `false` | 是否已脱敏 |

正文的 `## 关联` 用 `[[双链]]`，供人导航；frontmatter 的关系字段用纯文本，供脚本查询。两者不混。

## 5. 命名

- 项目：`02_项目/<项目名>/<项目名>.md`，文件夹与主文件同名。
- 人物：`03_人物/<姓名>.md`；重名用 `<姓名>-<机构>.md`。
- 方向：`01_方向/<方向>/<方向>.md`。
- 会议：`YYYY-MM-DD_主题.md`，主题不超过 20 字。
- `06_AI`：`YYYY-MM-DD_主题/`，主文件放目录内，图片放 `attachments/`。
- 不用空格、斜杠、冒号；用中文短横或下划线。

## 6. 任务语法

项目页 frontmatter：

```yaml
next_action: 跟苏宁确认 11 月排期
next_action_due: 2026-11-02
waiting_for: 苏宁影城回复排期
```

正文：

```markdown
## 待办

- [ ] T-03 跟苏宁确认 11 月排期 ｜ 宇航员 ｜ 2026-11-02 ｜ 进行中
- [ ] T-04 补一份分账测算表 ｜ 宇航员 ｜ 2026-11-05 ｜ 待办
- [x] T-02 拿到场地报价 ｜ 宇航员 ｜ 2026-10-20 ｜ 已完成
```

校验正则：

```text
^- \[( |x)\] T-\d{2,} .+ ｜ .+ ｜ \d{4}-\d{2}-\d{2} ｜ (待办|进行中|等待中|已完成|已取消)$
```

规则：

- 任务 ID 项目内唯一，从 `T-01` 起。
- 一个项目最多 7 条未完成。
- `next_action` 与第一条未完成一致。
- 会议里的待办落到项目页，会议页只放链接。

## 7. 归档与索引

- 会议归档流程见 `00_系统/归档操作规范.md`，本文件不重复。
- `_index.md`、`HOME.md` 由 `00_系统/agent/vault-index.py`、`vault-home.py` 生成，agent 不手写。
- `_changelog.md` 只追加，格式 `## [YYYY-MM-DD HH:mm] 操作类型 | 文件名`。

## 8. 修改流程

1. 改本文件。
2. 记 changelog。
3. 跑 `python3 00_系统/agent/vault-lint.py --write-baseline`（如果新增合法值）。
4. 通知所有 agent：规则版本变了。

## 关联

- [[运营手册]]
- [[归档操作规范]]
- [[_index]]
````

---

## B3 · `运营手册.md` 骨架

**落盘**：`00_系统/运营手册.md`（替换现有 102 行版本）
**原则**：手册管流程，不写枚举；枚举一律指向 `_schema.md`。

````markdown
---
type: reference
name: 运营手册
status: final
editable: true
audience: both
created: 2026-06-07
updated: 2026-10-28
summary: 24帧运营库的目录、流程、决策与协作规则
---

# 24帧运营库 · 运营手册

> 字段取值以 [[_schema]] 为准；归档步骤以 [[归档操作规范]] 为准。本文件只管流程与分工。

## 0. 怎么用

三个入口：

- 人：看 [[HOME]]。
- agent：先看根 `AGENTS.md`。
- 找页面：看 [[_index]]。

设计原则：少而清，宁删勿堆；一个事实只有一个家；能链接就不复述。

## 1. 目录与权限

| 目录 | 放什么 | agent 权限 |
|---|---|---|
| `00_系统/` | 规范、索引、日志、工具 | 可写生成物与日志；改规范需批准 |
| `01_方向/` | 5 个业务方向 | 可写，改结论需批准 |
| `02_项目/` | 项目、参考、归档、草稿 | 可写 |
| `03_人物/` | 人物档案 | 可写；默认 owner |
| `04_灵感/` | 捕获、加工、知识库、品牌策略 | 可写 |
| `05_档案/` | 会议、公众号、媒体、数据 | 只读；只能新建会议 |
| `06_AI/` | AI 草稿与任务产出 | 可写 |

## 2. 文件类型

10 个 `type`、4 个 `status`、4 个 `audience`，全部见 [[_schema]]。新建文件前必读。

## 3. 项目与任务

- 一个项目一个文件夹，主文件与文件夹同名。
- 任务写在主文件 `## 待办`，不建独立任务文件。
- `next_action` 永远指向下一步动作，不写「继续推进」这种空话。
- 项目页必备：一句话、当前状态、待办、决策记录、风险、关联。

## 4. 命名

见 [[_schema]] §5。会议用 `YYYY-MM-DD_主题.md`；`06_AI` 用 `YYYY-MM-DD_主题/`。

## 5. 归档

按 [[归档操作规范]] 六步走：转录存档、信息提炼、背景调研、可交付物、自我审计、通知到位。
归档完成的标准是「存好的东西可以直接用」，不是「文件存好了」。

## 6. 灵感

1. 新捕获 → `04_灵感/AI加工区/`，`stage: 新捕获`。
2. 加工：一句话本质、可行性、连接 → `stage: 已加工`。
3. 预启动：最小验证 → `stage: 预启动`。
4. 转项目需宇航员确认 → `stage: 已转项目`，移到 `04_灵感/归档/`。

## 7. 项目生命周期

`待办` → `进行中` → `等待中` / `已完成` / `已取消` / `已终止`。
停滞超过 14 天，HOME 自动标黄；超过 30 天，审计员要求写「继续/暂停/终止」。

## 8. Lint 与健康检查

```bash
python3 00_系统/agent/vault-lint.py
python3 00_系统/agent/vault-index.py
python3 00_系统/agent/vault-home.py
```

lint 错误必须当天修；警告每周清一次。禁止用 `| tail` 看结果，退出码会被吞。

## 9. 周检与月检

- 周日：跑 lint，更新 HOME，清 review 队列，写健康快照。
- 每月 1 日：隐私扫描，检查 public 页，复核停滞项目。
- 每季：归档过期内容，分卷 changelog，提炼 3 条经验。

## 10. 子目录

项目内按需建 `01_参考文档/`、`02_归档文件/`、`03_AI文档/`、`04_草稿/`，不建空壳。
`06_AI` 每个任务一个日期目录，图片放 `attachments/`。

## 11. 决策灯

- 红灯，先问：钱、发布、删除、新建人物/项目、改规范、push、批量改 >20 文件。
- 黄灯，做完记日志：普通编辑、归档、灵感加工、lint 修复。
- 绿灯，直接做：查询、生成索引、格式修复、只读分析。

拿不准按高一级处理。

## 12. 协作

- 单写者：同一时间只有一个 agent 写库。
- 并行只用于读：多个子代理查资料，主 agent 落盘。
- 交接格式：`TASK / CHANGED / VERIFY / RISK / NEXT`。
- 角色：图书管理员、归档员、写作者、研究员、审计员、宇航员。

## 13. 复利

每份报告提炼三问：

1. 这是哪类问题？一句话。
2. 怎么防它再犯？一个 action。
3. 出现过几次？≥3 次升级成硬规则。

去向：一次性事实进 changelog；可复用经验进 `00_系统/agent/经验沉淀.md`；反复出现升级进本手册或 lint。

## 14. 迁移与遗留

旧字段、旧路径按「动到才改」处理，不批量重写。
`03_任务/`、`06_灵感库/`、`07_档案/` 已废弃，出现即 lint 报错。

## 15. 入库检查清单

- [ ] `type/status/audience/editable/created/updated/summary` 齐全
- [ ] `direction` 是 5 个之一，纯文本
- [ ] 文件在正确目录
- [ ] 有 `## 关联`，至少 2 条双链
- [ ] 没有断链
- [ ] public 页有 `public_approved` 和 `redacted`
- [ ] `_changelog.md` 已记
- [ ] lint `--file` 通过

## 关联

- [[_schema]]
- [[归档操作规范]]
- [[HOME]]
- [[_index]]
````

---

## B4 · 两个路由 Skill

### B4-1 `24frames-vault/SKILL.md`

**落盘**：`.agents/skills/24frames-vault/SKILL.md`
**上限**：150 行。

````markdown
---
name: 24frames-vault
description: 24FRAMES 运营库的读写路由。用于查项目/人物/会议、写项目页、处理灵感、维护索引与健康检查时。进入库内任务先读本 skill。
updated: 2026-10-28
---

# 24帧运营库 · 路由

## 何时用

任何对 `~/Documents/24帧运营库` 的读、写、查、维护。纯外部写作（不涉及库）不用。

## 先读三份，按需

1. 库根 `AGENTS.md`：边界与红线。
2. `00_系统/_schema.md`：要写文件时必读。
3. 对应目录的 `AGENTS.md`：`02_项目` / `03_人物` / `05_档案` / `06_AI` / `00_系统`。

一次最多三份。不要通读全库。

## 路由

| 任务 | 读 | 写 |
|---|---|---|
| 今日待办 | `HOME.md` | — |
| 找项目/人物 | `_index.md` → `vault-search.py` | — |
| 写项目页 | 项目页 + `02_项目/AGENTS.md` | `02_项目/<项目>/<项目>.md` |
| 归档会议 | `归档操作规范.md` + 相关项目/人物页 | `05_档案/会议存档/` 新建 + 项目/人物更新 |
| 处理灵感 | `04_灵感/README.md` + `_schema.md` | `04_灵感/AI加工区/` |
| 写公众号 | `references/writing.md` + 项目页 + `01_参考文档` | `06_AI/YYYY-MM-DD_主题/` |
| 维护 | `AGENTS.md` + lint 输出 | `00_系统/` 生成物 |

## 硬规则

1. `05_档案/` 只读；只能按归档规范新建会议。
2. `06_AI/` 每个任务一个 `YYYY-MM-DD_主题/`，不散落。
3. 每次写操作记 `_changelog.md`，格式 `## [YYYY-MM-DD HH:mm] 类型 | 文件`。
4. `public` 只给已批准对外的页面；人物/会议默认 `owner`。
5. 不编造；缺失写「待补充」。
6. 不 commit、不 push。
7. 改动超过 20 个文件先出计划。

## 工具

```bash
cd "$HOME/Documents/24帧运营库"
python3 00_系统/agent/vault-search.py "关键词" --limit 10
python3 00_系统/agent/vault-lint.py --file <文件>
python3 00_系统/agent/vault-index.py
python3 00_系统/agent/vault-home.py
```

## 写作与参考

- 写作风格：`references/writing.md`
- 常用命令：`references/commands.md`
- 字段细节：`00_系统/_schema.md`
- 归档细节：`00_系统/归档操作规范.md`

## 不要

- 不要装 Dataview，不要新建 `03_任务/`。
- 不要把 skill 当规范；规范在 `_schema.md` 和手册里。
- 不要把会议内容写进项目页正文，链接到会议页。
- 不要在 `05_档案/公众号存档/` 改字。
````

### B4-2 `vault-archiving/SKILL.md`

**落盘**：`.agents/skills/vault-archiving/SKILL.md`
**上限**：120 行。

````markdown
---
name: vault-archiving
description: 把录音、通话、会议转写归档进 24FRAMES 运营库。触发词：归档、存档、录音、会议记录、通话记录、转写、会议纪要。
updated: 2026-10-28
---

# 会议 / 录音归档

## 先读

1. `00_系统/归档操作规范.md`（唯一流程）
2. `00_系统/_schema.md`（字段）
3. 相关项目页、人物页

## 六步

1. **转录存档**：清洗错标说话人，统一「说话人 + 时间戳 + 内容」，新建 `05_档案/会议存档/YYYY-MM-DD_主题.md`。
2. **信息提炼**：更新相关项目页 `## 决策记录` / `## 待办`，更新人物页 `## 行为记录`；新人物先提议，不直接建。
3. **背景调研**：涉及的电影/品牌/人物查公开资料，写进项目 `01_参考文档/`。
4. **可交付物**：群聊对齐信息、协议、执行方案，达到「确认后可直接用」。
5. **自我审计**：逐项勾 §15 清单；缺一项不算完成。
6. **通知**：在频道说明归档了什么、建了哪些文件、交付物在哪。

## 字段

```yaml
type: meeting
name: 2026-10-28_主题
status: final
audience: owner
editable: false
created: 2026-10-28
updated: 2026-10-28
summary: 一句话
date: 2026-10-28
participants: [宇航员, Peter]
direction: 影视创作
related_projects: [何力长片-浮生若丽]
related_people: [Peter]
source: human
```

## 完成标准

- [ ] 会议页在 `05_档案/会议存档/`，命名正确
- [ ] 项目页/人物页已更新，且有双链
- [ ] 待办落到项目页，格式正确
- [ ] 背景资料已写入 `01_参考文档/`
- [ ] 可交付物可直接用
- [ ] `vault-lint.py --file` 通过
- [ ] changelog 已记

## 停

- 涉及未公开的资金、合同、个人隐私，`audience: owner`，不要写 public。
- 需要新建人物/项目，先问宇航员。
- 原始文件大于 10 MB，放库外，库内留路径。
````

---

## B5 · Skill 参考文件

**落盘**：`.agents/skills/24frames-vault/references/writing.md`、`commands.md`

### B5-1 `writing.md`

````markdown
# 24FRAMES 写作要点

## 语气

- 短句，有态度，敢下判断。不要四平八稳。
- 像一个真实的人在看电影、做事、和人打交道。
- 不写「首先/其次/最后」，不写「综上所述」，不写「值得注意的是」。
- 不堆形容词，不写空泛的赞美。

## 结构

- 开头给一个具体的场景、动作或冲突。
- 中段用事实和细节推进，不用概念撑篇幅。
- 结尾落在感受或判断，不做总结陈词。

## 禁止

- 否定递进：「不是 A，而是 B」。
- 三段式排比。
- 空洞的行业黑话。
- 没有来源的数字。
- 把争议升华成道理。

## 发布前

- 隐私检查：真实姓名、电话、微信、金额、合同条款。
- 事实检查：片名、人名、时间、地点。
- 过 `ai-reviewer-yuhong` 或人工复核。
````

### B5-2 `commands.md`

````markdown
# 常用命令

```bash
cd "$HOME/Documents/24帧运营库"

# 健康检查
python3 00_系统/agent/vault-lint.py
python3 00_系统/agent/vault-lint.py --file "02_项目/苏宁影城路演合作/苏宁影城路演合作.md"

# 重建索引与首页
python3 00_系统/agent/vault-index.py
python3 00_系统/agent/vault-home.py

# 检索
python3 00_系统/agent/vault-search.py "资金 分工" --limit 10
python3 00_系统/agent/vault-search.py --rebuild

# 最近日志
grep '^## \[' 00_系统/_changelog.md | tail -5
```
````

---

## B9 · 嵌套 `AGENTS.md`

### B9-1 `02_项目/AGENTS.md`

````markdown
# 项目目录规则

- 一个项目一个文件夹，主文件与文件夹同名。
- 主文件必备段落：一句话、当前状态、`## 待办`、`## 决策记录`、`## 风险`、`## 关联`。
- 任务格式见 `_schema.md` §6；最多 7 条未完成。
- 子目录只用 `01_参考文档/`、`02_归档文件/`、`03_AI文档/`、`04_草稿/`，不建空壳。
- 会议不放在项目目录，链接到 `05_档案/会议存档/`。
- 改项目结论（预算、合作模式、时间线）先在 `## 决策记录` 写理由，再改正文。
````

### B9-2 `03_人物/AGENTS.md`

````markdown
# 人物目录规则

- 默认 `audience: owner`，`editable: true`。
- 必备段落：画像速写、行为记录、待观察、关键对话时间线、`## 关联`。
- 行为记录写事实与日期，不写性格判断；判断放「待观察」。
- 金额、家庭、健康、私下评价只写内部页，永不进 `public`。
- 新建人物先问宇航员；重名用 `姓名-机构.md`。
- 人物页至少链到一个项目或一次会议。
````

### B9-3 `05_档案/AGENTS.md`

````markdown
# 档案目录规则

- 本目录只读。唯一例外：按 `00_系统/归档操作规范.md` 在 `会议存档/` 新建文件。
- 不重命名、不移动、不改写已存在的文件。
- 会议命名 `YYYY-MM-DD_主题.md`；公众号按年份目录。
- 对外分享前必须脱敏：人名、金额、联系方式、合同条款。
- 大文件（>10 MB）放库外，库内只留路径。
- 发现错误，写一份勘误到 `06_AI/`，不改原文。
````

### B9-4 `06_AI/AGENTS.md`

````markdown
# AI 产出目录规则

- 每个任务一个 `YYYY-MM-DD_主题/`，不在根目录散落文件。
- 主文件放目录内，图片放 `attachments/`，原始素材放 `素材/`。
- 未校准：文件名不加后缀；宇航员校准后加 `_已校准`；发布后移到 `05_档案/公众号存档/`。
- `type` 用 `draft`；成稿待发用 `output`。
- 不把 `06_AI/` 的内容当事实；事实以项目页/人物页为准。
- 任务结束后在 changelog 记一条，写清产出与状态。
````

### B9-5 `00_系统/AGENTS.md`

````markdown
# 系统目录规则

- 本目录放规范、索引、日志、工具，不放 AI 草稿。
- `_schema.md` 是字段唯一源；`运营手册.md` 管流程；`归档操作规范.md` 管归档。
- 改规范前先问宇航员，改完记 changelog。
- `_index.md`、`HOME.md` 由脚本生成，不手写。
- `_changelog.md` 只追加，不改旧条目。
- `agent/` 放脚本与日志；`logs/`、`.cache/` 不进 git。
````

---

## B12 · 页面模板

### B12-1 项目页

````markdown
---
type: project
name: 项目名
status: final
audience: both
editable: true
created: 2026-10-28
updated: 2026-10-28
summary: 一句话说清做什么、和谁、到什么程度
direction: 观影团
progress: 进行中
priority: high
next_action: 下一步具体动作
next_action_due: 2026-11-02
waiting_for:
related_people: []
tags: [项目]
---

# 项目名

## 一句话

## 当前状态

## 待办

- [ ] T-01 下一步具体动作 ｜ 宇航员 ｜ 2026-11-02 ｜ 进行中

## 决策记录

| 日期 | 决策 | 理由 | 决策人 | 依据 |
|---|---|---|---|---|

## 风险

## 关联

- [[方向页]]
- [[相关人物]]
- [[相关会议]]
````

### B12-2 人物页

````markdown
---
type: person
name: 姓名
status: final
audience: owner
editable: true
created: 2026-10-28
updated: 2026-10-28
summary: 一句话说清身份与关系
category: external
role: 资方对接人
related_projects: []
tags: [人物]
---

# 姓名

## 画像速写

## 行为记录

- 2026-10-28：

## 待观察

## 关键对话时间线

| 日期 | 场合 | 要点 | 链接 |
|---|---|---|---|

## 关联

- [[项目]]
- [[会议]]
````

### B12-3 会议页

````markdown
---
type: meeting
name: 2026-10-28_主题
status: final
audience: owner
editable: false
created: 2026-10-28
updated: 2026-10-28
summary: 一句话说清这次谈了什么、结论是什么
date: 2026-10-28
participants: [宇航员]
direction: 影视创作
related_projects: []
related_people: []
source: human
tags: [会议]
---

# 2026-10-28 主题

## 摘要

## 关键信息

## 决策

## 待办

> 落到项目页 `## 待办`，这里只放链接。

## 原文

## 关联

- [[项目]]
- [[人物]]
````

### B12-4 灵感页

````markdown
---
type: inspiration
name: 灵感名
status: draft
audience: both
editable: true
created: 2026-10-28
updated: 2026-10-28
summary: 一句话
stage: 新捕获
captured: 2026-10-28
source: human
direction: 观影团
tags: [灵感]
---

# 灵感名

## 原始想法

## AI 加工

## 可行性

## 关联

- [[方向]]
- [[项目]]
````

### B12-5 方向页

````markdown
---
type: direction
name: 观影团
status: final
audience: both
editable: true
created: 2026-10-28
updated: 2026-10-28
summary: 一句话说清这个方向做什么
direction: 观影团
tags: [方向]
---

# 观影团

## 定义

## 当前项目

> 见 [[_index]] 与 [[HOME]]。

## 判断

## 关联

- [[项目]]
````

---

## B13 · Changelog 格式

**落盘**：`00_系统/_changelog.md` 头部说明。

````markdown
# 操作日志

> 只追加，不改旧条目。
> 格式：`## [YYYY-MM-DD HH:mm] 操作类型 | 文件名`
> 操作类型：归档 / 新建 / 更新 / 迁移 / 修复 / 方案 / 发布 / 删除 / 仓库
> 取最近 5 条：`grep '^## \[' 00_系统/_changelog.md | tail -5`
> 超过 500 KB 或 2,000 行时分卷到 `_changelog/YYYY.md`，主文件保留最近 100 条。

## [2026-10-28 01:14] 方案 | 24帧运营库-DSH使用与优化方案-v2
````

---

## B14 · 自动化配置

### B14-1 headless 模型路由

**落盘**：`~/.dsh/profiles/headless/cordis.patch.yml`
**做法**：从 `~/.dsh/profiles/desktop/cordis.patch.yml` 复制 `llm-pi-ai` 与 `agent-default-model` 两块，模型改成便宜的长上下文模型。最小示例：

```yaml
- id: llm-pi-ai
  name: "@deepseek-ai/dsh-llm-pi-ai"
  config:
    providers:
      yhy2049:
        displayName: yhy2049
        apiKeyEnv: YHY2049_API_KEY
        api: openai-completions
        baseURL: https://token.sensenova.cn/v1
        models:
          - id: sensenova-6.8-flash-lite
            name: sensenova-6.8-flash-lite
            contextWindow: 262144
- id: agent-default-model
  name: "@deepseek-ai/dsh-agent-default-model"
  config:
    provider: yhy2049
    model: sensenova-6.8-flash-lite
```

密钥环境变量：launchd 不继承 shell，wrapper 里 `source ~/.zshrc`，或用 `launchctl setenv YHY2049_API_KEY ...`。

### B14-2 `nightly.sh`

**落盘**：`00_系统/agent/nightly.sh`，`chmod +x`。

```bash
#!/bin/zsh
set -u
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
source "$HOME/.zshrc" >/dev/null 2>&1 || true

VAULT="$HOME/Documents/24帧运营库"
LOG_DIR="$VAULT/00_系统/agent/logs"
LOG="$LOG_DIR/nightly-$(date +%F).log"
mkdir -p "$LOG_DIR"

{
  echo "== $(date '+%F %T') =="
  python3 "$VAULT/00_系统/agent/vault-lint.py" --json
  python3 "$VAULT/00_系统/agent/vault-index.py"
  python3 "$VAULT/00_系统/agent/vault-home.py"
  python3 "$VAULT/00_系统/agent/vault-metrics.py" --markdown
} >> "$LOG" 2>&1
```

### B14-3 LaunchAgent

**落盘**：`~/Library/LaunchAgents/cc.frames24.vault-nightly.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>cc.frames24.vault-nightly</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/zsh</string>
    <string>/Users/haishangyinghuo/Documents/24帧运营库/00_系统/agent/nightly.sh</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key><integer>2</integer>
    <key>Minute</key><integer>0</integer>
  </dict>
  <key>RunAtLoad</key>
  <false/>
  <key>StandardOutPath</key>
  <string>/Users/haishangyinghuo/Documents/24帧运营库/00_系统/agent/logs/launchd.out.log</string>
  <key>StandardErrorPath</key>
  <string>/Users/haishangyinghuo/Documents/24帧运营库/00_系统/agent/logs/launchd.err.log</string>
</dict>
</plist>
```

安装：

```bash
launchctl load ~/Library/LaunchAgents/cc.frames24.vault-nightly.plist
launchctl list | grep frames24
```

---

## 关联

- [[24帧运营库-DSH使用与优化方案-v2]]
- [[附件A-现状复核与执行队列]]
- [[附件C-脚本源码]]
- [[_schema]]
