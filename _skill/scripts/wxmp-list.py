#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""公众号后台 → 全量文章列表（持久化登录）

用法：
    python3 _skill/scripts/wxmp-list.py            # 已登录直接拉，未登录弹窗扫码
    python3 _skill/scripts/wxmp-list.py --force-ui # 强制弹出浏览器扫码

关键前提（实测，别再改回去）：
  1. 真实结构是 publish_page.publish_list[].publish_info，两层嵌套 JSON 字符串，
     需要二次 json.loads；不是 publish_page_list。
  2. content_url 是短链 /s/XXXXX，抓正文不需要 chksm。
  3. 一次推送可能含多条图文（appmsg_info 是数组）。只取 appmsgs[0] 会漏文章：
     2026-10 实测只取第一条得 329 篇，遍历全部得 333 篇。
  4. 翻页用 begin 偏移、count=20；偶发空页要重试，不能直接 break。
  5. 登录态保存在 ~/.wechat-automation/browser-profile，headless 复用可免扫码。

产物：~/Library/Caches/wxmp/articles.json
"""
import argparse, json, os, re, sys, time
from playwright.sync_api import sync_playwright

PROFILE = os.environ.get("WXMP_PROFILE", os.path.expanduser("~/.wechat-automation/browser-profile"))
OUTDIR = os.environ.get("WXMP_HOME") or (
    os.path.expanduser("~/Library/Caches/wxmp") if sys.platform == "darwin"
    else os.path.expanduser("~/.cache/wxmp"))
OUT = os.path.join(OUTDIR, "articles.json")
UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.40")
TYPES = ("101_1_102_103", "1")
PAGE = 20


def ts_date(ts):
    if not ts:
        return ""
    return time.strftime("%Y-%m-%d", time.gmtime(ts + 8 * 3600))


def unwrap(v):
    if isinstance(v, str):
        try:
            return json.loads(v)
        except Exception:
            return {}
    return v or {}


def parse_entry(entry):
    """一次推送可能有多条图文，全部展开"""
    raw = entry.get("publish_info")
    if not raw:
        return []
    try:
        info = json.loads(raw) if isinstance(raw, str) else raw
    except Exception:
        return []
    appmsgs = info.get("appmsg_info") or []
    pinfo = info.get("publish_info") or {}
    ts = pinfo.get("create_time") or 0
    out = []
    for a in appmsgs:
        link = (a.get("content_url") or "").replace("\\/", "/")
        if not link:
            continue
        out.append({
            "mid": a.get("appmsgid") or info.get("msgid"),
            "title": (a.get("title") or "").strip(),
            "link": link,
            "create_time": ts,
            "date": ts_date(ts),
            "read_num": a.get("read_num", 0),
            "share_num": a.get("share_num", 0),
            "item_show_type": a.get("item_show_type", 0),
            "copyright": a.get("copyright", 0),
            "is_original": a.get("copyright", 0) == 1,
        })
    return out


def api(pg, token, t, begin):
    u = (f"https://mp.weixin.qq.com/cgi-bin/appmsgpublish"
         f"?token={token}&lang=zh_CN&sub=list&begin={begin}"
         f"&count={PAGE}&type={t}&f=json")
    txt = pg.evaluate(
        "(u) => fetch(u, {credentials:'include',"
        " headers:{'X-Requested-With':'XMLHttpRequest'}})"
        ".then(r => r.text())", u)
    return json.loads(txt)


def get_token(pg, wait_sec):
    deadline = time.time() + wait_sec
    while time.time() < deadline:
        m = re.search(r"[?&]token=(\d+)", pg.url)
        if m and "login" not in pg.url:
            return m.group(1)
        pg.wait_for_timeout(2000)
    return None


def pull(pg, token):
    items, used = [], None
    for t in TYPES:
        try:
            d = api(pg, token, t, 0)
        except Exception as e:
            print(f"   type={t}: 请求失败 {str(e)[:60]}", flush=True)
            continue
        pp = unwrap(d.get("publish_page"))
        total = pp.get("total_count", 0)
        first = pp.get("publish_list") or []
        print(f"   type={t}: total={total} 首页 {len(first)} 条推送", flush=True)
        if not first:
            continue
        used = t
        for e in first:
            items.extend(parse_entry(e))
        begin, misses = PAGE, 0
        while begin < total:
            time.sleep(0.35)
            try:
                batch = unwrap(api(pg, token, t, begin).get("publish_page")).get("publish_list") or []
            except Exception:
                batch = []
            if not batch:
                misses += 1
                if misses > 2:
                    print(f"   └─ begin={begin}: 连续空页，停止", flush=True)
                    break
                time.sleep(1.5)
                continue
            misses = 0
            for e in batch:
                items.extend(parse_entry(e))
            print(f"   └─ begin={begin}: +{len(batch)} 条推送", flush=True)
            begin += PAGE
        break
    return items, used


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force-ui", action="store_true", help="强制弹出浏览器扫码")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    os.makedirs(PROFILE, exist_ok=True)

    with sync_playwright() as p:
        headless = not a.force_ui
        ctx = p.chromium.launch_persistent_context(
            PROFILE, headless=headless, user_agent=UA, locale="zh-CN",
            viewport={"width": 1280, "height": 800}, args=["--no-sandbox"])
        pg = ctx.new_page()
        pg.goto("https://mp.weixin.qq.com/", wait_until="domcontentloaded", timeout=60000)
        token = get_token(pg, 12 if headless else 0)
        if not token and headless:
            print("   登录态已失效，改用可见窗口扫码…", flush=True)
            ctx.close()
            ctx = p.chromium.launch_persistent_context(
                PROFILE, headless=False, user_agent=UA, locale="zh-CN",
                viewport={"width": 1280, "height": 800}, args=["--no-sandbox"])
            pg = ctx.new_page()
            pg.goto("https://mp.weixin.qq.com/", wait_until="domcontentloaded", timeout=60000)
            print("=" * 60)
            print("  请在弹出的窗口里扫码登录公众号后台（5 分钟内）")
            print("=" * 60, flush=True)
            token = get_token(pg, 300)
        if not token:
            pg.screenshot(path=os.path.join(OUTDIR, "login-timeout.png"))
            print("❌ 未取到登录态", flush=True)
            ctx.close()
            return 1
        print(f"✅ 已登录 token={token}", flush=True)

        items, used = pull(pg, token)
        ctx.close()

    seen, uniq = set(), []
    for x in items:
        if x["link"] not in seen:
            seen.add(x["link"])
            uniq.append(x)
    uniq.sort(key=lambda x: (x.get("create_time") or 0, x["date"]), reverse=True)
    json.dump(uniq, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    with open(os.path.join(os.path.dirname(a.out), "fetched_at.txt"), "w", encoding="utf-8") as fh:
        fh.write(time.strftime("%Y-%m-%d %H:%M"))

    print(f"\n✅ type={used}，展开多图文后共 {len(uniq)} 篇 → {a.out}")
    for x in uniq[:12]:
        print(f"  {x['date']}  [show={x['item_show_type']}]  {x['title'][:34]}  (读{x['read_num']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
