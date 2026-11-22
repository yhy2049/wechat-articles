#!/usr/bin/env bash
# PostToolUse: lint the file that was just written. Exit 2 blocks with feedback.
set -u
VAULT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
AGENT="${VAULT_AGENT:-$VAULT/00_系统/agent}"

payload="$(cat)"
path="$(printf '%s' "$payload" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get("tool_input", {}).get("file_path", "") or "")
except Exception:
    print("")
' 2>/dev/null)"

[ -z "$path" ] && exit 0
case "$path" in
  *.md) ;;
  *) exit 0 ;;
esac

# 相对路径按库根解析
case "$path" in
  /*) abs="$path" ;;
  *) abs="$VAULT/$path" ;;
esac
case "$abs" in
  "$VAULT"/*) ;;
  *) exit 0 ;;
esac
[ -f "$abs" ] || exit 0

out="$(cd "$AGENT" && python3 vault-lint.py --file "$abs" 2>&1)"
rc=$?
if [ "$rc" -eq 2 ]; then
  printf '%s\n' "$out" >&2
  exit 2
fi
exit 0
