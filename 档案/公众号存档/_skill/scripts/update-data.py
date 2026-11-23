#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""刷新 _数据/数据看板.md（唯一数据出口）

用法：python3 _skill/scripts/update-data.py
输入：~/Library/Caches/wxmp/articles.json（wxmp-list.py 产物）
输出：_数据/数据看板.md + _数据/图表/*.png
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.expanduser("~/Library/Caches/wxmp/articles.json")


def main():
    if not os.path.exists(SRC):
        print(f"❌ 缺少 {SRC}，先跑 wxmp-list.py")
        return 1
    arts = json.load(open(SRC, encoding="utf-8"))
    print(f"后台 {len(arts)} 条图文 → 生成看板…", flush=True)
    import subprocess
    dash = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build-dashboard.py")
    return subprocess.run([sys.executable, dash], check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
