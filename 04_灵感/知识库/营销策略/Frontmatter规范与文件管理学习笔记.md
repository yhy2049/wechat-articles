---
type: reference
name: "Frontmatter规范与文件管理学习笔记"
status: final
editable: true
audience: both
created: 2026-06-12
updated: 2026-06-12
---

# Frontmatter规范与文件管理学习笔记

> 学习时间：2026-06-01 19:13
> 学习来源：tmp-deliverable-02-frontmatter-spec.md（新增规范文档）

## 一、规范概述

今天工作台新增了一份重要的Frontmatter规范文档，专门针对“24帧”运营库的文件管理需求而设计。这份规范解决了原lifecycle字段混合两个维度（状态与权限）的问题，将其拆分为两个正交字段：**status（文件成熟度状态）** 和 **editable（AI编辑权限）**。

这份规范的出现，标志着“24帧”品牌在文档管理上从经验驱动转向系统化、规范化管理的重要一步。

## 二、核心字段解析

### 1. status字段（文件成熟度状态）

| 枚举值 | 含义 | 适用阶段 |
|---|---|---|
| `draft` | 草稿/讨论中/多版本方案。内容未定，可能被推翻或废弃 | 过程管理区、进行中的项目初始版本 |
| `review` | 等我审阅、拍板。内容基本成型，AI可提建议但不能定稿 | 新建会议存档未确认、对外提交类报告、品牌策略初稿 |
| `final` | 已确认、可执行的定稿。内容经宇航员确认，AI可后续增量更新 | 已确认的项目/任务、定稿的品牌手册 |
| `archive` | 归档，仅查阅不再修改。内容冻结，不会再有主动更新 | 已完结的项目、已确认冻结的会议存档、公众号历史文章 |

**关键洞察**：这四个状态形成了文件生命周期的完整闭环：从草稿（draft）到待审（review）、定稿（final）、归档（archive）。每个状态都有明确的边界和转换规则。

### 2. editable字段（AI编辑权限）

| 值 | 含义 |
|---|---|
| `true` | AI可直接修改文件内容 |
| `false` | AI不能改原件。如需修订，在11_草稿池/另起草稿 |

**核心原则**：editable和status是正交的，互不推导。这意味着：
- `editable: false` 不等于 `archive`
- `draft` 不等于 `editable: true`

例如：外部输入的方案（status=draft, editable=false），AI不能直接修改，只能基于它另写草稿。

## 三、各目录默认值映射表（精简版）

| 目录 | 默认status | 默认editable | 说明 |
|---|---|---|---|
| 01_方向 | final | true | 方向笔记可增量更新 |
| 02_项目（进行中） | draft/review | true | 进行中的项目：初始draft，需要确认时改为review |
| 02_项目（已完成/已取消） | archive | false | 完结后自动更新为archive |
| 03_任务 | draft/final | true | 新建任务draft，宇航员拍板后final |
| 04_人物 | final | true | 人物画像持续更新 |
| 05_会议存档/待审阅 | review | false | 刚书面化，等待确认质量 |
| 05_会议存档/已存档 | archive | false | 确认后更新为archive |
| 06_灵感库/原始原文 | archive | false | 外部素材，AI不改原文 |
| 06_灵感库/AI加工区 | draft | true | AI可自由加工、延伸、提炼 |
| 07_变更日志 | final | true | 只追加，不修改已有记录 |
| 08_公众号 | archive | false | 历史文章，仅宇航员可改 |
| 08_品牌 | review/final | 条件写 | 品牌手册草稿draft，定稿final |
| 10_报告/自动汇总 | final | true | 数据快照，AI自动生成并更新 |
| 10_报告/对外提交 | draft→review | true | AI起草→设review→确认后改final |
| 11_草稿池 | draft | true | 默认true；外部输入设为false |
| 90_仪表盘 | — | — | Dataview视图，不存放业务文件 |

## 四、示例文件头解析

### 示例1：进行中且AI可修改的项目文件
```yaml
---
type: project
direction: "[[观影团]]"
status: draft
editable: true
created: 2026-06-01
updated: 2026-06-01
---
```

**解读**：这是一个典型的项目文件，AI可以自由更新进展和待办。当宇航员确认项目阶段后，可将status改为final。

### 示例2：等待确认的会议存档
```yaml
---
type: meeting
date: 2026-06-01
participants: ["[[谢琌]]", "[[何力]]"]
status: review
editable: false
created: 2026-06-01
---
```

**解读**：会议存档刚创建，等待宇航员确认质量。确认前不可修改，确认后迁入已存档目录，status改为archive。

### 示例3：已归档的公众号历史文章
```yaml
---
type: article
status: archive
editable: false
published: 2022-05-20
author: "宇航员"
---
```

**解读**：历史归档文件，不再改动。通过`editable: false`可快速过滤出参考类内容。

### 示例4：草稿池中的外部输入
```yaml
---
type: draft
主题: 麓湖电影节合作方案
版本: v0.1
owner: "合作方名称"
status: draft
editable: false
来源: 外部输入
创建日期: 2026-06-01
更新日期: 2026-06-01
---
```

**解读**：外部给的初稿方案，AI不可直接修改原件。如需修订，在草稿池中新建一个`_v0.2`版本，editable: true。

## 五、字段维护规则

### 谁在什么时机设置/更新

| 动作 | 设置/更新字段 | 执行者 |
|---|---|---|
| 创建新文件 | status设对应默认值，editable设对应默认值 | 创建文件的AI |
| AI完成修改、确认内容无问题 | status不变。如需宇航员确认→改为review | AI |
| 宇航员口头确认 | status: final（或archive），editable按需 | AI（依据指令） |
| 项目/任务完结 | status: archive，editable: false | AI（lint时自动检测） |
| 宇航员要求修改已归档文件 | 在11_草稿池/新建草稿，status: draft，editable: true | AI |

### 字段冲突处理

1. **同一个文件在不同阶段需要不同status**：更新frontmatter即可
2. **editable和子目录归属冲突**：以frontmatter为准
3. **文件已迁入已存档/但status仍为review**：这是不合法状态，迁移时必须同步更新

## 六、Dataview查询示例

### 查看所有需要审阅的内容
```dataview
LIST
FROM ""
WHERE status = "review"
SORT file.ctime DESC
```

### 查看所有参考类内容（只读已冻结文件）
```dataview
LIST
FROM ""
WHERE editable = false AND status = "archive"
SORT file.mtime DESC
```

### 查看草稿池状态
```dataview
TABLE status, dateformat(file.ctime, "yyyy-MM-dd") AS 最后更新
FROM "11_草稿池"
SORT file.mtime DESC
```

## 七、对“24帧”品牌的价值分析

### 1. 建立清晰的文档生命周期
这套规范为“24帧”运营库建立了从草稿到归档的完整生命周期管理。每个阶段都有明确的状态标识和操作规则，避免了文档管理的混乱。

### 2. 平衡AI自动化与人工控制
通过editable字段，规范明确了AI在文档管理中的边界。AI可以自由处理草稿和进行中的项目，但对于需要审阅的内容和已归档的文件，必须遵循严格的规则。这既保证了效率，又确保了质量控制。

### 3. 支持协作与权限管理
规范为不同类型的文档设置了不同的默认权限。例如，公众号历史文章只能由宇航员修改，而AI可以自由更新项目进展。这种权限分离有助于保护核心资产，同时提高协作效率。

### 4. 提供强大的查询能力
通过Dataview查询，宇航员可以快速找到所有需要审阅的内容、所有参考类内容，或者查看草稿池状态。这种查询能力对于日常管理和决策支持非常有价值。

### 5. 为自动化奠定基础
规范中提到的lint检测和自动状态更新，为未来的自动化流程奠定了基础。AI可以在特定条件下自动更新文件状态，减少人工干预。

## 八、待确认事项

规范文档最后列出了几个TODO事项，需要宇航员确认：
1. 枚举值名称和含义是否有需要调整的（尤其draft/review/final/archive四段够不够用）
2. 11的目录名（当前临时用11_草稿池/，宇航员最终确定）
3. editable字段在个别目录下的默认值（如01_方向editable=true是否合适）
4. 是否需要为editable增加枚举（如always/conditional/never），当前二值true/false是否够用

## 九、学习总结

这份Frontmatter规范是“24帧”品牌文档管理的重要里程碑。它不仅解决了状态与权限混合的问题，还为整个运营库建立了清晰、可执行的管理框架。

对于我（毛毛）而言，理解并掌握这套规范至关重要。它将指导我在日常工作中如何正确创建、修改和归档文档，确保既高效又符合规范。

**核心记忆点**：
1. status和editable是正交的，互不推导
2. 不同目录有不同的默认值，但以frontmatter为准
3. AI在处理文档时必须遵循状态和权限规则
4. 查询能力是这套系统的重要价值所在

这份规范与之前学习的真实感营销、文艺电影营销等内容形成互补：一个关注内部管理效率，一个关注外部内容创作。两者共同支撑“24帧”品牌的长期发展。