# 员工工作台 - 账户开立模块数据建模方案

## 目录
1. [功能概述](#功能概述)
2. [实体关系图（ER图）](#实体关系图er图)
3. [数据表结构设计](#数据表结构设计)
4. [开户流程状态机设计](#开户流程状态机设计)
5. [审核规则定义](#审核规则定义)

---

## 功能概述

账户开立模块支持四种开户类型：
- **高净值个人开户**：针对高净值个人投资者
- **专业机构开户**：针对企业、机构等法人实体
- **家族办公室开户**：针对家族财富管理需求
- **产品开户**：针对基金产品、资管计划等

---

## 实体关系图（ER图）

### 实体关系概览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           账户开立模块 ER图                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│   AccountType   │◄─────────────┐
│   (账户类型)     │              │
├─────────────────┤              │
│ PK type_id      │              │
│   type_name     │              │
│   type_code     │              │
│   description   │              │
└────────┬────────┘              │
         │                       │
         │ 1:N                   │
         ▼                       │
┌─────────────────┐     ┌────────┴────────┐
│ AccountOpening  │     │  ProcessStatus  │
│   (开户申请)     │◄────│   (流程状态)     │
├─────────────────┤     ├─────────────────┤
│ PK application_id│     │ PK status_id    │
│   type_id (FK)  │     │   status_name   │
│   status_id(FK) │     │   status_code   │
│   applicant_id  │     │   description   │
│   submit_time   │     └─────────────────┘
│   current_step  │
└────────┬────────┘
         │ 1:1 (按类型)
         ├─────────────────────────────────────────────────────────────────┐
         │                     │                      │                    │
         ▼                     ▼                      ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ HNWIndividual   │  │ Institution     │  │ FamilyOffice    │  │ ProductAccount  │
│  (高净值个人)    │  │  (专业机构)      │  │  (家族办公室)    │  │  (产品账户)      │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ PK account_id   │  │ PK account_id   │  │ PK account_id   │  │ PK account_id   │
│ FK application  │  │ FK application  │  │ FK application  │  │ FK application  │
│   full_name     │  │   org_name      │  │   rep_name      │  │   product_code  │
│   id_number     │  │   uscc          │  │   total_assets  │  │   product_name  │
│   phone         │  │   legal_rep     │  │   requirements  │  │   manager       │
│   asset_scale   │  │   org_type      │  │   event_arrange │  │   custodian     │
│   risk_level    │  │   license_no    │  │   family_desc   │  │   product_type  │
│   risk_score    │  │   license_path  │  │                 │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘

┌─────────────────┐
│  AuditRecord    │
│   (审核记录)     │
├─────────────────┤
│ PK audit_id     │
│ FK application  │
│   auditor_id    │
│   audit_time    │
│   audit_type    │
│   audit_result  │
│   audit_comment │
│   next_status   │
└─────────────────┘

┌─────────────────┐
│ Document        │
│   (附件材料)     │
├─────────────────┤
│ PK doc_id       │
│ FK application  │
│   doc_type      │
│   doc_name      │
│   file_path     │
│   upload_time   │
│   verify_status │
└─────────────────┘
```

### 实体关系详细说明

| 关系 | 类型 | 说明 |
|------|------|------|
| AccountType → AccountOpening | 1:N | 一个账户类型可对应多个开户申请 |
| ProcessStatus → AccountOpening | 1:N | 一个状态可对应多个开户申请 |
| AccountOpening → HNWIndividual | 1:1 | 高净值个人开户详情 |
| AccountOpening → Institution | 1:1 | 专业机构开户详情 |
| AccountOpening → FamilyOffice | 1:1 | 家族办公室开户详情 |
| AccountOpening → ProductAccount | 1:1 | 产品开户详情 |
| AccountOpening → AuditRecord | 1:N | 一个申请可有多个审核记录 |
| AccountOpening → Document | 1:N | 一个申请可上传多个附件 |

---

## 数据表结构设计

### 1. 账户类型表 (account_types)

存储支持的账户类型定义。

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| type_id | INT | PRIMARY KEY, AUTO_INCREMENT | - | 类型ID |
| type_code | VARCHAR(32) | UNIQUE, NOT NULL | - | 类型编码：HNW_INDIVIDUAL / INSTITUTION / FAMILY_OFFICE / PRODUCT |
| type_name | VARCHAR(64) | NOT NULL | - | 类型名称 |
| description | VARCHAR(255) | NULL | - | 类型描述 |
| is_active | TINYINT | NOT NULL | 1 | 是否启用 |
| created_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 更新时间 |

**初始化数据：**
```sql
INSERT INTO account_types (type_code, type_name, description) VALUES
('HNW_INDIVIDUAL', '高净值个人', '高净值个人投资者开户'),
('INSTITUTION', '专业机构', '企业、机构等法人开户'),
('FAMILY_OFFICE', '家族办公室', '家族财富管理开户'),
('PRODUCT', '产品开户', '基金产品、资管计划开户');
```

### 2. 流程状态表 (process_status)

存储开户流程的状态定义。

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| status_id | INT | PRIMARY KEY, AUTO_INCREMENT | - | 状态ID |
| status_code | VARCHAR(32) | UNIQUE, NOT NULL | - | 状态编码 |
| status_name | VARCHAR(64) | NOT NULL | - | 状态名称 |
| status_category | VARCHAR(32) | NOT NULL | - | 状态分类：DRAFT/SUBMIT/APPROVE/REJECT/CANCEL |
| description | VARCHAR(255) | NULL | - | 状态描述 |
| display_order | INT | NOT NULL | 0 | 显示顺序 |
| is_terminal | TINYINT | NOT NULL | 0 | 是否为终态 |

**初始化数据：**
```sql
INSERT INTO process_status (status_code, status_name, status_category, is_terminal, display_order) VALUES
('DRAFT', '草稿', 'DRAFT', 0, 10),
('SUBMITTED', '已提交', 'SUBMIT', 0, 20),
('PRELIM_REVIEW', '初审中', 'REVIEW', 0, 30),
('PRELIM_APPROVED', '初审通过', 'REVIEW', 0, 40),
('PRELIM_REJECTED', '初审驳回', 'REJECT', 1, 50),
('RISK_REVIEW', '风控审核中', 'REVIEW', 0, 60),
('RISK_APPROVED', '风控通过', 'REVIEW', 0, 70),
('RISK_REJECTED', '风控驳回', 'REJECT', 1, 80),
('COMPLIANCE_REVIEW', '合规审核中', 'REVIEW', 0, 90),
('COMPLIANCE_APPROVED', '合规通过', 'REVIEW', 0, 100),
('COMPLIANCE_REJECTED', '合规驳回', 'REJECT', 1, 110),
('FINAL_REVIEW', '终审中', 'REVIEW', 0, 120),
('APPROVED', '已批准', 'APPROVE', 1, 130),
('REJECTED', '已驳回', 'REJECT', 1, 140),
('CANCELLED', '已取消', 'CANCEL', 1, 150);
```

### 3. 开户申请表 (account_openings)

存储开户申请的主表信息。

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| application_id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | - | 申请ID |
| application_no | VARCHAR(32) | UNIQUE, NOT NULL | - | 申请编号：AO + 年月日 + 6位序列号 |
| type_id | INT | FOREIGN KEY, NOT NULL | - | 账户类型ID |
| status_id | INT | FOREIGN KEY, NOT NULL | - | 当前状态ID |
| applicant_id | BIGINT | NOT NULL | - | 申请人（员工）ID |
| submit_time | DATETIME | NULL | - | 提交时间 |
| complete_time | DATETIME | NULL | - | 完成时间 |
| current_step | VARCHAR(32) | NULL | - | 当前处理步骤 |
| priority | TINYINT | NOT NULL | 1 | 优先级：1-普通, 2-加急, 3-特急 |
| remarks | TEXT | NULL | - | 备注说明 |
| created_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 更新时间 |

**索引：**
- `idx_type_status` (type_id, status_id)
- `idx_applicant` (applicant_id)
- `idx_submit_time` (submit_time)
- `idx_application_no` (application_no)

### 4. 高净值个人开户详情表 (hnw_individual_accounts)

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| account_id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | - | 账户ID |
| application_id | BIGINT | FOREIGN KEY, UNIQUE, NOT NULL | - | 申请ID |
| full_name | VARCHAR(128) | NOT NULL | - | 客户姓名 |
| id_number | VARCHAR(18) | NOT NULL | - | 身份证号 |
| phone | VARCHAR(20) | NOT NULL | - | 联系电话 |
| email | VARCHAR(128) | NULL | - | 电子邮箱 |
| asset_scale_min | DECIMAL(18,4) | NULL | - | 预计资产规模下限（万元） |
| asset_scale_max | DECIMAL(18,4) | NULL | - | 预计资产规模上限（万元） |
| risk_level | TINYINT | NOT NULL | - | 风险测评等级：1-保守型, 2-稳健型, 3-平衡型, 4-进取型, 5-激进型 |
| risk_score | INT | NULL | - | 风险测评分数 |
| risk_assessment_date | DATE | NULL | - | 风险测评日期 |
| risk_valid_until | DATE | NULL | - | 风险测评有效期至 |
| address | VARCHAR(255) | NULL | - | 联系地址 |
| occupation | VARCHAR(64) | NULL | - | 职业 |
| company_name | VARCHAR(128) | NULL | - | 工作单位 |
| created_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 更新时间 |

**索引：**
- `idx_id_number` (id_number)
- `idx_phone` (phone)
- `idx_full_name` (full_name)

### 5. 专业机构开户详情表 (institution_accounts)

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| account_id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | - | 账户ID |
| application_id | BIGINT | FOREIGN KEY, UNIQUE, NOT NULL | - | 申请ID |
| org_name | VARCHAR(256) | NOT NULL | - | 机构全称 |
| short_name | VARCHAR(64) | NULL | - | 机构简称 |
| uscc | VARCHAR(18) | NOT NULL | - | 统一社会信用代码 |
| legal_rep_name | VARCHAR(128) | NOT NULL | - | 法定代表人姓名 |
| legal_rep_id_number | VARCHAR(18) | NOT NULL | - | 法定代表人身份证号 |
| legal_rep_phone | VARCHAR(20) | NOT NULL | - | 法定代表人联系电话 |
| org_type | VARCHAR(32) | NOT NULL | - | 机构类型：ENTERPRISE/GOVERNMENT/FINANCIAL/OTHER |
| industry | VARCHAR(64) | NULL | - | 所属行业 |
| registered_capital | DECIMAL(18,4) | NULL | - | 注册资本（万元） |
| established_date | DATE | NULL | - | 成立日期 |
| registered_address | VARCHAR(255) | NULL | - | 注册地址 |
| business_address | VARCHAR(255) | NULL | - | 办公地址 |
| business_scope | TEXT | NULL | - | 经营范围 |
| license_no | VARCHAR(64) | NOT NULL | - | 营业执照编号 |
| license_path | VARCHAR(500) | NOT NULL | - | 营业执照文件路径 |
| contact_name | VARCHAR(128) | NOT NULL | - | 联系人姓名 |
| contact_phone | VARCHAR(20) | NOT NULL | - | 联系人电话 |
| contact_email | VARCHAR(128) | NULL | - | 联系人邮箱 |
| created_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 更新时间 |

**索引：**
- `idx_uscc` (uscc)
- `idx_org_name` (org_name)
- `idx_org_type` (org_type)

### 6. 家族办公室开户详情表 (family_office_accounts)

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| account_id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | - | 账户ID |
| application_id | BIGINT | FOREIGN KEY, UNIQUE, NOT NULL | - | 申请ID |
| rep_name | VARCHAR(128) | NOT NULL | - | 家族代表姓名 |
| rep_id_number | VARCHAR(18) | NOT NULL | - | 家族代表身份证号 |
| rep_phone | VARCHAR(20) | NOT NULL | - | 家族代表联系电话 |
| rep_email | VARCHAR(128) | NULL | - | 家族代表邮箱 |
| total_assets_min | DECIMAL(18,4) | NULL | - | 总资产规模下限（万元） |
| total_assets_max | DECIMAL(18,4) | NULL | - | 总资产规模上限（万元） |
| investment_requirements | TEXT | NULL | - | 投资需求描述 |
| family_description | TEXT | NULL | - | 家族背景描述 |
| preferred_products | VARCHAR(255) | NULL | - | 偏好产品类型（逗号分隔） |
| investment_horizon | VARCHAR(32) | NULL | - | 投资期限偏好 |
| liquidity_requirement | VARCHAR(32) | NULL | - | 流动性需求 |
| event_arrangement | TEXT | NULL | - | 私享会安排 |
| event_preferred_date | DATE | NULL | - | 期望私享会日期 |
| event_location | VARCHAR(255) | NULL | - | 私享会地点 |
| service_team_req | TINYINT | NULL | - | 专属服务团队需求：0-否, 1-是 |
| created_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 更新时间 |

**索引：**
- `idx_rep_id_number` (rep_id_number)
- `idx_rep_name` (rep_name)

### 7. 产品开户详情表 (product_accounts)

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| account_id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | - | 账户ID |
| application_id | BIGINT | FOREIGN KEY, UNIQUE, NOT NULL | - | 申请ID |
| product_code | VARCHAR(32) | NOT NULL | - | 产品代码 |
| product_name | VARCHAR(256) | NOT NULL | - | 产品名称 |
| product_short_name | VARCHAR(64) | NULL | - | 产品简称 |
| manager_name | VARCHAR(128) | NOT NULL | - | 管理人名称 |
| manager_uscc | VARCHAR(18) | NOT NULL | - | 管理人统一社会信用代码 |
| custodian_bank | VARCHAR(128) | NOT NULL | - | 托管行 |
| custodian_account | VARCHAR(64) | NULL | - | 托管账户 |
| product_type | VARCHAR(32) | NOT NULL | - | 产品类型：SECURITIES_FUND/ASSET_MGMT/PE_FUND/OTHER |
| product_sub_type | VARCHAR(32) | NULL | - | 产品子类型 |
| fund_size | DECIMAL(18,4) | NULL | - | 基金规模（万元） |
| establish_date | DATE | NULL | - | 成立日期 |
| maturity_date | DATE | NULL | - | 到期日期 |
| investment_scope | TEXT | NULL | - | 投资范围 |
| product_manager_name | VARCHAR(128) | NOT NULL | - | 产品经理姓名 |
| product_manager_phone | VARCHAR(20) | NOT NULL | - | 产品经理电话 |
| product_manager_email | VARCHAR(128) | NULL | - | 产品经理邮箱 |
| risk_level | TINYINT | NOT NULL | - | 产品风险等级 |
| registration_no | VARCHAR(64) | NULL | - | 产品备案号 |
| created_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 更新时间 |

**索引：**
- `idx_product_code` (product_code)
- `idx_manager_uscc` (manager_uscc)
- `idx_product_type` (product_type)

### 8. 审核记录表 (audit_records)

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| audit_id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | - | 审核记录ID |
| application_id | BIGINT | FOREIGN KEY, NOT NULL | - | 申请ID |
| audit_type | VARCHAR(32) | NOT NULL | - | 审核类型：PRELIM/RISK/COMPLIANCE/FINAL |
| auditor_id | BIGINT | NOT NULL | - | 审核人ID |
| auditor_name | VARCHAR(128) | NOT NULL | - | 审核人姓名 |
| audit_time | DATETIME | NOT NULL | - | 审核时间 |
| audit_result | TINYINT | NOT NULL | - | 审核结果：1-通过, 2-驳回, 3-退回修改 |
| audit_comment | TEXT | NULL | - | 审核意见 |
| prev_status_id | INT | NOT NULL | - | 审核前状态 |
| next_status_id | INT | NOT NULL | - | 审核后状态 |
| created_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |

**索引：**
- `idx_application_audit` (application_id, audit_type)
- `idx_auditor` (auditor_id)
- `idx_audit_time` (audit_time)

### 9. 附件材料表 (documents)

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| doc_id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | - | 附件ID |
| application_id | BIGINT | FOREIGN KEY, NOT NULL | - | 申请ID |
| doc_type | VARCHAR(32) | NOT NULL | - | 附件类型编码 |
| doc_type_name | VARCHAR(64) | NOT NULL | - | 附件类型名称 |
| doc_name | VARCHAR(256) | NOT NULL | - | 文件名称 |
| file_path | VARCHAR(500) | NOT NULL | - | 文件存储路径 |
| file_size | BIGINT | NOT NULL | - | 文件大小（字节） |
| file_hash | VARCHAR(64) | NULL | - | 文件哈希值（MD5） |
| mime_type | VARCHAR(64) | NULL | - | 文件MIME类型 |
| uploaded_by | BIGINT | NOT NULL | - | 上传人ID |
| uploaded_time | DATETIME | NOT NULL | - | 上传时间 |
| verify_status | TINYINT | NOT NULL | 0 | 核验状态：0-未核验, 1-核验通过, 2-核验失败 |
| verify_result | TEXT | NULL | - | 核验结果说明 |
| created_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |

**索引：**
- `idx_application_doc` (application_id, doc_type)
- `idx_upload_time` (uploaded_time)

### 10. 流程状态流转表 (status_transitions)

定义允许的状态流转规则。

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|----------|------|--------|------|
| transition_id | INT | PRIMARY KEY, AUTO_INCREMENT | - | 流转ID |
| from_status_id | INT | FOREIGN KEY, NOT NULL | - | 起始状态ID |
| to_status_id | INT | FOREIGN KEY, NOT NULL | - | 目标状态ID |
| action_code | VARCHAR(32) | NOT NULL | - | 操作编码：SUBMIT/APPROVE/REJECT/RETURN/CANCEL |
| action_name | VARCHAR(64) | NOT NULL | - | 操作名称 |
| required_role | VARCHAR(32) | NULL | - | 所需角色 |
| is_auto | TINYINT | NOT NULL | 0 | 是否自动流转 |
| condition_expr | TEXT | NULL | - | 流转条件表达式 |
| description | VARCHAR(255) | NULL | - | 说明 |

---

## 开户流程状态机设计

### 状态机概览

```
                              ┌─────────────────────────────────────────────────────────┐
                              │                        开户流程状态机                     │
                              └─────────────────────────────────────────────────────────┘

                                   ┌─────────────┐
                                   │    草稿     │
                                   │   DRAFT    │
                                   └──────┬──────┘
                                          │ 提交申请
                                          ▼
                                   ┌─────────────┐
                                   │   已提交    │     初审驳回
                                   │  SUBMITTED  │◄────────────────┐
                                   └──────┬──────┘                 │
                                          │ 进入初审                │
                                          ▼                         │
                                   ┌─────────────┐                  │
                                   │   初审中    │                  │
                                   │ PRELIM_REVIEW│                 │
                                   └──────┬──────┘                 │
                                          │ 初审通过/驳回           │
                           ┌──────────────┼──────────────┐          │
                           ▼              │              ▼          │
                    ┌─────────────┐       │       ┌─────────────┐   │
                    │ 初审通过    │       │       │ 初审驳回    │───┘
                    │PRELIM_APPROVED      │       │PRELIM_REJECTED
                    └──────┬──────┘       │       └─────────────┘
                           │              │              (终态)
                           │ 进入风控审核  │
                           ▼              │
                    ┌─────────────┐       │
                    │ 风控审核中  │       │
                    │ RISK_REVIEW │       │
                    └──────┬──────┘       │
                           │ 风控通过/驳回│
              ┌────────────┼────────────┐ │
              ▼            │            ▼ │
       ┌─────────────┐     │     ┌─────────────┐     ┌─────────────┐
       │ 风控通过    │     │     │ 风控驳回    │────►│   已驳回    │
       │RISK_APPROVED│     │     │RISK_REJECTED      │  REJECTED   │
       └──────┬──────┘     │     └─────────────┘     └─────────────┘
              │            │            (终态)             (终态)
              │ 进入合规审核│
              ▼            │
       ┌─────────────┐     │
       │ 合规审核中  │     │
       │COMPLIANCE_REVIEW   │
       └──────┬──────┘     │
              │ 合规通过/驳回
     ┌────────┼────────┐   │
     ▼        │        ▼   │
┌─────────┐   │   ┌─────────┴─┐
│合规通过 │   │   │ 合规驳回  │────► ┌─────────┐
│COMPLIANCE_APPROVED    │COMPLIANCE_REJECTED      │ 已驳回  │
└────┬────┘   │   └───────────┘      │ REJECTED│
     │        │        (终态)        └─────────┘
     │ 进入终审  │                         (终态)
     ▼        │
┌─────────┐   │
│ 终审中  │   │
│FINAL_REVIEW   │
└────┬────┘   │
     │ 终审通过/驳回
   ┌─┴────────┐
   ▼          ▼
┌───────┐  ┌─────────┐
│已批准 │  │ 已驳回  │
│APPROVED    │REJECTED │
└───────┘  └─────────┘
  (终态)      (终态)

┌─────────┐
│ 已取消  │
│CANCELLED│
└─────────┘
  (终态)
```

### 状态流转规则表

| 当前状态 | 操作 | 下一状态 | 执行角色 | 触发条件 |
|----------|------|----------|----------|----------|
| 草稿 (DRAFT) | 提交 | 已提交 (SUBMITTED) | 申请人 | 必填字段完整校验通过 |
| 已提交 (SUBMITTED) | 初审 | 初审中 (PRELIM_REVIEW) | 系统 | 自动流转 |
| 初审中 (PRELIM_REVIEW) | 通过 | 初审通过 (PRELIM_APPROVED) | 初审员 | 基础信息校验通过 |
| 初审中 (PRELIM_REVIEW) | 驳回 | 初审驳回 (PRELIM_REJECTED) | 初审员 | 信息不完整或不符合要求 |
| 初审通过 (PRELIM_APPROVED) | 风控审核 | 风控审核中 (RISK_REVIEW) | 系统 | 自动流转 |
| 风控审核中 (RISK_REVIEW) | 通过 | 风控通过 (RISK_APPROVED) | 风控专员 | 风险测评匹配、资产规模达标 |
| 风控审核中 (RISK_REVIEW) | 驳回 | 风控驳回 (RISK_REJECTED) | 风控专员 | 风险不匹配或异常 |
| 风控通过 (RISK_APPROVED) | 合规审核 | 合规审核中 (COMPLIANCE_REVIEW) | 系统 | 自动流转 |
| 合规审核中 (COMPLIANCE_REVIEW) | 通过 | 合规通过 (COMPLIANCE_APPROVED) | 合规专员 | 合规检查通过 |
| 合规审核中 (COMPLIANCE_REVIEW) | 驳回 | 合规驳回 (COMPLIANCE_REJECTED) | 合规专员 | 合规问题 |
| 合规通过 (COMPLIANCE_APPROVED) | 终审 | 终审中 (FINAL_REVIEW) | 系统 | 自动流转 |
| 终审中 (FINAL_REVIEW) | 批准 | 已批准 (APPROVED) | 审批负责人 | 全部审核通过 |
| 终审中 (FINAL_REVIEW) | 驳回 | 已驳回 (REJECTED) | 审批负责人 | 综合评估不通过 |
| 草稿/已提交 | 取消 | 已取消 (CANCELLED) | 申请人 | 申请人主动取消 |
| 初审驳回/风控驳回/合规驳回 | 重新提交 | 已提交 (SUBMITTED) | 申请人 | 修改后重新提交 |

### 各状态停留时限

| 状态 | 建议时限 | 超时处理 |
|------|----------|----------|
| 草稿 | 无限制 | - |
| 已提交 | 即时处理 | 自动流转至初审 |
| 初审中 | 1个工作日 | 自动催办 |
| 风控审核中 | 2个工作日 | 自动催办+升级通知 |
| 合规审核中 | 2个工作日 | 自动催办 |
| 终审中 | 1个工作日 | 自动催办+升级通知 |

---

## 审核规则定义

### 1. 通用审核规则

#### 1.1 字段完整性校验

| 开户类型 | 必填字段清单 |
|----------|--------------|
| 高净值个人 | 客户姓名、身份证号、联系电话、预计资产规模、风险测评等级 |
| 专业机构 | 机构全称、统一社会信用代码、法定代表人、机构类型、营业执照编号 |
| 家族办公室 | 家族代表姓名、总资产规模、投资需求描述 |
| 产品开户 | 产品代码、产品名称、管理人、托管行、产品类型 |

#### 1.2 身份认证规则

| 规则ID | 规则名称 | 规则描述 | 适用类型 | 触发动作 |
|--------|----------|----------|----------|----------|
| ID-001 | 身份证号格式校验 | 身份证号必须符合18位国家标准格式 | 高净值个人、家族代表 | 格式校验失败则提示修正 |
| ID-002 | 身份证号唯一性校验 | 同一身份证号不能重复开户 | 高净值个人、家族代表 | 重复则提示已存在账户 |
| ID-003 | 统一社会信用代码校验 | USCC必须符合18位国家标准格式 | 机构、产品管理人 | 格式校验失败则提示修正 |
| ID-004 | USCC唯一性校验 | 同一USCC不能重复开户 | 机构 | 重复则提示已存在账户 |
| ID-005 | 手机实名认证 | 联系电话需通过运营商实名认证 | 高净值个人、机构联系人 | 认证失败则要求补充材料 |

### 2. 分类审核规则

#### 2.1 高净值个人开户审核规则

| 规则ID | 规则类别 | 规则名称 | 规则条件 | 审核结果 |
|--------|----------|----------|----------|----------|
| HNW-001 | 准入门槛 | 资产规模下限 | 预计资产规模 ≥ 300万元 | 不满足则驳回 |
| HNW-002 | 准入门槛 | 年龄限制 | 18岁 ≤ 年龄 ≤ 70岁 | 不满足则驳回 |
| HNW-003 | 风险匹配 | 风险测评有效期 | 风险测评日期在1年内 | 过期则要求重新测评 |
| HNW-004 | 合规检查 | 反洗钱黑名单 | 不在监管黑名单中 | 命中则驳回并上报 |
| HNW-005 | 合规检查 | 敏感职业检查 | 非政府敏感岗位 | 命中则要求补充说明 |
| HNW-006 | 材料完整性 | 身份证件 | 身份证正反面照片完整 | 缺失则退回补充 |
| HNW-007 | 材料完整性 | 风险测评问卷 | 已完成风险测评 | 未完成则退回 |

#### 2.2 专业机构开户审核规则

| 规则ID | 规则类别 | 规则名称 | 规则条件 | 审核结果 |
|--------|----------|----------|----------|----------|
| INS-001 | 准入门槛 | 机构存续期 | 成立日期 ≥ 1年 | 不满足则驳回 |
| INS-002 | 准入门槛 | 注册资本 | 注册资本 ≥ 100万元 | 不满足则驳回 |
| INS-003 | 合规检查 | 营业执照有效性 | 营业执照在有效期内 | 过期则驳回 |
| INS-004 | 合规检查 | 工商信息一致性 | 填写信息与工商登记一致 | 不一致则要求说明 |
| INS-005 | 合规检查 | 反洗钱黑名单 | 机构及法人不在黑名单中 | 命中则驳回并上报 |
| INS-006 | 合规检查 | 经营范围匹配 | 经营范围包含投资管理相关内容 | 不匹配则要求说明 |
| INS-007 | 材料完整性 | 营业执照 | 加盖公章的营业执照复印件 | 缺失或不合规则退回 |
| INS-008 | 材料完整性 | 法人身份证 | 法人身份证正反面 | 缺失则退回 |
| INS-009 | 材料完整性 | 授权书 | 联系人授权委托书 | 缺失则退回 |
| INS-010 | 材料完整性 | 公司章程 | 加盖公章的公司章程 | 缺失则退回 |

#### 2.3 家族办公室开户审核规则

| 规则ID | 规则类别 | 规则名称 | 规则条件 | 审核结果 |
|--------|----------|----------|----------|----------|
| FAM-001 | 准入门槛 | 资产规模 | 总资产规模 ≥ 1000万元 | 不满足则驳回 |
| FAM-002 | 准入门槛 | 家族代表资质 | 家族代表具有完全民事行为能力 | 不满足则驳回 |
| FAM-003 | 需求评估 | 投资需求明确 | 投资需求描述 ≥ 50字 | 不满足则退回完善 |
| FAM-004 | 服务匹配 | 私享会安排 | 私享会日期需在未来30天内 | 超过期限则建议调整 |
| FAM-005 | 合规检查 | 资金来源 | 需提供资金来源说明 | 缺失则退回 |
| FAM-006 | 材料完整性 | 家族关系证明 | 家族成员关系证明材料 | 缺失则退回 |
| FAM-007 | 材料完整性 | 资产证明 | 资产规模证明材料 | 缺失则退回 |

#### 2.4 产品开户审核规则

| 规则ID | 规则类别 | 规则名称 | 规则条件 | 审核结果 |
|--------|----------|----------|----------|----------|
| PRO-001 | 准入门槛 | 产品备案 | 已在中国证券投资基金业协会备案 | 未备案则驳回 |
| PRO-002 | 准入门槛 | 产品存续期 | 产品成立日期 ≥ 6个月 | 不满足则驳回 |
| PRO-003 | 合规检查 | 管理人资质 | 管理人具备相应牌照 | 缺失则驳回 |
| PRO-004 | 合规检查 | 托管行资质 | 托管行为持牌金融机构 | 不合规则驳回 |
| PRO-005 | 合规检查 | 产品风险等级 | 产品风险等级与投资者匹配 | 不匹配则提示风险 |
| PRO-006 | 材料完整性 | 备案证明 | 基金业协会备案函 | 缺失则退回 |
| PRO-007 | 材料完整性 | 产品合同 | 产品合同/招募说明书 | 缺失则退回 |
| PRO-008 | 材料完整性 | 托管协议 | 托管协议复印件 | 缺失则退回 |
| PRO-009 | 材料完整性 | 管理人资质 | 管理人营业执照及牌照 | 缺失则退回 |

### 3. 审核评分卡

#### 3.1 风险评分维度

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| 客户资质 | 25% | 资产规模、从业背景、投资经验 |
| 合规风险 | 30% | 黑名单命中、敏感信息、历史违规 |
| 材料完整性 | 20% | 必填材料齐全、材料真实有效 |
| 业务匹配度 | 15% | 投资需求与产品匹配 |
| 操作风险 | 10% | 流程规范性、时效性 |

#### 3.2 评分等级

| 综合得分 | 风险等级 | 建议处理 |
|----------|----------|----------|
| 90-100 | 低风险 | 快速通道，简化审核 |
| 70-89 | 中低风险 | 标准审核流程 |
| 50-69 | 中风险 | 加强审核，额外尽调 |
| 30-49 | 高风险 | 高级审批，风险缓释措施 |
| 0-29 | 极高风险 | 建议拒绝 |

### 4. 审核流程配置表

| 配置项 | 高净值个人 | 专业机构 | 家族办公室 | 产品开户 |
|--------|------------|----------|------------|----------|
| 初审 | 必需 | 必需 | 必需 | 必需 |
| 风控审核 | 必需 | 必需 | 必需 | 必需 |
| 合规审核 | 资产≥1000万时必需 | 必需 | 必需 | 必需 |
| 终审 | 资产≥3000万时必需 | 必需 | 必需 | 必需 |
| 双人复核 | 资产≥5000万时启用 | 必需 | 必需 | 必需 |

### 5. 审核结果处理规则

| 审核结果 | 后续动作 | 通知对象 |
|----------|----------|----------|
| 初审通过 | 进入风控审核 | 申请人、风控专员 |
| 初审驳回 | 退回申请人修改 | 申请人 |
| 风控通过 | 进入合规审核 | 合规专员 |
| 风控驳回 | 退回申请人/驳回申请 | 申请人、主管 |
| 合规通过 | 进入终审/批准 | 审批负责人 |
| 合规驳回 | 退回申请人/驳回申请 | 申请人、主管 |
| 终审批准 | 开户成功，通知客户 | 申请人、客户 |
| 终审驳回 | 申请结束 | 申请人、主管 |

---

## 附录：附件类型定义

| 开户类型 | 附件类型编码 | 附件类型名称 | 是否必填 | 格式要求 |
|----------|--------------|--------------|----------|----------|
| 通用 | ID_CARD_FRONT | 身份证正面 | 是 | JPG/PNG/PDF |
| 通用 | ID_CARD_BACK | 身份证反面 | 是 | JPG/PNG/PDF |
| 高净值个人 | RISK_ASSESSMENT | 风险测评问卷 | 是 | PDF |
| 高净值个人 | ASSET_PROOF | 资产证明 | 是 | PDF |
| 专业机构 | BUSINESS_LICENSE | 营业执照 | 是 | PDF |
| 专业机构 | AUTHORIZATION | 授权委托书 | 是 | PDF |
| 专业机构 | COMPANY_ARTICLES | 公司章程 | 是 | PDF |
| 家族办公室 | FAMILY_RELATION | 家族关系证明 | 是 | PDF |
| 家族办公室 | WEALTH_PROOF | 资产规模证明 | 是 | PDF |
| 产品开户 | REGISTRATION_CERT | 备案证明 | 是 | PDF |
| 产品开户 | PRODUCT_CONTRACT | 产品合同 | 是 | PDF |
| 产品开户 | CUSTODY_AGREEMENT | 托管协议 | 是 | PDF |

---

*文档版本：v1.0*  
*创建日期：2026-03-07*  
*最后更新：2026-03-07*
