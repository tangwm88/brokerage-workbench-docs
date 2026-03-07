# 业务支持中心 - 提示事项模块数据建模方案

> 文档版本: v1.0  
> 创建日期: 2026-03-07  
> 适用模块: 提示事项管理（重大事项请示、问题反馈、资源协调）

---

## 一、实体关系图（ER图文字描述）

### 1.1 核心实体关系概览

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              提示事项模块核心实体关系图                                │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│   ┌──────────────────┐         ┌──────────────────┐                                 │
│   │    用户表         │         │    部门表         │                                 │
│   │   (sys_user)     │◄────────►│  (sys_dept)      │                                 │
│   │  - user_id       │         │  - dept_id       │                                 │
│   │  - dept_id       │         │  - dept_name     │                                 │
│   │  - user_name     │         │  - parent_id     │                                 │
│   └────────┬─────────┘         └──────────────────┘                                 │
│            │                                                                         │
│            │ 创建/处理/审批                                                            │
│            ▼                                                                         │
│   ┌──────────────────────────────────────────────────────┐                          │
│   │                    提示事项主表                        │                          │
│   │                (alert_management)                     │                          │
│   │  ┌────────────────────────────────────────────────┐  │                          │
│   │  │ - alert_id (PK)        提示事项ID              │  │                          │
│   │  │ - alert_type           事项类型               │  │                          │
│   │  │ - alert_title          事项标题               │  │                          │
│   │  │ - alert_content        事项内容               │  │                          │
│   │  │ - submitter_id (FK)    提交人ID               │  │                          │
│   │  │ - dept_id (FK)         所属部门               │  │                          │
│   │  │ - current_status       当前状态               │  │                          │
│   │  │ - current_handler_id   当前处理人             │  │                          │
│   │  │ - priority             优先级                 │  │                          │
│   │  │ - submit_time          提交时间               │  │                          │
│   │  │ - deadline             截止时间               │  │                          │
│   │  └────────────────────────────────────────────────┘  │                          │
│   └──────────────┬───────────────────────────────────────┘                          │
│                  │                      │                                           │
│      ┌───────────┴───────────┐          │                                           │
│      │                       │          │                                           │
│      ▼                       ▼          ▼                                           │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐                          │
│ │  重大事项请示    │ │   问题反馈       │ │   资源协调       │                          │
│ │   (major_request)│ │  (issue_feedback)│ │  (resource_coord)│                          │
│ │                 │ │                 │ │                 │                          │
│ │ - request_type  │ │ - feedback_type │ │ - resource_type │                          │
│ │ - policy_scope  │ │ - issue_category│ │ - resource_quota│                          │
│ │ - risk_level    │ │ - impact_scope  │ │ - usage_period  │                          │
│ └────────┬────────┘ └────────┬────────┘ └────────┬────────┘                          │
│          │                   │                   │                                  │
│          └───────────────────┼───────────────────┘                                  │
│                              │                                                      │
│                              ▼                                                      │
│   ┌──────────────────────────────────────────────────────┐                          │
│   │                    审批记录表                          │                          │
│   │              (approval_record)                        │                          │
│   │  ┌────────────────────────────────────────────────┐  │                          │
│   │  │ - record_id (PK)       记录ID                 │  │                          │
│   │  │ - alert_id (FK)        关联事项ID             │  │                          │
│   │  │ - approval_node        审批节点               │  │                          │
│   │  │ - approver_id (FK)     审批人ID               │  │                          │
│   │  │ - action_type          操作类型               │  │                          │
│   │  │ - approval_comment     审批意见               │  │                          │
│   │  │ - approval_time        审批时间               │  │                          │
│   │  │ - next_handler_id      下一处理人             │  │                          │
│   │  └────────────────────────────────────────────────┘  │                          │
│   └──────────────────────────────────────────────────────┘                          │
│                                                                                      │
│   ┌──────────────────────────────────────────────────────┐                          │
│   │                    附件表                             │                          │
│   │              (attachment)                             │                          │
│   │  ┌────────────────────────────────────────────────┐  │                          │
│   │  │ - attach_id (PK)       附件ID                 │  │                          │
│   │  │ - alert_id (FK)        关联事项ID             │  │                          │
│   │  │ - file_name            文件名                 │  │                          │
│   │  │ - file_path            存储路径               │  │                          │
│   │  │ - file_size            文件大小               │  │                          │
│   │  │ - upload_time          上传时间               │  │                          │
│   │  └────────────────────────────────────────────────┘  │                          │
│   └──────────────────────────────────────────────────────┘                          │
│                                                                                      │
│   ┌──────────────────────────────────────────────────────┐                          │
│   │                  通知记录表                           │                          │
│   │              (notification)                           │                          │
│   │  ┌────────────────────────────────────────────────┐  │                          │
│   │  │ - notify_id (PK)       通知ID                 │  │                          │
│   │  │ - alert_id (FK)        关联事项ID             │  │                          │
│   │  │ - recipient_id (FK)    接收人ID               │  │                          │
│   │  │ - notify_type          通知类型               │  │                          │
│   │  │ - notify_content       通知内容               │  │                          │
│   │  │ - is_read              是否已读               │  │                          │
│   │  └────────────────────────────────────────────────┘  │                          │
│   └──────────────────────────────────────────────────────┘                          │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 实体关系说明

| 主表 | 关联表 | 关系类型 | 关联字段 | 业务说明 |
|------|--------|----------|----------|----------|
| alert_management | major_request | 一对一 | alert_id | 重大事项请示扩展信息 |
| alert_management | issue_feedback | 一对一 | alert_id | 问题反馈扩展信息 |
| alert_management | resource_coord | 一对一 | alert_id | 资源协调扩展信息 |
| alert_management | approval_record | 一对多 | alert_id | 一个事项可有多条审批记录 |
| alert_management | attachment | 一对多 | alert_id | 一个事项可有多个附件 |
| alert_management | notification | 一对多 | alert_id | 一个事项可产生多条通知 |
| sys_user | alert_management | 一对多 | submitter_id | 用户可提交多个事项 |
| sys_dept | alert_management | 一对多 | dept_id | 部门可拥有多个事项 |

---

## 二、数据表结构设计

### 2.1 提示事项主表 (alert_management)

| 字段名 | 字段类型 | 长度/精度 | 是否可空 | 默认值 | 约束 | 说明 |
|--------|----------|-----------|----------|--------|------|------|
| alert_id | BIGINT | - | NOT NULL | 自增 | PRIMARY KEY | 提示事项唯一标识 |
| alert_no | VARCHAR | 32 | NOT NULL | - | UNIQUE | 事项编号（如：ALT-20260307-001） |
| alert_type | TINYINT | - | NOT NULL | - | CHECK(1-3) | 事项类型：1-重大事项请示 2-问题反馈 3-资源协调 |
| alert_title | VARCHAR | 200 | NOT NULL | - | - | 事项标题 |
| alert_content | TEXT | - | NOT NULL | - | - | 事项详细内容 |
| submitter_id | BIGINT | - | NOT NULL | - | FOREIGN KEY | 提交人ID，关联sys_user |
| submitter_name | VARCHAR | 50 | NOT NULL | - | - | 提交人姓名（冗余） |
| dept_id | BIGINT | - | NOT NULL | - | FOREIGN KEY | 所属部门ID，关联sys_dept |
| dept_name | VARCHAR | 100 | NOT NULL | - | - | 部门名称（冗余） |
| current_status | TINYINT | - | NOT NULL | 1 | CHECK(0-6) | 当前状态：0-草稿 1-待审批 2-审批中 3-已通过 4-已驳回 5-已撤销 6-已完成 |
| current_handler_id | BIGINT | - | NULL | - | FOREIGN KEY | 当前处理人ID |
| priority | TINYINT | - | NOT NULL | 2 | CHECK(1-4) | 优先级：1-紧急 2-高 3-中 4-低 |
| submit_time | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | - | 提交时间 |
| deadline | DATETIME | - | NULL | - | - | 截止时间 |
| complete_time | DATETIME | - | NULL | - | - | 完成时间 |
| is_urgent | TINYINT | - | NOT NULL | 0 | CHECK(0-1) | 是否加急：0-否 1-是 |
| source_channel | TINYINT | - | NOT NULL | 1 | - | 来源渠道：1-PC端 2-移动端 3-API |
| created_at | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | - | 创建时间 |
| updated_at | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | - | 更新时间（自动更新） |
| created_by | BIGINT | - | NOT NULL | - | - | 创建人ID |
| updated_by | BIGINT | - | NULL | - | - | 更新人ID |
| is_deleted | TINYINT | - | NOT NULL | 0 | CHECK(0-1) | 逻辑删除标记：0-正常 1-已删除 |

**索引设计：**
```sql
CREATE INDEX idx_alert_type ON alert_management(alert_type);
CREATE INDEX idx_current_status ON alert_management(current_status);
CREATE INDEX idx_submitter_id ON alert_management(submitter_id);
CREATE INDEX idx_dept_id ON alert_management(dept_id);
CREATE INDEX idx_submit_time ON alert_management(submit_time);
CREATE INDEX idx_priority ON alert_management(priority);
CREATE INDEX idx_current_handler ON alert_management(current_handler_id);
CREATE INDEX idx_alert_no ON alert_management(alert_no);
```

---

### 2.2 重大事项请示扩展表 (major_request)

| 字段名 | 字段类型 | 长度/精度 | 是否可空 | 默认值 | 约束 | 说明 |
|--------|----------|-----------|----------|--------|------|------|
| id | BIGINT | - | NOT NULL | 自增 | PRIMARY KEY | 主键 |
| alert_id | BIGINT | - | NOT NULL | - | FOREIGN KEY, UNIQUE | 关联提示事项主表 |
| request_type | TINYINT | - | NOT NULL | - | CHECK(1-3) | 请示类型：1-战略客户政策 2-资源投入 3-合规风险 |
| policy_scope | TINYINT | - | NULL | - | CHECK(1-3) | 政策适用范围：1-单一客户 2-区域范围 3-全公司 |
| customer_id | BIGINT | - | NULL | - | - | 关联客户ID（战略客户政策时必填） |
| customer_name | VARCHAR | 100 | NULL | - | - | 客户名称 |
| estimated_amount | DECIMAL | 18,2 | NULL | - | - | 预估金额（万元） |
| risk_level | TINYINT | - | NOT NULL | 2 | CHECK(1-4) | 风险等级：1-极高 2-高 3-中 4-低 |
| risk_desc | TEXT | - | NULL | - | - | 风险描述 |
| expected_result | TEXT | - | NULL | - | - | 期望审批结果 |
| related_dept_ids | VARCHAR | 500 | NULL | - | - | 涉及部门ID列表（JSON格式） |
| need_report | TINYINT | - | NOT NULL | 0 | CHECK(0-1) | 是否需要上报：0-否 1-是 |
| report_target | TINYINT | - | NULL | - | CHECK(1-3) | 上报对象：1-部门负责人 2-分管领导 3-总经理 |
| created_at | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | - | 创建时间 |
| updated_at | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | - | 更新时间 |

**索引设计：**
```sql
CREATE INDEX idx_alert_id_major ON major_request(alert_id);
CREATE INDEX idx_request_type ON major_request(request_type);
CREATE INDEX idx_risk_level ON major_request(risk_level);
CREATE INDEX idx_customer_id ON major_request(customer_id);
```

---

### 2.3 问题反馈扩展表 (issue_feedback)

| 字段名 | 字段类型 | 长度/精度 | 是否可空 | 默认值 | 约束 | 说明 |
|--------|----------|-----------|----------|--------|------|------|
| id | BIGINT | - | NOT NULL | 自增 | PRIMARY KEY | 主键 |
| alert_id | BIGINT | - | NOT NULL | - | FOREIGN KEY, UNIQUE | 关联提示事项主表 |
| feedback_type | TINYINT | - | NOT NULL | - | CHECK(1-5) | 反馈类型：1-产品问题 2-流程问题 3-系统问题 4-协作问题 5-其他 |
| issue_category | TINYINT | - | NOT NULL | - | - | 问题分类（根据类型动态） |
| impact_scope | TINYINT | - | NOT NULL | 1 | CHECK(1-4) | 影响范围：1-个人 2-团队 3-部门 4-公司级 |
| impact_desc | TEXT | - | NULL | - | - | 影响描述 |
| occurrence_time | DATETIME | - | NULL | - | - | 问题发生时间 |
| frequency | TINYINT | - | NULL | - | CHECK(1-4) | 发生频率：1-首次 2-偶尔 3-经常 4-持续 |
| reproduction_steps | TEXT | - | NULL | - | - | 重现步骤 |
| expected_solution | TEXT | - | NULL | - | - | 期望解决方案 |
| related_system | VARCHAR | 100 | NULL | - | - | 相关系统/模块 |
| related_order_no | VARCHAR | 50 | NULL | - | - | 关联订单号 |
| assignee_id | BIGINT | - | NULL | - | FOREIGN KEY | 被指派人ID |
| assignee_dept_id | BIGINT | - | NULL | - | - | 被指派人部门ID |
| resolve_deadline | DATETIME | - | NULL | - | - | 解决期限 |
| resolve_result | TEXT | - | NULL | - | - | 解决结果 |
| satisfaction_score | TINYINT | - | NULL | - | CHECK(1-5) | 满意度评分：1-5分 |
| created_at | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | - | 创建时间 |
| updated_at | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | - | 更新时间 |

**索引设计：**
```sql
CREATE INDEX idx_alert_id_issue ON issue_feedback(alert_id);
CREATE INDEX idx_feedback_type ON issue_feedback(feedback_type);
CREATE INDEX idx_assignee_id ON issue_feedback(assignee_id);
CREATE INDEX idx_issue_category ON issue_feedback(issue_category);
```

---

### 2.4 资源协调扩展表 (resource_coord)

| 字段名 | 字段类型 | 长度/精度 | 是否可空 | 默认值 | 约束 | 说明 |
|--------|----------|-----------|----------|--------|------|------|
| id | BIGINT | - | NOT NULL | 自增 | PRIMARY KEY | 主键 |
| alert_id | BIGINT | - | NOT NULL | - | FOREIGN KEY, UNIQUE | 关联提示事项主表 |
| resource_type | TINYINT | - | NOT NULL | - | CHECK(1-3) | 资源类型：1-算力 2-人力 3-预算 |
| resource_subtype | VARCHAR | 50 | NULL | - | - | 资源子类型（如：GPU/CPU/内存） |
| resource_quota | DECIMAL | 18,2 | NOT NULL | - | - | 申请额度（算力-GPU小时/人力-人天/预算-万元） |
| used_quota | DECIMAL | 18,2 | NOT NULL | 0 | - | 已使用额度 |
| quota_unit | VARCHAR | 20 | NOT NULL | - | - | 额度单位 |
| usage_purpose | TEXT | - | NOT NULL | - | - | 使用目的 |
| usage_period_start | DATE | - | NOT NULL | - | - | 使用期限-开始 |
| usage_period_end | DATE | - | NOT NULL | - | - | 使用期限-结束 |
| project_id | BIGINT | - | NULL | - | - | 关联项目ID |
| project_name | VARCHAR | 100 | NULL | - | - | 项目名称 |
| cost_center | VARCHAR | 50 | NULL | - | - | 成本中心 |
| is_cross_dept | TINYINT | - | NOT NULL | 0 | CHECK(0-1) | 是否跨部门：0-否 1-是 |
| support_dept_id | BIGINT | - | NULL | - | - | 支持部门ID（跨部门时必填） |
| support_dept_name | VARCHAR | 100 | NULL | - | - | 支持部门名称 |
| actual_allocation | DECIMAL | 18,2 | NULL | - | - | 实际分配额度 |
| allocation_time | DATETIME | - | NULL | - | - | 分配时间 |
| allocation_by | BIGINT | - | NULL | - | - | 分配人ID |
| return_plan | TEXT | - | NULL | - | - | 资源归还计划 |
| return_status | TINYINT | - | NOT NULL | 0 | CHECK(0-2) | 归还状态：0-未归还 1-部分归还 2-已归还 |
| created_at | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | - | 创建时间 |
| updated_at | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | - | 更新时间 |

**索引设计：**
```sql
CREATE INDEX idx_alert_id_resource ON resource_coord(alert_id);
CREATE INDEX idx_resource_type ON resource_coord(resource_type);
CREATE INDEX idx_project_id ON resource_coord(project_id);
CREATE INDEX idx_usage_period ON resource_coord(usage_period_start, usage_period_end);
```

---

### 2.5 审批记录表 (approval_record)

| 字段名 | 字段类型 | 长度/精度 | 是否可空 | 默认值 | 约束 | 说明 |
|--------|----------|-----------|----------|--------|------|------|
| record_id | BIGINT | - | NOT NULL | 自增 | PRIMARY KEY | 记录ID |
| alert_id | BIGINT | - | NOT NULL | - | FOREIGN KEY | 关联事项ID |
| alert_type | TINYINT | - | NOT NULL | - | - | 事项类型（冗余） |
| approval_node | TINYINT | - | NOT NULL | - | - | 审批节点序号 |
| node_name | VARCHAR | 50 | NOT NULL | - | - | 节点名称 |
| approver_id | BIGINT | - | NOT NULL | - | FOREIGN KEY | 审批人ID |
| approver_name | VARCHAR | 50 | NOT NULL | - | - | 审批人姓名（冗余） |
| approver_dept_id | BIGINT | - | NOT NULL | - | - | 审批人部门ID |
| approver_role | VARCHAR | 50 | NULL | - | - | 审批人角色 |
| action_type | TINYINT | - | NOT NULL | - | CHECK(1-6) | 操作类型：1-提交 2-通过 3-驳回 4-转办 5-加签 6-撤回 |
| action_name | VARCHAR | 20 | NOT NULL | - | - | 操作名称（显示用） |
| approval_comment | VARCHAR | 1000 | NULL | - | - | 审批意见 |
| approval_time | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | - | 审批时间 |
| next_handler_id | BIGINT | - | NULL | - | - | 下一处理人ID |
| next_node | TINYINT | - | NULL | - | - | 下一节点序号 |
| is_current | TINYINT | - | NOT NULL | 0 | CHECK(0-1) | 是否当前节点：0-否 1-是 |
| cost_time | INT | - | NULL | - | - | 耗时（分钟） |
| created_at | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | - | 创建时间 |

**索引设计：**
```sql
CREATE INDEX idx_alert_id_record ON approval_record(alert_id);
CREATE INDEX idx_approver_id ON approval_record(approver_id);
CREATE INDEX idx_approval_time ON approval_record(approval_time);
CREATE INDEX idx_is_current ON approval_record(is_current);
CREATE INDEX idx_action_type ON approval_record(action_type);
```

---

### 2.6 附件表 (attachment)

| 字段名 | 字段类型 | 长度/精度 | 是否可空 | 默认值 | 约束 | 说明 |
|--------|----------|-----------|----------|--------|------|------|
| attach_id | BIGINT | - | NOT NULL | 自增 | PRIMARY KEY | 附件ID |
| alert_id | BIGINT | - | NOT NULL | - | FOREIGN KEY | 关联事项ID |
| file_name | VARCHAR | 200 | NOT NULL | - | - | 文件名 |
| original_name | VARCHAR | 200 | NOT NULL | - | - | 原始文件名 |
| file_path | VARCHAR | 500 | NOT NULL | - | - | 存储路径 |
| file_size | BIGINT | - | NOT NULL | - | - | 文件大小（字节） |
| file_type | VARCHAR | 50 | NOT NULL | - | - | 文件类型 |
| file_ext | VARCHAR | 10 | NOT NULL | - | - | 文件扩展名 |
| upload_by | BIGINT | - | NOT NULL | - | - | 上传人ID |
| upload_time | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | - | 上传时间 |
| is_deleted | TINYINT | - | NOT NULL | 0 | CHECK(0-1) | 是否删除：0-否 1-是 |

**索引设计：**
```sql
CREATE INDEX idx_alert_id_attach ON attachment(alert_id);
CREATE INDEX idx_upload_time ON attachment(upload_time);
```

---

### 2.7 通知记录表 (notification)

| 字段名 | 字段类型 | 长度/精度 | 是否可空 | 默认值 | 约束 | 说明 |
|--------|----------|-----------|----------|--------|------|------|
| notify_id | BIGINT | - | NOT NULL | 自增 | PRIMARY KEY | 通知ID |
| alert_id | BIGINT | - | NOT NULL | - | FOREIGN KEY | 关联事项ID |
| recipient_id | BIGINT | - | NOT NULL | - | FOREIGN KEY | 接收人ID |
| notify_type | TINYINT | - | NOT NULL | - | CHECK(1-5) | 通知类型：1-待办 2-审批通过 3-审批驳回 4-转办 5-超时提醒 |
| notify_title | VARCHAR | 200 | NOT NULL | - | - | 通知标题 |
| notify_content | TEXT | - | NULL | - | - | 通知内容 |
| notify_channel | TINYINT | - | NOT NULL | 1 | CHECK(1-4) | 通知渠道：1-系统消息 2-邮件 3-短信 4-企微 |
| is_read | TINYINT | - | NOT NULL | 0 | CHECK(0-1) | 是否已读：0-否 1-是 |
| read_time | DATETIME | - | NULL | - | - | 阅读时间 |
| send_time | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | - | 发送时间 |
| expire_time | DATETIME | - | NULL | - | - | 过期时间 |
| created_at | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | - | 创建时间 |

**索引设计：**
```sql
CREATE INDEX idx_alert_id_notify ON notification(alert_id);
CREATE INDEX idx_recipient_id ON notification(recipient_id);
CREATE INDEX idx_is_read ON notification(is_read);
CREATE INDEX idx_send_time ON notification(send_time);
CREATE INDEX idx_notify_type ON notification(notify_type);
```

---

### 2.8 审批流程配置表 (approval_flow_config)

| 字段名 | 字段类型 | 长度/精度 | 是否可空 | 默认值 | 约束 | 说明 |
|--------|----------|-----------|----------|--------|------|------|
| config_id | BIGINT | - | NOT NULL | 自增 | PRIMARY KEY | 配置ID |
| alert_type | TINYINT | - | NOT NULL | - | - | 事项类型 |
| request_type | TINYINT | - | NULL | - | - | 请示类型（重大事项请示时必填） |
| resource_type | TINYINT | - | NULL | - | - | 资源类型（资源协调时必填） |
| node_seq | TINYINT | - | NOT NULL | - | - | 节点序号 |
| node_name | VARCHAR | 50 | NOT NULL | - | - | 节点名称 |
| approver_type | TINYINT | - | NOT NULL | - | CHECK(1-4) | 审批人类型：1-指定人 2-上级 3-角色 4-部门负责人 |
| approver_id | BIGINT | - | NULL | - | - | 指定审批人ID |
| approver_role_id | BIGINT | - | NULL | - | - | 审批角色ID |
| is_parallel | TINYINT | - | NOT NULL | 0 | CHECK(0-1) | 是否并行审批：0-否 1-是 |
| condition_expr | VARCHAR | 500 | NULL | - | - | 条件表达式（如：amount>100000） |
| is_enabled | TINYINT | - | NOT NULL | 1 | CHECK(0-1) | 是否启用：0-否 1-是 |
| created_at | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | - | 创建时间 |
| updated_at | DATETIME | - | NOT NULL | CURRENT_TIMESTAMP | - | 更新时间 |

**索引设计：**
```sql
CREATE INDEX idx_alert_type_config ON approval_flow_config(alert_type);
CREATE INDEX idx_node_seq ON approval_flow_config(node_seq);
CREATE INDEX idx_is_enabled ON approval_flow_config(is_enabled);
```

---

## 三、审批流程状态机

### 3.1 状态流转图

```
                              ┌─────────────┐
                              │   草稿       │
                              │  (DRAFT)    │
                              │    状态码:0  │
                              └──────┬──────┘
                                     │ 提交
                                     ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                       │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐           │
│   │   待审批     │───►│   审批中     │───►│   已通过     │───►│   已完成     │           │
│   │ (PENDING)   │    │ (APPROVING) │    │  (APPROVED) │    │ (COMPLETED) │           │
│   │   状态码:1  │    │   状态码:2  │    │   状态码:3  │    │   状态码:6  │           │
│   └──────┬──────┘    └──────┬──────┘    └─────────────┘    └─────────────┘           │
│          │                  │                                                         │
│          │ 驳回              │ 驳回                                                    │
│          ▼                  ▼                                                         │
│   ┌─────────────┐    ┌─────────────┐                                                   │
│   │   已驳回     │◄───│   已驳回     │                                                   │
│   │ (REJECTED)  │    │ (REJECTED)  │                                                   │
│   │   状态码:4  │    │   状态码:4  │                                                   │
│   └─────────────┘    └──────┬──────┘                                                   │
│                             │                                                         │
│                             │ 撤销                                                     │
│                             ▼                                                         │
│                       ┌─────────────┐                                                   │
│                       │   已撤销     │                                                   │
│                       │ (CANCELLED) │                                                   │
│                       │   状态码:5  │                                                   │
│                       └─────────────┘                                                   │
│                                                                                       │
└──────────────────────────────────────────────────────────────────────────────────────┘

                           ▲              ▲              ▲
                           │              │              │
                    ┌──────┴──────┐       │              │
                    │   重新提交   │────────┘              │
                    │ (RESUBMIT)  │                      │
                    └─────────────┘                      │
                                                         │
                                                         │ 完成/归档
                                                         └──────────────►
```

### 3.2 状态流转规则

| 当前状态 | 允许操作 | 目标状态 | 触发条件 | 权限要求 |
|----------|----------|----------|----------|----------|
| 草稿(0) | 提交 | 待审批(1) | 提交人确认提交 | 提交人本人 |
| 草稿(0) | 删除 | 删除 | 提交人删除草稿 | 提交人本人 |
| 待审批(1) | 审批通过 | 已通过(3) | 审批人同意 | 当前审批人 |
| 待审批(1) | 审批驳回 | 已驳回(4) | 审批人不同意 | 当前审批人 |
| 待审批(1) | 转办 | 待审批(1) | 转给其他审批人 | 当前审批人 |
| 待审批(1) | 加签 | 审批中(2) | 增加审批节点 | 当前审批人 |
| 待审批(1) | 撤回 | 已撤销(5) | 提交人主动撤回 | 提交人本人 |
| 审批中(2) | 审批通过 | 已通过(3) | 最后节点审批通过 | 当前审批人 |
| 审批中(2) | 审批驳回 | 已驳回(4) | 任一节点审批驳回 | 当前审批人 |
| 审批中(2) | 继续审批 | 审批中(2) | 中间节点审批通过 | 当前审批人 |
| 已通过(3) | 归档完成 | 已完成(6) | 事项处理完成 | 系统/管理员 |
| 已驳回(4) | 重新提交 | 待审批(1) | 提交人修改后重提 | 原提交人 |
| 已驳回(4) | 关闭 | 已完成(6) | 不再处理 | 提交人/管理员 |
| 已撤销(5) | 重新提交 | 待审批(1) | 提交人修改后重提 | 原提交人 |
| 已完成(6) | 无 | - | 终态 | - |

### 3.3 各类型事项审批流程配置

#### 3.3.1 重大事项请示审批流

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                          重大事项请示审批流程配置                                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  【战略客户政策类型】                                                                 │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐               │
│  │ 提交人   │──►│部门主管  │──►│部门经理  │──►│ 分管领导 │──►│ 总经理   │               │
│  │  (自动)  │   │ (条件1) │   │ (条件2) │   │ (条件3) │   │ (条件4) │               │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘               │
│                                                                                      │
│  条件说明：                                                                          │
│  - 条件1: 预估金额 ≥ 50万 或 风险等级 = 高/极高                                     │
│  - 条件2: 预估金额 ≥ 100万 或 影响范围 = 全公司                                      │
│  - 条件3: 预估金额 ≥ 500万 或 需要上报总经理                                        │
│  - 条件4: 预估金额 ≥ 1000万                                                          │
│                                                                                      │
│  ──────────────────────────────────────────────────────────────                     │
│                                                                                      │
│  【资源投入类型】                                                                     │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐                             │
│  │ 提交人   │──►│部门经理  │──►│ 财务部门 │──►│ 分管领导 │                             │
│  │  (自动)  │   │ (条件1) │   │ (条件2) │   │ (条件3) │                             │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘                             │
│                                                                                      │
│  条件说明：                                                                          │
│  - 条件1: 预估金额 ≥ 10万                                                            │
│  - 条件2: 预估金额 ≥ 50万                                                            │
│  - 条件3: 预估金额 ≥ 200万                                                           │
│                                                                                      │
│  ──────────────────────────────────────────────────────────────                     │
│                                                                                      │
│  【合规风险类型】                                                                     │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐               │
│  │ 提交人   │──►│合规专员  │──►│合规主管  │──►│ 分管领导 │──►│ 总经理   │               │
│  │  (自动)  │   │ (必审)  │   │ (条件1) │   │ (条件2) │   │ (条件3) │               │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘               │
│                                                                                      │
│  条件说明：                                                                          │
│  - 条件1: 风险等级 ≥ 中                                                              │
│  - 条件2: 风险等级 = 高                                                              │
│  - 条件3: 风险等级 = 极高                                                            │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

#### 3.3.2 问题反馈处理流程

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            问题反馈处理流程                                           │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐               │
│  │ 提交人   │──►│ 问题分派 │──►│ 问题处理 │──►│ 处理审核 │──►│ 提交人   │               │
│  │ 提交问题 │   │ (管理员) │   │ (被指派人)│   │ (主管)  │   │ 确认关闭 │               │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘               │
│                   │                                                              │
│                   ▼                                                              │
│              ┌─────────┐                                                         │
│              │ 转交其他 │                                                         │
│              │ 部门/人员 │                                                         │
│              └─────────┘                                                         │
│                                                                                      │
│  流程说明：                                                                          │
│  1. 问题提交后进入"待分派"状态                                                     │
│  2. 管理员根据问题类型分派给处理人/部门                                             │
│  3. 处理人接收后进行问题处理                                                       │
│  4. 处理完成后提交主管审核                                                         │
│  5. 审核通过后反馈给提交人确认                                                     │
│  6. 提交人确认或超时自动关闭                                                       │
│                                                                                      │
│  特殊情况：                                                                          │
│  - 无法处理时可申请转交其他部门                                                    │
│  - 审核不通过退回重新处理                                                          │
│  - 提交人不满意可重新打开                                                          │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

#### 3.3.3 资源协调审批流

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           资源协调审批流程配置                                        │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  【算力资源】                                                                         │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐                             │
│  │ 提交人   │──►│技术主管  │──►│资源管理员│──►│ 分管领导 │                             │
│  │  (自动)  │   │ (条件1) │   │ (条件2) │   │ (条件3) │                             │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘                             │
│                                                                                      │
│  条件说明：                                                                          │
│  - 条件1: 申请额度 ≥ 100 GPU小时                                                    │
│  - 条件2: 申请额度 ≥ 500 GPU小时 或 跨部门申请                                      │
│  - 条件3: 申请额度 ≥ 2000 GPU小时                                                   │
│                                                                                      │
│  ──────────────────────────────────────────────────────────────                     │
│                                                                                      │
│  【人力资源】                                                                         │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐               │
│  │ 提交人   │──►│部门经理  │──►│  HR部门  │──►│资源管理员│──►│ 分管领导 │               │
│  │  (自动)  │   │ (条件1) │   │ (条件2) │   │ (条件3) │   │ (条件4) │               │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘               │
│                                                                                      │
│  条件说明：                                                                          │
│  - 条件1: 申请额度 ≥ 10人天                                                          │
│  - 条件2: 申请额度 ≥ 30人天                                                          │
│  - 条件3: 申请额度 ≥ 90人天 或 跨部门申请                                           │
│  - 条件4: 申请额度 ≥ 180人天                                                         │
│                                                                                      │
│  ──────────────────────────────────────────────────────────────                     │
│                                                                                      │
│  【预算资源】                                                                         │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐               │
│  │ 提交人   │──►│部门经理  │──►│ 财务部门 │──►│ 财务总监 │──►│ 总经理   │               │
│  │  (自动)  │   │ (条件1) │   │ (条件2) │   │ (条件3) │   │ (条件4) │               │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘               │
│                                                                                      │
│  条件说明：                                                                          │
│  - 条件1: 申请额度 ≥ 5万元                                                           │
│  - 条件2: 申请额度 ≥ 20万元                                                          │
│  - 条件3: 申请额度 ≥ 100万元                                                         │
│  - 条件4: 申请额度 ≥ 500万元                                                         │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### 3.4 状态变更事件日志

| 事件类型 | 事件代码 | 触发时机 | 业务处理 | 通知对象 |
|----------|----------|----------|----------|----------|
| 事项提交 | EVT_SUBMIT | 从草稿提交 | 启动审批流 | 第一审批人 |
| 审批通过 | EVT_APPROVE | 审批人通过 | 推进下一节点 | 下一审批人 |
| 审批驳回 | EVT_REJECT | 审批人驳回 | 结束流程 | 提交人 |
| 事项转办 | EVT_TRANSFER | 审批人转办 | 更换处理人 | 新审批人 |
| 事项加签 | EVT_ADDSIGN | 审批人加签 | 插入审批节点 | 被加签人 |
| 事项撤回 | EVT_CANCEL | 提交人撤回 | 终止流程 | 当前审批人 |
| 重新提交 | EVT_RESUBMIT | 驳回后重提 | 重启审批流 | 第一审批人 |
| 流程完成 | EVT_COMPLETE | 最终节点通过 | 归档处理 | 相关人员 |
| 超时提醒 | EVT_TIMEOUT | 审批超期 | 发送催办 | 当前审批人+主管 |
| 自动关闭 | EVT_AUTOCLOSE | 反馈确认超时 | 自动归档 | 提交人 |

---

## 四、权限规则定义

### 4.1 角色定义

| 角色编码 | 角色名称 | 角色描述 | 适用范围 |
|----------|----------|----------|----------|
| ROLE_SUBMITTER | 事项提交人 | 提交各类提示事项 | 全员 |
| ROLE_DEPT_LEAD | 部门负责人 | 审批本部门相关事项 | 各部门经理 |
| ROLE_MAJOR_AUDITOR | 重大事项审批人 | 审批重大事项请示 | 战略/财务/合规负责人 |
| ROLE_ISSUE_MANAGER | 问题管理员 | 分派和处理问题反馈 | 业务支持中心 |
| ROLE_RESOURCE_ADMIN | 资源管理员 | 审批和分配资源 | 资源管理部门 |
| ROLE_FINANCE_AUDITOR | 财务审批人 | 审批涉及资金事项 | 财务部门 |
| ROLE_COMPLIANCE | 合规专员 | 审批合规风险事项 | 合规部门 |
| ROLE_HR | HR专员 | 审批人力资源协调 | HR部门 |
| ROLE_DIVISION_LEAD | 分管领导 | 审批重大事项 | 各业务线VP |
| ROLE_CEO | 总经理 | 最高审批权限 | 总经理 |
| ROLE_SYSTEM_ADMIN | 系统管理员 | 系统配置和管理 | IT管理员 |
| ROLE_VIEWER | 查看者 | 只读查看权限 | 按需分配 |

### 4.2 功能权限矩阵

| 功能模块 | 功能点 | 提交人 | 部门负责人 | 问题管理员 | 资源管理员 | 财务审批 | 合规专员 | 分管领导 | 总经理 | 系统管理员 |
|----------|--------|--------|------------|------------|------------|----------|----------|----------|--------|------------|
| **事项管理** |||||||||
| | 创建事项 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| | 编辑草稿 | ✓(本人) | - | - | - | - | - | - | - | ✓ |
| | 删除草稿 | ✓(本人) | - | - | - | - | - | - | - | ✓ |
| | 查看列表 | ✓(本部门) | ✓(本部门) | ✓(全部) | ✓(全部) | ✓(相关) | ✓(相关) | ✓(分管) | ✓(全部) | ✓(全部) |
| | 查看详情 | ✓(相关) | ✓(本部门) | ✓(全部) | ✓(全部) | ✓(相关) | ✓(相关) | ✓(分管) | ✓(全部) | ✓(全部) |
| **审批操作** |||||||||
| | 提交审批 | ✓(本人) | - | - | - | - | - | - | - | ✓ |
| | 审批通过 | - | ✓(相关) | ✓(相关) | ✓(相关) | ✓(相关) | ✓(相关) | ✓(相关) | ✓ | ✓ |
| | 审批驳回 | - | ✓(相关) | ✓(相关) | ✓(相关) | ✓(相关) | ✓(相关) | ✓(相关) | ✓ | ✓ |
| | 转办 | - | ✓(相关) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| | 加签 | - | ✓(相关) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| | 撤回 | ✓(本人) | - | - | - | - | - | - | - | ✓ |
| | 重新提交 | ✓(本人) | - | - | - | - | - | - | - | ✓ |
| **问题反馈** |||||||||
| | 分派问题 | - | - | ✓ | - | - | - | - | - | ✓ |
| | 处理问题 | - | - | ✓(被指) | - | - | - | - | - | ✓ |
| | 转交部门 | - | - | ✓ | - | - | - | - | - | ✓ |
| | 关闭问题 | - | - | ✓ | - | - | - | - | - | ✓ |
| | 确认解决 | ✓(本人) | - | - | - | - | - | - | - | ✓ |
| **资源协调** |||||||||
| | 资源分配 | - | - | - | ✓ | - | - | - | - | ✓ |
| | 资源调整 | - | - | - | ✓ | - | - | - | - | ✓ |
| | 归还确认 | - | - | - | ✓ | - | - | - | - | ✓ |
| **系统管理** |||||||||
| | 流程配置 | - | - | - | - | - | - | - | - | ✓ |
| | 权限配置 | - | - | - | - | - | - | - | - | ✓ |
| | 数据导出 | - | - | - | - | - | - | ✓ | ✓ | ✓ |
| | 统计分析 | - | ✓(本部门) | ✓ | ✓ | - | - | ✓(分管) | ✓ | ✓ |

### 4.3 数据权限规则

```sql
-- ========================================
-- 数据权限规则定义
-- ========================================

-- 规则1: 提交人只能看到本人提交的事项
RULE submitter_view {
    condition: submitter_id = CURRENT_USER_ID
    scope: [view]
}

-- 规则2: 部门负责人可查看本部门全部事项
RULE dept_lead_view {
    condition: dept_id IN (SELECT dept_id FROM sys_user_dept WHERE user_id = CURRENT_USER_ID)
    scope: [view]
}

-- 规则3: 问题管理员可查看全部问题反馈类型事项
RULE issue_manager_view {
    condition: alert_type = 2
    scope: [view, assign, close]
}

-- 规则4: 资源管理员可查看全部资源协调类型事项
RULE resource_admin_view {
    condition: alert_type = 3
    scope: [view, allocate, adjust]
}

-- 规则5: 审批人只能审批流转到自己节点的事项
RULE approver_action {
    condition: current_handler_id = CURRENT_USER_ID AND is_current = 1
    scope: [approve, reject, transfer, addsign]
}

-- 规则6: 分管领导可查看分管业务线的事项
RULE division_lead_view {
    condition: dept_id IN (
        SELECT dept_id FROM sys_dept_division 
        WHERE division_lead_id = CURRENT_USER_ID
    )
    scope: [view, approve]
}

-- 规则7: 财务审批人只能查看涉及金额的事项
RULE finance_view {
    condition: (
        alert_type = 1 AND (estimated_amount > 0 OR EXISTS (SELECT 1 FROM resource_coord WHERE resource_type = 3))
    )
    scope: [view, approve]
}

-- 规则8: 合规专员只能查看合规风险类型事项
RULE compliance_view {
    condition: alert_type = 1 AND request_type = 3
    scope: [view, approve]
}

-- 规则9: 系统管理员拥有全部数据权限
RULE admin_all {
    condition: 1 = 1
    scope: [all]
}
```

### 4.4 字段级权限控制

| 字段 | 提交人 | 审批人 | 管理员 | 查看者 |
|------|--------|--------|--------|--------|
| alert_no | R | R | R/W | R |
| alert_title | R/W | R | R/W | R |
| alert_content | R/W | R | R/W | R |
| submitter_id | R | R | R/W | R |
| submitter_name | R | R | R/W | R |
| current_status | R | R | R/W | R |
| current_handler_id | R | R | R/W | - |
| approval_comment | - | R/W | R/W | - |
| estimated_amount (重大事项) | R/W | R | R/W | R* |
| risk_desc (重大事项) | R/W | R | R/W | - |
| resolve_result (问题反馈) | R | R/W | R/W | R |
| resource_quota (资源协调) | R/W | R | R/W | - |
| actual_allocation (资源协调) | R | R/W | R/W | - |

> R: 只读, R/W: 读写, -: 不可见  
> R*: 脱敏显示（如：显示为"***万元"）

### 4.5 审批权限校验逻辑

```python
# 审批权限校验伪代码
def check_approval_permission(alert_id, user_id, action_type):
    # 1. 获取事项信息
    alert = get_alert_by_id(alert_id)
    
    # 2. 检查事项状态
    if alert.current_status not in [1, 2]:  # 待审批或审批中
        return False, "事项不在审批状态"
    
    # 3. 检查是否是当前处理人
    if alert.current_handler_id != user_id:
        # 检查是否有代理权限
        if not has_delegate_permission(alert.current_handler_id, user_id):
            return False, "非当前处理人，无审批权限"
    
    # 4. 检查操作类型权限
    user_roles = get_user_roles(user_id)
    if action_type == "approve" and not has_role(user_roles, "ROLE_APPROVER"):
        return False, "无审批权限"
    if action_type == "transfer" and not has_role(user_roles, "ROLE_TRANSFER"):
        return False, "无转办权限"
    
    # 5. 特殊事项类型权限检查
    if alert.alert_type == 1:  # 重大事项请示
        if not check_major_request_permission(alert, user_id, user_roles):
            return False, "无重大事项审批权限"
    elif alert.alert_type == 2:  # 问题反馈
        if not check_issue_feedback_permission(alert, user_id, user_roles):
            return False, "无问题处理权限"
    elif alert.alert_type == 3:  # 资源协调
        if not check_resource_coord_permission(alert, user_id, user_roles):
            return False, "无资源审批权限"
    
    return True, "权限校验通过"
```

---

## 五、数据字典

### 5.1 枚举值定义

#### 事项类型 (alert_type)
| 值 | 名称 | 说明 |
|----|------|------|
| 1 | 重大事项请示 | 战略客户政策、资源投入、合规风险等重大决策事项 |
| 2 | 问题反馈 | 产品、流程、系统等各类问题反馈 |
| 3 | 资源协调 | 算力、人力、预算等资源申请协调 |

#### 事项状态 (current_status)
| 值 | 名称 | 说明 |
|----|------|------|
| 0 | 草稿 | 已创建但未提交 |
| 1 | 待审批 | 已提交等待审批 |
| 2 | 审批中 | 正在审批流程中 |
| 3 | 已通过 | 审批已通过 |
| 4 | 已驳回 | 审批被驳回 |
| 5 | 已撤销 | 提交人主动撤回 |
| 6 | 已完成 | 事项已处理完成并归档 |

#### 请示类型 (request_type)
| 值 | 名称 | 说明 |
|----|------|------|
| 1 | 战略客户政策 | 针对战略客户的特殊政策申请 |
| 2 | 资源投入 | 项目或业务资源投入申请 |
| 3 | 合规风险 | 合规相关风险评估和决策 |

#### 反馈类型 (feedback_type)
| 值 | 名称 | 说明 |
|----|------|------|
| 1 | 产品问题 | 产品功能缺陷或改进建议 |
| 2 | 流程问题 | 业务流程优化或阻塞 |
| 3 | 系统问题 | 系统BUG或性能问题 |
| 4 | 协作问题 | 部门间协作问题 |
| 5 | 其他 | 其他类型问题 |

#### 资源类型 (resource_type)
| 值 | 名称 | 单位 | 说明 |
|----|------|------|------|
| 1 | 算力 | GPU小时 | 计算资源 |
| 2 | 人力 | 人天 | 人力资源 |
| 3 | 预算 | 万元 | 资金预算 |

#### 优先级 (priority)
| 值 | 名称 | 颜色标识 | 响应时限 |
|----|------|----------|----------|
| 1 | 紧急 | 红色 | 2小时内 |
| 2 | 高 | 橙色 | 24小时内 |
| 3 | 中 | 黄色 | 3个工作日内 |
| 4 | 低 | 绿色 | 7个工作日内 |

#### 风险等级 (risk_level)
| 值 | 名称 | 说明 |
|----|------|------|
| 1 | 极高 | 可能导致重大损失或违规 |
| 2 | 高 | 可能导致较大影响 |
| 3 | 中 | 有一定影响可控 |
| 4 | 低 | 影响较小 |

#### 操作类型 (action_type)
| 值 | 名称 | 说明 |
|----|------|------|
| 1 | 提交 | 提交事项进入审批 |
| 2 | 通过 | 审批通过 |
| 3 | 驳回 | 审批驳回 |
| 4 | 转办 | 转给其他审批人 |
| 5 | 加签 | 增加审批节点 |
| 6 | 撤回 | 撤回事项 |

---

## 六、扩展设计建议

### 6.1 未来扩展点

| 扩展项 | 描述 | 优先级 |
|--------|------|--------|
| 工作流引擎集成 | 接入BPMN工作流引擎，支持可视化流程配置 | 高 |
| 智能分派 | 基于问题类型和内容自动分派给最合适处理人 | 中 |
| SLA监控 | 增加服务级别协议监控和预警 | 高 |
| 数据分析看板 | 提供多维度的数据分析和可视化看板 | 中 |
| 移动端适配 | 完善的移动端审批和处理体验 | 高 |
| 消息模板配置 | 可配置的通知消息模板 | 低 |
| 批量操作 | 支持批量审批、批量导出 | 中 |
| 历史归档 | 自动归档机制和历史数据迁移 | 低 |

### 6.2 性能优化建议

1. **索引优化**: 高频查询字段建立联合索引
2. **分表策略**: 按年份对历史数据进行分表
3. **缓存策略**: 审批流程配置、用户权限数据缓存
4. **异步处理**: 通知发送、日志记录异步化
5. **读写分离**: 查询操作走从库

---

## 附录

### A. 建表SQL汇总（MySQL示例）

```sql
-- 提示事项主表
CREATE TABLE alert_management (
    alert_id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '提示事项ID',
    alert_no VARCHAR(32) NOT NULL UNIQUE COMMENT '事项编号',
    alert_type TINYINT NOT NULL COMMENT '事项类型：1-重大事项请示 2-问题反馈 3-资源协调',
    alert_title VARCHAR(200) NOT NULL COMMENT '事项标题',
    alert_content TEXT NOT NULL COMMENT '事项详细内容',
    submitter_id BIGINT NOT NULL COMMENT '提交人ID',
    submitter_name VARCHAR(50) NOT NULL COMMENT '提交人姓名',
    dept_id BIGINT NOT NULL COMMENT '所属部门ID',
    dept_name VARCHAR(100) NOT NULL COMMENT '部门名称',
    current_status TINYINT NOT NULL DEFAULT 1 COMMENT '当前状态：0-草稿 1-待审批 2-审批中 3-已通过 4-已驳回 5-已撤销 6-已完成',
    current_handler_id BIGINT COMMENT '当前处理人ID',
    priority TINYINT NOT NULL DEFAULT 2 COMMENT '优先级：1-紧急 2-高 3-中 4-低',
    submit_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '提交时间',
    deadline DATETIME COMMENT '截止时间',
    complete_time DATETIME COMMENT '完成时间',
    is_urgent TINYINT NOT NULL DEFAULT 0 COMMENT '是否加急：0-否 1-是',
    source_channel TINYINT NOT NULL DEFAULT 1 COMMENT '来源渠道：1-PC端 2-移动端 3-API',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by BIGINT NOT NULL COMMENT '创建人ID',
    updated_by BIGINT COMMENT '更新人ID',
    is_deleted TINYINT NOT NULL DEFAULT 0 COMMENT '逻辑删除标记：0-正常 1-已删除',
    INDEX idx_alert_type (alert_type),
    INDEX idx_current_status (current_status),
    INDEX idx_submitter_id (submitter_id),
    INDEX idx_dept_id (dept_id),
    INDEX idx_submit_time (submit_time),
    INDEX idx_priority (priority),
    INDEX idx_current_handler (current_handler_id),
    INDEX idx_alert_no (alert_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='提示事项主表';

-- [其他表SQL省略，按上述字段定义创建]
```

---

**文档结束**
