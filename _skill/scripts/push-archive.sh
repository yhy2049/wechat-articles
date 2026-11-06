#!/bin/bash
# 发布公众号存档到 GitHub：仓库根目录 = 本目录内容，只上传存档本身
set -euo pipefail

VAULT=$(git rev-parse --show-toplevel)
MSG="${1:-更新公众号存档}"
cd "$VAULT"
git fetch origin main

# 直接取本地存档树作为仓库根树，不合并任何其他目录
TREE=$(git rev-parse 'main:05_档案/公众号存档')
COMMIT=$(git commit-tree "$TREE" -p origin/main -m "$MSG")
git push origin "$COMMIT:main"
echo "✅ $COMMIT"
