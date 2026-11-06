#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用后台列表刷新 _数据/：阅读量排行榜 + 当日数据快照

用法：
    python3 _skill/scripts/update-data.py

输入：~/Library/Caches/wxmp/articles.json（wxmp-list.py 产物）
      ~/Library/Caches/wxmp/fetched_at.txt（可选，列表抓取时间）
输出：_数据/阅读量排行榜.md
      _数据/YYYY-MM-DD-数据快照.md

口径：
  - 同一篇文章可能同时有短链和 tempkey 长链两条记录，按标题归一化去重，
    阅读量取最大值，避免总量重复计算。
  - 日期优先用后台 create_time；没有则用年份目录文件名反查。
"""
import collections, datetime, html, json, os, re, statistics, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "_数据")
CACHE = os.path.expanduser("~/Library/Caches/wxmp")
SRC = os.path.join(CACHE, "articles.json")
STAMP = os.path.join(CACHE, "fetched_at.txt")


def norm(s):
    s = html.unescape(s or "").replace("\u200b", "")
    return re.sub(r"[\W_]+", "", s, flags=re.UNICODE)


def load_dates():
    m = {}
    for y in sorted(d for d in os.listdir(ROOT) if re.fullmatch(r"\d{4}", d)):
        for f in os.listdir(os.path.join(ROOT, y)):
            if f.endswith(".md"):
                b = f[:-3]
                m.setdefault(norm(b[11:]).replace("amp", ""), b[:10])
    return m


def category(t):
    if re.search(r"路演|主创|到场|导演连线|连线交流|映后", t):
        return "路演/主创"
    if re.search(r"招募|组讯|志愿者|征片|征集", t):
        return "招募/组讯"
    if re.search(r"影展|展映|电影节|戛纳|威尼斯|柏林|FIRST|海影节|短片展", t):
        return "影展/展映"
    if re.search(r"放映|专场|点映|加场|重映|返场|告别场|超前", t):
        return "放映/专场"
    if re.search(r"转载", t):
        return "转载"
    return "原创/回顾"


def main():
    if not os.path.exists(SRC):
        print(f"❌ 缺少 {SRC}，先跑 wxmp-list.py")
        return 1
    arts = json.load(open(SRC, encoding="utf-8"))
    dates = load_dates()
    fetched = ""
    if os.path.exists(STAMP):
        fetched = open(STAMP, encoding="utf-8").read().strip()
    today = datetime.date.today().isoformat()

    # 按归一化标题去重，阅读量取最大值（短链/tempkey 双份只算一次）
    best = {}
    for a in arts:
        k = norm(a["title"]).replace("amp", "")
        rd = a.get("read_num") or 0
        if k not in best or rd > best[k]["read"]:
            best[k] = {
                "read": rd,
                "title": a["title"].strip(),
                "date": a.get("date") or dates.get(k, ""),
                "link": a["link"],
            }
    rows = [(v["read"], v["date"], v["title"], category(v["title"]), v["link"]) for v in best.values()]
    rows.sort(key=lambda x: -x[0])
    total = sum(r[0] for r in rows)
    n_articles = sum(1 for y in os.listdir(ROOT) if re.fullmatch(r"\d{4}", y)
                     for f in os.listdir(os.path.join(ROOT, y)) if f.endswith(".md"))

    os.makedirs(DATA, exist_ok=True)
    lines = [
        "# 阅读量排行榜", "",
        "> 数据来源：公众号后台文章列表（累计阅读，抓取时点快照）。",
        f"> 最近更新：{today}" + (f"（列表抓取于 {fetched}）" if fetched else ""),
        f"> 后台 {len(arts)} 条图文，去重后 {len(rows)} 篇，累计阅读 {total:,}。", "",
        "## 历史 TOP 30", "",
        "| 排名 | 文章 | 阅读量 | 日期 | 类别 |", "| --- | --- | --- | --- | --- |",
    ]
    for i, (rd, d, t, c, _) in enumerate(rows[:30], 1):
        lines.append(f"| {i} | {t.replace('|', '｜')[:34]} | {rd:,} | {d or '—'} | {c} |")

    by_cat = collections.defaultdict(list)
    for rd, _, _, c, _ in rows:
        if rd:
            by_cat[c].append(rd)
    lines += ["", "## 分类统计", "", "| 类别 | 篇数 | 中位阅读 | 最高阅读 |", "| --- | --- | --- | --- |"]
    for c, v in sorted(by_cat.items(), key=lambda x: -statistics.median(x[1])):
        lines.append(f"| {c} | {len(v)} | {int(statistics.median(v)):,} | {max(v):,} |")
    lines += ["", "> 阅读量为抓取时点累计值，非当日增量。日期为「—」表示后台未返回时间且存档未匹配到。"]
    open(os.path.join(DATA, "阅读量排行榜.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")

    snap = [
        "# 公众号数据快照", "", f"> 抓取时间：{fetched or today}",
        f"> 数据来源：mp.weixin.qq.com 后台 appmsgpublish 列表（{len(arts)} 条图文，去重 {len(rows)} 篇）",
        "> 说明：仅含累计阅读/分享量，不含来源分布与完成率", "",
        "| 指标 | 数值 |", "| --- | --- |",
        f"| 后台图文条数 | {len(arts)} |",
        f"| 去重文章数 | {len(rows)} |",
        f"| 存档文章数 | {n_articles} |",
        f"| 累计阅读总量 | {total:,} |",
        f"| 单篇最高 | {rows[0][0]:,}（{rows[0][2][:24]}） |",
        f"| 阅读量中位数 | {int(statistics.median([r[0] for r in rows if r[0]])):,} |",
        f"| 阅读量 > 1000 | {sum(1 for r in rows if r[0] > 1000)} 篇 |", "",
        "## 近三个月文章", "",
        "| 日期 | 文章 | 阅读量 | 类别 |", "| --- | --- | --- | --- |",
    ]
    cutoff = (datetime.date.today() - datetime.timedelta(days=92)).isoformat()
    recent = sorted([r for r in rows if r[1] and r[1] >= cutoff], key=lambda x: x[1])
    for rd, d, t, c, _ in recent:
        snap.append(f"| {d} | {t.replace('|', '｜')[:30]} | {rd:,} | {c} |")
    open(os.path.join(DATA, f"{today}-数据快照.md"), "w", encoding="utf-8").write("\n".join(snap) + "\n")

    print(f"✅ 排行榜与快照已更新：{len(rows)} 篇（后台 {len(arts)} 条），累计阅读 {total:,}")
    print(f"   TOP3: " + " / ".join(f"{r[2][:16]} {r[0]:,}" for r in rows[:3]))
    # 同步重建可视化看板
    import subprocess
    dash = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build-dashboard.py")
    subprocess.run([sys.executable, dash], check=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
