#!/usr/bin/env bash
# 发布公众号存档到 GitHub：仓库根目录 = 存档目录内容，并保留远端已有的其他内容
#
#   bash _skill/scripts/push-archive.sh "提交说明"
#   bash _skill/scripts/push-archive.sh --dry-run "提交说明"    # 只算树，不推送
#
# 环境变量：
#   GIT_REMOTE  远端名（默认 origin）    GIT_BRANCH  分支（默认 main）
#   WXMP_GIT_RESOLVE  直连 github.com 失败时依次尝试的 IP 列表
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARCHIVE="$(cd "$HERE/../.." && pwd)"          # 存档根目录
REMOTE="${GIT_REMOTE:-origin}"
BRANCH="${GIT_BRANCH:-main}"
DRY=0
MSG="更新公众号存档"
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY=1 ;;
    *) MSG="$arg" ;;
  esac
done

IPS="${WXMP_GIT_RESOLVE:-140.82.112.3 140.82.113.3 140.82.114.3}"

git_try() {  # 直连失败则逐个 IP 绕行
  local desc="$1"; shift
  if git "$@"; then return 0; fi
  local ip
  for ip in $IPS; do
    echo "  ↻ $desc 经 $ip 重试" >&2
    if git -c http.curloptResolve="github.com:443:$ip" -c http.version=HTTP/1.1 \
            -c http.lowSpeedLimit=0 -c http.lowSpeedTime=600 "$@"; then
      return 0
    fi
  done
  return 1
}

TOPLEVEL="$(git -C "$ARCHIVE" rev-parse --show-toplevel 2>/dev/null || true)"
[ -z "$TOPLEVEL" ] && { echo "❌ 存档目录不在 git 仓库里：$ARCHIVE"; exit 1; }
PREFIX="$(python3 -c "import os;print(os.path.relpath('$ARCHIVE','$TOPLEVEL'))")"
[ "$PREFIX" = "." ] && PREFIX=""

git_try "fetch" -C "$TOPLEVEL" fetch "$REMOTE" "$BRANCH" || { echo "❌ 拉取 $REMOTE/$BRANCH 失败"; exit 1; }

if [ -n "$PREFIX" ]; then
  ARCHIVE_TREE="$(git -C "$TOPLEVEL" rev-parse "HEAD:$PREFIX" 2>/dev/null || true)"
else
  ARCHIVE_TREE="$(git -C "$TOPLEVEL" rev-parse "HEAD^{tree}" 2>/dev/null || true)"
fi
[ -z "$ARCHIVE_TREE" ] && { echo "❌ 本地 HEAD 里没有存档目录（先提交改动）"; exit 1; }
echo "存档目录: $ARCHIVE"
echo "仓库前缀: ${PREFIX:-（存档即仓库根目录）}"
echo "存档树:   $ARCHIVE_TREE"

TREE="$ARCHIVE_TREE"
if [ -n "$PREFIX" ]; then
  TOP="${PREFIX%%/*}"
  if git_try "探测远端 $TOP" -C "$TOPLEVEL" cat-file -e "$REMOTE/$BRANCH:$TOP" 2>/dev/null; then
    REST="${PREFIX#*/}"
    WORK="$(mktemp -d)"
    GIT_INDEX_FILE="$WORK/sub" git -C "$TOPLEVEL" read-tree "$REMOTE/$BRANCH:$TOP"
    if [ -n "$REST" ]; then
      GIT_INDEX_FILE="$WORK/sub" git -C "$TOPLEVEL" rm -r --cached --quiet --ignore-unmatch "$REST"
    fi
    OTHER="$(GIT_INDEX_FILE="$WORK/sub" git -C "$TOPLEVEL" write-tree)"
    GIT_INDEX_FILE="$WORK/root" git -C "$TOPLEVEL" read-tree "$ARCHIVE_TREE"
    GIT_INDEX_FILE="$WORK/root" git -C "$TOPLEVEL" read-tree --prefix="$TOP/" "$OTHER"
    TREE="$(GIT_INDEX_FILE="$WORK/root" git -C "$TOPLEVEL" write-tree)"
    rm -rf "$WORK"
    echo "合并树:   $TREE（保留 $TOP 下其他内容）"
  else
    echo "合并树:   $TREE（远端无 $TOP，直接镜像）"
  fi
fi

if [ "$DRY" = "1" ]; then
  echo "🧪 dry-run：不提交不推送"
  git -C "$TOPLEVEL" ls-tree --name-only "$TREE" | head -20
  exit 0
fi

COMMIT="$(git -C "$TOPLEVEL" commit-tree "$TREE" -p "$REMOTE/$BRANCH" -m "$MSG")"
git_try "push" -C "$TOPLEVEL" push "$REMOTE" "$COMMIT:$BRANCH" || { echo "❌ 推送失败"; exit 1; }
echo "✅ $COMMIT → $REMOTE/$BRANCH"
