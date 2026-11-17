#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 _数据/数据看板.html（单文件、纯 SVG、无外部依赖）

用法：python3 _skill/scripts/build-dashboard.py
输入：~/Library/Caches/wxmp/articles.json + 年份目录 md
输出：_数据/数据看板.html
"""
import datetime, html, json, os, re, statistics, collections, math

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "_数据")
CACHE = os.path.expanduser("~/Library/Caches/wxmp")
SRC = os.path.join(CACHE, "articles.json")
STAMP = os.path.join(CACHE, "fetched_at.txt")

PAL = {"bg": "#f7f5f2", "card": "#ffffff", "ink": "#1f2328", "muted": "#7a8088",
       "line": "#e6e2dc", "accent": "#b03a2e", "accent2": "#2c6e6f",
       "warm": "#d68910", "cool": "#5b7db1"}


def norm(s):
    s = html.unescape(s or "").replace("\u200b", "")
    return re.sub(r"[\W_]+", "", s, flags=re.UNICODE)


def esc(s):
    return html.escape(str(s), quote=True)


def category(t):
    if re.search(r"路演|主创|到场|导演连线|连线交流|映后", t): return "路演/主创"
    if re.search(r"招募|组讯|志愿者|征片|征集", t): return "招募/组讯"
    if re.search(r"影展|展映|电影节|戛纳|威尼斯|柏林|FIRST|海影节|短片展", t): return "影展/展映"
    if re.search(r"放映|专场|点映|加场|重映|返场|告别场|超前", t): return "放映/专场"
    if re.search(r"转载", t): return "转载"
    return "原创/回顾"


def load():
    arts = json.load(open(SRC, encoding="utf-8"))
    dates, texts, imgs = {}, {}, {}
    for y in sorted(d for d in os.listdir(ROOT) if re.fullmatch(r"\d{4}", d)):
        for f in os.listdir(os.path.join(ROOT, y)):
            if not f.endswith(".md"):
                continue
            b = f[:-3]
            k = norm(b[11:]).replace("amp", "")
            dates.setdefault(k, b[:10])
            t = open(os.path.join(ROOT, y, f), encoding="utf-8").read()
            texts[k] = len(t)
            imgs[k] = len(re.findall(r"!\[[^\]]*\]\(", t))
    best = {}
    for a in arts:
        k = norm(a["title"]).replace("amp", "")
        rd, sh = a.get("read_num") or 0, a.get("share_num") or 0
        if k not in best or rd > best[k]["read"]:
            best[k] = {"read": rd, "share": sh, "title": a["title"].strip(),
                       "date": a.get("date") or dates.get(k, ""), "link": a["link"],
                       "len": texts.get(k, 0), "imgs": imgs.get(k, 0), "cat": category(a["title"])}
    rows = list(best.values())
    rows.sort(key=lambda r: (r["date"] or "9999", r["title"]))
    return rows


def month_of(d):
    return d[:7] if d else ""


def pct(x, n):
    return 0 if not n else 100.0 * x / n


# ---------- SVG helpers ----------
def svg_open(w, h):
    return f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" style="display:block">'


def ticks(vmax, n=4):
    if vmax <= 0:
        return [0, 1]
    raw = vmax / n
    mag = 10 ** math.floor(math.log10(raw))
    step = mag
    for m in (1, 2, 2.5, 5, 10):
        step = mag * m
        if step * n >= vmax:
            break
    out, v = [], 0
    while v < vmax * 0.999:
        out.append(v); v += step
    out.append(v)
    return out


def bar_line_chart(months, counts, avgs, w=1080, h=300):
    pad = {"l": 46, "r": 46, "t": 18, "b": 42}
    iw, ih = w - pad["l"] - pad["r"], h - pad["t"] - pad["b"]
    cmax, amax = max(counts) if counts else 1, max(avgs) if avgs else 1
    ct, at = ticks(cmax, 4), ticks(amax, 4)
    ct_max, at_max = ct[-1] or 1, at[-1] or 1
    bw = iw / max(len(months), 1)
    s = [svg_open(w, h)]
    for t in ct:
        y = pad["t"] + ih - ih * t / ct_max
        s.append(f'<line x1="{pad["l"]}" x2="{w-pad["r"]}" y1="{y:.1f}" y2="{y:.1f}" stroke="{PAL["line"]}"/>')
        s.append(f'<text x="{pad["l"]-6}" y="{y+4:.1f}" text-anchor="end" font-size="10" fill="{PAL["muted"]}">{int(t)}</text>')
    for t in at:
        y = pad["t"] + ih - ih * t / at_max
        s.append(f'<text x="{w-pad["r"]+5}" y="{y+4:.1f}" font-size="10" fill="{PAL["accent2"]}">{int(t)}</text>')
    for i, (m, c, a) in enumerate(zip(months, counts, avgs)):
        x = pad["l"] + i * bw
        bh = ih * c / ct_max
        s.append(f'<rect x="{x+bw*0.18:.1f}" y="{pad["t"]+ih-bh:.1f}" width="{bw*0.64:.1f}" height="{bh:.1f}" rx="2" fill="{PAL["accent"]}" opacity="0.82"><title>{m}：{c} 篇</title></rect>')
        if i % max(1, len(months) // 12) == 0 or i == len(months) - 1:
            s.append(f'<text x="{x+bw/2:.1f}" y="{h-20}" text-anchor="middle" font-size="9.5" fill="{PAL["muted"]}">{m[2:]}</text>')
    pts = []
    for i, a in enumerate(avgs):
        x = pad["l"] + i * bw + bw / 2
        y = pad["t"] + ih - ih * a / at_max
        pts.append(f"{x:.1f},{y:.1f}")
    if pts:
        s.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{PAL["accent2"]}" stroke-width="2"/>')
        for i, a in enumerate(avgs):
            x = pad["l"] + i * bw + bw / 2
            y = pad["t"] + ih - ih * a / at_max
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.4" fill="{PAL["accent2"]}"><title>{months[i]}：篇均 {a:.0f} 阅读</title></circle>')
    s.append(f'<text x="{pad["l"]}" y="12" font-size="10" fill="{PAL["accent"]}">柱：发文数</text>')
    s.append(f'<text x="{pad["l"]+74}" y="12" font-size="10" fill="{PAL["accent2"]}">线：篇均阅读</text>')
    s.append("</svg>")
    return "".join(s)


def hbar(items, w=560, rowh=26, label_w=190, value_fmt=lambda v: f"{v:,.0f}", color=None, maxchars=16):
    """items: [(label, value, tip)]"""
    h = max(60, len(items) * rowh + 16)
    vmax = max([v for _, v, _ in items] or [1]) or 1
    s = [svg_open(w, h)]
    for i, (label, v, tip) in enumerate(items):
        y = 8 + i * rowh
        bw = (w - label_w - 70) * v / vmax
        s.append(f'<text x="{label_w-8}" y="{y+13}" text-anchor="end" font-size="11.5" fill="{PAL["ink"]}">{esc(label[:maxchars])}</text>')
        s.append(f'<rect x="{label_w}" y="{y+3}" width="{max(bw,1):.1f}" height="{rowh-9}" rx="3" fill="{color or PAL["accent2"]}" opacity="0.85"><title>{esc(tip)}</title></rect>')
        s.append(f'<text x="{label_w+max(bw,1)+6:.1f}" y="{y+13}" font-size="10.5" fill="{PAL["muted"]}">{esc(value_fmt(v))}</text>')
    s.append("</svg>")
    return "".join(s)


def heatmap(years, matrix, counts, w=1080, h=280):
    """matrix[year][month] = 篇均阅读；counts[year][month] = 篇数"""
    pad = {"l": 56, "r": 20, "t": 30, "b": 20}
    iw, ih = w - pad["l"] - pad["r"], h - pad["t"] - pad["b"]
    cw, ch = iw / 12, ih / max(len(years), 1)
    vmax = max([v for row in matrix.values() for v in row.values()] or [1]) or 1
    s = [svg_open(w, h)]
    for j, m in enumerate(["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]):
        s.append(f'<text x="{pad["l"]+cw*(j+0.5):.1f}" y="18" text-anchor="middle" font-size="12" fill="{PAL["muted"]}">{m}</text>')
    for i, y in enumerate(years):
        s.append(f'<text x="{pad["l"]-8}" y="{pad["t"]+ch*(i+0.5)+4:.1f}" text-anchor="end" font-size="12" fill="{PAL["ink"]}">{y}</text>')
        for j in range(12):
            v = matrix.get(y, {}).get(j + 1, 0)
            n = counts.get(y, {}).get(j + 1, 0)
            a = 0.08 + 0.82 * (v / vmax) if v else 0.04
            s.append(f'<rect x="{pad["l"]+cw*j+1:.1f}" y="{pad["t"]+ch*i+1:.1f}" width="{cw-2:.1f}" height="{ch-2:.1f}" rx="2" fill="{PAL["accent"]}" opacity="{a:.2f}"><title>{y}年{j+1}月：{n} 篇，篇均 {v:,.0f}</title></rect>')
            if v:
                s.append(f'<text x="{pad["l"]+cw*(j+0.5):.1f}" y="{pad["t"]+ch*(i+0.5)+4:.1f}" text-anchor="middle" font-size="10.5" fill="{"#fff" if v/vmax>0.55 else PAL["ink"]}">{v:.0f}</text>')
    s.append("</svg>")
    return "".join(s)


def scatter(points, w=1080, h=340):
    """points: [(x, y, label, cat)]"""
    pad = {"l": 52, "r": 20, "t": 18, "b": 40}
    iw, ih = w - pad["l"] - pad["r"], h - pad["t"] - pad["b"]
    xmax = max([p[0] for p in points] or [1]) or 1
    ymax = max([p[1] for p in points] or [1]) or 1
    s = [svg_open(w, h)]
    for k in range(5):
        y = pad["t"] + ih - ih * k / 4
        s.append(f'<line x1="{pad["l"]}" x2="{w-pad["r"]}" y1="{y:.1f}" y2="{y:.1f}" stroke="{PAL["line"]}"/>')
        s.append(f'<text x="{pad["l"]-6}" y="{y+4:.1f}" text-anchor="end" font-size="10" fill="{PAL["muted"]}">{int(ymax*k/4):,}</text>')
    colors = {c: col for c, col in zip(["路演/主创", "影展/展映", "放映/专场", "原创/回顾", "招募/组讯", "转载"],
                                       [PAL["accent"], PAL["accent2"], PAL["warm"], PAL["cool"], "#8e6bb0", "#999"])}
    for x, y, label, cat in points:
        cx = pad["l"] + iw * x / xmax
        cy = pad["t"] + ih - ih * y / ymax
        s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.6" fill="{colors.get(cat, "#888")}" opacity="0.72"><title>{esc(label)}：{int(x)} 字 / {y:,} 阅读</title></circle>')
    for k in range(5):
        x = pad["l"] + iw * k / 4
        s.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{pad["t"]+ih}" y2="{pad["t"]+ih+4}" stroke="{PAL["muted"]}"/>')
        s.append(f'<text x="{x:.1f}" y="{pad["t"]+ih+16}" text-anchor="middle" font-size="9.5" fill="{PAL["muted"]}">{int(xmax*k/4):,}</text>')
    s.append(f'<text x="{pad["l"]+iw/2:.0f}" y="{h-8}" text-anchor="middle" font-size="10" fill="{PAL["muted"]}">正文长度（字符）</text>')
    s.append(f'<text x="12" y="{pad["t"]+ih/2:.0f}" font-size="10" fill="{PAL["muted"]}" transform="rotate(-90 12 {pad["t"]+ih/2:.0f})" text-anchor="middle">阅读量</text>')
    s.append("</svg>")
    return "".join(s)



def bubble_chart(items, w=560, h=320):
    """items: [(label, count, median, total)]  产量 × 中位阅读，气泡=总阅读"""
    pad = {"l": 52, "r": 16, "t": 16, "b": 38}
    iw, ih = w - pad["l"] - pad["r"], h - pad["t"] - pad["b"]
    xmax = max([i[1] for i in items] or [1]) * 1.15 or 1
    ymax = max([i[2] for i in items] or [1]) * 1.15 or 1
    rmax = max([i[3] for i in items] or [1]) or 1
    s = [svg_open(w, h)]
    for k in range(5):
        y = pad["t"] + ih - ih * k / 4
        s.append(f'<line x1="{pad["l"]}" x2="{w-pad["r"]}" y1="{y:.1f}" y2="{y:.1f}" stroke="{PAL["line"]}"/>')
        s.append(f'<text x="{pad["l"]-6}" y="{y+4:.1f}" text-anchor="end" font-size="9.5" fill="{PAL["muted"]}">{int(ymax*k/4):,}</text>')
        x = pad["l"] + iw * k / 4
        s.append(f'<text x="{x:.1f}" y="{h-18}" text-anchor="middle" font-size="9.5" fill="{PAL["muted"]}">{int(xmax*k/4)}</text>')
    for label, n, med, total in items:
        cx = pad["l"] + iw * n / xmax
        cy = pad["t"] + ih - ih * med / ymax
        r = 6 + 20 * math.sqrt(total / rmax)
        s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{PAL["accent2"]}" opacity="0.28"><title>{label}：{n} 篇，中位 {med:,.0f}，总阅读 {total:,}</title></circle>')
        s.append(f'<text x="{cx:.1f}" y="{cy+4:.1f}" text-anchor="middle" font-size="10.5" fill="{PAL["ink"]}">{esc(label)}</text>')
    s.append(f'<text x="{pad["l"]+iw/2:.0f}" y="{h-2}" text-anchor="middle" font-size="9.5" fill="{PAL["muted"]}">篇数 →</text>')
    s.append("</svg>")
    return "".join(s)


def quadrant_chart(points, med_read, med_share, w=1080, h=360):
    """points: [(read, share_rate, label, cat)]"""
    pad = {"l": 56, "r": 24, "t": 20, "b": 42}
    iw, ih = w - pad["l"] - pad["r"], h - pad["t"] - pad["b"]
    xmax = max([p[0] for p in points] or [1]) * 1.05
    ymax = max([p[1] for p in points] or [1]) * 1.1
    colors = {c: col for c, col in zip(["路演/主创", "影展/展映", "放映/专场", "原创/回顾", "招募/组讯", "转载"],
                                       [PAL["accent"], PAL["accent2"], PAL["warm"], PAL["cool"], "#8e6bb0", "#999"])}
    s = [svg_open(w, h)]
    for k in range(5):
        y = pad["t"] + ih - ih * k / 4
        s.append(f'<line x1="{pad["l"]}" x2="{w-pad["r"]}" y1="{y:.1f}" y2="{y:.1f}" stroke="{PAL["line"]}"/>')
        s.append(f'<text x="{pad["l"]-6}" y="{y+4:.1f}" text-anchor="end" font-size="9.5" fill="{PAL["muted"]}">{ymax*k/4:.1f}%</text>')
        x = pad["l"] + iw * k / 4
        s.append(f'<text x="{x:.1f}" y="{h-20}" text-anchor="middle" font-size="9.5" fill="{PAL["muted"]}">{int(xmax*k/4):,}</text>')
    mx = pad["l"] + iw * med_read / xmax
    my = pad["t"] + ih - ih * med_share / ymax
    s.append(f'<line x1="{mx:.1f}" x2="{mx:.1f}" y1="{pad["t"]}" y2="{pad["t"]+ih}" stroke="{PAL["muted"]}" stroke-dasharray="4,4" opacity="0.6"/>')
    s.append(f'<line x1="{pad["l"]}" x2="{w-pad["r"]}" y1="{my:.1f}" y2="{my:.1f}" stroke="{PAL["muted"]}" stroke-dasharray="4,4" opacity="0.6"/>')
    for read, sr, label, cat in points:
        cx = pad["l"] + iw * read / xmax
        cy = pad["t"] + ih - ih * sr / ymax
        s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.4" fill="{colors.get(cat, "#888")}" opacity="0.7"><title>{esc(label)}：{read:,} 阅读，分享率 {sr:.1f}%</title></circle>')
    s.append(f'<text x="{pad["l"]+iw*0.78:.0f}" y="{pad["t"]+14}" font-size="10" fill="{PAL["muted"]}">高阅读 · 高分享（破圈）</text>')
    s.append(f'<text x="{pad["l"]+iw*0.02:.0f}" y="{pad["t"]+14}" font-size="10" fill="{PAL["muted"]}">低阅读 · 高分享（小众共鸣）</text>')
    s.append(f'<text x="{pad["l"]+iw/2:.0f}" y="{h-4}" text-anchor="middle" font-size="9.5" fill="{PAL["muted"]}">阅读量 →</text>')
    s.append("</svg>")
    return "".join(s)

def pareto_chart(reads, w=1080, h=280):
    pad = {"l": 52, "r": 46, "t": 18, "b": 34}
    iw, ih = w - pad["l"] - pad["r"], h - pad["t"] - pad["b"]
    vals = sorted(reads, reverse=True)
    total = sum(vals) or 1
    cum, acc = [], 0
    for v in vals:
        acc += v
        cum.append(acc / total * 100)
    s = [svg_open(w, h)]
    for k in range(5):
        y = pad["t"] + ih - ih * k / 4
        s.append(f'<line x1="{pad["l"]}" x2="{w-pad["r"]}" y1="{y:.1f}" y2="{y:.1f}" stroke="{PAL["line"]}"/>')
        s.append(f'<text x="{pad["l"]-6}" y="{y+4:.1f}" text-anchor="end" font-size="10" fill="{PAL["muted"]}">{k*25}%</text>')
    pts = []
    for i, p in enumerate(cum):
        x = pad["l"] + iw * i / max(len(cum) - 1, 1)
        y = pad["t"] + ih - ih * p / 100
        pts.append(f"{x:.1f},{y:.1f}")
    s.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{PAL["accent"]}" stroke-width="2"/>')
    for frac in (0.1, 0.2, 0.5):
        i = min(len(cum) - 1, int(frac * len(cum)))
        x = pad["l"] + iw * i / max(len(cum) - 1, 1)
        y = pad["t"] + ih - ih * cum[i] / 100
        s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{PAL["accent"]}"><title>前 {int(frac*100)}% 文章占 {cum[i]:.0f}% 阅读</title></circle>')
    s.append(f'<text x="{pad["l"]}" y="{h-8}" font-size="10" fill="{PAL["muted"]}">文章按阅读量从高到低排序</text>')
    s.append(f'<text x="{w-pad["r"]}" y="{pad["t"]+10}" text-anchor="end" font-size="10" fill="{PAL["accent"]}">累计阅读占比</text>')
    s.append("</svg>")
    return "".join(s)


def card(title, body, note=""):
    return f'<section class="card"><h2>{esc(title)}</h2>{body}' + (f'<p class="note">{note}</p>' if note else "") + "</section>"


def main():
    rows = load()
    dated = [r for r in rows if r["date"]]
    fetched = open(STAMP, encoding="utf-8").read().strip() if os.path.exists(STAMP) else ""
    today = datetime.date.today().isoformat()
    total_reads = sum(r["read"] for r in rows)
    total_share = sum(r["share"] for r in rows)
    med = int(statistics.median([r["read"] for r in rows if r["read"]]))
    p90 = int(sorted([r["read"] for r in rows if r["read"]])[int(len([r for r in rows if r["read"]]) * 0.9)])

    months = sorted({month_of(r["date"]) for r in dated})
    mcount = [sum(1 for r in dated if month_of(r["date"]) == m) for m in months]
    mavg = []
    for m in months:
        v = [r["read"] for r in dated if month_of(r["date"]) == m]
        mavg.append(sum(v) / len(v) if v else 0)

    cats = ["路演/主创", "影展/展映", "放映/专场", "原创/回顾", "招募/组讯", "转载"]
    cat_stat = {}
    for c in cats:
        v = [r for r in rows if r["cat"] == c]
        if not v: continue
        reads = [r["read"] for r in v]
        cat_stat[c] = {"n": len(v), "median": statistics.median(reads), "mean": sum(reads) / len(reads),
                       "total": sum(reads), "share_rate": pct(sum(r["share"] for r in v), max(sum(reads), 1))}
    cat_items = sorted([(c, s["median"], f"{c}：{s['n']} 篇，中位 {s['median']:.0f}，篇均 {s['mean']:.0f}") for c, s in cat_stat.items()], key=lambda x: -x[1])

    top = sorted(rows, key=lambda r: -r["read"])[:20]
    years = sorted({r["date"][:4] for r in dated})
    heat = {y: collections.defaultdict(list) for y in years}
    for r in dated:
        heat[r["date"][:4]][int(r["date"][5:7])].append(r["read"])
    matrix = {y: {m: sum(v)/len(v) for m, v in d.items()} for y, d in heat.items()}
    counts = {y: {m: len(v) for m, v in d.items()} for y, d in heat.items()}

    buckets = [(0, 50), (50, 100), (100, 200), (200, 400), (400, 800), (800, 1500), (1500, 3000), (3000, 10**9)]
    hist = []
    for lo, hi in buckets:
        n = sum(1 for r in rows if lo <= r["read"] < hi)
        hist.append((f"{lo}-{hi if hi < 10**9 else '∞'}", n, f"{lo}~{hi} 阅读：{n} 篇"))

    # 标题特征
    feats = [
        ("含《片名》", lambda t: "《" in t), ("含「」标签", lambda t: "「" in t),
        ("含数字/日期", lambda t: bool(re.search(r"\d", t))), ("含问号", lambda t: "？" in t or "?" in t),
        ("含感叹号", lambda t: "！" in t or "!" in t),
    ]
    feat_rows = []
    for name, fn in feats:
        yes = [r["read"] for r in rows if fn(r["title"])]
        no = [r["read"] for r in rows if not fn(r["title"])]
        if yes and no:
            feat_rows.append((name, statistics.mean(yes), len(yes), statistics.mean(no), len(no)))

    # 星期
    wd_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    wd_reads = collections.defaultdict(list)
    for r in dated:
        try:
            d = datetime.date.fromisoformat(r["date"])
            wd_reads[d.weekday()].append(r["read"])
        except Exception:
            pass
    wd_items = [(wd_names[i], statistics.mean(wd_reads[i]), f"{wd_names[i]}：{len(wd_reads[i])} 篇，篇均 {statistics.mean(wd_reads[i]):.0f}") for i in range(7) if wd_reads[i]]

    # 片名
    films = collections.defaultdict(list)
    for r in rows:
        for f in re.findall(r"《([^》]{1,20})》", r["title"]):
            films[f].append(r["read"])
    film_items = [(f, statistics.mean(v), f"《{f}》：{len(v)} 篇，篇均 {statistics.mean(v):.0f}") for f, v in films.items() if len(v) >= 2]
    film_items.sort(key=lambda x: -x[1])

    # 系列
    series = [("FIRST 主动放映", r"FIRST"), ("戛纳短片/一日", r"戛纳"), ("威尼斯", r"威尼斯"), ("柏林", r"柏林"),
              ("海影节", r"海影节"), ("影展/短片展", r"影展|短片展"), ("路演", r"路演"), ("专场", r"专场"), ("组讯/招募", r"组讯|招募")]
    series_items = []
    for name, pat in series:
        v = [r["read"] for r in rows if re.search(pat, r["title"])]
        if len(v) >= 3:
            series_items.append((name, statistics.mean(v), f"{name}：{len(v)} 篇，篇均 {statistics.mean(v):.0f}"))
    series_items.sort(key=lambda x: -x[1])

    # 分享象限
    qpoints = [(r["read"], pct(r["share"], r["read"]), r["title"], r["cat"]) for r in rows if r["read"] and r["share"] > 0]
    med_read = statistics.median([q[0] for q in qpoints]) if qpoints else 0
    med_share = statistics.median([q[1] for q in qpoints]) if qpoints else 0

    # 系列逐年
    series_year = []
    for name, pat in (("FIRST 主动放映", r"FIRST"), ("戛纳短片/一日", r"戛纳")):
        for y in years:
            v = [r["read"] for r in dated if r["date"][:4] == y and re.search(pat, r["title"])]
            if v:
                series_year.append({"series": name, "year": y, "n": len(v), "avg": sum(v)/len(v), "max": max(v)})

    # 年度汇总
    year_stats = []
    for y in years:
        v = [r for r in dated if r["date"][:4] == y]
        if not v: continue
        reads = [r["read"] for r in v]
        ds = sorted(r["date"] for r in v)
        gaps = [(datetime.date.fromisoformat(ds[i+1]) - datetime.date.fromisoformat(ds[i])).days for i in range(len(ds)-1)]
        year_stats.append({
            "y": y, "n": len(v), "total": sum(reads), "avg": sum(reads)/len(reads),
            "median": statistics.median(reads), "share": pct(sum(r["share"] for r in v), max(sum(reads),1)),
            "gap": statistics.median(gaps) if gaps else 0,
        })

    # 近 90 天
    cutoff = (datetime.date.today() - datetime.timedelta(days=92)).isoformat()
    recent = sorted([r for r in dated if r["date"] >= cutoff], key=lambda r: r["date"])

    # 12 个月对比
    d12 = (datetime.date.today() - datetime.timedelta(days=365)).isoformat()
    d24 = (datetime.date.today() - datetime.timedelta(days=730)).isoformat()
    cur = [r["read"] for r in dated if r["date"] >= d12]
    prev = [r["read"] for r in dated if d24 <= r["date"] < d12]

    # 自动洞察
    insights = []
    if cat_stat.get("路演/主创") and cat_stat.get("放映/专场"):
        ratio = cat_stat["路演/主创"]["median"] / max(cat_stat["放映/专场"]["median"], 1)
        insights.append(f"路演/主创类中位阅读 {cat_stat['路演/主创']['median']:.0f}，是日常放映类的 <b>{ratio:.1f} 倍</b>，仍是流量杠杆。")
    reads_sorted = sorted([r["read"] for r in rows if r["read"]], reverse=True)
    if reads_sorted:
        top10 = sum(reads_sorted[:max(1, len(reads_sorted) // 10)]) / max(sum(reads_sorted), 1) * 100
        insights.append(f"前 10% 的文章贡献了 <b>{top10:.0f}%</b> 的阅读，长尾极长，选题要围绕头部事件。")
    if cur and prev:
        delta = (statistics.mean(cur) - statistics.mean(prev)) / max(statistics.mean(prev), 1) * 100
        insights.append(f"近 12 个月篇均阅读 {statistics.mean(cur):.0f}，较此前 12 个月 <b>{delta:+.0f}%</b>。")
    if wd_items:
        best = max(wd_items, key=lambda x: x[1])
        insights.append(f"发布效果最好的星期是 <b>{best[0]}</b>（篇均 {best[1]:.0f}），可把重点推文排到这一天。")
    if series_items:
        s0 = series_items[0]
        insights.append(f"系列里篇均最高的是 <b>{s0[0]}</b>（{s0[1]:.0f}），可评估是否加大该系列排期。")
    if cat_stat.get("招募/组讯"):
        insights.append(f"招募/组讯类共 {cat_stat['招募/组讯']['n']} 篇，篇均 {cat_stat['招募/组讯']['mean']:.0f}，业务信息同样能带来稳定阅读。")

    decisions = []
    if cat_stat.get("路演/主创") and cat_stat.get("放映/专场"):
        decisions.append(f"排期：把路演/主创作为月度主推（中位 {cat_stat['路演/主创']['median']:.0f}，是日常放映 {cat_stat['放映/专场']['median']:.0f} 的 {cat_stat['路演/主创']['median']/max(cat_stat['放映/专场']['median'],1):.1f} 倍）。")
    if cat_stat.get("招募/组讯"):
        decisions.append(f"业务信息：招募/组讯篇均 {cat_stat['招募/组讯']['mean']:.0f}，建议固定每月 1 篇，兼顾招募与阅读。")
    if reads_sorted:
        decisions.append(f"选题结构：前 10% 文章占 {top10:.0f}% 阅读，每月至少安排 1 个头部事件（路演/影展/FIRST），其余内容围绕它做预热与回顾。")
    if wd_items:
        decisions.append(f"发布节奏：周四篇均最高（{max(wd_items, key=lambda x: x[1])[1]:.0f}），重点推文优先排周四；篇均间隔中位约 {year_stats[-1]['gap']:.0f} 天，保持稳定节奏。")
    decision_html = "".join(f"<li>{x}</li>" for x in decisions)
    # 组装 HTML
    kpis = [
        ("文章总数", f"{len(rows)}", "去重后"),
        ("累计阅读", f"{total_reads:,}", f"{len([r for r in rows if r['read']])} 篇有数据"),
        ("篇均阅读", f"{total_reads/len(rows):.0f}" if rows else "0", f"中位 {med:,}"),
        ("P90 阅读", f"{p90:,}", "头部线"),
        ("分享率", f"{pct(total_share, total_reads):.1f}%", f"分享 {total_share:,}"),
        ("时间跨度", f"{dated[0]['date'][:7]} → {dated[-1]['date'][:7]}" if dated else "—", f"{len(dated)} 篇有日期"),
    ]
    kpi_html = "".join(f'<div class="kpi"><div class="k">{esc(k)}</div><div class="v{" small" if k == "时间跨度" else ""}">{esc(v)}</div><div class="s">{esc(s)}</div></div>' for k, v, s in kpis)

    sections = []
    sections.append(card("月度节奏：发文量 vs 篇均阅读", bar_line_chart(months, mcount, mavg),
                         "柱越高说明当月发得越多；线越高说明单篇越能打。两条线背离时，通常是「发得多但不精」。"))
    sections.append(f'<div class="grid2">' +
                    card("分类表现（中位阅读）", hbar(cat_items, w=560),
                         "中位数比平均值更抗爆款干扰，适合判断一类内容的「基本盘」。") +
                    card("选题象限：产量 × 中位阅读", bubble_chart([(c, s["n"], s["median"], s["total"]) for c, s in cat_stat.items()]),
                         "气泡大小=总阅读。右上角是主力品类，左上角是低频高回报，右下角多发但单篇弱，需压缩。") +
                    '</div>')
    sections.append(card("TOP 20 单篇", hbar([(r["title"], r["read"], f"{r['date']}｜{r['read']:,} 阅读｜{r['cat']}") for r in top], w=1080, rowh=24, label_w=330, maxchars=22),
                         "头部集中在路演、影展与 FIRST；这些是复盘选题时最值得复用的模板。"))
    sections.append(card("年度 × 月份篇均阅读热力", heatmap(years, matrix, counts),
                         "颜色越深表示当月单篇越能打，数字为篇均阅读；空档月份留白。鼠标悬停可看当月篇数。"))
    sections.append(f'<div class="grid2">' + card("阅读分布（长尾）", hbar(hist, w=560, label_w=110, value_fmt=lambda v: f"{v} 篇"), "如果 0-200 区间占比过高，说明多数内容没穿过基础粉丝层。") +
                    card("帕累托：头部集中度", pareto_chart([r["read"] for r in rows if r["read"]]), "前 20% 文章的阅读占比，决定你该把精力押在少数选题还是铺量。") + '</div>')
    sections.append(f'<div class="grid2">' + card("标题特征 vs 篇均阅读", hbar([(n, m, f"{n}：{c} 篇，篇均 {m:.0f}") for n, m, c, _, _ in feat_rows], w=560, label_w=130, value_fmt=lambda v: f"{v:.0f}"),
                         "相关性不等于因果，但能提示哪种标题结构更常出现在高阅读文章里。") +
                    card("星期分布（篇均阅读）", hbar(wd_items, w=560, label_w=70), "按发布日期统计，仅含有日期的文章。") + '</div>')
    sections.append(f'<div class="grid2">' + card("系列/IP 篇均阅读", hbar(series_items[:10], w=560, label_w=130), "系列标签按标题关键词匹配，可横向比较不同 IP 的带量能力。") +
                    card("片名复现（≥2 篇）", hbar(film_items[:10], w=560, label_w=150, value_fmt=lambda v: f"{v:,.0f}"), "同一部片被多次写到时，篇均阅读可反映观众关注度与疲劳度。") + '</div>')
    sections.append(card("阅读 × 分享象限", quadrant_chart(qpoints, med_read, med_share),
                         "右上=高阅读高分享（破圈）；左上=低阅读高分享（小众共鸣）；右下=高阅读低分享（信息型，可优化转发理由）。"))
    sy_rows = ''.join(f'<tr><td>{x["series"]}</td><td>{x["year"]}</td><td class="num">{x["n"]}</td><td class="num">{x["avg"]:.0f}</td><td class="num">{x["max"]:,}</td></tr>' for x in series_year)
    sections.append(card("系列逐年表现", f'<table><thead><tr><th>系列</th><th>年份</th><th class="num">篇数</th><th class="num">篇均</th><th class="num">最高</th></tr></thead><tbody>{sy_rows}</tbody></table>',
                         "看系列的生命周期：篇均下滑通常意味着观众疲劳或选题重复，需要换角度。"))
    sections.append(card("决策清单（自动生成）", f'<ul class="insights">{decision_html}</ul>'))
    sections.append(card("正文长度 vs 阅读量", scatter([(r["len"], r["read"], r["title"], r["cat"]) for r in dated if r["len"]]),
                         "点越靠右越长，越靠上阅读越高；用来判断「长文是否值得」。"))

    year_rows = ''.join(
        f'<tr><td>{x["y"]}</td><td class="num">{x["n"]}</td><td class="num">{x["total"]:,}</td>'
        f'<td class="num">{x["avg"]:.0f}</td><td class="num">{x["median"]:,.0f}</td>'
        f'<td class="num">{x["share"]:.1f}%</td><td class="num">{x["gap"]:.0f}</td></tr>' for x in year_stats)
    year_table = ('<table><thead><tr><th>年份</th><th class="num">篇数</th><th class="num">总阅读</th>'
                  '<th class="num">篇均</th><th class="num">中位</th><th class="num">分享率</th><th class="num">篇均间隔(天)</th>'
                  f'</tr></thead><tbody>{year_rows}</tbody></table>')
    sections.insert(2, f'<div class="grid2">' + card("年度汇总", year_table, "篇均间隔 = 相邻两篇发布日期间隔的中位数。注：2024 年前分享率异常偏低，可能是后台统计口径/数据缺失，不宜跨年直接对比。") +
                    card("分类分享率（分享/阅读）", hbar([(c, s["share_rate"], f"{c}：分享率 {s['share_rate']:.1f}%") for c, s in sorted(cat_stat.items(), key=lambda x: -x[1]["share_rate"])], w=560, label_w=120, value_fmt=lambda v: f"{v:.1f}%"), "分享率反映「值得转给别人」的程度，与阅读量不完全同步。") + '</div>')

    sec_recent = ''.join(f'<tr><td>{r["date"]}</td><td><a href="{esc(r["link"])}" target="_blank" rel="noopener">{esc(r["title"][:38])}</a></td><td class="num">{r["read"]:,}</td><td>{esc(r["cat"])}</td></tr>' for r in recent)
    sections.append(card("近 90 天文章", f'<table><thead><tr><th>日期</th><th>文章</th><th class="num">阅读</th><th>类别</th></tr></thead><tbody>{sec_recent}</tbody></table>'))
    insight_html = "".join(f"<li>{x}</li>" for x in insights)
    sections.insert(0, card("自动洞察", f'<ul class="insights">{insight_html}</ul>'))

    html_out = f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>24帧公众号数据看板</title>
<style>
  :root {{ --bg:{PAL["bg"]}; --card:{PAL["card"]}; --ink:{PAL["ink"]}; --muted:{PAL["muted"]}; --line:{PAL["line"]}; --accent:{PAL["accent"]}; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--ink); font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif; line-height:1.6; }}
  .wrap {{ max-width:1180px; margin:0 auto; padding:28px 20px 60px; }}
  header {{ display:flex; align-items:flex-end; justify-content:space-between; gap:16px; flex-wrap:wrap; margin-bottom:22px; }}
  h1 {{ font-size:26px; margin:0; letter-spacing:.02em; }}
  .sub {{ color:var(--muted); font-size:12.5px; }}
  .kpis {{ display:grid; grid-template-columns:repeat(6,1fr); gap:12px; margin-bottom:18px; }}
  .kpi {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:12px 14px; }}
  .kpi .k {{ font-size:11.5px; color:var(--muted); }}
  .kpi .v {{ font-size:22px; font-weight:700; margin-top:2px; }}
  .kpi .v.small {{ font-size:14px; line-height:1.5; }}
  .kpi .s {{ font-size:10.5px; color:var(--muted); }}
  .card {{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:16px 18px 12px; margin-bottom:16px; }}
  .card h2 {{ font-size:14px; margin:0 0 10px; font-weight:600; letter-spacing:.02em; }}
  .note {{ font-size:11.5px; color:var(--muted); margin:8px 0 2px; }}
  .grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; align-items:start; }}
  .insights {{ margin:4px 0 6px; padding-left:20px; font-size:13.5px; }}
  .insights li {{ margin:5px 0; }}
  table {{ width:100%; border-collapse:collapse; font-size:12.5px; }}
  th,td {{ text-align:left; padding:6px 8px; border-bottom:1px solid var(--line); }}
  th {{ color:var(--muted); font-weight:500; font-size:11.5px; }}
  td.num {{ text-align:right; font-variant-numeric:tabular-nums; }}
  a {{ color:var(--accent); text-decoration:none; }}
  a:hover {{ text-decoration:underline; }}
  footer {{ color:var(--muted); font-size:11.5px; margin-top:18px; }}
  @media (max-width:900px) {{ .kpis {{ grid-template-columns:repeat(3,1fr); }} .grid2 {{ grid-template-columns:1fr; }} }}
</style></head><body><div class="wrap">
<header><div><h1>24帧公众号数据看板</h1><div class="sub">文章 {len(rows)} 篇（后台 {len(json.load(open(SRC,encoding="utf-8")))} 条去重）· 阅读 {total_reads:,} · 数据抓取 {esc(fetched or today)}</div></div>
<div class="sub">生成 {today}</div></header>
<div class="kpis">{kpi_html}</div>
{''.join(sections)}
<footer>口径：阅读/分享为后台累计值；日期优先后台时间，缺失时按存档文件名补；未入档的 9 条（6 条 tempkey 失效 + 3 条按规则移除）不计入图表。图表为静态 SVG，鼠标悬停可看数值。</footer>
</div></body></html>'''
    os.makedirs(DATA, exist_ok=True)
    out = os.path.join(DATA, "数据看板.html")
    open(out, "w", encoding="utf-8").write(html_out)

    # ---- Obsidian / GitHub 可读的 Markdown 看板（图表截成 PNG 内嵌）----
    shots = {
        "月度节奏：发文量 vs 篇均阅读": "monthly.png",
        "分类表现（中位阅读）": "category-median.png",
        "选题象限：产量 × 中位阅读": "category-quadrant.png",
        "分类分享率（分享/阅读）": "share-rate.png",
        "TOP 20 单篇": "top20.png",
        "年度 × 月份篇均阅读热力": "heatmap.png",
        "阅读分布（长尾）": "distribution.png",
        "帕累托：头部集中度": "pareto.png",
        "标题特征 vs 篇均阅读": "title-features.png",
        "星期分布（篇均阅读）": "weekday.png",
        "系列/IP 篇均阅读": "series.png",
        "片名复现（≥2 篇）": "films.png",
        "阅读 × 分享象限": "quadrant-engagement.png",
        "正文长度 vs 阅读量": "length.png",
    }
    imgdir = os.path.join(DATA, "图表")
    os.makedirs(imgdir, exist_ok=True)
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            pg = b.new_page(viewport={"width": 1240, "height": 1000}, device_scale_factor=2)
            pg.goto("file://" + out)
            pg.wait_for_timeout(500)
            for card_el in pg.locator("section.card").all():
                h2 = card_el.locator("h2").inner_text().strip()
                if h2 in shots:
                    card_el.screenshot(path=os.path.join(imgdir, shots[h2]))
            b.close()
        print(f"   图表截图：{len(shots)} 张 → {imgdir}")
    except Exception as e:
        print(f"   ⚠ 图表截图失败（Markdown 看板可能缺图）：{str(e)[:80]}")

    kpi_md = "\n".join(f"| {k} | {v} | {s} |" for k, v, s in kpis)
    _md = lambda x: x.replace("<b>", "**").replace("</b>", "**")
    insight_md = "\n".join(f"- {_md(x)}" for x in insights)
    decision_md = "\n".join(f"- {_md(x)}" for x in decisions)
    year_md = "\n".join(f"| {x['y']} | {x['n']} | {x['total']:,} | {x['avg']:.0f} | {x['median']:,.0f} | {x['share']:.1f}% | {x['gap']:.0f} |" for x in year_stats)
    cat_md = "\n".join(f"| {c} | {v['n']} | {v['median']:,.0f} | {v['mean']:.0f} | {v['share_rate']:.1f}% |" for c, v in sorted(cat_stat.items(), key=lambda x: -x[1]["median"]))
    top_md = "\n".join(f"| {i} | {r['title'].replace('|','｜')[:40]} | {r['read']:,} | {r['date'] or '—'} | {r['cat']} |" for i, r in enumerate(top[:20], 1))
    sy_md = "\n".join(f"| {x['series']} | {x['year']} | {x['n']} | {x['avg']:.0f} | {x['max']:,} |" for x in series_year)
    recent_md = "\n".join(f"| {r['date']} | {r['title'].replace('|','｜')[:36]} | {r['read']:,} | {r['cat']} |" for r in recent[-20:])

    md = f"""# 公众号数据看板

> 数据抓取：{fetched or today} ｜ 文章 {len(rows)} 篇（后台 {len(json.load(open(SRC, encoding="utf-8")))} 条去重）｜ 累计阅读 {total_reads:,}
> 交互版：[数据看板.html](数据看板.html)（浏览器打开，可悬停看数值）

## 核心指标

| 指标 | 数值 | 说明 |
|---|---|---|
{kpi_md}

## 自动洞察

{insight_md}

## 决策清单

{decision_md}

## 月度节奏

![](图表/monthly.png)

## 分类表现

| 类别 | 篇数 | 中位阅读 | 篇均阅读 | 分享率 |
|---|---|---|---|---|
{cat_md}

![](图表/category-median.png)

## 选题象限

![](图表/category-quadrant.png)

## 年度汇总

| 年份 | 篇数 | 总阅读 | 篇均 | 中位 | 分享率 | 篇均间隔(天) |
|---|---|---|---|---|---|---|
{year_md}

> 2024 年前分享率异常偏低，可能是后台统计口径变化，不宜跨年直接对比。

![](图表/share-rate.png)

## TOP 20

| 排名 | 文章 | 阅读量 | 日期 | 类别 |
|---|---|---|---|---|
{top_md}

![](图表/top20.png)

## 年度 × 月份篇均阅读

![](图表/heatmap.png)

## 长尾与头部集中度

![](图表/distribution.png)

![](图表/pareto.png)

## 标题特征与发布星期

![](图表/title-features.png)

![](图表/weekday.png)

## 系列 / IP 与片名

![](图表/series.png)

![](图表/films.png)

## 系列逐年表现

| 系列 | 年份 | 篇数 | 篇均 | 最高 |
|---|---|---|---|---|
{sy_md}

## 阅读 × 分享象限

![](图表/quadrant-engagement.png)

## 正文长度 vs 阅读量

![](图表/length.png)

## 近 90 天文章（最近 20 条）

| 日期 | 文章 | 阅读量 | 类别 |
|---|---|---|---|
{recent_md}

> 口径：阅读/分享为后台累计值；9 条未入档（6 条 tempkey 失效 + 3 条按规则移除）不计入图表。
"""
    md_path = os.path.join(DATA, "数据看板.md")
    open(md_path, "w", encoding="utf-8").write(md)
    print(f"✅ 看板已生成：{out}（{len(html_out)/1024:.0f} KB，{len(rows)} 篇）")
    print(f"✅ Obsidian/GitHub 版：{md_path}")
    print("   洞察：")
    for x in insights:
        print("   -", re.sub("<[^>]+>", "", x))


if __name__ == "__main__":
    main()
