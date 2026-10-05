---
type: research
name: AI agent 与个人知识库/笔记库协作 · 公开最佳实践调研
status: final
audience: agent+human
created: 2026-10-05
updated: 2026-10-05
sources:
  - https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
  - https://agents.md/
  - https://llmstxt.org/
  - https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
  - https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
  - https://docs.claude.com/en/docs/claude-code/memory
---

# AI agent 与个人知识库协作 · 调研

所有 URL 均已实际抓取。标"未查证"的是抓取失败或只能拿二手来源的项。

## 1. 卡帕西相关

### 1.1 原始出处已定位：不是"笔记方法"，是一份可执行的 idea file

2026-04-02/03 卡帕西发 X 帖「LLM Knowledge Bases」，次日（4 月 4 日）跟一条补充帖并放出 **GitHub gist `llm-wiki.md`**。gist 原文首行自述："This is an idea file, it is designed to be copy pasted to your own LLM Agent (e.g. OpenAI Codex, Claude Code, OpenCode / Pi, or etc.)"。

- gist 全文（已抓取，11,985 字节 / 75 行）：[gist.github.com/karpathy/442a6bf555914893e9891c11519de94f](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- 原帖：[x.com/karpathy/status/2039805659525644595](https://x.com/karpathy/status/2039805659525644595)（X 页面本身未抓取成功）
- 互动量：一手未查证。第三方（dev.to 作者 Forrest Zhang）称到 2026 年 9 月底约 **2190 万浏览、10.86 万书签**：[dev.to/forrestzhang/karpathys-llm-wiki-what-it-is-and-how-to-set-one-up-56ck](https://dev.to/forrestzhang/karpathys-llm-wiki-what-it-is-and-how-to-set-one-up-56ck)

### 1.2 核心主张：wiki > RAG，因为知识要被"编译一次"

卡帕西原文（gist 第 9–13 行）：

> "Most people's experience with LLMs and documents looks like RAG... the LLM is rediscovering knowledge from scratch on every question. There's no accumulation."
> "the LLM **incrementally builds and maintains a persistent wiki** — a structured, interlinked collection of markdown files that sits between you and the raw sources."
> "The knowledge is compiled once and then *kept current*, not re-derived on every query."

**可直接抄的做法**：把"每次检索"改成"入库时合成"。新素材进来时同步修订实体页、主题页，并显式标注"这条新数据推翻了哪条旧结论"。

### 1.3 三层架构（gist 第 27–33 行，逐字）

| 层 | 归属 | 卡帕西原话要点 |
|---|---|---|
| **Raw sources** | 人 | "These are immutable — the LLM reads from them but never modifies them. This is your source of truth." |
| **The wiki** | LLM | "The LLM owns this layer entirely... You read it; the LLM writes it." |
| **The schema** | 人+LLM 共演化 | "a document (e.g. CLAUDE.md for Claude Code or AGENTS.md for Codex)... the key configuration file — it's what makes the LLM a disciplined wiki maintainer rather than a generic chatbot." |

**可直接抄的做法**：给 agent 划一条不可越过的只读线（raw 层），再让它全权拥有一个可写目录。两者混在一起时 agent 会反过来"修订"原始记录。

### 1.4 三个操作 + 两个索引文件

- **Ingest**：「A single source might touch 10-15 wiki pages.」流程 = 读源 → 与人讨论要点 → 写 summary 页 → 更新 index → 更新相关 entity/concept 页 → 追加 log。
- **Query**：「**good answers can be filed back into the wiki as new pages.** A comparison you asked for, an analysis, a connection you discovered — these are valuable and shouldn't disappear into chat history.」
- **Lint**：查「contradictions between pages, stale claims that newer sources have superseded, orphan pages with no inbound links, important concepts mentioned but lacking their own page, missing cross-references, data gaps」。
- **index.md**（内容索引）：每页一行摘要。原话："the LLM reads the index first to find relevant pages, then drills into them. This works surprisingly well at moderate scale (~100 sources, ~hundreds of pages) and avoids the need for embedding-based RAG infrastructure."
- **log.md**（时序日志）：append-only。原文给了可直接用的 shell 技巧——条目统一前缀 `## [2026-04-02] ingest | Article Title`，然后 `grep "^## \[" log.md | tail -5`。

**可直接抄的做法**：「有价值的分析必须落成文件」这一条是对聊天式协作最大的纠偏。以及给 log 定一个可被 grep 的前缀格式——这是零成本的可查询性。

### 1.5 人机分工与工作台

> "Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase."
> "Humans abandon wikis because the maintenance burden grows faster than the value. LLMs don't get bored... and can touch 15 files in one pass."

工具面：Web Clipper 剪藏 → 附件目录固定 + 绑定 "Download attachments for current file" 快捷键；graph view 看枢纽/孤岛页；Marp 出 slides；Dataview 查 frontmatter；"The wiki is just a git repo of markdown files."

**未查证**：卡帕西 25 个 GitHub 仓库（nanochat/nanoGPT/llm.c/autoresearch 等）均与 llm-wiki 无关，他 4 月唯一相关公开物就是该 gist。nanochat README 是常规项目文档，**没有**"docs that an LLM can read and improve"这类表述——此说法未查证，不要引用。

## 2. 开源项目清单

Star 数与最后 push 均来自 GitHub API / 页面抓取（2026-10-05 当日）。

| 项目 | URL | Star | 定位 | 可借鉴点 |
|---|---|---|---|---|
| **basic-memory** | [basicmachines-co/basic-memory](https://github.com/basicmachines-co/basic-memory) | 4,101 | Markdown 双向知识库 + MCP，人和 AI 写同一批文件 | 直接指向 vault 目录即用（"Point Obsidian at `~/basic-memory`"），不需要迁移；`edit_note` 支持 append/prepend 且缺文件自动创建；`write_note` 防误覆盖；有 `schema_infer`/`schema_validate`/`schema_diff` 三个工具做库结构校验 |
| **claude-mem** | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | 96,555 | 跨会话持久上下文，自动捕获 agent 会话过程 | 会话过程自动落盘，而不是靠人记得写；可作"每次动手后记 changelog"的自动化替代 |
| **mem0** | [mem0ai/mem0](https://github.com/mem0ai/mem0) | 66,604 | 通用 agent 记忆层（非 markdown 本位） | 记忆的增删改查抽象；但对 Obsidian 场景属外部数据库，不落成可读文件，移植价值低 |
| **qmd** | [tobi/qmd](https://github.com/tobi/qmd) | 30,214 | 本地 markdown 搜索引擎，BM25+向量+LLM 重排 | 卡帕西 gist 唯一点名的检索工具；同时给 CLI 和 MCP server 两种接法。库大了再上，小库用 index.md 就够 |
| **khoj** | [khoj-ai/khoj](https://github.com/khoj-ai/khoj) | 37,561 | 自托管 AI 第二大脑 | 定时任务 + 自定义 agent；semantic search 思路可参考 |
| **graphiti** | [getzep/graphiti](https://github.com/getzep/graphiti) | 31,456 | 实时知识图谱 | 时序化的实体关系（谁在什么时候说了什么），适合"人物/合作方"这种带时间线的关系 |
| **cognee** | [topoteretes/cognee](https://github.com/topoteretes/cognee) | 31,397 | AI 记忆平台 | 图 + 向量混合；同样偏外部库 |
| **letta / MemGPT** | [letta-ai/letta](https://github.com/letta-ai/letta) | 25,029 | 有状态 agent 平台 | "自编辑记忆"概念；2026-09-10 后无 push，热度下降 |
| **logseq** | [logseq/logseq](https://github.com/logseq/logseq) | 45,142 | 大纲式隐私优先知识库 | 大纲块引用（block ref）比文件级双链更细；可作为 agent 写回的粒度参考 |
| **Smart Connections** | [brianpetro/obsidian-smart-connections](https://github.com/brianpetro/obsidian-smart-connections) | 5,485 | Obsidian 内嵌语义关联推荐 | 在 Obsidian 侧做向量检索；与 agent 侧检索二选一，别重复建设 |
| **foam** | [foambubble/foam](https://github.com/foambubble/foam) | 17,438 | VS Code 里的 PKM | 纯编辑器方案，无 Obsidian 依赖 |
| **quartz** | [jackyzha0/quartz](https://github.com/jackyzha0/quartz) | 13,326 | Markdown → 静态站点 | 把库的一部分发布成对外站点，双链会转成网页链接 |
| **dendron** | [dendronhq/dendron](https://github.com/dendronhq/dendron) | 7,468 | 层级式 PKM | **已停滞**（最后 push 2025-11-13），不要选它做基础 |
| **mcp-obsidian** | [MarkusPfundstein/mcp-obsidian](https://github.com/MarkusPfundstein/mcp-obsidian) | 4,459 | 经 Obsidian Local REST API 读写 vault | 工具清单可直接抄：`list_files_in_vault` / `get_file_contents` / `search` / **`patch_content`（按 heading、block ref 或 frontmatter 字段定位插入）** / `append_content`。`patch_content` 是比全文件覆写安全得多的写法 |
| **obsidian-mcp-server** | [cyanheads/obsidian-mcp-server](https://github.com/cyanheads/obsidian-mcp-server) | 691 | MCP 读写 + 外科手术式编辑 | "surgically edit notes, tags, and frontmatter"，比 4.4k 那个更细；支持 STDIO 与 Streamable HTTP |
| **Karpathy-LLM-Wiki-Stack** | [ScrapingArt/Karpathy-LLM-Wiki-Stack](https://github.com/ScrapingArt/Karpathy-LLM-Wiki-Stack) | 未查证 | 按卡帕西模式搭 Obsidian + Claude Code 的完整参考 | 抓取被 403 限流，内容未验证 |
| **awesome-llm-wiki** | [gavischneider/awesome-llm-wiki](https://github.com/gavischneider/awesome-llm-wiki) | 216 | LLM wiki 模式的项目汇编 | 可作持续跟进的索引源 |

## 3. 社区实操案例

### 3.1 Pedram Amini：25,000 文件的 vault，六层记忆

一位安全研究员（InQuest 首席科学家）在 Obsidian vault 里内嵌 Claude Code agent，vault 含健康数据、财务、联系人、项目跟踪、会议记录、多年日记。他的自述关键句："It has persistent memory layered across **six different systems**. It has custom Python tools *it built for itself*."

- 来源：[pedramamini.com/__blog/blogs.php?sub=2026-03-27](https://pedramamini.com/__blog/blogs.php?sub=2026-03-27)
- 他自己的 agent 博客列出四篇技术文章，其中一篇叫 **《How I Fake Having Memory》**，副标题明确写"六层补偿每次会话从零开始：context window、Maestro session history、operational journal、CLAUDE.md files、semantic search、auto-memory。Where each layer works. Where each layer fails."
- **踩坑信号（重要）**：标题本身就是结论——没有单一记忆方案能解决跨会话记忆，要靠多层叠加，且每层都有失效边界。
- **未查证**：该 agent 博客的正文页抓取只返回了页面标题，具体六层细节与"哪里失效"未取到。

### 3.2 Kenneth Reitz：把 CLAUDE.md 当成 API 契约

467 个 markdown 文件、PARA 改造版编号目录（`000 Meta` / `100 Daily` / `200 Projects` / `300 Areas` … `900 Archive`）、全库统一 frontmatter（`type` / `role` / `status` / `date` / `themes`），根目录一个约 200 行的 CLAUDE.md。

- 来源（PDF，已解析全文）：[kennethreitz.org/essays/2026-03-06-obsidian_vaults_and_claude_code.pdf](https://kennethreitz.org/essays/2026-03-06-obsidian_vaults_and_claude_code.pdf)
- **可直接抄的 CLAUDE.md 反面清单**（原文）：
  > "Do not create new files unless explicitly asked. / Do not restructure existing folder hierarchies. / Do not add emojis. / Do not over-engineer simple requests. / Do not editorialize about mental health content."
- **核心隐喻**："The CLAUDE.md is an API contract... design from human mental models outward." 先定义契约，再整理笔记。
- **踩坑/立场**：明确写 "Claude proposes, you dispose. It suggests connections; you verify them against lived experience." 以及版本控制不能省（Obsidian Git 插件自动提交）。
- **其插件栈**：Smart Connections、Excalibrain、Claude Sidebar、MCP Tools、Dataview、Templater、Obsidian Git，共 26 个。

### 3.3 多写者失效模式（对"AI 维护的运营库"最实用的一段）

Forrest Zhang 基于实际运营总结出多 agent / 多机器写同一个 wiki 的四类问题：

- **两个写者改同一批文件**：每次 ingest 都会重写 `index.md`、`log.md` 以及 10–15 个页面。两个 ingest 并发就撞车；网盘同步会丢保存或留下冲突副本；git 则给你"散文里的 merge conflict"。
- **页面变馊**：lint 只在有人要求时才跑，两次 lint 之间旧结论一直被 agent 当事实复读。
- **归属不明**：没有 git 就没有历史；有 git 的话 commit author 往往是你的名字，分不清是哪个 agent 写的。
- 对策三选一：git 仓库（有历史，有冲突）/ 同步文件夹（简单，无历史，有覆盖）/ 托管服务走 MCP（单副本，无合并，需服务端处理并发写与历史）。
- 来源：[dev.to/forrestzhang/karpathys-llm-wiki-what-it-is-and-how-to-set-one-up-56ck](https://dev.to/forrestzhang/karpathys-llm-wiki-what-it-is-and-how-to-set-one-up-56ck)

### 3.4 其他已核实的接入方式

- Claude Code 原生：vault 根目录放 CLAUDE.md 即可，无需插件；MCP server 用 `claude mcp add --transport http --scope user ... --header "Authorization: Bearer $TOKEN"` 注册到 `~/.claude.json`：见 [dexio.wiki/guides/claude-code-memory](https://dexio.wiki/guides/claude-code-memory/)。
- 会话级记忆走 `~/.claude/projects/<project>/memory/MEMORY.md`，每次会话只加载前 200 行或 25KB，且**仅本机**（worktree 共享，跨机器不共享）：[docs.claude.com/en/docs/claude-code/memory](https://docs.claude.com/en/docs/claude-code/memory)
- 小型社区方案（star 量低，仅作模式参考）：[markdown-memory](https://github.com/mworldorg/markdown-memory)（25 stars，把 project passport / handoff / session log 同步进 Obsidian vault）、[obsidian-pkm-plugin](https://github.com/AdrianV101/obsidian-pkm-plugin)（13 stars，20 个工具 + agents + hooks）、[obsidian-memory-layer-mcp](https://github.com/honam867/obsidian-memory-layer-mcp)（5 stars）。

## 4. Agent 文档规范要点

### 4.1 AGENTS.md — [agents.md](https://agents.md/)

- 定位："a **README for agents**"；README 给人，AGENTS.md 给 agent。
- 采用量 "over **60k open-source projects**"；已由 Linux Foundation 下的 Agentic AI Foundation 托管。
- **无必填字段**："just standard Markdown. Use any headings you like."
- 建议覆盖：Project overview / Build and test commands / Code style / Testing instructions / Security considerations。
- **冲突规则**："The closest AGENTS.md to the edited file wins; explicit user chat prompts override everything."
- 单体仓库用嵌套文件，agent 自动读最近的（OpenAI 主仓库有 88 个）。
- 列出的测试命令，agent 会真的跑并修到通过才收工。

### 4.2 llms.txt v2 — [llmstxt.org](https://llmstxt.org/)

- 作者 Jeremy Howard，2024-09-03 初版，2026-08-10 修订为 v2。
- 位置：站点根 `/llms.txt` **或任意子路径**（`/docs/llms.txt` 覆盖 `/docs/` 全部页面），多个匹配时用最具体的。
- **强制顺序**：可选 BOM → **H1（唯一必填项）** → 引用块摘要 → 零或多个普通段落 → 零或多个 H2 分隔的"文件列表"，每项必须 `[name](url)`，后可跟 `:` 与说明。
- v2 新增：页面应提供同 URL 的干净 markdown 版（`page.html.md`）；用 `rel="alternate" type="text/markdown"` 与 `rel="describedby"` 供发现，可用 HTTP `Link:` 头。
- `## Optional` 段约定为"上下文紧张时可跳过"。
- 规模原则："The file itself stays small enough to fit in context. The detail lives behind the links."
- 已采用：OpenAI / Anthropic / Gemini 官方文档站；Mintlify、GitBook、Wix 自动生成；Chrome Lighthouse 已纳入 agentic browsing 审计。

### 4.3 上下文工程 — [effective-context-engineering-for-ai-agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

发布于 2025-09-29。硬结论：

- **上下文是有限资源**，token 越多召回越差（context rot），目标是"找到**最小的**高信号 token 集合"。
- **Just-in-time 检索 > 预先塞满**：agent 只保留轻量标识（文件路径、查询、链接），运行时加载。Claude Code 的做法是 CLAUDE.md 前置注入 + glob/grep 即时导航，"effectively bypassing the issues of stale indexing"。
- **文件系统本身就是信号**："Folder hierarchies, naming conventions, and timestamps all provide important signals." → 目录与文件命名是 prompt 的一部分。
- **长任务三件套**：compaction（保留架构决策/未解 bug/实现细节，丢冗余工具输出）、**structured note-taking**（"your custom agent maintaining a NOTES.md file"）、sub-agent（子 agent 烧几万 token，只回 1,000–2,000 token 浓缩结论）。
- 系统提示词要落在 "right altitude"：既不硬编码 if-else，也不空泛到没有可执行信号。
- 工具集要**最小且无功能重叠**："If a human engineer can't definitively say which tool should be used in a given situation, an AI agent can't be expected to do better."

### 4.4 Agent Skills — [equipping-agents-for-the-real-world-with-agent-skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

发布于 2025-10-16，2025-12-18 起作为开放标准发布于 [agentskills.io](https://agentskills.io/)。

- **硬格式**：一个目录 + 一个 `SKILL.md`，**必须以 YAML frontmatter 开头，含 `name` 与 `description` 两个必填字段**。启动时只把全部 skill 的 name+description 预载进系统提示。
- **三级渐进披露**：① name/description（常驻）→ ② SKILL.md 正文（判定相关才读）→ ③ 目录内被引用的附件（`reference.md`、`forms.md` 等按需读）。原文结论："the amount of context that can be bundled into a skill is effectively **unbounded**."
- SKILL.md 臃肿就拆文件；互斥场景分开放以省 token。
- 代码既可当工具也可当文档，但要写清是"让 Claude 跑"还是"让 Claude 读"。
- 只从可信来源装 skill，装前审依赖与网络调用。
- docs：[docs.claude.com/.../agent-skills/overview](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)

### 4.5 CLAUDE.md 现行规范 — [docs.claude.com/en/docs/claude-code/memory](https://docs.claude.com/en/docs/claude-code/memory)

- **大小硬线**：「target **under 200 lines** per CLAUDE.md file. Longer files consume more context and reduce adherence.」
- **导入语法** `@path/to/import`，相对路径按"包含该 import 的文件"解析，最大深度 **4 跳**；import **不省 token**（同样在启动时载入）；路径含空格需反斜杠转义，路径被引号包住则**完全不导入**。
- 指令必须具体：「"Use 2-space indentation" 而不是 "Format code properly"」。
- 矛盾指令会被任意挑选执行，需定期审计清理。
- `.claude/rules/*.md`：一文件一主题，可用 `paths` frontmatter 做路径作用域，只在处理匹配文件时载入。规则常驻；任务型内容应放 skill。
- 加载顺序：Managed → User（`~/.claude/CLAUDE.md`）→ Project（`./CLAUDE.md`）→ Local（`./CLAUDE.local.md`，进 .gitignore）；子目录按需加载。
- **auto memory**：Claude 自己写笔记，存 `~/.claude/projects/<project>/memory/MEMORY.md`，**每次会话只加载前 200 行或 25KB**，本机限定。
- 关键边界：CLAUDE.md 是**上下文而非强制配置**。要绝对禁止某动作，得用 PreToolUse hook。

### 4.6 未查证

Anthropic《Writing tools for agents》（[链接](https://www.anthropic.com/engineering/writing-tools-for-agents)）未单独抓取；4.3 中"工具最小化/无功能重叠"两条转述自上下文工程文章，措辞以该文为准。

## 5. 对"AI 维护的 Obsidian 运营库"的移植建议

现有 24帧运营库已具备卡帕西三层架构的雏形（`05_档案/` ≈ 半只 raw 层、`06_AI/` ≈ 编译产物层、根 `AGENTS.md` ≈ schema）。缺的是**机器可导航的索引**、**可解析的日志**、**周期性的 lint 流程**。逐条给落点：

1. **补齐 raw 层声明（不可写边界）**。在根 `AGENTS.md` 第 3 节硬规则里把 `05_档案/` 明确定义为 raw 层："原始记录，agent 只能读，不得改写、不得移动、不得重命名"。对应卡帕西 "These are immutable — the LLM reads from them but never modifies them"（[gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)）。编译产物只能写在 `06_AI/` 与 `04_灵感/`。

2. **把 `00_系统/_index.md` 改造成机器优先的目录索引**。现有 `_index.md` 是结构说明，改为"每个内容文件一行：`[[文件名]] — 一句话摘要（源数/更新时间）`"，按 01–06 分节。规则写进 AGENTS.md：**任何查询先读 `_index.md`，再钻取具体文件**。卡帕西称此方式在 ~100 源 / 数百页规模下可完全替代向量检索。注意与现有结构索引并存会违反"单一事实源"，建议合并成一份。

3. **让 `_changelog.md` 可被 grep**。格式已接近卡帕西推荐（`## [YYYY-MM-DD HH:mm] 操作类型 | 文件名`）。在 AGENTS.md 里补一句：**每条条目必须保持该前缀格式**，并在健康检查文档里给出用法，例如 `grep "^## \[" 00_系统/_changelog.md | tail -10` 取最近 10 次操作。

4. **给 frontmatter 定最小必填集**。现库已有 `type/name/status/editable/audience/created/updated`。补三项：`sources:`（来源文件或 URL 列表）、`related:`（相关页面）、`confidence: high|medium|low`。低置信度页可被 Dataview 一次性捞出来复核。参考 Kenneth Reitz 的 "At minimum: type, status, date"，以及 [Dataview 查询语法](https://blacksmithgu.github.io/obsidian-dataview/)。

5. **把健康检查脚本升级成 lint 操作**。现有 `00_系统/agent/vault-health-check.py` 已扫 frontmatter 缺失、wikilink 断裂、06_AI 命名违规、会议错位。按卡帕西的 lint 清单再加三类：**跨文件矛盾**、**被新素材推翻但未更新的旧结论**、**被提及 3 次以上却没有独立页面的概念（人物/合作方/影片）**。结果写到 `00_系统/_lint-log.md`，不直接改文件。

6. **给"新素材入库"定义固定 6 步流程**，写进 AGENTS.md 作为 ingest workflow：① 素材放 `05_档案/会议存档/YYYY-MM-DD_主题.md` → ② 读源、向宇航员复述要点 → ③ 写/更新 `06_AI/<日期>_<主题>/` 下的摘要页 → ④ 更新 `00_系统/_index.md` → ⑤ 更新受影响的 `03_人物/`、`02_项目/`、`01_方向/` 页面 → ⑥ 追加 `_changelog.md`。卡帕西原话是一份源"might touch 10-15 wiki pages"，运营库里现实预期是 3–8 个文件。

7. **给 AGENTS.md 加 200 行上限，并把细则拆出去**。当前根 AGENTS.md 已相当长，还会继续长。按 Anthropic 规范（[CLAUDE.md 文档](https://docs.claude.com/en/docs/claude-code/memory)）：单文件目标 **< 200 行**；用 `.agent/rules/*.md` 一文件一主题（归档规范、写作规范、隐私检查、财务口径各一份），通过 `@` 导入。若在 Claude Code 里跑，可直接用 `paths` frontmatter 让"归档规则"只在处理 `05_档案/` 时载入。注意 `@` 导入不省 token（仍全量载入），真正的节省来自 paths 作用域。

8. **把"有价值的回答落成文件"设为硬规则**。AGENTS.md 加一条：任何一次对话里产出的**分析、对比表、判断**，只要宇航员认可，必须落成 `06_AI/<日期>_<主题>/` 下的页面并在 `_index.md` 登记，禁止只留在聊天里。这是卡帕西 Query 操作的核心（"good answers can be filed back into the wiki as new pages"），也是运营库目前最大的信息泄漏点。

9. **写回用 patch，不用覆写**。给 agent 的写入约定按 [mcp-obsidian](https://github.com/MarkusPfundstein/mcp-obsidian) 的 `patch_content` 语义来定：**按 heading、block ref 或 frontmatter 字段定点插入**，避免整文件重写。同时借鉴 basic-memory 的 `write_note` 防误覆盖设计——写入前先读。这条直接防"agent 一次 ingest 把某页其他内容吃掉"。

10. **图片落本地固定目录**。Obsidian 设置里把附件目录固定（现库可设 `05_档案/媒体/` 或库内统一 assets 目录），绑定 "Download attachments for current file" 快捷键。卡帕西的理由是"lets the LLM view and reference images directly instead of relying on URLs that may break"，并提醒 LLM 无法一次读带内联图片的 markdown，需要先读文字再单独看图。

**实施顺序建议**：先做 1、2、3、8（纯文档约定，零风险，当天可完成），再做 4、6（改 schema 与流程，影响面大但可逆），最后做 5、7、9、10（改脚本与工具链）。第 1 条与第 8 条是收益最大且成本最低的两条。
