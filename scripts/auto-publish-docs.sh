#!/bin/bash
# 产品设计文档自动发布脚本

set -e

echo "=== 文档自动发布开始 ==="
echo "时间: $(date)"

# 检查 docs 目录变更
if [ -z "$(git status --porcelain docs/ 2>/dev/null)" ]; then
    echo "✓ docs/ 目录无变更，无需发布"
    exit 0
fi

echo "发现 docs/ 目录变更，准备发布..."

# 添加变更
git add docs/

# 提交
COMMIT_MSG="docs: 自动更新交互设计 $(date '+%Y-%m-%d %H:%M')"
git commit -m "$COMMIT_MSG"
echo "✓ 已提交: $COMMIT_MSG"

# 使用 GitHub CLI 或环境变量中的 Token 推送
echo "正在推送到 GitHub..."
if timeout 60 git push origin master; then
    echo "✓ 推送成功"
    echo ""
    echo "=== 发布完成 ==="
    echo "GitHub 链接: https://github.com/tangwm88/brokerage-workbench-docs/tree/master/docs"
    echo "最新提交: $(git log -1 --oneline)"
    exit 0
else
    echo "× 推送失败"
    echo "请检查网络连接或稍后手动执行: git push origin master"
    exit 1
fi
