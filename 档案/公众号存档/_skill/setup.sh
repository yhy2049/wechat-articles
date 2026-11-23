#!/usr/bin/env bash
# 自检 / 安装依赖，让这套 skill 在任何机器、任何 agent 上都能跑
#   bash _skill/setup.sh           # 只检查
#   bash _skill/setup.sh install   # 缺什么装什么
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-check}"
MISSING=0

ok()   { printf '  ✅ %s\n' "$1"; }
bad()  { printf '  ❌ %s\n' "$1"; MISSING=1; }
warn() { printf '  ⚠️  %s\n' "$1"; }

PY="$(command -v python3 || true)"
if [ -z "$PY" ]; then bad "python3 未安装"; else ok "python3 $($PY -V 2>&1 | awk '{print $2}')"; fi

if [ -n "$PY" ]; then
  for m in playwright requests PIL fitz; do
    if "$PY" -c "import $m" 2>/dev/null; then ok "Python 模块 $m"; else bad "Python 模块 $m（pip install $m）"; fi
  done
  if "$PY" - <<'PYEOF' >/dev/null 2>&1
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); b.close()
PYEOF
  then ok "Playwright Chromium 可启动"; else bad "Playwright Chromium 未就绪（python3 -m playwright install chromium）"; fi
fi

if command -v git >/dev/null 2>&1; then ok "git $(git --version | awk '{print $3}')"; else bad "git 未安装（push-archive.sh 需要）"; fi
if command -v gh >/dev/null 2>&1; then ok "gh 已安装"; else warn "无 gh CLI：推送走 git 凭据即可"; fi

echo
