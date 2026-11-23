#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量修复历史文章排版

用法：
    python3 _skill/scripts/fix-all-formatting.py          # 检查并修复所有文章
    python3 _skill/scripts/fix-all-formatting.py --dry-run # 只检查，不修复

扫描所有年份目录，找出有排版问题的文章（短行占比 > 40%），
使用与 wxmp-fetch.py 相同的 fix_formatting() 函数修复。
"""
import os
import sys
import re

def is_block_element(line):
    """判断是否是块级元素"""
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith('!['):
        return True
    if stripped.startswith('#'):
        return True
    if stripped.startswith('>'):
        return True
    if stripped.startswith('- ') or stripped.startswith('* ') or re.match(r'^\d+\.', stripped):
        return True
    if stripped in ['---', '***', '___']:
        return True
    return False

def fix_formatting(md_body):
    """修复微信文章排版"""
    lines = md_body.split('\n')
    fixed = []
    text_buffer = []

    def flush_buffer():
        if text_buffer:
            merged = ''.join(text_buffer)
            fixed.append(merged)
            text_buffer.clear()

    for line in lines:
        stripped = line.strip()

        if is_block_element(line):
            flush_buffer()
            fixed.append(line)
            continue

        if not stripped:
            if text_buffer:
                flush_buffer()
            continue

        if len(stripped) >= 50:
            flush_buffer()
            fixed.append(stripped)
        else:
            text_buffer.append(stripped)

    flush_buffer()

    result = '\n'.join(fixed)
    result = re.sub(r'\n{3,}', '\n\n', result)
    return result

def check_formatting_issue(content):
    """检查是否有排版问题：短行占比 > 40%"""
    lines = content.split('\n')
    short_lines = 0
    text_lines = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('![') or stripped.startswith('#') or stripped.startswith('>'):
            continue

        text_lines += 1
        if len(stripped) < 20:
            short_lines += 1

    if text_lines > 0:
        ratio = short_lines / text_lines
        return ratio > 0.4, ratio

    return False, 0

def main():
    dry_run = '--dry-run' in sys.argv

    # 扫描所有年份目录
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    years = ['2022', '2023', '2024', '2025', '2026']

    total_files = 0
    issues = []
    fixed_count = 0

    for year in years:
        year_dir = os.path.join(base_dir, year)
        if not os.path.exists(year_dir):
            continue

        for f in os.listdir(year_dir):
            if not f.endswith('.md'):
                continue

            filepath = os.path.join(year_dir, f)
            total_files += 1

            with open(filepath, 'r', encoding='utf-8') as fp:
                content = fp.read()

            has_issue, ratio = check_formatting_issue(content)
            if has_issue:
                issues.append((filepath, ratio))

                if not dry_run:
                    # 修复排版
                    fixed_content = fix_formatting(content)

                    # 写回文件
                    with open(filepath, 'w', encoding='utf-8') as fp:
                        fp.write(fixed_content)

                    fixed_count += 1
                    if fixed_count % 50 == 0:
                        print(f"  已修复 {fixed_count} 篇...", flush=True)

    # 输出结果
    print(f"\n扫描完成: {total_files} 篇文章")
    print(f"发现排版问题: {len(issues)} 篇")

    if dry_run:
        print("\n=== 有问题的文章（前 20 篇）===")
        for filepath, ratio in sorted(issues, key=lambda x: x[1], reverse=True)[:20]:
            print(f"  {ratio*100:.0f}% 短行 | {os.path.relpath(filepath, base_dir)}")
    else:
        print(f"\n✅ 已修复 {fixed_count} 篇文章")

    return 0

if __name__ == "__main__":
    sys.exit(main())
