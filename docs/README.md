# 自动发布说明

本文档目录已配置自动发布到 GitHub。

## 发布触发条件

- docs/ 目录下的任何文件发生变更
- 每 5 分钟自动检查一次

## GitHub 仓库

https://github.com/tangwm88/brokerage-workbench-docs/tree/master/docs

## 手动发布

如需立即发布，可运行：
```bash
bash scripts/auto-publish-docs.sh
```

## 最新状态

- 上次提交: $(git log -1 --oneline 2>/dev/null || echo "未知")
- 自动发布任务: 已启用（每5分钟检查）
