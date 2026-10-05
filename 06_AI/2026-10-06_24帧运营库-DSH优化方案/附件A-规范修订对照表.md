---
type: reference
name: 附件A-规范修订对照表
status: review
editable: true
audience: agent
created: 2026-10-06
updated: 2026-10-06
source: ai-generated
tags: [基建, 规范修订]
---

# 附件A · 规范修订对照表

> 配套 [[24帧运营库-DSH优化方案]]。
> **用法**：找到你要改的 P0 编号 → 按"现在写的"原文定位 → 替换成"改成"。行号基于 2026-10-06 的文件状态，改之前先 `grep -n` 复核一次。
>
> **顺序建议**：先做 §A11 的三条纯约定（零风险、半小时），再做 §A1 起的文件级修订。

---

## A0 · 改之前的三条纪律

1. **一次只改一个 P0**，改完立刻 commit。别把 8 个 P0 混在一个 commit 里。
2. **改规范不动内容**。这次只修矛盾路径和错误引用，不重写文风、不重排章节。
3. **改了规范就要同步改引用它的地方**（skill、`_index.md`、`AGENTS.md`）。列表见 §A9。

---

## A1 · `00_系统/归档操作规范.md`（P0-1）

### A1-1 第 4 行 frontmatter

| | 内容 |
|---|---|
| 现在 | `audience: agent` |
| 改成 | `audience: both` |
| 为什么 | 宇航员也要能读归档 SOP；`audience: agent` 会让 Dataview/Bases 的 owner 视图把它过滤掉 |

### A1-2 第 6 行 frontmatter

| | 内容 |
|---|---|
| 现在 | `direction: 策展人` |
| 改成 | （删除这一行） |
| 为什么 | 归档 SOP 是全库通用规范，不属于"策展人"这一个方向；留着会污染方向筛选 |

### A1-3 第 44 行 · 任务文件那行（表格）

| | 内容 |
|---|---|
| 现在 | `\| 任务文件 \| 衍生笔记 \| type: task, name, status, priority, assignee, due, audience, created, updated \|` |
| 改成 | （删除整行） |
| 替代 | 在表格下方加一行说明：`> 任务已并入项目页正文的「待办」段，不再有独立 task 文件。历史 task 文件保留在原处，不再新增。` |
| 为什么 | 任务目录 2026-06-12 就废止了（见 `_changelog` 第 908 行"03_任务 → 02_项目"），规范里还留着入口 |

### A1-4 第 72 行 · Step 1 第 4 条（**最关键的一条**）

```diff
- 4. 存入项目目录 `02_归档文件/`（如项目目录不存在则先创建）
+ 4. 存入 `05_档案/会议存档/`，命名 `YYYY-MM-DD_主题.md`（会议/通话/访谈/录音的唯一归属，项目目录不放会议）
```

> 依据：`运营手册.md` §1.1「会议文件唯一归属（硬规则）」，2026-06-19 已宣布废止旧 SOP。
> 这一条不改，所有 agent 都会继续往项目目录塞会议记录。

### A1-5 第 80 行 · Step 2 人物文件路径

```diff
- **人物文件**（`04_人物/`）：
+ **人物文件**（`03_人物/`）：
```

> 第 5 行「Step 2 信息提炼」的正文里如果也有 `04_人物`，一并改。全库搜 `04_人物` 应只剩 `_changelog.md` 和 `agent/_archive/` 的历史记录。

### A1-6 第 91–94 行 · Step 2 任务文件整段

| | 内容 |
|---|---|
| 现在 | `**任务文件**（任务并入项目，放 \`02_项目/项目名/\` 内，type: task）：` 及下面 3 条（待办按时间线拆分 / 每条有执行人和截止 / 链项目文件） |
| 改成 | `**项目页待办段**（不建独立文件）：在 \`02_项目/项目名/项目名.md\` 正文加/更新 \`## 待办\` 段，每条写成 \`- [ ] 事项 — @执行人 — 截止 YYYY-MM-DD\`。不新建 task 文件。` |

### A1-7 第 140–152 行 · 文末「目录结构参考」

把整块替换为：

```
24帧运营库/
├── 02_项目/
│   └── [项目名]/
│       ├── [项目名].md          # 项目概况（衍生笔记）：关键参数 + 决策记录 + ## 待办 段
│       ├── 01_参考文档/         # 背景调研、协议、群聊对齐信息
│       ├── 02_归档文件/         # 项目原始素材（剧本、排期）；★不放会议
│       ├── 03_AI文档/           # AI 生成的方案 / 初稿
│       └── 04_草稿/             # 草稿
├── 03_人物/
│   └── [人名].md                # 人物文件（衍生笔记，链原始存档）
└── 05_档案/会议存档/
    └── YYYY-MM-DD_主题.md       # ★会议/通话/访谈/录音的唯一归属（原始笔记，不加出站双链）
```

### A1-8 全文搜索确认

```bash
cd ~/Documents/24帧运营库
grep -n "02_归档文件/\|04_人物\|type: task\|03_任务" 00_系统/归档操作规范.md
# 期望：只剩 A1-7 里的 `02_归档文件/         # 项目原始素材（剧本、排期）；★不放会议` 这一处说明性文字
```

---

## A2 · 新建 `00_系统/_schema.md`（P0-2）

**内容照抄 [[附件B-Agent落地执行手册]] §B1。**

### A2-1 同步改 `运营手册.md`

在 `## 1. 目录结构与权限（共读）` 之后插入一段：

```markdown
### 1.2 frontmatter 单一事实源

所有文件的 frontmatter 取值以 `00_系统/_schema.md` 为准。本手册不再单独列枚举。
新增/修改取值，只改 `_schema.md`，并在此处不改。
```

### A2-2 同步改 `运营手册.md` 第 89 行

| | 内容 |
|---|---|
| 现在 | `- 会议标准 frontmatter：`type: meeting, title, date, participants, direction, related_projects, related_people, tags, status: archive, editable: false, audience, created, updated, source`。` |
| 改成 | `- 会议标准 frontmatter：见 \`_schema.md\` §2「会议」行。` |

### A2-3 同步改 `归档操作规范.md` §15 的 frontmatter 表

那张表（第 39–48 行）删掉，替换成一句：`frontmatter 字段与取值以 \`00_系统/_schema.md\` §2 为准。`

---

## A3 · 修 6 个断裂双链（P0-3）

> 说明：下表用反引号标注原始 wikilink 目标名，**不写成方括号**，避免本文件自己产生断链。

| # | 文件 | 现在 | 改成 |
|---|---|---|---|
| 1 | `03_人物/宇航员.md` | 一条**被截断的多行 wikilink**：目标以 `何力长片-浮生若丽` 开头，后面对接了三行正文，以 `]]` 收尾 | 删掉这整条畸形链接，改写成正常列表：`- [[何力长片-浮生若丽]]（2026年7月起参与）`，后面两条独立成行 |
| 2 | `06_AI/2026-07-10_痴迷影评/影评评分机制-可复用版.md` | wikilink 目标 `film-spotlight-writing` | `` `film-spotlight-writing` ``（skill 名不加 wikilink） |
| 3 | 同上 | wikilink 目标 `film-festival-coverage` | `` `film-festival-coverage` `` |
| 4 | 同上 | wikilink 目标 `film-festival-reporting` | `` `film-festival-reporting` `` |
| 5 | `00_系统/_changelog.md` | wikilink 目标 `2026-05-31-系统提示词泄露与频道投递异常` | 加进 `vault-health-check.py` 的 `KNOWN_DEBT_LINKS`（历史记录，文件从未创建） |
| 6 | `00_系统/_changelog.md` | wikilink 目标 `遂宁市/四川省/射洪市影视产业` | 改成纯文本 `遂宁市/四川省/射洪市影视产业`（这不是笔记名） |

**顺手升级脚本**（`00_系统/agent/vault-health-check.py`）：
- 把 `KNOWN_DEBT_LINKS` 的两条加进去
- 新增一条规则：**wikilink 目标如果匹配 `~/.agents/skills/` 下任何 skill 的 name，报"skill 名误用为 wikilink"**，而不是报断链（这两类问题的修法不同）

---

## A4 · skill 搬进库（P0-4）

### A4-1 目录

```bash
mkdir -p ~/Documents/24帧运营库/.agents/skills
```

### A4-2 `24frames-vault` 瘦身

| | 现状 | 目标 |
|---|---|---|
| 位置 | `~/.agents/skills/24frames-vault/`（21 文件 / 168 KB） | `24帧运营库/.agents/skills/24frames-vault/SKILL.md`（1 文件 / ≤150 行） |
| 内容 | 1052 行，含 frontmatter 解析代码、Dataview 查询实现、20 篇 case 文档 | 只留：库结构图（10 行）+ 硬规则（8 条）+ 路由表（"要做什么 → 读哪个文件"）+ frontmatter 指向 `_schema.md` |
| 必须删 | `OH-WorkSpace` 路径、"6 个业务方向"、`03_任务`、"06_灵感库/归档/" | — |

**新版 SKILL.md 全文照抄 附件B §B4。**

### A4-3 `vault-archiving` 瘦身

| | 内容 |
|---|---|
| 位置 | `~/.agents/skills/vault-archiving/` → `24帧运营库/.agents/skills/vault-archiving/SKILL.md` |
| 删掉 | **整个「⚠️ 已知陷阱：`归档操作规范.md` 文本与实际约定不一致」章节**（P0-1 修完规范后这节就是错的） |
| 删掉 | 「⚠️ Step 1 增强：口误与转写错误审计」中的**具体案例表**（阿巴斯/西宁那些），改成"音误检查原则"一句话；案例移到 `00_系统/agent/经验沉淀.md` |
| 保留 | 六步流程速记表、多部分采访必须合并为单文件、Verification Checklist |
| frontmatter 加 | `user-invocable: false`（这是给模型的路由壳，不该出现在人的斜杠命令里） |

### A4-4 旧 skill 处置

`~/.agents/skills/` 下的旧目录**先别删**，改名加 `.bak-20261006` 后缀，观察两周。观察期内如果发现哪次调用走的是旧版，说明库内版有问题，回滚。

---

## A5 · 三份嵌套 `AGENTS.md`（P0-5）

**内容照抄 附件B §B2。** 放完在根 `AGENTS.md` 的 §2 后面加一段：

```markdown
## 2.5 局部规则（自动加载）

进入以下目录时，DSH 会自动把该目录的 `AGENTS.md` 追加进上下文，不需要手动读：
- `02_项目/` 写项目页前
- `06_AI/` 写 AI 产出前
- `05_档案/会议存档/` 归档前
```

---

## A6 · `HOME.md` 去 Dataview（P0-6）

### A6-1 替换 4 个代码块

| 行号 | 现在 | 改成 |
|---|---|---|
| 17–22 | `## 📊 项目进度全貌` + dataview 块 | 静态 Markdown 表格（列：项目 / 方向 / 进度 / 目标 / 更新），由 agent 在每次改项目页时同步 |
| 28–33 | `## ⏭️ 在推什么 · 在等什么` + dataview 块 | 静态表格或列表，只列 `progress: 进行中` 的项目 |
| 37–42 | `## 🔍 等我拍板` + dataview 块 | 静态列表；**每次新增 `status: review` 文件时必须同时加到这里**（写进 `_schema.md` 的硬规则） |
| 46–51 | `## 💡 灵感待决策` + dataview 块 | 静态列表，来源 `04_灵感/AI加工区/` 里 `stage != 已转项目/已归档` 的文件 |

### A6-2 文件头加一句

```markdown
> 本页由 agent 维护：改动 `02_项目` / `04_灵感` / `status: review` 时同步更新本页。
> 自动视图在 `.base/` 目录（Obsidian 原生 Bases，不用装插件）。
```

### A6-3 `_index.md` 同样处理

第 16、34、42 行的 3 个 dataview 块，同样换成静态表格。

### A6-4 新建 `.base` 文件

`.base/项目看板.base`：

```yaml
filters:
  and:
    - file.inFolder("02_项目")
    - type == "project"
views:
  - type: table
    name: 项目进度
    order:
      - file.name
      - direction
      - progress
      - goal
      - updated
    sort:
      - property: progress
        direction: ASC
```

`.base/待拍板.base`：

```yaml
filters:
  and:
    - 'status == "review"'
    - 'audience != "agent"'
views:
  - type: table
    name: 等我拍板
    order: [file.name, file.folder, file.mtime]
```

> 语法依据：Obsidian Bases 用 YAML，支持 `filters`（and/or/not、`file.hasTag`、`file.inFolder`、`file.hasLink`）、`formulas`、`properties`、`views`（table/limit/groupBy/order/sort/summaries）。本库 `.obsidian/core-plugins.json` 里 `"bases": true` 已开启，**不需要装任何插件**。

---

## A7 · 清库外垃圾（P0-7）

```bash
cd ~/Documents/24帧运营库

# 1) .hermes 逐个文件判性质（不要整个删）
ls -la .hermes/desktop-attachments/

# 1a) 2 个 docx 与项目目录 md5 完全相同 → 精确重复，直接删
md5 -q ".hermes/desktop-attachments/我的一生new.docx" \
       "02_项目/何力长片-浮生若丽/01_参考文档/我的一生new.docx"      # 两行应一致
md5 -q ".hermes/desktop-attachments/浮生若丽-创作谈.docx" \
       "02_项目/何力长片-浮生若丽/01_参考文档/浮生若丽-创作谈.docx"  # 两行应一致

# 1b) 4 个政策 PDF 是【原文】，项目目录里放的是 _标注版（内容不同）→ 归位，不要删
mkdir -p "02_项目/何力长片-浮生若丽/01_参考文档/00_原始政策文件"
mv .hermes/desktop-attachments/*.pdf "02_项目/何力长片-浮生若丽/01_参考文档/00_原始政策文件/"

# 1c) 停跟踪 + 忽略
git rm -r --cached .hermes
rm -rf .hermes
printf '\n# Hermes 历史附件缓存（内容已归位，勿再跟踪）\n.hermes/\n' >> .gitignore

# 2) 抓取工具链：先抢救文档，再移出库
mkdir -p "06_AI/2026-10-05_公众号抓取工具链"
cp 05_档案/公众号存档/_skill/SKILL.md            "06_AI/2026-10-05_公众号抓取工具链/SKILL.md"
cp 05_档案/公众号存档/_skill/docs/python-fetching.md "06_AI/2026-10-05_公众号抓取工具链/python-fetching.md"
mv 05_档案/公众号存档/_skill ~/Documents/_24帧库外备份/公众号抓取工具链_20261006

# 3) .DS_Store
find . -name .DS_Store -not -path './.git/*' -delete
```

> ⚠️ **别把 `.hermes/` 整个删掉**：里面 4 个 PDF 是政策原文，项目目录里放的是 `_标注版.pdf`（体积和内容都不同，不是同一文件）。只有 2 个 docx 是精确重复。

---

## A8 · 会议存档命名统一（P0-8）

### A8-1 要改的 8 个文件

```
2026-05-17-24帧策展团队暨多项目启动会.md   → 2026-05-17_24帧策展团队暨多项目启动会.md
2026-05-19-策展团队困境与转型.md           → 2026-05-19_策展团队困境与转型.md
2026-05-28-AI创作方向与战略咨询.md         → 2026-05-28_AI创作方向与战略咨询.md
2026-05-29-赞助方案与策展分工.md           → 2026-05-29_赞助方案与策展分工.md
2026-05-30-项目推进与人员招募.md           → 2026-05-30_项目推进与人员招募.md
2026-06-01-业务模式与赞助策略讨论.md       → 2026-06-01_业务模式与赞助策略讨论.md
2026-06-01-何力长片项目面谈.md             → 2026-06-01_何力长片项目面谈.md
2026-06-04-项目进度同步与商业模式转型.md   → 2026-06-04_项目进度同步与商业模式转型.md
宇航员个人访谈-从地质工程到电影制片与使命探寻.md → 2026-07-07_宇航员个人访谈-从地质工程到电影制片与使命探寻.md
```

### A8-2 改名必须先改链接（顺序不能反）

```bash
cd ~/Documents/24帧运营库

# ① 先找出所有引用（含 wikilink、frontmatter 里的 related_*、正文纯文本）
grep -rln "2026-05-17-24帧策展团队暨多项目启动会" --include='*.md' .

# ② 逐个文件把旧名替换成新名（用 edit 工具，不要 sed 批量）
# ③ 全改完之后再 git mv 文件本身
git mv "05_档案/会议存档/2026-05-17-24帧策展团队暨多项目启动会.md" \
       "05_档案/会议存档/2026-05-17_24帧策展团队暨多项目启动会.md"

# ④ 改名后复查
python3 00_系统/agent/vault-health-check.py --detail
```

> ⚠️ Obsidian 按 basename 解析 wikilink，改文件名会立刻断链。`03_人物/*.md`、`02_项目/*/*.md`、`_changelog.md` 里都有引用，别漏。

---

## A9 · 改了规范之后，这些地方要同步（检查清单）

| 改了 | 必须同步改 |
|---|---|
| `归档操作规范.md`（P0-1） | `.agents/skills/vault-archiving/SKILL.md`、`00_系统/agent/录音会议存档SOP.md`、根 `AGENTS.md` §1 表格 |
| 新建 `_schema.md`（P0-2） | `运营手册.md` §1.2 + §1.1 会议 frontmatter 行、`归档操作规范.md` §15 表、`04_灵感/README.md` frontmatter 段、`.agents/skills/*/SKILL.md` |
| skill 搬进库（P0-4） | `_index.md` 末尾「架构说明」段（现在写的是"Hermes 通过 Skill 强制加载"，要改成"库自带 skill，任何 agent 直接读"） |
| `HOME.md` 静态化（P0-6） | `_index.md` 顶部「日常行动看 [[HOME]]」保持；`运营手册.md` §设计哲学第 2 条提到"三个入口"的地方加一句"HOME 由 agent 维护，非自动查询" |
| 会议改名（P0-8） | `_index.md`、`03_人物/*.md`、`02_项目/*/**.md`、`_changelog.md` 里的全部引用 |

---

## A11 · 三条零风险约定（P0-9 / P0-10 / P0-11）

> 纯文档约定，不改任何内容文件，半小时能做完。**收益最大、成本最低，应该最先做。**

### A11-1 P0-9 · raw 层不可写边界

**改哪**：根 `AGENTS.md` §3 硬规则，在现有 8 条后追加第 9 条。

```markdown
9. **raw 层只读**：`05_档案/` 是原始层（会议存档 / 公众号存档 / 媒体 / 放映数据）。
   agent **只能读**——不得改写、不得移动、不得重命名。
   唯一例外：按 `00_系统/归档操作规范.md` 在 `05_档案/会议存档/` **新建**文件。
   所有加工产物只能写 `06_AI/` 与 `04_灵感/`。
```

**为什么**：卡帕西 LLM Wiki 三层架构里，raw 层"these are immutable — the LLM reads from them but never modifies them"。现在库里 4 个 `review` 文件挂了 114 天、`_changelog` 里出现过"恢复意外删除的目录"，都是因为**没有一条明确的只读线**。

**验收**：`grep -n "raw 层只读" AGENTS.md` 有命中；下一次要求 agent 改会议存档正文时，它应该先说不。

### A11-2 P0-10 · `_index.md` 改成机器优先索引

**改哪**：`00_系统/_index.md`（现在 62 行，是结构说明）+ 根 `AGENTS.md` 加一条规则。

**现在的 `_index.md` 长这样**（结构说明，对 agent 无用）：

```markdown
## 01_方向
[[观影团]] · [[策展人]] · [[影视创作]] · [[宣发平台]] · [[AI影像]]
```

**改成**（每个内容文件一行，可 grep、可摘取）：

```markdown
## 01_方向
- [[观影团]] — 24帧核心业务：选片、放映、映后、观影团招募
- [[策展人]] — 策展团队机制、片单策划、影展合作
- [[影视创作]] — 24帧自制短片与联合出品长片的创作线
- [[宣发平台]] — 区域宣发、KOL 招募、观影团 + 策划展的宣发闭环
- [[AI影像]] — AI 短片、AI 电影节、AI 创作者活动

## 02_项目
- [[银发戏剧工作坊与定制短片]] — 观影团 · 进行中 — 用小酒馆场地+川传生源跑通戏剧工作坊，再转定制短片
- [[何力长片-浮生若丽]] — 影视创作 · 进行中 — 联合出品院线长片，380万/9月开机
（每行格式：[[文件名]] — 方向 · 进度 — 一句话）
```

**同步在 `AGENTS.md` 加规则**：

```markdown
10. **查库先读 `_index.md`**：任何"找某个项目/人物/资料"的请求，第一步读 `00_系统/_index.md`，
    再按行里的摘要钻取具体文件。不要一上来就全库 grep。
    新建/改名/删除内容文件时，同步更新 `_index.md`。
```

**为什么**：卡帕西说在 ~100 源 / 数百页的规模下，一份好的 `index.md` **可以完全替代向量检索**。你的库非存档部分只有 214 个文件，完全在这个量级内。

**验收**：`grep -c "^- \[\[" 00_系统/_index.md` ≥ 60；问 agent"苏宁影城路演合作的票价怎么定的"时，它先读 `_index.md` 而不是 grep。

### A11-3 P0-11 · 有价值的回答必须落成文件

**改哪**：根 `AGENTS.md` §3 硬规则，追加第 11 条。

```markdown
11. **回答要落库**：任何一次对话里产出的**分析、对比表、判断、方案**，
    只要宇航员认可（说"可以""就这样""存下来"或没有反对），
    必须落成 `06_AI/<日期>_<主题>/` 下的页面，并在 `_index.md` 登记。
    禁止只留在聊天里。
```

**为什么**：这是卡帕西 Query 操作的核心原话"good answers can be filed back into the wiki as new pages"，也是运营库**目前最大的信息泄漏点**——所有"帮我分析一下 X"的结论都消失在会话里，下次要从零再来。

**验收**：库里出现第一个由"对话结论"落成的 `06_AI/` 页面（本方案走的就是这条规则）。

---

## A10 · 一次性验证脚本

```bash
#!/usr/bin/env bash
# 00_系统/agent/verify-p0.sh —— P0 全部做完后跑一次
set -u
cd "$(dirname "$0")/../.." || exit 1
fail=0
chk() { printf '%-52s' "$1"; if eval "$2" >/dev/null 2>&1; then echo "✅"; else echo "❌"; fail=1; fi; }

chk "P0-1 归档规范无失效路径"   '! grep -q "02_归档文件/\|04_人物\|type: task" 00_系统/归档操作规范.md'
chk "P0-2 _schema.md 存在"      'test -f 00_系统/_schema.md'
chk "P0-3 健康检查零错误"       'python3 00_系统/agent/vault-health-check.py'
chk "P0-4 库内 skill 存在"      'test -f .agents/skills/24frames-vault/SKILL.md'
chk "P0-4 skill 无失效路径"     '! grep -rq "OH-WorkSpace\|03_任务\|06_灵感库" .agents/skills/'
chk "P0-5 三份嵌套 AGENTS.md"   'test -f 02_项目/AGENTS.md -a -f 06_AI/AGENTS.md -a -f 05_档案/会议存档/AGENTS.md'
chk "P0-6 HOME 无 dataview"     '! grep -q "```dataview" HOME.md'
chk "P0-6 .base 看板存在"       'test -f .base/项目看板.base'
chk "P0-7 .hermes 未被跟踪"     '! git ls-files --error-unmatch .hermes >/dev/null 2>&1'
chk "P0-8 会议命名统一"         '! ls 05_档案/会议存档/ | grep -qvE "^[0-9]{4}-[0-9]{2}-[0-9]{2}_"'
chk "P0-9 raw 层只读已声明"     'grep -q "raw 层只读" AGENTS.md'
chk "P0-10 _index 机器可读"     'grep -qE "^- \\[\\[" 00_系统/_index.md'
chk "P0-11 回答落库规则已写"     'grep -q "回答要落库" AGENTS.md'
chk "根 AGENTS.md ≤150 行"      '[ "$(wc -l < AGENTS.md)" -le 150 ]'

echo
if [ "$fail" = 0 ]; then echo "🎉 P0 全部通过"; else echo "⚠️  有未通过项，见上"; fi
exit "$fail"
```

> 这份脚本本身就是 P0 的交付物之一，放到 `00_系统/agent/verify-p0.sh` 并 `chmod +x`。

## 关联

- [[24帧运营库-DSH优化方案]]
- [[附件B-Agent落地执行手册]]
- [[运营手册]] ｜ [[归档操作规范]] ｜ [[_index]] ｜ [[HOME]]
- 配套调研：[[AI-agent与个人知识库协作-公开最佳实践调研]] ｜ [[多agent协作-长期记忆-知识资产治理-工程化素材]]
