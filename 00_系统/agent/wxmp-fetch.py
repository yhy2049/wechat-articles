#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""公众号文章抓取 → Markdown 归档

用法：
    python3 00_系统/agent/wxmp-fetch.py URL
    python3 00_系统/agent/wxmp-fetch.py --date 2026-09-20 URL [URL...]

关键前提（2026-10 实测，别再改回去）：
  1. 后台 appmsgpublish 返回的是短链 /s/XXXXX 格式，不需要 chksm。
     之前误以为「必须带 chksm」是因为只测了存档里的 __biz 长链格式——
     那批链接 11 个里 9 个缺 chksm，9 月能抓到纯属微信当时不校验。
     短链实测 4.5MB 完整页面，js_content 正常，零降级。
  2. 正文抓取走公开链接，本身不需要登录。需要登录的只有「拿列表」。
  3. #img_swiper 图片轮播在 #js_content 之外（Vue 渲染），必须单独取。
  4. 同一张图有多个 URL 变体（sz_mmbiz_ / mmbiz_ / tp=webp / from=appmsg），
     按 mmbiz 图片 ID（? 之前的路径）去重，按完整 URL 去重会数错。
  5. 排除 pic_blank.gif（1x1 空白间距）、video_player_tmpl（视频占位）、二维码。
  6. 内容类型看「有无」而非「等于几」：贴图类才有 window.item_show_type='8'，
     文章类完全不出这个变量（页面里的 0/5 是 JS 常量表或比较语句）。
  7. 短链页面 document.title 为空，标题必须从 og:title meta 取。
"""
import argparse, os, re, sys, time
from playwright.sync_api import sync_playwright

ARCH = "/Users/haishangyinghuo/Documents/24帧运营库/05_档案/公众号存档"
UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.40")
BLOCKED = ("环境异常", "请在微信客户端打开", "参数错误", "去验证", "安全验证")
BAD_CHARS = set('「」『』【】《》〈〉（）()[]·—–―…、，。！!？?：:;；·,.|\\/<>?:*"\'‘’“”~`#@$%^&=_+-｜／＼－　')

# 取标题 / 发布时间 / 内容类型。时间有三处可能藏身，逐一试
JS_META = r"""() => {
  const h = document.documentElement.outerHTML;
  const title = ((document.getElementById('activity-name') || {}).innerText ||
                 (document.querySelector('meta[property="og:title"]') || {}).content ||
                 document.title || '').trim();
  let date = '';
  let m = h.match(/var\s+create_time\s*=\s*['"]([^'"]+)['"]/);
  if (m) date = m[1];
  if (/^\d{10}$/.test(date)) date = new Date(parseInt(date) * 1000).toISOString().slice(0, 10);
  if (!date) {
    m = h.match(/var\s+ct\s*=\s*['"]?(\d{10})['"]?/);
    if (m) date = new Date(parseInt(m[1]) * 1000).toISOString().slice(0, 10);
  }
  if (!date) {
    const el = document.querySelector('.rich_media_meta_text, #publish_time, .weui-msg');
    if (el) date = el.innerText.trim().slice(0, 12);
  }
  const show = h.match(/window\.(?:real_)?item_show_type\s*=\s*['"]?(\d+)['"]?/);
  return { title: title, date: date, type: show ? show[1] : '' };
}"""

# DOM → Markdown。标题降级不超出 6 级，轮播图追加在末尾
JS_TO_MD = r"""() => {
  const root = document.getElementById('js_content');
  if (!root) return '';
  const NOISE = ['pic_blank.gif', 'video_player_tmpl', 'blank.gif', 'qrcode', 'wx_qrcode'];
  const skip = u => !u || u.indexOf('http') !== 0 || NOISE.some(n => u.indexOf(n) >= 0);
  const imgTag = u => '![](' + u.split('#')[0] + ')';
  const clean = s => (s || '').replace(/\s+/g, ' ').trim();
  const out = [];

  function inline(el) {
    let s = '';
    for (const n of el.childNodes) {
      if (n.nodeType === 3) { s += n.textContent; continue; }
      if (n.nodeType !== 1) continue;
      const tag = n.tagName.toLowerCase();
      if (tag === 'br') { s += '\n'; continue; }
      if (tag === 'img') {
        const u = n.getAttribute('data-src') || n.getAttribute('src') || '';
        if (!skip(u)) s += imgTag(u) + '\n';
        continue;
      }
      if (tag === 'a') {
        const href = n.getAttribute('href') || '';
        const t = clean(inline(n));
        if (!href || href === '#') { s += t; continue; }
        s += t ? '[' + t + '](' + href + ')' : '';
        continue;
      }
      if (tag === 'strong' || tag === 'b') { s += '**' + inline(n) + '**'; continue; }
      if (tag === 'em' || tag === 'i') { s += '*' + inline(n) + '*'; continue; }
      if (tag === 'code') { s += '`' + n.textContent + '`'; continue; }
      s += inline(n);
    }
    return s;
  }

  function block(el) {
    for (const n of el.childNodes) {
      if (n.nodeType === 3) {
        const t = clean(n.textContent);
        if (t) out.push(t);
        continue;
      }
      if (n.nodeType !== 1) continue;
      const tag = n.tagName.toLowerCase();
      if (tag === 'script' || tag === 'style' || tag === 'svg') continue;
      if (tag === 'img') {
        const u = n.getAttribute('data-src') || n.getAttribute('src') || '';
        if (!skip(u)) out.push(imgTag(u));
        continue;
      }
      if (/^h[1-6]$/.test(tag)) {
        const t = clean(inline(n));
        if (t) out.push('#'.repeat(+tag[1]) + ' ' + t);
        continue;
      }
      if (tag === 'p' || tag === 'blockquote') {
        const t = clean(inline(n));
        if (t) out.push((tag === 'blockquote' ? '> ' : '') + t);
        continue;
      }
      if (tag === 'ul' || tag === 'ol') {
        for (const li of n.querySelectorAll(':scope > li')) {
          const t = clean(inline(li));
          if (t) out.push('- ' + t);
        }
        continue;
      }
      block(n);   // section / div / span 继续下钻
    }
  }

  block(root);
  // 图片轮播 #img_swiper 在 #js_content 之外，单独取
  document.querySelectorAll('[class*="swiper_item"][data-src]').forEach(d => {
    const u = d.getAttribute('data-src');
    if (!skip(u)) out.push(imgTag(u));
  });
  return out.join('\n\n');
}"""


def fetch(pg, url):
    """返回 (html, err)。err 非空 = 降级页/失败，调用方退避重试"""
    pg.goto(url, wait_until="domcontentloaded", timeout=90000)
    try:
        pg.wait_for_selector("#js_content", timeout=20000)
    except Exception:
        pass
    for _ in range(4):          # 滚动触发懒加载
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


def safe_title(t):
    return "".join(c for c in re.sub(r"\s+", "", t or "") if c not in BAD_CHARS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("urls", nargs="+")
    ap.add_argument("--date", help="YYYY-MM-DD，页面提取不到时间时用")
    a = ap.parse_args()

    ok = 0
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=["--no-sandbox"])
        pg = b.new_page(user_agent=UA, viewport={"width": 430, "height": 950}, locale="zh-CN")

        for url in a.urls:
            html = err = None
            for attempt in range(1, 4):
                html, err = fetch(pg, url)
                if not err:
                    break
                print(f"  ↻ {err}，{attempt}/3 退避重试")
                time.sleep(6 * attempt)

            if html is None:
                print(f"❌ 失败 {url[:70]}\n   {err}")
                continue

            meta = pg.evaluate(JS_META)
            title = meta.get("title", "")
            date = a.date or re.sub(r"[^0-9-]", "", meta.get("date", "") or "")
            if not re.match(r"\d{4}-\d{2}-\d{2}", date):
                date = date[:10] if len(date) >= 10 else ""

            md_body = pg.evaluate(JS_TO_MD)
            n_img = len(re.findall(r"!\[\]\(https?://", md_body))

            if not title:
                print(f"❌ 无标题 {url[:64]}")
                continue
            if not date:
                print(f"❌ 无日期 {title[:32]}（用 --date YYYY-MM-DD 指定）")
                continue

            outdir = os.path.join(ARCH, date[:4])
            os.makedirs(outdir, exist_ok=True)
            fp = os.path.join(outdir, f"{date}-{safe_title(title)}.md")
            if os.path.exists(fp):
                print(f"  ⚠ 已存在，改名追加序号：{os.path.basename(fp)}")
                fp = fp.replace(".md", f"-{int(time.time()) % 100000}.md")

            kind = "贴图" if meta.get("type") == "8" else "文章"
            with open(fp, "w", encoding="utf-8") as f:
                f.write(f"#  {title}\n\n{md_body.strip()}\n")

            print(f"✅ {date} [{kind}] {title[:34]}\n   {len(md_body):,} 字 / {n_img} 图\n"
                  f"   → {fp}")
            ok += 1

        pg.close()
        b.close()

    print(f"\n成功 {ok}/{len(a.urls)} 篇")
    return 0 if ok == len(a.urls) else 1


if __name__ == "__main__":
    sys.exit(main())
