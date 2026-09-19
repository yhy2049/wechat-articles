#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
24帧运营库 · 健康检查脚本（vault-health-check.py）
=================================================
每周或动手前运行：python3 00_系统/agent/vault-health-check.py

检查项：
  1. frontmatter 缺失（排除 05_档案/公众号存档 与 attachments）
  2. wikilink 断裂（[[目标]] 找不到对应文件）
  3. status: review 堆积（等宇航员拍板但长期未动）
  4. 06_AI 命名违规（子目录不符合 YYYY-MM-DD_主题）
  5. 会议文件错位（type: meeting/redirect 在 05_档案/会议存档 之外）
  6. 失效路径引用（03_任务 / 06_灵感库 / 07_档案 等已废弃路径）
  7. 空目录
  8. .DS_Store 残留

用法：python3 vault-health-check.py [--detail]   （--detail 显示全部条目）
退出码：0 = 健康；1 = 发现问题
"""
import os
import re
import sys
from pathlib import Path
from datetime import datetime

VAULT = Path(__file__).resolve().parents[2]
DETAIL = "--detail" in sys.argv

# 排除目录（相对 vault 根）
EXCLUDE_DIRS = {
    ".git", ".obsidian", ".trash",
    "05_档案/公众号存档",          # 历史文章，宇航员要求不动
    "06_AI/2026-07-25_地下美人导演夏昊专访/attachments",
    "00_系统/agent/_archive",      # agent 历史档案，不要求结构
}
# 不要求 frontmatter 的目录
NO_FM_DIRS = {"05_档案/公众号存档", "00_系统/agent/_archive"}
# 不要求 frontmatter 的根级文件（系统入口/日志/说明）
NO_FM_FILES = {"AGENTS.md", "README.md", "00_系统/_changelog.md"}
# wikilink 模板占位符（不视为断链）
PLACEHOLDER_LINKS = {"wikilink", "会议文件名", "来源文件名", "文件名", "人物名", "项目名", "任务名", "灵感", "内容"}

# 已废弃的路径引用（dataview / 文本中的旧路径）
STALE_PATHS = ["03_任务", "06_灵感库", "07_档案", "24帧运营库/03_任务"]

report = []  # (category, severity, message)
ok_count = 0


def is_excluded(rel: str) -> bool:
    return any(rel == d or rel.startswith(d + "/") for d in EXCLUDE_DIRS)


def rel_path(p: Path) -> str:
    return str(p.relative_to(VAULT))


def all_md_files():
    for p in VAULT.rglob("*.md"):
        rel = rel_path(p)
        if not is_excluded(rel) and "/attachments/" not in rel and "/images/" not in rel:
            yield p, rel


def has_frontmatter(text: str) -> bool:
    return text.startswith("---") and "\n---" in text[3:]


def is_no_fm_file(rel: str) -> bool:
    return rel in NO_FM_FILES or any(rel.startswith(d + "/") for d in NO_FM_DIRS)


def frontmatter_field(text: str, field: str) -> str:
    m = re.search(rf"^{field}:\s*(.+)$", text[:2000], re.M)
    return m.group(1).strip() if m else ""


def find_note(name: str) -> bool:
    """按 Obsidian 规则（basename 匹配）判断 [[name]] 是否存在。"""
    if name.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".docx", ".xlsx", ".txt", ".m4a", ".mp3")):
        return any(p.name == name for p in VAULT.rglob(name))
    if not name.lower().endswith(".md"):
        name = name + ".md"
    return any(p.name == name for p in VAULT.rglob(name))


# ---------- 1. frontmatter 缺失 ----------
no_fm = []
for p, rel in all_md_files():
    if is_no_fm_file(rel):
        continue
    text = p.read_text(encoding="utf-8", errors="ignore")
    if not has_frontmatter(text):
        no_fm.append(rel)
if no_fm:
    report.append(("frontmatter", "warn", f"{len(no_fm)} 个文件缺 frontmatter"))
    if DETAIL:
        report += [("frontmatter", "info", f"  - {r}") for r in no_fm[:50]]
else:
    ok_count += 1

# ---------- 2. wikilink 断裂 ----------
broken = []
for p, rel in all_md_files():
    text = p.read_text(encoding="utf-8", errors="ignore")
    for m in re.finditer(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]", text):
        target = m.group(1).strip().strip("/")
        if not target or target.startswith(("http", "www")):
            continue
        # 去掉路径前缀，取 basename（Obsidian 按 basename 解析）
        base = target.split("/")[-1]
        if base in PLACEHOLDER_LINKS:
            continue
        if not find_note(base):
            broken.append((rel, target))
if broken:
    report.append(("wikilink", "error", f"{len(broken)} 个断裂双链"))
    if DETAIL:
        report += [("wikilink", "info", f"  - {r} → [[{t}]]") for r, t in broken[:50]]
else:
    ok_count += 1

# ---------- 3. review 堆积 ----------
stale_review = []
for p, rel in all_md_files():
    text = p.read_text(encoding="utf-8", errors="ignore")
    if frontmatter_field(text, "status") == "review":
        mtime = datetime.fromtimestamp(p.stat().st_mtime)
        age_days = (datetime.now() - mtime).days
        if age_days >= 7:
            stale_review.append((rel, age_days))
if stale_review:
    report.append(("review", "warn", f"{len(stale_review)} 个 status:review 文件 ≥7 天未动"))
    if DETAIL:
        report += [("review", "info", f"  - {r}（{d} 天）") for r, d in stale_review[:30]]
else:
    ok_count += 1

# ---------- 4. 06_AI 命名违规 ----------
ai_dir = VAULT / "06_AI"
naming_bad = []
if ai_dir.is_dir():
    for d in sorted(ai_dir.iterdir()):
        if d.is_dir():
            if not re.match(r"^\d{4}-\d{2}-\d{2}_", d.name):
                naming_bad.append(d.name)
    # 06_AI 根目录散落文件
    loose = [f.name for f in ai_dir.iterdir() if f.is_file() and not f.name.startswith(".")]
    if loose:
        naming_bad.append(f"[散落文件] {', '.join(loose)}")
if naming_bad:
    report.append(("06_AI命名", "error", f"{len(naming_bad)} 项不符合 YYYY-MM-DD_主题 规范"))
    if DETAIL:
        report += [("06_AI命名", "info", f"  - {n}") for n in naming_bad]
else:
    ok_count += 1

# ---------- 5. 会议文件错位 ----------
meeting_misplaced = []
meeting_dir = VAULT / "05_档案/会议存档"
for p, rel in all_md_files():
    text = p.read_text(encoding="utf-8", errors="ignore")
    fm_type = frontmatter_field(text, "type")
    if fm_type in ("meeting", "redirect") and not rel.startswith("05_档案/会议存档/"):
        meeting_misplaced.append(rel)
if meeting_misplaced:
    report.append(("会议归位", "error", f"{len(meeting_misplaced)} 个会议/重定向文件在会议存档之外"))
    if DETAIL:
        report += [("会议归位", "info", f"  - {r}") for r in meeting_misplaced]
else:
    ok_count += 1

# ---------- 6. 失效路径引用（仅 dataview FROM，纯文本提及不算） ----------
stale_refs = []
for p, rel in all_md_files():
    text = p.read_text(encoding="utf-8", errors="ignore")
    # 只查 ```dataview 代码块 或 FROM "..." 行
    for m in re.finditer(r'FROM\s*"[^"]*"', text):
        for sp in STALE_PATHS:
            if sp in m.group(0):
                stale_refs.append((rel, sp))
if stale_refs:
    seen = {(r, s) for r, s in stale_refs}
    report.append(("旧路径", "warn", f"{len(seen)} 处废弃路径引用（03_任务/06_灵感库/07_档案）"))
    if DETAIL:
        for r, s in sorted(seen)[:30]:
            report.append(("旧路径", "info", f"  - {r}: {s}"))
else:
    ok_count += 1

# ---------- 7. 空目录 ----------
empty_dirs = []
for d in sorted(p for p in VAULT.rglob("*") if p.is_dir()):
    rel = rel_path(d)
    if is_excluded(rel) or rel.startswith(".git"):
        continue
    entries = [e for e in d.iterdir() if not e.name.startswith(".DS_Store")]
    if not entries:
        empty_dirs.append(rel)
if empty_dirs:
    report.append(("空目录", "info", f"{len(empty_dirs)} 个空目录"))
    if DETAIL:
        report += [("空目录", "info", f"  - {r}") for r in empty_dirs]
else:
    ok_count += 1

# ---------- 8. .DS_Store ----------
ds = [rel_path(p) for p in VAULT.rglob(".DS_Store")]
if ds:
    report.append(("系统文件", "info", f"{len(ds)} 个 .DS_Store 残留"))
    if DETAIL:
        report += [("系统文件", "info", f"  - {r}") for r in ds]
else:
    ok_count += 1

# ---------- 输出 ----------
issues = [r for r in report if r[1] in ("error", "warn")]
print("=" * 56)
print("24帧运营库 · 健康检查报告")
print(f"时间：{datetime.now():%Y-%m-%d %H:%M}")
print("=" * 56)

if not report:
    print("\n✅ 全部检查通过，未发现问题。")
    sys.exit(0)

# 每个类别一行摘要 + 明细
seen_cats = []
for cat, sev, msg in report:
    if cat not in seen_cats:
        seen_cats.append(cat)

label = {"error": "🔴 错误", "warn": "🟡 警告", "info": "🔵 信息"}
for cat in seen_cats:
    items = [(s, m) for c, s, m in report if c == cat]
    sev = items[0][0]
    n = len([1 for s, _ in items if s != "info"])
    print(f"\n{label.get(sev, sev)} {cat}（{n}）")
    if DETAIL:
        for s, m in items:
            print(f"  {m}")
    else:
        for s, m in items[:3]:
            print(f"  {m}")
        if len(items) > 3:
            print(f"  … 共 {len(items)} 条，加 --detail 看全部")

print(f"\n{'=' * 56}")
if issues:
    print(f"共发现问题 {len(issues)} 项（错误 {sum(1 for r in issues if r[1]=='error')} / 警告 {sum(1 for r in issues if r[1]=='warn')}）")
    print("处理建议：错误项尽快修，警告项择机修；信息项可忽略。")
    sys.exit(1)
else:
    print("✅ 无错误无警告（仅信息项）。")
    sys.exit(0)
