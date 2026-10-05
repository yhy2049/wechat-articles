#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""公众号存档完整性审核：对比后台文章列表 vs 本地存档

用法：
    python3 00_系统/agent/wxmp-audit.py                    # 用 /tmp/wxmp-articles.json
    python3 00_系统/agent/wxmp-audit.py /path/to/articles.json
    python3 00_系统/agent/wxmp-audit.py --verbose           # 显示缺失/重复明细

审核项：
    1. 数量对比：后台总数 vs 存档总数（年份目录 + .github-pages）
    2. 覆盖范围：最早/最晚日期对比
    3. 重复检测：年份目录 vs .github-pages 的同名文章
    4. 缺失检测：后台有但存档没有的文章（按标题关键词匹配）
    5. 过期检测：tempkey URL 已过期的文章（无法补抓）
    6. 移除检测：读取 _meta/removals.md，报告已移除的文章

依赖：Python 3.6+，无外部库
"""
import json, os, re, sys, argparse
from pathlib import Path
from collections import defaultdict

ARCH = "/Users/haishangyinghuo/Documents/24帧运营库/05_档案/公众号存档"
DEFAULT_ARTS = os.environ.get("WXMP_ARTICLES", "/tmp/wxmp-articles.json")

def safe_title(t):
    """清理标题中的特殊字符，用于文件名匹配"""
    return re.sub(r'[^\w\u4e00-\u9fff]+', '', t or '')

def find_archive_files():
    """扫描存档，返回 {title_keyword: [(path, source)]}"""
    files = defaultdict(list)
    
    # 年份目录
    year_dirs = [d for d in Path(ARCH).iterdir() if d.is_dir() and d.name.isdigit()]
    for d in year_dirs:
        for f in d.glob("*.md"):
            m = re.match(r'(\d{4}-\d{2}-\d{2})-(.+)\.md', f.name)
            if m:
                date, title = m.groups()
                # 提取标题关键词（去掉常见前缀）
                kw = re.sub(r'^(「[^」]+」|放映本周[日六]|嘉宾映后|联名|回顾|成都路演)', '', title)
                files[kw].append((str(f), f"年份目录/{d.name}"))
    
    # .github-pages
    gh = Path(ARCH) / ".github-pages" / "articles"
    if gh.exists():
        for f in gh.rglob("*"):
            if f.suffix in (".md", ".html"):
                m = re.match(r'(\d{4}-\d{2}-\d{2})-(.+)\.(md|html)$', f.name)
                if m:
                    date, title, _ = m.groups()
                    kw = re.sub(r'^(「[^」]+」|放映本周[日六]|嘉宾映后|联名|回顾|成都路演)', '', title)
                    files[kw].append((str(f), ".github-pages"))
    
    return files

def check_duplicates(files):
    """找出在两个位置都存在的文章"""
    dupes = []
    for kw, paths in files.items():
        sources = set(p[1] for p in paths)
        if len(sources) > 1:
            dupes.append((kw, paths))
    return dupes

def load_removals():
    """读取 _meta/removals.md，返回移除记录"""
    removals_file = Path(ARCH) / "_meta" / "removals.md"
    removals = []
    
    if not removals_file.exists():
        return removals
    
    with open(removals_file) as f:
        lines = f.readlines()
    
    # 解析表格行
    for line in lines:
        line = line.strip()
        if line.startswith('|') and not line.startswith('|---') and not line.startswith('| 日期'):
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 5:
                date, title, reason, _ = parts[1], parts[2], parts[3], parts[4]
                if date and title:
                    removals.append({
                        'date': date,
                        'title': title,
                        'reason': reason
                    })
    
    return removals

def check_missing(articles, files):
    """找出后台有但存档没有的文章"""
    missing = []
    for a in articles:
        title = a.get('title', '')
        url = a.get('content_url', '') or a.get('content_url_no_chksm', '')
        
        # 检查 URL 是否有效（tempkey 过期）
        if 'tempkey=' in url:
            missing.append({
                'title': title,
                'url': url,
                'reason': 'tempkey 过期',
                'recoverable': False
            })
            continue
        
        # 提取标题关键词
        kw = safe_title(title)
        # 去掉常见前缀
        kw = re.sub(r'^(「[^」]+」|放映本周[日六]|嘉宾映后|联名|回顾|成都路演)', '', kw)
        
        # 检查存档里是否有
        found = False
        for fkw, paths in files.items():
            if kw and (kw in fkw or fkw in kw):
                found = True
                break
        
        if not found:
            missing.append({
                'title': title,
                'url': url,
                'reason': '存档未找到',
                'recoverable': True
            })
    
    return missing

def main():
    parser = argparse.ArgumentParser(description="公众号存档完整性审核")
    parser.add_argument("articles_json", nargs="?", default=DEFAULT_ARTS)
    parser.add_argument("--verbose", "-v", action="store_true", help="显示明细")
    args = parser.parse_args()
    
    # 加载后台文章列表
    if not os.path.exists(args.articles_json):
        print(f"❌ 找不到 {args.articles_json}")
        print(f"   请先运行 wxmp-list.py 生成，或设置环境变量 WXMP_ARTICLES")
        return 1
    
    with open(args.articles_json) as f:
        articles = json.load(f)
    
    print(f"📊 公众号存档完整性审核")
    print(f"{'='*50}")
    print(f"\n📡 后台文章总数: {len(articles)}")
    
    # 检查日期分布
    dates = [a.get('date', '') for a in articles if a.get('date')]
    if dates:
        print(f"📅 后台日期范围: {min(dates)} ~ {max(dates)}")
        print(f"   有日期: {len(dates)} 篇，无日期: {len(articles) - len(dates)} 篇")
    
    # 扫描存档
    print(f"\n📁 扫描存档...")
    files = find_archive_files()
    year_count = sum(1 for paths in files.values() for p in paths if '年份目录' in p[1])
    gh_count = sum(1 for paths in files.values() for p in paths if '.github-pages' in p[1])
    print(f"   年份目录: {year_count} 篇")
    print(f"   .github-pages: {gh_count} 篇")
    print(f"   存档总数: {year_count + gh_count} 篇（含重复）")
    
    # 检查移除记录
    print(f"\n🗑️ 移除记录...")
    removals = load_removals()
    print(f"   已移除: {len(removals)} 篇")
    if args.verbose and removals:
        for r in removals:
            print(f"     - {r['date']} {r['title'][:30]} ({r['reason']})")
    
    # 检查重复
    dupes = check_duplicates(files)
    print(f"\n🔄 重复文章: {len(dupes)} 篇")
    if args.verbose and dupes:
        print(f"   {'关键词':<30} {'来源'}")
        print(f"   {'-'*30} {'-'*20}")
        for kw, paths in dupes[:20]:
            sources = ', '.join(p[1] for p in paths)
            print(f"   {kw[:30]:<30} {sources}")
        if len(dupes) > 20:
            print(f"   ... 还有 {len(dupes) - 20} 篇")
    
    # 检查缺失
    print(f"\n❌ 缺失文章检测...")
    missing = check_missing(articles, files)
    tempkey_expired = [m for m in missing if m['reason'] == 'tempkey 过期']
    truly_missing = [m for m in missing if m['reason'] == '存档未找到']
    
    print(f"   tempkey 过期（无法补抓）: {len(tempkey_expired)} 篇")
    if args.verbose and tempkey_expired:
        for m in tempkey_expired[:10]:
            print(f"     - {m['title'][:40]}")
        if len(tempkey_expired) > 10:
            print(f"     ... 还有 {len(tempkey_expired) - 10} 篇")
    
    print(f"   存档未找到（可补抓）: {len(truly_missing)} 篇")
    if args.verbose and truly_missing:
        for m in truly_missing[:20]:
            print(f"     - {m['title'][:40]}")
        if len(truly_missing) > 20:
            print(f"     ... 还有 {len(truly_missing) - 20} 篇")
    
    # 汇总
    print(f"\n{'='*50}")
    print(f"📋 审核汇总")
    print(f"{'='*50}")
    print(f"   后台总数: {len(articles)}")
    print(f"   存档总数: {year_count + gh_count}（含 {len(dupes)} 篇重复）")
    print(f"   已移除: {len(removals)} 篇（见 _meta/removals.md）")
    print(f"   缺失: {len(missing)} 篇")
    print(f"     - tempkey 过期: {len(tempkey_expired)}")
    print(f"     - 可补抓: {len(truly_missing)}")
    
    if truly_missing:
        print(f"\n💡 建议: 运行以下命令补抓缺失文章")
        print(f"   python3 00_系统/agent/wxmp-fetch.py URL1 URL2 ...")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
