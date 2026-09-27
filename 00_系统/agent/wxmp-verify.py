# -*- coding: utf-8 -*-
"""公众号存档完整性校验：逐篇比对「线上真实 DOM」vs「归档 MD」

用法：
    python3 00_系统/agent/wxmp-verify.py                       # 用 /tmp/wxmp/articles.json
    python3 00_系统/agent/wxmp-verify.py /path/to/articles.json
    python3 00_系统/agent/wxmp-verify.py --since 2026-05-15
    python3 00_系统/agent/wxmp-verify.py --fast                # 不滚动，快但可能漏懒加载图
依赖：playwright chromium。公开分享链接无需登录。

踩坑沉淀（每次别忘）：
  1. 图片轮播 #img_swiper 在 #js_content 之外（Vue 渲染），必须单独取
     [class*=swiper_item][data-src]；lxml 会截断该树，用真实 DOM 或原始 HTML 正则
  2. 同一张图有多个 URL 变体（tp=webp / from=appmsg / sz_mmbiz_* vs mmbiz_*），
     必须按 mmbiz 图片 ID（? 之前的路径）去重，按完整 URL 去重会数错
  3. 排除 pic_blank.gif（1x1 空白间距）、video_player_tmpl（视频占位图）、二维码图
  4. 内容类型看「有无」而非「等于几」：贴图类页面才有
     `window.item_show_type = '8'`，文章类**完全不出这个变量**（页面里的 0 是
     JS 常量表或比较语句，不是文章实际值）。所以：有 = 贴图，无 = 文章。
"""
import argparse, json, os, re, sys, time
from playwright.sync_api import sync_playwright

UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.38")
ARCH = "/Users/haishangyinghuo/Documents/OH-WorkSpace/24帧运营库/05_档案/公众号存档"
DEFAULT_ARTS = "/tmp/wxmp/articles.json"
# 干扰项：不是正文内容图
NOISE = ("pic_blank.gif", "video_player_tmpl", "blank.gif", "qrcode", "wx_qrcode")
# 频控/风控时微信会返降级页（标题仍是文章标题，但正文被抽掉）
BLOCKED = ("环境异常", "去验证", "安全验证", "请在微信客户端打开")
BAD_CHARS = set('「」『』【】《》〈〉（）()[]·—–―…、，。！!？?：:;；·,.|\\/<>?:*"\'‘’“”~`#@$%^&=_+-｜／＼－　')

# 页面内取数：只认 #js_content 内 + img_swiper 的 swiper_item，不碰作者头像等页脚元素
JS = """() => {
  const r = [];
  const jc = document.getElementById('js_content');
  if (jc) {
    jc.querySelectorAll('img').forEach(im => {
      const u = im.getAttribute('data-src') || im.getAttribute('src') || '';
      if (u.indexOf('http') === 0) r.push(u.split('#')[0]);
    });
    jc.querySelectorAll('[data-src]').forEach(d => {
      if (d.tagName === 'IMG') return;
      const u = d.getAttribute('data-src');
      if (u.indexOf('http') === 0) r.push(u.split('#')[0]);
    });
  }
  document.querySelectorAll('[class*="swiper_item"][data-src]').forEach(d => {
    const u = d.getAttribute('data-src');
    if (u.indexOf('http') === 0) r.push(u.split('#')[0]);
  });
  return r;
}"""
# 贴图类页面才有 window.item_show_type = '8'；文章类完全不出这个变量
TYPE_PAT = r"window\.(?:real_)?item_show_type\s*=\s*['\"]?(\d+)['\"]?"
TYPE_NAME = {"8": "贴图", "0": "文章"}


def img_id(url):
    """按 mmbiz 图片 ID 归一（? 之前的路径），同一张图的压缩变体会撞到一起"""
    u = (url or "").split("#")[0]
    if any(n in u for n in NOISE):
        return None
    m = re.match(r"(https?://[^/]+/(?:sz_)?mmbiz_[a-z]+/[^/?]+)", u)
    return m.group(1) if m else None


def safe_title(t):
    return "".join(c for c in re.sub(r"\s+", "", t or "") if c not in BAD_CHARS)


def find_md(date_str, title):
    p = os.path.join(ARCH, date_str[:4], f"{date_str}-{safe_title(title)}.md")
    return p if os.path.exists(p) else None


def md_ids(path):
    return {i for i in (img_id(u) for u in re.findall(r"!\[[^\]]*\]\((https?://[^)]+)\)",
                                                        open(path, encoding="utf-8").read())) if i}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("articles", nargs="?", default=DEFAULT_ARTS)
    ap.add_argument("--since", default="2026-05-15")
    ap.add_argument("--fast", action="store_true")
    a = ap.parse_args()
    arts = [x for x in json.load(open(a.articles)) if x.get("date_str", "") > a.since]
    if not arts:
        print(f"无 >{a.since} 的文章，退出"); return
    rows, tot_src, tot_md = [], 0, 0
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=["--no-sandbox"])
        for x in arts:
            pg = b.new_page(user_agent=UA, viewport={"width": 430, "height": 950}, locale="zh-CN")
            src, typ = set(), None
            try:
                pg.goto(x["url"], wait_until="domcontentloaded", timeout=90000)
                try:
                    pg.wait_for_selector("#js_content", timeout=20000)
                except Exception:
                    pass
                if not a.fast:
                    for _ in range(4):
                        pg.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        time.sleep(0.4)
                    time.sleep(1.3)
                h = pg.content()
                m = re.search(TYPE_PAT, h)
                typ = m.group(1) if m else "0"   # 无此变量 = 文章
                for u in pg.evaluate(JS):
                    i = img_id(u)
                    if i:
                        src.add(i)
                # img_swiper 是 Vue 渲染，等 DOM 不稳定（同一篇不同轮次可能 0 或 1）；
                # 原始 HTML 里 data-src 一定有，直接扫 swiper_item 附近的窗口更可靠
                for m2 in re.finditer(r"swiper_item", h):
                    seg = h[max(0, m2.start() - 500): m2.start() + 500]
                    for u in re.findall(r'data-src="(https?://[^"]+)"', seg):
                        i = img_id(u)
                        if i:
                            src.add(i)
            except Exception as e:
                src = {None}
                print(f"  ! 抓取失败 {x['date_str']}: {str(e)[:70]}")
            pg.close()
            fp = find_md(x["date_str"], x["title"])
            mids = md_ids(fp) if fp else set()
            miss = src - mids
            rows.append((x["date_str"], TYPE_NAME.get(typ, typ),
                         len(src), len(mids), len(miss), bool(fp), x["title"][:30]))
            tot_src += len(src); tot_md += len(mids)
        b.close()
    print(f"\n{'日期':11s}{'类型':5s}{'源':>4s}{'MD':>4s}{'缺':>4s}  {'文件':5s}标题")
    for d, k, s, m, mi, fp, t in rows:
        flag = "MISS" if mi else ("无文件" if not fp else "OK")
        print(f"{d:11s}{k:5s}{s:4d}{m:4d}{mi:4d}  {flag:5s}{t}")
    bad = [r for r in rows if r[4] or not r[5]]
    print(f"\n合计 {len(rows)} 篇 | 源 {tot_src} 张 | MD {tot_md} 张 | "
          f"缺失 {sum(r[4] for r in rows)} 张 | {'全部齐全' if not bad else str(len(bad)) + ' 篇有问题'}")


if __name__ == "__main__":
    main()
