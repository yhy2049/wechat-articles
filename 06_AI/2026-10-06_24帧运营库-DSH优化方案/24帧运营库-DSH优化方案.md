---
type: reference
name: 24帧运营库-DSH优化方案
status: review
editable: true
audience: both
created: 2026-10-06
updated: 2026-10-06
source: ai-generated
tags: [基建, DSH, agent协作, 知识管理]
---

# 24帧运营库 · DSH 优化方案

> 2026-10-06 ｜ 基于对全库 865 个 md 文件、52 次 git 提交、DSH 运行时与 skills 目录的实测
> 配套：[[附件A-规范修订对照表]] ｜ [[附件B-Agent落地执行手册]]

---

## 0. 怎么读这份文档

| 你是谁 | 读哪几节 | 读完做什么 |
|---|---|---|
| 任何刚进库的 agent | §1 §3 §4 §6 | 按 §6.0 修正自己的行为，再干活 |
| 宇航员（拍板用） | §2 §7 §9 | 决定 P0/P1 范围，其他不用看 |
| 负责执行的 agent | §5 §6 §8 + 附件B | 照抄附件B 的内容建文件，按 §6 顺序做 |
| 只想知道要干嘛 | §2 表格 + §6 表格 | 两张表就是全部结论 |

**一句话结论**：这个库的**内容层**（素材成色、双链习惯、frontmatter 纪律、归档 SOP）已经强过绝大多数个人知识库；卡点在**接口层和维护层**——DSH 的 6 项原生能力一项没用上，库里有 4 处自相矛盾的规范靠"已知陷阱"绕了四个月，agent 每次进来都要先猜规则。

---

## 1. 实测体检：硬数据

### 1.1 体量

| 指标 | 数值 | 备注 |
|---|---|---|
| md 文件总数 | **865** | 排除 `.git`、`node_modules`（含 `05_档案/公众号存档/_skill/node_modules` 里的 28 个 md）|
| 总字节 | **5.53 MB** | ≈ 184 万汉字等效（中文 UTF-8 按 3 字节/字估）|
| 去掉公众号存档后 | **2.15 MB** ≈ 72 万汉字 | agent 日常真正需要掌握的内容 |
| `05_档案` 占比 | 642 / 865 = **74%** | 库的体量由历史存档决定 |
| git 提交数 | **52**（审计时） | 提交节奏健康：2026-09 有 25 次、2026-10 有 27 次 |
| 工作区体积 / `.git` | **208 MB / 85 MB**（审计时） | 其中 19 MB（node_modules）+ 8.9 MB（`.hermes`）可以在库外存放 |
| git 跟踪文件 | **1330**（审计时） | 本次方案落库后 1336 |

> 说明：本节数字为 2026-10-06 审计时快照。库每天都在长（审计当天 `_changelog.md` 就从 1184 行涨到 1229 行），要最新数字请重跑 §1.3 的健康检查。

### 1.2 目录分布

| 目录 | md 数 | 字符量 | 状态 |
|---|---|---|---|
| `00_系统` | 17 | 5.1 万 | 规范齐，但有陈旧内容 |
| `01_方向` | 11 | 2.3 万 | 5 个方向齐全 |
| `02_项目` | 61 | 17.0 万 | 质量最高的一层 |
| `03_人物` | 20 | 1.5 万 | schema 高度一致 |
| `04_灵感` | 44 | 6.4 万 | 知识库有 44 篇笔记 |
| `05_档案` | 642 | 125.6 万 | 会议存档 17 + 其他 29 + 公众号存档 596 |
| `06_AI` | 70 | 22.8 万 | 命名合规，内容类型混杂 |

### 1.3 健康检查现状（`vault-health-check.py` 实跑结果）

| 级别 | 项目 | 数量 |
|---|---|---|
| 🔴 错误 | 断裂双链 | 6 |
| 🟡 警告 | 缺 frontmatter | 1（`06_AI/2026-09-20_DSH-AI宇航员思路讨论/思路讨论.md`） |
| 🟡 警告 | `status: review` 堆积 ≥7 天 | 4（品牌策略 3 篇 + 何力面谈，均已 114 天） |
| 🔵 信息 | `.DS_Store` 残留 | 5 |

---

## 2. 体检结论：16 个问题，按"谁被卡住"分四类

> 每条都带证据。修复方案见 §6，逐文件改法见 [[附件A-规范修订对照表]]。

### A 类 · 让 agent 读不懂（接口层，5 条）

| # | 问题 | 证据 |
|---|---|---|
| **A1** | **`HOME.md` / `_index.md` 的查询是死的**。库里**没装 Dataview**，7 个 ```dataview 代码块在 Obsidian 里就是 7 段代码 | `.obsidian/` 只有 4 个文件，无 `plugins/`、无 `community-plugins.json`；`HOME.md` 4 个块，`_index.md` 3 个块 |
| **A2** | **`24frames-vault` skill 与库内规范脱节**：1052 行、21 个文件、168 KB，写的是旧世界 | 路径写 `~/Documents/OH-WorkSpace/24帧运营库`（**不存在**）、说"6 个业务方向"（实际 5）、提 `03_任务`（已废止）、提 `06_灵感库/归档/`（实际 `04_灵感/归档/`） |
| **A3** | **入场入口太薄**：`AGENTS.md` 只有 2.7 KB / 8 条硬规则，真正的规则分散在 6 个文件里，没有"什么时候读哪个"的路由 | `AGENTS.md` 2,695 字节；规范实际分布在 `运营手册.md`、`_index.md`、`归档操作规范.md`、`04_灵感/README.md`、`经验沉淀.md`、`录音会议存档SOP.md` |
| **A4** | **没有 schema 单一事实源**：frontmatter 枚举散在 3 份文档里，实际用法早就跑飞 | 实测 273 个非存档 md：`type` **24 种**取值（17 个文件完全没有 `type`）、`status` **9 种**（22 个没有）、`audience` **5 种**——手册只定义了 3 种，实际多出 `public`（67 次）和自创的 `agent+human`（2 次），另有 30 个文件没有；`editable` 缺 44、`updated` 缺 46、`created` 缺 38 |
| **A5** | **检索只有 grep**：865 个文件没有全文索引，agent 每次靠"目录印象"找文件 | 库里唯一检索手段是 grep；`astronaut` preset 那边有 FTS5 索引，但只索引自己那 19 个文件 |

### B 类 · 让 agent 做错（规范层，6 条）

| # | 问题 | 证据 |
|---|---|---|
| **B1** | **`归档操作规范.md` 与 `运营手册.md` 直接冲突**，且冲突被"绕过"而不是被修好 | 规范 Step 1 写"存入项目目录 `02_归档文件/`"，手册 §1.1 写"唯一存放位置 `05_档案/会议存档/`"。手册 2026-06-19 就宣布废止旧 SOP，规范文件至今没改 |
| **B2** | **规范里还有两个失效路径** | `归档操作规范.md` Step 2 指向 `04_人物/`（实际 `03_人物/`）和"任务文件放 `02_项目/项目名/`，type: task"（任务机制已废止并入项目页） |
| **B3** | **`vault-archiving` skill 用"已知陷阱"章节代替修规范** | skill 里有一整节"⚠️ 已知陷阱：`归档操作规范.md` 文本与实际约定不一致"，把矛盾写成注意事项，等于把 bug 固化成文档 |
| **B4** | **决策灯有两套，口径不同** | `AGENTS.md`：红灯 = "**先问**宇航员"；`astronaut` preset：红灯 = "**先说明再执行**"。同一件事两种行为 |
| **B5** | **`status` / `type` 中英混用**，Dataview/Bases 查询会漏 | `type` 里同时有 `draft`/`draft`（42 次）与 `影评`/`公众号文章`/`游戏推荐`/`评分`；`status` 里同时有 `final`/`draft`/`archive` 与 `进行中`/`选定版` |
| **B6** | **`review` 状态成了黑洞**：4 个文件挂了 114 天没人管 | `04_灵感/品牌策略/品牌手册.md`、`品牌目标.md`、`品牌策略备忘.md`、`05_档案/会议存档/2026-06-01-何力长片项目面谈.md` |

### C 类 · 让库失控（结构层，5 条）

| # | 问题 | 证据 |
|---|---|---|
| **C1** | **292 篇文章双份存** | 年份目录（`2022`–`2026`）295 个唯一文件名 vs `.github-pages/articles/` 294 个，**交集 292**。`_meta/removals.md` 自己写了规则"重复内容保留年份目录版本"，但从没执行 |
| **C2** | **`.hermes/` 8.9 MB 被 git 跟踪**（Hermes 时代的附件缓存，现在是死目录）| 6 个文件：2 个 docx **与项目目录 md5 完全相同**（可直接删）；4 个 PDF 是政策**原文**，项目目录里放的是 `_标注版.pdf`（内容不同，**不能直接删**，要归位）|
| **C3** | **19 MB 的 `node_modules` 留在库内** | `05_档案/公众号存档/_skill/node_modules/`（playwright-core + playwright）。虽然嵌套 `.gitignore` 排除了它，但它仍在工作区，且每次 `rglob` 都要扫 |
| **C4** | **会议存档命名两种风格** | 17 个文件里 8 个用 `YYYY-MM-DD-主题.md`、8 个用 `YYYY-MM-DD_主题.md`，1 个（`宇航员个人访谈-…`）无日期前缀。手册规定是下划线 |
| **C5** | **`_changelog.md` 只增不减** | 审计当天 1184 行，**当天又涨到 1229 行**（+45 行）——因为它没有轮转机制。145 个 `## ` 标题里 **133 条合规、12 条不合规**（形如 `## 2026-09-27`，缺 `[日期 时间]` 和 `类型 \| 文件`，破坏 `grep "^## \["` 解析约定）|

### D 类 · 让工作重复（自动化层，4 条，含 1 个实测坑）

| # | 问题 | 证据 |
|---|---|---|
| **D1** | **健康检查靠手动跑** | `00_系统/agent/vault-health-check.py` 写了"每周或动手前运行"，没有任何定时机制 |
| **D2** | **公众号存档校验靠手动跑** | `wxmp-verify.py` 同款问题；9 月的 17 篇补录就是"忘了跑"导致的 |
| **D3** | **`dsh headless` 现在跑不起来**（实测）——这挡住了所有定时自动化的路 | 实跑 `dsh --profile headless "…"` → `MISSING_CREDENTIAL: llm-deepseek: no API key for provider route "deepseek-official"`。`~/.dsh/profiles/headless/` 没有模型路由补丁，而 desktop profile 有。**加 `--patch` 指向 sensenova 后实测跑通** |
| **D4** | **库和 astronaut preset 的记忆层是两套互不可见的系统** | preset 侧：32 个文件 / 476 KB，FTS5 索引 19 文件 891 条目；库侧：865 文件。库里的行业知识 preset 检索不到，preset 里的公理/案例词库里的 agent 也读不到 |

### 另外两条（文档陈旧，顺手记）

| # | 问题 |
|---|---|
| **E1** | 记忆和文档里的路径已失效：`~/Documents/OH-WorkSpace/24帧运营库`（不存在，实际 `~/Documents/24帧运营库`）、`~/Github/24frames-web`（不存在，实际 `~/Documents/24FRAMES-WEB`）。`24frames-vault` skill 的默认路径就是那个失效路径 |
| **E2** | `05_档案/公众号存档/_meta/corpus-overview.md` 的年度分布数字（49/62/70/66/47 = 294）与实际（48/62/71/66/48 = 295）对不上 |

---

## 3. DSH 能力盘点：6 件你现在没用上的事

> 全部来自本机 DSH 包内的 README（`~/.dsh/profiles/node_modules/@deepseek-ai/…`），不是推测。

| # | 能力 | 出处 | 现状 | 怎么用 | 收益 |
|---|---|---|---|---|---|
| **1** | **项目级 skill 根**：`<项目根>/.agents/skills`，优先级 **rank 200**，高于用户级 `~/.agents/skills`（rank 500） | `dsh-skill-filesystem` README「Roots and priority」 | 运营库根目录下没有 `.agents/`，vault 相关 skill 全在 `~/.agents/skills/`（全局、跨项目、不在版本控制里） | 在库根建 `.agents/skills/`，把 `24frames-vault`、`vault-archiving` 搬进库 | skill 跟着库走，**进了 git**，Claude Code / Codex 也能读；改库=改 skill，不会再脱节 |
| **2** | **嵌套 `AGENTS.md`**：agent 每 `read`/`write`/`edit` 到一个更深目录，下一次请求就带上那层的 `AGENTS.md` | `dsh-agent-instructions` README | 只有库根一个 `AGENTS.md` | 在 `02_项目/`、`06_AI/`、`05_档案/会议存档/` 各放一份 20 行的局部规则 | 项目页规则、AI 产出规则、归档规则**在用到的那一刻才进上下文**，不占用无关任务的预算 |
| **3** | **AGENTS.md 有 65,536 字节预算**，现在只用掉约 11 KB | `dsh-agent-instructions` README（`maxBytes: 65536`） | 全局 8.4 KB + 库内 2.7 KB ≈ 11 KB | 可以把 schema 摘要、决策灯、路由表写进 `AGENTS.md`，预算充足 | 一次请求就能拿到完整规则，不用再"先读 6 个文件" |
| **4** | **skill frontmatter 开关**：`disable-model-invocation: true`（对人可见、不进模型目录）、`user-invocable: false`（对模型可见、不进人用的命令） | `dsh-skill-filesystem` README「Skill format」 | 170 个 skill 全部默认双开 | 路由壳（如 `vault-archiving`）设 `user-invocable: false`；纯人用的操作手册设 `disable-model-invocation: true` | 模型目录变干净，误触发变少 |
| **5** | **`dsh headless` 一次性任务 + `--patch` 覆盖 + `--json`**（`--session-id` 还能续跑同一会话） | `dsh headless --help`（本机实测） | 未配置，跑不通（见 D3） | 配 `~/.dsh/profiles/headless/cordis.patch.yml`，然后用 launchd/cron 定时跑健康检查、周报、复利压缩 | **跨 session 自动化的唯一可行入口**，补上 2026-09-20 那份思路讨论里认定的"最大缺口" |
| **6** | **大文件与附件的正规通道**：`dsh-attachment`、`dsh-spill`、`@文件引用` | 包清单 `dsh-attachment` / `dsh-spill` / `dsh-file-reference` | 库里直接塞 16 MB 海报、22 MB node_modules | 大素材不进库（或进 `git-lfs`），库内只留路径引用；单次任务素材放 `06_AI/<日期_主题>/attachments/` | 库体积和工作区扫描成本降下来 |

> 补充：DSH 的 `dsh-schedule` 是**会话内提醒**（最小间隔 5 分钟，必须有一个活着的 session 才投递），不适合"每天定时跑库维护"。跨 session 定时请走 **`dsh headless` + launchd**。

---

## 4. 对标 Karpathy LLM Wiki：你已经对了 70%，差的是那 30%

Andrej Karpathy 在 2026-04 发布的 LLM Wiki 模式（[原始 gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)｜[系统解读](https://www.aibuilderclub.com/blog/karpathy-llm-wiki)）主张：**不要做 RAG 检索原始文档，让 LLM 增量维护一个持久 wiki**。他的原话是"the wiki is a persistent, compounding artifact"，工作方式是"Obsidian 是 IDE，LLM 是程序员，wiki 是代码库"。

### 4.1 逐条对表

| Karpathy 的三层 | 他说的 | 你的库 | 差距 |
|---|---|---|---|
| **L1 原始素材层**（不可变，LLM 只读） | `raw/`，源文件不动 | 有，但不纯：`05_档案/会议存档/` 是原始层，但 `06_AI/` 里混着 whisper json、`transcript.txt` 这类原始素材 | 🟡 **层没分开**，路径随任务漂 |
| **L2 wiki 层**（LLM 全权维护） | 摘要 / 实体页 / 概念页 / 交叉引用 / 矛盾标注 | 有，而且质量更高：`01_方向`+`02_项目`+`03_人物`+`04_灵感/知识库` | ✅ 已达成 |
| **L3 schema 层**（AGENTS.md 告诉 LLM 怎么维护） | 一份 schema 文件统管结构、约定、工作流 | 有 `运营手册.md`，但**不是单一事实源**（4 处冲突），且 agent 要读 6 个文件才拼得全 | 🔴 **最大差距** |

| Karpathy 的三个操作 | 他说的 | 你的库 | 差距 |
|---|---|---|---|
| **Ingest**（摄入，一份素材动 10–15 页） | 读→讨论→写摘要→更新索引→更新实体页和概念页→追加日志 | 归档六步流程**比他更狠**（还多"背景调研"和"可交付物"） | ✅ 已超过 |
| **Query**（提问，好答案要回填成新页） | 检索→综合→**把好的答案存回 wiki** | 完全没有：讨论结果留在会话里，不落库 | 🔴 **零** |
| **Lint**（定期体检：矛盾、过期、孤儿页、缺引用） | 定期让 LLM 体检，并提示"该补哪些问题、该找哪些素材" | 有脚本，但① 手动跑 ② 只查机械项（断链/命名），不查**矛盾与过期** | 🟡 **半成品** |

### 4.2 Karpathy 的导航系统，你几乎复刻了

| 他的做法 | 你的对应 | 一致性 |
|---|---|---|
| `index.md`：每页一行摘要 + 分类，LLM 回答前先读它 | `_index.md` | ✅ 结构一致，**但查询是死的**（A1） |
| `log.md`：追加式日志，用固定前缀 `## [2026-04-02] ingest \| Title`，靠 `grep "^## \["` 取最近 5 条 | `_changelog.md`，格式 `## [YYYY-MM-DD HH:mm] 操作类型 \| 文件名` | ✅ **完全一致**（连 grep 前缀都一样），差别是你的日志永不轮转（C5） |

> 结论：**你独立走出来的是同一套架构**。真正缺的不是理念，是三件具体的事——**schema 收敛、query 回填、lint 自动化**。

### 4.3 另一个可抄的：Karpathy 的 CLAUDE.md 四原则

社区把 Karpathy 关于 LLM 行为偏差的观察做成了 70 行的 [`andrej-karpathy-skills`](https://github.com/forrestchang/andrej-karpathy-skills)（[中文拆解](https://cloud.tencent.com.cn/developer/article/2661615)），四原则：

| 原则 | 原文要求 | 移植到运营库应该写成什么 |
|---|---|---|
| **Think Before Coding** 先想再动 | 显式说出假设；不确定就问；有多种解读就都列出来**不要默默选一个** | agent 归档时：说话人识别不确定、场地名有歧义（"对方庆/放庆空间"）、数字前后矛盾 → **必须列出来问**，不许自己选一个写进去（这条你已经在做，见 `2026-10-06` 归档的"已知缺口"段） |
| **Simplicity First** 能 50 行别写 200 行 | 不写没要求的功能，不为一次性用途造抽象 | 库里对应的是**别造流程**：不要新增目录、不要新建"任务系统"、不要给一个需求写三份文档 |
| **Surgical Changes** 只动该动的 | 每一行改动都要能追溯到用户请求；不改相邻代码、不顺手"优化" | 库里对应**"用户版本优先"**（你已沉淀）；再加一条：**修规范冲突时只改那一处，不顺手重排整个文件** |
| **Goal-Driven Execution** 给成功标准 | 把"加个校验"翻译成"先写会失败的测试再让它过" | 库里对应的是：**每条任务写成"做什么 → 怎么验证"**，验收标准不能是"弄好" |

来源：[forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills)、Karpathy 原帖 [x.com/karpathy/status/2015883857489522876](https://x.com/karpathy/status/2015883857489522876)。

### 4.4 还需要补的一块：本地检索

Karpathy 在 wiki 长到几百页后靠 [tobi/qmd](https://github.com/tobi/qmd)（markdown 本地混合检索 BM25+向量+LLM 重排，带 CLI 和 MCP，约 3 万 star，是他 gist 里**唯一点名**的工具）。你的库已经 865 个文件、184 万字，到了该上检索的规模。**不必装 qmd**——见 §6 P1-4 的轻量替代（SQLite FTS5，已实测）。

### 4.5 调研补充：另外六条能直接抄的硬结论

> 完整调研（46 个 URL，逐条抓过原文）见 [[AI-agent与个人知识库协作-公开最佳实践调研]]。

| # | 结论 | 出处 | 落到运营库 |
|---|---|---|---|
| 1 | **写回要 patch，不要覆写**。`mcp-obsidian`（4,459★）的 `patch_content` 按 heading / block ref / frontmatter 字段**定点插入** | [MarkusPfundstein/mcp-obsidian](https://github.com/MarkusPfundstein/mcp-obsidian) | 写进 `AGENTS.md`：更新已有文件时**只改目标段落**，改前先读；禁止整文件重写吃掉别人的内容 |
| 2 | **单一入口文件有 200 行硬线**：`CLAUDE.md` 官方文档要求「target under 200 lines per file；更长的文件消耗更多上下文且降低遵守率」 | [docs.claude.com/.../memory](https://docs.claude.com/en/docs/claude-code/memory) | 根 `AGENTS.md` **压到 150 行以内**，细则全部下沉到嵌套 `AGENTS.md`。DSH 的嵌套 `AGENTS.md` 正是 Claude Code `.claude/rules/*.md` 的原生等价物，而且**不需要 `@` 导入**（`@` 导入不省 token） |
| 3 | **目录层级和命名本身就是给 agent 的信号**："Folder hierarchies, naming conventions, and timestamps all provide important signals." | [Anthropic 上下文工程](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | 这条直接支持 P0-8（命名统一）和 C4——命名不一致不是洁癖问题，是**让 agent 读错的问题** |
| 4 | **上下文是有限资源**：token 越多召回越差（context rot），目标是"找到**最小的**高信号 token 集合" | 同上 | 反对"进场先读 6 个规范文件"；改成 `AGENTS.md`（路由）+ 用到哪个目录才加载哪份局部规则 |
| 5 | **Skill 的三级渐进披露**：① name+description 常驻 → ② SKILL.md 正文按需读 → ③ 引用的附件再按需读 | [agentskills.io](https://agentskills.io/) | 支持把 `24frames-vault` 从 1052 行砍到 150 行（P0-4）；细则留在库内文件里，不进 skill |
| 6 | **多写者会撞车**：每次 ingest 都要重写 index/log + 10–15 个页面，两个 ingest 并发就冲突；git 会给你"散文里的 merge conflict"；`commit author` 分不清是哪个 agent | [dev.to 实测帖](https://dev.to/forrestzhang/karpathys-llm-wiki-what-it-is-and-how-to-set-one-up-56ck) | 一次只让**一个** agent 写库；定时任务**只报告不写正文**；commit message 里带 agent 标识 |

### 4.6 工程化补充：六条可执行的机制（来自第二份调研）

> 完整内容见 [[多agent协作-长期记忆-知识资产治理-工程化素材]]（50 个 URL 实测）。

| # | 结论 | 出处 | 落到运营库 |
|---|---|---|---|
| 1 | **SKILL.md 硬线 < 500 行**；且"**skill 一旦加载，内容会跨轮常驻上下文，每一行都是重复 token 成本**" | Anthropic Agent Skills 官方文档 | 这是 P0-4 砍 1052 行的直接依据。skill 只放"去哪读"，不放"写什么" |
| 2 | **没有值得直接接进 Obsidian 的记忆框架**。可移植的是四条机制：①只追加不覆写 ②事实带有效期与 provenance ③热度驱动升格（访问够多才提炼到长期）④**先索引后全文**（claude-mem 三层检索：50–100 token/条 → 时间线 → 500–1000 token/条，差一个数量级） | mem0 / Graphiti / MemOS / claude-mem | ①对应 P0-11 + patch 写回；②对应 `_schema.md` 里给判断标 `confidence`；③对应灵感页的 `stage` 升格；④对应 P0-10 的 `_index.md` 优先 |
| 3 | **frontmatter ↔ JSON Schema 校验器只有一个**：`remark-lint-frontmatter-schema`（npm） | 卫生工具调研 | P2 新增：把 `_schema.md` 落成 `_schema.json`，用它做机器校验，人读 md 版 |
| 4 | **markdown 库没有成熟的内容近似重复检测工具** | 同上（明确标注为未查证到的缺口） | P2 新增：在 `vault-health-check.py` 里自己加指纹比对（标题 + 首段 + wikilink 集合），不引外部依赖。**这条正好治 C1 的 292 篇重复** |
| 5 | **AI 自审失败是结构性的**：同一段有偏上下文是"回忆"规则而不是"执行"规则，加"再检查一遍"没用。正解是**干净上下文的子代理 + run-don't-read**（每个数值断言必须跑一个能证伪它的命令）+ 证据日志（`CLAIM/CMD/OUT/VERDICT`，**说不出证伪命令就标 UNVERIFIED**） | [anthropics/claude-code #72206](https://github.com/anthropics/claude-code/issues/72206) | 新增 §9.4 评审流水线。本方案自己就是这么验的（见 §9.4 末行） |
| 6 | **多 agent 成本**：比单 agent 聊天多用约 **15× token**，**只在广度优先可并行的场景划算**；"多数编码任务的可并行部分比研究少" | Anthropic multi-agent 研究系统 | 新增反面清单：日常归档/写作任务**不要**上多 agent 编排，一个 agent 串行做完更便宜也更一致 |

---

## 5. 目标架构（To-Be）

### 5.1 目标目录树

```
24帧运营库/
├── AGENTS.md                    ← 扩到 8–12 KB：路由表 + schema 摘要 + 决策灯 + 硬规则（唯一入口）
├── HOME.md                      ← 静态表格（agent 维护），不再依赖 Dataview
├── .agents/skills/              ← ★新增：库自带 skill（rank 200，进 git）
│   ├── 24frames-vault/SKILL.md  ← 瘦身到 ≤150 行，只做路由，规范指向库内文件
│   └── vault-archiving/SKILL.md ← 薄壳，指向 归档操作规范.md
├── .base/                       ← ★新增：Obsidian Bases 看板（原生，不用装插件）
│   ├── 项目看板.base
│   ├── 灵感待决策.base
│   └── 待拍板.base
├── 00_系统/
│   ├── 运营手册.md               ← 单一事实源，修掉与归档规范的冲突
│   ├── 归档操作规范.md           ← 修 Step1/Step2 的失效路径（P0）
│   ├── _schema.md               ← ★新增：frontmatter 唯一枚举表（type/status/audience/stage/progress）
│   ├── _index.md                ← 加"给我一个问题该读哪页"的路由段
│   ├── _changelog.md            ← 当前卷 + 归档卷
│   ├── _changelog-归档-2026H1.md ← ★新增：老条目移出
│   └── agent/
│       ├── vault-health-check.py ← 升级：加 schema 校验、重复检测、矛盾标记
│       ├── vault-lint.sh         ← ★新增：一条命令跑完全部检查
│       └── 经验沉淀.md
├── 01_方向/ … 04_灵感/           ← 不动
├── 02_项目/AGENTS.md             ← ★新增：项目页必填字段 + 会议不放这里
├── 05_档案/
│   ├── 会议存档/AGENTS.md        ← ★新增：命名规范 + 原始层规则（不加出站双链）
│   ├── 会议存档/                 ← 命名统一为 YYYY-MM-DD_主题.md
│   └── 公众号存档/               ← 删掉 292 篇重复；_skill/node_modules 移出库
└── 06_AI/
    ├── AGENTS.md                ← ★新增：三态生命周期 + 原始素材与成品分目录
    └── YYYY-MM-DD_主题/
        ├── 主文件.md
        ├── 00_原始素材/          ← ★原始层（转写、截图、json），不改写
        └── attachments/
```

### 5.2 新增文件清单（每个干什么）

| 文件 | 作用 | 谁读 | 优先级 |
|---|---|---|---|
| `00_系统/_schema.md` | frontmatter 唯一枚举表 + 每类文件的必填字段 + 校验脚本读它 | 所有 agent + lint 脚本 | P0 |
| `.agents/skills/24frames-vault/SKILL.md` | 库自带入口 skill，≤150 行，只路由 | 所有 agent | P0 |
| `02_项目/AGENTS.md` | 写项目页时的局部规则 | 写项目页的 agent | P0 |
| `06_AI/AGENTS.md` | AI 产出的三态生命周期 + 原始素材隔离 | 写产出的 agent | P0 |
| `05_档案/会议存档/AGENTS.md` | 原始层规则 + 命名规范 | 归档的 agent | P0 |
| `.base/*.base` | 给宇航员看的看板，原生 Bases | 宇航员 | P1 |
| `00_系统/agent/vault-lint.sh` | 一条命令跑完全部检查 | cron / agent | P1 |
| `~/.dsh/profiles/headless/cordis.patch.yml` | 让 `dsh headless` 能跑（库外） | 定时任务 | P1 |
| `00_系统/_changelog-归档-*.md` | 日志分卷 | agent | P2 |

---

## 6. 优化清单：P0 / P1 / P2

> 每条格式：**改什么 → 怎么改 → 做完的标志**。附件B 提供可直接照抄的文件内容。

### 6.0 P0-0：先修 agent 自己的三个坏习惯（不动库，改行为）

| 坏习惯 | 该怎么改 | 为什么 |
|---|---|---|
| 发现规范矛盾就写"已知陷阱"绕过 | **停下来，改规范原文**，然后在 changelog 记一行"修规范" | `vault-archiving` 里那个"⚠️ 已知陷阱"章节已经挂了 3 个月，矛盾还在 |
| 把 skill 名当笔记链（写成了指向 `film-spotlight-writing` 的 wikilink） | wikilink **只链笔记**，skill 名写反引号或纯文本 | 这是 6 个断链里的 3 个 |
| 产出直接堆在 `06_AI/<日期_主题>/` 根下 | 原始素材进 `00_原始素材/`，成品在主题目录根 | 现在 whisper json 和成品混在一起 |

### 6.1 P0：不用拍板、本周能做完（8 条）

| # | 改什么 | 怎么改 | 做完的标志 |
|---|---|---|---|
| **P0-1** | **修 `归档操作规范.md` 的两处失效路径** | Step 1 第 4 条 `02_归档文件/` → `05_档案/会议存档/`；Step 2 的 `04_人物/` → `03_人物/`；删掉 Step 2 里的"任务文件"段（任务已并入项目页）；文末"目录结构参考"同步改 | 文件里搜不到 `02_归档文件`、`04_人物`、`03_任务` |
| **P0-2** | **建 `00_系统/_schema.md`** | 照抄附件B §B1。定义：`type` 12 个合法值、`status` 5 个、`audience` 3 个、`stage` 4 个、`progress` 6 个；每类文件必填字段表；"新增取值要改这个文件"的硬规则 | `_schema.md` 存在，`运营手册.md` / `归档操作规范.md` / skill 都改为**引用**它，不再各写一份 |
| **P0-3** | **修 6 个断裂双链** | `03_人物/宇航员.md` 那条被截断的多行 wikilink（目标以 `何力长片-浮生若丽` 开头）重写；`06_AI/2026-07-10_痴迷影评/影评评分机制-可复用版.md` 的三个 skill 名去掉 `[[]]`；`_changelog.md` 里两个历史断链加进脚本白名单 | `python3 00_系统/agent/vault-health-check.py` 退出码 0 |
| **P0-4** | **把 skill 搬进库并瘦身** | 库根建 `.agents/skills/`，`24frames-vault` 从 **1052 行砍到 ≤150 行**（只留路由 + 硬规则 + 指向库内文件的路径）；`vault-archiving` 删掉「已知陷阱」整节（P0-1 已修规范）。**官方硬线是 SKILL.md < 500 行**，1052 行是 2 倍超限——而且"skill 一旦加载就常驻上下文，每一行都是每轮重复付费的 token" | 库根 `.agents/skills/` 存在且进 git；两个 skill 都在 150 行内；搜不到 `OH-WorkSpace`、`03_任务`、`06_灵感库` |
| **P0-5** | **三份嵌套 `AGENTS.md`** | `02_项目/`、`06_AI/`、`05_档案/会议存档/` 各一份，每份 15–25 行，照抄附件B §B2 | 三个文件存在；`AGENTS.md`（根）里写明"进入子目录会自动加载局部规则" |
| **P0-6** | **修 `HOME.md` 的死查询** | 4 个 ```dataview 块改成 **agent 维护的静态表格**（每次改动项目页时顺手更新），另建 `.base/项目看板.base` 给 Obsidian 用 | `HOME.md` 在 Obsidian 里打开看到的是真表格，不是代码块 |
| **P0-7** | **清死目录** | ① `.hermes/` 里的 **2 个 docx 是精确重复**（md5 与 `02_项目/何力长片-浮生若丽/01_参考文档/` 下同名文件一致）→ 删；**4 个政策 PDF 是原文**（项目里是 `_标注版`，不是同一文件）→ 移到 `02_项目/何力长片-浮生若丽/01_参考文档/00_原始政策文件/` 归位；② `git rm -r --cached .hermes`，`.gitignore` 加 `.hermes/`；③ `05_档案/公众号存档/_skill/node_modules/` 移出库（先把 `SKILL.md`、`docs/python-fetching.md` 复制进 `06_AI/2026-10-05_公众号抓取工具链/`）；④ 删 5 个 `.DS_Store` | `.hermes` 不再被跟踪；工作区体积降到 175 MB 以下；`_skill` 目录不再存在于库内 |
| **P0-8** | **统一会议存档命名** | 8 个 `YYYY-MM-DD-主题.md` 改成 `YYYY-MM-DD_主题.md`；`宇航员个人访谈-…` 补日期前缀；**同步改所有指向它们的 wikilink**（Obsidian 按 basename 解析，改名会断链，必须一起改） | `ls 05_档案/会议存档/` 全部符合 `^\d{4}-\d{2}-\d{2}_`；健康检查断链数不增加 |
| **P0-9** | **声明 raw 层不可写边界**（卡帕西 L1） | 在根 `AGENTS.md` 硬规则里加一条：`05_档案/` 是**原始层，agent 只能读**——不得改写、不得移动、不得重命名。唯一例外是按归档 SOP 在 `会议存档/` **新建**文件。编译产物只能写 `06_AI/` 与 `04_灵感/` | `AGENTS.md` 里有这条；任何 agent 被要求"改一下会议存档里的字"时应该拒绝并说明 | 
| **P0-10** | **`_index.md` 改成机器优先索引** | 从"结构说明"改成"内容目录"：每个内容文件一行 `[[文件名]] — 一句话摘要`，按 `01`–`06` 分节。规则写进 `AGENTS.md`：**任何查找先读 `_index.md`，再钻取具体文件**（卡帕西：数百页规模下这能完全替代向量检索） | `_index.md` 里能被 `grep` 出每个 `01_方向` / `02_项目` / `03_人物` / `04_灵感` 文件的摘要行 | 
| **P0-11** | **"有价值的回答必须落成文件"** | 在 `AGENTS.md` 加硬规则：任何一次对话里产出的**分析、对比表、判断**，只要宇航员认可，必须落成 `06_AI/<日期>_<主题>/` 下的页面并在 `_index.md` 登记。禁止只留在聊天里 | 规则在 `AGENTS.md`；下一次"帮我分析一下 X"之后，库里能找到一个对应文件 |

### 6.2 P1：需要宇航员拍板（6 条）

| # | 改什么 | 怎么改 | 为什么需要拍板 | 做完的标志 |
|---|---|---|---|---|
| **P1-1** | **删 292 篇重复文章** | 保留年份目录版本，删 `.github-pages/articles/*.md`（**保留** `api/*.json`、`stats.json`，那些是索引数据）；删前 `git tag archive-dedup-20261006` 兜底 | 删文件 = 红灯 | 公众号存档 md 从 596 降到 ~304；`_meta/removals.md` 记录本次去重 |
| **P1-2** | **`_changelog.md` 分卷** | 保留最近 90 天，更早的整段移到 `00_系统/_changelog-归档-2026H1.md`；`_index.md` 里加两个入口 | 改 00_系统 受控文件 | 当前卷 ≤400 行；`grep "^## \[" _changelog.md` 仍能用 |
| **P1-3** | **`dsh headless` 配好 + 上定时** | 建 `~/.dsh/profiles/headless/cordis.patch.yml`（内容见附件B §B3，**已实测跑通**），再用 launchd 每天 09:00 跑 `vault-lint` | 改库外配置 + 会消耗 API token | `dsh --profile headless "回答：OK"` 返回正常；`launchctl list \| grep 24frames` 有任务 |
| **P1-4** | **落库检索（轻量版）** | 不装 qmd。用 `sqlite3` + FTS5 建 `00_系统/agent/vault-index.db`，索引 `00_系统`–`04_灵感`+`06_AI`（跳过公众号存档），提供 `vault-search.py "关键词"` | 新增工具，需要维护意愿 | `python3 00_系统/agent/vault-search.py "苏宁"` 秒回相关文件列表 |
| **P1-5** | **接上 astronaut preset 的记忆层** | 两条路选一条：① 让 preset 的 `index.sh` **索引运营库**（现在只索引自己 19 个文件）；② 库内 `_index.md` 暴露一个"人设/公理/经验"区块给 preset 读 | 涉及 preset，属库外 | preset 的 RAG 检索能命中库里的项目/人物页 |
| **P1-6** | **处理 4 个 114 天没动的 `status: review`** | `04_灵感/品牌策略/` 三篇 + 何力面谈页：要么降级 `status: final`，要么进 `HOME.md` 的"等我拍板"区 | 涉及内容定性 | 健康检查 review 项归零或明确列在 HOME |

### 6.3 P2：观察项（5 条，不急着做）

| # | 事项 | 触发条件 |
|---|---|---|
| P2-1 | 上 `git-lfs` 管大素材（现有 16 MB 海报、8.4 MB PDF） | 库体积再涨 50 MB |
| P2-2 | 加 `pre-commit` hook 跑 `vault-lint.sh`，不合规不让提交 | P1-3 跑稳两周后 |
| P2-3 | `06_AI` 产出的 `_已校准` 三态真正用起来（现在 0 个文件在用） | 下一次宇航员校准文案时 |
| P2-4 | 公众号存档「转载判定」自动化（`wxmp-audit.py` 现在靠 `_meta/removals.md` 手工维护） | 下次补档时 |
| P2-5 | 给 `05_档案/写作DNA/` 的 20+ 个 JSON 建 `_meta/index.json` 说明 | 要用到写作 DNA 时 |
| P2-6 | 把 `_schema.md` 落成 `_schema.json`，用 `remark-lint-frontmatter-schema` 做机器校验（这是调研里找到的**唯一**一个 frontmatter↔JSON Schema 校验器）| P0-2 落地两周后 |
| P2-7 | 在 `vault-health-check.py` 里自己加**内容指纹比对**（标题 + 首段 + wikilink 集合），治 C1 类重复。调研确认：markdown 库没有成熟的开源近似重复检测工具，只能自己写 | C1 去重之后作为回归防线 |

---

## 7. 执行路线图

| 阶段 | 时间 | 内容 | 依赖 |
|---|---|---|---|
| **第 0 步** | 半小时 | **P0-9（raw 层边界）+ P0-10（_index 机器优先）+ P0-11（回答落文件）** | 无。纯文档约定，零风险，**收益最大成本最低，先做这三条** |
| **第 1 步** | Day 1 | P0-1（修规范）+ P0-2（_schema）+ P0-3（断链） | 无，可并行 |
| **第 2 步** | Day 1–2 | P0-4（skill 进库）+ P0-5（嵌套 AGENTS.md） | 依赖 P0-2 |
| **第 3 步** | Day 2 | P0-6（HOME 静态化 + .base）+ P0-7（清垃圾） | 无 |
| **第 4 步** | Day 3 | P0-8（会议命名统一，含双链同步） | 依赖 P0-3 已把断链清零，否则分不清新断链 |
| **第 5 步** | 拍板后 | P1-1（去重）+ P1-2（日志分卷） | 红灯，等宇航员 |
| **第 6 步** | 拍板后 | P1-3（headless + 定时）→ P1-4（检索） | P1-3 是 P2-2 的前置 |
| **第 7 步** | 拍板后 | P1-5（接 preset 记忆）+ P1-6（清 review） | 可独立 |

**每个阶段的收尾动作（不能省）**：
1. 跑 `python3 00_系统/agent/vault-health-check.py --detail`，确认没有新增错误
2. `_changelog.md` 追加 `## [YYYY-MM-DD HH:mm] 操作类型 | 文件名`
3. `git add -A && git commit -m "<类型>: <做了什么>"`

---

## 8. 给不同 agent 的分工

| 角色 | 入口 | 该干什么 | 不该干什么 |
|---|---|---|---|
| **DSH（desktop / web）** | `AGENTS.md` → `_schema.md` → 对应目录的局部 `AGENTS.md` | 归档、写项目页、产出 AI 草稿、跑 lint | 不要把 skill 内容抄进库，库是事实源 |
| **`dsh headless`（cron）** | 无会话，纯任务文本 | 每天跑 `vault-lint.sh`；每周生成"库健康周报"写进 `06_AI/`；月度跑一次"矛盾扫描" | 不要自动改内容，**只报告**（改内容要人确认） |
| **Claude Code / Codex** | 库根 `AGENTS.md` + `.agents/skills/` | 读同一个 schema，产出落到 `06_AI/YYYY-MM-DD_主题/` | 不要自己新建目录层级；不要绕开 `_schema.md` |
| **Obsidian（宇航员）** | `HOME.md` + `.base/` | 看板、拍板、校准（文件名加 `_已校准`） | — |
| **astronaut preset（数字分身）** | `persona/` + `memory/` | 人设、公理、复利压缩 | 库里的**业务事实**以库为准，preset 只放"怎么做人"不做"业务台账" |

**边界口诀：库管事实，preset 管性格，skill 管流程。**

---

## 9. 验收标准与回滚

### 9.1 全部做完的验收（跑这一条就够）

```bash
cd ~/Documents/24帧运营库
bash 00_系统/agent/verify-p0.sh                         # 期望：10 项全 ✅
python3 00_系统/agent/vault-health-check.py --detail    # 期望：退出码 0
git status --short                                      # 期望：干净
ls .agents/skills/ 00_系统/_schema.md .base/ 02_项目/AGENTS.md 06_AI/AGENTS.md 05_档案/会议存档/AGENTS.md
grep -rn "OH-WorkSpace\|03_任务\|06_灵感库\|02_归档文件/" --include='*.md' . | grep -v _changelog | grep -v _archive
                                                         # 期望：无输出
wc -l AGENTS.md                                          # 期望：≤150
grep "^## \[" 00_系统/_changelog.md | tail -5           # 期望：5 条格式统一的记录
dsh --profile headless "回答两个字：可用"                 # 期望：正常返回
```

### 9.2 分项验收

| 项 | 通过条件 |
|---|---|
| 规范一致性 | 全库搜 `02_归档文件/`、`04_人物/`、`03_任务` 只剩 changelog 历史记录 |
| schema 收敛 | 新建文件的 `type`/`status`/`audience` 100% 落在 `_schema.md` 枚举内 |
| skill 跟随库 | `.agents/skills/` 在 git 里；skill 内不出现库外绝对路径 |
| 上下文成本 | 谈一个项目只需要 `AGENTS.md`（≤150 行）+ 项目页 + `02_项目/AGENTS.md`，不需要读手册全文 |
| raw 层边界 | `05_档案/` 在最近 30 天 git log 里没有"内容修改"型提交（只有新增归档） |
| 自动化 | 连续 3 天 cron 有执行记录，且健康检查结果写进了日志 |
| 体积 | 工作区 < 175 MB，`.git` < 80 MB |

### 9.3 评审流水线（对外交付物必过）

> 依据：Anthropic 官方 issue 的结论——**自审失败是结构性的**，加"再检查一遍"无效。有效的是换干净上下文 + 强制跑命令。

| 段 | 做什么 | 谁做 |
|---|---|---|
| ① 干净上下文 | 起一个**不带主会话历史**的子代理，只给它 `git diff` 和文件清单 | 主 agent 派发 |
| ② run-don't-read | 每个数值/行为断言，必须**跑一个能证伪它的命令**（`wc -l`、`md5`、`grep`、实跑脚本），不许只"读一遍觉得对" | 评审子代理 |
| ③ 证据日志 | 每条结论写 `CLAIM / CMD / OUT / VERDICT`。**说不出证伪命令的，标 UNVERIFIED，不算通过** | 评审子代理 |
| ④ 卡口 | 评审没出结论前不 `git commit` | 主 agent |

**互审要跨模型家族**：同一模型自审有 correlated blind spots。库里可用的组合是 DSH(deepseek) / Claude Code / Codex——用不同家族的模型审同一份对外文档。

**本方案自己的执行记录**：找出了 3 处自己的错误——`.hermes` 的重复判定（4 个 PDF 其实是原文，不是副本）、`05_档案` 文件数（670 含 node_modules，实为 642）、`status` 取值数（11 → 实为 9）。修正见 commit `64af1de`。

### 9.4 回滚

| 操作 | 回滚方式 |
|---|---|
| P1-1 删重复文章 | `git tag archive-dedup-20261006` → `git checkout archive-dedup-20261006 -- 05_档案/公众号存档/.github-pages/articles` |
| P0-4 skill 搬家 | 旧 skill 留在 `~/.agents/skills/` 不删，观察两周再删 |
| P0-8 会议改名 | 一次性做完就 commit，`git revert <sha>` 可整体回退 |
| P1-3 headless 配置 | 删掉 `~/.dsh/profiles/headless/cordis.patch.yml` 即恢复原状 |

---

## 10. 反面清单：明确不做什么

| 不做 | 为什么 |
|---|---|
| 不装 Dataview 社区插件 | Obsidian 核心已开 `bases: true`，原生 Bases 够用，少一个插件依赖 |
| 不引入第二套目录编号（Johnny Decimal 全量版） | 5+1 已经够好，`运营手册` §设计哲学说得对：越少越好找 |
| 不把 `05_档案/公众号存档` 加 frontmatter | 宇航员明确要求过"不动公众号文件" |
| 不让 agent 自动改内容 | 定时任务只报告不写正文，改动一律走人确认 |
| 不为"未来可能的需求"造目录和流程 | Karpathy 的 Simplicity First：不写没要求的东西 |
| 不把 skill 内容复制进库 | 库是事实源，skill 是路由。两边都存=两边都会过期（现在的 `24frames-vault` 就是反面教材） |
| 不追求"零警告" | `_DS_Store`、空目录这类信息项不用管，把精力放在错误项和规范一致性上 |
| 日常任务不上多 agent 编排 | 多 agent 比单 agent 多用约 **15×** token，只在广度优先可并行时划算（如本次的两份并行调研）。归档、写稿、改项目页这类串行活儿，一个好 agent 做完更便宜也更一致 |
| 不装 Claude Code 的 PreToolUse 那一套 | DSH 没有 PreToolUse 钩子。**DSH 里等价的口子是 git pre-commit hook + `--sandbox`/审批策略**（见 P2-2）。硬要"写入前拦截"，只能靠 hook 跑 lint 拦住 commit，拦不住 write 本身——这一点要如实告诉 agent，别让它以为有绝对防线 |

---

## 11. 参考来源

| 主题 | 链接 |
|---|---|
| Karpathy LLM Wiki 原始 gist | https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f |
| LLM Wiki 三层三操作解读 | https://www.aibuilderclub.com/blog/karpathy-llm-wiki |
| Karpathy 四原则仓库 | https://github.com/forrestchang/andrej-karpathy-skills |
| Karpathy 原帖 | https://x.com/karpathy/status/2015883857489522876 |
| 四原则中文拆解 | https://cloud.tencent.com.cn/developer/article/2661615 |
| qmd（markdown 本地混合检索） | https://github.com/tobi/qmd |
| Obsidian Bases 语法 | https://obsidian.md/help/bases/syntax |
| 本库配套调研①：卡帕西/文档规范/知识库协作（46 个 URL 逐条抓原文） | [[AI-agent与个人知识库协作-公开最佳实践调研]] |
| 本库配套调研②：记忆分层/文件即协议/卫生工具/Git 治理/评审流水线（50 个 URL 实测） | [[多agent协作-长期记忆-知识资产治理-工程化素材]] |
| mcp-obsidian（定点 patch 写回） | https://github.com/MarkusPfundstein/mcp-obsidian |
| basic-memory（可直接指向 vault） | https://github.com/basicmachines-co/basic-memory |
| llms.txt v2 规范 | https://llmstxt.org/ |
| Anthropic 上下文工程 | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents |
| Agent Skills 开放标准 | https://agentskills.io/ |
| Claude Code 记忆与 CLAUDE.md 规范 | https://docs.claude.com/en/docs/claude-code/memory |
| DSH skill 根与优先级 | 本机 `~/.dsh/profiles/node_modules/@deepseek-ai/dsh-skill-filesystem/README.md` |
| DSH AGENTS.md 加载规则 | 本机 `…/dsh-agent-instructions/README.md` |
| DSH headless 用法 | 本机 `dsh headless --help` |
| DSH schedule 能力边界 | 本机 `…/dsh-schedule/README.md` |

## 关联

- [[运营手册]] ｜ [[_index]] ｜ [[归档操作规范]] ｜ [[HOME]] ｜ [[经验沉淀]]
- [[附件A-规范修订对照表]] ｜ [[附件B-Agent落地执行手册]]
- 相关方向：[[观影团]] ｜ [[宣发平台]] ｜ [[影视创作]]
- 前序讨论：[[06_AI/2026-09-20_DSH-AI宇航员思路讨论/思路讨论|DSH-AI宇航员思路讨论]]
- 配套调研①：[[AI-agent与个人知识库协作-公开最佳实践调研]]
- 配套调研②：[[多agent协作-长期记忆-知识资产治理-工程化素材]]
