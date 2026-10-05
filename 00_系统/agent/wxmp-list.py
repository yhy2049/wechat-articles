#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""公众号后台 → 文章列表（需扫码）v3

v2 踩坑：解析字段名错了——真实结构是
    publish_page.publish_list[].publish_info   ← 嵌套 JSON 字符串，要二次解析
而不是 publish_page_list。所以一直显示「返回 0 条」。

v3 修正：
  - 正确解析 publish_page.publish_list[].publish_info（二次 json.loads）
  - content_url 是短链 /s/XXXXX 格式，实测不需要 chksm，正文正常
  - 同时试 type=101_1_102_103（后台真实请求）和 type=1（兜底）
  - 翻页遍历，去重排序

用法：python3 00_系统/agent/wxmp-list.py
产物：/tmp/wxmp-articles.json
"""
import json, re, sys, time
from playwright.sync_api import sync_playwright

UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.40")
OUT = "/tmp/wxmp-articles.json"
TYPES = ("101_1_102_103", "1")
PAGE = 20


def ts_date(ts):
    """unix 时间戳 → CST 日期串"""
    if not ts:
        return ""
    return time.strftime("%Y-%m-%d", time.gmtime(ts + 8 * 3600))


def unwrap(v):
    """接口里有两层嵌套 JSON 字符串：publish_page 本身是串，
    里面的 publish_info 也是串。统一解包，调用方不用操心"""
    if isinstance(v, str):
        try:
            return json.loads(v)
        except Exception:
            return {}
    return v or {}


def parse_item(entry):
    """从 publish_list 条目解析出文章信息"""
    raw = entry.get("publish_info")
    if not raw:
        return None
    try:
        info = json.loads(raw) if isinstance(raw, str) else raw
    except Exception:
        return None
    appmsgs = info.get("appmsg_info") or []
    if not appmsgs:
        return None
    a = appmsgs[0]
    link = (a.get("content_url") or "").replace("\\/", "/")
    if not link:
        return None
    pinfo = info.get("publish_info") or {}
    return {
        "mid": a.get("appmsgid") or info.get("msgid"),
        "title": (a.get("title") or "").strip(),
        "link": link,
        "create_time": pinfo.get("create_time") or 0,
        "date": ts_date(pinfo.get("create_time") or 0),
        "read_num": a.get("read_num", 0),
        "share_num": a.get("share_num", 0),
        "item_show_type": a.get("item_show_type", 0),
        "copyright": a.get("copyright", 0),  # 1=原创, 0=转载
        "is_original": a.get("copyright", 0) == 1,  # 便捷判断
    }


def api(pg, token, t, begin):
    """调 appmsgpublish，返回顶层 JSON"""
    u = (f"https://mp.weixin.qq.com/cgi-bin/appmsgpublish"
         f"?token={token}&lang=zh_CN&sub=list&begin={begin}"
         f"&count={PAGE}&type={t}&f=json")
    txt = pg.evaluate(
        "(u) => fetch(u, {credentials:'include',"
        " headers:{'X-Requested-With':'XMLHttpRequest'}})"
        ".then(r => r.text())", u)
    return json.loads(txt)


def main():
    with sync_playwright() as p:
        b = p.chromium.launch(headless=False, args=["--no-sandbox", "--disable-setuid-sandbox"])
        pg = b.new_page(user_agent=UA, locale="zh-CN", viewport={"width": 1280, "height": 800})

        pg.goto("https://mp.weixin.qq.com/", wait_until="domcontentloaded", timeout=60000)
        print("=" * 64)
        print("  请扫码登录公众号后台")
        print("  登录后立刻拉列表（登录态时效短）")
        print("=" * 64, flush=True)

        deadline = time.time() + 300
        while time.time() < deadline:
            u = pg.url
            if "cgi-bin" in u and "login" not in u and "loginpage" not in u:
                break
            pg.wait_for_timeout(2500)
        else:
            pg.screenshot(path="/tmp/wxmp-login-timeout.png")
            print("❌ 扫码超时")
            b.close()
            return 1

        print("✅ 登录成功")
        m = re.search(r"[?&]token=(\d+)", pg.url)
        token = m.group(1) if m else None
        print("   token:", token, flush=True)
        if not token:
            b.close()
            return 1

        all_items, used_type = [], None
        for t in TYPES:
            try:
                d = api(pg, token, t, 0)
            except Exception as e:
                print(f"   type={t}: 请求失败 {str(e)[:60]}")
                continue
            br = d.get("base_resp") or {}
            pp = unwrap(d.get("publish_page"))
            total = pp.get("total_count", 0)
            first = pp.get("publish_list") or []
            print(f"   type={t}: ret={br.get('ret')} total={total} "
                  f"publish_count={pp.get('publish_count')} "
                  f"masssend_count={pp.get('masssend_count')} 首页 {len(first)} 条",
                  flush=True)
            if not first:
                continue

            used_type = t
            for e in first:
                x = parse_item(e)
                if x:
                    all_items.append(x)

            # 翻页
            for begin in range(PAGE, total, PAGE):
                time.sleep(0.4)
                try:
                    d2 = api(pg, token, t, begin)
                except Exception:
                    continue
                batch = unwrap(d2.get("publish_page")).get("publish_list") or []
                if not batch:
                    break
                for e in batch:
                    x = parse_item(e)
                    if x:
                        all_items.append(x)
                print(f"   └─ begin={begin}: +{len(batch)} 条", flush=True)
            break

        b.close()

        seen, uniq = set(), []
        for x in all_items:
            k = x["mid"]
            if k and k not in seen:
                seen.add(k)
                uniq.append(x)
        uniq.sort(key=lambda x: x.get("create_time", 0), reverse=True)

        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(uniq, f, ensure_ascii=False, indent=2)

        print(f"\n✅ type={used_type}，去重后 {len(uniq)} 篇 → {OUT}")
        print(f"\n最新 15 篇：")
        for x in uniq[:15]:
            print(f"  {x['date']}  [show={x['item_show_type']}]  "
                  f"{x['title'][:36]}  (读{x['read_num']})")
            print(f"    {x['link'][:76]}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
