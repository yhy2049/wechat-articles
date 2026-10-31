#!/bin/bash
# 发布公众号存档到 GitHub：仓库根目录 = 本目录内容，保留 05_档案 下其他内容
set -euo pipefail

VAULT=$(git rev-parse --show-toplevel)
MSG="${1:-更新公众号存档}"
ARCHIVE="$VAULT/05_档案/公众号存档"
cd "$VAULT"
git fetch origin main

TMP=$(mktemp -d /tmp/archive-push.XXXXXX)
git worktree add --detach "$TMP" origin/main >/dev/null

(
  cd "$TMP"
  shopt -s dotglob nullglob
  for p in ./*; do
    [ "$p" = "./.git" ] && continue
    [ "$p" = "./05_档案" ] && continue
    rm -rf -- "$p"
  done
  rsync -a "$ARCHIVE/" "$TMP/"
  git add -A
)
TREE=$(git -C "$TMP" write-tree)
git worktree remove --force "$TMP"

COMMIT=$(git commit-tree "$TREE" -p origin/main -m "$MSG")
git push origin "$COMMIT:main"
echo "✅ $COMMIT"
