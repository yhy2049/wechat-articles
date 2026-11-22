#!/usr/bin/env bash
# PreToolUse: keep archives read-only; enforce the minimum schema for a new meeting.
set -u
VAULT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
payload="$(cat)"
path="$(printf '%s' "$payload" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get("tool_input", {}).get("file_path", "") or "")
except Exception:
    print("")
' 2>/dev/null)"
content="$(printf '%s' "$payload" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
    ti = d.get("tool_input", {})
    print(ti.get("content") or ti.get("new_string") or "")
except Exception:
    print("")
' 2>/dev/null)"

[ -z "$path" ] && exit 0
case "$path" in
  /*) abs="$path" ;;
  *) abs="$VAULT/$path" ;;
esac
case "$abs" in
  "$VAULT"/*) path="$abs" ;;
  *) exit 0 ;;
esac
case "$path" in
  *05_档案/公众号存档/*|*05_档案/媒体/*|*05_档案/放映数据/*)
    echo "存档目录只读：$path。新内容写到 06_AI/ 或对应项目目录，发布后再归档。" >&2
    exit 2
    ;;
  *05_档案/会议存档/*)
    if [ -e "$path" ]; then
      echo "会议存档已存在：$path。修订请写 06_AI/ 草稿，定稿后再替换存档并记 changelog。" >&2
      exit 2
    fi
    base="$(basename "$path")"
    if ! printf '%s' "$base" | grep -Eq '^[0-9]{4}-[0-9]{2}-[0-9]{2}[_-].+\.md$'; then
      echo "会议文件名必须是 YYYY-MM-DD_主题.md：$base" >&2
      exit 2
    fi
    missing=""
    for key in type date participants direction audience; do
      printf '%s' "$content" | grep -Eq "^${key}:" || missing="$missing $key"
    done
    if [ -n "$missing" ]; then
      echo "新会议缺 frontmatter 字段：$missing" >&2
      exit 2
    fi
    ;;
esac
exit 0
