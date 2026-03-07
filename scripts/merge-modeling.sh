#!/bin/bash
# 汇总建模方案脚本

cd /root/.openclaw/workspace/docs

# 等待所有子任务完成（检查文件是否存在）
echo "等待所有建模方案文件生成..."

files=(
  "modeling-01-lead-management.md"
  "modeling-02-account-opening.md"
  "modeling-03-trading-service.md"
  "modeling-04-customer-service.md"
  "modeling-05-performance-dashboard.md"
  "modeling-06-alert-management.md"
  "modeling-07-business-organization.md"
  "modeling-08-team-status.md"
  "modeling-09-risk-management.md"
  "modeling-10-performance-center.md"
)

# 合并所有建模方案
cat > modeling-complete.md << 'EOF'
# 机构经纪智能体 - 完整数据建模方案

> 生成时间：$(date '+%Y-%m-%d %H:%M:%S')
> 版本：V1.0

---

## 目录

1. [引入客户模块建模方案](#一引入客户模块)
2. [账户开立模块建模方案](#二账户开立模块)
3. [交易服务模块建模方案](#三交易服务模块)
4. [客户服务模块建模方案](#四客户服务模块)
5. [员工端业绩看板建模方案](#五员工端业绩看板)
6. [提示事项模块建模方案](#六提示事项模块)
7. [业务组织模块建模方案](#七业务组织模块)
8. [队伍状况模块建模方案](#八队伍状况模块)
9. [风险提示模块建模方案](#九风险提示模块)
10. [支持中心业绩看板建模方案](#十支持中心业绩看板)

---

EOF

# 追加各模块内容
for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "" >> modeling-complete.md
    cat "$file" >> modeling-complete.md
    echo "" >> modeling-complete.md
    echo "---" >> modeling-complete.md
  else
    echo "警告：$file 未找到" >&2
  fi
done

# 添加附录
cat >> modeling-complete.md << 'EOF'

## 附录

### A. 全局实体关系图

```
[客户] --(拥有)--> [账户]
[客户] --(产生)--> [线索]
[客户] --(提交)--> [订单]
[客户] --(咨询)--> [工单]
[员工] --(跟进)--> [线索]
[员工] --(处理)--> [工单]
[员工] --(管理)--> [客户]
```

### B. 统一字段命名规范

| 中文含义 | 英文字段名 | 数据类型 |
|---------|-----------|---------|
| 客户编号 | customer_id | VARCHAR(32) |
| 员工编号 | employee_id | VARCHAR(32) |
| 创建时间 | created_at | DATETIME |
| 更新时间 | updated_at | DATETIME |
| 状态 | status | TINYINT |
| 备注 | remark | TEXT |

### C. 状态码定义

| 状态码 | 含义 |
|-------|------|
| 0 | 无效/删除 |
| 1 | 有效/正常 |
| 2 | 处理中 |
| 3 | 已完成 |
| 4 | 已取消 |

EOF

echo "建模方案汇总完成！"
echo "输出文件：modeling-complete.md"
