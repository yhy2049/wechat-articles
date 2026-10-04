# -*- coding: utf-8 -*-
"""公众号存档完整性校验：逐篇比对「线上真实 DOM」vs「归档 MD」

用法：
    python3 00_系统/agent/wxmp-verify.py                       # 用 /tmp/wxmp/articles.json
    python3 00_系统/agent/wxmp-verify.py /path/to/articles.json
    python3 00_系统/agent/wxmp-verify.py --since 2026-05-15
    python3 00_系统/agent/wxmp-verify.py --fast                # 不滚动，快但可能漏懒加载图
依赖：playwright chromium。公开分享链接无需登录。

踩坑沉淀（每条都踩过，别改回去）：
  1. 图片轮播 #img_swiper 在 #js_content 之外（Vue 渲染），必须单独取
  2. 别只信 DOM：等渲染时机不稳定，连跑两轮同一篇能在 0/1 张之间跳。原始 HTML 里
     data-src 是服务端渲染出来的，正则扫 swiper_item 窗口才确定
  3. 同一张图有多个 URL 变体（tp=webp / from=appmsg / sz_mmbiz_* vs mmbiz_*），
     必须按 mmbiz 图片 ID（? 之前的路径）去重，按完整 URL 去重会数错
  4. 排除 pic_blank.gif（1x1 空白间距）、video_player_tmpl（视频占位）、二维码
  5. 内容类型看「有无」而非「等于几」：贴图类页面才有 window.item_show_type='8'，
     文章类完全不出这个变量（页面里出现的 0/5 是 JS 常量表或比较语句）
  6. 只算「源 - MD」会假绿：源被频控抽空时差集为空，照样显示 0 缺失。必须双向算，
     并显式检测降级页重试
"""
import argparse, json, os, re, sys, time
from playwright.sync_api import sync_playwright

UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.38")
ARCH = "/Users/haishangyinghuo/Documents/24帧运营库/05_档案/公众号存档"
# articles.json 由公众号后台 appmsgpublish 接口生成（需扫码登录），不入库
DEFAULT_ARTS = os.environ.get("WXMP_ARTICLES", "")
NOISE = ("pic_blank.gif", "video_player_tmpl", "blank.gif", "qrcode", "wx_qrcode")
# 频控/风控时微信返降级页：标题还在、正文被抽空，极易漏判
BLOCKED = ("环境异常", "去验证", "安全验证", "请在微信客户端打开")
BAD_CHARS = set('「」『』【】《》〈〉（）()[]·—–―…、，。！!？?：:;；·,.|\\/<>?:*"\'‘’“”~`#@$%^&=_+-｜／＼－　')
TYPE_PAT = r"window\.(?:real_)?item_show_type\s*=\s*['\"]?(\d+)['\"]?"
TYPE_NAME = {"8": "贴图", "0": "文章"}

# 只认 #js_content 内 + img_swiper 的 swiper_item，不碰作者头像等页脚元素
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


def img_id(url):
    """按 mmbiz 图片 ID 归一（? 之前的路径），同一张图的压缩变体撞到一起"""
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


def fetch(pg, url, fast):
    """返回 (html, err)。err 非空 = 降级页/失败，调用方退避重试"""
    pg.goto(url, wait_until="domcontentloaded", timeout=90000)
    try:
        pg.wait_for_selector("#js_content", timeout=20000)
    except Exception:
        pass
    if not fast:
        for _ in range(4):
            pg.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(0.4)
        time.sleep(1.3)
    h = pg.content()
    bad = [k for k in BLOCKED if k in h]
    if bad:
        return None, f"降级页({bad[0]})"
    if "js_content" not in h:
        return None, "正文缺失"
    return h, ""


def source_ids(pg, h):
    """DOM 查询 + 原始 HTML 正则兜底，取并集"""
    s = set()
    for u in pg.evaluate(JS):
        i = img_id(u)
        if i:
            s.add(i)
    for m in re.finditer(r"swiper_item", h):
        seg = h[max(0, m.start() - 500): m.start() + 500]
        for u in re.findall(r'data-src="(https?://[^"]+)"', seg):
            i = img_id(u)
            if i:
                s.add(i)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("articles", nargs="?", default=DEFAULT_ARTS)
    ap.add_argument("--since", default="2026-05-15")
    ap.add_argument("--fast", action="store_true")
    a = ap.parse_args()
    if not a.articles:
        print("未指定 articles.json（用参数传入，或设环境变量 WXMP_ARTICLES）")
        return 1
    arts = [x for x in json.load(open(a.articles)) if x.get("date_str", "") > a.since]
    if not arts:
        print(f"无 >{a.since} 的文章，退出")
        return 0
    rows, warn = [], []
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=["--no-sandbox"])
        pg = b.new_page(user_agent=UA, viewport={"width": 430, "height": 950}, locale="zh-CN")
        for x in arts:
            h = err = None
            for attempt in range(1, 4):
                h, err = fetch(pg, x["url"], a.fast)
                if not err:
                    break
                if attempt < 3:
                    print(f"  ↻ {x['date_str']} {err}，{attempt}/3 退避重试")
                    time.sleep(6 * attempt)
            if h is None:
                src, typ = set(), None
                warn.append(f"{x['date_str']} 抓取失败：{err}")
            else:
                m = re.search(TYPE_PAT, h)
                typ = m.group(1) if m else "0"   # 无此变量 = 文章
                src = source_ids(pg, h)
            fp = find_md(x["date_str"], x["title"])
            mids = md_ids(fp) if fp else set()
            # 双向：只算 src - mids 会在源被抽空时假绿
            miss, extra = src - mids, mids - src
            if not fp:
                warn.append(f"{x['date_str']} 未找到归档文件：{x['title'][:24]}")
            if not src and mids:
                warn.append(f"{x['date_str']} 源端 0 图但 MD 有 {len(mids)} 张 → 抓取疑不可靠")
            rows.append((x["date_str"], TYPE_NAME.get(typ, str(typ)), len(src),
                         len(mids), len(miss), len(extra), bool(fp), x["title"][:28]))
        pg.close()
        b.close()
    print(f"\n{'日期':11s}{'类型':5s}{'源':>4s}{'MD':>4s}{'源缺':>4s}{'MD多':>5s}{'文件':>5s}标题")
    for d, k, s, m_, mi, ex, fp, t in rows:
        flag = "缺图" if mi else ("无文件" if not fp else "OK")
        print(f"{d:11s}{k:5s}{s:4d}{m_:4d}{mi:4d}{ex:5d}{flag:>5s}{t}")
    bad = [r for r in rows if r[4] or not r[6]]
    print(f"\n合计 {len(rows)} 篇 | 源 {sum(r[2] for r in rows)} 张 | "
          f"MD {sum(r[3] for r in rows)} 张 | 源端漏收 {sum(r[4] for r in rows)} 张")
    if bad:
        print(f"❌ {len(bad)} 篇有问题")
    elif warn:
        print(f"⚠️  图量齐全，但有 {len(warn)} 条警告需人工看：")
        for w in warn:
            print("   - " + w)
    else:
        print("✅ 全部齐全")
    return 1 if (bad or warn) else 0


if __name__ == "__main__":
    sys.exit(main())
