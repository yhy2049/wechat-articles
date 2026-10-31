---
type: draft
name: 附件C-脚本源码
status: review
editable: true
audience: both
created: 2026-10-28
updated: 2026-10-28
summary: 已在本库实跑的索引、HOME、lint、检索、指标与 hooks 源码
source: ai-generated
tags: [脚本, 自动化, DSH, lint]
---

# 附件C · 脚本源码

> 配套 [[24帧运营库-DSH使用与优化方案-v2]]、[[附件A-现状复核与执行队列]]、[[附件B-模板与脚本]]。
> 本附件里的每一段源码都在 `2026-10-28` 对本库实跑过；测试结果见 §C7。
> 运行环境：macOS + Python 3.9+；只用标准库，`PyYAML` 可选（没装时走内置的简化解析器）。

## C0 · 安装位置与公共模块

落盘结构：

```text
00_系统/agent/
├── vault_common.py          # 公共解析
├── vault-lint.py             # P1-3
├── vault-index.py            # P1-1
├── vault-home.py             # P1-2
├── vault-search.py           # P2-1
├── vault-metrics.py          # P2-8
├── .vault-lint-baseline.json # P1-3 生成
└── .vault-search.db          # P2-1 生成，gitignore
.claude/
├── hooks.json
└── hooks/
    ├── post-write-lint.sh
    └── guard-archive.sh
```

先建目录，再把 C0–C6 的文件按名字存进去：

```bash
cd "$HOME/Documents/24帧运营库"
mkdir -p 00_系统/agent .claude/hooks
chmod +x .claude/hooks/*.sh
```

`vault_common.py` 是所有脚本的公共底座：路径解析、frontmatter 解析（含 `audience: public---` 这种坏尾）、raw 目录判定、代码块剥离。**先装它，其余脚本才能 import。**

### C0 · `vault_common.py`

````python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared helpers for vault scripts."""
import os
import re
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

_env = os.environ.get("VAULT_PATH")
VAULT = Path(_env).expanduser().resolve() if _env else Path(__file__).resolve().parents[2]

EXCLUDE_DIRS = {
    ".git", ".obsidian", ".trash", "node_modules",
    "00_系统/agent/_archive",
    # 公众号存档的站点镜像与工具依赖不是库内容
    "05_档案/公众号存档/.github-pages",
    "05_档案/公众号存档/_skill",
}

RAW_PREFIXES = (
    "05_档案/公众号存档",
    "05_档案/媒体",
    "05_档案/放映数据",
    "05_档案/写作DNA",
)

NO_FM_FILES = {
    "AGENTS.md", "README.md", "HOME.md",
    "00_系统/_changelog.md", "00_系统/_index.md",
}


def rel(p: Path) -> str:
    return p.relative_to(VAULT).as_posix()


def is_excluded(r: str) -> bool:
    return any(r == d or r.startswith(d + "/") for d in EXCLUDE_DIRS)


def iter_md():
    for p in VAULT.rglob("*.md"):
        r = rel(p)
        if is_excluded(r):
            continue
        if "/attachments/" in r or "/images/" in r:
            continue
        yield p, r


def is_raw(r: str) -> bool:
    return any(r == d or r.startswith(d + "/") for d in RAW_PREFIXES)


def parse_frontmatter(text: str):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    end = None
    for i in range(1, len(lines)):
        s = lines[i].strip()
        if s == "---":
            end = i
            break
        if s.endswith("---"):
            lines[i] = s[:-3].rstrip()
            end = i
            break
    if end is None:
        return {}, text
    raw = "\n".join(lines[1:end])
    body = "\n".join(lines[end + 1:])
    if yaml is None:
        data = {}
        for line in raw.splitlines():
            m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
            if m:
                data[m.group(1)] = m.group(2).strip().strip('"').strip("'")
        return data, body
    try:
        data = yaml.safe_load(raw) or {}
        if not isinstance(data, dict):
            data = {}
    except Exception:
        data = {}
    return data, body


def as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value]
    s = str(value).strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    return [x.strip().strip('"').strip("'") for x in re.split(r"[,，、]", s) if x.strip()]


def truthy(value) -> bool:
    return str(value).strip().lower() in {"true", "yes", "1", "是"}


def strip_code_fences(text: str) -> str:
    # fences may be longer than three backticks (nested examples)
    text = re.sub(r"(`{3,})[^\n]*\n.*?\n\1", "", text, flags=re.S)
    text = re.sub(r"``[^`\n]*``", "", text)
    return re.sub(r"`[^`\n]*`", "", text)
````

## C1 · `vault-index.py`（B6，P1-1）

扫描活跃页的 frontmatter，生成 `00_系统/_index.md`：按方向/项目/项目参考文档/人物/灵感/知识库/品牌策略/系统/会议/成稿/方向参考文档/其他分组，每条带摘要与状态；另出「无入链」段收孤儿页。支持 `--check`、`--stdout`、`--out`。

````python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate 00_系统/_index.md from frontmatter.

用法：
  python3 vault-index.py            # 写入 _index.md
  python3 vault-index.py --check    # 只检查是否最新，过期 exit 1
  python3 vault-index.py --stdout   # 打印，不写入
"""
import argparse
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from vault_common import VAULT, iter_md, is_raw, parse_frontmatter, strip_code_fences

INDEX = VAULT / "00_系统/_index.md"
WIKI_TYPES = {"project", "person", "direction", "inspiration", "reference", "output"}
LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
GEN_RE = re.compile(r"^> 生成时间：.*$", re.M)

SECTION_ORDER = [
    ("direction", "方向"),
    ("project", "项目"),
    ("project_ref", "项目参考文档"),
    ("person", "人物"),
    ("inspiration", "灵感"),
    ("knowledge", "知识库"),
    ("brand", "品牌策略"),
    ("system", "系统与规范"),
    ("meeting", "会议存档"),
    ("output", "成稿"),
    ("direction_ref", "方向参考文档"),
    ("other", "其他 / 待归类"),
]
DIRECTION_ORDER = ["观影团", "策展人", "影视创作", "宣发平台", "AI影像"]


def clean_direction(value) -> str:
    return str(value or "").strip().replace("[[", "").replace("]]", "").strip()


def norm(text: str) -> str:
    return GEN_RE.sub("> 生成时间：<auto>", text)


def build_names():
    names = defaultdict(list)
    for p, r in iter_md():
        names[p.stem].append(r)
    return names


def link_for(p: Path, names) -> str:
    if len(names.get(p.stem, [])) > 1:
        return f"[[{p.relative_to(VAULT).with_suffix('').as_posix()}|{p.stem}]]"
    return f"[[{p.stem}]]"


def one_line(fm, kind: str) -> str:
    s = str(fm.get("summary", "")).strip() or "待补摘要"
    if kind == "project":
        prog = str(fm.get("progress", "")).strip() or "待补进度"
        nxt = str(fm.get("next_action", "")).strip() or "待补下一步"
        return f"{s} ｜ {prog} ｜ 下一步：{nxt}"
    if kind == "person":
        role = str(fm.get("role", "")).strip()
        return f"{s} ｜ {role}" if role else s
    if kind == "inspiration":
        stage = str(fm.get("stage", "")).strip()
        return f"{s} ｜ {stage}" if stage else s
    if kind == "meeting":
        d = str(fm.get("date", "")).strip()
        return f"{s} ｜ {d}" if d else s
    return s


def collect():
    names = build_names()
    pages = []
    inbound = defaultdict(set)
    for p, r in iter_md():
        if is_raw(r):
            continue
        fm, body = parse_frontmatter(p.read_text(encoding="utf-8", errors="ignore"))
        t = str(fm.get("type", "")).strip()
        pages.append((p, r, fm, t, body))
        for m in LINK_RE.finditer(strip_code_fences(body)):
            target = m.group(1).strip().strip("/").split("/")[-1].removesuffix(".md")
            if target and target != p.stem:
                inbound[target].add(r)
    return names, pages, inbound


def section_of(r: str, t: str) -> str:
    if r.startswith("06_AI/"):
        return ""
    if t == "direction":
        return "direction"
    if t == "project":
        return "project"
    if t == "person":
        return "person"
    if t == "inspiration":
        return "inspiration"
    if t == "meeting":
        return "meeting"
    if t == "output":
        return "output"
    if t == "reference":
        if r in {"AGENTS.md", "HOME.md", "README.md", "00_系统/_index.md", "00_系统/_changelog.md"}:
            return "system"
        if r.startswith("04_灵感/知识库/"):
            return "knowledge"
        if r.startswith("04_灵感/品牌策略/"):
            return "brand"
        if r.startswith("00_系统/"):
            return "system"
        if r.startswith("02_项目/"):
            return "project_ref"
        if r.startswith("01_方向/"):
            return "direction_ref"
    return "other"


def render():
    names, pages, inbound = collect()
    grouped = defaultdict(list)
    orphans = []
    for p, r, fm, t, _ in pages:
        sec = section_of(r, t)
        if not sec:
            continue
        if t in WIKI_TYPES and not inbound.get(p.stem):
            orphans.append((p, r, fm, t))
        grouped[sec].append((p, r, fm, t))

    active = len(pages)
    no_type = sum(1 for _p, r, _fm, t, _b in pages if not t and not r.startswith("06_AI/"))
    no_fm = sum(1 for _p, _r, fm, _t, _b in pages if not fm)
    raw = sum(1 for _p, _r in iter_md() if is_raw(_r))
    out = [
        "# 24帧运营库 · 索引",
        "",
        "> 自动生成，勿手改。重新生成：`python3 00_系统/agent/vault-index.py`",
        f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"> 活跃页 {active} 个（其中 {no_type} 个缺 `type`，{no_fm} 个连 frontmatter 都没有）；未列入 {raw} 个档案页（公众号原文、媒体、放映数据、写作 DNA）。",
        "",
    ]

    for key, label in SECTION_ORDER:
        rows = grouped.get(key, [])
        if not rows:
            continue

        if key in {"project", "project_ref", "direction_ref"}:
            group_prefix = 1
            rows.sort(key=lambda x: (x[1].split("/")[group_prefix] if len(x[1].split("/")) > group_prefix + 1 else "", x[0].stem))
        else:
            def dir_key(item):
                d = clean_direction(item[2].get("direction"))
                return (DIRECTION_ORDER.index(d) if d in DIRECTION_ORDER else 99, d, item[0].stem)

            rows.sort(key=dir_key)
        out.append(f"## {label}（{len(rows)}）")
        out.append("")
        current_dir = None
        for p, r, fm, t in rows:
            if key == "project":
                d = clean_direction(fm.get("direction")) or "未标方向"
                if d != current_dir:
                    out.append(f"### {d}")
                    out.append("")
                    current_dir = d
            elif key in {"project_ref", "direction_ref"}:
                parts = r.split("/")
                d = parts[1] if len(parts) > 2 else "未归类"
                if d != current_dir:
                    out.append(f"### {d}")
                    out.append("")
                    current_dir = d
            suffix = f" — {r}" if key in {"project_ref", "direction_ref", "other"} else ""
            out.append(f"- {link_for(p, names)} — {one_line(fm, t)}{suffix}")
        out.append("")

    if orphans:
        out.append(f"## 未归类 · 无入链（{len(orphans)}）")
        out.append("")
        out.append("> 这些页没有被任何页面链接。处理方式：在相关项目/人物/方向页的 `## 关联` 加入双链，或归档。")
        out.append("")
        for p, r, fm, t in sorted(orphans, key=lambda x: x[1]):
            out.append(f"- {link_for(p, names)} — {one_line(fm, t)} — {r}")
        out.append("")

    drafts = sum(1 for p, r in iter_md() if r.startswith("06_AI/") and not is_raw(r))
    out.append(f"> `06_AI/` 另有 {drafts} 个草稿/任务文件，不逐条列入；按目录名在文件管理器或 `vault-search.py` 中查。")
    out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--stdout", action="store_true")
    ap.add_argument("--out", help="写入指定路径（测试用）")
    args = ap.parse_args()

    text = render()
    if args.stdout:
        print(text)
        return 0

    target = Path(args.out).expanduser() if args.out else INDEX
    old = target.read_text(encoding="utf-8") if target.exists() else ""
    if args.check:
        if norm(old) == norm(text):
            print("index up to date")
            return 0
        print("index is stale: run python3 00_系统/agent/vault-index.py", file=sys.stderr)
        return 1

    if norm(old) != norm(text):
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        print(f"index written: {target} ({len(text)} chars)")
    else:
        print("index unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
````

## C2 · `vault-home.py`（B7，P1-2）

从 `02_项目/` 的 frontmatter 与 `## 待办` 任务行生成 `HOME.md`：今日焦点（手写块保留）、在做、待办、在等、待审、最近更新。支持 `--check`、`--stdout`、`--out`。

````python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate HOME.md from project frontmatter and `## 待办` task lines.

用法：
  python3 vault-home.py            # 写入 HOME.md
  python3 vault-home.py --check    # 过期 exit 1
  python3 vault-home.py --stdout
  python3 vault-home.py --out /tmp/home.md
"""
import argparse
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from vault_common import VAULT, iter_md, is_raw, parse_frontmatter

HOME = VAULT / "HOME.md"
TASK_RE = re.compile(
    r"^- \[( |x)\] (T-\d{2,}) (.+?) ｜ (.+?) ｜ (\d{4}-\d{2}-\d{2}) ｜ (待办|进行中|等待中|已完成|已取消)$"
)
GEN_RE = re.compile(r"^> 生成时间：.*$", re.M)
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2, "": 3}


def norm(text: str) -> str:
    return GEN_RE.sub("> 生成时间：<auto>", text)


def parse_date(value):
    s = str(value or "").strip()[:10]
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


def projects():
    rows = []
    base = VAULT / "02_项目"
    if not base.is_dir():
        return rows
    for p in sorted(base.glob("*/*.md")):
        if p.parent.name != p.stem:
            continue
        fm, body = parse_frontmatter(p.read_text(encoding="utf-8", errors="ignore"))
        tasks = []
        in_todo = False
        for line in body.splitlines():
            if line.strip() == "## 待办":
                in_todo = True
                continue
            if in_todo and line.startswith("## "):
                break
            if in_todo:
                m = TASK_RE.match(line.strip())
                if m:
                    tasks.append({
                        "done": m.group(1) == "x",
                        "id": m.group(2),
                        "text": m.group(3).strip(),
                        "project": m.group(4).strip(),
                        "due": parse_date(m.group(5)),
                        "status": m.group(6),
                    })
        rows.append({
            "path": p,
            "name": p.stem,
            "fm": fm,
            "tasks": tasks,
            "direction": str(fm.get("direction", "")).replace("[[", "").replace("]]", "").strip(),
            "progress": str(fm.get("progress", "")).strip(),
            "priority": str(fm.get("priority", "")).strip(),
            "next_action": str(fm.get("next_action", "")).strip(),
            "summary": str(fm.get("summary", "")).strip(),
            "updated": parse_date(fm.get("updated")),
        })
    return rows


def reviews():
    rows = []
    for p, r in iter_md():
        if is_raw(r) or r.startswith("06_AI/"):
            continue
        fm, _ = parse_frontmatter(p.read_text(encoding="utf-8", errors="ignore"))
        if str(fm.get("status", "")).strip() == "review":
            rows.append({
                "name": p.stem,
                "summary": str(fm.get("summary", "")).strip() or "待补摘要",
                "due": parse_date(fm.get("review_due")),
                "updated": parse_date(fm.get("updated")),
            })
    rows.sort(key=lambda x: x["due"] or date.max)
    return rows


def recent(days=7):
    cutoff = date.today() - timedelta(days=days)
    rows = []
    for p, r in iter_md():
        if is_raw(r) or r.startswith("06_AI/"):
            continue
        fm, _ = parse_frontmatter(p.read_text(encoding="utf-8", errors="ignore"))
        d = parse_date(fm.get("updated"))
        if d and d >= cutoff:
            rows.append((d, p.stem, str(fm.get("type", "")).strip()))
    rows.sort(reverse=True)
    return rows[:20]


def manual_block(old: str) -> str:
    m = re.search(r"<!-- MANUAL:START -->(.*?)<!-- MANUAL:END -->", old, re.S)
    if m and m.group(1).strip():
        return m.group(1).strip()
    return "- [ ] 今天最重要的一件事\n- [ ] 今天必须回的人"


def render(old=""):
    ps = projects()
    doing = sorted([x for x in ps if x["progress"] == "进行中"],
                   key=lambda x: (PRIORITY_ORDER.get(x["priority"], 3), -(x["updated"] or date.min).toordinal()))
    waiting = sorted([x for x in ps if x["progress"] == "等待中"],
                     key=lambda x: x["updated"] or date.min, reverse=True)
    all_tasks = []
    for x in ps:
        for t in x["tasks"]:
            if t["status"] in {"待办", "进行中", "等待中"} and not t["done"]:
                all_tasks.append((x, t))
    all_tasks.sort(key=lambda xt: (xt[1]["due"] or date.max, PRIORITY_ORDER.get(xt[0]["priority"], 3)))
    revs = reviews()

    out = [
        "# 24FRAMES · 今日",
        "",
        "> 自动生成，勿手改。重新生成：`python3 00_系统/agent/vault-home.py`",
        f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"> 数据源：`02_项目/` 的 frontmatter 与 `## 待办`；{len(ps)} 个项目，{len(all_tasks)} 条未完成任务。",
        "",
        "## 今日焦点（手写）",
        "",
        "<!-- MANUAL:START -->",
        manual_block(old),
        "<!-- MANUAL:END -->",
        "",
        "## 在做",
        "",
    ]
    if doing:
        out += ["| 项目 | 方向 | 下一步 | 更新 |", "|---|---|---|---|"]
        for x in doing:
            out.append(f"| [[{x['name']}]] | {x['direction'] or '—'} | {x['next_action'] or '待补'} | {x['updated'] or '—'} |")
    else:
        out.append("（无进行中项目）")
    out += ["", f"## 待办（{len(all_tasks)}）", ""]
    if all_tasks:
        out += ["| 任务 | 项目 | 截止 | 状态 |", "|---|---|---|---|"]
        for x, t in all_tasks:
            due = t["due"].isoformat() if t["due"] else "—"
            flag = ""
            if t["due"] and t["due"] < date.today():
                flag = f" ⚠️ 逾期 {(date.today() - t['due']).days} 天"
            out.append(f"| {t['id']} {t['text']} | [[{x['name']}]] | {due}{flag} | {t['status']} |")
    else:
        out.append("（无。任务写在项目页 `## 待办`，不单独建任务文件。）")
    out += ["", "## 在等", ""]
    if waiting:
        out += ["| 项目 | 在等什么 | 更新 |", "|---|---|---|"]
        for x in waiting:
            out.append(f"| [[{x['name']}]] | {x['next_action'] or '待补'} | {x['updated'] or '—'} |")
    else:
        out.append("（无等待中项目）")
    out += ["", f"## 待审（{len(revs)}）", ""]
    if revs:
        out += ["| 页面 | 摘要 | 截止 |", "|---|---|---|"]
        for x in revs:
            out.append(f"| [[{x['name']}]] | {x['summary']} | {x['due'] or '—'} |")
    else:
        out.append("（无待审页面）")
    out += ["", "## 最近更新（7 天）", ""]
    rec = recent()
    if rec:
        for d, name, t in rec:
            out.append(f"- {d} · [[{name}]]" + (f"（{t}）" if t else ""))
    else:
        out.append("（无）")
    out += [
        "",
        "---",
        "",
        "索引：[[_index]] ｜ 字段：[[_schema]] ｜ 流程：[[运营手册]] ｜ 归档：[[归档操作规范]] ｜ 日志：[[_changelog]]",
        "",
    ]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--stdout", action="store_true")
    ap.add_argument("--out")
    args = ap.parse_args()

    target = Path(args.out).expanduser() if args.out else HOME
    old = target.read_text(encoding="utf-8") if target.exists() else ""
    text = render(old)
    if args.stdout:
        print(text)
        return 0
    if args.check:
        if norm(old) == norm(text):
            print("home up to date")
            return 0
        print("HOME.md is stale: run python3 00_系统/agent/vault-home.py", file=sys.stderr)
        return 1
    if norm(old) != norm(text):
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        print(f"home written: {target} ({len(text)} chars)")
    else:
        print("home unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
````

## C3 · `vault-lint.py`（B8，P1-3）

全库检查：必填字段、枚举、目录归属、命名、public 审批、双链、孤儿、`## 关联`、任务语法、changelog 格式、禁用物、重名。`--file` 单文件模式只查该文件的字段/格式/命名，不查跨文件的双链与孤儿（hooks 用它做即时反馈）。支持基线、`--json`。退出码 0 干净 / 1 仅警告 / 2 有错误。

````python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""24帧运营库 lint v2.

用法：
  python3 vault-lint.py                 # 全库
  python3 vault-lint.py --file <path>   # 单文件（hooks 用）
  python3 vault-lint.py --json          # JSON 输出
  python3 vault-lint.py --write-baseline
  python3 vault-lint.py --no-baseline
退出码：0 干净；1 仅警告；2 有错误。
"""
import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

from vault_common import (
    VAULT, NO_FM_FILES, iter_md, is_raw, parse_frontmatter,
    rel, strip_code_fences, truthy,
)

LEGAL_TYPES = {
    "meeting", "person", "project", "direction", "inspiration",
    "reference", "draft", "output", "media", "task",
}
LEGAL_STATUS = {"draft", "review", "final", "archive"}
LEGAL_AUDIENCE = {"owner", "agent", "both", "public"}
LEGAL_PROGRESS = {"待办", "进行中", "等待中", "已完成", "已取消", "已终止"}
LEGAL_STAGE = {"新捕获", "已加工", "预启动", "已转项目", "已归档"}
LEGAL_DIRECTION = {"观影团", "策展人", "影视创作", "宣发平台", "AI影像"}
LEGAL_PRIORITY = {"high", "medium", "low"}
LEGAL_CATEGORY = {"internal", "external"}

WIKI_TYPES = {"project", "person", "direction", "inspiration", "reference", "output"}
SUMMARY_TYPES = WIKI_TYPES
REQUIRED_COMMON = ["type", "name", "status", "audience", "editable", "created", "updated"]
REQUIRED_BY_TYPE = {
    "meeting": ["date", "participants", "direction"],
    "person": ["category", "role"],
    "project": ["direction", "progress", "priority", "next_action"],
    "direction": ["direction"],
    "inspiration": ["stage", "captured"],
}

PLACEHOLDERS = {
    "wikilink", "会议文件名", "来源文件名", "文件名", "人物名",
    "项目名", "任务名", "灵感", "内容", "方向页", "相关人物", "相关会议",
    "项目", "人物", "会议", "方向",
}
LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
TASK_RE = re.compile(
    r"^- \[( |x)\] T-\d{2,} .+ ｜ .+ ｜ \d{4}-\d{2}-\d{2} ｜ (待办|进行中|等待中|已完成|已取消)$"
)
CHANGELOG_RE = re.compile(r"^## \[\d{4}-\d{2}-\d{2} \d{2}:\d{2}\] .+ \| .+")

issues = []


def add(code, sev, path, msg):
    issues.append({"code": code, "sev": sev, "path": path, "msg": msg})


def parse_date(value):
    if not value:
        return None
    s = str(value)[:10]
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


def check_location(r, t, p):
    if t == "meeting" and not r.startswith("05_档案/会议存档/"):
        add("LOCATION", "error", r, "meeting 必须在 05_档案/会议存档/")
    elif t == "person" and not r.startswith("03_人物/"):
        add("LOCATION", "error", r, "person 必须在 03_人物/")
    elif t == "project":
        if not (r.startswith("02_项目/") and p.parent.parent.name == "02_项目" and p.parent.name == p.stem):
            add("LOCATION", "error", r, "project 必须是 02_项目/<项目名>/<项目名>.md")
    elif t == "direction":
        if not (r.startswith("01_方向/") and p.parent.name == p.stem):
            add("LOCATION", "error", r, "direction 必须是 01_方向/<方向>/<方向>.md")
    elif t == "inspiration" and not r.startswith("04_灵感/"):
        add("LOCATION", "error", r, "inspiration 必须在 04_灵感/")
    elif t == "draft" and not r.startswith("06_AI/"):
        add("LOCATION", "error", r, "draft 必须在 06_AI/")
    elif t == "output" and not (r.startswith("06_AI/") or r.startswith("05_档案/公众号存档/")):
        add("LOCATION", "error", r, "output 必须在 06_AI/ 或 05_档案/公众号存档/")
    elif t == "media" and not r.startswith("05_档案/媒体/"):
        add("LOCATION", "error", r, "media 必须在 05_档案/媒体/")
    elif t == "reference":
        allowed = (
            r.startswith("00_系统/")
            or r.startswith("04_灵感/知识库/")
            or r.startswith("04_灵感/品牌策略/")
            or r.startswith("01_参考文档/")
            or "/01_参考文档/" in r
            or p.name == "README.md"
        )
        if not allowed:
            add("LOCATION", "warn", r, "reference 建议放 00_系统/、04_灵感/知识库/、04_灵感/品牌策略/ 或项目 01_参考文档/")


def check_file(p, r, names, inbound, collect_links):
    text = p.read_text(encoding="utf-8", errors="ignore")
    if not text.strip():
        return
    fm, body = parse_frontmatter(text)
    raw = is_raw(r)

    if not fm:
        if not raw and r not in NO_FM_FILES:
            add("FM_MISSING", "error", r, "缺 frontmatter")
        return

    if raw:
        return

    for key in REQUIRED_COMMON:
        if key not in fm or str(fm.get(key, "")).strip() == "":
            add("REQUIRED", "error", r, f"缺必填字段 {key}")

    t = str(fm.get("type", "")).strip()
    if t and t not in LEGAL_TYPES:
        add("TYPE", "error", r, f"非法 type: {t}")
    elif t == "task":
        add("TASK_LEGACY", "warn", r, "type: task 已废弃，任务写进项目页 ## 待办")
    elif t not in LEGAL_TYPES:
        return

    status = str(fm.get("status", "")).strip()
    if status and status not in LEGAL_STATUS:
        add("STATUS", "error", r, f"非法 status: {status}")
    if status == "review":
        due = parse_date(fm.get("review_due"))
        updated = parse_date(fm.get("updated"))
        ref = due or updated
        if ref and (date.today() - ref).days > 7:
            add("STALE_REVIEW", "warn", r, f"review 已超 7 天（{ref}）")

    aud = str(fm.get("audience", "")).strip()
    if aud and aud not in LEGAL_AUDIENCE:
        add("AUDIENCE", "error", r, f"非法 audience: {aud}")
    if aud == "public":
        if not fm.get("public_approved"):
            add("PUBLIC_UNAPPROVED", "error", r, "public 页缺 public_approved")
        if not truthy(fm.get("redacted")):
            add("PUBLIC_UNAPPROVED", "error", r, "public 页缺 redacted: true")

    if "progress" in fm and str(fm["progress"]).strip() not in LEGAL_PROGRESS:
        add("PROGRESS", "error", r, f"非法 progress: {fm['progress']}")
    if "stage" in fm and str(fm["stage"]).strip() not in LEGAL_STAGE:
        add("STAGE", "error", r, f"非法 stage: {fm['stage']}")
    if "priority" in fm and str(fm["priority"]).strip() not in LEGAL_PRIORITY:
        add("PRIORITY", "error", r, f"非法 priority: {fm['priority']}")
    if "category" in fm and str(fm["category"]).strip() not in LEGAL_CATEGORY:
        add("CATEGORY", "error", r, f"非法 category: {fm['category']}")

    direction = fm.get("direction")
    if direction is not None and str(direction).strip():
        d = str(direction).strip()
        if "[[" in d or "]]" in d:
            add("DIRECTION", "error", r, f"direction 不能带双链: {d}")
        elif d not in LEGAL_DIRECTION:
            add("DIRECTION", "error", r, f"非法 direction: {d}")

    if t in SUMMARY_TYPES and not str(fm.get("summary", "")).strip():
        add("SUMMARY", "error", r, "缺 summary（索引会标待补摘要）")

    for key in REQUIRED_BY_TYPE.get(t, []):
        if key not in fm or str(fm.get(key, "")).strip() == "":
            add("REQUIRED", "error", r, f"{t} 缺专属字段 {key}")

    check_location(r, t, p)

    if t == "meeting" and not re.match(r"^\d{4}-\d{2}-\d{2}[_-].+\.md$", p.name):
        add("NAMING", "error", r, "会议命名必须是 YYYY-MM-DD_主题.md")

    if "```dataview" in text and not r.startswith("06_AI/"):
        add("DEAD_DATAVIEW", "error", r, "含 Dataview 查询块，本库未装插件")

    if t in WIKI_TYPES | {"meeting"} and "## 关联" not in body:
        add("NO_RELATED", "warn", r, "缺 ## 关联 段")

    if t == "project":
        in_todo = False
        for line in body.splitlines():
            if line.strip() == "## 待办":
                in_todo = True
                continue
            if in_todo and line.startswith("## "):
                break
            if in_todo and line.startswith("- ["):
                if not TASK_RE.match(line.strip()):
                    add("TASK_FORMAT", "warn", r, f"任务行格式不符: {line.strip()[:50]}")

    if collect_links:
        clean = strip_code_fences(text)
        for m in LINK_RE.finditer(clean):
            target = m.group(1).strip().strip("/")
            if not target or target.startswith(("http", "www")):
                continue
            base = target.split("/")[-1]
            if base in PLACEHOLDERS:
                continue
            if base.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".docx", ".xlsx", ".txt", ".m4a", ".mp3", ".mp4")):
                found = base in names
            else:
                found = base.removesuffix(".md") in names
            if not found:
                add("LINK_BROKEN", "warn", r, f"断链 [[{target}]]")
            else:
                inbound.setdefault(base.removesuffix(".md"), set()).add(r)


def global_checks():
    for p in VAULT.rglob(".DS_Store"):
        add("FORBIDDEN", "warn", rel(p), ".DS_Store 残留")
    for d in VAULT.rglob("node_modules"):
        if ".git" not in d.parts:
            add("FORBIDDEN", "warn", rel(d), "node_modules 不应在库内")
    if (VAULT / ".hermes").exists():
        add("FORBIDDEN", "warn", ".hermes", ".hermes 运行时目录不应在库内")

    ai = VAULT / "06_AI"
    if ai.is_dir():
        for d in ai.iterdir():
            if d.is_dir() and not re.match(r"^\d{4}-\d{2}-\d{2}_.+", d.name):
                add("AI_NAMING", "error", rel(d), "06_AI 子目录必须是 YYYY-MM-DD_主题")
        for f in ai.iterdir():
            if f.is_file() and f.suffix == ".md":
                add("AI_ROOT_FILE", "error", rel(f), "06_AI 根目录不能散落文件")

    log = VAULT / "00_系统/_changelog.md"
    if log.exists():
        lines = log.read_text(encoding="utf-8", errors="ignore").splitlines()[-200:]
        for line in lines:
            if line.startswith("## ") and not CHANGELOG_RE.match(line):
                add("CHANGELOG_FORMAT", "warn", "00_系统/_changelog.md", f"格式不符: {line[:60]}")

    stems = {}
    for p, r in iter_md():
        if is_raw(r):
            continue
        stems.setdefault(p.stem, []).append(r)
    for stem, paths in stems.items():
        if len(paths) > 1:
            add("DUP_BASENAME", "warn", paths[0], f"重名 {stem}: {len(paths)} 处")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--write-baseline", action="store_true")
    ap.add_argument("--no-baseline", action="store_true")
    args = ap.parse_args()

    names = set()
    for p in VAULT.rglob("*"):
        if ".git" in p.parts or ".trash" in p.parts or "node_modules" in p.parts:
            continue
        if p.is_file():
            names.add(p.name)
            if p.suffix == ".md":
                names.add(p.stem)

    inbound = {}
    targets = []
    if args.file:
        p = Path(args.file).expanduser()
        if not p.is_absolute():
            p = VAULT / p
        p = p.resolve()
        try:
            r = p.relative_to(VAULT).as_posix()
        except ValueError:
            return 0
        if p.suffix == ".md" and p.exists():
            targets = [(p, r)]
    else:
        targets = list(iter_md())
        global_checks()

    for p, r in targets:
        check_file(p, r, names, inbound, collect_links=not args.file)

    if not args.file:
        for p, r in targets:
            fm, _ = parse_frontmatter(p.read_text(encoding="utf-8", errors="ignore"))
            if str(fm.get("type", "")) in WIKI_TYPES and not inbound.get(p.stem):
                add("ORPHAN", "warn", r, "无入链")

    baseline_path = VAULT / "00_系统/agent/.vault-lint-baseline.json"
    if args.write_baseline:
        keys = sorted({f"{i['path']}|{i['code']}" for i in issues})
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        baseline_path.write_text(json.dumps(keys, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"baseline written: {len(keys)} issues -> {baseline_path}")
        return 0

    baseline = set()
    if baseline_path.exists() and not args.no_baseline:
        try:
            baseline = set(json.loads(baseline_path.read_text(encoding="utf-8")))
        except Exception:
            baseline = set()

    shown = [i for i in issues if f"{i['path']}|{i['code']}" not in baseline]
    errors = [i for i in shown if i["sev"] == "error"]
    warns = [i for i in shown if i["sev"] == "warn"]

    if args.json:
        print(json.dumps({"errors": len(errors), "warnings": len(warns), "issues": shown}, ensure_ascii=False, indent=1))
    elif not args.quiet:
        for i in shown:
            print(f"[{i['sev'].upper()}] {i['code']} {i['path']}: {i['msg']}")
        print(f"\n{len(errors)} error / {len(warns)} warning")
    else:
        for i in errors:
            print(f"{i['code']} {i['path']}: {i['msg']}")
        if errors:
            print(f"{len(errors)} error", file=sys.stderr)

    return 2 if errors else (1 if warns else 0)


if __name__ == "__main__":
    sys.exit(main())
````

## C4 · `vault-search.py`（B10，P2-1）

SQLite FTS5 全文检索。中文按重叠 bigram 入 `unicode61` 索引，解决 FTS5 trigram 对 2 字词零命中的问题；英文按整词；单字回退 `LIKE`。支持 `--build`、`--stats`、`--limit`、`--json`、`--active-only`。

````python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Local full-text search for the vault, Chinese-friendly.

FTS5 trigram does not match queries shorter than 3 Unicode chars, so this
script indexes CJK text as overlapping bigrams instead.

用法：
  python3 vault-search.py --build
  python3 vault-search.py "放映 赞助"
  python3 vault-search.py "何力" --active-only --json
"""
import argparse
import json
import os
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

from vault_common import VAULT, iter_md, is_raw, parse_frontmatter, strip_code_fences

DB = Path(os.environ.get("VAULT_SEARCH_DB", str(VAULT / "00_系统/agent/.vault-search.db")))
CJK = re.compile(r"[\u4e00-\u9fff]")
TOKEN_RE = re.compile(r"[\u4e00-\u9fff]+|[A-Za-z0-9_]+")


def tokens(text: str):
    out = []
    for m in TOKEN_RE.finditer(text):
        s = m.group(0)
        if CJK.match(s):
            if len(s) == 1:
                out.append(s)
            else:
                out.extend(s[i:i + 2] for i in range(len(s) - 1))
        else:
            out.append(s.lower())
    return out


def connect():
    if not DB.exists():
        build()
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def build(verbose=True):
    docs = []
    for p, r in iter_md():
        text = p.read_text(encoding="utf-8", errors="ignore")
        fm, body = parse_frontmatter(text)
        title = str(fm.get("name", "")).strip() or p.stem
        summary = str(fm.get("summary", "")).strip()
        clean = strip_code_fences(body)
        docs.append((
            r, title,
            str(fm.get("type", "")).strip(),
            str(fm.get("status", "")).strip(),
            str(fm.get("audience", "")).strip(),
            str(fm.get("updated", "")).strip(),
            "raw" if is_raw(r) else "active",
            summary,
            clean,
        ))

    DB.parent.mkdir(parents=True, exist_ok=True)
    tmp = DB.with_suffix(".tmp")
    if tmp.exists():
        tmp.unlink()
    con = sqlite3.connect(tmp)
    con.executescript("""
        CREATE TABLE docs(
            path TEXT PRIMARY KEY, title TEXT, type TEXT, status TEXT,
            audience TEXT, updated TEXT, layer TEXT, summary TEXT, body TEXT
        );
        CREATE VIRTUAL TABLE fts USING fts5(path UNINDEXED, grams, tokenize='unicode61');
        CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT);
    """)
    for row in docs:
        path, title, _t, _s, _a, _u, _layer, summary, body = row
        con.execute("INSERT INTO docs VALUES (?,?,?,?,?,?,?,?,?)", row)
        grams = " ".join(tokens(title + "\n" + summary + "\n" + body))
        con.execute("INSERT INTO fts(path, grams) VALUES (?,?)", (path, grams))
    con.execute("INSERT INTO meta VALUES ('built_at', ?)", (datetime.now().isoformat(timespec="seconds"),))
    con.execute("INSERT INTO meta VALUES ('docs', ?)", (str(len(docs)),))
    con.commit()
    con.close()
    if DB.exists():
        DB.unlink()
    tmp.rename(DB)
    if verbose:
        print(f"index built: {DB} ({len(docs)} docs, {DB.stat().st_size // 1024} KB)")


def snippet(body: str, query: str, width=90):
    body = re.sub(r"\s+", " ", body).strip()
    needle = query.strip()
    pos = body.lower().find(needle.lower()) if needle else -1
    if pos < 0:
        grams = tokens(query)
        for g in grams:
            pos = body.lower().find(g.lower())
            if pos >= 0:
                break
    if pos < 0:
        return body[:width] + ("…" if len(body) > width else "")
    start = max(0, pos - width // 2)
    end = min(len(body), pos + len(needle) + width // 2)
    return ("…" if start else "") + body[start:end] + ("…" if end < len(body) else "")


def query(q, limit=10, active_only=False, as_json=False):
    con = connect()
    grams = tokens(q)
    rows = []
    if grams:
        match = " ".join(f'"{g}"' for g in grams)
        sql = """
            SELECT d.path, d.title, d.type, d.layer, d.updated, d.summary, d.body
            FROM fts JOIN docs d ON d.path = fts.path
            WHERE fts MATCH ?
        """
        params = [match]
        if active_only:
            sql += " AND d.layer = 'active'"
        sql += " ORDER BY bm25(fts) LIMIT ?"
        params.append(limit)
        rows = con.execute(sql, params).fetchall()
    if not rows:
        like = f"%{q}%"
        sql = "SELECT path, title, type, layer, updated, summary, body FROM docs WHERE (title LIKE ? OR body LIKE ?)"
        params = [like, like]
        if active_only:
            sql += " AND layer = 'active'"
        sql += " ORDER BY updated DESC LIMIT ?"
        params.append(limit)
        rows = con.execute(sql, params).fetchall()
    con.close()
    results = [{
        "path": r["path"],
        "title": r["title"],
        "type": r["type"],
        "layer": r["layer"],
        "updated": r["updated"],
        "summary": r["summary"],
        "snippet": snippet(r["body"], q),
    } for r in rows]
    if as_json:
        print(json.dumps(results, ensure_ascii=False, indent=1))
    else:
        print(f"{len(results)} results for: {q}")
        for x in results:
            tag = "档案" if x["layer"] == "raw" else "活跃"
            print(f"\n[{tag}] {x['title']}  ({x['type'] or '无 type'}, {x['updated'] or '—'})")
            print(f"  {x['path']}")
            print(f"  {x['snippet']}")
    return 0 if results else 1


def stats():
    con = connect()
    rows = con.execute("SELECT layer, count(*) n FROM docs GROUP BY layer").fetchall()
    meta = dict(con.execute("SELECT key, value FROM meta").fetchall())
    con.close()
    print(f"db: {DB} ({DB.stat().st_size // 1024} KB)")
    print(f"built_at: {meta.get('built_at', '?')}")
    for r in rows:
        print(f"{r['layer']}: {r['n']}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="*")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--active-only", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.build:
        build()
        return 0
    if args.stats:
        return stats()
    if not args.query:
        ap.print_help()
        return 1
    return query(" ".join(args.query), args.limit, args.active_only, args.json)


if __name__ == "__main__":
    sys.exit(main())
````
## C5 · hooks（B11，P2-3）

两个命令钩子，挂在 DSH 的 `@deepseek-ai/dsh-hooks-claude-code` 上：

- `post-write-lint.sh`：`PostToolUse`，写 `.md` 后跑 `vault-lint.py --file`；有 error 时 exit 2，把问题回给模型。
- `guard-archive.sh`：`PreToolUse`，存档目录只读；新建会议必须符合命名和最小 frontmatter。

### C5-1 · `.claude/hooks.json`

````json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/guard-archive.sh\"",
            "timeout": 30
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/post-write-lint.sh\"",
            "timeout": 60
          }
        ]
      }
    ]
  }
}
````

### C5-2 · profile 挂载

在库目录的 DSH profile 配置里加：

```yaml
- name: '@deepseek-ai/dsh-hooks-claude-code'
  config:
    configPath: ./.claude/hooks.json
    projectDir: .
```

`configPath` 相对启动目录解析；`projectDir` 会替换命令里的 `${CLAUDE_PROJECT_DIR}`，并设为钩子进程的环境变量。

### C5-3 · `.claude/hooks/post-write-lint.sh`

````bash
#!/usr/bin/env bash
# PostToolUse: lint the file that was just written. Exit 2 blocks with feedback.
set -u
VAULT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
AGENT="${VAULT_AGENT:-$VAULT/00_系统/agent}"

payload="$(cat)"
path="$(printf '%s' "$payload" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get("tool_input", {}).get("file_path", "") or "")
except Exception:
    print("")
' 2>/dev/null)"

[ -z "$path" ] && exit 0
case "$path" in
  *.md) ;;
  *) exit 0 ;;
esac

# 相对路径按库根解析
case "$path" in
  /*) abs="$path" ;;
  *) abs="$VAULT/$path" ;;
esac
[ -f "$abs" ] || exit 0

out="$(cd "$AGENT" && python3 vault-lint.py --file "$abs" 2>&1)"
rc=$?
if [ "$rc" -eq 2 ]; then
  printf '%s\n' "$out" >&2
  exit 2
fi
exit 0
````

### C5-4 · `.claude/hooks/guard-archive.sh`

````bash
#!/usr/bin/env bash
# PreToolUse: keep archives read-only; enforce the minimum schema for a new meeting.
set -u
payload="$(cat)"
path="$(printf '%s' "$payload" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get("tool_input", {}).get("file_path", "") or "")
except Exception:
    print("")
' 2>/dev/null)"
content="$(printf '%s' "$payload" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
    ti = d.get("tool_input", {})
    print(ti.get("content") or ti.get("new_string") or "")
except Exception:
    print("")
' 2>/dev/null)"

[ -z "$path" ] && exit 0
case "$path" in
  *05_档案/公众号存档/*|*05_档案/媒体/*|*05_档案/放映数据/*)
    echo "存档目录只读：$path。新内容写到 06_AI/ 或对应项目目录，发布后再归档。" >&2
    exit 2
    ;;
  *05_档案/会议存档/*)
    if [ -e "$path" ]; then
      echo "会议存档已存在：$path。修订请写 06_AI/ 草稿，定稿后再替换存档并记 changelog。" >&2
      exit 2
    fi
    base="$(basename "$path")"
    if ! printf '%s' "$base" | grep -Eq '^[0-9]{4}-[0-9]{2}-[0-9]{2}[_-].+\.md$'; then
      echo "会议文件名必须是 YYYY-MM-DD_主题.md：$base" >&2
      exit 2
    fi
    missing=""
    for key in type date participants direction audience; do
      printf '%s' "$content" | grep -Eq "^${key}:" || missing="$missing $key"
    done
    if [ -n "$missing" ]; then
      echo "新会议缺 frontmatter 字段：$missing" >&2
      exit 2
    fi
    ;;
esac
exit 0
````

## C6 · `vault-metrics.py`（B15，P2-8）

一页健康快照：活跃页/档案页、frontmatter 与 summary 覆盖率、schema 漂移、public 数、lint 计数、changelog 格式、生成物新鲜度。支持 `--markdown`、`--json`、`--out`。

````python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One-page health snapshot for the vault.

用法：
  python3 vault-metrics.py --markdown
  python3 vault-metrics.py --json
  python3 vault-metrics.py --markdown --out /tmp/health.md
"""
import argparse
import json
import os
import subprocess
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path

from vault_common import VAULT, iter_md, is_raw, parse_frontmatter

AGENT = VAULT / "00_系统/agent"
LINT = Path(os.environ.get("VAULT_LINT", str(AGENT / "vault-lint.py")))
DB = Path(os.environ.get("VAULT_SEARCH_DB", str(AGENT / ".vault-search.db")))


def scan():
    active = raw = fm_n = summary = complete = 0
    types, statuses, audiences, directions = Counter(), Counter(), Counter(), Counter()
    public = Counter()
    req = ["type", "name", "status", "audience", "editable", "created", "updated"]
    for p, r in iter_md():
        if is_raw(r):
            raw += 1
            continue
        active += 1
        fm, _ = parse_frontmatter(p.read_text(encoding="utf-8", errors="ignore"))
        if not fm:
            continue
        fm_n += 1
        t = str(fm.get("type", "")).strip()
        types[t or "(空)"] += 1
        statuses[str(fm.get("status", "")).strip() or "(空)"] += 1
        audiences[str(fm.get("audience", "")).strip() or "(空)"] += 1
        d = str(fm.get("direction", "")).strip()
        if d:
            directions[d] += 1
        if str(fm.get("summary", "")).strip():
            summary += 1
        if all(str(fm.get(k, "")).strip() for k in req):
            complete += 1
        if str(fm.get("audience", "")).strip() == "public":
            public[t or "(空)"] += 1
    return {
        "active": active, "raw": raw, "with_fm": fm_n, "no_fm": active - fm_n,
        "with_summary": summary, "complete_7": complete,
        "type_values": len([k for k in types if k != "(空)"]),
        "status_values": len([k for k in statuses if k != "(空)"]),
        "audience_values": len([k for k in audiences if k != "(空)"]),
        "direction_spellings": len(directions),
        "public_total": sum(public.values()),
        "public_person": public.get("person", 0),
        "public_meeting": public.get("meeting", 0),
        "types": dict(types.most_common()),
        "public_by_type": dict(public.most_common()),
    }


def lint():
    if not LINT.exists():
        return {"available": False}
    try:
        out = subprocess.run(
            [sys.executable, str(LINT), "--json", "--no-baseline"],
            capture_output=True, text=True, timeout=120,
        )
        data = json.loads(out.stdout)
        codes = Counter(i["code"] for i in data["issues"])
        return {
            "available": True,
            "errors": data["errors"],
            "warnings": data["warnings"],
            "by_code": dict(codes.most_common()),
        }
    except Exception as e:
        return {"available": False, "error": str(e)}


def changelog():
    p = VAULT / "00_系统/_changelog.md"
    if not p.exists():
        return {"available": False}
    import re
    ok = re.compile(r"^## \[\d{4}-\d{2}-\d{2} \d{2}:\d{2}\] .+ \| .+")
    lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    heads = [l for l in lines if l.startswith("## [")]
    bad = [l for l in heads if not ok.match(l)]
    return {"available": True, "lines": len(lines), "entries": len(heads), "bad": len(bad)}


def freshness():
    idx = VAULT / "00_系统/_index.md"
    return {
        "index_exists": idx.exists(),
        "index_updated": datetime.fromtimestamp(idx.stat().st_mtime).strftime("%Y-%m-%d %H:%M") if idx.exists() else None,
        "search_exists": DB.exists(),
        "search_size_kb": DB.stat().st_size // 1024 if DB.exists() else 0,
        "search_built": datetime.fromtimestamp(DB.stat().st_mtime).strftime("%Y-%m-%d %H:%M") if DB.exists() else None,
    }


def collect():
    return {
        "date": date.today().isoformat(),
        "scan": scan(),
        "lint": lint(),
        "changelog": changelog(),
        "freshness": freshness(),
    }


def markdown(d):
    s, l, c, f = d["scan"], d["lint"], d["changelog"], d["freshness"]
    lines = [
        f"# 24帧运营库 · 健康快照 {d['date']}",
        "",
        "| 指标 | 当前 | 目标 |",
        "|---|---:|---:|",
        f"| 活跃页 | {s['active']} | — |",
        f"| 档案页（raw） | {s['raw']} | — |",
        f"| 活跃页有 frontmatter | {s['with_fm']} / {s['active']} | 100% |",
        f"| 活跃页有 summary | {s['with_summary']} / {s['active']} | 100% |",
        f"| 七字段齐全 | {s['complete_7']} / {s['active']} | 100% |",
        f"| type 取值数 | {s['type_values']} | ≤10 |",
        f"| status 取值数 | {s['status_values']} | 4 |",
        f"| audience 取值数 | {s['audience_values']} | 4 |",
        f"| direction 写法数 | {s['direction_spellings']} | 5 |",
        f"| public 页 | {s['public_total']}（人物 {s['public_person']} / 会议 {s['public_meeting']}） | 0 未批准 |",
    ]
    if l.get("available"):
        lines += [
            f"| lint error | {l['errors']} | 0（基线外） |",
            f"| lint warning | {l['warnings']} | ≤20 |",
        ]
    if c.get("available"):
        lines.append(f"| changelog 格式不符 | {c['bad']} / {c['entries']} 条 | 0 |")
    lines += [
        "",
        "## 待处理 Top",
        "",
    ]
    if l.get("available"):
        for code, n in list(l["by_code"].items())[:8]:
            lines.append(f"- `{code}`：{n}")
    lines += [
        "",
        "## 生成物",
        "",
        f"- `_index.md`：{'存在' if f['index_exists'] else '缺失'}（{f['index_updated'] or '—'}）",
        f"- 检索库：{'存在' if f['search_exists'] else '缺失'}（{f['search_size_kb']} KB，{f['search_built'] or '—'}）",
        "",
        "> 由 `00_系统/agent/vault-metrics.py --markdown` 生成。lint 数字未扣基线。",
        "",
    ]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument("--out")
    args = ap.parse_args()

    d = collect()
    text = json.dumps(d, ensure_ascii=False, indent=1) if args.json else markdown(d)
    if args.out:
        p = Path(args.out).expanduser()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        print(f"written: {p}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
````

## C7 · 实跑记录（2026-10-28）

环境：macOS 25.6.0，Python 3.9，SQLite 3.51.0，库路径 `~/Documents/24帧运营库`。

> 库在审计期间被并行修改：首轮与复核（03:30）的部分计数不同。下表是 03:30 复核值；首轮 lint 为 793 条（551 error / 242 warning，601 个基线键）。数字只证明脚本能跑通，不构成对库的验收标准。

| 命令 | 结果 |
|---|---|
| `vault-lint.py --no-baseline` | 822 条问题，553 error / 269 warning，605 条 `path\|code` 基线键，exit 2 |
| `vault-index.py --stdout` | 241 个活跃页（含 78 个 `06_AI` 草稿）；12 个 Dataview 死块；92 个孤儿页；340 行 / 30 KB |
| `vault-home.py --stdout` | 11 个项目；0 条规范任务（任务迁移未做）；4 个待审页；手写块可保留 |
| `vault-search.py --build` | 564 篇文档；索引 15.9 MB |
| `vault-search.py 放映` | 3 条命中（2 字词） |
| `vault-search.py 赞助` | 3 条命中（2 字词） |
| `vault-search.py 放映员` | 2 条命中（3 字词） |
| `guard-archive.sh` | 存档目录 Write exit 2；已存在会议 Write exit 2；新会议缺 `audience` exit 2；新会议字段齐全 exit 0；已存在会议 Edit（读 `new_string`）exit 2；新会议 Edit（`new_string` 含字段）exit 0；坏 JSON、非目标路径 exit 0 |
| `post-write-lint.sh` | 合规文件 exit 0；有 `REQUIRED` 错误的文件 exit 2 并回传错误行；文件不存在或非 `.md` exit 0 |
| `vault-metrics.py --markdown` | 输出 241 活跃 / 320 档案 / 232 有 fm / 4 有 summary / 61 public / changelog 12 bad of 140 |

### 已知边界

1. **中文检索**：bigram 索引会有跨词误命中（「影放」也会命中「电影放映」），这是子串检索的代价；要精确短语再上 qmd 或向量。
2. **基线粒度**：基线键是 `path|code`，同一文件同一类问题只豁免一次；新增同类问题不会报。编辑过的文件在 `--file` 下仍按基线抑制旧债，只报新 code。要强制全查，用 `--no-baseline`。
3. **索引摘要**：全库只有 4 篇有 `summary`，首版索引会大量显示「待补摘要」。这是真实缺口，不是脚本 bug；P1-8 补摘要后才好看。
4. **HOME 任务**：当前 11 个项目没有一条符合新任务语法的 `## 待办`，所以首版「待办」是空的。P1-5 迁移后才有内容。
5. **`.github-pages` 与 `_skill`**：默认不扫描。它们合计 30 MB、332 份 md，是站点镜像和工具依赖，不属于库内容。
6. **单文件模式**：`--file` 不查跨文件双链和孤儿，只做字段/格式/命名/归属检查；完整链路检查交给全库模式与 nightly。这是为了让 hooks 在写入瞬间快速返回。

## C8 · 常用命令

```bash
cd "$HOME/Documents/24帧运营库"

# 体检（先写一次基线，之后只报新增）
python3 00_系统/agent/vault-lint.py --write-baseline
python3 00_系统/agent/vault-lint.py

# 单文件（hooks 同款）
python3 00_系统/agent/vault-lint.py --file 03_人物/宇航员.md

# 索引与首页
python3 00_系统/agent/vault-index.py
python3 00_系统/agent/vault-index.py --check
python3 00_系统/agent/vault-home.py
python3 00_系统/agent/vault-home.py --check

# 检索
python3 00_系统/agent/vault-search.py --build
python3 00_系统/agent/vault-search.py "资金 分工" --limit 5
python3 00_系统/agent/vault-search.py "放映" --active-only

# 健康快照
python3 00_系统/agent/vault-metrics.py --markdown
```

## 关联

- [[24帧运营库-DSH使用与优化方案-v2]]
- [[附件A-现状复核与执行队列]]
- [[附件B-模板与脚本]]
- [[_schema]]
- [[运营手册]]
- [[归档操作规范]]
