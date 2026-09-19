---
type: reference
name: HOME
status: final
editable: true
audience: owner
created: 2026-06-08
updated: 2026-09-09
---

# 🏠 24帧 · 现在

> 每天从这里开始。全库索引在 [[_index]]，规范在 [[运营手册]]。

## 📊 项目进度全貌

```dataview
TABLE direction AS "方向", progress AS "进度", goal AS "目标", dateformat(updated, "MM-dd") AS "更新"
FROM "02_项目"
WHERE type = "project"
SORT progress ASC, direction ASC
```

## ⏭️ 在推什么 · 在等什么（进行中的项目）

> 任务已并入项目（不设独立任务目录）。这里列出进行中的项目，任务级细节在项目页内。

```dataview
TABLE direction AS "方向", goal AS "目标", dateformat(updated, "MM-dd") AS "最近更新"
FROM "02_项目"
WHERE type = "project" AND progress = "进行中"
SORT direction ASC
```

## 🔍 等我拍板

```dataview
TABLE file.folder AS "位置", dateformat(file.mtime, "MM-dd") AS "上次修改"
FROM -"05_档案/公众号存档"
WHERE status = "review" AND audience != "agent"
SORT file.mtime DESC
```

## 💡 灵感待决策

```dataview
TABLE direction AS "方向", stage AS "阶段"
FROM "04_灵感/AI加工区"
WHERE stage != "已转项目" AND stage != "已归档" AND audience != "agent"
SORT direction ASC
```
