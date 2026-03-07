# 员工工作台 - 客户服务模块数据建模方案

## 概述

本文档为【员工工作台 - 客户服务模块】提供完整的数据建模方案，涵盖咨询响应、舆情监控、定期回访、投诉处理四大核心业务领域。

---

## 一、实体关系图（ER图文字描述）

### 1.1 核心实体列表

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           客户服务模块核心实体关系图                               │
└─────────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
    │   客户信息   │◄──────►│  咨询工单    │◄──────►│  工单记录    │
    │  (customer)  │   1:N  │  (inquiry)   │   1:N  │(ticket_log)  │
    └──────────────┘        └──────┬───────┘        └──────────────┘
                                   │
                                   │ N:M
                                   ▼
    ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
    │  舆情信息    │        │   客服人员   │◄──────►│  回访记录    │
    │(sentiment)   │        │    (agent)   │   1:N  │(visit_record)│
    └──────────────┘        └──────┬───────┘        └──────────────┘
                                   │
                                   │ 1:N
                                   ▼
    ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
    │  投诉工单    │◄──────►│  处理流程    │◄──────►│   SLA规则    │
    │(complaint)   │   1:N  │  (workflow)  │   N:1  │  (sla_rule)  │
    └──────────────┘        └──────────────┘        └──────────────┘
```

### 1.2 实体关系详细说明

| 主实体 | 关系 | 从实体 | 关联类型 | 关系描述 |
|--------|------|--------|----------|----------|
| customer | 1:N | inquiry | 一对多 | 一个客户可提交多个咨询工单 |
| customer | 1:N | complaint | 一对多 | 一个客户可提交多个投诉工单 |
| customer | 1:N | visit_record | 一对多 | 一个客户对应多条回访记录 |
| inquiry | 1:N | ticket_log | 一对多 | 一个咨询工单有多条处理日志 |
| inquiry | N:1 | agent | 多对一 | 多个工单可分配给同一客服 |
| complaint | 1:N | workflow | 一对多 | 一个投诉经历多个处理节点 |
| complaint | N:1 | agent | 多对一 | 投诉处理人 |
| agent | 1:N | visit_record | 一对多 | 客服执行回访任务 |
| sla_rule | 1:N | inquiry | 一对多 | SLA规则应用于咨询工单 |
| sla_rule | 1:N | complaint | 一对多 | SLA规则应用于投诉工单 |
| sentiment | N:1 | customer | 多对一 | 舆情关联客户（可选） |

### 1.3 实体属性概览

```
customer (客户信息)
├── customer_id (PK)
├── customer_name
├── customer_type
├── contact_phone
├── contact_email
├── registration_date
└── status

inquiry (咨询工单)
├── inquiry_id (PK)
├── customer_id (FK)
├── inquiry_type
├── priority
├── status
├── agent_id (FK)
├── create_time
├── response_deadline
├── resolve_deadline
└── satisfaction_score

sentiment (舆情监控)
├── sentiment_id (PK)
├── source_type
├── source_url
├── content_summary
├── sentiment_type
├── risk_level
├── discover_time
└── handler_id (FK)

visit_record (回访记录)
├── visit_id (PK)
├── customer_id (FK)
├── agent_id (FK)
├── visit_plan_type
├── scheduled_date
├── actual_date
├── visit_result
└── satisfaction_level

complaint (投诉工单)
├── complaint_id (PK)
├── customer_id (FK)
├── complaint_type
├── complaint_content
├── priority
├── status
├── handler_id (FK)
├── create_time
└── close_time

ticket_log (工单日志)
├── log_id (PK)
├── source_type
├── source_id
├── action_type
├── operator_id
├── operation_time
└── remark

sla_rule (SLA规则)
├── rule_id (PK)
├── rule_name
├── apply_scope
├── response_time_min
├── resolve_time_min
├── priority_level
└── is_active
```

---

## 二、数据表结构设计

### 2.1 客户信息表 (customer)

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|----------|------|------|--------|------|
| customer_id | VARCHAR | 32 | PRIMARY KEY | - | 客户唯一标识 |
| customer_code | VARCHAR | 20 | UNIQUE, NOT NULL | - | 客户编号 |
| customer_name | VARCHAR | 100 | NOT NULL | - | 客户名称 |
| customer_type | TINYINT | 1 | NOT NULL | 1 | 客户类型:1-个人,2-企业,3-VIP |
| contact_phone | VARCHAR | 20 | NOT NULL | - | 联系电话 |
| contact_email | VARCHAR | 100 | - | NULL | 联系邮箱 |
| id_number | VARCHAR | 18 | UNIQUE | NULL | 身份证号/营业执照号 |
| registration_date | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | 注册时间 |
| customer_level | TINYINT | 1 | NOT NULL | 1 | 客户等级:1-普通,2-银卡,3-金卡,4-钻石 |
| status | TINYINT | 1 | NOT NULL | 1 | 状态:1-正常,2-冻结,3-注销 |
| tags | VARCHAR | 500 | - | NULL | 客户标签,JSON格式 |
| create_time | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP ON UPDATE | 更新时间 |

**索引设计:**
- INDEX idx_customer_code (customer_code)
- INDEX idx_customer_name (customer_name)
- INDEX idx_phone (contact_phone)
- INDEX idx_type_status (customer_type, status)

---

### 2.2 咨询工单表 (inquiry)

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|----------|------|------|--------|------|
| inquiry_id | VARCHAR | 32 | PRIMARY KEY | - | 咨询工单唯一标识 |
| inquiry_no | VARCHAR | 20 | UNIQUE, NOT NULL | - | 咨询工单编号 |
| customer_id | VARCHAR | 32 | FOREIGN KEY | - | 关联客户ID |
| inquiry_type | TINYINT | 1 | NOT NULL | - | 咨询类型:1-业务咨询,2-技术支持,3-产品咨询,4-其他 |
| inquiry_channel | TINYINT | 1 | NOT NULL | 1 | 咨询渠道:1-电话,2-在线,3-邮件,4-APP,5-微信 |
| priority | TINYINT | 1 | NOT NULL | 2 | 优先级:1-紧急,2-高,3-中,4-低 |
| status | TINYINT | 1 | NOT NULL | 1 | 状态:1-待响应,2-处理中,3-待确认,4-已解决,5-已关闭 |
| title | VARCHAR | 200 | NOT NULL | - | 咨询标题 |
| content | TEXT | - | NOT NULL | - | 咨询内容 |
| attachments | VARCHAR | 2000 | - | NULL | 附件URL,JSON数组 |
| agent_id | VARCHAR | 32 | FOREIGN KEY | NULL | 处理客服ID |
| create_time | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| response_time | DATETIME | - | - | NULL | 首次响应时间 |
| response_deadline | DATETIME | - | NOT NULL | - | 响应时限 |
| resolve_deadline | DATETIME | - | NOT NULL | - | 处理时限 |
| resolve_time | DATETIME | - | - | NULL | 实际解决时间 |
| close_time | DATETIME | - | - | NULL | 关闭时间 |
| satisfaction_score | TINYINT | 1 | - | NULL | 满意度评分:1-5分 |
| satisfaction_comment | VARCHAR | 500 | - | NULL | 满意度评价 |
| source_ip | VARCHAR | 50 | - | NULL | 来源IP地址 |
| device_info | VARCHAR | 200 | - | NULL | 设备信息 |

**索引设计:**
- INDEX idx_inquiry_no (inquiry_no)
- INDEX idx_customer_id (customer_id)
- INDEX idx_agent_id (agent_id)
- INDEX idx_status (status)
- INDEX idx_create_time (create_time)
- INDEX idx_deadline (response_deadline, resolve_deadline)
- INDEX idx_type_priority (inquiry_type, priority)

---

### 2.3 舆情监控表 (sentiment)

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|----------|------|------|--------|------|
| sentiment_id | VARCHAR | 32 | PRIMARY KEY | - | 舆情唯一标识 |
| source_type | TINYINT | 1 | NOT NULL | - | 来源类型:1-财经网,2-新闻门户,3-社交媒体,4-论坛,5-自媒体,6-其他 |
| source_name | VARCHAR | 100 | NOT NULL | - | 来源名称 |
| source_url | VARCHAR | 500 | NOT NULL | - | 原文链接 |
| title | VARCHAR | 300 | NOT NULL | - | 舆情标题 |
| content_summary | TEXT | - | NOT NULL | - | 内容摘要 |
| full_content | LONGTEXT | - | - | NULL | 完整内容 |
| sentiment_type | TINYINT | 1 | NOT NULL | - | 情感类型:1-正面,2-中性,3-负面,4-严重负面 |
| sentiment_score | DECIMAL | 5,4 | NOT NULL | 0.5 | 情感分值:0-1,越小越负面 |
| risk_level | TINYINT | 1 | NOT NULL | - | 风险等级:1-低,2-中,3-高,4-严重 |
| related_keywords | VARCHAR | 500 | - | NULL | 相关关键词,JSON格式 |
| mention_count | INT | - | NOT NULL | 1 | 提及次数/转发量 |
| view_count | INT | - | NOT NULL | 0 | 浏览量 |
| customer_id | VARCHAR | 32 | FOREIGN KEY | NULL | 关联客户ID(可选) |
| discover_time | DATETIME | - | NOT NULL | - | 发现时间 |
| handler_id | VARCHAR | 32 | FOREIGN KEY | NULL | 处理人ID |
| handle_status | TINYINT | 1 | NOT NULL | 1 | 处理状态:1-待处理,2-处理中,3-已处理,4-已归档 |
| handle_result | TEXT | - | - | NULL | 处理结果 |
| notify_sent | TINYINT | 1 | NOT NULL | 0 | 是否已发送预警:0-否,1-是 |
| create_time | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP ON UPDATE | 更新时间 |

**索引设计:**
- INDEX idx_source_type (source_type)
- INDEX idx_sentiment_type (sentiment_type)
- INDEX idx_risk_level (risk_level)
- INDEX idx_handle_status (handle_status)
- INDEX idx_discover_time (discover_time)
- INDEX idx_risk_time (risk_level, discover_time)

---

### 2.4 回访计划表 (visit_plan)

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|----------|------|------|--------|------|
| plan_id | VARCHAR | 32 | PRIMARY KEY | - | 计划唯一标识 |
| plan_no | VARCHAR | 20 | UNIQUE, NOT NULL | - | 计划编号 |
| plan_type | TINYINT | 1 | NOT NULL | - | 计划类型:1-30天回访,2-60天回访,3-90天回访,4-自定义 |
| plan_name | VARCHAR | 100 | NOT NULL | - | 计划名称 |
| customer_id | VARCHAR | 32 | FOREIGN KEY | NOT NULL | 关联客户ID |
| related_business_type | TINYINT | 1 | NOT NULL | - | 关联业务:1-咨询,2-投诉,3-购买,4-服务完成 |
| related_business_id | VARCHAR | 32 | - | NULL | 关联业务ID |
| agent_id | VARCHAR | 32 | FOREIGN KEY | NULL | 分配客服ID |
| scheduled_date | DATE | - | NOT NULL | - | 计划回访日期 |
| visit_purpose | VARCHAR | 500 | - | NULL | 回访目的/重点事项 |
| status | TINYINT | 1 | NOT NULL | 1 | 状态:1-待执行,2-已执行,3-已延期,4-已取消 |
| create_time | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP ON UPDATE | 更新时间 |

**索引设计:**
- INDEX idx_plan_no (plan_no)
- INDEX idx_customer_id (customer_id)
- INDEX idx_agent_id (agent_id)
- INDEX idx_scheduled_date (scheduled_date)
- INDEX idx_status (status)

---

### 2.5 回访记录表 (visit_record)

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|----------|------|------|--------|------|
| record_id | VARCHAR | 32 | PRIMARY KEY | - | 记录唯一标识 |
| plan_id | VARCHAR | 32 | FOREIGN KEY | NULL | 关联计划ID |
| customer_id | VARCHAR | 32 | FOREIGN KEY | NOT NULL | 关联客户ID |
| agent_id | VARCHAR | 32 | FOREIGN KEY | NOT NULL | 执行客服ID |
| visit_type | TINYINT | 1 | NOT NULL | 1 | 回访方式:1-电话,2-上门,3-视频,4-其他 |
| scheduled_date | DATE | - | NOT NULL | - | 计划回访日期 |
| actual_date | DATETIME | - | NOT NULL | - | 实际回访时间 |
| visit_duration | INT | - | - | NULL | 回访时长(分钟) |
| visit_content | TEXT | - | NOT NULL | - | 回访内容记录 |
| customer_feedback | TEXT | - | - | NULL | 客户反馈 |
| satisfaction_level | TINYINT | 1 | - | NULL | 满意度:1-非常不满意,2-不满意,3-一般,4-满意,5-非常满意 |
| satisfaction_score | TINYINT | 1 | - | NULL | 评分:1-100分 |
| problem_resolved | TINYINT | 1 | - | NULL | 问题是否解决:0-否,1-是,2-部分解决 |
| follow_up_needed | TINYINT | 1 | NOT NULL | 0 | 是否需要跟进:0-否,1-是 |
| follow_up_content | VARCHAR | 500 | - | NULL | 跟进事项 |
| attachments | VARCHAR | 2000 | - | NULL | 附件,JSON格式 |
| remark | VARCHAR | 1000 | - | NULL | 备注 |
| create_time | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP ON UPDATE | 更新时间 |

**索引设计:**
- INDEX idx_customer_id (customer_id)
- INDEX idx_agent_id (agent_id)
- INDEX idx_plan_id (plan_id)
- INDEX idx_actual_date (actual_date)
- INDEX idx_satisfaction (satisfaction_level)

---

### 2.6 投诉工单表 (complaint)

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|----------|------|------|--------|------|
| complaint_id | VARCHAR | 32 | PRIMARY KEY | - | 投诉工单唯一标识 |
| complaint_no | VARCHAR | 20 | UNIQUE, NOT NULL | - | 投诉工单编号 |
| customer_id | VARCHAR | 32 | FOREIGN KEY | NOT NULL | 关联客户ID |
| complaint_type | TINYINT | 1 | NOT NULL | - | 投诉类型:1-服务态度,2-产品质量,3-处理效率,4-收费问题,5-其他 |
| complaint_channel | TINYINT | 1 | NOT NULL | 1 | 投诉渠道:1-电话,2-在线,3-邮件,4-信函,5-监管部门转办,6-其他 |
| priority | TINYINT | 1 | NOT NULL | 2 | 优先级:1-特急,2-紧急,3-一般,4-低 |
| status | TINYINT | 1 | NOT NULL | 1 | 状态:1-待受理,2-处理中,3-待反馈,4-待确认,5-已解决,6-已关闭,7-已驳回 |
| is_urgent | TINYINT | 1 | NOT NULL | 0 | 是否加急:0-否,1-是 |
| is_escalated | TINYINT | 1 | NOT NULL | 0 | 是否升级:0-否,1-是 |
| title | VARCHAR | 200 | NOT NULL | - | 投诉标题 |
| content | TEXT | - | NOT NULL | - | 投诉内容 |
| expected_result | VARCHAR | 500 | - | NULL | 客户期望结果 |
| attachments | VARCHAR | 2000 | - | NULL | 附件URL,JSON数组 |
| handler_id | VARCHAR | 32 | FOREIGN KEY | NULL | 当前处理人ID |
| handler_dept_id | VARCHAR | 32 | - | NULL | 处理部门ID |
| create_time | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| accept_time | DATETIME | - | - | NULL | 受理时间 |
| first_response_time | DATETIME | - | - | NULL | 首次响应时间 |
| resolve_time | DATETIME | - | - | NULL | 实际解决时间 |
| close_time | DATETIME | - | - | NULL | 关闭时间 |
| response_deadline | DATETIME | - | NOT NULL | - | 响应时限 |
| resolve_deadline | DATETIME | - | NOT NULL | - | 处理时限 |
| satisfaction_score | TINYINT | 1 | - | NULL | 满意度评分:1-5分 |
| satisfaction_comment | VARCHAR | 500 | - | NULL | 满意度评价 |
| refund_amount | DECIMAL | 15,2 | - | NULL | 退款金额 |
| compensation_amount | DECIMAL | 15,2 | - | NULL | 补偿金额 |
| is_repeated | TINYINT | 1 | NOT NULL | 0 | 是否重复投诉:0-否,1-是 |
| previous_complaint_id | VARCHAR | 32 | - | NULL | 关联前序投诉ID |
| source_ip | VARCHAR | 50 | - | NULL | 来源IP地址 |

**索引设计:**
- INDEX idx_complaint_no (complaint_no)
- INDEX idx_customer_id (customer_id)
- INDEX idx_handler_id (handler_id)
- INDEX idx_status (status)
- INDEX idx_create_time (create_time)
- INDEX idx_type_priority (complaint_type, priority)
- INDEX idx_deadline (response_deadline, resolve_deadline)

---

### 2.7 工单处理流程表 (workflow_node)

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|----------|------|------|--------|------|
| node_id | VARCHAR | 32 | PRIMARY KEY | - | 节点唯一标识 |
| source_type | TINYINT | 1 | NOT NULL | - | 来源类型:1-咨询,2-投诉 |
| source_id | VARCHAR | 32 | NOT NULL | - | 关联工单ID |
| node_type | TINYINT | 1 | NOT NULL | - | 节点类型:1-受理,2-分派,3-处理,4-审核,5-反馈,6-关闭,7-转办,8-升级 |
| node_name | VARCHAR | 50 | NOT NULL | - | 节点名称 |
| sequence | INT | - | NOT NULL | - | 节点顺序 |
| operator_id | VARCHAR | 32 | FOREIGN KEY | - | 操作人ID |
| operator_dept_id | VARCHAR | 32 | - | NULL | 操作部门ID |
| operation_time | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | 操作时间 |
| operation_result | TINYINT | 1 | NOT NULL | - | 操作结果:1-通过,2-驳回,3-转办,4-升级,5-其他 |
| operation_content | TEXT | - | - | NULL | 操作内容/处理意见 |
| attachments | VARCHAR | 2000 | - | NULL | 附件,JSON格式 |
| next_operator_id | VARCHAR | 32 | - | NULL | 下一处理人ID |
| next_dept_id | VARCHAR | 32 | - | NULL | 下一处理部门ID |
| duration_minutes | INT | - | - | NULL | 节点耗时(分钟) |
| remark | VARCHAR | 1000 | - | NULL | 备注 |

**索引设计:**
- INDEX idx_source (source_type, source_id)
- INDEX idx_operator_id (operator_id)
- INDEX idx_operation_time (operation_time)

---

### 2.8 工单日志表 (ticket_log)

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|----------|------|------|--------|------|
| log_id | VARCHAR | 32 | PRIMARY KEY | - | 日志唯一标识 |
| source_type | TINYINT | 1 | NOT NULL | - | 来源类型:1-咨询,2-投诉,3-回访,4-舆情 |
| source_id | VARCHAR | 32 | NOT NULL | - | 关联业务ID |
| action_type | TINYINT | 1 | NOT NULL | - | 操作类型:1-创建,2-更新,3-分派,4-转办,5-响应,6-处理,7-关闭,8-回访,9-其他 |
| action_name | VARCHAR | 50 | NOT NULL | - | 操作名称 |
| operator_id | VARCHAR | 32 | FOREIGN KEY | NOT NULL | 操作人ID |
| operator_role | TINYINT | 1 | NOT NULL | 1 | 操作人角色:1-客户,2-客服,3-主管,4-系统 |
| operation_time | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | 操作时间 |
| before_status | TINYINT | 1 | - | NULL | 操作前状态 |
| after_status | TINYINT | 1 | - | NULL | 操作后状态 |
| operation_content | TEXT | - | - | NULL | 操作内容详情 |
| ip_address | VARCHAR | 50 | - | NULL | 操作IP地址 |
| user_agent | VARCHAR | 500 | - | NULL | 用户代理信息 |
| remark | VARCHAR | 1000 | - | NULL | 备注 |

**索引设计:**
- INDEX idx_source (source_type, source_id)
- INDEX idx_operator_id (operator_id)
- INDEX idx_action_type (action_type)
- INDEX idx_operation_time (operation_time)

---

### 2.9 SLA规则表 (sla_rule)

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|----------|------|------|--------|------|
| rule_id | VARCHAR | 32 | PRIMARY KEY | - | 规则唯一标识 |
| rule_code | VARCHAR | 20 | UNIQUE, NOT NULL | - | 规则编码 |
| rule_name | VARCHAR | 100 | NOT NULL | - | 规则名称 |
| business_type | TINYINT | 1 | NOT NULL | - | 业务类型:1-咨询,2-投诉 |
| priority_level | TINYINT | 1 | NOT NULL | - | 优先级:1-特急,2-紧急,3-一般,4-低 |
| customer_level | TINYINT | 1 | - | NULL | 客户等级:1-普通,2-银卡,3-金卡,4-钻石, NULL表示全部 |
| response_time_minutes | INT | - | NOT NULL | - | 响应时限(分钟) |
| resolve_time_minutes | INT | - | NOT NULL | - | 处理时限(分钟) |
| work_time_type | TINYINT | 1 | NOT NULL | 1 | 工作时间类型:1-24小时,2-工作日8小时,3-自定义 |
| work_time_config | VARCHAR | 500 | - | NULL | 工作时间配置,JSON格式 |
| escalation_time_minutes | INT | - | - | NULL | 升级提醒时间(分钟) |
| escalation_target | VARCHAR | 50 | - | NULL | 升级对象:主管/部门 |
| warning_threshold | DECIMAL | 3,2 | NOT NULL | 0.8 | 预警阈值:0-1,如0.8表示80%时限触发预警 |
| is_active | TINYINT | 1 | NOT NULL | 1 | 是否启用:0-否,1-是 |
| effective_date | DATE | - | NOT NULL | - | 生效日期 |
| expiry_date | DATE | - | - | NULL | 失效日期 |
| create_time | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP ON UPDATE | 更新时间 |
| created_by | VARCHAR | 32 | NOT NULL | - | 创建人ID |

**索引设计:**
- INDEX idx_rule_code (rule_code)
- INDEX idx_business_type (business_type)
- INDEX idx_priority (priority_level)
- INDEX idx_active (is_active)

---

### 2.10 客服人员表 (customer_agent)

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|----------|------|------|--------|------|
| agent_id | VARCHAR | 32 | PRIMARY KEY | - | 客服唯一标识 |
| employee_no | VARCHAR | 20 | UNIQUE, NOT NULL | - | 员工编号 |
| agent_name | VARCHAR | 50 | NOT NULL | - | 客服姓名 |
| dept_id | VARCHAR | 32 | NOT NULL | - | 部门ID |
| role_type | TINYINT | 1 | NOT NULL | 1 | 角色:1-普通客服,2-高级客服,3-客服主管,4-客服经理 |
| skill_tags | VARCHAR | 500 | - | NULL | 技能标签,JSON格式 |
| max_ticket_count | INT | - | NOT NULL | 20 | 最大同时处理工单数 |
| current_ticket_count | INT | - | NOT NULL | 0 | 当前处理工单数 |
| status | TINYINT | 1 | NOT NULL | 1 | 状态:1-在职,2-离岗,3-休假,4-离职 |
| phone | VARCHAR | 20 | NOT NULL | - | 联系电话 |
| email | VARCHAR | 100 | NOT NULL | - | 邮箱 |
| create_time | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP ON UPDATE | 更新时间 |

**索引设计:**
- INDEX idx_employee_no (employee_no)
- INDEX idx_dept_id (dept_id)
- INDEX idx_status (status)

---

### 2.11 SLA超时记录表 (sla_violation)

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|----------|------|------|--------|------|
| violation_id | VARCHAR | 32 | PRIMARY KEY | - | 超时记录唯一标识 |
| source_type | TINYINT | 1 | NOT NULL | - | 业务类型:1-咨询,2-投诉 |
| source_id | VARCHAR | 32 | NOT NULL | - | 关联工单ID |
| rule_id | VARCHAR | 32 | FOREIGN KEY | NOT NULL | 关联SLA规则ID |
| violation_type | TINYINT | 1 | NOT NULL | - | 超时类型:1-响应超时,2-处理超时 |
| deadline_time | DATETIME | - | NOT NULL | - | 应完成时限 |
| actual_time | DATETIME | - | - | NULL | 实际完成时间 |
| overdue_minutes | INT | - | NOT NULL | - | 超时分钟数 |
| severity_level | TINYINT | 1 | NOT NULL | - | 严重程度:1-轻微,2-一般,3-严重,4-特别严重 |
| reason_type | TINYINT | 1 | - | NULL | 原因类型:1-系统故障,2-人员不足,3-客户原因,4-不可抗力,5-其他 |
| reason_description | VARCHAR | 500 | - | NULL | 原因说明 |
| is_excused | TINYINT | 1 | NOT NULL | 0 | 是否豁免:0-否,1-是 |
| excuse_reason | VARCHAR | 500 | - | NULL | 豁免原因 |
| excused_by | VARCHAR | 32 | - | NULL | 豁免审批人ID |
| penalty_score | INT | - | NOT NULL | 0 | 扣分值 |
| create_time | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |

**索引设计:**
- INDEX idx_source (source_type, source_id)
- INDEX idx_rule_id (rule_id)
- INDEX idx_violation_type (violation_type)

---

## 三、工单流转状态图

### 3.1 咨询工单状态流转图

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                               咨询工单状态流转图                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘

                                ┌─────────────┐
                                │   创建工单   │
                                │   [系统]    │
                                └──────┬──────┘
                                       │
                                       ▼
┌─────────────┐    首次响应    ┌─────────────┐    开始处理    ┌─────────────┐
│  自动关闭    │◄───────────────│   待响应     │──────────────►│   处理中     │
│ [超时/取消]  │                │   [初始]     │  分配客服     │             │
└─────────────┘                └──────┬──────┘               └──────┬──────┘
                                      │                             │
                         客户要求关闭 │                             │ 需要确认
                                      │                             ▼
                                      │                      ┌─────────────┐
                                      │                      │   待确认     │
                                      │                      │ [方案确认]   │
                                      │                      └──────┬──────┘
                                      │                             │
                                      │         客户确认            │ 拒绝
                                      │◄────────────────────────────┤
                                      │                             │
                                      │                             ▼
                                      │                      ┌─────────────┐
                                      │                      │  重新处理    │
                                      │                      │  [返回上级]  │
                                      │                      └─────────────┘
                                      │                             │
                                      │                             └──────┐
                                      │                                    │
                                      ▼                                    ▼
                               ┌─────────────┐                    ┌─────────────┐
                               │   已解决     │───────────────────►│   已关闭     │
                               │ [待评价]     │    评价/归档        │   [终态]     │
                               └──────┬──────┘                    └─────────────┘
                                      │
                                      │ 客户评价
                                      ▼
                               ┌─────────────┐
                               │   已评价     │
                               │ [满意度]     │
                               └─────────────┘


状态说明:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
状态值    状态名称        说明
─────────────────────────────────────────────────────────────────────────────────────
  1       待响应          工单创建后等待客服首次响应
  2       处理中          客服已响应并正在处理中
  3       待确认          提出解决方案等待客户确认
  4       已解决          问题已解决待客户评价
  5       已关闭          工单结束(包括已评价/超时关闭/客户取消)
  6       自动关闭        超时未响应自动关闭
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

流转规则:
1. 待响应 → 处理中: 客服首次响应(回复/电话/处理动作)
2. 待响应 → 自动关闭: 超过SLA响应时限仍未响应
3. 处理中 → 待确认: 提出解决方案
4. 待确认 → 已解决: 客户确认方案有效
5. 待确认 → 处理中: 客户拒绝方案, 返回处理
6. 已解决 → 已关闭: 客户评价完成或超过评价时限
7. 任何状态 → 已关闭: 客户主动取消(需确认)
```

### 3.2 投诉工单状态流转图

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                               投诉工单状态流转图                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘

                                ┌─────────────┐
                                │   创建投诉   │
                                │   [系统]    │
                                └──────┬──────┘
                                       │
                                       ▼
┌─────────────┐    分派受理    ┌─────────────┐    受理确认    ┌─────────────┐
│   已驳回     │◄───────────────│   待受理     │──────────────►│   处理中     │
│ [不符合条件] │                │   [初始]     │               │             │
└─────────────┘                └──────┬──────┘               └──────┬──────┘
                                      │                             │
                         不符合受理条件│                             │ 处理完成
                                      │                             ▼
                                      │                      ┌─────────────┐
                                      │                      │   待审核     │
                                      │                      │ [主管审核]   │
                                      │                      └──────┬──────┘
                                      │                             │
                                      │                             │ 审核通过
                                      │                             ▼
                                      │                      ┌─────────────┐
                                      │                      │   待反馈     │
                                      │                      │ [客户反馈]   │
                                      │                      └──────┬──────┘
                                      │                             │
                                      │                             │ 客户确认
                                      │                             ▼
                                      │                      ┌─────────────┐
                                      │                      │   待确认     │
                                      │                      │ [满意度]     │
                                      │                      └──────┬──────┘
                                      │                             │
                                      │    ┌────────────────────────┼────────────────┐
                                      │    │                        │                │
                                      │    │ 不满意                │ 满意           │
                                      │    ▼                        ▼                │
                                      │ ┌─────────────┐      ┌─────────────┐         │
                                      │ │  重新处理    │      │   已解决     │         │
                                      │ │ [升级/重新]  │◄─────│   [待评价]   │         │
                                      │ └──────┬──────┘      └──────┬──────┘         │
                                      │        │                    │                │
                                      │        └────────────────────┤                │
                                      │                             │                │
                                      │                             ▼                │
                                      │                      ┌─────────────┐         │
                                      └─────────────────────►│   已关闭     │◄────────┘
                                                               │   [终态]     │
                                                               └─────────────┘

特殊流转:
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 升级流程: 处理中 ──► 升级处理 ──► 转入待审核                                      │
│ 转办流程: 任何处理状态 ──► 转办 ──► 分配给新处理人                                │
│ 监管部门转办: 自动设置为"特急"优先级, 跳过待受理直接进入处理中                    │
└─────────────────────────────────────────────────────────────────────────────────┘

状态说明:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
状态值    状态名称        说明
─────────────────────────────────────────────────────────────────────────────────────
  1       待受理          投诉创建后等待主管分派和受理
  2       处理中          已受理, 正在调查处理
  3       待审核          处理完成等待主管审核
  4       待反馈          审核通过, 向客户反馈处理结果
  5       待确认          客户已收到反馈, 等待确认满意度
  6       已解决          客户确认满意, 待最终评价
  7       已关闭          投诉结束
  8       已驳回          投诉不符合受理条件被驳回
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 3.3 舆情处理状态流转图

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                               舆情处理状态流转图                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘

                                ┌─────────────┐
                                │   舆情发现   │
                                │   [系统]    │
                                └──────┬──────┘
                                       │
                                       │ 风险评级
                                       ▼
                               ┌─────────────┐
                               │   待处理     │
                               │ [风险确认]   │
                               └──────┬──────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    │ 低风险           │ 中风险          │ 高风险
                    ▼                 ▼                 ▼
            ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
            │   直接归档    │   │   处理中     │   │   紧急处理   │
            │   [记录]     │   │  [跟进]      │   │  [升级]      │
            └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
                   │                 │                 │
                   │                 ▼                 │
                   │        ┌─────────────┐            │
                   │        │   待确认     │            │
                   │        │ [效果确认]   │            │
                   │        └──────┬──────┘            │
                   │               │                   │
                   │               │ 舆情平息          │ 持续发酵
                   │               ▼                   │
                   │        ┌─────────────┐            ▼
                   │        │   已归档     │     ┌─────────────┐
                   │        │ [终态]       │     │  危机升级    │
                   │        └─────────────┘     │ [高管介入]   │
                   │                            └──────┬──────┘
                   │                                   │
                   │                                   ▼
                   │                            ┌─────────────┐
                   └───────────────────────────►│   已归档     │
                                                │   [终态]     │
                                                └─────────────┘

预警级别与响应:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
风险等级    情感分值范围      响应要求                      通知对象
─────────────────────────────────────────────────────────────────────────────────────
  低        0.6 - 1.0        24小时内记录归档              舆情监控员
  中        0.4 - 0.6        4小时内介入处理               客服主管+舆情专员
  高        0.2 - 0.4        1小时内响应, 2小时出方案     客服经理+公关部门
  严重      0.0 - 0.2        30分钟内响应, 立即上报       高管层+危机小组
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 四、SLA规则定义

### 4.1 咨询工单SLA规则

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           咨询工单SLA规则矩阵                                        │
└─────────────────────────────────────────────────────────────────────────────────────┘

优先级    │ 客户等级 │ 响应时限      │ 处理时限       │ 升级时限      │ 预警阈值
──────────┼─────────┼─────────────┼─────────────┼─────────────┼──────────
紧急(1)   │ 全部    │ 15分钟       │ 2小时        │ 10分钟       │ 80%
──────────┼─────────┼─────────────┼─────────────┼─────────────┼──────────
高(2)     │ 钻石    │ 30分钟       │ 4小时        │ 20分钟       │ 80%
高(2)     │ 金卡    │ 30分钟       │ 4小时        │ 20分钟       │ 80%
高(2)     │ 银卡    │ 1小时        │ 8小时        │ 40分钟       │ 80%
高(2)     │ 普通    │ 2小时        │ 12小时       │ 1小时        │ 80%
──────────┼─────────┼─────────────┼─────────────┼─────────────┼──────────
中(3)     │ 全部    │ 4小时        │ 24小时       │ 3小时        │ 80%
──────────┼─────────┼─────────────┼─────────────┼─────────────┼──────────
低(4)     │ 全部    │ 8小时        │ 48小时       │ 6小时        │ 80%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4.2 投诉工单SLA规则

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           投诉工单SLA规则矩阵                                        │
└─────────────────────────────────────────────────────────────────────────────────────┘

优先级     │ 受理时限   │ 首响时限   │ 处理时限    │ 审核时限   │ 反馈时限   │ 总时限
───────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────
特急(1)   │ 15分钟   │ 30分钟   │ 4小时    │ 1小时    │ 2小时    │ 8小时
───────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────
紧急(2)   │ 30分钟   │ 1小时    │ 8小时    │ 2小时    │ 4小时    │ 16小时
───────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────
一般(3)   │ 2小时    │ 4小时    │ 24小时   │ 4小时    │ 8小时    │ 42小时
───────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────
低(4)     │ 4小时    │ 8小时    │ 48小时   │ 8小时    │ 16小时   │ 84小时
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

特殊场景SLA调整:
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 场景                  │ SLA调整规则                                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 监管部门转办          │ 自动提升为"特急", 总时限压缩50%                         │
│ 重复投诉              │ 自动提升一级优先级                                      │
│ 加急标记              │ 响应时限减半, 处理时限压缩30%                           │
│ 非工作时间提交        │ 从下一个工作时段开始计算时限                            │
│ 客户要求延期          │ 可申请SLA暂停, 最长暂停48小时                           │
│ 系统故障              │ 可申请SLA豁免, 需提供故障工单号                         │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 回访SLA规则

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           回访计划执行SLA规则                                        │
└─────────────────────────────────────────────────────────────────────────────────────┘

回访类型        │ 计划提前期   │ 执行时限      │ 逾期处理
────────────────┼─────────────┼─────────────┼──────────────────────────────────────────
30天回访        │ 提前3天提醒  │ ±3天完成    │ 逾期3天自动升级为60天回访计划
60天回访        │ 提前5天提醒  │ ±5天完成    │ 逾期5天自动升级为90天回访计划
90天回访        │ 提前7天提醒  │ ±7天完成    │ 逾期7天标记为"回访失败",转人工跟进
自定义回访      │ 提前3天提醒  │ 按计划日期   │ 逾期自动转主管分配
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4.4 舆情响应SLA规则

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           舆情监控响应SLA规则                                        │
└─────────────────────────────────────────────────────────────────────────────────────┘

风险等级    │ 发现时限      │ 首次响应      │ 初步方案     │ 处理完成     │ 预警级别
───────────┼─────────────┼─────────────┼─────────────┼─────────────┼──────────
严重(4)    │ 实时监控     │ 30分钟内     │ 2小时内      │ 24小时内     │ 红色
高(3)      │ 实时监控     │ 1小时内      │ 4小时内      │ 48小时内     │ 橙色
中(2)      │ 每4小时扫描  │ 4小时内      │ 8小时内      │ 72小时内     │ 黄色
低(1)      │ 每日汇总     │ 24小时内     │ 无需方案     │ 记录归档     │ 蓝色
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4.5 SLA计算规则

```
工作时间计算方式:
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 类型              │ 计算规则                                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 24小时制          │ 自然时间连续计算, 不分节假日                                │
│ 工作日8小时       │ 工作日 9:00-18:00 计算, 不含周末和节假日                     │
│ 客服工作时间      │ 根据客服排班表计算有效工作时间                               │
└─────────────────────────────────────────────────────────────────────────────────┘

SLA状态判定:
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 状态              │ 判定条件                                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 正常              │ 当前时间 < 时限 × 预警阈值 (默认80%)                        │
│ 预警              │ 时限 × 预警阈值 ≤ 当前时间 < 时限                           │
│ 超时              │ 当前时间 ≥ 时限                                             │
│ 即将升级          │ 当前时间 ≥ 升级时限 (如有设置)                              │
└─────────────────────────────────────────────────────────────────────────────────┘

SLA豁免条件:
1. 系统故障导致的延误(需提供故障工单)
2. 客户提供信息不完整导致的等待时间
3. 客户主动要求延期(需客户确认)
4. 不可抗力因素(自然灾害、政策变化等)
5. 第三方依赖导致的延误(需凭证)
```

---

## 五、数据字典

### 5.1 通用枚举值定义

```yaml
# 客户类型
customer_type:
  1: 个人客户
  2: 企业客户
  3: VIP客户

# 客户等级
customer_level:
  1: 普通
  2: 银卡
  3: 金卡
  4: 钻石

# 优先级
priority:
  1: 特急/紧急
  2: 紧急/高
  3: 一般/中
  4: 低

# 情感类型
sentiment_type:
  1: 正面
  2: 中性
  3: 负面
  4: 严重负面

# 风险等级
risk_level:
  1: 低
  2: 中
  3: 高
  4: 严重

# 满意度等级
satisfaction_level:
  1: 非常不满意
  2: 不满意
  3: 一般
  4: 满意
  5: 非常满意

# 问题是否解决
problem_resolved:
  0: 否
  1: 是
  2: 部分解决
```

---

## 六、数据库设计规范

### 6.1 命名规范

| 对象类型 | 命名规则 | 示例 |
|----------|----------|------|
| 表名 | 小写 + 下划线 | `inquiry`, `visit_record` |
| 字段名 | 小写 + 下划线 | `customer_id`, `create_time` |
| 主键 | `表名_id` | `inquiry_id`, `complaint_id` |
| 外键 | `关联表名_id` | `customer_id`, `agent_id` |
| 索引 | `idx_字段名` | `idx_status`, `idx_create_time` |
| 唯一索引 | `uk_字段名` | `uk_inquiry_no` |

### 6.2 字段设计规范

1. **主键**: 统一使用 VARCHAR(32)，UUID格式
2. **状态字段**: 使用 TINYINT，附带详细注释说明每个值含义
3. **时间字段**: 
   - 创建时间: `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP
   - 更新时间: `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE
4. **金额字段**: 使用 DECIMAL(15,2)
5. **JSON字段**: 用于存储可变数组或对象，如 `attachments`, `tags`
6. **软删除**: 不使用物理删除，通过 `status` 字段控制

### 6.3 索引设计原则

1. 所有外键字段创建索引
2. 经常用于查询条件的字段创建索引
3. 状态 + 时间的组合索引用于列表查询
4. 避免过多索引(单表不超过10个)

---

## 七、扩展设计

### 7.1 未来可能扩展的表

| 表名 | 用途 | 关联表 |
|------|------|--------|
| knowledge_base | 知识库 | inquiry |
| auto_reply_template | 自动回复模板 | inquiry |
| satisfaction_survey | 满意度调查问卷 | visit_record, complaint |
| escalation_record | 升级记录 | inquiry, complaint |
| work_schedule | 客服排班 | customer_agent |
| sla_calendar | SLA工作日历 | sla_rule |

---

## 附录: ER图完整描述

```
[客户] 1 ─────── N [咨询工单] 1 ─────── N [工单日志]
  │                   │
  │ 1                 │ N
  │                   │
  N                   N
  │                   │
[回访记录] N ─────── 1 [客服]
  │                   │
  │ 1                 │ 1
  │                   │
  N                   N
  │                   │
[回访计划]            [投诉工单] 1 ─────── N [处理流程]
                        │
                        │ N
                        │
                        N
                        │
                       [SLA规则]

[舆情监控] N ─────── 1 [客服]
```

---

*文档版本: v1.0*
*创建日期: 2024年*
*适用模块: 员工工作台 - 客户服务模块*
