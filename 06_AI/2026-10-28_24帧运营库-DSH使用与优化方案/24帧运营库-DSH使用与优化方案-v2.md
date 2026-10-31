---
type: draft
name: 24帧运营库-DSH使用与优化方案-v2
status: review
editable: true
audience: both
created: 2026-10-28
updated: 2026-10-28
summary: 对 24 帧运营库的全面复核与 DSH 原生优化方案，含 24 张执行卡与可抄模板
source: ai-generated
tags: [基建, DSH, agent协作, 方案]
---

# 24帧运营库 · DSH 使用与优化方案 v2

> 复核日期：2026-10-28
> 适用环境：DSH 0.2.1-rc.3，Obsidian 核心插件（Bases / Properties），macOS
> 配套文件：[[附件A-现状复核与执行队列]]、[[附件B-模板与脚本]]、[[附件C-脚本源码]]
> 上一版：[[24帧运营库-DSH优化方案]]（2026-10-06，未执行）

---

## 0. 给 agent 的读取协议

这份方案写给两种读者：宇航员做决策，agent 做执行。如果你是 agent，按下面的顺序用，不要从头到尾通读。

1. 先读 §1「结论」和 [[附件A-现状复核与执行队列]] 的任务卡索引，知道自己能领哪张卡。
2. 领卡前读卡片的 `Depends`、`Files`、`Done` 三栏。依赖没完成就不领。
3. 只改卡片 `Files` 里列出的文件。需要越界，停下来在报告里说明，不要自行扩大范围。
4. 执行完必须跑卡片里的 `Verify` 命令，把原始输出贴进报告。没有输出等于没做。
5. 卡片要写脚本时，先翻 [[附件C-脚本源码]] 对应小节，复制已实跑的版本；不要自己重写。模板文件（AGENTS/schema/skill/页面）在 [[附件B-模板与脚本]]。
6. 按 `00_系统/_schema.md` 的格式记 `_changelog.md`。
7. 报告固定五段：`TASK / CHANGED / VERIFY / RISK / NEXT`。不要写过程叙事。

三条禁令，优先级高于任何任务卡：

- 不执行 P0-1（公开仓库处置）。那是宇航员本人的账号操作，agent 只提醒，不代做。
- 不批量改写 `05_档案/`。历史存档只读，唯一允许的写操作是按归档规范新建会议文件。
- 不 commit、不 push。当前工作区有大量宇航员未提交的改动（复核时 81 项），`origin` 仍指向公开仓库。

---

## 1. 结论

### 1.1 五条判断

**第一，库的内容够用，坏在接口层。** 561 篇内容 markdown 里，320 篇是历史档案（公众号原文 302 篇），真正需要 agent 持续维护的 241 篇。另有 302 份 `.github-pages` 生成副本和 30 份工具依赖文档，不纳入扫描。问题不在数量，在于这 241 篇没有一套能执行的字段规则、没有可用的索引、没有写入校验。agent 每次都在猜。

**第二，规范有四个版本，互相打架。** `运营手册.md` 只有 102 行，正文引用的 §4/§6/§8/§10/§11/§13/§15 全部不存在；`归档操作规范.md` 让会议存进 `02_归档文件/`，手册说只进 `05_档案/会议存档/`；`00_系统/agent/录音会议存档SOP.md` 又抄了一遍旧规则；两个 skill 各自再写一套。agent 读到哪份，就按哪份做。

**第三，看板和索引是死的。** 全库 12 个活跃页用了 Dataview，Obsidian 没装 Dataview 插件，所有查询块渲染为空白。`HOME.md` 四张表全空，`_index.md` 只是目录树，没有一条「这是哪个项目、现在什么状态」的摘要。

**第四，隐私是今天必须处理的事。** `github.com/yhy2049/wechat-articles` 是公开仓库，默认分支 `main` 里有 16 篇会议逐字稿，包括资金分工、团队关系、个人访谈；此外 20 个人物页有 16 个标了 `audience: public`，15 篇会议有 10 篇标了 public；全库共 61 个 `public` 页，只有 0 个带 `public_approved`。`public` 现在被当成「不保密」在用，实际语义应该是「已批准对外」。

**第五，v1 方案的 11 个 P0，落地 0 个。** 2026-10-06 的方案设计是完整的，但它是文档，不是执行队列：没有任务卡、没有验收命令、没有依赖顺序。这次改成 24 张卡，每张卡带文件清单、验证命令和回滚方式，先做 7 件小事。

### 1.2 最该做的七件事

| 顺序 | 任务 | 谁做 | 耗时 | 解决什么 |
|---|---|---|---|---|
| 1 | P0-1 关闭公开仓库 | 宇航员本人 | 10 分钟 | 停止 16 篇会议逐字稿继续公开 |
| 2 | P0-7 修正全局 AGENTS 路径 | agent | 5 分钟 | 每个会话开头不再拿到错误路径 |
| 3 | P0-3 落盘 `_schema.md` | agent | 1 小时 | 字段有唯一合法值 |
| 4 | P0-2 重写根 `AGENTS.md` | agent | 1 小时 | agent 有一页可执行的契约 |
| 5 | P0-4 规范三合一 | agent | 1.5 小时 | 会议、人物、任务的规则只剩一份 |
| 6 | P0-5 skill 迁入项目并瘦身 | agent | 1 小时 | 每次少烧 1 万 token，少学旧规则 |
| 7 | P0-6 隐私元数据清理 | agent | 1 小时 | `public` 不再等于「内部资料」 |

这七件做完，库从「靠 agent 自觉」变成「有契约、有拦截、有索引」。后面的 P1/P2 才有意义。

### 1.3 本方案与 v1 的关系

v1 是设计稿，v2 是施工图。v1 的 `_schema.md` 草案、嵌套 AGENTS 草案、headless 方案仍然有效，本方案直接引用并修正了三处：方向枚举从 5 个确认（俱乐部已停，归入 `05_档案`）、`summary` 增为必填、`public` 增加审批字段。v1 主文件在 P3 阶段标记 `superseded`，附件保留作参考，不删。

---

## 2. 现状复核

> 快照时间 2026-10-28 03:30（复核末期重跑）。复核期间库内有并行改动：`05_档案/俱乐部/`、`05_档案/写作DNA/北瓦放映/`、`06_AI/2026-09-27_生日快乐文案/` 被移出，`05_档案/合作资源库/` 新增 2 页。以下数字是 03:30 的脚本实测值，会随库继续变化；执行任务卡时一律以 `vault-lint.py` / `vault-metrics.py` 的实时输出为准，不要拿本文数字当验收标准。

### 2.1 规模与构成

| 指标 | 数值 | 说明 |
|---|---:|---|
| 内容 markdown | 561 | 241 活跃 + 320 档案；另有 302 份站点副本、30 份工具文档不纳入扫描 |
| 有 frontmatter | 232 | 41.4%；活跃页 232/241 |
| 无 frontmatter | 329 | 58.6%；320 篇档案 + 9 篇活跃页 |
| 有 summary | 4 | 1.7%；索引因此只能标「待补摘要」 |
| 项目页 | 11 | `02_项目/` 下 11 个项目主文件 |
| 人物页 | 20 | `03_人物/` |
| 方向页 | 5 | AI影像、宣发平台、影视创作、策展人、观影团 |
| 灵感 | 11 | `04_灵感/AI加工区` |
| 会议存档 | 15 | `05_档案/会议存档/` |
| 06_AI 任务目录 | 28 | 另有 1 个散落根目录的文件 |
| 库体积 | 217 MB | `.git` 98 MB + 内容与工具 119 MB，见 §2.8 |

### 2.2 Schema 漂移

| 字段 | 出现过的值 | 合法值 | 典型非法值 |
|---|---:|---:|---|
| `type` | 20 | 10 | `项目会议`、`非正式饭局谈话`、`direction-reference`、`external-submission`、`brand-resource`、`project_plan`、`research`、`影评`、`公众号文章`、`guide`、`analysis`、`游戏推荐` |
| `status` | 9 | 4 | `active`、`exploring`、`completed`、`进行中`、`选定版` |
| `audience` | 5 | 4 | `agent+human` |
| `direction` | 12 种写法 | 5 | `[[AI影像]]` 与 `AI影像` 并存；`[[策展人]]、[[观影团]]` 塞进一个字段 |
| 活跃页缺 `type` | 12 篇 | 0 | 3 篇有 fm 无 type；9 篇无 fm（其中 8 篇在 `06_AI/`） |
| 活跃页缺 `status` | 6 篇 | 0 | — |
| 活跃页缺 `audience` | 15 篇 | 0 | — |

后果很直接：任何跨文件查询都不可信。想知道「观影团方向有哪些进行中的项目」，得同时匹配 `观影团`、`[[观影团]]`、`[[观影团]]` 三种写法，还要把 `status: active` 和 `progress: 进行中` 都算上。agent 每次都要重新猜规则，猜错还没有东西拦它。

### 2.3 规范冲突

| 规则 | `运营手册.md` | `归档操作规范.md` | `录音会议存档SOP.md` | 实际文件 |
|---|---|---|---|---|
| 会议存哪 | `05_档案/会议存档/` | 项目目录 `02_归档文件/` | 项目目录 `02_归档文件/` | `05_档案/会议存档/` |
| 人物存哪 | `03_人物/` | `04_人物/` | 未提 | `03_人物/` |
| 任务怎么存 | 无 `03_任务`，任务在项目内 | 建 `type: task` 任务文件 | 建 `type: task` 任务文件 | 5 种写法并存，无 `type: task` |
| 手册章节 | 只有 §0、§1 | 引用 §15 | 引用 §8/§13 | §4/§6/§8/§10/§11/§13/§15 全缺 |
| 会议字段 | 未定义 | 定义了 `title/direction/related_people` | 未定义 | 实际是 `date/participants/related_projects`，缺 `title/direction` |

`运营手册.md` 开头写「不读不动」，但被要求读的那份文件本身不完整。这比没有规范更糟：agent 会以为自己已经遵守了规范。

### 2.4 入口和看板失效

- `HOME.md` 1,282 字节，4 个 Dataview 查询块，全部无输出。
- 全库 12 个活跃页含 ` ```dataview ` 代码块；`.obsidian/plugins/` 不存在，社区插件一个没装。
- Obsidian 核心插件里 `bases: true`，Bases 可用，但没有任何 `.base` 文件。
- `00_系统/_index.md` 1,763 字节，是目录树，不是内容目录：没有摘要、没有状态、没有更新时间。
- 根 `AGENTS.md` 2,695 字节、55 行，要求 agent 开工前读三份规范，其中两份自相矛盾、一份缺章节。

### 2.5 导航失效

| 指标 | 数值 | 含义 |
|---|---:|---|
| 孤儿页（无入链） | 92 | 多数是项目参考文档，只能靠搜索找到 |
| 无 `## 关联` 段 | 69 | 人点不开，agent 也串不起来 |
| 断裂双链 | 42 处（15 个目标） | 27 处来自新建的 `05_档案/合作资源库/` 尚未建子页；4 处 `_schema.md` 未建；3 处 skill 名；其余 8 处是旧结构残留 |
| 重名文件（活跃页） | 3 | `群聊对齐信息`、`主文件`、`公众号版` |
| `status: review` 超 7 天 | 7 | 最早的挂了 5 个月 |
| 项目页任务写法 | 5 种 | `## 待办`、`- [ ]`、`next_action`、纯正文、什么都没有 |

11 个项目页里，只有 3 个有 `## 待办` 段，5 个用 frontmatter `next_action`，2 个完全没有任务入口。agent 想知道「这个项目下一步做什么」，得读完整篇正文再自己总结。

### 2.6 隐私暴露

**公开仓库。** `yhy2049/wechat-articles` 当前 `private: false`、`visibility: public`、默认分支 `main`、984 个文件、最后推送 2026-10-21。公开文件里包括：

- `05_档案/会议存档/` 16 篇逐字稿，含《宇航员与Peter电话-资金分工与团队关系》《赞助分工与Peter定位》《第二部短片资金问题讨论》。
- `05_档案/写作DNA/` 40 篇。
- `05_档案/媒体/` 14 篇、`05_档案/俱乐部/` 5 篇、`05_档案/放映数据/` 4 篇。

**本地元数据。**

| 对象 | 总数 | `audience: public` | 问题 |
|---|---:|---:|---|
| 人物页 | 20 | 16 | 含「在群里汇报工作时只提自己」「从资方妈妈处额外磨到1万元」这类内部判断 |
| 会议页 | 15 | 10 | 含资金分成、团队关系、个人访谈；另有 2 篇缺 `audience` |
| 全库活跃页 | 241 | 61 | 0 篇带 `public_approved`；`public` 被当成「不保密」 |

**语义错位。** 现在的 `public` 实际含义是「不保密」；一旦有人按这个字段做对外发布或分享，内部判断会直接出去。本方案把 `public` 定义为「已批准对外」，并要求 `public_approved` 与 `redacted` 两个字段同时存在。

**本地风险。** `origin` 仍指向公开仓库；本地 `origin/main` 保存着完整旧库。任何人执行 `git push` 都会把当前内容再次公开。

### 2.7 上下文成本

| 加载项 | 体积 | 估算 token | 何时加载 | 问题 |
|---|---:|---:|---|---|
| `~/.dsh/AGENTS.md` | 8.4 KB | ~2.5k | 每个会话 | 第 43、51 行路径错误 |
| 库根 `AGENTS.md` | 2.7 KB | ~0.8k | 进入库 | 太薄，未含字段和任务语法 |
| `24frames-vault` skill | 44.9 KB / 1,052 行 | ~11k–15k | 每次调用 | 旧路径、旧目录、旧 frontmatter 建议 |
| `vault-archiving` skill | 7.0 KB / 162 行 | ~2k | 每次归档 | 用「known pitfall」掩盖规范冲突 |
| 170 个 skill 描述 | — | ~8k | 每个请求 | 大量与本库无关 |
| astronaut preset 启动序列 | 9 步 | — | 每次启动 | 引用多个不存在的 memory 文件 |

一个归档任务，光「读规则」就可能花掉 2 万 token，其中一半在教 agent 过时的路径。上下文越长，模型对真正任务的注意力越差，这是 context rot 的直接来源。

### 2.8 工具与体积

| 目录/文件 | 体积 | 性质 | 建议 |
|---|---:|---|---|
| `.git` | 98 MB | 历史（含公开仓库全部内容） | 见 P1-9 / P2-6 |
| `node_modules`（公众号存档 `_skill` 下） | 19 MB | 工具依赖，含 30 份 md 文档 | 移出库，加 `.gitignore` |
| `.hermes` | 8.9 MB | agent 运行时状态 | 移出库 |
| `05_档案/公众号存档/.github-pages` | 7.0 MB | 站点镜像，302 份文章副本 | 移出库，归站点仓库 |
| 公众号文章重复 | 302 篇 | 年目录与镜像各一份 | 保留年目录为唯一版本 |

其他工具事实：

- 没有任何 hooks 配置；`~/.dsh/profiles/headless/cordis.patch.yml` 是空数组 `[]`，headless 没有模型路由。
- 健康检查靠手动跑，且只查格式，不查枚举、隐私、任务语法；管道到 `tail` 时退出码会被吞掉。
- `_changelog.md` 90 KB / 1,291 行 / 140 条，12 条格式不合规，无分卷。
- `06_AI/` 根目录有 1 个散落文件 `关于项目陈述会，和我们正在做的事.md`。
- 公众号 302 篇原文全部没有 frontmatter；`.github-pages/articles/` 还有 302 份同名副本，两套目录只能靠文件名对应。

### 2.9 v1 执行审计

| v1 项 | 内容 | 当前证据 | 状态 |
|---|---|---|---|
| P0-1 | 关闭公开仓库 | `private: false` | 未做 |
| P0-2 | `_schema.md` | 文件不存在 | 未做 |
| P0-3 | 重写根 AGENTS | 仍为 2.7 KB 旧版 | 未做 |
| P0-4 | 规范合一 | 手册 102 行，两份 SOP 冲突 | 未做 |
| P0-5 | skill 迁入库内 | 仍只有 `~/.agents/skills` 全局副本 | 未做 |
| P0-6 | 清死 Dataview | 12 个活跃页仍有查询块 | 未做 |
| P0-7 | 索引目录 | `_index.md` 仍为目录树 | 未做 |
| P0-8 | changelog 分卷 | 91 KB 未分卷 | 未做 |
| P0-9 | 全局路径修正 | 第 43/51 行仍是 `~/Documents/OH-WorkSpace` | 未做 |
| P0-10 | headless 可用 | patch 为空 | 未做 |
| P0-11 | 会议隐私 | 10 篇 public | 未做 |

**0/11。** 原因不是方案不好，是方案没有落到「谁、改哪个文件、跑什么命令、怎么算完成」。v2 的任务卡就是为了补这一层。

### 2.10 根因

1. **没有唯一 schema。** 字段规则散在手册、SOP、skill、历史文件里，每处都只写一部分，且互相矛盾。agent 没有可执行的判断依据。
2. **没有写入拦截。** 所有规则都是「应该」，没有一条能在写错时让操作失败。agent 会模仿最近的例子，而最近的例子本身不合规。
3. **没有复利回路。** ingest 和 query 都在发生，write-back 和 lint 没有。库在长大，但没有变聪明：答案留在聊天记录里，矛盾留在页面上，索引永远落后。

---

## 3. 外部方法与本库的映射

### 3.1 卡帕西的 LLM Wiki

原文把方法拆成三层三操作，和本库的匹配度很高。关键句：

> "the wiki is a persistent, compounding artifact"——wiki 是持续复利的产物，不是每次查询重新拼装的临时答案。
>
> "good answers can be filed back into the wiki as new pages"——好答案要回写成页面，不能消失在聊天记录里。
>
> `index.md` 是内容目录，每页一行摘要；`log.md` 是追加式时间线，条目用 `## [日期] 类型 | 标题`。

| LLM Wiki 要素 | 本库现状 | 结论 |
|---|---|---|
| Raw 层不可变 | `05_档案/` 事实上只读，但没有明文规则 | 已有 70%，补规则与守卫 |
| Wiki 层由 LLM 维护 | 项目/人物/方向页在维护，但字段自由 | 已有 60%，补 schema |
| Schema 层（AGENTS.md） | 根 AGENTS 只有 55 行，无字段规则 | 缺，P0-2/P0-3 |
| Ingest | 归档流程存在，但两份 SOP 冲突 | 有流程，缺唯一版本 |
| Query | 靠 grep 和记忆 | 缺索引与检索 |
| Lint | 有手动脚本，不查 schema/隐私 | 缺自动 lint |
| index.md | 目录树，无摘要 | 缺 |
| log.md | `_changelog.md` 格式不稳 | 半有 |
| 答案回写 | 基本没有 | 缺 |

**判断：本库已经是一个 LLM Wiki 的雏形，完成度约 70%。缺的三块正是 schema、lint、write-back。**

### 3.2 AGENTS.md 标准

AGENTS.md 的定位是「给 agent 的 README」，不是人类文档。官方站点给的两条关键规则：

> "Think of AGENTS.md as a README for agents."
>
> "The closest AGENTS.md to the edited file wins."——离被改文件最近的那份优先。

对本库的用法：

- 根 `AGENTS.md` 只放全局契约：四层边界、硬规则、任务语法、红灯清单。目标 6–8 KB、150 行以内。
- 局部规则放嵌套 `AGENTS.md`：`02_项目/` 管项目页结构，`03_人物/` 管隐私，`05_档案/` 管只读，`06_AI/` 管草稿生命周期。DSH 在读写更深目录时自动追加，不占无关任务的预算。
- 规范细节放 `_schema.md` 和 `运营手册.md`，根 AGENTS 只给链接和读取条件。这样规则只有一份，AGENTS 不会随规则增长而膨胀。

### 3.3 Agent Skills 的渐进披露

Anthropic 的 skill 机制是渐进披露：启动时只加载 `name` 和 `description`，正文在调用时才读；官方建议 `SKILL.md` 控制在 500 行以内，入口文件越短，遵循度越高。

本库的做法正好相反：`24frames-vault` 一个文件 1,052 行、44.9 KB，把目录结构、字段表、工作流、历史坑全塞在入口里。每次调用都全量加载，旧规则和新规则一起进上下文。

改造原则：

- `SKILL.md` 只做路由：什么任务、读哪三份文件、按什么顺序、什么时候停。目标 150 行以内。
- 细节拆到 `references/`：`schema.md`、`archiving.md`、`writing.md`，按需读。
- 一个任务只加载一个 skill；不要在一次会话里同时调用多个写库 skill。

### 3.4 多 agent 治理

多 agent 的价值在并行读，不在并行写。可查的实践共识是：多 agent 的 token 成本约为单 agent 的 15 倍，收益只在「可并行的广度任务」上成立；共享写入会带来覆盖和冲突。

本库的规则：

- **单写者。** 同一时间只有一个 agent 能写库。其他 agent 只读，结果交回写者。
- **并行只用于研究。** 多个子代理分别查资料、读历史文章、核对外部信息，最后汇总成一份草稿。
- **交接用固定格式。** `TASK / CONTEXT / DONE / EVIDENCE / NEXT`，不写过程。
- **每张任务卡只有一个 owner。** 需要协作时拆卡，不共享一张卡。

### 3.5 检索

Karpathy 的建议是先用 `index.md`，规模大了再上搜索；他推荐 qmd（本地 BM25 + 向量 + 重排）。本库 561 篇内容页，索引足够导航，但「谁在哪次会上说过某句话」需要全文检索。

采用顺序：

1. `_index.md` 摘要目录（P1-1）解决「找页面」。
2. SQLite FTS5 + CJK bigram（P2-1）解决「找句子」，零外部依赖。**不要直接用 `tokenize='trigram'`**：实测 FTS5 trigram 对少于 3 个 Unicode 字符的查询零命中，「电影」「放映」都搜不到；脚本把中文切成重叠 bigram 再入 `unicode61`，2 字词可命中，英文按整词。
3. qmd 作为可选升级，等页面超过 2,000 篇或需要语义相似度再引入。qmd 的 BM25 硬编码 porter 分词器，中文整句会变成一个 token（issue #617），引入前必须过 20 条中文查询验收。

### 3.6 不照搬的东西

- **不装 Dataview。** 核心插件已有 Bases，静态生成对 agent 更稳；再装插件会增加环境依赖。
- **不上向量数据库。** 561 篇的规模用 FTS5 足够，向量检索的维护成本高于收益。
- **不做全自动发布。** 公众号、小红书发布前必须过隐私检查与人工确认。
- **不做多 agent 并行写库。** 冲突成本远高于速度收益。
- **不批量重写历史存档。** 旧文件按「动到才改」迁移，避免一次性引入大量断链。

---

## 4. 目标架构

### 4.1 四层

```
人类（Obsidian）                     agent（DSH）
      │ 读                                 │ 读
      ▼                                    ▼
  HOME.md  ◄── 生成 ──  _index.md  ◄── frontmatter
      │                                    │
      ├──────────── wiki 层 ───────────────┤
      │  01_方向  02_项目  03_人物  04_灵感 │  agent 写
      │  有 schema、有摘要、有 ## 关联      │
      ├──────────── raw 层 ────────────────┤
      │  05_档案（会议/公众号/媒体/数据）   │  只读，只能新建会议
      ├──────────── draft 层 ──────────────┤
      │  06_AI/YYYY-MM-DD_主题/             │  agent 写，不进 wiki
      └──────────── schema 层 ─────────────┘
         AGENTS.md / _schema.md / 运营手册 / 归档规范
                        │
                  tooling：00_系统/agent
                  lint / index / home / search / hooks / launchd
```

一句话：**raw 存事实，wiki 存结论，draft 存过程，schema 存规则，tooling 存自动化。**

### 4.2 单一事实源矩阵

| 规则 | 唯一出处 | 谁引用 |
|---|---|---|
| 字段枚举、必填、命名 | `00_系统/_schema.md` | AGENTS、手册、SOP、lint、模板 |
| 目录边界、红灯、任务语法 | `AGENTS.md` | 所有 agent |
| 归档六步与验收 | `00_系统/归档操作规范.md` | `vault-archiving` skill |
| 日常流程与分工 | `00_系统/运营手册.md` | 人、agent |
| 页面导航 | `00_系统/_index.md`（生成） | 人、agent |
| 历史操作 | `00_系统/_changelog.md`（追加） | 人、审计 |
| 项目/人物/方向事实 | 各自页面 | 所有查询 |
| 决策风格与表达偏好 | astronaut preset `persona/` | 写作者 |
| 操作步骤 | `.agents/skills/*/SKILL.md` | 执行者 |

**一条规则只写一次。** 其他文件只能链接，不能复述。发现两处写了同一条规则，删一处并记 changelog。

### 4.3 目标目录

```
24帧运营库/
├── AGENTS.md                     # 6–8 KB，150 行以内，全局契约
├── HOME.md                       # 生成，今日看板
├── _schema.md                    # 唯一字段规则
├── .agents/skills/               # 项目级 skill（rank 200）
│   ├── 24frames-vault/SKILL.md   # 路由，≤150 行
│   └── vault-archiving/SKILL.md  # 路由，≤120 行
├── .claude/                      # 可选 hooks
│   ├── hooks.json
│   └── hooks/*.sh
├── 00_系统/
│   ├── 运营手册.md               # 流程，不再写枚举
│   ├── 归档操作规范.md           # 唯一归档 SOP
│   ├── _index.md                 # 生成，内容目录
│   ├── _changelog.md             # 最近 100 条 + 分卷链接
│   ├── _changelog/2026.md        # 分卷
│   └── agent/
│       ├── AGENTS.md             # 本目录规则
│       ├── vault-lint.py
│       ├── vault-index.py
│       ├── vault-home.py
│       ├── vault-search.py
│       ├── vault-metrics.py
│       ├── .vault-search.db      # FTS 索引，gitignore
│       ├── logs/                 # 运行日志，gitignore
│       └── .vault-lint-baseline.json
├── 01_方向/                      # 5 个方向，各一页
├── 02_项目/                      # 11 个项目
│   └── AGENTS.md                 # 项目页结构与任务语法
├── 03_人物/                      # 20 个人物
│   └── AGENTS.md                 # 隐私默认 owner
├── 04_灵感/                      # 捕获/加工/知识库/品牌策略
├── 05_档案/                      # raw，只读
│   ├── AGENTS.md
│   ├── 会议存档/
│   ├── 公众号存档/
│   ├── 媒体/
│   └── 放映数据/
└── 06_AI/                        # 草稿
    └── AGENTS.md                 # 每个任务一个日期目录
```

`00_系统/agent/` 下五个脚本的逐字源码在 [[附件C-脚本源码]]，已对本库实跑，不要另起炉灶重写。

需要移动的东西：

| 从 | 到 | 原因 |
|---|---|---|
| `~/.agents/skills/24frames-vault/` | 库内 `.agents/skills/24frames-vault/` | 项目级优先，版本随库走 |
| `~/.agents/skills/vault-archiving/` | 库内 `.agents/skills/vault-archiving/` | 同上 |
| `05_档案/公众号存档/_skill/` 及 `node_modules/` | `~/.agents/tools/wechat-archive/` | 工具不進知识库 |
| `05_档案/公众号存档/.github-pages/` | 站点仓库（库外） | 发布物与内容分离 |
| `.hermes/` | `~/Library/Application Support/24frames/hermes/` 或删除 | 运行时状态不进库 |
| `00_系统/agent/录音会议存档SOP.md` | 合并进 `归档操作规范.md` 后删除 | 消除第三份规则 |
| 大于 10 MB 的音视频 | 库外媒体盘，库内留 `媒体索引.md` | git 不适合存大文件 |

### 4.4 文件契约

所有新建文件必须满足 `_schema.md`。最小公共字段：

```yaml
type: project            # 10 个合法值之一
name: 苏宁影城路演合作
status: final            # draft / review / final / archive
audience: both           # owner / agent / both / public
editable: true
created: 2026-10-28
updated: 2026-10-28
summary: 与苏宁影城的路演合作，探索商业片分账模式
```

`summary` 是新增强制字段，一句话，40 字以内，供 `_index.md` 和 HOME 使用。没有摘要的页面不进索引，等于不存在。

### 4.5 任务语法

任务不再建独立文件，写在项目页。项目页 frontmatter 只放「下一步」：

```yaml
next_action: 跟苏宁确认 11 月排期与分账比例
next_action_due: 2026-11-02
waiting_for: 苏宁影城回复排期
```

正文 `## 待办` 用固定行格式，一行一个任务：

```markdown
## 待办

- [ ] T-03 跟苏宁确认 11 月排期 ｜ 宇航员 ｜ 2026-11-02 ｜ 进行中
- [ ] T-04 补一份分账测算表 ｜ 宇航员 ｜ 2026-11-05 ｜ 待办
- [x] T-02 拿到场地报价 ｜ 宇航员 ｜ 2026-10-20 ｜ 已完成
```

格式固定为：`- [状态] 任务ID 动作 ｜ 负责人 ｜ 截止日 ｜ 状态`。任务 ID 在项目内唯一，从 `T-01` 起。完成的写 `[x]`，状态写「已完成」。

规则：

- 一个项目最多 7 条未完成任务，超出拆阶段。
- 每周一清理已完成任务，移到 `## 已完成` 或删除，保留最近 10 条。
- 会议里产生的待办，落到对应项目页，会议页只放链接。
- `next_action` 必须与 `## 待办` 第一条一致；不一致时以 `## 待办` 为准。

### 4.6 索引与日志

**`_index.md` 由脚本生成，agent 不手写。** 结构：

```markdown
## 项目（11）

- [[苏宁影城路演合作]] — 与苏宁影城的路演合作，探索商业片分账模式 ｜ 进行中 ｜ 2026-10-28

## 人物（20）

- [[Peter]] — 资方对接人，参与长片资金与团队协调 ｜ external ｜ 2026-10-20
```

生成器读 frontmatter 的 `summary`、`progress`、`updated`，按目录分组。文件头写生成时间与条目数；正文用 `<!-- AUTO:INDEX:START -->` / `<!-- AUTO:INDEX:END -->` 包住。agent 只读，脚本重写。

**`_changelog.md` 是唯一日志。** 格式：

```markdown
## [2026-10-28 01:14] 方案 | 24帧运营库-DSH使用与优化方案-v2
```

超过 500 KB 或 2,000 行时，把旧条目移到 `00_系统/_changelog/YYYY.md`，主文件保留最近 100 条和分卷链接。分卷只追加，不改写。

### 4.7 隐私语义

`audience` 四值，含义固定：

| 值 | 含义 | 默认用于 |
|---|---|---|
| `owner` | 只给宇航员 | 人物页、会议页、资金/关系类内容 |
| `agent` | agent 工作记忆 | `00_系统/agent/`、草稿 |
| `both` | 宇航员和 agent 都看 | 项目页、方向页、大多数 wiki 页 |
| `public` | **已批准对外**，可直接给合作方或发布 | 对外计划书、媒体介绍 |

`public` 必须同时满足：

```yaml
audience: public
public_approved: 2026-10-28   # 宇航员批准日期
redacted: true                # 已移除内部人名、金额、关系判断
```

缺任一字段，lint 报错。人物页和会议页默认 `owner`，改成 `public` 需要宇航员明确同意并记 changelog。

### 4.8 查询回写

每次回答一个非平凡问题，结果要落到页面，否则这次查询对库没有贡献。去向：

| 问题类型 | 回写到 |
|---|---|
| 项目决策、取舍、理由 | 项目页 `## 决策记录` |
| 人物行为、关系变化 | 人物页 `## 行为记录` |
| 可复用的方法、行业知识 | `04_灵感/知识库/` 新页或更新 |
| 一次性研究、外部资料 | `06_AI/YYYY-MM-DD_主题/` |
| 规范变更 | `_schema.md` / `运营手册.md` + changelog |

不要求每次问答都建页。判断标准：三个月后还会有人问同样的问题，就回写。

### 4.9 记忆边界

| 系统 | 存什么 | 不存什么 |
|---|---|---|
| 运营库 | 业务事实、项目状态、人物关系、决策记录 | agent 性格、prompt、操作步骤 |
| astronaut preset | 决策风格、表达偏好、公理、争议日志 | 项目细节、会议内容 |
| skills | 操作步骤、路由、检查清单 | 字段枚举、业务事实 |
| changelog | 谁在什么时候改了什么 | 结论、分析 |

四者不复制同一内容。preset 需要业务事实时读库，不往 persona 里抄。

---

## 5. DSH 下的使用方式

### 5.1 加载链与上下文预算

| 层 | 文件 | 何时加载 | 目标体积 |
|---|---|---|---:|
| 全局 | `~/.dsh/AGENTS.md` | 每个会话 | ≤6 KB |
| 项目 | `24帧运营库/AGENTS.md` | 进入库 | ≤8 KB |
| 目录 | `02_项目/AGENTS.md` 等 | 读写该目录时 | 各 ≤3 KB |
| 规范 | `_schema.md` | 写文件前 | ≤8 KB |
| 流程 | `运营手册.md` / `归档规范.md` | 对应任务 | 各 ≤10 KB |
| 导航 | `_index.md` | 找页面时 | ≤20 KB |
| 技能 | `SKILL.md` | 调用时 | ≤150 行 |

原则：**入口只放「去哪找」，细节按需加载。** 一次归档任务的上下文应该控制在 12k token 以内。

### 5.2 任务读取路径

| 任务 | 只读这些 | 不要读 |
|---|---|---|
| 今日待办 | `HOME.md` | 全库 |
| 接一个项目 | 项目页 + 该项目关联的会议摘要 + 提到的人物页 | 全部会议 |
| 归档录音 | `归档操作规范.md` + `_schema.md` + 相关项目页 | 其他项目 |
| 写公众号 | 对应 `film-*` skill + 项目页 + `01_参考文档` | 历史文章全量 |
| 查历史事实 | `_index.md` → `vault-search.py` → 命中页 | 逐篇 grep |
| 维护库 | `AGENTS.md` + lint 输出 | 正文 |

### 5.3 Skill 布局

DSH 的 skill 根按优先级排序：项目 `.dsh/skills`（100）、项目 `.agents/skills`（200）、自定义（300）、用户 `~/.dsh/skills`（400）、用户 `~/.agents/skills`（500）。项目根是最近的含 `.git` 的祖先目录，本库有 `.git`，所以 `24帧运营库/.agents/skills/` 会被识别，且优先于全局副本。

做法：

1. 把两个 skill 目录整体复制到库内 `.agents/skills/`。
2. 按 `_schema.md` 重写 `SKILL.md`，入口压到 150 行以内。
3. 把旧的长内容拆到 `references/`，只在需要时读。
4. 删除 `~/.agents/skills/` 下的旧副本，避免同名竞争。
5. 验证：在库内新开 DSH 会话，输入 `/24frames-vault`，确认加载的是库内版本（看 frontmatter 的 `updated` 或新增的标记行）。

### 5.4 嵌套 AGENTS

DSH 在 agent 读、写、编辑更深目录的文件后，会把该目录的 `AGENTS.md` 追加到后续请求。利用这一点，把局部规则放在局部：

| 文件 | 内容 | 不超过 |
|---|---|---:|
| `02_项目/AGENTS.md` | 项目页必备段落、任务语法、子目录只用 01–04、决策记录格式 | 3 KB |
| `03_人物/AGENTS.md` | 人物页结构、默认 `audience: owner`、敏感信息写法 | 2 KB |
| `05_档案/AGENTS.md` | 只读、会议命名、发布前脱敏、禁止重命名 | 2 KB |
| `06_AI/AGENTS.md` | 日期目录、草稿生命周期、`_已校准` 后缀、发布后归档 | 2 KB |
| `00_系统/AGENTS.md` | 规范唯一源、改规范需批准、changelog 格式 | 2 KB |

根 AGENTS 只写一句：「进入目录后以该目录 AGENTS.md 为准」。

### 5.5 Hooks

DSH 通过 `dsh-hooks-claude-code` 支持 Claude Code 的命令钩子，可用事件：`SessionStart`、`UserPromptSubmit`、`PreToolUse`、`PostToolUse`、`Stop`、`SubagentStart/Stop`。`PreToolUse` 可以 deny 或 ask；`PostToolUse` 可以用 exit 2 阻断并把 stderr 反馈给模型；`Stop` 可以强制再走一轮。

本库只用两个，避免误伤：

1. **PostToolUse（Write/Edit）→ `post-write-lint.sh`**
   读取 stdin JSON，取出 `tool_input.file_path`，跑 `vault-lint.py --file`。有硬错误时 exit 2，stderr 写「字段/目录/隐私」的具体问题。模型会收到反馈并立即修。
2. **PreToolUse（Write/Edit）→ `guard-archive.sh`**
   `05_档案/公众号存档/`、`05_档案/媒体/`、`05_档案/放映数据/` 一律 exit 2；`05_档案/会议存档/` 已存在文件 exit 2，新建文件必须匹配 `YYYY-MM-DD_主题.md` 且含 `type/date/participants/direction/audience`。提示「档案只读，修订写 06_AI 草稿」。

不启用 `Stop` 钩子。当前桥接的 `stop_hook_active` 恒为 false，没有连续阻断上限，容易死循环。

hooks 属于进程级配置，需要在 DSH profile 里挂载 `@deepseek-ai/dsh-hooks-claude-code`，`configPath` 指向库内 `.claude/hooks.json`。这是配置变更，按红灯处理：先备份 profile，再在临时 profile 验证，最后切正式。没有跑通之前，lint 靠任务卡手动执行。

### 5.6 Headless 与定时任务

`dsh --profile headless` 可以一次性执行任务并退出，支持 `--json` 和 `--session-id`。当前 profile 的 `cordis.patch.yml` 是空数组，没有模型路由，直接跑会失败。

修复步骤：

1. 从 `~/.dsh/profiles/desktop/cordis.patch.yml` 复制 `llm-pi-ai` 和 `agent-default-model` 两个块到 headless 的 patch，模型选一个便宜、长上下文的（如 `sensenova-6.8-flash-lite`）。
2. 确认 API key 在 launchd 能读到的位置。launchd 不继承 shell 环境，wrapper 里先 `source ~/.zshrc` 或显式 `export`。
3. 先用一条只读任务验证：`dsh --profile headless "读 00_系统/_index.md，输出项目数"`。
4. 再挂 launchd。

分两层跑：

| 频率 | 任务 | 是否用 LLM |
|---|---|---|
| 每晚 02:00 | lint + index + home + changelog 分卷检查 | 否，纯 Python |
| 每周日 20:00 | 语义体检：矛盾、过期结论、缺页概念 | 是，headless |
| 每月 1 日 | 隐私扫描 + 公开页复核 | 否 + 人工 |

`dsh schedule` 是会话内提醒，最小 5 分钟，进程退出就失效，不能当 cron 用。跨会话定时只能靠 launchd 或系统 cron。

### 5.7 Goal、Plan、Subagent

| 机制 | 适用 | 不适用 |
|---|---|---|
| Goal 自动续跑 | 一次领多张卡、批量迁移、长任务 | 需要人类频繁拍板的任务 |
| Plan 模式 | 改动超过 20 个文件、涉及规范变更 | 单文件修复 |
| 子代理 | 并行读资料、核对历史文章、外部调研 | 并行写库 |
| Workflow | 一次性批量审计 | 日常维护 |

本库的维护任务大多有明确验收，适合 Goal；规范变更和隐私处置适合 Plan + 人工确认。

### 5.8 附件与录音

- 图片附件放 `06_AI/YYYY-MM-DD_主题/attachments/`，不散落。
- 音频、视频先转写，原文放 `05_档案/会议存档/`，原始文件放库外媒体目录，库内留一行路径。
- `@file` 只是路径补全，模型仍需调用文件工具读取，不要以为 @ 了就进上下文。
- 转写用 `speech-to-text` skill；中文会议先确认说话人，再按归档规范清洗。

### 5.9 Schedule 的边界

`dsh schedule` 的提醒只在当前会话有效，需要 root agent 在线，最小间隔 5 分钟，不支持日历规则。它适合「20 分钟后提醒我看结果」，不适合「每天凌晨跑 lint」。定时任务放 launchd。

### 5.10 Astronaut preset 桥接

astronaut preset 目前和库是两套记忆：preset 启动读 9 个文件，其中多个 `memory/*` 子目录不存在；库里的业务事实从不进入 preset，preset 的公理也不影响库的写法。

桥接方式：

1. 在 preset 的 `agent.cordis.yml` 启动序列里，把不存在的文件删掉，只保留存在的 `persona/`、`memory/axioms/INDEX.md`、`memory/WANT-TO-DO.md`、`memory/OBSERVATIONS.md`。
2. 新增 `memory/VAULT-BRIDGE.md`，只写：库路径、根 AGENTS、`_schema.md`、`HOME.md`、`_index.md` 四个入口，以及「业务事实以库为准」。
3. preset 的 persona 不写项目细节；需要时读库。
4. 每次任务结束，preset 只更新自己的 `OBSERVATIONS.md`，业务结论写回库。

### 5.11 Skill 目录瘦身

当前 `~/.agents/skills/` 有 170 个 skill，每个请求都加载名称和描述，约 8k token。大部分与本库无关。

做法：

1. 统计最近 30 天实际调用的 skill（DSH 日志或人工回忆）。
2. 保留 30–50 个高频，其余在 frontmatter 加 `disable-model-invocation: true`，或移到不加载的归档目录。
3. 每个保留的 skill 描述压到一句话，写清「什么时候用」。
4. 每月复核一次，新增 skill 必须能说出使用场景。

目标：skill 描述总成本降到 3k token 以内。

---

## 6. 优化路线图

### P0 · 今天（约 5 小时，其中 10 分钟由宇航员完成）

| ID | 任务 | 产出 | 验收 |
|---|---|---|---|
| P0-1 | 关闭公开仓库 | 仓库转 private | `curl` 返回 `private: true` |
| P0-2 | 重写根 AGENTS | 6–8 KB 契约 | 行数 ≤150，含四层与红线 |
| P0-3 | 落盘 `_schema.md` | 唯一字段规则 | lint 能读取枚举 |
| P0-4 | 规范三合一 | 手册补全、SOP 修正、旧 SOP 删除 | 全文无 `02_归档文件/`、无 `04_人物/` |
| P0-5 | skill 迁入并瘦身 | 库内两个路由 skill | `wc -l` ≤150 / ≤120，旧副本删除 |
| P0-6 | 隐私元数据清理 | 人物/会议 `audience` 修正 | public 人物/会议为 0（除已批准） |
| P0-7 | 全局路径修正 | `~/.dsh/AGENTS.md` 正确路径 | 全文无 `OH-WorkSpace` |

### P1 · 第 1 周

| ID | 任务 | 产出 | 依赖 |
|---|---|---|---|
| P1-1 | 索引生成器 | `_index.md` 自动生成 | P0-3 |
| P1-2 | HOME 静态看板 | 今日待办、等我拍板、停滞项目 | P0-3、P1-5 |
| P1-3 | Lint v2 | 枚举、目录、隐私、双链、changelog | P0-3 |
| P1-4 | 嵌套 AGENTS | 5 个目录规则 | P0-2 |
| P1-5 | 任务语法迁移 | 11 个项目页统一 | P0-3 |
| P1-6 | 清死 Dataview | 12 个文件改为静态/Bases | P1-1、P1-2 |
| P1-7 | changelog 规范化 | 12 条修正 + 分卷规则 | 无 |
| P1-8 | Review 队列清零 | 7 个 review 页处理 | 宇航员 |
| P1-9 | 归档去重与工具外迁 | 删 302 重复、移 node_modules | 无 |

### P2 · 第 2–4 周

| ID | 任务 | 产出 | 依赖 |
|---|---|---|---|
| P2-1 | FTS5 检索 | `vault-search.py` | P1-1 |
| P2-2 | headless + launchd | 夜间 lint/index/home | P1-3 |
| P2-3 | hooks 写入拦截 | PostToolUse lint、PreToolUse 档案守卫 | P1-3 |
| P2-4 | Astronaut 桥接 | `VAULT-BRIDGE.md` + 启动序列修正 | P0-2 |
| P2-5 | Bases 视图 | 项目/人物/灵感三个视图 | P1-6 |
| P2-6 | 媒体与 git 策略 | `.gitignore`、媒体索引、历史处理 | P0-1 |
| P2-7 | 语义 lint | 每周矛盾/过期/缺页报告 | P2-2 |
| P2-8 | 指标看板 | 每周健康快照 | P1-3 |
| P2-9 | skill 目录瘦身 | 170 → ≤50 活跃 | 无 |

### P3 · 第 2 个月

| ID | 任务 | 产出 |
|---|---|---|
| P3-1 | 查询回写 routine | 每周把高价值问答落页 |
| P3-2 | 季度归档与复盘 | 公众号存档、会议、changelog 的季度整理 |
| P3-3 | v1 方案归档 | v1 标记 superseded，附件保留 |

### 依赖图

```
P0-1 ──────────────────────────────► P2-6
P0-7
P0-3 ──► P1-1 ──► P1-2 ──► P1-6 ──► P2-5
  │        └──────► P2-1
  ├──────► P1-3 ──► P1-5 ──► P1-2
  │          └─────► P2-2 ──► P2-7
  │          └─────► P2-3
  └──────► P2-8
P0-2 ──► P1-4
P0-2 ──► P2-4
P0-5
P0-6
P1-7 / P1-8 / P1-9 独立
P2-9 独立
```

---

## 7. Agent 分工与协作

### 7.1 角色

| 角色 | 职责 | 写权限 | 不做什么 |
|---|---|---|---|
| 图书管理员 | 索引、lint、双链、changelog | `00_系统/` 生成物 | 不改项目结论 |
| 归档员 | 录音转写、六步归档、更新项目/人物 | `05_档案/会议存档/` 新建、项目/人物页 | 不改历史会议 |
| 写作者 | 公众号、影评、方案初稿 | `06_AI/` | 不发布、不改 wiki 事实 |
| 研究员 | 外部调研、资料核对 | `06_AI/` 或 `04_灵感/知识库/` | 不写项目页 |
| 审计员 | 隐私、schema、质量抽查 | 只读，产出报告 | 不直接改 |
| 宇航员 | 红灯决策、发布、删除、规范批准 | 全部 | — |

### 7.2 RACI

| 操作 | 执行 | 批准 | 咨询 | 告知 |
|---|---|---|---|---|
| 新建会议存档 | 归档员 | 宇航员（敏感时） | 项目负责人 | 图书管理员 |
| 新建项目页 | 图书管理员 | 宇航员 | 写作者 | — |
| 改 `_schema.md` | 图书管理员 | 宇航员 | 审计员 | 所有 agent |
| 改根 AGENTS | 图书管理员 | 宇航员 | — | 所有 agent |
| 对外发布 | 写作者 | 宇航员 | 审计员 | — |
| 删除文件 | 宇航员 | 宇航员 | 图书管理员 | — |
| 批量迁移 >20 文件 | 图书管理员 | 宇航员 | 审计员 | — |
| 每周体检 | 审计员 | — | — | 宇航员 |

### 7.3 交接格式

```markdown
TASK: P1-5 把苏宁影城项目页改成任务语法
CHANGED: 02_项目/苏宁影城路演合作/苏宁影城路演合作.md
VERIFY: python3 00_系统/agent/vault-lint.py --file ... → 0 error
RISK: 原「时间线」段落保留，未删
NEXT: 另 10 个项目页按同一模板迁移
```

没有 `VERIFY` 原文的交接视为未完成。

### 7.4 单写者

- 同一时刻只允许一个 agent 写库。其他 agent 只读，把结果交给写者。
- 需要并行时按目录分区：A 写 `02_项目`，B 写 `03_人物`，C 只读汇总。分区写也要串行提交，避免同一文件冲突。
- 子代理不直接写库；子代理产出文本，主 agent 落盘。

### 7.5 红灯

以下操作必须先问宇航员，agent 不得自行执行：

1. 涉及钱、报价、分账、赞助。
2. 对外发布或发给合作方。
3. 删除文件、清空目录、改写历史存档。
4. 新建人物页或项目页（可以先提议）。
5. 修改 `_schema.md`、根 AGENTS、运营手册、归档规范。
6. `git push`、改 remote、改仓库可见性。
7. 批量修改超过 20 个文件。
8. 安装插件或改 DSH profile。

---

## 8. 验收与度量

### 8.1 基线 vs 目标

| 指标 | 基线 2026-10-28 | 目标 | 检查方式 |
|---|---:|---:|---|
| 活跃页 frontmatter 覆盖 | 232/241；summary 4/241 | 100% 必填齐全 | `vault-lint.py` |
| 非法 `type` 新增 | 20 种历史值 | 新文件 0 | lint |
| 非法 `status` 新增 | 9 种 | 新文件 0 | lint |
| `direction` 写法 | 12 种 | 5 种，纯文本 | lint |
| 断裂双链 | 15 | ≤5 | lint |
| 孤儿页 | 92 | ≤15 | index |
| 无 `## 关联` | 69 | ≤10 | lint |
| 未批准 public 人物/会议 | 26（全库 public 61） | 0 | lint |
| 死 Dataview | 12 文件 | 0 | `grep` |
| Review 超 7 天 | 7 | 0 | lint |
| changelog 格式 | 128/140 | 新条目 100% | lint |
| 根 AGENTS | 2.7 KB | 6–8 KB，≤150 行 | `wc` |
| 24frames-vault skill | 1,052 行 | ≤150 行 | `wc` |
| 索引新鲜度 | 手工，过期 | ≤24 小时 | 文件时间 |
| lint 运行时间 | 手工 | <5 秒 | `time` |

### 8.2 每周体检

每周日 20:00 生成 `00_系统/agent/logs/health-YYYY-MM-DD.md`：

```markdown
# 健康快照 2026-11-01

- 内容页：561 → 575（新增 schema、脚本、模板）
- 新增未合规：2（列出）
- 断裂双链：15 → 5
- 孤儿：92 → 15
- public 未批准：61 → 0
- Review 超期：7 → 0
- 本周写入：12 次，涉及 9 个文件
- 待宇航员拍板：3 条
- 建议动作：3 条，每条带文件路径
```

只留最近一份，旧报告删除。结论提炼进 `00_系统/agent/经验沉淀.md`。

### 8.3 总验收

P0+P1 完成的标志：

1. 在库内新开 DSH 会话，问「现在有哪些项目、各自下一步」，agent 只读 `HOME.md` 就能在 30 秒内答出，且答案与项目页一致。
2. 故意写一个 `type: 项目会议` 的文件，lint 在 5 秒内报错；如果启用了 hooks，写入当场被拦。
3. 问「某次会上谁说了资金怎么分」，agent 先用 `_index.md` 定位项目，再用 `vault-search.py` 找到会议，给出原文链接。
4. 新归档一篇录音，六步全部完成，项目页、人物页、changelog 同时更新，lint 通过。
5. 全库 `public` 页面都能说出批准日期和脱敏依据。

---

## 9. 反清单

1. 不装 Dataview。已有 Bases，静态生成更稳。
2. 不新建 `03_任务/`。任务写在项目页。
3. 不在 skill 里复述 schema。skill 只路由。
4. 不把业务事实写进 astronaut persona。
5. 不用 `audience: public` 表示「不保密」。
6. 不批量重写历史存档。
7. 不让多个 agent 同时写库。
8. 不把 `node_modules`、`.hermes`、音视频大文件放进库。
9. 不在没有 lint 的情况下做批量迁移。
10. 不自动发布到公众号、小红书。
11. 不把 `dsh schedule` 当 cron。
12. 不在 `main` 上直接试验，先开分支。

---

## 10. 风险与回滚

### 10.1 开工前

```bash
cd /Users/haishangyinghuo/Documents/24帧运营库
git status --short > /tmp/vault-status-before.txt
git tag pre-optimize-2026-10-28
git switch -c vault-optimize-2026-10
```

复核时有 81 项未提交改动（71 删除、5 修改、5 新增，含本次新增的方案目录），其中包含宇航员正在处理的文章与调研。**不要 commit 这些改动，不要 restore。** 开工前把 `git status` 存档，迁移只碰任务卡列出的文件。

### 10.2 风险表

| 风险 | 触发 | 缓解 | 回滚 |
|---|---|---|---|
| 批量改字段导致断链 | P1-5/P1-6 | 先跑 lint 基线，逐项目改 | `git restore <file>` |
| agent 迁移期读旧 skill | P0-5 | 先删全局副本，再验证加载路径 | 从备份恢复 skill |
| hooks 误拦正常写入 | P2-3 | 先在临时 profile 验证，只拦两类 | 移除 hook 配置 |
| headless 消耗过多 token | P2-2 | 每周一次，限制输出，用便宜模型 | 停 launchd |
| 隐私清理误删信息 | P0-6 | 只改 `audience`，不删正文 | `git restore` |
| 归档去重删错版本 | P1-9 | 先比对 md5，保留年目录，镜像整体移出 | 从站点仓库取回 |

### 10.3 回滚粒度

- 单文件：`git restore --source=pre-optimize-2026-10-28 -- <path>`
- 单任务：按任务卡的 `Rollback` 执行。
- 整批：`git switch main`，删除实验分支。

---

## 11. 第一周执行表

| 日期 | 上午 | 下午 | 验收 |
|---|---|---|---|
| 10-28 周三 | P0-1（人）、P0-7 | P0-3、P0-2 | 仓库 private；根 AGENTS 定稿 |
| 10-29 周四 | P0-4 规范合一 | P0-5 skill 迁移 | 全文无旧路径；skill ≤150 行 |
| 10-30 周五 | P0-6 隐私清理 | P1-3 lint v2 | 26 个人物/会议 public 清零（全库 61 个分步处理）；lint <5s |
| 10-31 周六 | P1-1 索引 | P1-2 HOME | 首页能回答「现在做什么」 |
| 11-01 周日 | P1-4 嵌套 AGENTS | P1-5 任务语法（前 5 个项目） | 5 个项目页格式统一 |
| 11-02 周一 | P1-5 剩余 6 个 | P1-6 清 Dataview | 12 个文件无查询块 |
| 11-03 周二 | P1-7 changelog | P1-8 review、P1-9 归档 | 12 条修正；302 重复移除 |

每天结束前 10 分钟：跑 lint、更新 `HOME.md`、记 changelog、把当天结论写进 `经验沉淀.md`。

---

## 12. 来源

- Karpathy, *LLM Wiki*：https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- AGENTS.md 标准：https://agents.md/
- AGENTS.md 仓库：https://github.com/agentsmd/agents.md
- qmd 本地检索：https://github.com/tobi/qmd
- 本机 DSH 文档：`~/.dsh/profiles/node_modules/@deepseek-ai/dsh-agent-instructions/README.md`、`dsh-skill-filesystem/README.md`、`dsh-hooks-claude-code/README.md`、`dsh-hook-protocol/README.md`、`dsh-schedule/README.md`、`dsh-attachment/README.md`、`dsh-file-reference/README.md`
- 本库基线数据：2026-10-28 全库扫描，原始结果在 `/tmp/audit_result.json`（临时文件，结论已写入本文件）

---

## 关联

- [[附件A-现状复核与执行队列]]
- [[附件B-模板与脚本]]
- [[附件C-脚本源码]]
- [[运营手册]]
- [[_index]]
- [[归档操作规范]]
- [[24帧运营库-DSH优化方案]]
