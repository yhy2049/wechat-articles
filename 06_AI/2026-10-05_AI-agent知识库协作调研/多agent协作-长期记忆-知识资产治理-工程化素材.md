---
type: research
name: 多 agent 协作 + 长期记忆 + 知识资产治理 · 工程化素材
status: final
audience: agent+human
created: 2026-10-06
updated: 2026-10-06
sources:
  - https://github.com/mem0ai/mem0
  - https://github.com/letta-ai/letta
  - https://github.com/getzep/graphiti
  - https://github.com/basicmachines-co/basic-memory
  - https://github.com/topoteretes/cognee
  - https://github.com/thedotmack/claude-mem
  - https://github.com/BAI-LAB/MemoryOS
  - https://github.com/MemTensor/MemOS
  - https://code.claude.com/docs/en/sub-agents
  - https://code.claude.com/docs/en/hooks
  - https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
  - https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
  - https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
  - https://www.anthropic.com/engineering/multi-agent-research-system
  - https://github.com/anthropics/claude-code/issues/72206
  - https://stevekinney.com/writing/codex-as-a-second-opinion
  - https://github.com/addyosmani/adverse
---

# 多 agent 协作 + 长期记忆 + 知识资产治理 · 工程化素材

所有 URL 均实际抓取（curl / GitHub API / Mintlify `.md` 端点）。star 数读取时间 2026-10-06。抓不到的写"未查证"。

> 与同目录《AI-agent与个人知识库协作-公开最佳实践调研》互补：那份覆盖 AGENTS.md / llms.txt / Karpathy llm-wiki / 上下文工程原则；本文覆盖**记忆分层实现、文件即协议的可执行规范、卫生工具链、Git 治理配置、评审流水线**。

## 1. 记忆分层

| 方案 | URL | 存什么 | 检索方式 | 可借鉴点 |
|---|---|---|---|---|
| **mem0** (66.6k★) | [mem0ai/mem0](https://github.com/mem0ai/mem0) | 单遍 **ADD-only** 抽取：一次 LLM 调用，不 UPDATE/DELETE，记忆只累积不覆盖；agent 自己确认的事实与用户事实同权 | 多信号并行打分再融合：语义 + BM25 关键词 + 实体匹配；带时间推理（区分"当前状态/过去事件/未来计划"） | 「**只追加不覆写**」是知识库里最该抄的一条——审计可追溯，且避免 LLM 反复重写同一结论导致语义漂移 |
| **Letta / MemGPT** (25.0k★) | [letta-ai/letta](https://github.com/letta-ai/letta) | 有状态 agent（memory blocks 分 core / archival），可自我编辑记忆 | 自编辑记忆块 + 工具调用式分页读取 | 注意：**源码已迁到 [letta-ai/letta-code](https://github.com/letta-ai/letta-code)**，letta-ai/letta 主分支只剩导航，V1 API server 进了 `archive` 分支。别照旧文档抄 |
| **Graphiti / Zep** (31.5k★ / 4.9k★) | [getzep/graphiti](https://github.com/getzep/graphiti)、[getzep/zep](https://github.com/getzep/zep) | **时序知识图谱**：追踪事实随时间如何变化，保留 provenance 指回原始数据；支持预设本体 + 学习本体 | 混合检索：语义 + 关键词 + 图遍历；增量更新，无需重算全图；支持"精确历史查询" | 「**事实有有效期**」模型直接对应运营库：人物职位、合作方、片单状态都会变。旧结论不该删，该标失效时间 |
| **basic-memory** (4.1k★) | [basicmachines-co/basic-memory](https://github.com/basicmachines-co/basic-memory) | **markdown 文件本身**（本地优先、人机双向写同一批文件、wikilink + observation 复利成图） | 语义检索 + 可选 cross-encoder rerank；MCP 接任意客户端 | 与 Obsidian 库同构，是最贴近的参考。"**渐进式工具发现**"：每个工具打 read-only / destructive / idempotent 标签，agent 不用试错就知道该用哪个，省 context |
| **Cognee** (31.4k★) | [topoteretes/cognee](https://github.com/topoteretes/cognee) | 文档/代码/对话 → 自托管知识图谱 | 图谱 + 向量检索 | 卖点是**用本地小模型跑，不用 API key**；对成本敏感的场景值得看 |
| **claude-mem** (~96.6k★) | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | 5 个生命周期 hook（SessionStart / UserPromptSubmit / PostToolUse / Stop / SessionEnd）自动捕获工具调用观察 → AI 压缩成语义摘要 → 存 SQLite（含 FTS5） | **3 层渐进检索**：`search` 拿紧凑索引 (~50–100 token/条) → `timeline` 看上下文 → `get_observations` 只对筛过的 ID 取全文 (~500–1000 token/条) | 这是"**渐进式披露落到检索层**"最完整的实现。默认不把记忆塞进上下文，先给索引让 agent 自己决定要不要深入 |
| **MemoryOS** (1.6k★, EMNLP 2025 Oral) | [BAI-LAB/MemoryOS](https://github.com/BAI-LAB/MemoryOS) | 短/中/长期**分层**：QA 对先进短期；短期满 → Updater 段化成中期的"segment"；segment 累积 **heat**（访问频率 + 交互长度），超阈值才提炼到长期 user profile / knowledge | retriever 跨全部层检索 | **衰减/压缩是显式机制，不是靠遗忘**。运营库里可以直接用：素材被引用次数 = heat，够热才升格进 `00_系统/` 或人物档 |
| **MemOS** (11.7k★) | [MemTensor/MemOS](https://github.com/MemTensor/MemOS) | MemCube 统一 store/retrieve/manage；分层 L1 traces / L2 policies / L3 world model，另加 crystallized Skills | FTS5 + 向量混合检索；智能去重 | 声称 35.24% token 节省。**L1→L2→L3 分层**（事件轨迹→策略→世界模型）可直接映射成 `06_AI 草稿 → 04_灵感知识库 → 00_系统手册` |

**结论**：没有任何一个开源记忆框架值得直接接进 Obsidian 库。真正可移植的是四条机制——①只追加不覆写；②事实带有效期；③热度驱动的升格/衰减；④先给索引再给全文。

## 2. 文件即协议

### 2.1 Claude Code subagents：`.claude/agents/*.md`

[code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents)

- 权限范围：`.claude/agents/`（项目级，**建议进版本控制**）、`~/.claude/agents/`（用户级）；**递归扫描**子目录，`agents/review/` 这种分组不影响身份——身份**只来自 `name` frontmatter 字段**。
- Frontmatter 全集：`description`、`tools`、`disallowedTools`、`model`、`permissionMode`、`mcpServers`、`hooks`、`maxTurns`、`skills`、`initialPrompt`、`memory`、`effort`、`background`、`omitClaudeMd`、`isolation`。
- 同名冲突：同一目录树下 `name` 重复时按文件系统读取顺序加载其中一个（**无文档化优先级**），`/doctor` 会报。嵌套项目目录时"离工作目录最近的赢"。
- 子代理**不继承** Claude Code 主系统提示，只拿自己那段 + 工作目录；`Explore`/`Plan` 内置代理跳过 CLAUDE.md 以省钱。
- `isolation: worktree` 给子代理一份仓库隔离副本——**多 agent 并行写同一个 Git 库的正确姿势**。

**最小可用实现**（建议直接落进 24帧库）：

```
.claude/agents/
  vault-writer.md      # 只写 06_AI/，tools: Read, Write, Edit, Grep, Glob
  vault-auditor.md     # 只读，tools: Read, Grep, Glob —— 产报告不产改动
  review-adversary.md  # memory: project，专职挑错
.claude/agent-memory/<agent-name>/MEMORY.md
```

### 2.2 子代理持久记忆（官方 `memory` 字段）

- `user` → `~/.claude/agent-memory/<name>/`；`project` → `.claude/agent-memory/<name>/`（**官方推荐默认，可进版本控制共享**）；`local` → `.claude/agent-memory-local/<name>/`。
- 启用后自动：系统提示带读写指令 + **注入 `MEMORY.md` 前 200 行或 25KB（取先到者）** + 自动开 Read/Write/Edit 工具。
- 硬性约束：超过 200 行/25KB 时代理会收到"请整理 MEMORY.md"的指令——**这条限制就是天然的上下文预算上限**。

**最小可用实现**：给 `vault-writer` 加 `memory: project`，在 md 里写死一句"每次归档后把新学到的命名/归属规则追加进 memory，保持 MEMORY.md 在 200 行内"。

### 2.3 Hooks：把"文件改动"变成有闸门的动作

[code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks)

事件全集（节选，均已在文档中核对）：`SessionStart` / `SessionEnd`、`UserPromptSubmit`、`Stop`/`StopFailure`、`PreToolUse`（**可拦截**）/ `PostToolUse` / `PostToolUseFailure` / `PostToolBatch`、`SubagentStart` / `SubagentStop`、`TaskCreated` / `TaskCompleted`、`PreCompact` / `PostCompact`、`TeammateIdle`、`Notification`、`FileChanged`、`InstructionsLoaded`、`PermissionRequest` / `PermissionDenied`、`WorktreeCreate` / `WorktreeRemove`。

- **退出码 2 = 阻断**，stderr 回灌给模型；`PreToolUse` 可返回 JSON `permissionDecision: deny`。
- Matcher 支持 `Edit|Write`、`mcp__.*` 等；`SessionStart` 的 matcher 能区分 `startup`/`resume`/`clear`/`compact`/`fork`。
- 子代理里的工具调用**同样触发**这些 hook，输入带 `agent_id` / `agent_type`——可以按 agent 身份差异化管控。

**最小可用实现**：`00_系统/agent/hooks/guard-vault.sh`，`PreToolUse` matcher `Edit|Write`：路径不在 `06_AI/`、`04_灵感/`、`02_项目/`、`03_人物/`、`00_系统/_changelog.md` 之内 → exit 2 并打印"越权：05_档案 只读、00_系统手册需红灯"。

### 2.4 Anthropic 官方长程 agent harness：progress 文件是刚需

[effective-harnesses-for-long-running-agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

- 双 agent 结构：**initializer agent** 首次运行建 `init.sh` + `claude-progress.txt`（记录历代 agent 干了什么）+ 一次初始 git commit；**coding agent** 每次只做增量并留下结构化更新。
- 原文关键结论：**"compaction 不够"**。即使 Opus 4.5 跑 Claude Agent SDK 循环，光靠压缩也会在实现中途耗尽上下文，把半成品和未记录状态丢给下一个 session。真正让新 session 快速进入状态的是 **`claude-progress.txt` + git history**。
- 两个失败模式：①想 one-shot，中途断气；②后来的 agent 看到"已有进展"就宣布完工。对策是 initializer 先写一份**穷举的功能清单**（claude.ai clone 例子写了 200+ 条），全部初始标 `failing`。
- 硬细节：清单**用 JSON 不用 Markdown**——原文说模型更不容易乱改 JSON；且只允许改 `passes` 字段，配"删改测试是不可接受的"这类强硬措辞。

**最小可用实现**：库里已有 `00_系统/_changelog.md`，它是"事后日志"；缺的是**事前进度板**。补 `00_系统/agent/_progress.md`（当前在做什么 / 上一步结论 / 下一步 / 阻塞）+ `00_系统/agent/_queue.json`（任务队列，只改 `status` 字段，schema 用 JSON Schema 锁死）。

### 2.5 其他"文件即协议"实践

| 项目 | URL | 做法 |
|---|---|---|
| **spec-kit** (140.2k★) | [github/spec-kit](https://github.com/github/spec-kit) | 命令流 `/speckit-constitution`（一次/项目）→ `/speckit-specify` → `plan` → `tasks` → `implement` → `converge`（每 feature）；产物落 `.specify/`，bug / assessment 报告也进 `.specify/bugs/`、`.specify/assessments/` |
| **BMAD-METHOD** (53.8k★) | [bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) | 多 agent 结构化讨论产出 brief / specification / architecture，再交给实现流程；核心主张是"**把没说的假设显式化并留成后续上下文**" |
| **agent-os** (5.5k★) | [buildermethods/agent-os](https://github.com/buildermethods/agent-os) | 把团队标准注入 codebase，先写 spec 再写码 |
| **agetor** (86★) | [alamops/agetor](https://github.com/alamops/agetor) | 本地 kanban + **每个 agent 一个 git worktree** 并行跑 Claude Code / Codex。小众但模式干净 |
| **claude-task-master** (28.2k★) | [eyaltoledano/claude-task-master](https://github.com/eyaltoledano/claude-task-master) | 可拖进多种编辑器的任务管理系统 |
| 索引类 | [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) (55.1k★)、[wshobson/agents](https://github.com/wshobson/agents) (40.2k★)、[VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) (25.5k★)、[e2b-dev/awesome-ai-agents](https://github.com/e2b-dev/awesome-ai-agents) (30.3k★) | 拆 subagent 的样本池。awesome 列表本身不构成最佳实践证据 |

## 3. 知识库卫生工具

| 工具 | URL | 能查什么 | 接入方式 |
|---|---|---|---|
| **markdownlint** (6.4k★) | [DavidAnson/markdownlint](https://github.com/DavidAnson/markdownlint) | 结构类规则：MD001 标题逐级递增、MD013 行长、MD025 单文档多 H1、MD041 首行须 H1、MD024 重复标题；支持 `markdownlint-disable-file` 逐文件豁免 | `.markdownlint.json`；CLI 用 [markdownlint-cli2](https://github.com/DavidAnson/markdownlint-cli2) (939★) |
| **Vale** (6.2k★) | [vale-cli/vale](https://github.com/vale-cli/vale)（原 errata-ai/vale，已 301 跳转） | **散文层面** lint：术语一致性、禁用词、语气；支持多标记语言，能**智能排除代码块**避免误报；规则可扩展成团队风格指南 | `.vale.ini` + 自定义 style；官方列出 GitLab / Homebrew / Linode / CockroachDB / Spotify 在用 |
| **lychee** (4.0k★) | [lycheeverse/lychee](https://github.com/lycheeverse/lychee) | 死链：Markdown / HTML / reStructuredText / 整站；也查邮箱地址 | Rust 异步流式；关键参数 `--exclude`、`--exclude-path`、`--exclude-all-private`、`--cache` + `--max-cache-age`（**避免每次全量重查**）、`--accept`（自定义可接受状态码如 `429`）、`--max-retries`、`--max-concurrency`；`.lycheeignore` 文件；有官方 GitHub Action |
| **markdown-link-check** (718★) | [tcort/markdown-link-check](https://github.com/tcort/markdown-link-check) | 只查链接存活 | Node CLI，轻量替代；能力弱于 lychee |
| **remark-lint** (1.0k★) | [remarkjs/remark-lint](https://github.com/remarkjs/remark-lint) | markdown 代码风格，插件式 | unified 生态 |
| **remark-lint-frontmatter-schema** (npm 3.15.4) | [JulianCataldo/remark-lint-frontmatter-schema](https://github.com/JulianCataldo/remark-lint-frontmatter-schema) | **frontmatter YAML 对照 JSON Schema 校验**——正是"type/status/audience/created 必填且枚举合法"要的东西 | remark 插件，底层 ajv；配 `.frontmatter-config.json` |
| **Obsidian Linter** (2.1k★) | [platers/obsidian-linter](https://github.com/platers/obsidian-linter) | 插件内批量规整：YAML 规则（`yaml-timestamp` 自动更新时间戳、`yaml-key-sort`、`dedupe-yaml-array-values`、`move-tags-to-yaml`、`insert-yaml-attributes`）、标题规则等 | Obsidian 社区插件；规则可独立开关，但**规则间会互相干扰**（官方明确点名 "Paragraph blank lines" × "Two Spaces Between Lines" 组合有意外结果） |
| **vault-inspector** (npm 1.0.0) | [rogerdigital/vault-inspector](https://github.com/rogerdigital/vault-inspector) | Obsidian vault 长期维护问题扫描 | npm/插件；**star 与采用度未查证，属低成熟度工具，建议先试跑再依赖** |
| **Obsidian 原生** | [Graph view 文档源](https://github.com/obsidianmd/obsidian-help/blob/master/en/Plugins/Graph%20view.md) | Graph view 的 Filters 里有 **"Existing files only"**（= 未解析链接 / 指向不存在笔记的链接）和 **"Orphans"**（= 无任何链接的笔记）两个开关。原文：笔记不需要存在就可以被链接，所以"Existing files only"能把图限制在真实存在的笔记上 | Obsidian 内置，零安装 |
| **pre-commit** (15.6k★) | [pre-commit/pre-commit](https://github.com/pre-commit/pre-commit) | 不是检查器，是**钩子框架**——把上面所有工具串成提交前闸门，多语言 | `.pre-commit-config.yaml` + `pre-commit install` |
| **gitleaks** (29.7k★) | [gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) | 密钥/密码/token 泄漏，扫 git 历史与文件 | 官方支持 pre-commit hook 与 GitHub Action，见 §4 |

**缺口（未查证到专门工具）**：独立的"**重复笔记检测**"（内容近似去重）没有找到 markdown/Obsidian 专用成熟工具。实践上要么用通用代码重复检测器，要么自己写——建议在 `vault-health-check.py` 里加一段基于标题+首段+wikilink 集合的指纹比对，不引外部依赖。

## 4. Git 治理

### 4.1 commit 规范 + CHANGELOG

- **[commitlint](https://github.com/conventional-changelog/commitlint)** (18.8k★)：配置文件必须是 `commitlint.config.{js,cjs,mjs,ts,cts,mts}` 之一；`extends: ['@commitlint/config-conventional']`（基于 Angular 约定）；本地配合 husky 在 commit 时 lint（官方有 [Local setup 指南](https://commitlint.js.org/guides/local-setup)）。
- **[git-cliff](https://github.com/orhun/git-cliff)** (12.3k★)：从 git 历史按 conventional commits 生成 changelog，支持 regex 自定义 parser 与模板；配置 `cliff.toml`，文档 [git-cliff.org/docs](https://git-cliff.org/docs)。
- **[release-please](https://github.com/googleapis/release-please)** (7.6k★)：按 conventionalcommits 规范**自动开 release PR**，合并后更新 `CHANGELOG.md` 与版本文件。内置多种 release-type（`node`、`python`、`go`、`simple` 等）——**markdown 库用 `simple`**。

配置样例（三件套）：

```toml
# cliff.toml
[changelog]
header = "# Changelog\n"
body = """
{% if version %}\
## [{{ version }}] - {{ timestamp | date(format="%Y-%m-%d") }}
{% else %}\
## [Unreleased]
{% endif %}\
{% for group, commits in commits | group_by(attribute="group") %}
### {{ group | upper_first }}
{% for c in commits %}- {{ c.message }} ({{ c.id | truncate(length=7, end="") }})
{% endfor %}{% endfor %}
"""
[git]
conventional_commits = true
filter_unconventional = true
commit_parsers = [
  { message = "^feat", group = "新增" },
  { message = "^fix", group = "修复" },
  { message = "^docs", group = "文档" },
  { message = "^chore|^refactor", group = "维护" },
]
```

```js
// commitlint.config.mjs
export default {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'scope-enum': [2, 'always',
      ['系统','方向','项目','人物','灵感','档案','AI']],
    'subject-max-length': [2, 'always', 72],
  },
};
```

**落地建议**：24帧库已有 `00_系统/_changelog.md` 手工追加制。建议**保留它作人读日志**，另用 git-cliff 从 commit 生成 `CHANGELOG.md` 作机器生成版——前者记"改了什么内容"，后者记"哪些 commit"。

### 4.2 大文件策略

[git-lfs/git-lfs](https://github.com/git-lfs/git-lfs) (14.5k★)。**建议**：媒体文件（放映数据原始表、海报、录音）走 LFS 或干脆不入库，`05_档案/媒体/` 只留索引 md。**此条未在库内实测，属建议而非已验证配置。**

### 4.3 防 agent 乱改

三层，从软到硬：

1. **`PreToolUse` hook**（§2.3）——唯一能在**写入发生前**拦截的机制。exit 2 阻断，stderr 回灌。
2. **pre-commit 闸门**：官方给出的 gitleaks 接入样例是 `.pre-commit-config.yaml` + `pre-commit install`，失败输出形如 `Detect hardcoded secrets.................................................Failed`；临时跳过用 `SKIP=gitleaks git commit`。同一份配置可挂 markdownlint / lychee / frontmatter schema。
3. **CI 校验 + CODEOWNERS**：[GitHub CODEOWNERS 文档](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)——文件放 `.github/`、根目录、或 `docs/` 三处之一（多个存在时按此顺序取第一个）；语法用 `@org/team` 或 `@user`；**配合 branch protection 强制 code owner approve 才能合并**；且 CODEOWNERS 必须在目标分支上才生效。

```
# .github/CODEOWNERS
00_系统/          @yuhong
AGENTS.md         @yuhong
00_系统/运营手册.md @yuhong
05_档案/          @yuhong
*                 @yuhong
```

**关键判断**：CODEOWNERS 只在**走 PR 流程**时有意义。如果日常是 agent 直接 commit 到 main，真正的防线只有 `PreToolUse` hook（前置）+ pre-commit（提交时）——这也是为什么 §2.3 的那个脚本优先级最高。

## 5. 上下文预算与渐进式披露

1. **渐进式披露是三层，官方定义如下**（[Agent Skills 文章](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)，逐字）：① skill 的 `name` + `description` 在启动时预载进 system prompt——"just enough information for Claude to know when each skill should be used without loading all of it into context"；② 判定相关后才读 `SKILL.md` 全文；③ 目录内附带文件（`reference.md` / `forms.md`）**只在实际需要时**才被读取。原文比喻：像一本先目录、再章节、最后附录的手册。
2. **硬性上限**：Claude Code 官方 [skills 文档](https://code.claude.com/docs/en/skills)明写 **"Keep `SKILL.md` under 500 lines"**，详细参考材料拆到单独文件。
3. **skill 一旦加载就常驻**：文档警告"Once a skill loads, its content stays in context across turns, so every line is a recurring token cost"——**每多一行，是每一轮都付一次**。这条比 500 行上限更重要。
4. **context rot 有实证**：Anthropic [context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) 明确"as the number of tokens in the context window increases, the model's ability to accurately recall information from that context decreases"，且**所有模型都有此特性**；attention budget 有限，transformer 是 n 个 token 的 n² 两两关系。
5. **目标函数**：不是塞更多，是"find the smallest possible set of high-signal tokens that maximize the likelihood of some desired outcome"。
6. **混合策略才是实操解**：Claude Code 本身就是混合体——`CLAUDE.md` 是"naively dropped into context up front"，而 glob / grep 让它 **just-in-time** 取文件，"effectively bypassing the issues of stale indexing"。**大型知识库的正解：小索引前置 + 检索优先，不要预建全量索引。**
7. **compaction 的正确调法**：先**最大化 recall**（确保摘要不漏关键信息），再迭代提 precision（删冗余）。最安全的轻量压缩是 **tool result clearing**——深埋在历史里的工具原始返回，agent 不需要再看第二遍。
8. **sub-agent 是上下文预算的杠杆**：子代理各自可烧几万 token，**只回传 1000–2000 token 的浓缩摘要**给主 agent。
9. **多 agent 的成本要算清**（[multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)）：token 用量**单独解释了 80% 的性能方差**；但 agent 比 chat 多用约 **4×** token，多 agent 系统约 **15×**。且只在**广度优先、可并行**的查询上划算——原文点名"多数编码任务的可并行部分比研究少"，共享上下文或强依赖的场景**不适合**。
10. **basic-memory 的"渐进式工具发现"**（见 §1）：工具的 read-only / destructive / idempotent 标签让 agent 不必靠试错摸清行为。适用于任何工具数超过 10 个的 agent。
11. **claude-mem 的 token 预算分层**（见 §1）：索引 50–100 token/条、全文 500–1000 token/条，**差一个数量级**。这是"先索引后全文"能省多少的实测参照。

## 6. 评审流水线

1. **[anthropics/claude-code issue #72206](https://github.com/anthropics/claude-code/issues/72206)**（2026-06-29，closed）——最完整的一份"作者盲区"分析与对策。核心论断：同一个 agent 自审会**确认自己的推理而不是试图证伪**；往上加 review 指令**无效**，因为"同一段有偏的上下文是**回忆**规则而不是**执行**规则"。三个结构性缺口 = 无独立性 / 只回忆不执行 / 无强制。四段对策：
   - **独立性** → 开一个**干净上下文的子代理**读 `git diff`，契约写明"You did not write this code. Be adversarial — try to falsify each claim"，并强制 **run-don't-read**（每个数据/数值/行为断言都要**跑**能证伪它的命令，看输出判断，绝不靠读代码）。
   - **执行** → 用 TodoWrite 把改动拆成"证伪命令"清单，每条产出 `CLAIM / CMD / ENV / OUT / VERDICT / STRENGTH` 证据日志。规则：**说不出能证伪它的命令，就是 UNVERIFIED，不是 verified**。每个 pass 要配 negative control（证明它真的会失败——不会失败的测试是假绿）。
   - **强制** → `PreToolUse` hook 卡在 `git commit`：有 staged 代码但没有近期 review 日志就提醒或阻断。"done" 从此不是自封的。
   - **复利** → 每条可泛化的发现回写进规则文件和 finding-class 目录，让下一轮 review 更强。作者给了两条经验律：**二阶 fold law**（每个修复会生出下一轮的发现，所以每次 fold 都要重审）；**收敛信号**（HIGH 级发现数量单调下降 = 在收敛；HIGH 降不下来 = 设计错了，不是代码错了）。
   - 该 issue 还附了一份从 ~200 次独立 review 挖出来的**领域无关 finding-class 分类**（parity/claim-falsification、determinism、cross-surface divergence、enforcement-vs-decoration、concurrency seam、money/grain、silent caps、runtime-substrate-only defects 等）——**可直接当 24帧库文档评审的检查表改**。
2. **[Steve Kinney · Using Codex for a Second Opinion in Claude Code](https://stevekinney.com/writing/codex-as-a-second-opinion)**（2026-06-04）——**不同模型家族互审**的实操。关键概念 "**correlated blind spots**"：让一个模型审自己的推理，等于从产生该推理的同一分布里采样，它自信地错时，评审也朝同一方向自信地错。他给 Codex 写 `codex-review.sh` 包一层而不是直接调 MCP：因为要自己控制 **timeout、失败码、沙箱边界**。最重要的一段警告：**advisor 必须只做分析不采取行动**——"I want analysis, not action"；真正的失败模式不是"Codex 给错答案"，而是"**outsourcing the judgment**"（把判断权外包出去）。
3. **[addyosmani/adverse](https://github.com/addyosmani/adverse)** (60★)——可跑的多 agent 对抗评审实现，同时是 CLI 和 Claude Code Skill。流程：**3 个角色并行审**（auditor / adversary / pragmatist）→ 第 2 轮**交叉质证**（各自对别人的发现做 validated / challenged / 新增）→ 合成。输出带 `SHIP-WITH-CAVEATS (2/3 ship, 1/3 block)` 这类**分裂裁决**，并单列 **"Cross-validated findings"（多个 reviewer 独立报出的同一问题）**。这个"交叉验证"分区很值得抄——**多评审独立命中 = 高置信度信号**。
4. **[Tree-of-Concerns](https://arxiv.org/abs/2608.20777)**（arXiv 2608.20777，Sahil Mishra 等）——层级多 agent 辩论抽取论文中**未言明的局限**。每个 skeptic persona 走一个 category-specific 分析视角，作为并行 debate tree 做**有证据支撑的结构化论证**。适用于"评审别人写的方案时，专门找它没说的地方"。
5. **[Anthropic multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)**——生产系统里的评审/校验分工：lead agent 汇总后交给独立的 **CitationAgent** 处理引用归属，"ensures all claims are properly attributed to their sources"。**把"引用校验"拆成独立 agent 而不是让主 agent 自查**，这是可复用的一条。
6. **"Who Reviews the Reviewer?"**（*Systems Research and Behavioral Science*, Wiley, [doi 10.1002/sres.70163](https://onlinelibrary.wiley.com/doi/10.1002/sres.70163)）——多 agent + meta-review 合成的编辑peer review 架构。**仅通过搜索结果确认存在，未抓取全文，"meta-review 合成"的具体机制未查证。**

**对 24帧库的最小落地**：写稿→发 `review-adversary`（干净上下文，读 diff，run-don't-read 校准人名/片名/日期）→ 发 `review-perspective`（读者/合作方视角）→ 两个结果里**独立命中同一问题的进"必改"**，只有一个 reviewer 提的进"待议"。评审 agent 全部只读（`tools: Read, Grep, Glob`），改稿权留在写稿 agent 和人类手上。
