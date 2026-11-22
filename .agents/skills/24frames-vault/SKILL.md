---
name: 24frames-vault
description: 24FRAMES 运营库的读写路由。用于查项目/人物/会议、写项目页、处理灵感、维护索引与健康检查时。进入库内任务先读本 skill。
updated: 2026-10-28
---

# 24帧运营库 · 路由

## 何时用

任何对 `~/Documents/24帧运营库` 的读、写、查、维护。纯外部写作（不涉及库）不用。

## 先读三份，按需

1. 库根 `AGENTS.md`：边界与红线。
2. `00_系统/_schema.md`：要写文件时必读。
3. 对应目录的 `AGENTS.md`：`02_项目` / `03_人物` / `05_档案` / `06_AI` / `00_系统`。

一次最多三份。不要通读全库。

## 路由

| 任务 | 读 | 写 |
|---|---|---|
| 今日待办 | `HOME.md` | — |
| 找项目/人物 | `_index.md` → `vault-search.py` | — |
| 写项目页 | 项目页 + `02_项目/AGENTS.md` | `02_项目/<项目>/<项目>.md` |
| 归档会议 | `归档操作规范.md` + 相关项目/人物页 | `05_档案/会议存档/` 新建 + 项目/人物更新 |
| 处理灵感 | `04_灵感/README.md` + `_schema.md` | `04_灵感/AI加工区/` |
| 写公众号 | `references/writing.md` + 项目页 + `01_参考文档` | `06_AI/YYYY-MM-DD_主题/` |
| 维护 | `AGENTS.md` + lint 输出 | `00_系统/` 生成物 |

## 硬规则

1. `05_档案/` 只读；只能按归档规范新建会议。
2. `06_AI/` 每个任务一个 `YYYY-MM-DD_主题/`，不散落。
3. 每次写操作记 `_changelog.md`，格式 `## [YYYY-MM-DD HH:mm] 类型 | 文件`。
4. `public` 只给已批准对外的页面；人物/会议默认 `owner`。
5. 不编造；缺失写「待补充」。
6. 不 commit、不 push。
7. 改动超过 20 个文件先出计划。

## 工具

```bash
cd "$HOME/Documents/24帧运营库"
python3 00_系统/agent/vault-search.py "关键词" --limit 10
python3 00_系统/agent/vault-lint.py --file <文件>
python3 00_系统/agent/vault-index.py
python3 00_系统/agent/vault-home.py
```

## 写作与参考

- 写作风格：`references/writing.md`
- 常用命令：`references/commands.md`
- 字段细节：`00_系统/_schema.md`
- 归档细节：`00_系统/归档操作规范.md`

## 不要

- 不要装 Dataview，不要新建 `03_任务/`。
- 不要把 skill 当规范；规范在 `_schema.md` 和手册里。
- 不要把会议内容写进项目页正文，链接到会议页。
- 不要在 `05_档案/公众号存档/` 改字。
