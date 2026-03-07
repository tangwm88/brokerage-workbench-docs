# 业务支持中心 - 业务组织模块数据建模方案

## 版本信息
- 版本：v1.0
- 创建日期：2026-03-07
- 模块名称：业务组织模块
- 所属系统：业务支持中心

---

## 一、实体关系图（ER图文字描述）

### 1.1 核心实体关系概览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           业务组织模块实体关系图                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐       ┌──────────────┐       ┌──────────────┐            │
│  │   客户信息    │◄─────►│   客户资质   │       │   跟进记录   │            │
│  │   Customer   │  1:N  │ Qualification│       │  FollowUp    │            │
│  └──────┬───────┘       └──────────────┘       └──────┬───────┘            │
│         │                                             │                     │
│         │ 1:1                                         │                     │
│         ▼                                             │                     │
│  ┌──────────────┐       ┌──────────────┐             │                     │
│  │   开户申请    │◄─────►│   审核任务   │◄────────────┘                     │
│  │AccountOpening│  1:N  │ AuditTask    │  跟进关联                              │
│  └──────┬───────┘       └──────┬───────┘                                   │
│         │                      │                                            │
│         │ 1:N                  │ N:1                                        │
│         ▼                      ▼                                            │
│  ┌──────────────┐       ┌──────────────┐                                   │
│  │  系统开通记录  │       │   审核人员   │                                   │
│  │SystemAccess  │       │  Auditor     │                                   │
│  └──────┬───────┘       └──────────────┘                                   │
│         │                                                                   │
│         │ N:1                                                               │
│         ▼                                                                   │
│  ┌──────────────┐       ┌──────────────┐       ┌──────────────┐            │
│  │   系统类型    │       │  分支机构    │◄─────►│   业绩统计   │            │
│  │ SystemType   │       │  Branch      │  1:N  │  Performance │            │
│  └──────────────┘       └──────┬───────┘       └──────────────┘            │
│                                │                                            │
│                                │ 1:N                                        │
│                                ▼                                            │
│                         ┌──────────────┐                                   │
│                         │  业务进展记录  │                                   │
│                         │ BizProgress  │                                   │
│                         └──────────────┘                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 实体关系详细说明

| 主实体 | 关系 | 从实体 | 关系类型 | 说明 |
|--------|------|--------|----------|------|
| 客户信息(Customer) | 1:N | 客户资质(Qualification) | 一对多 | 一个客户可有多条资质记录 |
| 客户信息(Customer) | 1:1 | 开户申请(AccountOpening) | 一对一 | 一个客户对应一个开户申请 |
| 客户信息(Customer) | 1:N | 跟进记录(FollowUp) | 一对多 | 一个客户可有多条跟进记录 |
| 开户申请(AccountOpening) | 1:N | 审核任务(AuditTask) | 一对多 | 一个开户申请可产生多个审核任务 |
| 审核任务(AuditTask) | N:1 | 审核人员(Auditor) | 多对一 | 多个任务可分配给同一审核人员 |
| 开户申请(AccountOpening) | 1:N | 系统开通记录(SystemAccess) | 一对多 | 一个开户可申请多个系统 |
| 系统开通记录(SystemAccess) | N:1 | 系统类型(SystemType) | 多对一 | 多个开通记录对应同一系统类型 |
| 分支机构(Branch) | 1:N | 业务进展记录(BizProgress) | 一对多 | 一个机构有多条进展记录 |
| 分支机构(Branch) | 1:N | 业绩统计(Performance) | 一对多 | 一个机构有多期业绩统计 |
| 分支机构(Branch) | 1:N | 客户信息(Customer) | 一对多 | 一个机构服务多个客户 |

### 1.3 关联关系属性

```
┌────────────────────────────────────────────────────────┐
│                    关联关系详情                         │
├────────────────────────────────────────────────────────┤
│                                                        │
│  【客户-资质】关联                                     │
│  ├── 关联ID: qualification_id                          │
│  ├── 资质类型: qual_type (营业执照/金融牌照/其他)       │
│  └── 有效期: valid_until                               │
│                                                        │
│  【开户申请-审核任务】关联                              │
│  ├── 任务ID: task_id                                   │
│  ├── 审核类型: audit_type (资料审核/实地审核/风控审核)   │
│  └── 优先级: priority (高/中/低)                       │
│                                                        │
│  【开通记录-系统类型】关联                              │
│  ├── 系统编码: system_code                             │
│  ├── 开通版本: version                                 │
│  └── 授权模块: auth_modules                            │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## 二、数据表结构设计

### 2.1 客户信息表 (biz_customer)

| 字段名 | 数据类型 | 长度/精度 | 是否为空 | 默认值 | 约束 | 说明 |
|--------|----------|-----------|----------|--------|------|------|
| customer_id | VARCHAR | 32 | 否 | - | PK | 客户唯一标识 |
| customer_code | VARCHAR | 64 | 否 | - | UK | 客户编码(业务号) |
| customer_name | VARCHAR | 128 | 否 | - | - | 客户名称 |
| customer_short | VARCHAR | 64 | 是 | NULL | - | 客户简称 |
| customer_type | TINYINT | 1 | 否 | 1 | - | 客户类型:1-机构,2-个人 |
| industry_code | VARCHAR | 32 | 是 | NULL | FK | 所属行业编码 |
| region_code | VARCHAR | 32 | 是 | NULL | FK | 地区编码 |
| contact_name | VARCHAR | 64 | 是 | NULL | - | 联系人姓名 |
| contact_phone | VARCHAR | 32 | 是 | NULL | - | 联系人电话 |
| contact_email | VARCHAR | 128 | 是 | NULL | - | 联系人邮箱 |
| address | VARCHAR | 256 | 是 | NULL | - | 详细地址 |
| sales_manager_id | VARCHAR | 32 | 是 | NULL | FK | 销售经理ID |
| branch_id | VARCHAR | 32 | 是 | NULL | FK | 所属分支机构ID |
| source_channel | VARCHAR | 32 | 是 | NULL | - | 客户来源渠道 |
| status | TINYINT | 1 | 否 | 0 | - | 状态:0-待审核,1-已确认,2-已分配,9-无效 |
| audit_status | TINYINT | 1 | 否 | 0 | - | 审核状态:0-未审核,1-审核中,2-已通过,3-已驳回 |
| assign_status | TINYINT | 1 | 否 | 0 | - | 分配状态:0-未分配,1-已分配 |
| assign_time | DATETIME | - | 是 | NULL | - | 分配时间 |
| assignee_id | VARCHAR | 32 | 是 | NULL | FK | 被分配人ID |
| create_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 创建时间 |
| update_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 更新时间 |
| create_by | VARCHAR | 32 | 否 | - | - | 创建人ID |
| update_by | VARCHAR | 32 | 否 | - | - | 更新人ID |
| remark | VARCHAR | 512 | 是 | NULL | - | 备注 |
| deleted | TINYINT | 1 | 否 | 0 | - | 删除标记:0-正常,1-已删除 |

**索引设计：**
```sql
CREATE UNIQUE INDEX uk_customer_code ON biz_customer(customer_code);
CREATE INDEX idx_customer_name ON biz_customer(customer_name);
CREATE INDEX idx_customer_status ON biz_customer(status);
CREATE INDEX idx_customer_branch ON biz_customer(branch_id);
CREATE INDEX idx_customer_sales ON biz_customer(sales_manager_id);
CREATE INDEX idx_customer_create_time ON biz_customer(create_time);
```

---

### 2.2 客户资质表 (biz_customer_qualification)

| 字段名 | 数据类型 | 长度/精度 | 是否为空 | 默认值 | 约束 | 说明 |
|--------|----------|-----------|----------|--------|------|------|
| qual_id | VARCHAR | 32 | 否 | - | PK | 资质ID |
| customer_id | VARCHAR | 32 | 否 | - | FK | 客户ID |
| qual_type | TINYINT | 1 | 否 | - | - | 资质类型:1-营业执照,2-金融牌照,3-税务登记,4-其他 |
| qual_name | VARCHAR | 128 | 否 | - | - | 资质名称 |
| qual_code | VARCHAR | 64 | 是 | NULL | - | 资质编号 |
| issue_org | VARCHAR | 128 | 是 | NULL | - | 发证机构 |
| issue_date | DATE | - | 是 | NULL | - | 发证日期 |
| valid_until | DATE | - | 是 | NULL | - | 有效期至 |
| file_url | VARCHAR | 512 | 是 | NULL | - | 资质文件URL |
| file_hash | VARCHAR | 64 | 是 | NULL | - | 文件哈希值 |
| verify_status | TINYINT | 1 | 否 | 0 | - | 核验状态:0-未核验,1-核验通过,2-核验不通过 |
| verify_time | DATETIME | - | 是 | NULL | - | 核验时间 |
| verify_by | VARCHAR | 32 | 是 | NULL | - | 核验人ID |
| verify_remark | VARCHAR | 256 | 是 | NULL | - | 核验备注 |
| create_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 创建时间 |
| update_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 更新时间 |
| deleted | TINYINT | 1 | 否 | 0 | - | 删除标记 |

**索引设计：**
```sql
CREATE INDEX idx_qual_customer ON biz_customer_qualification(customer_id);
CREATE INDEX idx_qual_type ON biz_customer_qualification(qual_type);
CREATE INDEX idx_qual_verify ON biz_customer_qualification(verify_status);
```

---

### 2.3 跟进记录表 (biz_follow_up)

| 字段名 | 数据类型 | 长度/精度 | 是否为空 | 默认值 | 约束 | 说明 |
|--------|----------|-----------|----------|--------|------|------|
| follow_id | VARCHAR | 32 | 否 | - | PK | 跟进ID |
| customer_id | VARCHAR | 32 | 否 | - | FK | 客户ID |
| follow_type | TINYINT | 1 | 否 | - | - | 跟进类型:1-电话,2-邮件,3-拜访,4-会议,5-其他 |
| follow_content | TEXT | - | 否 | - | - | 跟进内容 |
| follow_result | TINYINT | 1 | 是 | NULL | - | 跟进结果:1-有意向,2-需跟进,3-无意向,4-已签约 |
| next_follow_time | DATETIME | - | 是 | NULL | - | 下次跟进时间 |
| next_follow_content | VARCHAR | 512 | 是 | NULL | - | 下次跟进计划 |
| attachment_urls | VARCHAR | 1024 | 是 | NULL | - | 附件URL列表(JSON) |
| follow_by | VARCHAR | 32 | 否 | - | FK | 跟进人ID |
| follow_time | DATETIME | - | 否 | - | - | 跟进时间 |
| create_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 创建时间 |
| update_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 更新时间 |
| deleted | TINYINT | 1 | 否 | 0 | - | 删除标记 |

**索引设计：**
```sql
CREATE INDEX idx_follow_customer ON biz_follow_up(customer_id);
CREATE INDEX idx_follow_time ON biz_follow_up(follow_time);
CREATE INDEX idx_follow_by ON biz_follow_up(follow_by);
CREATE INDEX idx_follow_result ON biz_follow_up(follow_result);
```

---

### 2.4 开户申请表 (biz_account_opening)

| 字段名 | 数据类型 | 长度/精度 | 是否为空 | 默认值 | 约束 | 说明 |
|--------|----------|-----------|----------|--------|------|------|
| opening_id | VARCHAR | 32 | 否 | - | PK | 开户申请ID |
| customer_id | VARCHAR | 32 | 否 | - | FK | 客户ID |
| opening_code | VARCHAR | 64 | 否 | - | UK | 开户申请编号 |
| apply_type | TINYINT | 1 | 否 | - | - | 申请类型:1-新开户,2-增开,3-变更 |
| business_type | VARCHAR | 32 | 是 | NULL | - | 业务类型编码 |
| risk_level | TINYINT | 1 | 是 | NULL | - | 风险等级:1-低,2-中,3-高 |
| status | TINYINT | 1 | 否 | 0 | - | 状态:0-待提交,1-审核中,2-已通过,3-已驳回,4-已撤销 |
| current_stage | VARCHAR | 32 | 是 | NULL | - | 当前审核阶段 |
| submit_time | DATETIME | - | 是 | NULL | - | 提交时间 |
| submit_by | VARCHAR | 32 | 是 | NULL | - | 提交人ID |
| audit_complete_time | DATETIME | - | 是 | NULL | - | 审核完成时间 |
| reject_reason | VARCHAR | 512 | 是 | NULL | - | 驳回原因 |
| remark | VARCHAR | 512 | 是 | NULL | - | 备注 |
| create_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 创建时间 |
| update_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 更新时间 |
| create_by | VARCHAR | 32 | 否 | - | - | 创建人ID |
| update_by | VARCHAR | 32 | 否 | - | - | 更新人ID |
| deleted | TINYINT | 1 | 否 | 0 | - | 删除标记 |

**索引设计：**
```sql
CREATE UNIQUE INDEX uk_opening_code ON biz_account_opening(opening_code);
CREATE INDEX idx_opening_customer ON biz_account_opening(customer_id);
CREATE INDEX idx_opening_status ON biz_account_opening(status);
CREATE INDEX idx_opening_submit ON biz_account_opening(submit_time);
```

---

### 2.5 审核任务表 (biz_audit_task)

| 字段名 | 数据类型 | 长度/精度 | 是否为空 | 默认值 | 约束 | 说明 |
|--------|----------|-----------|----------|--------|------|------|
| task_id | VARCHAR | 32 | 否 | - | PK | 任务ID |
| opening_id | VARCHAR | 32 | 否 | - | FK | 开户申请ID |
| task_code | VARCHAR | 64 | 否 | - | UK | 任务编号 |
| audit_type | TINYINT | 1 | 否 | - | - | 审核类型:1-资料审核,2-实地审核,3-风控审核,4-合规审核 |
| stage_order | TINYINT | 2 | 否 | - | - | 审核阶段顺序 |
| priority | TINYINT | 1 | 否 | 2 | - | 优先级:1-高,2-中,3-低 |
| status | TINYINT | 1 | 否 | 0 | - | 状态:0-待分配,1-已分配,2-审核中,3-已通过,4-已驳回 |
| assignee_id | VARCHAR | 32 | 是 | NULL | FK | 审核人员ID |
| assign_time | DATETIME | - | 是 | NULL | - | 分配时间 |
| start_time | DATETIME | - | 是 | NULL | - | 开始审核时间 |
| complete_time | DATETIME | - | 是 | NULL | - | 完成时间 |
| due_date | DATE | - | 是 | NULL | - | 截止日期 |
| audit_opinion | TEXT | - | 是 | NULL | - | 审核意见 |
| audit_result | TINYINT | 1 | 是 | NULL | - | 审核结果:1-通过,2-驳回,3-退回补充 |
| reject_reason | VARCHAR | 512 | 是 | NULL | - | 驳回原因 |
| attachment_urls | VARCHAR | 1024 | 是 | NULL | - | 附件列表(JSON) |
| create_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 创建时间 |
| update_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 更新时间 |
| create_by | VARCHAR | 32 | 否 | - | - | 创建人ID |
| deleted | TINYINT | 1 | 否 | 0 | - | 删除标记 |

**索引设计：**
```sql
CREATE UNIQUE INDEX uk_task_code ON biz_audit_task(task_code);
CREATE INDEX idx_task_opening ON biz_audit_task(opening_id);
CREATE INDEX idx_task_status ON biz_audit_task(status);
CREATE INDEX idx_task_assignee ON biz_audit_task(assignee_id);
CREATE INDEX idx_task_due ON biz_audit_task(due_date);
```

---

### 2.6 审核历史记录表 (biz_audit_history)

| 字段名 | 数据类型 | 长度/精度 | 是否为空 | 默认值 | 约束 | 说明 |
|--------|----------|-----------|----------|--------|------|------|
| history_id | VARCHAR | 32 | 否 | - | PK | 历史记录ID |
| task_id | VARCHAR | 32 | 否 | - | FK | 任务ID |
| opening_id | VARCHAR | 32 | 否 | - | FK | 开户申请ID |
| action_type | TINYINT | 1 | 否 | - | - | 操作类型:1-分配,2-开始,3-通过,4-驳回,5-转交 |
| from_status | TINYINT | 1 | 是 | NULL | - | 原状态 |
| to_status | TINYINT | 1 | 否 | - | - | 新状态 |
| operator_id | VARCHAR | 32 | 否 | - | FK | 操作人ID |
| operate_time | DATETIME | - | 否 | - | - | 操作时间 |
| operate_ip | VARCHAR | 64 | 是 | NULL | - | 操作IP |
| remark | VARCHAR | 512 | 是 | NULL | - | 备注 |
| create_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 创建时间 |

**索引设计：**
```sql
CREATE INDEX idx_hist_task ON biz_audit_history(task_id);
CREATE INDEX idx_hist_opening ON biz_audit_history(opening_id);
CREATE INDEX idx_hist_time ON biz_audit_history(operate_time);
```

---

### 2.7 分支机构表 (biz_branch)

| 字段名 | 数据类型 | 长度/精度 | 是否为空 | 默认值 | 约束 | 说明 |
|--------|----------|-----------|----------|--------|------|------|
| branch_id | VARCHAR | 32 | 否 | - | PK | 机构ID |
| branch_code | VARCHAR | 64 | 否 | - | UK | 机构编码 |
| branch_name | VARCHAR | 128 | 否 | - | - | 机构名称 |
| branch_short | VARCHAR | 64 | 是 | NULL | - | 机构简称 |
| parent_id | VARCHAR | 32 | 是 | NULL | FK | 上级机构ID |
| branch_level | TINYINT | 1 | 否 | 1 | - | 机构层级:1-总部,2-分公司,3-营业部 |
| region_code | VARCHAR | 32 | 是 | NULL | - | 地区编码 |
| address | VARCHAR | 256 | 是 | NULL | - | 详细地址 |
| manager_id | VARCHAR | 32 | 是 | NULL | FK | 负责人ID |
| contact_phone | VARCHAR | 32 | 是 | NULL | - | 联系电话 |
| status | TINYINT | 1 | 否 | 1 | - | 状态:0-停用,1-正常 |
| open_date | DATE | - | 是 | NULL | - | 开业日期 |
| close_date | DATE | - | 是 | NULL | - | 停业日期 |
| sort_order | INT | - | 否 | 0 | - | 排序号 |
| create_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 创建时间 |
| update_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 更新时间 |
| create_by | VARCHAR | 32 | 否 | - | - | 创建人ID |
| update_by | VARCHAR | 32 | 否 | - | - | 更新人ID |
| deleted | TINYINT | 1 | 否 | 0 | - | 删除标记 |

**索引设计：**
```sql
CREATE UNIQUE INDEX uk_branch_code ON biz_branch(branch_code);
CREATE INDEX idx_branch_parent ON biz_branch(parent_id);
CREATE INDEX idx_branch_region ON biz_branch(region_code);
CREATE INDEX idx_branch_status ON biz_branch(status);
```

---

### 2.8 业务进展记录表 (biz_progress)

| 字段名 | 数据类型 | 长度/精度 | 是否为空 | 默认值 | 约束 | 说明 |
|--------|----------|-----------|----------|--------|------|------|
| progress_id | VARCHAR | 32 | 否 | - | PK | 进展ID |
| branch_id | VARCHAR | 32 | 否 | - | FK | 机构ID |
| customer_id | VARCHAR | 32 | 是 | NULL | FK | 客户ID |
| progress_type | TINYINT | 1 | 否 | - | - | 进展类型:1-新客开发,2-业务推进,3-问题解决,4-其他 |
| progress_title | VARCHAR | 128 | 否 | - | - | 进展标题 |
| progress_content | TEXT | - | 否 | - | - | 进展详情 |
| progress_stage | TINYINT | 1 | 是 | NULL | - | 业务阶段:1-意向,2-洽谈,3-签约,4-开户,5-正式合作 |
| expect_amount | DECIMAL | 18,2 | 是 | NULL | - | 预期金额 |
| actual_amount | DECIMAL | 18,2 | 是 | NULL | - | 实际金额 |
| progress_date | DATE | - | 否 | - | - | 进展日期 |
| recorder_id | VARCHAR | 32 | 否 | - | FK | 记录人ID |
| attachment_urls | VARCHAR | 1024 | 是 | NULL | - | 附件列表 |
| create_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 创建时间 |
| update_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 更新时间 |
| deleted | TINYINT | 1 | 否 | 0 | - | 删除标记 |

**索引设计：**
```sql
CREATE INDEX idx_progress_branch ON biz_progress(branch_id);
CREATE INDEX idx_progress_customer ON biz_progress(customer_id);
CREATE INDEX idx_progress_date ON biz_progress(progress_date);
CREATE INDEX idx_progress_type ON biz_progress(progress_type);
```

---

### 2.9 业绩统计表 (biz_performance)

| 字段名 | 数据类型 | 长度/精度 | 是否为空 | 默认值 | 约束 | 说明 |
|--------|----------|-----------|----------|--------|------|------|
| performance_id | VARCHAR | 32 | 否 | - | PK | 业绩ID |
| branch_id | VARCHAR | 32 | 否 | - | FK | 机构ID |
| stat_period | VARCHAR | 16 | 否 | - | - | 统计周期(YYYYMM) |
| period_type | TINYINT | 1 | 否 | 1 | - | 周期类型:1-月,2-季,3-年 |
| new_customer_count | INT | - | 否 | 0 | - | 新增客户数 |
| active_customer_count | INT | - | 否 | 0 | - | 活跃客户数 |
| opening_count | INT | - | 否 | 0 | - | 开户数 |
| business_amount | DECIMAL | 18,2 | 否 | 0.00 | - | 业务金额 |
| revenue_amount | DECIMAL | 18,2 | 否 | 0.00 | - | 收入金额 |
| completion_rate | DECIMAL | 5,2 | 是 | NULL | - | 目标完成率(%) |
| target_amount | DECIMAL | 18,2 | 是 | NULL | - | 目标金额 |
| ranking | INT | - | 是 | NULL | - | 业绩排名 |
| create_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 创建时间 |
| update_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 更新时间 |
| deleted | TINYINT | 1 | 否 | 0 | - | 删除标记 |

**索引设计：**
```sql
CREATE UNIQUE INDEX uk_performance_period ON biz_performance(branch_id, stat_period);
CREATE INDEX idx_perf_branch ON biz_performance(branch_id);
CREATE INDEX idx_perf_period ON biz_performance(stat_period);
```

---

### 2.10 系统类型表 (sys_system_type)

| 字段名 | 数据类型 | 长度/精度 | 是否为空 | 默认值 | 约束 | 说明 |
|--------|----------|-----------|----------|--------|------|------|
| system_id | VARCHAR | 32 | 否 | - | PK | 系统ID |
| system_code | VARCHAR | 64 | 否 | - | UK | 系统编码 |
| system_name | VARCHAR | 128 | 否 | - | - | 系统名称 |
| system_version | VARCHAR | 32 | 是 | NULL | - | 当前版本 |
| category | TINYINT | 1 | 否 | - | - | 系统分类:1-核心系统,2-业务系统,3-支撑系统 |
| description | VARCHAR | 512 | 是 | NULL | - | 系统描述 |
| modules | VARCHAR | 1024 | 是 | NULL | - | 功能模块配置(JSON) |
| status | TINYINT | 1 | 否 | 1 | - | 状态:0-停用,1-正常 |
| sort_order | INT | - | 否 | 0 | - | 排序号 |
| create_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 创建时间 |
| update_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 更新时间 |
| deleted | TINYINT | 1 | 否 | 0 | - | 删除标记 |

**索引设计：**
```sql
CREATE UNIQUE INDEX uk_system_code ON sys_system_type(system_code);
CREATE INDEX idx_system_category ON sys_system_type(category);
```

---

### 2.11 系统开通记录表 (biz_system_access)

| 字段名 | 数据类型 | 长度/精度 | 是否为空 | 默认值 | 约束 | 说明 |
|--------|----------|-----------|----------|--------|------|------|
| access_id | VARCHAR | 32 | 否 | - | PK | 开通记录ID |
| opening_id | VARCHAR | 32 | 否 | - | FK | 开户申请ID |
| system_id | VARCHAR | 32 | 否 | - | FK | 系统类型ID |
| customer_id | VARCHAR | 32 | 否 | - | FK | 客户ID |
| access_version | VARCHAR | 32 | 是 | NULL | - | 开通版本 |
| auth_modules | VARCHAR | 1024 | 是 | NULL | - | 授权模块(JSON) |
| access_status | TINYINT | 1 | 否 | 0 | - | 开通状态:0-待开通,1-开通中,2-已开通,3-开通失败,4-已停用 |
| apply_time | DATETIME | - | 是 | NULL | - | 申请开通时间 |
| open_time | DATETIME | - | 是 | NULL | - | 实际开通时间 |
| expire_date | DATE | - | 是 | NULL | - | 授权到期日 |
| admin_account | VARCHAR | 64 | 是 | NULL | - | 管理员账号 |
| access_url | VARCHAR | 256 | 是 | NULL | - | 访问地址 |
| create_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 创建时间 |
| update_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 更新时间 |
| create_by | VARCHAR | 32 | 否 | - | - | 创建人ID |
| update_by | VARCHAR | 32 | 否 | - | - | 更新人ID |
| deleted | TINYINT | 1 | 否 | 0 | - | 删除标记 |

**索引设计：**
```sql
CREATE INDEX idx_access_opening ON biz_system_access(opening_id);
CREATE INDEX idx_access_system ON biz_system_access(system_id);
CREATE INDEX idx_access_customer ON biz_system_access(customer_id);
CREATE INDEX idx_access_status ON biz_system_access(access_status);
```

---

### 2.12 系统反馈记录表 (biz_system_feedback)

| 字段名 | 数据类型 | 长度/精度 | 是否为空 | 默认值 | 约束 | 说明 |
|--------|----------|-----------|----------|--------|------|------|
| feedback_id | VARCHAR | 32 | 否 | - | PK | 反馈ID |
| access_id | VARCHAR | 32 | 否 | - | FK | 开通记录ID |
| customer_id | VARCHAR | 32 | 否 | - | FK | 客户ID |
| system_id | VARCHAR | 32 | 否 | - | FK | 系统ID |
| feedback_type | TINYINT | 1 | 否 | - | - | 反馈类型:1-功能建议,2-问题反馈,3-使用咨询,4-投诉 |
| priority | TINYINT | 1 | 否 | 2 | - | 优先级:1-紧急,2-一般,3-低 |
| feedback_title | VARCHAR | 128 | 否 | - | - | 反馈标题 |
| feedback_content | TEXT | - | 否 | - | - | 反馈内容 |
| contact_name | VARCHAR | 64 | 是 | NULL | - | 联系人 |
| contact_phone | VARCHAR | 32 | 是 | NULL | - | 联系电话 |
| status | TINYINT | 1 | 否 | 0 | - | 处理状态:0-待处理,1-处理中,2-已解决,3-已关闭 |
| handler_id | VARCHAR | 32 | 是 | NULL | FK | 处理人ID |
| handle_time | DATETIME | - | 是 | NULL | - | 处理时间 |
| handle_result | TEXT | - | 是 | NULL | - | 处理结果 |
| satisfaction | TINYINT | 1 | 是 | NULL | - | 满意度:1-5分 |
| attachment_urls | VARCHAR | 1024 | 是 | NULL | - | 附件列表 |
| create_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 创建时间 |
| update_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 更新时间 |
| create_by | VARCHAR | 32 | 否 | - | - | 创建人ID |
| deleted | TINYINT | 1 | 否 | 0 | - | 删除标记 |

**索引设计：**
```sql
CREATE INDEX idx_feedback_access ON biz_system_feedback(access_id);
CREATE INDEX idx_feedback_customer ON biz_system_feedback(customer_id);
CREATE INDEX idx_feedback_status ON biz_system_feedback(status);
CREATE INDEX idx_feedback_type ON biz_system_feedback(feedback_type);
CREATE INDEX idx_feedback_time ON biz_system_feedback(create_time);
```

---

### 2.13 枚举值定义表 (biz_enum_define)

| 字段名 | 数据类型 | 长度/精度 | 是否为空 | 默认值 | 约束 | 说明 |
|--------|----------|-----------|----------|--------|------|------|
| enum_id | VARCHAR | 32 | 否 | - | PK | 枚举ID |
| enum_type | VARCHAR | 64 | 否 | - | - | 枚举类型 |
| enum_code | VARCHAR | 32 | 否 | - | - | 枚举编码 |
| enum_name | VARCHAR | 64 | 否 | - | - | 枚举名称 |
| enum_value | INT | - | 否 | - | - | 枚举值 |
| sort_order | INT | - | 否 | 0 | - | 排序号 |
| status | TINYINT | 1 | 否 | 1 | - | 状态:0-停用,1-正常 |
| remark | VARCHAR | 256 | 是 | NULL | - | 备注 |
| create_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 创建时间 |
| update_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 更新时间 |

---

## 三、任务流转状态图

### 3.1 客户状态流转图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           客户状态流转图                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                           ┌──────────┐                                     │
│                           │   创建   │                                     │
│                           │ (INIT)   │                                     │
│                           └────┬─────┘                                     │
│                                │                                            │
│                                ▼                                            │
│                    ┌───────────────────────┐                               │
│                    │      待审核            │                               │
│              ┌────►│   (PENDING_AUDIT)     │◄────┐                        │
│              │     └───────────┬───────────┘     │                        │
│              │                 │                  │                        │
│        驳回/补充               │ 审核通过          │ 审核驳回                │
│              │                 ▼                  │                        │
│              │     ┌───────────────────────┐     │                        │
│              └─────┤      已确认            │     │                        │
│                    │   (CONFIRMED)         ├─────┘                        │
│                    └───────────┬───────────┘                               │
│                                │                                            │
│                                │ 分配跟进                                    │
│                                ▼                                            │
│                    ┌───────────────────────┐                               │
│                    │      已分配            │◄────────┐                    │
│              ┌────►│    (ASSIGNED)         │         │                    │
│              │     └───────────┬───────────┘         │                    │
│              │                 │                      │                    │
│              │         跟进转化                      │                    │
│              │                 │                      │ 重新分配            │
│              │                 ▼                      │                    │
│              │     ┌───────────────────────┐         │                    │
│              └─────┤      已转化            ├─────────┘                    │
│                    │  (CONVERTED)          │                               │
│                    └───────────┬───────────┘                               │
│                                │                                            │
│                                ▼                                            │
│                       ┌────────────────┐                                   │
│                       │     无效       │                                   │
│                       │  (INVALID)     │                                   │
│                       └────────────────┘                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 开户申请状态流转图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          开户申请状态流转图                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                       ┌────────────────┐                                   │
│                       │    草稿/待提交   │                                   │
│                       │   (DRAFT)      │                                   │
│                       └───────┬────────┘                                   │
│                               │                                            │
│                               │ 提交申请                                    │
│                               ▼                                            │
│ ┌──────────┐      ┌───────────────────────┐                               │
│ │   撤销   │◄─────┤       审核中          │                               │
│ │(REVOKED) │      │   (AUDITING)          │                               │
│ └──────────┘      └───────┬───────────────┘                               │
│                           │    ▲                                         │
│              ┌────────────┤    │                                         │
│              │            │    │ 退回补充                                  │
│         审核完成          │    │                                         │
│              │            ▼    │                                         │
│              │    ┌───────────────────────┐                               │
│              └───►│      补充资料         │                               │
│                   │  (SUPPLEMENT)         │                               │
│                   └───────────────────────┘                               │
│                                                                             │
│    ┌─────────────────────────────────────────────────────────────┐        │
│    │                        审核完成分支                          │        │
│    ├─────────────────────────────────────────────────────────────┤        │
│    │                                                             │        │
│    │     通过                    驳回                             │        │
│    │       │                      │                              │        │
│    │       ▼                      ▼                              │        │
│    │ ┌──────────────┐      ┌──────────────┐                     │        │
│    │ │    已通过    │      │    已驳回    │                     │        │
│    │ │ (APPROVED)   │      │ (REJECTED)   │                     │        │
│    │ └──────┬───────┘      └──────────────┘                     │        │
│    │        │                                                    │        │
│    │        ▼                                                    │        │
│    │ ┌──────────────┐                                           │        │
│    │ │   系统开通   │                                           │        │
│    │ │(PROVISIONING)│                                           │        │
│    │ └──────┬───────┘                                           │        │
│    │        │                                                    │        │
│    │        ▼                                                    │        │
│    │ ┌──────────────┐                                           │        │
│    │ │   已完成     │                                           │        │
│    │ │ (COMPLETED)  │                                           │        │
│    │ └──────────────┘                                           │        │
│    │                                                             │        │
│    └─────────────────────────────────────────────────────────────┘        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 审核任务状态流转图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          审核任务状态流转图                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                       ┌────────────────┐                                   │
│                       │    待分配       │                                   │
│                       │ (PENDING_ASSIGN)│                                   │
│                       └───────┬────────┘                                   │
│                               │                                            │
│                               │ 任务分配                                    │
│                               ▼                                            │
│                       ┌────────────────┐                                   │
│                       │    已分配       │                                   │
│                       │  (ASSIGNED)    │                                   │
│                       └───────┬────────┘                                   │
│                               │                                            │
│                               │ 开始审核                                    │
│                               ▼                                            │
│                       ┌────────────────┐                                   │
│                       │    审核中       │◄─────────────────────┐           │
│                       │  (AUDITING)    │                      │           │
│                       └───────┬────────┘                      │           │
│                               │                               │           │
│           ┌───────────────────┼───────────────────┐           │           │
│           │                   │                   │           │           │
│           ▼                   ▼                   ▼           │           │
│    ┌──────────────┐   ┌──────────────┐   ┌──────────────┐    │           │
│    │   审核通过   │   │   审核驳回   │   │   退回补充   │    │           │
│    │   (PASSED)   │   │  (REJECTED)  │   │(SUPPLEMENT)  │    │           │
│    └──────────────┘   └──────────────┘   └──────┬───────┘    │           │
│                                                  │            │           │
│                                                  └────────────┘           │
│                                                               重新提交     │
│                                                                             │
│  【任务流转规则】                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1. 任务分配：系统自动/手动分配给审核人员                              │   │
│  │ 2. 审核时限：高优先级-1天, 中优先级-3天, 低优先级-7天                 │   │
│  │ 3. 转交规则：审核中可转交给其他审核人员                               │   │
│  │ 4. 退回补充：审核不通过可退回给申请人补充资料                         │   │
│  │ 5. 阶段流转：前一阶段通过后才能进入下一阶段审核                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.4 系统开通状态流转图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          系统开通状态流转图                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                       ┌────────────────┐                                   │
│                       │    待开通       │                                   │
│                       │(PENDING_ACCESS)│                                   │
│                       └───────┬────────┘                                   │
│                               │                                            │
│                               │ 提交开通申请                                │
│                               ▼                                            │
│                       ┌────────────────┐                                   │
│                       │    开通中       │                                   │
│                       │ (PROVISIONING) │                                   │
│                       └───────┬────────┘                                   │
│                               │                                            │
│              ┌────────────────┼────────────────┐                          │
│              │                │                │                          │
│              ▼                ▼                ▼                          │
│      ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                  │
│      │   已开通     │ │   开通失败   │ │    已停用    │                  │
│      │ (ACCESSIBLE) │ │   (FAILED)   │ │ (DISABLED)   │                  │
│      └──────┬───────┘ └──────┬───────┘ └──────────────┘                  │
│             │                │                                            │
│             │                │                                            │
│             ▼                ▼                                            │
│      ┌──────────────┐ ┌──────────────┐                                   │
│      │ 服务反馈循环 │ │  重新开通    │                                   │
│      └──────────────┘ └──────────────┘                                   │
│                                                                             │
│  【开通流程说明】                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Step 1: 开户申请通过后, 自动生成系统开通任务                         │   │
│  │ Step 2: 技术部门接收开通任务, 执行系统配置                           │   │
│  │ Step 3: 开通完成后生成访问账号和权限配置                             │   │
│  │ Step 4: 通知客户系统已开通, 提供访问信息                             │   │
│  │ Step 5: 客户使用反馈, 进入服务支持阶段                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.5 状态流转矩阵

| 实体 | 当前状态 | 可操作动作 | 下一状态 |
|------|----------|------------|----------|
| 客户 | 待审核 | 审核通过 | 已确认 |
| 客户 | 待审核 | 审核驳回 | 待审核(补充) |
| 客户 | 已确认 | 分配跟进 | 已分配 |
| 客户 | 已分配 | 跟进转化 | 已转化 |
| 开户申请 | 草稿 | 提交审核 | 审核中 |
| 开户申请 | 审核中 | 审核通过 | 已通过 |
| 开户申请 | 审核中 | 审核驳回 | 已驳回 |
| 开户申请 | 审核中 | 退回补充 | 补充资料 |
| 开户申请 | 补充资料 | 重新提交 | 审核中 |
| 开户申请 | 已通过 | 系统开通 | 已完成 |
| 审核任务 | 待分配 | 任务分配 | 已分配 |
| 审核任务 | 已分配 | 开始审核 | 审核中 |
| 审核任务 | 审核中 | 审核通过 | 已通过 |
| 审核任务 | 审核中 | 审核驳回 | 已驳回 |
| 系统开通 | 待开通 | 提交开通 | 开通中 |
| 系统开通 | 开通中 | 开通成功 | 已开通 |
| 系统开通 | 开通中 | 开通失败 | 开通失败 |
| 系统开通 | 已开通 | 服务到期 | 已停用 |

---

## 四、统计口径定义

### 4.1 客户相关统计

#### 4.1.1 新增客户数

| 统计项 | 定义 |
|--------|------|
| **指标名称** | 新增客户数 |
| **指标编码** | CUST_NEW_COUNT |
| **计算公式** | 统计周期内状态变为"已确认"的客户数量 |
| **统计维度** | 分支机构、销售经理、客户类型、行业 |
| **数据来源** | biz_customer表, 按create_time统计 |
| **更新频率** | 实时/日/月 |
| **备注** | 仅统计首次确认的客户，不含重复确认 |

#### 4.1.2 客户审核通过率

| 统计项 | 定义 |
|--------|------|
| **指标名称** | 客户审核通过率 |
| **指标编码** | CUST_AUDIT_PASS_RATE |
| **计算公式** | 审核通过客户数 / 提交审核客户总数 × 100% |
| **统计维度** | 分支机构、审核人员、时间段 |
| **数据来源** | biz_customer表, audit_status字段 |
| **更新频率** | 日/周/月 |
| **备注** | 不包含待审核和审核中的数据 |

#### 4.1.3 客户分配转化率

| 统计项 | 定义 |
|--------|------|
| **指标名称** | 客户分配转化率 |
| **指标编码** | CUST_ASSIGN_CONV_RATE |
| **计算公式** | 已转化客户数 / 已分配客户总数 × 100% |
| **统计维度** | 分支机构、跟进人员、时间段 |
| **数据来源** | biz_customer表, assign_status和status字段 |
| **更新频率** | 周/月 |
| **备注** | 转化定义为客户进入"已转化"状态 |

### 4.2 开户审核统计

#### 4.2.1 开户申请数

| 统计项 | 定义 |
|--------|------|
| **指标名称** | 开户申请数 |
| **指标编码** | OPENING_APPLY_COUNT |
| **计算公式** | 统计周期内提交的开户申请总数 |
| **统计维度** | 分支机构、客户、业务类型 |
| **数据来源** | biz_account_opening表, submit_time统计 |
| **更新频率** | 实时/日/月 |
| **备注** | 包含所有申请类型的开户申请 |

#### 4.2.2 开户审核时效

| 统计项 | 定义 |
|--------|------|
| **指标名称** | 平均审核时效(小时) |
| **指标编码** | AUDIT_AVG_DURATION |
| **计算公式** | SUM(审核完成时间 - 提交时间) / 已完成审核数 |
| **统计维度** | 审核类型、审核人员、分支机构 |
| **数据来源** | biz_account_opening表, submit_time和audit_complete_time |
| **更新频率** | 周/月 |
| **备注** | 仅统计已完成的审核，不含进行中的 |

#### 4.2.3 审核任务积压数

| 统计项 | 定义 |
|--------|------|
| **指标名称** | 审核任务积压数 |
| **指标编码** | AUDIT_BACKLOG_COUNT |
| **计算公式** | 状态为"待分配"或"已分配"或"审核中"的任务数 |
| **统计维度** | 审核类型、优先级、分支机构 |
| **数据来源** | biz_audit_task表, status字段 |
| **更新频率** | 实时 |
| **备注** | 用于监控审核工作量和人员负荷 |

### 4.3 分支机构业绩统计

#### 4.3.1 业务金额

| 统计项 | 定义 |
|--------|------|
| **指标名称** | 业务金额 |
| **指标编码** | BRANCH_BUSINESS_AMOUNT |
| **计算公式** | SUM(统计周期内开户申请对应的实际业务发生金额) |
| **统计维度** | 分支机构、业务类型、时间段 |
| **数据来源** | biz_progress表, actual_amount字段 |
| **更新频率** | 日/周/月/季/年 |
| **备注** | 按业务进展记录中的实际金额汇总 |

#### 4.3.2 目标完成率

| 统计项 | 定义 |
|--------|------|
| **指标名称** | 目标完成率 |
| **指标编码** | TARGET_COMPLETION_RATE |
| **计算公式** | 实际业绩金额 / 目标金额 × 100% |
| **统计维度** | 分支机构、业务线、时间段 |
| **数据来源** | biz_performance表, business_amount和target_amount |
| **更新频率** | 月/季/年 |
| **备注** | 超过100%表示超额完成 |

#### 4.3.3 分支机构活跃度

| 统计项 | 定义 |
|--------|------|
| **指标名称** | 分支机构活跃度 |
| **指标编码** | BRANCH_ACTIVITY_RATE |
| **计算公式** | 有业务进展记录的天数 / 统计周期总工作日 × 100% |
| **统计维度** | 分支机构、时间段 |
| **数据来源** | biz_progress表, progress_date字段 |
| **更新频率** | 周/月 |
| **备注** | 反映分支机构的业务活跃程度 |

### 4.4 系统开通统计

#### 4.4.1 系统开通数

| 统计项 | 定义 |
|--------|------|
| **指标名称** | 系统开通数 |
| **指标编码** | SYS_ACCESS_COUNT |
| **计算公式** | 统计周期内状态变为"已开通"的系统数量 |
| **统计维度** | 系统类型、分支机构、客户类型 |
| **数据来源** | biz_system_access表, open_time统计 |
| **更新频率** | 实时/日/月 |
| **备注** | 按系统开通成功时间统计 |

#### 4.4.2 系统开通成功率

| 统计项 | 定义 |
|--------|------|
| **指标名称** | 系统开通成功率 |
| **指标编码** | SYS_ACCESS_SUCCESS_RATE |
| **计算公式** | 开通成功数 / (开通成功数 + 开通失败数) × 100% |
| **统计维度** | 系统类型、开通人员、时间段 |
| **数据来源** | biz_system_access表, access_status字段 |
| **更新频率** | 周/月 |
| **备注** | 不含待开通和开通中的数据 |

#### 4.4.3 系统故障率

| 统计项 | 定义 |
|--------|------|
| **指标名称** | 系统故障率 |
| **指标编码** | SYS_FAILURE_RATE |
| **计算公式** | 故障反馈数 / 已开通系统总数 × 100% |
| **统计维度** | 系统类型、客户、时间段 |
| **数据来源** | biz_system_feedback表, feedback_type=2(问题反馈) |
| **更新频率** | 月/季 |
| **备注** | 用于评估系统稳定性 |

### 4.5 统计维度总览

| 维度类型 | 维度名称 | 维度编码 | 说明 |
|----------|----------|----------|------|
| 时间 | 日 | DAY | 按自然日统计 |
| 时间 | 周 | WEEK | 按自然周统计 |
| 时间 | 月 | MONTH | 按自然月统计 |
| 时间 | 季度 | QUARTER | 按季度统计 |
| 时间 | 年 | YEAR | 按自然年统计 |
| 机构 | 总部 | HQ | 集团总部层面 |
| 机构 | 分公司 | BRANCH | 分公司层面 |
| 机构 | 营业部 | DEPT | 营业部层面 |
| 人员 | 销售经理 | SALES | 按销售经理统计 |
| 人员 | 审核人员 | AUDITOR | 按审核人员统计 |
| 业务 | 业务类型 | BIZ_TYPE | 按业务类型统计 |
| 业务 | 客户类型 | CUST_TYPE | 按客户类型统计 |
| 系统 | 系统类型 | SYS_TYPE | 按系统类型统计 |

### 4.6 核心指标汇总表

| 指标分类 | 指标名称 | 计算周期 | 重要程度 |
|----------|----------|----------|----------|
| 客户 | 新增客户数 | 日/月 | ⭐⭐⭐ |
| 客户 | 客户审核通过率 | 周/月 | ⭐⭐ |
| 客户 | 客户转化率 | 月/季 | ⭐⭐⭐ |
| 开户 | 开户申请数 | 日/月 | ⭐⭐⭐ |
| 开户 | 平均审核时效 | 周/月 | ⭐⭐ |
| 开户 | 审核积压数 | 实时 | ⭐⭐ |
| 机构 | 业务金额 | 月/季/年 | ⭐⭐⭐ |
| 机构 | 目标完成率 | 月/季/年 | ⭐⭐⭐ |
| 机构 | 机构排名 | 月/季/年 | ⭐⭐ |
| 系统 | 系统开通数 | 日/月 | ⭐⭐ |
| 系统 | 开通成功率 | 月/季 | ⭐⭐ |
| 系统 | 客户满意度 | 月/季 | ⭐⭐⭐ |

---

## 五、数据字典汇总

### 5.1 状态枚举值

```sql
-- 客户状态 (biz_customer.status)
0: 待审核 (PENDING)
1: 已确认 (CONFIRMED)
2: 已分配 (ASSIGNED)
3: 已转化 (CONVERTED)
9: 无效 (INVALID)

-- 开户申请状态 (biz_account_opening.status)
0: 草稿/待提交 (DRAFT)
1: 审核中 (AUDITING)
2: 已通过 (APPROVED)
3: 已驳回 (REJECTED)
4: 已撤销 (REVOKED)
5: 补充资料 (SUPPLEMENT)
6: 已完成 (COMPLETED)

-- 审核任务状态 (biz_audit_task.status)
0: 待分配 (PENDING_ASSIGN)
1: 已分配 (ASSIGNED)
2: 审核中 (AUDITING)
3: 已通过 (PASSED)
4: 已驳回 (REJECTED)

-- 系统开通状态 (biz_system_access.access_status)
0: 待开通 (PENDING)
1: 开通中 (PROVISIONING)
2: 已开通 (ACCESSIBLE)
3: 开通失败 (FAILED)
4: 已停用 (DISABLED)
```

### 5.2 类型枚举值

```sql
-- 客户类型 (biz_customer.customer_type)
1: 机构客户
2: 个人客户

-- 资质类型 (biz_customer_qualification.qual_type)
1: 营业执照
2: 金融牌照
3: 税务登记
4: 其他资质

-- 跟进类型 (biz_follow_up.follow_type)
1: 电话跟进
2: 邮件跟进
3: 实地拜访
4: 会议沟通
5: 其他方式

-- 审核类型 (biz_audit_task.audit_type)
1: 资料审核
2: 实地审核
3: 风控审核
4: 合规审核

-- 反馈类型 (biz_system_feedback.feedback_type)
1: 功能建议
2: 问题反馈
3: 使用咨询
4: 投诉建议
```

---

## 六、附录

### 6.1 数据库DDL脚本

```sql
-- =====================================================
-- 业务组织模块数据库DDL脚本
-- 数据库: MySQL 8.0+
-- 字符集: utf8mb4
-- 排序规则: utf8mb4_unicode_ci
-- =====================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS biz_organization 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE biz_organization;

-- 客户信息表
CREATE TABLE biz_customer (
    customer_id VARCHAR(32) PRIMARY KEY COMMENT '客户ID',
    customer_code VARCHAR(64) NOT NULL COMMENT '客户编码',
    customer_name VARCHAR(128) NOT NULL COMMENT '客户名称',
    -- ... 其他字段
    INDEX idx_customer_code (customer_code),
    INDEX idx_customer_name (customer_name),
    INDEX idx_customer_status (status)
) ENGINE=InnoDB COMMENT='客户信息表';

-- 其他表的DDL语句...
```

### 6.2 物理模型设计建议

| 设计项 | 建议方案 |
|--------|----------|
| 数据库引擎 | InnoDB (支持事务、行锁、外键) |
| 字符集 | utf8mb4 (支持完整Unicode) |
| 主键策略 | 雪花算法生成32位字符串 |
| 时间字段 | DATETIME类型, 默认CURRENT_TIMESTAMP |
| 软删除 | deleted字段标记, 0-正常, 1-删除 |
| 分表策略 | 跟进记录、审核历史按年分表 |
| 归档策略 | 3年以上历史数据归档到历史库 |

### 6.3 数据量估算

| 表名 | 日增量 | 年增量 | 保留策略 |
|------|--------|--------|----------|
| biz_customer | 50-100条 | 2-3万条 | 永久保留 |
| biz_follow_up | 200-500条 | 10万条 | 3年归档 |
| biz_account_opening | 30-50条 | 1万条 | 5年归档 |
| biz_audit_task | 100-200条 | 5万条 | 3年归档 |
| biz_audit_history | 300-600条 | 15万条 | 2年归档 |
| biz_progress | 100-300条 | 8万条 | 3年归档 |
| biz_performance | 按机构数 | 12期/年 | 永久保留 |
| biz_system_access | 30-50条 | 1万条 | 永久保留 |
| biz_system_feedback | 50-100条 | 2万条 | 3年归档 |

---

**文档结束**

*本文档为业务支持中心-业务组织模块数据建模方案，供系统设计、开发和测试参考使用。*
