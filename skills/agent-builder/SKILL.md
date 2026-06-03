---
name: agent-builder
description: Intelligent agent design and construction methodology for securities industry digital transformation. Use when designing, modeling, and building AI agents for business process automation, organizational transformation, or workflow orchestration. Covers business modeling, corpus design, data modeling, role definition, prompt engineering, and compliance review. Particularly effective for financial services, institutional brokerage, wealth management, and regulated industries requiring structured AI implementation.
---

# 智能体构建器 (Agent Builder)

基于证券公司AI转型实践的智能体设计与构建方法论。

## 何时使用此技能

设计AI智能体实现以下目标时：
- 业务流程自动化与智能化
- 组织扁平化转型支持
- 专业能力AI化输出
- 多智能体协作组网
- 合规要求严格的金融场景

## 核心原则

### 1. 业务驱动原则
- 智能体设计必须服务于业务目标
- 优先解决高价值、高频率业务场景
- 每个智能体有明确的业务价值衡量标准

### 2. 组织能力开放原则
- 将中后台专业能力通过AI方式"打开"
- 打破部门墙，形成统一能力平台
- 前端3-4步内完成业务达成

### 3. 可演进原则
- 支持从单智能体到多智能体组网演进
- 模块化设计，便于能力扩展
- 与底座能力逐步融合的路径

## 构建流程

```
第一阶段：目标分析
    ↓
第二阶段：业务建模（参考 methodology.md）
    - 业务目标拆解
    - 角色设计
    - 规定动作定义
    - 语料收集
    ↓
第三阶段：数据建模
    - 实体关系设计
    - 数据表结构
    - 流程状态机
    ↓
第四阶段：智能体设计
    - 组织者设计
    - 超级数字员工设计
    - 提示词工程（参考 prompt-engineering.md）
    ↓
第五阶段：评审与优化（参考 review-checklist.md）
    - 九维度评审
    - 合规检查
    ↓
第六阶段：实施与迭代
```

## 关键设计要素

### 角色体系

| 角色类型 | 职责 | 示例 |
|---------|------|------|
| **组织者** | 任务分解、协调、决策升级 | 机构经纪协调官 |
| **超级数字员工** | 执行规定动作 | 客户开发员、开户专员 |
| **底座能力** | 提供统一语料、身份、关系网络 | 机构账户关联、风控规则 |

### 业务目标结构

```yaml
业务目标:
  目标名称: "引入客户"
  目标动作:
    - 线索收集
    - 资质初筛
    - 客户画像
    - 分配跟进
  角色分配: "客户开发员"
  底座调用:
    - "机构账户关联"
    - "风控规则标准"
```

### 提示词规范（详见 prompt-engineering.md）

- 动词+名词为主，形容词<10%
- 单句<15字，指令明确
- 双层提示词结构（工程级+交互级）
- 覆盖标准业务目标，非具体案例

## 参考文档

根据具体任务加载相应参考文档：

| 任务 | 参考文档 |
|------|---------|
| 业务建模方法论 | [methodology.md](references/methodology.md) |
| 提示词工程规范 | [prompt-engineering.md](references/prompt-engineering.md) |
| 评审检查清单 | [review-checklist.md](references/review-checklist.md) |
| 证券业务知识 | [securities-business.md](references/securities-business.md) |

## 项目模板

使用模板快速启动项目：
- 项目目录结构：`assets/project-template/`
- 建模文档模板：`assets/modeling-templates/`

## 输出规范

智能体方案文档应包含：
1. 目标分析（组织转型符合性检查）
2. 架构设计（角色、组网、底座调用）
3. 业务逻辑（规定动作、流程闭环）
4. 数据模型（ER图、表结构）
5. 提示词工程（系统提示词+用户提示词）
6. 合规与风险（Human-in-the-loop、熔断机制）

## 行业特定知识

证券行业智能体需特别关注：
- 投资者适当性管理
- 反洗钱合规要求
- 异常交易监控
- 程序化交易报告
- 尽职调查要求

详见 [securities-business.md](references/securities-business.md)
