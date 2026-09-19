---
type: reference
status: final
editable: true
audience: both
created: 2026-05-31
updated: 2026-09-09
---

# 24帧运营库 · 索引

> 全库结构索引，给 agent 和查找用。日常行动看 [[HOME]]，规范看 [[运营手册]]。

## 📋 最近 7 天修改

```dataview
TABLE WITHOUT ID file.link AS "文件", dateformat(file.mtime, "MM-dd HH:mm") AS "修改时间", status AS "状态"
FROM -"05_档案/公众号存档"
WHERE audience != "agent" AND file.mtime >= date(today) - dur(7 days)
SORT file.mtime DESC
LIMIT 15
```

---

# 目录结构（5+1 目录）

## 01_方向
[[观影团]] · [[策展人]] · [[影视创作]] · [[宣发平台]] · [[AI影像]]

## 02_项目
项目 + 任务（一个项目所有相关东西都在里面；会议统一在 05_档案/会议存档）

```dataview
TABLE WITHOUT ID file.link AS "项目", direction AS "方向", progress AS "进度"
FROM "02_项目"
WHERE type = "project"
SORT progress ASC, file.name ASC
```

## 03_人物
```dataview
TABLE WITHOUT ID file.link AS "人物", role AS "角色", category AS "类别"
FROM "03_人物"
SORT category ASC, file.name ASC
```

## 04_灵感
想法类：AI加工区（灵感捕获与加工）+ 知识库（运营方法）+ 品牌策略 + 归档

## 05_档案
已完成类：会议存档 + 公众号存档（2022–2026）+ 媒体材料 + 放映数据

## 06_AI
AI 生成的草稿/半成品，按 `YYYY-MM-DD_主题/` 建子目录。未校准 → 已校准（文件名加后缀）→ 已发布（移入 05_档案/公众号存档）。

## 00_系统
手册、索引、日志 + agent 工作记忆（对宇航员隐藏）

---

> **架构说明**：规范保留在 vault 内（可移植、通用）。Hermes 通过 Skill 强制加载，其他 agent 直接读文件。
