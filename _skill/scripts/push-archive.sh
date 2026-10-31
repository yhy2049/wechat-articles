#!/bin/bash
# 发布公众号存档到 GitHub：仓库根目录 = 本目录内容，保留 05_档案 下其他内容
set -euo pipefail

VAULT=$(git rev-parse --show-toplevel)
MSG="${1:-更新公众号存档}"
cd "$VAULT"
git fetch origin main

ARCHIVE_TREE=$(git rev-parse 'main:05_档案/公众号存档')

if git cat-file -e 'origin/main:05_档案' 2>/dev/null; then
  OTHER_TREE=$(git rev-parse 'origin/main:05_档案')
  IDX=$(mktemp -u /tmp/archive-index.XXXXXX)
  GIT_INDEX_FILE=$IDX git read-tree "$ARCHIVE_TREE"
  GIT_INDEX_FILE=$IDX git read-tree --prefix=05_档案/ "$OTHER_TREE"
  TREE=$(GIT_INDEX_FILE=$IDX git write-tree)
  rm -f "$IDX"
else
  TREE=$ARCHIVE_TREE
fi

COMMIT=$(git commit-tree "$TREE" -p origin/main -m "$MSG")
git push origin "$COMMIT:main"
echo "✅ $COMMIT"
