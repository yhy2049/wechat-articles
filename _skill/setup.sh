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

if command -v node >/dev/null 2>&1; then
  ok "node $(node -v)"
  if node -e "require.resolve('marked',{paths:['$HERE/node_modules']})" >/dev/null 2>&1; then
    ok "marked 可用（站点生成）"
  else
    warn "marked 缺失，只有重建 .github-pages 站点才需要（cd _skill && npm install）"
  fi
else
  warn "无 node：抓取与推送不受影响，仅站点生成不可用"
fi

if command -v git >/dev/null 2>&1; then ok "git $(git --version | awk '{print $3}')"; else bad "git 未安装（push-archive.sh 需要）"; fi
if command -v gh >/dev/null 2>&1; then ok "gh 已安装"; else warn "无 gh CLI：推送走 git 凭据即可"; fi

echo
echo "可覆盖的环境变量："
echo "  WXMP_HOME     列表 JSON 目录（默认 macOS ~/Library/Caches/wxmp，其他系统 ~/.cache/wxmp）"
echo "  WXMP_PROFILE  登录态浏览器目录（默认 ~/.wechat-automation/browser-profile）"
echo "  WXMP_ARTICLES 列表 JSON 文件路径"
echo "  WXMP_GIT_RESOLVE  github.com 直连不通时的绕行 IP，如 140.82.112.3"

if [ "$MODE" = "install" ]; then
  echo
  echo "安装依赖…"
  "$PY" -m pip install -r "$HERE/requirements.txt"
  "$PY" -m playwright install chromium
  command -v npm >/dev/null 2>&1 && (cd "$HERE" && npm install --no-audit --no-fund)
  echo "完成，重新自检："
  exec "$BASH_SOURCE" check
fi

if [ "$MISSING" -eq 0 ]; then
  echo "✅ 依赖齐备，可直接跑 SKILL.md 的三步流程"
else
  echo "❌ 有缺失项，执行：bash _skill/setup.sh install"
fi
exit "$MISSING"
