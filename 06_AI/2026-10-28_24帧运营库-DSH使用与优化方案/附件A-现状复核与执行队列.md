---
type: draft
name: 附件A-现状复核与执行队列
status: review
editable: true
audience: both
created: 2026-10-28
updated: 2026-10-28
summary: 24 张可执行任务卡，含文件清单、验证命令、完成标准与回滚
source: ai-generated
tags: [执行队列, 验收, DSH]
---

# 附件A · 现状复核与执行队列

> 配套 [[24帧运营库-DSH使用与优化方案-v2]]。
> 每张卡都能独立执行；依赖未完成时不要领卡。
> 命令统一先设 `VAULT="$HOME/Documents/24帧运营库"`，避免相对路径出错。

---

## 0. 领卡规则

1. 读卡片的 `Depends`。依赖项在 `_changelog.md` 里能查到完成记录才开工。
2. 只改 `Files` 列出的文件。需要改别的文件，先在报告里申请。
3. 执行 `Steps`，然后跑 `Verify`，把输出原样贴进报告。
4. 按 `Done` 自查，全部满足才算完成。
5. 记 changelog：`## [YYYY-MM-DD HH:mm] 操作类型 | 文件名`。
6. 报告五段：`TASK / CHANGED / VERIFY / RISK / NEXT`。

状态标记：`待做` / `进行中` / `完成` / `阻塞`。本文件只记录任务定义，状态以 `_changelog.md` 和 `HOME.md` 为准。

---

## 1. 任务索引

| ID | 任务 | Owner | 预计 | 依赖 | 风险 |
|---|---|---|---:|---|---|
| P0-1 | 关闭公开仓库 | 宇航员 | 10 分钟 | — | 红灯，仅本人 |
| P0-2 | 重写根 AGENTS | 图书管理员 | 1 小时 | P0-3 | 低 |
| P0-3 | 落盘 `_schema.md` | 图书管理员 | 1 小时 | — | 低 |
| P0-4 | 规范三合一 | 图书管理员 | 1.5 小时 | P0-3 | 中 |
| P0-5 | Skill 迁入并瘦身 | 图书管理员 | 1 小时 | P0-2 | 中 |
| P0-6 | 隐私元数据清理 | 归档员 | 1 小时 | 宇航员确认 | 红灯，批量 |
| P0-7 | 修正全局 AGENTS 路径 | 图书管理员 | 5 分钟 | — | 低 |
| P1-1 | 索引生成器 | 图书管理员 | 1.5 小时 | P0-3 | 低 |
| P1-2 | HOME 静态看板 | 图书管理员 | 1 小时 | P0-3、P1-5 | 低 |
| P1-3 | Lint v2 | 审计员 | 2 小时 | P0-3 | 中 |
| P1-4 | 嵌套 AGENTS | 图书管理员 | 1 小时 | P0-2 | 低 |
| P1-5 | 任务语法迁移 | 图书管理员 | 3 小时 | P0-3 | 中 |
| P1-6 | 清死 Dataview | 图书管理员 | 1 小时 | P1-1、P1-2 | 低 |
| P1-7 | changelog 规范化 | 图书管理员 | 1 小时 | — | 低 |
| P1-8 | Review 队列清零 | 宇航员 + 审计员 | 1 小时 | — | 中 |
| P1-9 | 归档去重与工具外迁 | 归档员 | 2 小时 | 宇航员确认 | 红灯，批量 |
| P2-1 | FTS5 检索 | 图书管理员 | 2 小时 | P1-1 | 低 |
| P2-2 | headless + launchd | 图书管理员 | 2 小时 | P1-3 | 中 |
| P2-3 | hooks 写入拦截 | 审计员 | 2 小时 | P1-3 | 中 |
| P2-4 | Astronaut 桥接 | 图书管理员 | 1 小时 | P0-2 | 低 |
| P2-5 | Bases 视图 | 图书管理员 | 1 小时 | P1-6 | 低 |
| P2-6 | 媒体与 git 策略 | 审计员 | 2 小时 | P0-1 | 红灯 |
| P2-7 | 语义 lint | 审计员 | 每周 30 分钟 | P2-2 | 低 |
| P2-8 | 指标看板 | 审计员 | 1 小时 | P1-3 | 低 |
| P2-9 | Skill 目录瘦身 | 图书管理员 | 1.5 小时 | — | 中 |
| P3-1 | 查询回写 routine | 写作者 | 每周 30 分钟 | P1-1 | 低 |
| P3-2 | 季度归档与复盘 | 归档员 | 每季 2 小时 | P1-9 | 低 |
| P3-3 | v1 方案归档 | 图书管理员 | 10 分钟 | — | 低 |

---

# P0 · 今天

## P0-1 关闭公开仓库

- **Owner**：宇航员本人
- **Depends**：无
- **Time**：10 分钟
- **Why**：公开 `main` 分支含 16 篇会议逐字稿、40 篇写作 DNA、14 篇媒体材料。任何一次 `git push` 都会继续公开。
- **Files**：GitHub 仓库设置，不涉及本地文件
- **Steps**：
  1. 打开 `https://github.com/yhy2049/wechat-articles/settings`。
  2. 拉到 **Danger Zone** → **Change repository visibility** → **Make private**。
  3. 按提示输入仓库名 `yhy2049/wechat-articles` 确认。
  4. 回到本地，检查 remote 是否仍指向该仓库：
     ```bash
     cd "$HOME/Documents/24帧运营库"
     git remote -v
     ```
  5. **不要**立刻 `git push`。仓库转私有后，历史仍然完整；是否清史、是否迁新仓库，等 P2-6 再决定。
- **Verify**：
  ```bash
  curl -s https://api.github.com/repos/yhy2049/wechat-articles | python3 -c "import sys,json; print(json.load(sys.stdin).get('private'))"
  # 期望输出：True
  ```
- **Done**：`private` 为 `True`；`_changelog.md` 记一条「仓库可见性变更」。
- **Rollback**：只在误操作时改回 public，并立即评估暴露时长。
- **Agent 规则**：不代做、不催促、不尝试用 token 改设置。完成后由 agent 记 changelog。

---

## P0-2 重写根 `AGENTS.md`

- **Owner**：图书管理员
- **Depends**：P0-3
- **Time**：1 小时
- **Why**：当前 2,695 字节、55 行，只列了 8 条硬规则，没有字段契约、任务语法、四层边界；agent 读完仍不知道该怎么落笔。
- **Files**：`AGENTS.md`
- **Steps**：
  1. 备份：`cp AGENTS.md /tmp/AGENTS.md.bak`。
  2. 用 [[附件B-模板与脚本]] 的 **B1** 全文替换。
  3. 把 B1 里的占位路径改成实际路径（本库为 `/Users/haishangyinghuo/Documents/24帧运营库`）。
  4. 检查行数，超过 150 行就删细节，移到嵌套 AGENTS 或 `_schema.md`。
  5. 记 changelog。
- **Verify**：
  ```bash
  cd "$HOME/Documents/24帧运营库"
  wc -l AGENTS.md
  grep -n "05_档案/会议存档\|audience: public\|git push\|## 待办" AGENTS.md
  ```
  期望：行数 ≤150；四类关键词都能命中。
- **Done**：新会话里只读 `AGENTS.md`，agent 能回答三个问题：会议放哪、任务写哪、哪些操作必须先问。
- **Rollback**：`git restore --source=pre-optimize-2026-10-28 -- AGENTS.md`

---

## P0-3 落盘 `_schema.md`

- **Owner**：图书管理员
- **Depends**：无
- **Time**：1 小时
- **Why**：20 种 `type`、9 种 `status`、12 种 `direction` 写法，根因是没有唯一字段规则。
- **Files**：`_schema.md`（新建）
- **Steps**：
  1. 用 [[附件B-模板与脚本]] 的 **B2** 全文创建 `_schema.md`。
  2. 确认 5 个方向与 `01_方向/` 实际目录一致：AI影像、宣发平台、影视创作、策展人、观影团。
  3. 确认 10 个 `type`、4 个 `status`、4 个 `audience`、6 个 `progress`、5 个 `stage`。
  4. 在 `运营手册.md` 顶部加一行：「字段取值以 [[_schema]] 为准」。
  5. 记 changelog。
- **Verify**：
  ```bash
  cd "$HOME/Documents/24帧运营库"
  test -f _schema.md && echo OK
  grep -c '^| `' _schema.md
  grep -n "direction" _schema.md | head
  ```
- **Done**：`_schema.md` 能被 P1-3 的 lint 读取；任何 agent 新建文件前只需读这一份。
- **Rollback**：删除新文件；恢复 `运营手册.md`。

---

## P0-4 规范三合一

- **Owner**：图书管理员
- **Depends**：P0-3
- **Time**：1.5 小时
- **Why**：手册、归档规范、录音 SOP 三份相互冲突；agent 读到哪份就按哪份做。
- **Files**：
  - `00_系统/运营手册.md`（重写）
  - `00_系统/归档操作规范.md`（修正）
  - `00_系统/agent/录音会议存档SOP.md`（移入 `_archive/`）
- **Steps**：
  1. 用 **B3** 的骨架重写 `运营手册.md`。只留真实存在的章节：目录权限、文件类型、任务、归档、灵感、项目、lint、周检、决策灯、协作、复利。删除对 §4/§6/§8/§10/§13/§15 的空引用，改为指向 `_schema.md` / 本附件 / lint。
  2. 修正 `归档操作规范.md`：
     - Step 1 的「存入项目目录 `02_归档文件/`」改为 `05_档案/会议存档/`。
     - Step 2 的「`04_人物/`」改为 `03_人物/`。
     - 删除「任务文件 `type: task`」整段，改为「待办落到项目页 `## 待办`，格式见 `_schema.md`」。
     - frontmatter 表改为与 `_schema.md` 一致：`type/name/status/audience/editable/created/updated/summary/date/participants/related_projects/related_people/direction`。
  3. 把 `00_系统/agent/录音会议存档SOP.md` 移到 `00_系统/agent/_archive/`，不删除。移动前在文件顶部加一行：「已合并进 [[归档操作规范]]，本文件仅存档」。
  4. 全库搜索旧路径，确认真实规范文件里没有残留。
- **Verify**：
  ```bash
  cd "$HOME/Documents/24帧运营库"
  grep -n "02_归档文件/\|04_人物/\|type: task" 00_系统/运营手册.md 00_系统/归档操作规范.md || echo "NO_STALE_RULES"
  ls 00_系统/agent/_archive/录音会议存档SOP.md
  ```
  期望：`NO_STALE_RULES`；文件在 `_archive/`。
- **Done**：三份规则合并为两份（手册管流程、归档规范管归档），字段规则只在 `_schema.md`。
- **Rollback**：`git restore` 两个规范文件；把 SOP 移回原位。

---

## P0-5 Skill 迁入并瘦身

- **Owner**：图书管理员
- **Depends**：P0-2
- **Time**：1 小时
- **Why**：全局 `24frames-vault` 44.9 KB / 1,052 行，含旧路径 `~/Documents/OH-WorkSpace`、旧目录 `03_任务`、旧 frontmatter 建议；每次调用烧 1 万 token 以上。
- **Files**：
  - `.agents/skills/24frames-vault/SKILL.md`（新建）
  - `.agents/skills/24frames-vault/references/*.md`（新建）
  - `.agents/skills/vault-archiving/SKILL.md`（新建）
  - `~/.agents/skills/24frames-vault/`（备份后移除）
  - `~/.agents/skills/vault-archiving/`（备份后移除）
- **Steps**：
  1. 备份全局 skill：
     ```bash
     mkdir -p "$HOME/.agents/skills/_backup-2026-10-28"
     cp -R "$HOME/.agents/skills/24frames-vault" "$HOME/.agents/skills/_backup-2026-10-28/"
     cp -R "$HOME/.agents/skills/vault-archiving" "$HOME/.agents/skills/_backup-2026-10-28/"
     ```
  2. 在库内建目录：
     ```bash
     cd "$HOME/Documents/24帧运营库"
     mkdir -p .agents/skills/24frames-vault/references .agents/skills/vault-archiving
     ```
  3. 用 **B4** 创建两个 `SKILL.md`；用 **B5** 拆出 `schema.md`、`archiving.md`、`writing.md` 三个参考文件。
  4. 入口只保留：触发条件、读取顺序、三条硬规则、references 链接。
  5. 验证库内版本被识别后，再移除全局副本（不要先删）。
  6. 记 changelog。
- **Verify**：
  ```bash
  cd "$HOME/Documents/24帧运营库"
  wc -l .agents/skills/24frames-vault/SKILL.md .agents/skills/vault-archiving/SKILL.md
  grep -rn "OH-WorkSpace\|03_任务\|06_灵感库" .agents/skills || echo "NO_STALE_PATHS"
  ```
  期望：≤150 行 / ≤120 行；`NO_STALE_PATHS`。
- **Done**：新会话输入 `/24frames-vault`，agent 引用的是库内版本（可用 `updated: 2026-10-28` 核对），且不再加载旧的长文。
- **Rollback**：从 `_backup-2026-10-28/` 恢复全局副本；删除库内 `.agents/skills`。

---

## P0-6 隐私元数据清理

- **Owner**：归档员
- **Depends**：宇航员确认（批量改 61 个 public 页 + 15 个缺 audience 页，红灯）
- **Time**：1.5 小时
- **Why**：全库 61 个 `public` 页，0 个带 `public_approved`；其中 26 个人物/会议页含资金分工、团队关系、个人访谈，风险最高。`public` 当前被当作「不保密」。
- **Files**：全库活跃页；优先 `03_人物/*.md`、`05_档案/会议存档/*.md`
- **Steps**：
  1. 生成待改清单（全库）：
     ```bash
     cd "$HOME/Documents/24帧运营库"
     grep -rl '^audience: public' --include='*.md' 01_方向 02_项目 03_人物 04_灵感 05_档案 06_AI | sort
     grep -rL '^audience:' --include='*.md' 01_方向 02_项目 03_人物 04_灵感 05_档案 06_AI | sort
     ```
  2. 人物页、会议页默认改为 `owner`；确需给合作方看的，保留 `public` 并补 `public_approved` 与 `redacted: true`。
  3. 项目、方向、灵感、品牌材料默认改为 `both`；只有确实要外发的计划书/媒体介绍才保留 `public` 并补齐审批字段。
  4. 缺 `audience` 的 15 篇活跃页按类型补：人物/会议 `owner`，项目/方向 `both`，草稿 `agent`。
  5. 只改 frontmatter 与 `updated`，**不动正文**。
  6. 记 changelog，列出改了哪些文件。
- **Verify**：
  ```bash
  cd "$HOME/Documents/24帧运营库"
  python3 00_系统/agent/vault-lint.py --file 03_人物/宇航员.md
  # 不再出现 PUBLIC_UNAPPROVED
  grep -rl '^audience: public' --include='*.md' . | wc -l
  # 期望：仅剩带 public_approved + redacted 的文件，或 0
  ```
- **Done**：所有保留 `public` 的页面都有 `public_approved` 和 `redacted: true`；其余改为 `owner`/`both`/`agent`；缺 audience 的活跃页清零。
- **Rollback**：`git restore` 指定文件。

---

## P0-7 修正全局 AGENTS 路径

- **Owner**：图书管理员
- **Depends**：无
- **Time**：5 分钟
- **Why**：`~/.dsh/AGENTS.md` 第 43、51 行仍写 `~/Documents/OH-WorkSpace/24帧运营库` 和 `~/Github/24frames-web`，实际路径分别是 `~/Documents/24帧运营库` 和 `~/Documents/24FRAMES-WEB`。每个会话开局就拿到错误环境。
- **Files**：`~/.dsh/AGENTS.md`
- **Steps**：
  1. 备份：`cp ~/.dsh/AGENTS.md ~/.dsh/AGENTS.md.bak-2026-10-28`。
  2. 替换两处路径：
     - `~/Documents/OH-WorkSpace/24帧运营库` → `~/Documents/24帧运营库`
     - `~/Github/24frames-web` → `~/Documents/24FRAMES-WEB`
  3. 把「7目录」改为「5+1 目录」；把「技能：24frames-vault」改为「技能：库内 `.agents/skills/24frames-vault`」。
  4. 记 changelog（库内日志记一笔，说明改了全局文件）。
- **Verify**：
  ```bash
  grep -n "OH-WorkSpace\|Github/24frames-web" "$HOME/.dsh/AGENTS.md" || echo "PATHS_OK"
  grep -n "Documents/24帧运营库\|Documents/24FRAMES-WEB" "$HOME/.dsh/AGENTS.md"
  ```
- **Done**：`PATHS_OK`，两处新路径可命中。
- **Rollback**：`cp ~/.dsh/AGENTS.md.bak-2026-10-28 ~/.dsh/AGENTS.md`

---

# P1 · 第 1 周

## P1-1 索引生成器

- **Owner**：图书管理员
- **Depends**：P0-3
- **Time**：1.5 小时
- **Why**：`_index.md` 只是目录树，没有摘要；92 个孤儿页无法从索引到达。
- **Files**：`00_系统/agent/vault-index.py`（新建）、`00_系统/_index.md`（生成）
- **Steps**：
  1. 用 **B6** 创建脚本（逐字源码见 [[附件C-脚本源码]] C1）。
  2. 先 dry-run：`python3 00_系统/agent/vault-index.py --stdout > /tmp/index-preview.md`，人工看前 50 行。
  3. 确认分组正确（方向/项目/项目参考文档/人物/灵感/知识库/品牌策略/系统/会议/成稿/方向参考文档/其他），缺失 `summary` 的写 `待补摘要`。
  4. 正式写入 `_index.md`（整文件生成，不保留手写区）。
  5. 记 changelog。
- **Verify**：
  ```bash
  cd "$HOME/Documents/24帧运营库"
  python3 00_系统/agent/vault-index.py --check
  grep -c '^- \[\[' 00_系统/_index.md
  grep -c '未归类' 00_系统/_index.md
  ```
  期望：`--check` 返回 0；条目数 ≥230；存在「未归类」段。
- **Done**：索引 3 秒内生成；每个非 `06_AI/` 活跃页有条目（含项目参考文档）；孤儿页能在「无入链」段找到。
- **Rollback**：`git restore -- 00_系统/_index.md`；删除脚本。

---

## P1-2 HOME 静态看板

- **Owner**：图书管理员
- **Depends**：P0-3、P1-5
- **Time**：1 小时
- **Why**：`HOME.md` 的 4 个 Dataview 查询全部无输出，首页无法回答「今天做什么」。
- **Files**：`00_系统/agent/vault-home.py`（新建）、`HOME.md`（生成）
- **Steps**：
  1. 用 **B7** 创建脚本（逐字源码见 [[附件C-脚本源码]] C2）。
  2. 生成五段：今日焦点（手写区）、在做（`progress: 进行中` + `next_action`）、待办（项目页 `## 待办`）、在等（`progress: 等待中`）、待审（`status: review`）、最近更新（7 天）。
  3. 手写区用 `<!-- MANUAL:START -->` / `<!-- MANUAL:END -->` 包住，脚本重生成时保留块内内容。
  4. 记 changelog。
- **Verify**：
  ```bash
  cd "$HOME/Documents/24帧运营库"
  python3 00_系统/agent/vault-home.py --check
  grep -n "进行中项目\|等我拍板\|等待中" HOME.md
  ```
- **Done**：不装任何插件，Obsidian 打开 `HOME.md` 能看到表格；项目数与 `02_项目` 一致。
- **Rollback**：`git restore -- HOME.md`；删除脚本。

---

## P1-3 Lint v2

- **Owner**：审计员
- **Depends**：P0-3
- **Time**：2 小时
- **Why**：现有 `vault-health-check.py` 只查格式，不查枚举、目录归属、隐私、任务语法；管道到 `tail` 时退出码还会被吞。
- **Files**：`00_系统/agent/vault-lint.py`（新建）、`00_系统/agent/.vault-lint-baseline.json`（生成）
- **Steps**：
  1. 用 **B8** 创建脚本（逐字源码见 [[附件C-脚本源码]] C3）。检查项：
     - 必填字段与枚举（`type/status/audience/progress/stage/direction`）
     - 目录归属（meeting 在会议存档、project 在 `02_项目/<名>/`、person 在 `03_人物`）
     - 命名（会议 `YYYY-MM-DD_主题.md`、`06_AI` 目录 `YYYY-MM-DD_主题`、根目录无散落文件）
     - `public` 审批字段
     - 双链解析、孤儿、`## 关联`
     - changelog 格式（最近 200 行）
     - 禁用物：`node_modules`、`.hermes`、`.DS_Store`、` ```dataview `
     - 重复 basename
  2. 加 `--file`（单文件）、`--json`、`--write-baseline`、`--no-baseline`。
  3. 先跑全库，`--write-baseline` 记录约 600 条 `path|code` 豁免（2026-10-28 03:30 实测 605 条，553 error / 269 warning；库在变，以当场输出为准）；之后只报新增问题。
  4. 修前 10 个新问题，其余排期。
  5. 记 changelog。
- **Verify**：
  ```bash
  cd "$HOME/Documents/24帧运营库"
  time python3 00_系统/agent/vault-lint.py
  echo "EXIT:$?"
  ```
  期望：运行 <5 秒；退出码 0 或 1（只有警告）；错误列表可读。
- **Done**：故意造一个 `type: 项目会议` 的文件，lint 报 error；删除后恢复 0。
- **Rollback**：删除脚本与 baseline；旧脚本保留。

---

## P1-4 嵌套 AGENTS

- **Owner**：图书管理员
- **Depends**：P0-2
- **Time**：1 小时
- **Why**：根 AGENTS 不能无限膨胀；目录规则应只在进入该目录时加载。
- **Files**：
  - `02_项目/AGENTS.md`
  - `03_人物/AGENTS.md`
  - `05_档案/AGENTS.md`
  - `06_AI/AGENTS.md`
  - `00_系统/AGENTS.md`
- **Steps**：
  1. 用 **B9** 的五个模板创建。
  2. 每份只写本目录特有规则，不重复根 AGENTS。
  3. 每份 ≤3 KB。
  4. 记 changelog。
- **Verify**：
  ```bash
  cd "$HOME/Documents/24帧运营库"
  for f in 02_项目 03_人物 05_档案 06_AI 00_系统; do wc -c "$f/AGENTS.md"; done
  ```
- **Done**：五份都存在且 ≤3 KB；内容无重复的全局规则。
- **Rollback**：删除五份文件。

---

## P1-5 任务语法迁移

- **Owner**：图书管理员
- **Depends**：P0-3
- **Time**：3 小时
- **Why**：11 个项目页有 5 种任务写法，agent 无法稳定回答「下一步做什么」。
- **Files**：11 个项目主文件（`02_项目/<项目>/<项目>.md`）
- **Steps**：
  1. 先改一个样板：`02_项目/苏宁影城路演合作/苏宁影城路演合作.md`。加 `next_action`、`next_action_due`、`waiting_for`，把正文里的待办整理成 `## 待办`，加 `## 决策记录`。
  2. 让宇航员确认样板格式。
  3. 其余 10 个按样板迁移。没有待办的写 `next_action: 无`，不要留空。
  4. 已终止项目 `北回归线以北-成都观影团` 保留历史，`progress: 已终止`，不补任务。
  5. 记 changelog。
- **Verify**：
  ```bash
  cd "$HOME/Documents/24帧运营库"
  for f in 02_项目/*/*.md; do
    case "$f" in */01_参考文档/*|*/02_归档文件/*|*/03_AI文档/*|*/04_草稿/*) continue;; esac
    printf "%s: " "$f"; grep -c '^## 待办' "$f"
  done
  ```
  期望：11 个项目主文件都输出 `1`（已终止项目可为 `0`，但要有说明）。
- **Done**：任选一个项目问 agent「下一步」，答案与 `## 待办` 第一条一致。
- **Rollback**：逐文件 `git restore`。

---

## P1-6 清死 Dataview

- **Owner**：图书管理员
- **Depends**：P1-1、P1-2
- **Time**：1 小时
- **Why**：12 个文件含查询块，Obsidian 没装 Dataview，全部渲染为空白。
- **Files**（12 个实际文件）：
  - `HOME.md`
  - `00_系统/_index.md`
  - `01_方向/AI影像/AI影像.md`
  - `01_方向/影视创作/影视创作.md`
  - `01_方向/策展人/策展人.md`
  - `01_方向/观影团/观影团.md`
  - `02_项目/何力长片-浮生若丽/何力长片-浮生若丽.md`
  - `02_项目/影视创作-24帧首部短片/影视创作-24帧首部短片.md`
  - `02_项目/影视创作-第二部短片-弄死一条过/影视创作-第二部短片-弄死一条过.md`
  - `02_项目/望福美食地图/望福美食地图.md`
  - `02_项目/脱口秀-24帧TalkShow/脱口秀-24帧TalkShow.md`
  - `04_灵感/知识库/营销策略/Frontmatter规范与文件管理学习笔记.md`
- **Steps**：
  1. 每个方向页：删除查询块，替换为一行 `> 实时看板见 [[HOME]]；项目清单见 [[_index]]。`
  2. 每个项目页：删除查询块；项目自身状态写在 frontmatter，不再用查询展示。
  3. `HOME.md`、`_index.md` 由 P1-1/P1-2 生成，确保生成器不写 Dataview。
  4. 学习笔记里的示例块改为 ` ```text `，避免被当成真查询。
  5. 记 changelog。
- **Verify**：
  ```bash
  cd "$HOME/Documents/24帧运营库"
  grep -rl '```dataview' --include='*.md' . | grep -v '06_AI/2026-10-06\|06_AI/2026-10-28' || echo "NO_DATAVIEW"
  ```
  期望：`NO_DATAVIEW`（排除两份方案文档里的示例）。
- **Done**：Obsidian 打开任意页面无空白查询块；首页信息由静态表提供。
- **Rollback**：逐文件 `git restore`。

---

## P1-7 changelog 规范化

- **Owner**：图书管理员
- **Depends**：无
- **Time**：1 小时
- **Why**：140 条里 12 条格式不合规（`## 2026-09-27（修版）`、`## 2026-09-27 17:30 ...`），无法用 `grep "^## \["` 取最近记录。
- **Files**：`00_系统/_changelog.md`
- **Steps**：
  1. 备份。
  2. 用脚本只改标题行格式，不改正文：
     - `## YYYY-MM-DD HH:mm 类型 | 标题` → `## [YYYY-MM-DD HH:mm] 类型 | 标题`
     - `## YYYY-MM-DD（说明）` → `## [YYYY-MM-DD 00:00] 未分类 | 说明`
  3. 无法判断类型的，统一写 `未分类`。
  4. 在文件头加格式说明和取最近 5 条的命令。
  5. 记一条新的 changelog 记录本次整理。
- **Verify**：
  ```bash
  cd "$HOME/Documents/24帧运营库"
  grep '^## ' 00_系统/_changelog.md | grep -vc '^## \[[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\} [0-9]\{2\}:[0-9]\{2\}\] '
  # 期望：0
  grep '^## \[' 00_系统/_changelog.md | tail -5
  ```
- **Done**：所有二级标题都能被 `^## \[` 匹配；最近 5 条可读。
- **Rollback**：`git restore -- 00_系统/_changelog.md`

---

## P1-8 Review 队列清零

- **Owner**：宇航员 + 审计员
- **Depends**：无
- **Time**：1 小时
- **Why**：11 个 `status: review`，其中 7 个超过 7 天，最早的挂了 5 个月；review 成了黑洞。本次处理 8 个历史页，3 份 v2 方案页留到发布时再定。
- **Files**：
  - `04_灵感/品牌策略/品牌策略备忘.md`
  - `04_灵感/品牌策略/品牌目标.md`
  - `04_灵感/品牌策略/品牌手册.md`
  - `05_档案/会议存档/2026-06-01-何力长片项目面谈.md`
  - `06_AI/2026-10-06_24帧运营库-DSH优化方案/` 三份
  - `06_AI/2026-10-09_埃及电影生日快乐影评/生日快乐-影评.md`
- **Steps**：
  1. 逐篇给宇航员看摘要，选：`final` / `archive` / 继续 `review` 并写截止日。
  2. 品牌策略三份若已定稿，改 `final`；未定稿改 `draft` 并写 `review_due`。
  3. v1 三份在 P3-3 统一处理，本次先标 `archive` 或保留 `review` 并写截止日。
  4. 影评若已发布，改 `final` 并注明发布渠道；未发布改 `draft`。
  5. 记 changelog。
- **Verify**：
  ```bash
  cd "$HOME/Documents/24帧运营库"
  grep -rl '^status: review' --include='*.md' . | wc -l
  # 期望：0，或仅剩带 review_due 且未超期的
  ```
- **Done**：没有超过 7 天的 `review`；HOME 的「等我拍板」段为空或只有 3 条以内。
- **Rollback**：逐文件恢复 status。

---

## P1-9 归档去重与工具外迁

- **Owner**：归档员
- **Depends**：宇航员确认（移动 302 个文件，红灯）
- **Time**：2 小时
- **Why**：公众号存档有 302 篇重复；`_skill/node_modules` 19 MB 在库内；`.github-pages` 7.0 MB 是站点镜像。
- **Files**：
  - `05_档案/公众号存档/.github-pages/`（移出）
  - `05_档案/公众号存档/_skill/`（移出）
  - `05_档案/公众号存档/_meta/corpus-overview.md`（更新）
  - `05_档案/公众号存档/_meta/removals.md`（更新）
  - `.gitignore`（新建）
- **Steps**：
  1. 先算重复，确认年目录与镜像的对应关系：
     ```bash
     cd "$HOME/Documents/24帧运营库/05_档案/公众号存档"
     python3 - <<'PY'
     import hashlib, pathlib
     def h(p): return hashlib.md5(p.read_bytes()).hexdigest()
     year={h(p):p for p in pathlib.Path('.').glob('[0-9][0-9][0-9][0-9]/*.md')}
     gp={h(p):p for p in pathlib.Path('.github-pages/articles').glob('*.md')}
     print('year',len(year),'gp',len(gp),'dup',len(set(year)&set(gp)))
     PY
     ```
  2. 把整个 `.github-pages/` 移到库外 `~/Documents/24frames-site-archive/`；移动前确认站点仓库有同样的内容。
  3. 把 `_skill/` 移到 `~/.agents/tools/wechat-archive/`；`node_modules` 不跟库走。
  4. 新建 `.gitignore`：`node_modules/`、`.hermes/`、`00_系统/agent/.cache/`、`00_系统/agent/logs/`、`*.m4a`、`*.mp4`、`*.wav`、`.DS_Store`。
  5. 更新 `_meta` 统计：年目录 302 篇、去重后 302 篇（2026-10-28 已核对）。
  6. 记 changelog。
- **Verify**：
  ```bash
  cd "$HOME/Documents/24帧运营库"
  du -sh . 05_档案/公众号存档
  test ! -d 05_档案/公众号存档/.github-pages && echo "MIRROR_MOVED"
  test ! -d 05_档案/公众号存档/_skill/node_modules && echo "NODE_MODULES_MOVED"
  ```
- **Done**：库体积下降 ≥24 MB；站点仍能从库外构建；`_meta` 数字与实际一致。
- **Rollback**：从 `~/Documents/24frames-site-archive/` 移回；`git restore` `_meta`。

---

# P2 · 第 2–4 周

## P2-1 FTS5 检索

- **Owner**：图书管理员
- **Depends**：P1-1
- **Time**：2 小时
- **Why**：grep 对中文断词差，找不到「谁在哪次会上说过资金怎么分」。
- **Files**：`00_系统/agent/vault-search.py`（新建）、`00_系统/agent/.vault-search.db`（生成，gitignore）
- **Steps**：
  1. 用 **B10** 创建脚本（逐字源码见 [[附件C-脚本源码]] C4），SQLite FTS5。**不用 `trigram`**：实测 2 字中文查询零命中；把 CJK 文本切成重叠 bigram 存入 `unicode61` 索引。
  2. 建索引：标题、summary、正文；默认排除 `.github-pages` 与 `_skill/node_modules`。
  3. 支持 `--build`、`--stats`、`--limit`、`--json`、`--active-only`；`--build` 重建。
  4. 中文查询走 bigram；英文按整词；单字查询回退 `LIKE`。
  5. 记 changelog。
- **Verify**：
  ```bash
  cd "$HOME/Documents/24帧运营库"
  python3 00_系统/agent/vault-search.py --build
  python3 00_系统/agent/vault-search.py "资金 分工" --limit 5
  python3 00_系统/agent/vault-search.py "放映" --limit 3
  ```
  期望：三条命令都返回带路径与片段的结果；「放映」这类 2 字词必须有命中。
- **Done**：中文 2 字查询有结果；全库索引 <5 秒；结果带文件路径和上下文。
- **Rollback**：删除脚本与 `.vault-search.db`。

---

## P2-2 headless + launchd

- **Owner**：图书管理员
- **Depends**：P1-3
- **Time**：2 小时
- **Why**：夜间 lint/index/home 目前靠人记得；`dsh schedule` 不能跨会话。
- **Files**：
  - `~/.dsh/profiles/headless/cordis.patch.yml`
  - `00_系统/agent/nightly.sh`
  - `~/Library/LaunchAgents/cc.frames24.vault-nightly.plist`
- **Steps**：
  1. 备份 `cordis.patch.yml`。
  2. 从 `~/.dsh/profiles/desktop/cordis.patch.yml` 复制 `llm-pi-ai` 与 `agent-default-model` 两块，模型选 `sensenova-6.8-flash-lite`。
  3. 写 `nightly.sh`：`source ~/.zshrc`，跑 lint、index、home，输出日志到 `00_系统/agent/logs/`。
  4. 先手动跑 `dsh --profile headless "读 _index.md，输出项目数"`，确认模型路由可用。
  5. 再装 launchd，先设 `StartCalendarInterval` 02:00，`RunAtLoad` false。
  6. 记 changelog。
- **Verify**：
  ```bash
  launchctl list | grep frames24
  dsh --profile headless "读 $HOME/Documents/24帧运营库/_index.md，输出项目数"
  tail -20 "$HOME/Documents/24帧运营库/00_系统/agent/logs/nightly-$(date +%F).log"
  ```
- **Done**：连续两晚自动生成日志；失败时日志有 stderr。
- **Rollback**：`launchctl unload` 并删除 plist；恢复 patch 备份。

---

## P2-3 hooks 写入拦截

- **Owner**：审计员
- **Depends**：P1-3
- **Time**：2 小时
- **Why**：lint 靠自觉跑；写错字段时没有即时反馈。
- **Files**：
  - `.claude/hooks.json`
  - `.claude/hooks/post-write-lint.sh`
  - `.claude/hooks/guard-archive.sh`
  - DSH profile 挂载配置
- **Steps**：
  1. 用 **B11** 创建两个脚本（逐字源码与 `hooks.json` 见 [[附件C-脚本源码]] C5）。`post-write-lint.sh` 从 stdin 取 `tool_input.file_path`，跑 `vault-lint.py --file`；有 error 时 exit 2，stderr 写具体问题。
  2. `guard-archive.sh`：`05_档案/公众号存档/`、`05_档案/媒体/`、`05_档案/放映数据/` 一律 exit 2；`05_档案/会议存档/` 已存在文件 exit 2，新文件必须匹配 `YYYY-MM-DD_主题.md` 且 frontmatter 含 `type/date/participants/direction/audience`。
  3. 写 `.claude/hooks.json`，只挂 `PostToolUse` 与 `PreToolUse`，不挂 `Stop`。
  4. 在临时 profile 挂载 `@deepseek-ai/dsh-hooks-claude-code`，`configPath` 指库内 `.claude/hooks.json`，`projectDir` 指库根。
  5. 用假 payload 测两个脚本，再在正式会话试写一个非法文件。
  6. 记 changelog。
- **Verify**：
  ```bash
  cd "$HOME/Documents/24帧运营库"
  echo '{"tool_input":{"file_path":"/tmp/bad.md"}}' | .claude/hooks/post-write-lint.sh; echo "EXIT:$?"
  echo '{"tool_input":{"file_path":"05_档案/会议存档/2026-06-01-何力长片项目面谈.md","content":"x"}}' | .claude/hooks/guard-archive.sh; echo "EXIT:$?"
  ```
  期望：前者对非法文件 exit 2；后者对已存在会议 exit 2。
- **Done**：非法写入被拦，合法写入不拦；连续 10 次正常编辑无误报。
- **Rollback**：移除 profile 挂载，删除 `.claude/`。

---

## P2-4 Astronaut 桥接

- **Owner**：图书管理员
- **Depends**：P0-2
- **Time**：1 小时
- **Why**：preset 启动读 9 个文件，多个 `memory/*` 不存在；库与 preset 是两套记忆。
- **Files**：
  - `~/.dsh/.agent-presets/astronaut/agent.cordis.yml`
  - `~/.dsh/.agent-presets/astronaut/memory/VAULT-BRIDGE.md`（新建）
- **Steps**：
  1. 备份 preset 目录。
  2. 删掉启动序列里不存在的文件读取，保留 `persona/`、`memory/axioms/INDEX.md`、`memory/WANT-TO-DO.md`、`memory/OBSERVATIONS.md`。
  3. 新建 `VAULT-BRIDGE.md`，写四个入口：库根 AGENTS、`_schema.md`、`HOME.md`、`_index.md`；写一句「业务事实以库为准，persona 不复制项目细节」。
  4. 启动序列加一步：读 `VAULT-BRIDGE.md`。
  5. 记 changelog。
- **Verify**：
  ```bash
  grep -n "VAULT-BRIDGE\|memory/" "$HOME/.dsh/.agent-presets/astronaut/agent.cordis.yml" | head -20
  test -f "$HOME/.dsh/.agent-presets/astronaut/memory/VAULT-BRIDGE.md" && echo OK
  ```
- **Done**：新 preset 会话启动无「文件不存在」；问「库在哪」，回答正确路径。
- **Rollback**：恢复 preset 备份。

---

## P2-5 Bases 视图

- **Owner**：图书管理员
- **Depends**：P1-6
- **Time**：1 小时
- **Why**：静态 HOME 适合 agent，Bases 适合人类临时筛选。
- **Files**：`00_系统/看板/项目.base`、`人物.base`、`灵感.base`
- **Steps**：
  1. 在 Obsidian 里用 Bases 新建视图，选 `02_项目`，字段 `progress/direction/next_action/next_action_due`。
  2. 保存到 `00_系统/看板/`。
  3. 人物视图按 `category/audience` 分组。
  4. 灵感视图按 `stage/captured` 排序。
  5. 记 changelog。
- **Verify**：Obsidian 打开三个 `.base` 文件，表格有数据。
- **Done**：人类可在 Obsidian 内筛选；agent 不依赖 `.base`。
- **Rollback**：删除三个文件。

---

## P2-6 媒体与 git 策略

- **Owner**：审计员
- **Depends**：P0-1
- **Time**：2 小时
- **Why**：`.git` 91.9 MB，历史含公开仓库全部内容；媒体大文件会继续膨胀。
- **Files**：`.gitignore`、`05_档案/媒体/媒体索引.md`（新建）、git 配置
- **Steps**：
  1. 先确认 `.gitignore` 覆盖 `*.m4a/*.mp4/*.wav`、`node_modules/`、`.hermes/`、logs/cache。
  2. 建 `媒体索引.md`，列大文件路径、用途、外部备份位置。
  3. 评估历史：保留旧仓库作离线存档，另建私有新仓库、以当前工作树为初始提交；或在确认不再公开后用 `git filter-repo` 清史。两种方案都需宇航员拍板。
  4. 不执行 `git push`，直到 remote 指向私有仓库且确认无敏感文件。
  5. 记 changelog。
- **Verify**：
  ```bash
  cd "$HOME/Documents/24帧运营库"
  git count-objects -vH | grep size-pack
  git status --short | head
  git remote -v
  ```
- **Done**：remote 指向私有仓库或已移除；`.gitignore` 生效；媒体索引可查。
- **Rollback**：恢复 remote；保留旧仓库备份。

---

## P2-7 语义 lint

- **Owner**：审计员
- **Depends**：P2-2
- **Time**：每周 30 分钟
- **Why**：格式 lint 查不出矛盾、过期结论、缺页概念。
- **Files**：`00_系统/agent/logs/semantic-YYYY-MM-DD.md`
- **Steps**：
  1. 每周用 headless 跑固定 prompt：读 `_index.md` + 最近 7 天改动 + review 队列，找三类问题：互相矛盾的结论、被新事实推翻的旧结论、反复出现但没有独立页面的概念。
  2. 输出 3 条以内，每条带文件路径和一句 action。
  3. 不自动改文件，交宇航员确认。
  4. 结论提炼进 `经验沉淀.md`。
- **Verify**：报告存在且每条有路径与 action。
- **Done**：连续 4 周有报告；至少 1 条被采纳并落地。
- **Rollback**：无写入，无需回滚。

---

## P2-8 指标看板

- **Owner**：审计员
- **Depends**：P1-3
- **Time**：1 小时
- **Why**：优化是否有效需要基线对比。
- **Files**：`00_系统/agent/vault-metrics.py`（新建）、`00_系统/agent/logs/health-YYYY-MM-DD.md`
- **Steps**：
  1. 用 **B15** 创建脚本（逐字源码见 [[附件C-脚本源码]] C6），输出 §8.1 的指标 JSON 与 markdown。
  2. 接入 nightly。
  3. 每周保留一份，旧报告删除。
- **Verify**：
  ```bash
  python3 00_系统/agent/vault-metrics.py --markdown
  ```
- **Done**：指标与 lint/index 数字一致；趋势可读。
- **Rollback**：删除脚本。

---

## P2-9 Skill 目录瘦身

- **Owner**：图书管理员
- **Depends**：无
- **Time**：1.5 小时
- **Why**：170 个 skill 描述每请求约 8k token，大部分与本库无关。
- **Files**：`~/.agents/skills/*/SKILL.md` 的 frontmatter
- **Steps**：
  1. 列出 170 个 skill，标出最近 30 天用过的。
  2. 保留 30–50 个高频；其余加 `disable-model-invocation: true` 或移入 `_archive/`。
  3. 每个保留的描述压到一句话，写清触发场景。
  4. 记 changelog。
- **Verify**：
  ```bash
  find "$HOME/.agents/skills" -maxdepth 2 -name SKILL.md | wc -l
  grep -rl "disable-model-invocation: true" "$HOME/.agents/skills" | wc -l
  ```
- **Done**：活跃 skill ≤50；新会话 skill 目录明显变短。
- **Rollback**：从备份恢复。

---

# P3 · 第 2 个月

## P3-1 查询回写 routine

- **Owner**：写作者
- **Depends**：P1-1
- **Time**：每周 30 分钟
- **Files**：项目页 `## 决策记录`、人物页 `## 行为记录`、`04_灵感/知识库/`
- **Steps**：每周挑 3 个高价值问答，按 §4.8 回写；每条带来源链接。
- **Verify**：`_changelog.md` 有「回写」记录；页面有新增段落。
- **Done**：连续 4 周执行；至少 6 条结论进入 wiki。

## P3-2 季度归档与复盘

- **Owner**：归档员
- **Depends**：P1-9
- **Time**：每季 2 小时
- **Files**：`05_档案/`、`_changelog/`、`经验沉淀.md`
- **Steps**：季度末清理已完成项目、归档过期灵感、分卷 changelog、汇总 3 条经验。
- **Verify**：季度报告一份；changelog 分卷存在。
- **Done**：库体积与条目数可解释。

## P3-3 v1 方案归档

- **Owner**：图书管理员
- **Depends**：无
- **Time**：10 分钟
- **Files**：`06_AI/2026-10-06_24帧运营库-DSH优化方案/` 三份
- **Steps**：frontmatter `status: archive`，加一行「v2 已取代，保留作设计参考」；不删。
- **Verify**：`grep status` 为 archive。
- **Done**：新 agent 不会误把 v1 当现行方案。

---

## 关联

- [[24帧运营库-DSH使用与优化方案-v2]]
- [[附件B-模板与脚本]]
- [[附件C-脚本源码]]
- [[运营手册]]
- [[_schema]]
