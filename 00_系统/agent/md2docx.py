#!/usr/bin/env python3
"""把对外计划书 md 转成 docx（对外发送用）。库内只留 md。"""
import re, os
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

import sys
# 用法: python3 00_系统/agent/md2docx.py <src.md> <dst.docx>
SRC = sys.argv[1] if len(sys.argv) > 1 else "/path/to/plan.md"
DST = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser("~/Downloads/out.docx")

# 库内只留 md；docx 一律输出到 ~/Downloads/ 供对外发送

doc = Document()

# 全局中文字体
style = doc.styles["Normal"]
style.font.name = "微软雅黑"
style.font.size = Pt(10.5)
style.element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")

for i in range(1, 4):
    hs = doc.styles[f"Heading {i}"]
    hs.font.name = "微软雅黑"
    hs.font.size = Pt({1: 17, 2: 14, 3: 12}[i])
    hs.font.color.rgb = RGBColor(0x1a, 0x1a, 0x1a)
    hs.element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")

# 页边距
for s in doc.sections:
    s.left_margin = Cm(2.4); s.right_margin = Cm(2.4)
    s.top_margin = Cm(2.2); s.bottom_margin = Cm(2.2)

def clean(t):
    """去掉 md 标记，保留纯文本"""
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", t)
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", t)
    t = re.sub(r"`(.+?)`", r"\1", t)
    t = re.sub(r"(\[\[?)([^\]|]+)(\|[^]]+)?\]\]?", r"\2", t)  # [[链接|显示]] → 显示
    t = re.sub(r"\[[^\]]*\]\([^)]*\)", "", t)                    # [文本](url) → 文本
    return t.strip()

def set_cell_font(cell, bold=False, size=9.5):
    for p in cell.paragraphs:
        for r in p.runs:
            r.font.name = "微软雅黑"
            r.font.size = Pt(size)
            r.font.bold = bold
            r._element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")

def add_table(rows):
    ncol = max(len(r) for r in rows)
    t = doc.add_table(rows=0, cols=ncol)
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for ri, row in enumerate(rows):
        cells = t.add_row().cells
        for ci in range(ncol):
            txt = row[ci] if ci < len(row) else ""
            cells[ci].text = clean(txt)
            set_cell_font(cells[ci], bold=(ri == 0), size=9.5)
    doc.add_paragraph()

lines = open(SRC, encoding="utf-8").read().splitlines()

# 跳过 frontmatter
start = 0
if lines and lines[0].strip() == "---":
    for i, l in enumerate(lines[1:], 1):
        if l.strip() == "---":
            start = i + 1
            break

tbl_buf = []

def flush():
    global tbl_buf
    if tbl_buf:
        add_table(tbl_buf)
        tbl_buf = []

for raw in lines[start:]:
    line = raw.rstrip()
    # 表格行
    if line.startswith("|"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if set("".join(cells)) <= set("-: "):
            continue
        tbl_buf.append(cells)
        continue
    flush()

    if not line.strip():
        continue
    # 内部段（双链、内部备注）不进入对外文档
    if "INTERNAL-BELOW" in line:
        flush()
        break
    if line.strip() == "---":
        continue

    if line.startswith("# "):
        p = doc.add_paragraph(style="Title")
        r = p.add_run(clean(line[2:]))
        r.font.name = "微软雅黑"; r.font.size = Pt(20); r.bold = True
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif line.startswith("## "):
        doc.add_heading(clean(line[3:]), level=1)
    elif line.startswith("### "):
        doc.add_heading(clean(line[4:]), level=2)
    elif line.startswith(">"):
        txt = clean(line.lstrip("> "))
        if not txt:
            continue
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.6)
        r = p.add_run(txt)
        r.italic = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
    elif re.match(r"^\s*- \[[ x]\] ", line):
        txt = clean(re.sub(r"^\s*- \[[ x]\] ", "", line))
        p = doc.add_paragraph(style="List Bullet")
        p.style = doc.styles["List Bullet"]
        p.clear()
        r = p.add_run("☐ " + txt)
        r.font.name = "微软雅黑"; r.font.size = Pt(10.5)
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
    elif re.match(r"^\d+\. ", line.strip()):
        txt = clean(re.sub(r"^\d+\.\s*", "", line.strip()))
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.6)
        r = p.add_run(txt)
        r.font.name = "微软雅黑"; r.font.size = Pt(10.5)
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
    elif line.startswith("- "):
        p = doc.add_paragraph(style="List Bullet")
        p.clear()
        for part in re.split(r"(\*\*.+?\*\*)", line[2:]):
            if not part:
                continue
            bold = part.startswith("**") and part.endswith("**")
            txt = clean(part)
            if not txt:
                continue
            r = p.add_run(txt)
            r.font.name = "微软雅黑"; r.font.size = Pt(10.5)
            r.bold = bold
            r._element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
    else:
        p = doc.add_paragraph()
        # 处理内联 **加粗**
        parts = re.split(r"(\*\*.+?\*\*)", line)
        for part in parts:
            if not part:
                continue
            bold = part.startswith("**") and part.endswith("**")
            txt = clean(part)
            if not txt:
                continue
            r = p.add_run(txt)
            r.font.name = "微软雅黑"; r.font.size = Pt(10.5)
            r.bold = bold
            r._element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")

flush()
doc.save(DST)
print("saved:", DST, os.path.getsize(DST), "bytes")
