---
type: direction
name: AI影像
lead: "[[宇航员]]"
progress: 进行中
status: draft
editable: true
related_brand: "[[品牌目标]]"
created: 2026-06-09
updated: 2026-06-10
audience: public
---

## 整体策略

24帧 用 AI 做影像的新业务线，目前还在灵感与探索阶段。源头是 2026-05 与妙添的通话：西南还没有 AI 电影节，可以先做 AI 短片的主题展映与讨论，定位做连接创作者与观众的平台，再用活动数据换 AI 平台的资源赞助。

核心不是自己产内容，而是做连接者，为 AI 创作者提供被看见的出口和真人反馈。先小步验证（预启动），跑通再正式立项。

2026-06-10 更新：宇航员与邬智鑫首次见面，确认先做一场试试看。邬智鑫负责创作板块，宇航员负责活动设计。商业模式探索中（广告位、教育转化、商务对接、平台合作）。

## 本方向的项目

```dataview
TABLE WITHOUT ID file.link AS 项目, progress AS 进度, goal AS 目标, dateformat(updated, "MM-dd") AS 更新
FROM "02_项目"
WHERE direction = this.file.link AND type = "project"
SORT updated DESC
```

## 本方向的任务

```dataview
TABLE WITHOUT ID file.link AS 任务, progress AS 进度, owner AS 负责人, due AS 截止
FROM "02_项目"
WHERE type = "task" AND direction = this.file.link AND progress != "已完成" AND progress != "已取消"
SORT due ASC
```

## 本方向的灵感

```dataview
TABLE WITHOUT ID file.link AS 灵感, stage AS 阶段
FROM "04_灵感"
WHERE direction = this.file.link AND stage != "已归档"
SORT stage ASC
```
