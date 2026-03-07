# 员工工作台 - 引入客户模块数据建模方案

## 一、实体关系图（ER图文字描述）

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   员工(Employee) │     │   线索(Lead)    │     │  客户(Customer) │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ PK: employee_id │◄────┤ FK: owner_id    │────►│ PK: customer_id │
│     name        │     │ PK: lead_id     │     │     name        │
│     department  │     │     name        │     │     type        │
│     role        │     │     source_type │     │     status      │
│     email       │     │     status      │     │     industry    │
│     phone       │     │     score       │     │     scale       │
└─────────────────┘     │     ai_tag      │     └─────────────────┘
         ▲              │     created_at  │              ▲
         │              └─────────────────┘              │
         │                       │                        │
         │              ┌────────┴────────┐               │
         │              ▼                 ▼               │
         │       ┌─────────────┐   ┌─────────────┐        │
         │       │ 线索评估     │   │ 线索分配记录 │        │
         │       │(LeadEval)   │   │(LeadAssign) │        │
         │       └─────────────┘   └─────────────┘        │
         │                                                 │
         │       ┌─────────────────┐                      │
         └───────┤ 跟进记录(FollowUp)│◄─────────────────────┘
                 ├─────────────────┤
                 │ PK: follow_id   │
                 │ FK: lead_id     │
                 │ FK: customer_id │
                 │ FK: employee_id │
                 │   follow_type   │
                 │   content       │
                 │   result        │
                 │   next_plan     │
                 └─────────────────┘
         
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  活动(Activity) │     │   渠道(Channel) │     │  转化漏斗阶段    │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ PK: activity_id │     │ PK: channel_id  │     │ PK: stage_id    │
│     name        │     │     name        │     │ FK: lead_id     │
│     type        │     │     type        │     │     stage_name  │
│     start_time  │     │     contact     │     │     enter_time  │
│     end_time    │     │     region      │     │     exit_time   │
│     location    │     │     status      │     │     conversion_ │
│     status      │     └─────────────────┘     │       rate      │
└─────────────────┘                             └─────────────────┘

┌─────────────────┐     ┌─────────────────┐
│   转介绍记录     │     │   官网咨询记录   │
│  (Referral)     │     │ (WebsiteInquiry)│
├─────────────────┤     ├─────────────────┤
│ PK: referral_id │     │ PK: inquiry_id  │
│ FK: referrer_id │     │ FK: lead_id     │
│ FK: lead_id     │     │     page_source │
│     relation    │     │     inquiry_type│
│     reward      │     │     content     │
│     status      │     │     ip_address  │
└─────────────────┘     │     device_type │
                        └─────────────────┘
```

### 关系说明

| 关系 | 类型 | 说明 |
|------|------|------|
| 员工 → 线索 | 1:N | 一个员工可负责多个线索 |
| 线索 → 客户 | 1:1 | 线索转化后成为客户 |
| 线索 → 线索评估 | 1:1 | 每个线索对应一个评估记录 |
| 线索 → 线索分配记录 | 1:N | 一个线索可多次分配 |
| 员工 → 跟进记录 | 1:N | 一个员工可创建多条跟进记录 |
| 线索/客户 → 跟进记录 | 1:N | 可有多条跟进记录 |
| 活动 → 线索 | 1:N | 一个活动可产生多条线索 |
| 渠道 → 线索 | 1:N | 一个渠道可推荐多个线索 |
| 客户 → 转介绍记录 | 1:N | 一个客户可多次转介绍 |
| 线索 → 转化漏斗阶段 | 1:N | 线索经历多个转化阶段 |

---

## 二、数据表结构设计

### 2.1 员工表 (employees)

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| employee_id | VARCHAR(32) | PK, NOT NULL | - | 员工ID |
| name | VARCHAR(50) | NOT NULL | - | 姓名 |
| employee_no | VARCHAR(20) | UNIQUE | - | 工号 |
| department | VARCHAR(50) | NOT NULL | - | 部门 |
| role | TINYINT | NOT NULL | 1 | 角色：1-客户经理，2-团队主管，3-部门经理 |
| email | VARCHAR(100) | UNIQUE | - | 邮箱 |
| phone | VARCHAR(20) | UNIQUE | - | 手机号 |
| status | TINYINT | NOT NULL | 1 | 状态：1-在职，2-离职，3-休假 |
| max_leads | INT | NOT NULL | 50 | 最大负责线索数 |
| created_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 更新时间 |

### 2.2 线索表 (leads)

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| lead_id | VARCHAR(32) | PK, NOT NULL | - | 线索ID |
| name | VARCHAR(100) | NOT NULL | - | 客户名称 |
| contact_name | VARCHAR(50) | - | - | 联系人姓名 |
| contact_phone | VARCHAR(20) | - | - | 联系人电话 |
| contact_email | VARCHAR(100) | - | - | 联系人邮箱 |
| source_type | TINYINT | NOT NULL | - | 来源类型：1-AI挖掘，2-官网咨询，3-转介绍，4-活动获客，5-陌拜，6-渠道推荐 |
| source_detail | VARCHAR(100) | - | - | 来源详情（如活动名称、渠道名称） |
| status | TINYINT | NOT NULL | 1 | 状态：1-待分配，2-跟进中，3-已转化，4-已关闭，5-已失效 |
| score | INT | - | 0 | 评估分数（0-100） |
| priority | TINYINT | NOT NULL | 2 | 优先级：1-高，2-中，3-低 |
| ai_tag | VARCHAR(200) | - | - | AI标签（JSON格式） |
| owner_id | VARCHAR(32) | FK | - | 负责员工ID |
| customer_id | VARCHAR(32) | FK | - | 转化后的客户ID |
| registered_capital | DECIMAL(18,2) | - | - | 注册资本（万元） |
| management_scale | DECIMAL(18,2) | - | - | 管理规模（亿元） |
| established_date | DATE | - | - | 成立日期 |
| investment_style | VARCHAR(50) | - | - | 投资风格 |
| industry | VARCHAR(50) | - | - | 所属行业 |
| region | VARCHAR(50) | - | - | 所在地区 |
| website | VARCHAR(200) | - | - | 官网地址 |
| created_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 更新时间 |
| created_by | VARCHAR(32) | - | - | 创建人ID |

### 2.3 客户表 (customers)

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| customer_id | VARCHAR(32) | PK, NOT NULL | - | 客户ID |
| name | VARCHAR(100) | NOT NULL | - | 客户名称 |
| type | TINYINT | NOT NULL | - | 客户类型：1-公募基金，2-私募基金，3-银行理财，4-券商资管，5-保险资管，6-其他 |
| status | TINYINT | NOT NULL | 1 | 状态：1-潜在客户，2-意向客户，3-签约客户，4-流失客户 |
| level | TINYINT | NOT NULL | 1 | 客户等级：1-A类，2-B类，3-C类，4-D类 |
| industry | VARCHAR(50) | - | - | 所属行业 |
| registered_capital | DECIMAL(18,2) | - | - | 注册资本（万元） |
| management_scale | DECIMAL(18,2) | - | - | 管理规模（亿元） |
| established_date | DATE | - | - | 成立日期 |
| investment_style | VARCHAR(50) | - | - | 投资风格 |
| legal_person | VARCHAR(50) | - | - | 法定代表人 |
| address | VARCHAR(200) | - | - | 注册地址 |
| website | VARCHAR(200) | - | - | 官网地址 |
| primary_contact | VARCHAR(50) | - | - | 主要联系人 |
| primary_phone | VARCHAR(20) | - | - | 联系人电话 |
| primary_email | VARCHAR(100) | - | - | 联系人邮箱 |
| account_manager_id | VARCHAR(32) | FK | - | 客户经理ID |
| lead_id | VARCHAR(32) | FK | - | 来源线索ID |
| contract_count | INT | NOT NULL | 0 | 签约合同数 |
| total_contract_amount | DECIMAL(18,2) | NOT NULL | 0 | 合同总金额（万元） |
| first_contract_date | DATE | - | - | 首次签约日期 |
| last_contact_date | DATE | - | - | 最近联系日期 |
| created_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 更新时间 |

### 2.4 线索评估表 (lead_evaluations)

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| evaluation_id | VARCHAR(32) | PK, NOT NULL | - | 评估ID |
| lead_id | VARCHAR(32) | FK, NOT NULL, UNIQUE | - | 线索ID |
| total_score | INT | NOT NULL | 0 | 总评分（0-100） |
| capital_score | INT | - | 0 | 资本实力分（0-25） |
| scale_score | INT | - | 0 | 规模分（0-25） |
| history_score | INT | - | 0 | 历史分（0-20） |
| style_score | INT | - | 0 | 风格匹配分（0-20） |
| ai_score | INT | - | 0 | AI潜力分（0-10） |
| evaluation_level | TINYINT | NOT NULL | 2 | 评估等级：1-高价值，2-中价值，3-低价值 |
| evaluation_reason | TEXT | - | - | 评估说明 |
| evaluated_by | VARCHAR(32) | - | - | 评估人ID（AI评估为空） |
| evaluated_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 评估时间 |
| ai_model | VARCHAR(50) | - | - | AI模型版本 |
| ai_confidence | DECIMAL(5,2) | - | - | AI置信度（0-1） |

### 2.5 线索分配记录表 (lead_assignments)

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| assignment_id | VARCHAR(32) | PK, NOT NULL | - | 分配记录ID |
| lead_id | VARCHAR(32) | FK, NOT NULL | - | 线索ID |
| from_employee_id | VARCHAR(32) | FK | - | 原负责人ID |
| to_employee_id | VARCHAR(32) | FK, NOT NULL | - | 新负责人ID |
| assign_type | TINYINT | NOT NULL | - | 分配类型：1-自动分配，2-手动分配，3-主动认领，4-重新分配 |
| assign_reason | VARCHAR(200) | - | - | 分配原因 |
| assigned_by | VARCHAR(32) | - | - | 分配操作人ID |
| assigned_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 分配时间 |
| accepted_at | DATETIME | - | - | 接受时间 |
| status | TINYINT | NOT NULL | 1 | 状态：1-待确认，2-已接受，3-已拒绝 |
| reject_reason | VARCHAR(200) | - | - | 拒绝原因 |

### 2.6 跟进记录表 (follow_up_records)

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| follow_id | VARCHAR(32) | PK, NOT NULL | - | 跟进记录ID |
| lead_id | VARCHAR(32) | FK | - | 线索ID |
| customer_id | VARCHAR(32) | FK | - | 客户ID |
| employee_id | VARCHAR(32) | FK, NOT NULL | - | 跟进人ID |
| follow_type | TINYINT | NOT NULL | - | 跟进类型：1-电话，2-邮件，3-面谈，4-微信，5-陌拜，6-活动 |
| follow_date | DATE | NOT NULL | - | 跟进日期 |
| content | TEXT | NOT NULL | - | 跟进内容 |
| result | TINYINT | NOT NULL | 1 | 跟进结果：1-有效沟通，2-需求确认，3-方案提交，4-商务谈判，5-成功签约，6-暂无意向，7-拒绝 |
| customer_feedback | VARCHAR(500) | - | - | 客户反馈 |
| next_plan | VARCHAR(500) | - | - | 下一步计划 |
| next_follow_date | DATE | - | - | 下次跟进日期 |
| attachments | VARCHAR(500) | - | - | 附件（JSON格式文件列表） |
| location | VARCHAR(100) | - | - | 拜访地点（陌拜/面谈时填写） |
| duration_minutes | INT | - | - | 沟通时长（分钟） |
| created_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |

### 2.7 活动表 (activities)

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| activity_id | VARCHAR(32) | PK, NOT NULL | - | 活动ID |
| name | VARCHAR(100) | NOT NULL | - | 活动名称 |
| type | TINYINT | NOT NULL | - | 活动类型：1-线上路演，2-线下沙龙，3-策略会，4-客户答谢会，5-培训会，6-其他 |
| start_time | DATETIME | NOT NULL | - | 开始时间 |
| end_time | DATETIME | NOT NULL | - | 结束时间 |
| location | VARCHAR(200) | - | - | 活动地点 |
| online_url | VARCHAR(200) | - | - | 线上链接 |
| organizer | VARCHAR(50) | - | - | 主办方 |
| budget | DECIMAL(18,2) | - | - | 预算金额 |
| expected_participants | INT | - | - | 预计参与人数 |
| actual_participants | INT | NOT NULL | 0 | 实际参与人数 |
| leads_generated | INT | NOT NULL | 0 | 产生线索数 |
| status | TINYINT | NOT NULL | 1 | 状态：1-策划中，2-报名中，3-进行中，4-已结束，5-已取消 |
| description | TEXT | - | - | 活动描述 |
| created_by | VARCHAR(32) | FK | - | 创建人ID |
| created_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 更新时间 |

### 2.8 渠道表 (channels)

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| channel_id | VARCHAR(32) | PK, NOT NULL | - | 渠道ID |
| name | VARCHAR(100) | NOT NULL | - | 渠道名称 |
| type | TINYINT | NOT NULL | - | 渠道类型：1-合作机构，2-行业协会，3-媒体平台，4-第三方数据，5-个人推荐 |
| contact_name | VARCHAR(50) | - | - | 联系人姓名 |
| contact_phone | VARCHAR(20) | - | - | 联系人电话 |
| contact_email | VARCHAR(100) | - | - | 联系人邮箱 |
| region | VARCHAR(50) | - | - | 覆盖区域 |
| cooperation_model | VARCHAR(50) | - | - | 合作模式 |
| commission_rate | DECIMAL(5,2) | - | - | 佣金比例 |
| leads_count | INT | NOT NULL | 0 | 推荐线索数 |
| conversion_count | INT | NOT NULL | 0 | 转化成功数 |
| conversion_rate | DECIMAL(5,2) | NOT NULL | 0 | 转化率 |
| status | TINYINT | NOT NULL | 1 | 状态：1-合作中，2-暂停合作，3-终止合作 |
| created_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 更新时间 |

### 2.9 转介绍记录表 (referrals)

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| referral_id | VARCHAR(32) | PK, NOT NULL | - | 转介绍记录ID |
| referrer_customer_id | VARCHAR(32) | FK, NOT NULL | - | 介绍人客户ID |
| referred_lead_id | VARCHAR(32) | FK, NOT NULL | - | 被介绍线索ID |
| relation_type | TINYINT | NOT NULL | - | 关系类型：1-合作伙伴，2-股东关系，3-业务往来，4-个人关系，5-其他 |
| referral_date | DATE | NOT NULL | - | 转介绍日期 |
| reward_amount | DECIMAL(18,2) | - | - | 奖励金额 |
| reward_status | TINYINT | NOT NULL | 1 | 奖励状态：1-待发放，2-已发放，3-无需奖励 |
| notes | VARCHAR(500) | - | - | 备注说明 |
| status | TINYINT | NOT NULL | 1 | 状态：1-有效，2-已转化，3-已失效 |
| created_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |

### 2.10 官网咨询记录表 (website_inquiries)

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| inquiry_id | VARCHAR(32) | PK, NOT NULL | - | 咨询记录ID |
| lead_id | VARCHAR(32) | FK | - | 关联线索ID |
| page_source | VARCHAR(200) | NOT NULL | - | 来源页面 |
| inquiry_type | TINYINT | NOT NULL | - | 咨询类型：1-产品咨询，2-合作咨询，3-技术支持，4-投诉建议，5-其他 |
| content | TEXT | NOT NULL | - | 咨询内容 |
| contact_name | VARCHAR(50) | - | - | 联系人姓名 |
| contact_phone | VARCHAR(20) | - | - | 联系人电话 |
| contact_email | VARCHAR(100) | - | - | 联系人邮箱 |
| company_name | VARCHAR(100) | - | - | 公司名称 |
| ip_address | VARCHAR(50) | - | - | IP地址 |
| device_type | VARCHAR(50) | - | - | 设备类型 |
| browser_info | VARCHAR(200) | - | - | 浏览器信息 |
| status | TINYINT | NOT NULL | 1 | 状态：1-待处理，2-已处理，3-已转线索，4-无效咨询 |
| handler_id | VARCHAR(32) | FK | - | 处理人ID |
| handled_at | DATETIME | - | - | 处理时间 |
| handle_notes | VARCHAR(500) | - | - | 处理备注 |
| created_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |

### 2.11 转化漏斗阶段表 (conversion_funnel_stages)

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| stage_id | VARCHAR(32) | PK, NOT NULL | - | 阶段ID |
| lead_id | VARCHAR(32) | FK, NOT NULL | - | 线索ID |
| stage_name | VARCHAR(50) | NOT NULL | - | 阶段名称 |
| stage_order | TINYINT | NOT NULL | - | 阶段顺序 |
| enter_time | DATETIME | NOT NULL | - | 进入时间 |
| exit_time | DATETIME | - | - | 离开时间 |
| duration_hours | INT | - | - | 停留时长（小时） |
| conversion_rate | DECIMAL(5,2) | - | - | 该阶段转化率 |
| drop_reason | VARCHAR(200) | - | - | 流失原因 |
| notes | VARCHAR(500) | - | - | 备注 |
| created_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |

### 2.12 陌拜记录表 (cold_visit_records)

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| visit_id | VARCHAR(32) | PK, NOT NULL | - | 陌拜记录ID |
| lead_id | VARCHAR(32) | FK | - | 关联线索ID |
| employee_id | VARCHAR(32) | FK, NOT NULL | - | 陌拜人员ID |
| target_company | VARCHAR(100) | NOT NULL | - | 目标公司 |
| target_address | VARCHAR(200) | - | - | 目标地址 |
| visit_date | DATE | NOT NULL | - | 陌拜日期 |
| visit_result | TINYINT | NOT NULL | - | 陌拜结果：1-成功对接，2-留下资料，3-预约回访，4-拒绝见面，5-未找到联系人 |
| contact_name | VARCHAR(50) | - | - | 对接人姓名 |
| contact_title | VARCHAR(50) | - | - | 对接人职位 |
| contact_phone | VARCHAR(20) | - | - | 对接人电话 |
| feedback | VARCHAR(500) | - | - | 反馈内容 |
| next_plan | VARCHAR(200) | - | - | 下一步计划 |
| photos | VARCHAR(500) | - | - | 现场照片（JSON格式） |
| created_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |

---

## 三、关键字段说明

### 3.1 线索状态 (leads.status)

| 状态值 | 状态名称 | 说明 |
|--------|----------|------|
| 1 | 待分配 | 线索录入后等待分配 |
| 2 | 跟进中 | 已分配给客户经理，正在跟进 |
| 3 | 已转化 | 线索已成功转化为客户 |
| 4 | 已关闭 | 线索关闭，不再跟进 |
| 5 | 已失效 | 线索失效（联系不上、无需求等） |

### 3.2 线索来源类型 (leads.source_type)

| 类型值 | 类型名称 | 对应模块 | 说明 |
|--------|----------|----------|------|
| 1 | AI挖掘 | AI潜客挖掘 | AI算法挖掘的潜在线索 |
| 2 | 官网咨询 | 找过来的客户 | 通过官网咨询表单录入 |
| 3 | 转介绍 | 找过来的客户 | 现有客户转介绍 |
| 4 | 活动获客 | 找过来的客户 | 通过市场活动获取 |
| 5 | 陌拜 | 主动出击获客 | 主动上门拜访获取 |
| 6 | 渠道推荐 | 主动出击获客 | 合作渠道推荐 |

### 3.3 客户类型 (customers.type)

| 类型值 | 类型名称 | 示例 |
|--------|----------|------|
| 1 | 公募基金 | 易方达基金、华夏基金、南方基金 |
| 2 | 私募基金 | 高毅资产、景林资产 |
| 3 | 银行理财 | 华夏理财、招银理财 |
| 4 | 券商资管 | 中信证券资管、华泰资管 |
| 5 | 保险资管 | 中国人寿资管、平安资管 |
| 6 | 其他 | 信托、期货资管等 |

### 3.4 客户等级 (customers.level)

| 等级值 | 等级名称 | 评估标准 |
|--------|----------|----------|
| 1 | A类（核心客户） | 评估分数≥90分，或管理规模≥1000亿 |
| 2 | B类（重点客户） | 评估分数80-89分，或管理规模500-1000亿 |
| 3 | C类（普通客户） | 评估分数60-79分，或管理规模100-500亿 |
| 4 | D类（潜在客户） | 评估分数<60分，或管理规模<100亿 |

### 3.5 跟进结果类型 (follow_up_records.result)

| 结果值 | 结果名称 | 说明 |
|--------|----------|------|
| 1 | 有效沟通 | 与客户建立有效联系 |
| 2 | 需求确认 | 确认客户具体需求 |
| 3 | 方案提交 | 已提交产品/服务方案 |
| 4 | 商务谈判 | 进入商务条款谈判 |
| 5 | 成功签约 | 已完成合同签署 |
| 6 | 暂无意向 | 客户当前无明确需求 |
| 7 | 拒绝 | 客户明确拒绝合作 |

### 3.6 AI标签格式 (leads.ai_tag)

```json
{
  "tags": ["高分红偏好", "量化策略", "稳健型"],
  "industries": ["科技", "医药"],
  "risk_preference": "中低风险",
  "investment_period": "中长期",
  "potential_score": 85,
  "recommendation": "推荐固收+产品"
}
```

---

## 四、业务规则定义

### 4.1 客户评估规则

#### 4.1.1 评分维度与权重

| 评分维度 | 权重 | 满分 | 评分规则 |
|----------|------|------|----------|
| 资本实力 | 25% | 25分 | 注册资本≥50亿：25分；30-50亿：20分；10-30亿：15分；5-10亿：10分；<5亿：5分 |
| 管理规模 | 25% | 25分 | 管理规模≥1000亿：25分；500-1000亿：20分；200-500亿：15分；50-200亿：10分；<50亿：5分 |
| 成立年限 | 20% | 20分 | 成立≥20年：20分；10-20年：15分；5-10年：10分；3-5年：5分；<3年：2分 |
| 风格匹配 | 20% | 20分 | 与我司产品线高度匹配：20分；较匹配：15分；一般：10分；不匹配：0分 |
| AI潜力 | 10% | 10分 | AI模型预测潜力≥0.9：10分；0.8-0.9：8分；0.7-0.8：6分；0.6-0.7：4分；<0.6：2分 |

#### 4.1.2 评估等级划分

| 总分范围 | 评估等级 | 处理策略 |
|----------|----------|----------|
| 90-100 | 高价值客户（S级） | 优先分配，资深客户经理跟进，48小时内首次触达 |
| 80-89 | 中价值客户（A级） | 正常分配，普通客户经理跟进，72小时内首次触达 |
| 60-79 | 一般客户（B级） | 批量处理，定期培育，7天内首次触达 |
| <60 | 低价值客户（C级） | 进入公海池，自动化营销触达 |

### 4.2 线索分配规则

#### 4.2.1 自动分配规则

```
IF 线索.评估等级 = '高价值客户' THEN
    分配给：该领域资深客户经理（负责客户数<30）
    分配方式：智能匹配 + 手动确认
ELSE IF 线索.评估等级 = '中价值客户' THEN
    分配给：普通客户经理（负责客户数<50）
    分配方式：轮询分配
ELSE IF 线索.来源类型 = '转介绍' THEN
    优先分配给：原客户关系维护人员
ELSE IF 线索.来源类型 = '渠道推荐' THEN
    分配给：对应渠道负责人
ELSE
    进入公海池，等待认领
```

#### 4.2.2 分配上限规则

| 员工角色 | 最大线索数 | 最大客户数 |
|----------|------------|------------|
| 资深客户经理 | 30 | 50 |
| 普通客户经理 | 50 | 80 |
| 初级客户经理 | 30 | 40 |
| 团队主管 | 20（仅重点客户） | 30 |

### 4.3 跟进时效规则

| 线索等级 | 首次跟进时效 | 跟进频率 | 未跟进预警 |
|----------|--------------|----------|------------|
| S级（≥90分） | 48小时内 | 每周至少1次 | 超72小时未跟进 |
| A级（80-89分） | 72小时内 | 每两周至少1次 | 超7天未跟进 |
| B级（60-79分） | 7天内 | 每月至少1次 | 超14天未跟进 |
| C级（<60分） | 14天内 | 按需跟进 | 超30天未跟进 |

### 4.4 转化漏斗阶段定义

| 阶段顺序 | 阶段名称 | 定义 | 成功标准 |
|----------|----------|------|----------|
| 1 | 线索获取 | 获得客户基础信息 | 完成客户建档 |
| 2 | 需求确认 | 与客户建立联系，了解需求 | 完成首次有效沟通 |
| 3 | 方案提交 | 向客户提交产品/服务方案 | 客户收到并确认方案 |
| 4 | 商务谈判 | 就合作条款进行谈判 | 达成初步合作意向 |
| 5 | 合同签署 | 完成合同签署流程 | 正式签约 |
| 6 | 客户 onboarding | 完成客户上线/交付 | 客户开始使用产品/服务 |

### 4.5 线索失效规则

以下情况可将线索标记为"已失效"：

1. **联系失效**：连续3次（间隔≥3天）无法联系到客户
2. **需求失效**：客户明确表示无需求且未来6个月内无可能
3. **竞品签约**：客户已与竞品签署独家合作协议
4. **超期未跟进**：超过30天未有任何跟进记录
5. **信息错误**：客户关键信息（如公司名称、联系方式）经核实为虚假信息

### 4.6 数据质量规则

| 字段类别 | 必填字段 | 数据校验规则 |
|----------|----------|--------------|
| 基本信息 | 客户名称、来源类型 | 名称去重校验，同一名称无法重复录入 |
| 联系信息 | 至少一项联系方式 | 手机/电话格式校验，邮箱格式校验 |
| 评估信息 | 注册资本、管理规模 | 数值范围校验，单位统一为万元/亿元 |
| 跟进记录 | 跟进类型、内容、结果 | 内容长度≥10字 |

### 4.7 权限规则

| 角色 | 数据权限 | 操作权限 |
|------|----------|----------|
| 客户经理 | 查看/编辑自己负责的线索和客户 | 创建跟进记录，更新客户信息，提交转化申请 |
| 团队主管 | 查看/编辑团队所有线索和客户 | 分配线索，审批转化，查看团队报表 |
| 部门经理 | 查看部门所有数据 | 分配线索，数据导出，配置规则 |
| 系统管理员 | 全部数据 | 全部操作 |

---

## 五、索引设计建议

| 表名 | 索引字段 | 索引类型 | 说明 |
|------|----------|----------|------|
| leads | (status, score) | 复合索引 | 用于线索筛选和排序 |
| leads | (owner_id, status) | 复合索引 | 用于查询员工负责的线索 |
| leads | (source_type, created_at) | 复合索引 | 用于按来源统计 |
| customers | (account_manager_id, status) | 复合索引 | 用于查询员工负责的客户 |
| customers | (level, type) | 复合索引 | 用于客户分类统计 |
| follow_up_records | (lead_id, follow_date) | 复合索引 | 用于查询线索跟进历史 |
| follow_up_records | (employee_id, follow_date) | 复合索引 | 用于查询员工跟进记录 |
| lead_evaluations | (total_score) | 单列索引 | 用于按分数排序 |
| conversion_funnel_stages | (lead_id, stage_order) | 复合索引 | 用于查询线索转化路径 |
| prospecting_results | (match_score) | 单列索引 | 用于挖掘结果排序 |
| prospecting_results | (data_source, status) | 复合索引 | 用于按数据源筛选 |

---

## 五、潜客挖掘数据模型（新增）

### 5.1 潜客挖掘数据源表 (prospecting_data_sources)

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| source_id | VARCHAR(32) | PK, NOT NULL | - | 数据源ID |
| source_name | VARCHAR(50) | NOT NULL | - | 数据源名称 |
| source_type | TINYINT | NOT NULL | - | 类型：1-内部库，2-朝阳永续，3-基金业协会 |
| api_endpoint | VARCHAR(255) | NULL | - | API接口地址 |
| auth_type | VARCHAR(20) | NULL | - | 认证方式：token/apikey/oauth |
| sync_frequency | VARCHAR(20) | NOT NULL | 'daily' | 同步频率：realtime/hourly/daily/weekly |
| last_sync_time | DATETIME | NULL | - | 上次同步时间 |
| status | TINYINT | NOT NULL | 1 | 状态：1-启用，0-停用 |
| created_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |

### 5.2 潜客挖掘结果表 (prospecting_results)

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| result_id | VARCHAR(32) | PK, NOT NULL | - | 挖掘结果ID |
| data_source | TINYINT | NOT NULL | - | 数据源类型：1-内部库，2-朝阳永续，3-基金业协会 |
| external_id | VARCHAR(64) | NOT NULL | - | 外部数据源ID（如私募备案编号） |
| institution_name | VARCHAR(200) | NOT NULL | - | 机构名称 |
| institution_type | TINYINT | NOT NULL | - | 机构类型：1-私募，2-公募，3-资管，4-其他 |
| aum_range | VARCHAR(50) | NULL | - | 管理规模区间 |
| investment_strategy | VARCHAR(100) | NULL | - | 投资策略 |
| registration_date | DATE | NULL | - | 备案/注册日期 |
| compliance_status | TINYINT | NOT NULL | 1 | 合规状态：1-正常，2-异常，3-注销 |
| match_score | DECIMAL(5,2) | NOT NULL | 0.00 | 匹配度评分（0-100） |
| match_reason | TEXT | NULL | - | 匹配原因说明 |
| recommend_priority | TINYINT | NOT NULL | 3 | 推荐优先级：1-高，2-中，3-低 |
| status | TINYINT | NOT NULL | 0 | 处理状态：0-待处理，1-已采纳，2-已忽略，3-已转化 |
| assigned_to | VARCHAR(32) | NULL | - | 分配给员工ID |
| assigned_at | DATETIME | NULL | - | 分配时间 |
| raw_data_json | JSON | NULL | - | 原始数据JSON存储 |
| created_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 挖掘时间 |
| updated_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 更新时间 |

### 5.3 挖掘规则配置表 (prospecting_rules)

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| rule_id | VARCHAR(32) | PK, NOT NULL | - | 规则ID |
| rule_name | VARCHAR(100) | NOT NULL | - | 规则名称 |
| rule_type | TINYINT | NOT NULL | - | 规则类型：1-规模匹配，2-策略匹配，3-区域匹配，4-合规筛选 |
| data_source | TINYINT | NOT NULL | 0 | 适用数据源：0-全部，1-内部库，2-朝阳永续，3-基金业协会 |
| condition_json | JSON | NOT NULL | - | 规则条件（JSON格式） |
| score_weight | DECIMAL(3,2) | NOT NULL | 0.10 | 评分权重（0-1） |
| priority | INT | NOT NULL | 100 | 规则优先级（数字越小优先级越高） |
| status | TINYINT | NOT NULL | 1 | 状态：1-启用，0-停用 |
| created_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 更新时间 |

---

## 六、潜客挖掘规则设计

### 6.1 挖掘规则总览

```yaml
挖掘规则配置:
  版本: "v1.0"
  生效日期: "2026-03-07"
  
  规则分类:
    - 规模匹配规则
    - 策略匹配规则
    - 区域匹配规则
    - 合规筛选规则
    - 活跃度评估规则
    - 竞争态势规则
  
  评分机制:
    满分: 100分
    及格线: 60分
    优先级划分:
      高优先级: ≥80分
      中优先级: 60-79分
      低优先级: <60分
```

### 6.2 规模匹配规则（权重25%）

| 规则ID | 规则名称 | 条件 | 评分权重 |
|--------|----------|------|----------|
| SCALE_001 | 大型机构识别 | 管理规模 ≥ 50亿 | 25分 |
| SCALE_002 | 中型机构识别 | 管理规模 10-50亿 | 18分 |
| SCALE_003 | 成长型机构识别 | 管理规模 1-10亿且成立<3年 | 15分 |
| SCALE_004 | 小型机构识别 | 管理规模 < 1亿 | 8分 |

**数据源映射：**
- 朝阳永续：取最新季度管理规模数据
- 基金业协会：取备案时申报规模，结合产品数量推算
- 内部库：取历史成交最大规模或当前持仓规模

### 6.3 策略匹配规则（权重25%）

| 规则ID | 规则名称 | 条件 | 匹配度 |
|--------|----------|------|--------|
| STRATEGY_001 | 量化策略匹配 | 投资策略含"量化""程序化" | 高匹配（25分） |
| STRATEGY_002 | 权益策略匹配 | 投资策略含"股票""权益" | 高匹配（25分） |
| STRATEGY_003 | 债券策略匹配 | 投资策略含"债券""固收" | 中匹配（18分） |
| STRATEGY_004 | 混合策略匹配 | 投资策略含"混合""多策略" | 中匹配（18分） |
| STRATEGY_005 | 衍生品策略匹配 | 投资策略含"期货""期权""衍生品" | 高匹配（25分） |

**数据源映射：**
- 朝阳永续：fund_strategy字段
- 基金业协会：投资策略描述
- 内部库：客户历史交易品种偏好

### 6.4 区域匹配规则（权重15%）

| 规则ID | 规则名称 | 条件 | 评分 |
|--------|----------|------|------|
| REGION_001 | 核心区域 | 注册地在北京/上海/深圳 | 15分 |
| REGION_002 | 重点区域 | 注册地在杭州/广州/成都/南京 | 12分 |
| REGION_003 | 一般区域 | 其他省会城市 | 8分 |
| REGION_004 | 就近服务 | 与当前客户经理同区域 | +5分（额外加分） |

### 6.5 合规筛选规则（权重20%）

| 规则ID | 规则名称 | 条件 | 处理方式 |
|--------|----------|------|----------|
| COMPLIANCE_001 | 正常机构 | 合规状态=正常，无处罚记录 | 正常评分（20分） |
| COMPLIANCE_002 | 预警机构 | 近1年内有监管关注函 | 扣分10分，标记预警 |
| COMPLIANCE_003 | 高风险机构 | 近1年内有监管处罚 | 直接过滤，不推荐 |
| COMPLIANCE_004 | 新备案机构 | 备案时间<6个月 | 加分5分（新客拓展） |
| COMPLIANCE_005 | 即将到期 | 备案资质剩余<3个月 | 扣分5分，标记关注 |

**数据源映射：**
- 基金业协会：诚信信息公示、备案状态
- 朝阳永续：机构诚信标签
- 内部库：公司合规风控黑名单

### 6.6 活跃度评估规则（权重10%）

| 规则ID | 规则名称 | 条件 | 评分 |
|--------|----------|------|------|
| ACTIVITY_001 | 高活跃 | 近6个月新发产品≥3只 | 10分 |
| ACTIVITY_002 | 中活跃 | 近6个月新发产品1-2只 | 6分 |
| ACTIVITY_003 | 低活跃 | 近6个月无新发产品 | 2分 |
| ACTIVITY_004 | 沉睡唤醒 | 历史活跃但近1年无新发 | 5分（特殊标记） |

**数据源映射：**
- 朝阳永续：产品备案时间序列
- 基金业协会：产品备案公示

### 6.7 竞争态势规则（权重5%）

| 规则ID | 规则名称 | 条件 | 评分 |
|--------|----------|------|------|
| COMPETE_001 | 空白客户 | 无券商合作记录 | 5分 |
| COMPETE_002 | 他行客户 | 有合作但可替换 | 3分 |
| COMPETE_003 | 我行客户 | 已在我司开户 | 过滤排除 |
| COMPETE_004 | 流失风险 | 近6个月交易量下降>50% | 4分（挽回机会） |

---

## 七、挖掘流程设计

### 7.1 批量挖掘流程

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  数据源同步   │───▶│  数据清洗    │───▶│  规则匹配    │
│  (定时任务)   │    │  (标准化)    │    │  (评分计算)  │
└──────────────┘    └──────────────┘    └──────────────┘
                                               │
                                               ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  结果通知    │◀───│  人工审核    │◀───│  结果排序    │
│  (推送员工)   │    │  (确认/忽略)  │    │  (优先级)    │
└──────────────┘    └──────────────┘    └──────────────┘
```

### 7.2 实时挖掘流程

触发条件：
- 新员工入职（分配区域客户）
- 客户主动询价（官网/电话）
- 市场活动报名（展会/路演）
- 竞品客户流失预警

处理逻辑：
1. 实时查询三大数据源
2. 即时计算匹配度
3. 推送给责任员工
4. 24小时内必须响应

---

## 八、数据字典附录

### 6.1 投资风格枚举

- 价值投资
- 成长投资
- 指数跟踪
- 量化投资
- 固定收益
- 混合型
- 另类投资

### 6.2 行业枚举

- 金融服务
- 科技/互联网
- 医药健康
- 消费零售
- 制造业
- 能源化工
- 房地产
- 其他

### 6.3 地区枚举

- 北京
- 上海
- 深圳
- 广州
- 杭州
- 成都
- 其他城市

---

**文档版本**: v1.0  
**创建日期**: 2026-03-07  
**适用模块**: 员工工作台 - 引入客户模块
