# 机构经纪智能体 - 语料/数据/规则梳理方案索引

> 生成时间：2026-03-07  
> 版本：V1.0  
> 覆盖模块：10个（实际生成9个）

---

## 📚 文档清单

| 序号 | 模块 | 文档 | 大小 | 核心内容 |
|------|------|------|------|----------|
| 01 | 引入客户 | [corpus-01-lead-management.md](./corpus-01-lead-management.md) | 33KB | 5维度评估沟通、5级跟进时效、转化漏斗 |
| 02 | 账户开立 | [corpus-02-account-opening.md](./corpus-02-account-opening.md) | 66KB | 4种开户沟通、5级审核流程、30+审核规则 |
| 03 | 交易服务 | [corpus-03-trading-service.md](./corpus-03-trading-service.md) | 32KB | 10种风控规则、4级告警、订单状态机 |
| 04 | 客户服务 | [corpus-04-customer-service.md](./corpus-04-customer-service.md) | 37KB | 三大类Q&A语料、四级舆情风险、SLA规则 |
| 05 | 业绩看板(员工) | [corpus-05-performance-dashboard.md](./corpus-05-performance-dashboard.md) | 30KB | 10项指标、1224排名算法、4级预警 |
| 06 | 提示事项 | [corpus-06-alert-management.md](./corpus-06-alert-management.md) | 18KB | 3种请示模板、分级审批权限、三级SLA |
| 07 | 业务组织 | [corpus-07-business-organization.md](./corpus-07-business-organization.md) | 33KB | 审核沟通、负载均衡算法、6类业务时限 |
| 08 | 队伍状况 | [corpus-08-team-status.md](./corpus-08-team-status.md) | 23KB | 负载计算公式、五维度绩效、协同分配规则 |
| 09 | 风险提示 | [corpus-09-risk-management.md](./corpus-09-risk-management.md) | 24KB | 7条预警阈值、四级风险体系、整改通知沟通 |
| 10 | 业绩看板(支持) | ~~corpus-10-performance-center.md~~ | ❌ 缺失 | 14项指标、星型模型、排行榜规则 |

> ⚠️ **注意**：corpus-10-performance-center.md 文件在子任务执行过程中未能生成，可能需要手动补充。

**总计：约 296KB+ 语料/数据/规则文档（9/10模块完成）**

---

## 📖 内容结构

每个模块文档包含以下章节：

### 一、参考语料
- AI提示词模板（场景化）
- 沟通示例（开场白、询问、应答、结束）
- 通知/报告模板

### 二、数据需求
- 输入数据清单（字段定义）
- 输出数据清单（结果结构）
- 数据来源（内部系统/外部接口）

### 三、使用规则
- 业务规则（评分、计算、流转）
- 约束条件（必填、格式、范围）
- 权限控制（角色、操作、数据）
- SLA规则（响应/处理时限）

---

## 🎯 使用说明

### 对于产品经理
- 查看各模块的"参考语料"章节，了解AI交互设计规范
- 查看"使用规则"章节，确认业务逻辑和约束条件

### 对于开发工程师
- 查看"数据需求"章节，获取完整的字段定义和数据结构
- 查看"使用规则"章节，获取业务规则的配置参数

### 对于数据工程师
- 所有文档提供的数据结构可直接用于数据库设计
- 参考数据建模方案（modeling-complete.md）进行物理模型设计

---

## 🔗 相关文档

- [产品原型设计成果](./原型设计成果.md)
- [数据建模方案（完整版）](./modeling-complete.md)
- [数据建模任务分配](./modeling-task-assignment.md)

---

## 📝 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| V1.0 | 2026-03-07 | 初始版本，覆盖9个模块的语料/数据/规则梳理（corpus-10-performance-center.md 缺失）|

---

*本文档由AI智能体自动生成，基于产品原型页面内容梳理*
