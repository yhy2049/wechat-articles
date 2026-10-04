#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""公众号文章页公开抓取诊断

9 月还能抓的公开链接，现在还能不能抓？
测 URL 变体 × UA × 等待策略，找出确切失效点。

用法：python3 00_系统/agent/wxmp-probe.py
"""
import asyncio, re
from playwright.async_api import async_playwright

URLS = [
    ("带chksm", "http://mp.weixin.qq.com/s?__biz=Mzk0MDMyNzExMw==&mid=2247484875&idx=1"
                "&sn=623adf00478ba20f9d55efa441493a72"
                "&chksm=c2e22c6df595a57bfbd2cfa9f9cf1f68ef49418dd2c0d53ff7998336f3441bab6696646c0545&scene=21"),
    ("不带chksm", "https://mp.weixin.qq.com/s?__biz=Mzk0MDMyNzExMw==&mid=2247484875&idx=1"
                  "&sn=623adf00478ba20f9d55efa441493a72&scene=21"),
    ("另一篇", "https://mp.weixin.qq.com/s?__biz=Mzk0MDMyNzExMw==&mid=2247483664&idx=1"
               "&sn=d1f4581443381c6392d7dd8477836090&scene=21"),
]
UA_IOS = ("Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
          "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.40")
UA_DESK = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
           "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
BLOCKED_KW = ("请在微信客户端打开", "环境异常", "参数错误", "该公众号不存在",
              "页面不存在", "登录超时", "请重新登录", "当前环境异常")

JS_LEN = ("() => { const e = document.getElementById('js_content');"
          " return e ? e.innerText.trim().length : -1; }")


async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        print(f"{'结果':4s} {'URL变体':10s} | {'UA':10s} | {'status':>6s} {'html':>8s} "
              f"{'js_content':>10s} | 拦截关键词")
        print("-" * 92)
        good = 0
        for name, url in URLS:
            for ua_name, ua in (("iPhone微信", UA_IOS), ("桌面Chrome", UA_DESK)):
                ctx = await br.new_context(user_agent=ua, locale="zh-CN")
                pg = await ctx.new_page()
                try:
                    r = await pg.goto(url, wait_until="domcontentloaded", timeout=30000)
                    await asyncio.sleep(3)
                    html = await pg.content()
                    n = await pg.evaluate(JS_LEN)
                    hit = next((k for k in BLOCKED_KW if k in html), "")
                    t = re.search(r"<title[^>]*>(.*?)</title>", html, re.S)
                    title = re.sub(r"\s+", " ", t.group(1).strip())[:40] if t else ""
                    ok = (n or 0) > 50
                    good += ok
                    mark = "✅" if ok else "❌"
                    print(f"{mark:4s} {name:10s} | {ua_name:10s} | {r.status:>6} "
                          f"{len(html):>8,} {n:>10} | {hit or '无'}")
                    print(f"      title: {title!r}")
                    if not ok:
                        print(f"      html[:210]: {re.sub(chr(10) + '+', ' ', html[:210])!r}")
                except Exception as e:
                    print(f"❌ {name:10s} | {ua_name:10s} | FAIL {str(e)[:86]}")
                await ctx.close()
        print("-" * 92)
        print(f"成功 {good}/6 组")
        await br.close()


asyncio.run(main())
