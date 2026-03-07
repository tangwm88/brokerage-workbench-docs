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

---

## 六、数据字典附录

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

---

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

---

# 员工工作台 - 交易服务模块数据建模方案

## 目录
1. [实体关系图（ER图）](#1-实体关系图er图)
2. [数据表结构设计](#2-数据表结构设计)
3. [订单状态流转图](#3-订单状态流转图)
4. [异常检测规则定义](#4-异常检测规则定义)

---

## 1. 实体关系图（ER图）

### 1.1 实体关系概述

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           交易服务模块实体关系图                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  系统配置表      │      │   风控规则表     │      │  交易限额表      │
│  sys_config     │◄────►│  risk_rules     │◄────►│ trade_limits    │
└─────────────────┘      └─────────────────┘      └─────────────────┘
         │                       │                        │
         │                       │                        │
         └───────────────────────┴────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              订单核心实体                                         │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐    ┌─────────────┐ │
│  │   母订单表     │───►│   子订单表     │───►│   成交明细     │    │  订单快照    │ │
│  │ parent_orders │1:N │ child_orders  │1:N │  executions   │    │order_snapshots│ │
│  └───────────────┘    └───────────────┘    └───────────────┘    └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            分析与报告实体                                         │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐    ┌─────────────┐ │
│  │   滑点分析     │    │  成交量分布    │    │  执行效率评估   │    │  交易统计    │ │
│  │ slippage_anal │    │ volume_dist   │    │ exec_efficiency│    │trade_stats  │ │
│  └───────────────┘    └───────────────┘    └───────────────┘    └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
         │
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            异常处理实体                                           │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐    ┌─────────────┐ │
│  │   异常检测规则  │◄───│   异常记录     │───►│   告警通知     │    │  处理记录    │ │
│  │ abnormal_rules │   │  abnormal_logs │    │   alerts      │    │process_logs │ │
│  └───────────────┘    └───────────────┘    └───────────────┘    └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 实体间关系详解

| 关系 | 主表 | 从表 | 关系类型 | 说明 |
|------|------|------|----------|------|
| 配置依赖 | sys_config | risk_rules | 1:1 | 系统配置关联风控规则 |
| 限额绑定 | trade_limits | parent_orders | 1:N | 交易限额约束母订单 |
| 订单层级 | parent_orders | child_orders | 1:N | 母订单拆分为多个子订单 |
| 执行关联 | child_orders | executions | 1:N | 子订单产生成交明细 |
| 快照记录 | parent_orders | order_snapshots | 1:N | 记录订单状态变更快照 |
| 异常关联 | abnormal_rules | abnormal_logs | 1:N | 规则触发产生异常记录 |
| 告警绑定 | abnormal_logs | alerts | 1:1 | 异常产生告警通知 |
| 处理追踪 | abnormal_logs | process_logs | 1:N | 异常处理过程记录 |

---

## 2. 数据表结构设计

### 2.1 系统配置表

#### 2.1.1 系统基础配置表 (sys_config)

| 字段名 | 类型 | 长度 | 是否为空 | 默认值 | 约束 | 说明 |
|--------|------|------|----------|--------|------|------|
| id | BIGINT | - | 否 | 自增 | PRIMARY KEY | 主键ID |
| config_key | VARCHAR | 64 | 否 | - | UNIQUE | 配置键 |
| config_value | TEXT | - | 是 | NULL | - | 配置值(JSON格式) |
| config_type | VARCHAR | 32 | 否 | 'string' | - | 配置类型:string/number/json/boolean |
| description | VARCHAR | 256 | 是 | NULL | - | 配置说明 |
| is_active | TINYINT | 1 | 否 | 1 | - | 是否启用:0-禁用,1-启用 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | ON UPDATE | 更新时间 |
| created_by | VARCHAR | 64 | 是 | NULL | - | 创建人 |
| updated_by | VARCHAR | 64 | 是 | NULL | - | 更新人 |

**索引:**
- `idx_config_key`: config_key
- `idx_config_type`: config_type
- `idx_is_active`: is_active

---

#### 2.1.2 TWAP算法参数表 (twap_config)

| 字段名 | 类型 | 长度 | 是否为空 | 默认值 | 约束 | 说明 |
|--------|------|------|----------|--------|------|------|
| id | BIGINT | - | 否 | 自增 | PRIMARY KEY | 主键ID |
| config_name | VARCHAR | 64 | 否 | - | UNIQUE | 配置名称 |
| slice_interval | INT | - | 否 | 300 | - | 切片间隔(秒) |
| slice_variance | DECIMAL | (5,2) | 否 | 0.10 | - | 切片方差(0-1) |
| price_limit_pct | DECIMAL | (5,2) | 否 | 0.02 | - | 价格限制百分比 |
| volume_limit_pct | DECIMAL | (5,2) | 否 | 0.30 | - | 成交量限制百分比 |
| participation_rate | DECIMAL | (5,2) | 否 | 0.10 | - | 参与率 |
| start_time | TIME | - | 否 | '09:30:00' | - | 开始时间 |
| end_time | TIME | - | 否 | '15:00:00' | - | 结束时间 |
| is_aggressive | TINYINT | 1 | 否 | 0 | - | 是否激进模式 |
| is_active | TINYINT | 1 | 否 | 1 | - | 是否启用 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | ON UPDATE | 更新时间 |

**索引:**
- `idx_config_name`: config_name
- `idx_is_active`: is_active

---

### 2.2 风控与限额表

#### 2.2.1 风控规则表 (risk_rules)

| 字段名 | 类型 | 长度 | 是否为空 | 默认值 | 约束 | 说明 |
|--------|------|------|----------|--------|------|------|
| id | BIGINT | - | 否 | 自增 | PRIMARY KEY | 主键ID |
| rule_code | VARCHAR | 32 | 否 | - | UNIQUE | 规则编码 |
| rule_name | VARCHAR | 128 | 否 | - | - | 规则名称 |
| rule_type | VARCHAR | 32 | 否 | - | - | 规则类型:position/amount/frequency/velocity |
| rule_level | VARCHAR | 16 | 否 | 'medium' | - | 规则级别:low/medium/high/critical |
| trigger_condition | JSON | - | 否 | - | - | 触发条件(JSON) |
| action_type | VARCHAR | 32 | 否 | 'alert' | - | 动作类型:alert/block/notify/escalate |
| action_config | JSON | - | 是 | NULL | - | 动作配置 |
| effective_date | DATE | - | 否 | - | - | 生效日期 |
| expiry_date | DATE | - | 是 | NULL | - | 失效日期 |
| priority | INT | - | 否 | 100 | - | 优先级(数值越小优先级越高) |
| is_active | TINYINT | 1 | 否 | 1 | - | 是否启用 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | ON UPDATE | 更新时间 |
| created_by | VARCHAR | 64 | 是 | NULL | - | 创建人 |

**索引:**
- `idx_rule_code`: rule_code
- `idx_rule_type`: rule_type
- `idx_rule_level`: rule_level
- `idx_is_active`: is_active
- `idx_priority`: priority

---

#### 2.2.2 交易限额表 (trade_limits)

| 字段名 | 类型 | 长度 | 是否为空 | 默认值 | 约束 | 说明 |
|--------|------|------|----------|--------|------|------|
| id | BIGINT | - | 否 | 自增 | PRIMARY KEY | 主键ID |
| limit_type | VARCHAR | 32 | 否 | - | - | 限额类型:account/instrument/strategy |
| limit_scope | VARCHAR | 64 | 否 | - | - | 限额范围:用户ID/股票代码/策略ID |
| single_order_limit | DECIMAL | (18,4) | 是 | NULL | - | 单笔订单限额 |
| daily_order_limit | DECIMAL | (18,4) | 是 | NULL | - | 日累计订单限额 |
| daily_amount_limit | DECIMAL | (18,4) | 是 | NULL | - | 日累计金额限额 |
| position_limit | DECIMAL | (18,4) | 是 | NULL | - | 持仓限额 |
| cancel_limit | INT | - | 是 | NULL | - | 日撤单次数限制 |
| warn_threshold | DECIMAL | (5,2) | 否 | 0.80 | - | 预警阈值(0-1) |
| limit_currency | VARCHAR | 8 | 否 | 'CNY' | - | 限额币种 |
| effective_date | DATE | - | 否 | - | - | 生效日期 |
| expiry_date | DATE | - | 是 | NULL | - | 失效日期 |
| reset_cycle | VARCHAR | 16 | 否 | 'daily' | - | 重置周期:daily/weekly/monthly |
| is_active | TINYINT | 1 | 否 | 1 | - | 是否启用 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | ON UPDATE | 更新时间 |

**索引:**
- `idx_limit_type_scope`: limit_type, limit_scope
- `idx_is_active`: is_active
- `idx_effective_date`: effective_date

---

### 2.3 订单核心表

#### 2.3.1 母订单表 (parent_orders)

| 字段名 | 类型 | 长度 | 是否为空 | 默认值 | 约束 | 说明 |
|--------|------|------|----------|--------|------|------|
| id | BIGINT | - | 否 | 自增 | PRIMARY KEY | 主键ID |
| order_id | VARCHAR | 32 | 否 | - | UNIQUE | 母订单号 |
| user_id | VARCHAR | 64 | 否 | - | - | 用户ID |
| account_id | VARCHAR | 64 | 否 | - | - | 资金账户ID |
| strategy_id | VARCHAR | 64 | 是 | NULL | - | 策略ID |
| algorithm | VARCHAR | 32 | 否 | 'TWAP' | - | 算法类型:TWAP/VWAP/POV/IS |
| symbol | VARCHAR | 16 | 否 | - | - | 证券代码 |
| symbol_name | VARCHAR | 64 | 是 | NULL | - | 证券名称 |
| side | VARCHAR | 8 | 否 | - | - | 买卖方向:buy/sell |
| order_type | VARCHAR | 16 | 否 | 'limit' | - | 订单类型:market/limit/iceberg |
| total_qty | DECIMAL | (18,4) | 否 | - | - | 总数量 |
| filled_qty | DECIMAL | (18,4) | 否 | 0 | - | 已成交数量 |
| remaining_qty | DECIMAL | (18,4) | 否 | - | - | 剩余数量 |
| avg_price | DECIMAL | (18,4) | 是 | NULL | - | 成交均价 |
| limit_price | DECIMAL | (18,4) | 是 | NULL | - | 限价 |
| order_status | VARCHAR | 16 | 否 | 'pending' | - | 订单状态 |
| execution_status | VARCHAR | 16 | 否 | 'waiting' | - | 执行状态 |
| start_time | DATETIME | - | 是 | NULL | - | 计划开始时间 |
| end_time | DATETIME | - | 是 | NULL | - | 计划结束时间 |
| actual_start | DATETIME | - | 是 | NULL | - | 实际开始时间 |
| actual_end | DATETIME | - | 是 | NULL | - | 实际结束时间 |
| twap_config_id | BIGINT | - | 是 | NULL | FK | TWAP配置ID |
| total_amount | DECIMAL | (18,4) | 是 | NULL | - | 总金额 |
| filled_amount | DECIMAL | (18,4) | 否 | 0 | - | 已成交金额 |
| currency | VARCHAR | 8 | 否 | 'CNY' | - | 币种 |
| exchange | VARCHAR | 16 | 是 | NULL | - | 交易所代码 |
| market | VARCHAR | 8 | 否 | 'A' | - | 市场:A股/港股/美股 |
| memo | VARCHAR | 256 | 是 | NULL | - | 备注 |
| source | VARCHAR | 32 | 否 | 'manual' | - | 来源:manual/api/system |
| ip_address | VARCHAR | 64 | 是 | NULL | - | 下单IP |
| device_info | VARCHAR | 256 | 是 | NULL | - | 设备信息 |
| is_urgent | TINYINT | 1 | 否 | 0 | - | 是否紧急 |
| version | INT | - | 否 | 1 | - | 版本号(乐观锁) |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | ON UPDATE | 更新时间 |

**索引:**
- `idx_order_id`: order_id
- `idx_user_id`: user_id
- `idx_account_id`: account_id
- `idx_strategy_id`: strategy_id
- `idx_symbol`: symbol
- `idx_order_status`: order_status
- `idx_execution_status`: execution_status
- `idx_created_at`: created_at
- `idx_user_symbol`: user_id, symbol
- `idx_time_range`: created_at, order_status

---

#### 2.3.2 子订单表 (child_orders)

| 字段名 | 类型 | 长度 | 是否为空 | 默认值 | 约束 | 说明 |
|--------|------|------|----------|--------|------|------|
| id | BIGINT | - | 否 | 自增 | PRIMARY KEY | 主键ID |
| child_order_id | VARCHAR | 32 | 否 | - | UNIQUE | 子订单号 |
| parent_order_id | VARCHAR | 32 | 否 | - | FK | 母订单号 |
| slice_no | INT | - | 否 | - | - | 切片序号 |
| user_id | VARCHAR | 64 | 否 | - | - | 用户ID |
| account_id | VARCHAR | 64 | 否 | - | - | 资金账户ID |
| symbol | VARCHAR | 16 | 否 | - | - | 证券代码 |
| side | VARCHAR | 8 | 否 | - | - | 买卖方向 |
| order_qty | DECIMAL | (18,4) | 否 | - | - | 订单数量 |
| filled_qty | DECIMAL | (18,4) | 否 | 0 | - | 已成交数量 |
| order_price | DECIMAL | (18,4) | 是 | NULL | - | 委托价格 |
| avg_fill_price | DECIMAL | (18,4) | 是 | NULL | - | 平均成交价格 |
| order_status | VARCHAR | 16 | 否 | 'pending' | - | 订单状态 |
| external_order_id | VARCHAR | 64 | 是 | NULL | - | 外部订单号(交易所) |
| planned_time | DATETIME | - | 否 | - | - | 计划执行时间 |
| submit_time | DATETIME | - | 是 | NULL | - | 实际提交时间 |
| done_time | DATETIME | - | 是 | NULL | - | 完成时间 |
| cancel_time | DATETIME | - | 是 | NULL | - | 撤单时间 |
| fill_rate | DECIMAL | (5,2) | 是 | NULL | - | 成交率 |
| slippage | DECIMAL | (18,4) | 是 | NULL | - | 滑点 |
| is_last_slice | TINYINT | 1 | 否 | 0 | - | 是否最后一笔 |
| error_code | VARCHAR | 32 | 是 | NULL | - | 错误码 |
| error_msg | VARCHAR | 512 | 是 | NULL | - | 错误信息 |
| retry_count | INT | - | 否 | 0 | - | 重试次数 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | ON UPDATE | 更新时间 |

**索引:**
- `idx_child_order_id`: child_order_id
- `idx_parent_order_id`: parent_order_id
- `idx_user_id`: user_id
- `idx_symbol`: symbol
- `idx_order_status`: order_status
- `idx_external_order_id`: external_order_id
- `idx_planned_time`: planned_time
- `idx_parent_slice`: parent_order_id, slice_no

---

#### 2.3.3 成交明细表 (executions)

| 字段名 | 类型 | 长度 | 是否为空 | 默认值 | 约束 | 说明 |
|--------|------|------|----------|--------|------|------|
| id | BIGINT | - | 否 | 自增 | PRIMARY KEY | 主键ID |
| execution_id | VARCHAR | 32 | 否 | - | UNIQUE | 成交编号 |
| child_order_id | VARCHAR | 32 | 否 | - | FK | 子订单号 |
| parent_order_id | VARCHAR | 32 | 否 | - | FK | 母订单号 |
| user_id | VARCHAR | 64 | 否 | - | - | 用户ID |
| account_id | VARCHAR | 64 | 否 | - | - | 资金账户ID |
| symbol | VARCHAR | 16 | 否 | - | - | 证券代码 |
| side | VARCHAR | 8 | 否 | - | - | 买卖方向 |
| fill_qty | DECIMAL | (18,4) | 否 | - | - | 成交数量 |
| fill_price | DECIMAL | (18,4) | 否 | - | - | 成交价格 |
| fill_amount | DECIMAL | (18,4) | 否 | - | - | 成交金额 |
| fill_time | DATETIME | - | 否 | - | - | 成交时间 |
| external_exec_id | VARCHAR | 64 | 是 | NULL | - | 外部成交编号 |
| counterparty | VARCHAR | 64 | 是 | NULL | - | 对手方 |
| liquidity | VARCHAR | 16 | 是 | NULL | - | 流动性:add/remove |
| commission | DECIMAL | (18,4) | 是 | 0 | - | 佣金 |
| stamp_tax | DECIMAL | (18,4) | 是 | 0 | - | 印花税 |
| transfer_fee | DECIMAL | (18,4) | 是 | 0 | - | 过户费 |
| other_fees | DECIMAL | (18,4) | 是 | 0 | - | 其他费用 |
| total_fees | DECIMAL | (18,4) | 是 | 0 | - | 总费用 |
| net_amount | DECIMAL | (18,4) | 是 | NULL | - | 净额 |
| trade_date | DATE | - | 否 | - | - | 交易日期 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 创建时间 |

**索引:**
- `idx_execution_id`: execution_id
- `idx_child_order_id`: child_order_id
- `idx_parent_order_id`: parent_order_id
- `idx_user_id`: user_id
- `idx_symbol`: symbol
- `idx_fill_time`: fill_time
- `idx_trade_date`: trade_date
- `idx_user_symbol_date`: user_id, symbol, trade_date

---

#### 2.3.4 订单状态快照表 (order_snapshots)

| 字段名 | 类型 | 长度 | 是否为空 | 默认值 | 约束 | 说明 |
|--------|------|------|----------|--------|------|------|
| id | BIGINT | - | 否 | 自增 | PRIMARY KEY | 主键ID |
| parent_order_id | VARCHAR | 32 | 否 | - | FK | 母订单号 |
| snapshot_type | VARCHAR | 16 | 否 | - | - | 快照类型:status/progress/exception |
| from_status | VARCHAR | 16 | 是 | NULL | - | 原状态 |
| to_status | VARCHAR | 16 | 否 | - | - | 新状态 |
| filled_qty_before | DECIMAL | (18,4) | 否 | 0 | - | 变更前已成交数量 |
| filled_qty_after | DECIMAL | (18,4) | 否 | - | - | 变更后已成交数量 |
| progress_pct | DECIMAL | (5,2) | 否 | 0 | - | 进度百分比 |
| snapshot_data | JSON | - | 是 | NULL | - | 快照数据(JSON) |
| trigger_event | VARCHAR | 64 | 是 | NULL | - | 触发事件 |
| operator_id | VARCHAR | 64 | 是 | NULL | - | 操作人ID |
| operator_type | VARCHAR | 16 | 否 | 'system' | - | 操作人类型:system/user/api |
| snapshot_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 快照时间 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 创建时间 |

**索引:**
- `idx_parent_order_id`: parent_order_id
- `idx_snapshot_type`: snapshot_type
- `idx_from_status`: from_status
- `idx_to_status`: to_status
- `idx_snapshot_time`: snapshot_time

---

### 2.4 分析报告表

#### 2.4.1 滑点分析表 (slippage_analysis)

| 字段名 | 类型 | 长度 | 是否为空 | 默认值 | 约束 | 说明 |
|--------|------|------|----------|--------|------|------|
| id | BIGINT | - | 否 | 自增 | PRIMARY KEY | 主键ID |
| analysis_id | VARCHAR | 32 | 否 | - | UNIQUE | 分析ID |
| parent_order_id | VARCHAR | 32 | 否 | - | FK | 母订单号 |
| user_id | VARCHAR | 64 | 否 | - | - | 用户ID |
| symbol | VARCHAR | 16 | 否 | - | - | 证券代码 |
| side | VARCHAR | 8 | 否 | - | - | 买卖方向 |
| arrival_price | DECIMAL | (18,4) | 是 | NULL | - | 到达价格 |
| vwap_price | DECIMAL | (18,4) | 是 | NULL | - | VWAP价格 |
| avg_fill_price | DECIMAL | (18,4) | 否 | - | - | 实际成交均价 |
| slippage_bps | DECIMAL | (8,4) | 是 | NULL | - | 滑点(基点) |
| market_impact_bps | DECIMAL | (8,4) | 是 | NULL | - | 市场冲击(基点) |
| timing_cost_bps | DECIMAL | (8,4) | 是 | NULL | - | 时机成本(基点) |
| total_cost_bps | DECIMAL | (8,4) | 是 | NULL | - | 总成本(基点) |
| implementation_shortfall | DECIMAL | (18,4) | 是 | NULL | - | 执行差额 |
| benchmark_type | VARCHAR | 32 | 否 | 'vwap' | - | 基准类型:vwap/twap/arrival/close |
| benchmark_price | DECIMAL | (18,4) | 是 | NULL | - | 基准价格 |
| analysis_date | DATE | - | 否 | - | - | 分析日期 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 创建时间 |

**索引:**
- `idx_analysis_id`: analysis_id
- `idx_parent_order_id`: parent_order_id
- `idx_user_id`: user_id
- `idx_symbol`: symbol
- `idx_analysis_date`: analysis_date

---

#### 2.4.2 成交量分布表 (volume_distribution)

| 字段名 | 类型 | 长度 | 是否为空 | 默认值 | 约束 | 说明 |
|--------|------|------|----------|--------|------|------|
| id | BIGINT | - | 否 | 自增 | PRIMARY KEY | 主键ID |
| parent_order_id | VARCHAR | 32 | 否 | - | FK | 母订单号 |
| user_id | VARCHAR | 64 | 否 | - | - | 用户ID |
| symbol | VARCHAR | 16 | 否 | - | - | 证券代码 |
| time_bucket | VARCHAR | 16 | 否 | - | - | 时间桶:1min/5min/15min/30min/1hour |
| bucket_start | DATETIME | - | 否 | - | - | 时间段开始 |
| bucket_end | DATETIME | - | 否 | - | - | 时间段结束 |
| order_qty | DECIMAL | (18,4) | 否 | 0 | - | 委托数量 |
| filled_qty | DECIMAL | (18,4) | 否 | 0 | - | 成交数量 |
| market_volume | DECIMAL | (18,4) | 是 | NULL | - | 市场总成交量 |
| participation_rate | DECIMAL | (5,2) | 是 | NULL | - | 参与率 |
| avg_price | DECIMAL | (18,4) | 是 | NULL | - | 成交均价 |
| vwap | DECIMAL | (18,4) | 是 | NULL | - | 该时段VWAP |
| high_price | DECIMAL | (18,4) | 是 | NULL | - | 最高价 |
| low_price | DECIMAL | (18,4) | 是 | NULL | - | 最低价 |
| volume_pct | DECIMAL | (5,2) | 是 | NULL | - | 占母单比例 |
| trade_date | DATE | - | 否 | - | - | 交易日期 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 创建时间 |

**索引:**
- `idx_parent_order_id`: parent_order_id
- `idx_user_id`: user_id
- `idx_symbol`: symbol
- `idx_bucket_start`: bucket_start
- `idx_trade_date`: trade_date
- `idx_symbol_time`: symbol, bucket_start

---

#### 2.4.3 执行效率评估表 (execution_efficiency)

| 字段名 | 类型 | 长度 | 是否为空 | 默认值 | 约束 | 说明 |
|--------|------|------|----------|--------|------|------|
| id | BIGINT | - | 否 | 自增 | PRIMARY KEY | 主键ID |
| efficiency_id | VARCHAR | 32 | 否 | - | UNIQUE | 评估ID |
| parent_order_id | VARCHAR | 32 | 否 | - | FK | 母订单号 |
| user_id | VARCHAR | 64 | 否 | - | - | 用户ID |
| symbol | VARCHAR | 16 | 否 | - | - | 证券代码 |
| algorithm | VARCHAR | 32 | 否 | - | - | 算法类型 |
| duration_seconds | INT | - | 是 | NULL | - | 执行耗时(秒) |
| fill_rate | DECIMAL | (5,2) | 否 | 0 | - | 成交率 |
| avg_slippage_bps | DECIMAL | (8,4) | 是 | NULL | - | 平均滑点(基点) |
| market_impact_bps | DECIMAL | (8,4) | 是 | NULL | - | 市场冲击(基点) |
| completion_score | DECIMAL | (5,2) | 是 | NULL | - | 完成度评分(0-100) |
| timing_score | DECIMAL | (5,2) | 是 | NULL | - | 时机评分(0-100) |
| price_score | DECIMAL | (5,2) | 是 | NULL | - | 价格评分(0-100) |
| overall_score | DECIMAL | (5,2) | 是 | NULL | - | 综合评分(0-100) |
| expected_cost_bps | DECIMAL | (8,4) | 是 | NULL | - | 预期成本(基点) |
| actual_cost_bps | DECIMAL | (8,4) | 是 | NULL | - | 实际成本(基点) |
| cost_efficiency | DECIMAL | (5,2) | 是 | NULL | - | 成本效率(百分比) |
| cancel_rate | DECIMAL | (5,2) | 是 | NULL | - | 撤单率 |
| amend_rate | DECIMAL | (5,2) | 是 | NULL | - | 改单率 |
| urgency_level | VARCHAR | 16 | 否 | 'normal' | - | 紧急程度 |
| market_condition | VARCHAR | 32 | 是 | NULL | - | 市场环境:volatile/normal/quiet |
| assessment_date | DATE | - | 否 | - | - | 评估日期 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 创建时间 |

**索引:**
- `idx_efficiency_id`: efficiency_id
- `idx_parent_order_id`: parent_order_id
- `idx_user_id`: user_id
- `idx_symbol`: symbol
- `idx_assessment_date`: assessment_date
- `idx_overall_score`: overall_score

---

### 2.5 异常处理表

#### 2.5.1 异常检测规则表 (abnormal_rules)

| 字段名 | 类型 | 长度 | 是否为空 | 默认值 | 约束 | 说明 |
|--------|------|------|----------|--------|------|------|
| id | BIGINT | - | 否 | 自增 | PRIMARY KEY | 主键ID |
| rule_code | VARCHAR | 32 | 否 | - | UNIQUE | 规则编码 |
| rule_name | VARCHAR | 128 | 否 | - | - | 规则名称 |
| rule_category | VARCHAR | 32 | 否 | - | - | 规则类别:large_order/frequent_cancel/price_deviation/volume_spike |
| abnormal_type | VARCHAR | 32 | 否 | - | - | 异常类型 |
| detection_scope | VARCHAR | 16 | 否 | 'order' | - | 检测范围:order/user/account/system |
| trigger_condition | JSON | - | 否 | - | - | 触发条件(JSON) |
| alert_level | VARCHAR | 16 | 否 | 'medium' | - | 告警级别:low/medium/high/critical |
| auto_process | TINYINT | 1 | 否 | 0 | - | 是否自动处理 |
| process_action | VARCHAR | 32 | 是 | NULL | - | 自动处理动作 |
| notify_targets | JSON | - | 是 | NULL | - | 通知对象配置 |
| cooldown_seconds | INT | - | 否 | 300 | - | 冷却时间(秒) |
| is_active | TINYINT | 1 | 否 | 1 | - | 是否启用 |
| priority | INT | - | 否 | 100 | - | 优先级 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | ON UPDATE | 更新时间 |

**索引:**
- `idx_rule_code`: rule_code
- `idx_rule_category`: rule_category
- `idx_alert_level`: alert_level
- `idx_is_active`: is_active

---

#### 2.5.2 异常记录表 (abnormal_logs)

| 字段名 | 类型 | 长度 | 是否为空 | 默认值 | 约束 | 说明 |
|--------|------|------|----------|--------|------|------|
| id | BIGINT | - | 否 | 自增 | PRIMARY KEY | 主键ID |
| log_id | VARCHAR | 32 | 否 | - | UNIQUE | 异常日志ID |
| rule_id | BIGINT | - | 否 | - | FK | 规则ID |
| rule_code | VARCHAR | 32 | 否 | - | - | 规则编码 |
| abnormal_type | VARCHAR | 32 | 否 | - | - | 异常类型 |
| alert_level | VARCHAR | 16 | 否 | - | - | 告警级别 |
| related_order_id | VARCHAR | 32 | 是 | NULL | - | 关联订单号 |
| related_user_id | VARCHAR | 64 | 是 | NULL | - | 关联用户ID |
| related_account_id | VARCHAR | 64 | 是 | NULL | - | 关联账户ID |
| symbol | VARCHAR | 16 | 是 | NULL | - | 证券代码 |
| detection_data | JSON | - | 否 | - | - | 检测数据(触发时的上下文) |
| trigger_value | DECIMAL | (18,4) | 是 | NULL | - | 触发值 |
| threshold_value | DECIMAL | (18,4) | 是 | NULL | - | 阈值 |
| description | VARCHAR | 512 | 是 | NULL | - | 异常描述 |
| status | VARCHAR | 16 | 否 | 'pending' | - | 处理状态:pending/processing/resolved/ignored |
| handler_id | VARCHAR | 64 | 是 | NULL | - | 处理人ID |
| handler_name | VARCHAR | 64 | 是 | NULL | - | 处理人姓名 |
| resolution | VARCHAR | 512 | 是 | NULL | - | 解决方案 |
| resolved_at | DATETIME | - | 是 | NULL | - | 解决时间 |
| detection_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 检测时间 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | ON UPDATE | 更新时间 |

**索引:**
- `idx_log_id`: log_id
- `idx_rule_id`: rule_id
- `idx_related_order_id`: related_order_id
- `idx_related_user_id`: related_user_id
- `idx_abnormal_type`: abnormal_type
- `idx_alert_level`: alert_level
- `idx_status`: status
- `idx_detection_time`: detection_time
- `idx_symbol`: symbol

---

#### 2.5.3 告警通知表 (alerts)

| 字段名 | 类型 | 长度 | 是否为空 | 默认值 | 约束 | 说明 |
|--------|------|------|----------|--------|------|------|
| id | BIGINT | - | 否 | 自增 | PRIMARY KEY | 主键ID |
| alert_id | VARCHAR | 32 | 否 | - | UNIQUE | 告警ID |
| abnormal_log_id | VARCHAR | 32 | 否 | - | FK | 异常日志ID |
| alert_level | VARCHAR | 16 | 否 | - | - | 告警级别 |
| alert_channel | VARCHAR | 32 | 否 | - | - | 通知渠道:email/sms/app/webhook |
| alert_title | VARCHAR | 256 | 否 | - | - | 告警标题 |
| alert_content | TEXT | - | 是 | NULL | - | 告警内容 |
| recipient_type | VARCHAR | 16 | 否 | 'user' | - | 接收者类型:user/role/group |
| recipient_id | VARCHAR | 64 | 否 | - | - | 接收者ID |
| recipient_contact | VARCHAR | 128 | 是 | NULL | - | 接收者联系方式 |
| send_status | VARCHAR | 16 | 否 | 'pending' | - | 发送状态:pending/sent/failed/acknowledged |
| sent_at | DATETIME | - | 是 | NULL | - | 发送时间 |
| acknowledged_at | DATETIME | - | 是 | NULL | - | 确认时间 |
| acknowledged_by | VARCHAR | 64 | 是 | NULL | - | 确认人 |
| retry_count | INT | - | 否 | 0 | - | 重试次数 |
| error_msg | VARCHAR | 512 | 是 | NULL | - | 错误信息 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | ON UPDATE | 更新时间 |

**索引:**
- `idx_alert_id`: alert_id
- `idx_abnormal_log_id`: abnormal_log_id
- `idx_alert_level`: alert_level
- `idx_send_status`: send_status
- `idx_recipient_id`: recipient_id
- `idx_sent_at`: sent_at

---

#### 2.5.4 处理记录表 (process_logs)

| 字段名 | 类型 | 长度 | 是否为空 | 默认值 | 约束 | 说明 |
|--------|------|------|----------|--------|------|------|
| id | BIGINT | - | 否 | 自增 | PRIMARY KEY | 主键ID |
| process_id | VARCHAR | 32 | 否 | - | UNIQUE | 处理记录ID |
| abnormal_log_id | VARCHAR | 32 | 否 | - | FK | 异常日志ID |
| process_type | VARCHAR | 32 | 否 | - | - | 处理类型:manual/auto/system |
| process_action | VARCHAR | 64 | 否 | - | - | 处理动作 |
| process_desc | VARCHAR | 512 | 是 | NULL | - | 处理说明 |
| before_status | VARCHAR | 16 | 是 | NULL | - | 处理前状态 |
| after_status | VARCHAR | 16 | 否 | - | - | 处理后状态 |
| process_result | VARCHAR | 32 | 否 | 'success' | - | 处理结果:success/failed/partial |
| operator_id | VARCHAR | 64 | 是 | NULL | - | 操作人ID |
| operator_name | VARCHAR | 64 | 是 | NULL | - | 操作人姓名 |
| related_order_ids | JSON | - | 是 | NULL | - | 关联订单ID列表 |
| process_data | JSON | - | 是 | NULL | - | 处理数据(上下文) |
| attachment_urls | JSON | - | 是 | NULL | - | 附件链接 |
| process_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 处理时间 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | - | 创建时间 |

**索引:**
- `idx_process_id`: process_id
- `idx_abnormal_log_id`: abnormal_log_id
- `idx_process_type`: process_type
- `idx_process_action`: process_action
- `idx_operator_id`: operator_id
- `idx_process_time`: process_time

---

## 3. 订单状态流转图

### 3.1 母订单状态流转

```
                              ┌─────────────────────────────────────────┐
                              │           母订单状态流转图               │
                              └─────────────────────────────────────────┘

┌─────────────┐
│   PENDING   │ ───────────────────────────────────────────────────────
│   待处理     │         │                    │
└──────┬──────┘         │                    │
       │                │                    │
       ▼                │                    │
┌─────────────┐         │                    │
│   QUEUED    │         │                    │
│   排队中     │◄────────┘                    │
└──────┬──────┘                              │
       │                                     │
       ▼                                     │
┌─────────────┐         ┌─────────────┐     │
│  RUNNING    │────────►│   PAUSED    │─────┘
│   执行中     │         │   已暂停     │
└──────┬──────┘         └─────────────┘
       │
       │         ┌─────────────┐
       └────────►│  PARTIAL    │
                 │  部分成交    │◄────────────────┐
                 └──────┬──────┘                 │
                        │                        │
       ┌────────────────┼────────────────┐       │
       │                │                │       │
       ▼                ▼                ▼       │
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│   FILLED    │   │  CANCELLED  │   │   FAILED    │
│   全部成交   │   │   已撤单     │   │   执行失败   │
└─────────────┘   └─────────────┘   └─────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │  EXPIRED    │
                   │   已过期     │
                   └─────────────┘
```

### 3.2 子订单状态流转

```
                         ┌─────────────────────────────────────────┐
                         │           子订单状态流转图               │
                         └─────────────────────────────────────────┘

┌─────────────┐
│   PENDING   │ ───────────────────────────────────────────────────
│   待提交     │
└──────┬──────┘
       │
       ▼
┌─────────────┐         ┌─────────────┐
│  SUBMITTED  │◄───────►│  REJECTED   │
│   已提交     │         │   已拒绝     │
└──────┬──────┘         └─────────────┘
       │
       ▼
┌─────────────┐
│   QUEUED    │
│   已报      │
└──────┬──────┘
       │
       ├─────────────────────┬─────────────────────┐
       │                     │                     │
       ▼                     ▼                     ▼
┌─────────────┐        ┌─────────────┐       ┌─────────────┐
│  PARTIAL    │        │   FILLED    │       │  CANCELLED  │
│   部分成交   │───────►│   全部成交   │       │   已撤单     │
└─────────────┘        └─────────────┘       └─────────────┘
       │                     │
       │                     │
       └─────────────────────┘
```

### 3.3 状态流转规则表

| 当前状态 | 允许转换状态 | 触发条件 | 操作人/系统 | 说明 |
|----------|--------------|----------|-------------|------|
| PENDING | QUEUED, CANCELLED, FAILED | 通过风控检查/用户取消/风控拦截 | 系统/用户 | 待处理状态 |
| QUEUED | RUNNING, CANCELLED | 到达计划时间/用户取消 | 系统/用户 | 排队等待执行 |
| RUNNING | PAUSED, PARTIAL, FILLED, CANCELLED, FAILED | 用户暂停/部分成交/全部成交/用户撤单/执行异常 | 系统/用户 | 正在执行中 |
| PAUSED | RUNNING, CANCELLED | 用户恢复/用户取消 | 用户 | 暂停状态 |
| PARTIAL | FILLED, CANCELLED, FAILED | 继续成交完成/用户撤单/执行失败 | 系统/用户 | 部分成交 |
| FILLED | - | - | - | 终态：全部成交 |
| CANCELLED | - | - | - | 终态：已撤单 |
| FAILED | - | - | - | 终态：执行失败 |
| EXPIRED | - | - | - | 终态：已过期 |

### 3.4 状态流转详细说明

#### 3.4.1 正常执行流程
```
PENDING → QUEUED → RUNNING → PARTIAL → FILLED
                              ↓
                         (中间可能多次PARTIAL状态变更)
```

#### 3.4.2 用户撤单流程
```
PENDING/QUEUED/RUNNING/PAUSED/PARTIAL → CANCELLED
```

#### 3.4.3 异常处理流程
```
PENDING/QUEUED/RUNNING/PAUSED → FAILED → (人工干预/自动重试)
```

#### 3.4.4 超时处理流程
```
QUEUED/RUNNING → EXPIRED (超过截止时间未完成)
```

---

## 4. 异常检测规则定义

### 4.1 异常类型定义

| 异常类别 | 异常编码 | 异常名称 | 说明 |
|----------|----------|----------|------|
| 大单交易 | A001 | 大单买入 | 单笔买入金额超过阈值 |
| 大单交易 | A002 | 大单卖出 | 单笔卖出金额超过阈值 |
| 频繁撤单 | A003 | 频繁撤单 | 单位时间内撤单次数过多 |
| 价格偏离 | A004 | 价格向上偏离 | 委托价格大幅高于市场价格 |
| 价格偏离 | A005 | 价格向下偏离 | 委托价格大幅低于市场价格 |
| 成交量异常 | A006 | 成交量激增 | 成交量突增超过正常水平 |
| 执行异常 | A007 | 执行超时 | 订单执行超过预期时间 |
| 执行异常 | A008 | 成交率过低 | 订单成交率低于预期 |
| 账户异常 | A009 | 日内交易频繁 | 同一账户日内交易次数过多 |
| 风控异常 | A010 | 触碰风控线 | 订单触碰风控警戒线 |

### 4.2 异常检测规则配置

#### 4.2.1 大单交易检测规则

```json
{
  "rule_code": "A001",
  "rule_name": "大单买入检测",
  "rule_category": "large_order",
  "trigger_condition": {
    "type": "amount_threshold",
    "side": "buy",
    "thresholds": [
      {"level": "low", "value": 1000000, "currency": "CNY"},
      {"level": "medium", "value": 5000000, "currency": "CNY"},
      {"level": "high", "value": 10000000, "currency": "CNY"},
      {"level": "critical", "value": 50000000, "currency": "CNY"}
    ]
  },
  "detection_scope": "order",
  "alert_level_map": {
    "low": "low",
    "medium": "medium",
    "high": "high",
    "critical": "critical"
  },
  "auto_process": false,
  "notify_targets": {
    "low": ["trader"],
    "medium": ["trader", "manager"],
    "high": ["trader", "manager", "risk_officer"],
    "critical": ["trader", "manager", "risk_officer", "compliance"]
  },
  "cooldown_seconds": 60
}
```

#### 4.2.2 频繁撤单检测规则

```json
{
  "rule_code": "A003",
  "rule_name": "频繁撤单检测",
  "rule_category": "frequent_cancel",
  "trigger_condition": {
    "type": "frequency_threshold",
    "time_windows": [
      {"window": "1m", "thresholds": {"low": 3, "medium": 5, "high": 10}},
      {"window": "5m", "thresholds": {"low": 5, "medium": 10, "high": 20}},
      {"window": "1h", "thresholds": {"low": 10, "medium": 20, "high": 50}}
    ],
    "scope": "user",
    "cancel_types": ["manual", "system"]
  },
  "detection_scope": "user",
  "alert_level_map": {
    "low": "low",
    "medium": "medium",
    "high": "high"
  },
  "auto_process": true,
  "process_action": "limit_order",
  "process_config": {
    "limit_duration_minutes": 10,
    "limit_type": "temporary_ban"
  },
  "notify_targets": {
    "low": ["user"],
    "medium": ["user", "manager"],
    "high": ["user", "manager", "risk_officer"]
  },
  "cooldown_seconds": 300
}
```

#### 4.2.3 价格偏离检测规则

```json
{
  "rule_code": "A004",
  "rule_name": "价格向上偏离检测",
  "rule_category": "price_deviation",
  "trigger_condition": {
    "type": "price_deviation",
    "direction": "up",
    "reference_price": "last",
    "deviation_thresholds": [
      {"level": "low", "pct": 0.02},
      {"level": "medium", "pct": 0.05},
      {"level": "high", "pct": 0.10},
      {"level": "critical", "pct": 0.15}
    ],
    "min_order_amount": 100000
  },
  "detection_scope": "order",
  "alert_level_map": {
    "low": "low",
    "medium": "medium",
    "high": "high",
    "critical": "critical"
  },
  "auto_process": true,
  "process_action": "block_and_alert",
  "notify_targets": {
    "low": ["trader"],
    "medium": ["trader", "manager"],
    "high": ["trader", "manager", "risk_officer"],
    "critical": ["trader", "manager", "risk_officer", "compliance"]
  },
  "cooldown_seconds": 30
}
```

#### 4.2.4 执行超时检测规则

```json
{
  "rule_code": "A007",
  "rule_name": "订单执行超时检测",
  "rule_category": "execution_timeout",
  "trigger_condition": {
    "type": "time_threshold",
    "timeouts": [
      {"algorithm": "TWAP", "expected_duration_factor": 1.5},
      {"algorithm": "VWAP", "expected_duration_factor": 1.5},
      {"algorithm": "POV", "expected_duration_factor": 2.0},
      {"algorithm": "IS", "expected_duration_factor": 1.2}
    ],
    "min_progress_threshold": 0.1,
    "check_interval_seconds": 60
  },
  "detection_scope": "order",
  "alert_level_map": {
    "default": "medium"
  },
  "auto_process": false,
  "notify_targets": {
    "medium": ["trader", "system_admin"]
  },
  "cooldown_seconds": 600
}
```

#### 4.2.5 成交率过低检测规则

```json
{
  "rule_code": "A008",
  "rule_name": "订单成交率过低检测",
  "rule_category": "low_fill_rate",
  "trigger_condition": {
    "type": "fill_rate_threshold",
    "check_points": [
      {"progress": 0.25, "min_fill_rate": 0.20},
      {"progress": 0.50, "min_fill_rate": 0.45},
      {"progress": 0.75, "min_fill_rate": 0.70}
    ],
    "final_check": {
      "fill_rate": 0.80,
      "trigger_level": "high"
    }
  },
  "detection_scope": "order",
  "alert_level_map": {
    "checkpoint": "low",
    "final": "high"
  },
  "auto_process": false,
  "notify_targets": {
    "low": ["trader"],
    "high": ["trader", "manager"]
  },
  "cooldown_seconds": 300
}
```

### 4.3 告警级别与响应

| 告警级别 | 颜色标识 | 响应时间要求 | 通知方式 | 升级策略 |
|----------|----------|--------------|----------|----------|
| LOW | 🟢 绿色 | 30分钟内 | App推送/邮件 | 无需升级 |
| MEDIUM | 🟡 黄色 | 15分钟内 | App推送/邮件/短信 | 30分钟未处理升级至HIGH |
| HIGH | 🟠 橙色 | 5分钟内 | App推送/邮件/短信/电话 | 15分钟未处理升级至CRITICAL |
| CRITICAL | 🔴 红色 | 立即 | 全渠道+电话+IM | 立即通知管理层 |

### 4.4 异常处理流程

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         异常检测与处理流程                               │
└─────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │   数据收集与监控   │
                    │  (实时/批量检测)  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   规则匹配检测    │
                    │  (命中/未命中)   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        ┌─────────┐    ┌─────────┐    ┌─────────┐
        │  未命中  │    │  命中   │    │  冷却期  │
        │  忽略   │    │  生成异常 │    │  忽略   │
        └─────────┘    └────┬────┘    └─────────┘
                            │
                            ▼
                    ┌─────────────────┐
                    │   异常日志记录    │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        ┌─────────┐    ┌─────────┐    ┌─────────┐
        │ 人工处理 │    │ 自动处理 │    │ 告警通知 │
        │         │    │         │    │         │
        └────┬────┘    └────┬────┘    └────┬────┘
             │              │              │
             └──────────────┼──────────────┘
                            │
                            ▼
                    ┌─────────────────┐
                    │   处理结果记录    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    闭环与复盘    │
                    └─────────────────┘
```

### 4.5 异常状态定义

| 状态 | 说明 | 允许操作 |
|------|------|----------|
| PENDING | 待处理，刚检测到的异常 | 分配、标记、忽略 |
| PROCESSING | 处理中，已分配给处理人 | 更新进度、转交、升级 |
| RESOLVED | 已解决，异常已处理完毕 | 重新打开、归档 |
| IGNORED | 已忽略，经判断无需处理 | 重新打开 |
| ESCALATED | 已升级，超出处理能力 | 继续升级、指派专家 |

---

## 附录

### 附录A：数据类型说明

| 类型 | 说明 | 示例 |
|------|------|------|
| DECIMAL(18,4) | 高精度数值，用于金额和数量 | 123456789012.3456 |
| DECIMAL(5,2) | 百分比数值 | 99.99 |
| DECIMAL(8,4) | 基点数值 | 12.3456 |
| JSON | JSON格式数据 | {"key": "value"} |

### 附录B：枚举值定义

#### 订单状态枚举
```
PENDING     - 待处理
QUEUED      - 排队中
RUNNING     - 执行中
PAUSED      - 已暂停
PARTIAL     - 部分成交
FILLED      - 全部成交
CANCELLED   - 已撤单
FAILED      - 执行失败
EXPIRED     - 已过期
```

#### 买卖方向枚举
```
BUY  - 买入
SELL - 卖出
```

#### 告警级别枚举
```
LOW      - 低级
MEDIUM   - 中级
HIGH     - 高级
CRITICAL - 严重
```

### 附录C：表命名规范

- 系统配置表：`sys_xxx`
- 订单核心表：`parent_orders`, `child_orders`, `executions`
- 分析报表表：`xxx_analysis`, `xxx_distribution`, `xxx_efficiency`
- 异常处理表：`abnormal_xxx`, `alerts`, `process_xxx`

---

*文档版本: v1.0*  
*创建日期: 2026-03-07*  
*最后更新: 2026-03-07*

---

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

---

# 业绩看板模块数据建模方案

> 文档版本: v1.0
> 模块: 员工工作台 - 业绩看板
> 适用范围: 销售团队绩效管理

---

## 一、实体关系图（ER图文字描述）

### 1.1 核心实体概览

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   员工 (User)   │────<│  业绩记录       │>────│   部门 (Dept)   │
│   PK: user_id   │  1:N │  (Performance)  │ N:1 │   PK: dept_id   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                      │
         │ 1:1                  │ N:1
         ▼                      ▼
┌─────────────────┐     ┌─────────────────┐
│  业绩目标       │     │   客户 (Customer)│
│  (Target)       │     │   PK: cust_id   │
│  PK: target_id  │     └─────────────────┘
└─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐
│  满意度评价     │
│  (Satisfaction) │
│  PK: satis_id   │
└─────────────────┘
```

### 1.2 实体关系详细说明

| 主实体 | 关系 | 从实体 | 关系类型 | 业务说明 |
|--------|------|--------|----------|----------|
| 员工(User) | 拥有 | 业绩记录(Performance) | 1:N | 一个员工可有多条业绩记录（按时间维度） |
| 员工(User) | 属于 | 部门(Dept) | N:1 | 多个员工属于一个部门 |
| 员工(User) | 设定 | 业绩目标(Target) | 1:1 | 每个员工每期有一个业绩目标 |
| 业绩记录(Performance) | 关联 | 客户(Customer) | N:1 | 多条业绩可能来自同一客户 |
| 业绩目标(Target) | 包含 | 满意度评价(Satisfaction) | 1:N | 目标达成后的客户反馈 |

### 1.3 数据流向图

```
                    ┌─────────────────────────────────────┐
                    │           数据源层                   │
                    │  CRM系统 | 订单系统 | 财务系统       │
                    └───────────────┬─────────────────────┘
                                    │
                                    ▼
                    ┌─────────────────────────────────────┐
                    │           数据清洗层                 │
                    │  ETL处理 | 数据校验 | 异常过滤       │
                    └───────────────┬─────────────────────┘
                                    │
                                    ▼
        ┌───────────────────────────────────────────────────────────┐
        │                    数据存储层 (本模型)                      │
        │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │
        │  │ 员工表  │  │ 业绩表  │  │ 目标表  │  │ 客户表  │      │
        │  └─────────┘  └─────────┘  └─────────┘  └─────────┘      │
        └───────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
        ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
        │   业绩详情    │ │   排行榜      │ │   趋势分析    │
        │  (实时计算)   │ │  (定时聚合)   │ │  (时间序列)   │
        └───────────────┘ └───────────────┘ └───────────────┘
```

---

## 二、数据表结构设计

### 2.1 员工表 (sys_user)

存储员工基础信息，作为业绩数据的核心关联主体。

| 字段名 | 类型 | 长度 | 是否为空 | 默认值 | 说明 |
|--------|------|------|----------|--------|------|
| user_id | VARCHAR | 32 | 否 | - | 主键，员工唯一标识 |
| user_code | VARCHAR | 50 | 否 | - | 员工工号，唯一索引 |
| user_name | VARCHAR | 100 | 否 | - | 员工姓名 |
| dept_id | VARCHAR | 32 | 否 | - | 外键，所属部门ID |
| position | VARCHAR | 50 | 是 | NULL | 职位/岗位 |
| entry_date | DATE | - | 否 | - | 入职日期 |
| status | TINYINT | 1 | 否 | 1 | 状态：0-禁用，1-在职，2-离职 |
| manager_id | VARCHAR | 32 | 是 | NULL | 直属上级ID，自关联 |
| create_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

**索引设计：**
- 主键：user_id
- 唯一索引：user_code
- 普通索引：dept_id, manager_id
- 组合索引：(dept_id, status)

---

### 2.2 部门表 (sys_dept)

组织架构信息，支持多级部门结构。

| 字段名 | 类型 | 长度 | 是否为空 | 默认值 | 说明 |
|--------|------|------|----------|--------|------|
| dept_id | VARCHAR | 32 | 否 | - | 主键，部门唯一标识 |
| dept_name | VARCHAR | 100 | 否 | - | 部门名称 |
| parent_id | VARCHAR | 32 | 是 | '0' | 父部门ID，'0'为顶级部门 |
| dept_level | TINYINT | 1 | 否 | 1 | 部门层级：1-一级，2-二级... |
| dept_path | VARCHAR | 500 | 否 | - | 部门路径，如：/1/2/5/ |
| sort_order | INT | - | 否 | 0 | 排序序号 |
| status | TINYINT | 1 | 否 | 1 | 状态：0-禁用，1-启用 |
| create_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |

**索引设计：**
- 主键：dept_id
- 普通索引：parent_id, dept_path

---

### 2.3 业绩目标表 (perf_target)

定义员工各周期的业绩目标，支持多维度目标设定。

| 字段名 | 类型 | 长度 | 是否为空 | 默认值 | 说明 |
|--------|------|------|----------|--------|------|
| target_id | VARCHAR | 32 | 否 | - | 主键，目标唯一标识 |
| user_id | VARCHAR | 32 | 否 | - | 外键，员工ID |
| target_period | VARCHAR | 10 | 否 | - | 目标周期：YYYY-MM |
| target_type | TINYINT | 1 | 否 | 1 | 目标类型：1-月度，2-季度，3-年度 |
| revenue_target | DECIMAL | 18,2 | 否 | 0.00 | 收入目标（万元） |
| customer_target | INT | - | 否 | 0 | 新增客户目标数 |
| deal_target | DECIMAL | 18,2 | 否 | 0.00 | 成交额目标（万元） |
| satisfaction_target | DECIMAL | 5,2 | 否 | 95.00 | 满意度目标（%） |
| status | TINYINT | 1 | 否 | 1 | 状态：0-草稿，1-已确认，2-已归档 |
| create_by | VARCHAR | 32 | 否 | - | 创建人ID |
| create_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

**索引设计：**
- 主键：target_id
- 唯一索引：(user_id, target_period, target_type) - 防止重复目标
- 普通索引：target_period, user_id
- 组合索引：(user_id, status)

---

### 2.4 业绩记录表 (perf_record)

存储员工每日/每笔业绩明细数据，作为指标计算的基础。

| 字段名 | 类型 | 长度 | 是否为空 | 默认值 | 说明 |
|--------|------|------|----------|--------|------|
| record_id | VARCHAR | 32 | 否 | - | 主键，记录唯一标识 |
| user_id | VARCHAR | 32 | 否 | - | 外键，员工ID |
| record_date | DATE | - | 否 | - | 业绩日期 |
| revenue_amount | DECIMAL | 18,2 | 否 | 0.00 | 当日收入金额（元） |
| new_customers | INT | - | 否 | 0 | 当日新增客户数 |
| deal_amount | DECIMAL | 18,2 | 否 | 0.00 | 当日成交额（元） |
| deal_count | INT | - | 否 | 0 | 当日成交笔数 |
| satisfaction_score | DECIMAL | 3,2 | 是 | NULL | 当日平均满意度评分 |
| satisfaction_count | INT | - | 否 | 0 | 当日评价数 |
| source_type | TINYINT | 1 | 否 | 1 | 数据来源：1-手动录入，2-系统自动 |
| remark | VARCHAR | 500 | 是 | NULL | 备注说明 |
| create_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

**索引设计：**
- 主键：record_id
- 唯一索引：(user_id, record_date) - 每人每天一条记录
- 普通索引：record_date, user_id
- 组合索引：(user_id, record_date, source_type)
- 分区建议：按record_date按月分区

---

### 2.5 客户表 (crm_customer)

客户基础信息，用于统计新增客户数量。

| 字段名 | 类型 | 长度 | 是否为空 | 默认值 | 说明 |
|--------|------|------|----------|--------|------|
| cust_id | VARCHAR | 32 | 否 | - | 主键，客户唯一标识 |
| cust_name | VARCHAR | 200 | 否 | - | 客户名称 |
| cust_type | TINYINT | 1 | 否 | 1 | 客户类型：1-企业，2-个人 |
| industry | VARCHAR | 50 | 是 | NULL | 所属行业 |
| owner_id | VARCHAR | 32 | 否 | - | 外键，归属员工ID |
| belong_dept_id | VARCHAR | 32 | 否 | - | 归属部门ID |
| first_contact_date | DATE | - | 是 | NULL | 首次接触日期 |
| contract_date | DATE | - | 是 | NULL | 签约日期 |
| cust_status | TINYINT | 1 | 否 | 1 | 客户状态：1-潜在，2-跟进中，3-已签约，4-流失 |
| source_channel | VARCHAR | 50 | 是 | NULL | 客户来源渠道 |
| create_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

**索引设计：**
- 主键：cust_id
- 普通索引：owner_id, belong_dept_id, cust_status
- 组合索引：(owner_id, contract_date)
- 组合索引：(cust_status, create_time)

---

### 2.6 满意度评价表 (sat_evaluation)

存储客户满意度评价明细。

| 字段名 | 类型 | 长度 | 是否为空 | 默认值 | 说明 |
|--------|------|------|----------|--------|------|
| eval_id | VARCHAR | 32 | 否 | - | 主键，评价唯一标识 |
| cust_id | VARCHAR | 32 | 否 | - | 外键，客户ID |
| user_id | VARCHAR | 32 | 否 | - | 外键，被评价员工ID |
| order_id | VARCHAR | 32 | 是 | NULL | 关联订单ID |
| eval_score | DECIMAL | 3,2 | 否 | 5.00 | 评分：1.00-5.00 |
| eval_content | TEXT | - | 是 | NULL | 评价内容 |
| eval_tags | VARCHAR | 200 | 是 | NULL | 评价标签，JSON数组 |
| eval_type | TINYINT | 1 | 否 | 1 | 评价类型：1-服务评价，2-产品评价 |
| eval_time | DATETIME | - | 否 | - | 评价时间 |
| create_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |

**索引设计：**
- 主键：eval_id
- 普通索引：user_id, cust_id, eval_time
- 组合索引：(user_id, eval_time)

---

### 2.7 业绩汇总表 (perf_summary)

预聚合的月度业绩数据，用于提升查询性能。

| 字段名 | 类型 | 长度 | 是否为空 | 默认值 | 说明 |
|--------|------|------|----------|--------|------|
| summary_id | VARCHAR | 32 | 否 | - | 主键 |
| user_id | VARCHAR | 32 | 否 | - | 员工ID |
| summary_month | VARCHAR | 7 | 否 | - | 汇总月份：YYYY-MM |
| total_revenue | DECIMAL | 18,2 | 否 | 0.00 | 月度总收入（元） |
| total_new_customers | INT | - | 否 | 0 | 月度新增客户数 |
| total_deal_amount | DECIMAL | 18,2 | 否 | 0.00 | 月度总成交额（元） |
| total_deal_count | INT | - | 否 | 0 | 月度成交笔数 |
| avg_satisfaction | DECIMAL | 5,2 | 否 | 0.00 | 月度平均满意度（%） |
| satisfaction_count | INT | - | 否 | 0 | 月度评价总数 |
| completion_rate | DECIMAL | 5,2 | 否 | 0.00 | 收入目标完成率（%） |
| rank_in_dept | INT | - | 是 | NULL | 部门内排名 |
| rank_in_company | INT | - | 是 | NULL | 公司排名 |
| calc_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | 计算时间 |

**索引设计：**
- 主键：summary_id
- 唯一索引：(user_id, summary_month)
- 普通索引：summary_month
- 组合索引：(summary_month, completion_rate DESC)

---

### 2.8 排行榜快照表 (rank_snapshot)

存储各维度排行榜快照，支持历史排名回溯。

| 字段名 | 类型 | 长度 | 是否为空 | 默认值 | 说明 |
|--------|------|------|----------|--------|------|
| snapshot_id | VARCHAR | 32 | 否 | - | 主键 |
| rank_type | TINYINT | 1 | 否 | - | 排行类型：1-收入，2-新增客户，3-成交额 |
| rank_scope | TINYINT | 1 | 否 | 1 | 排行范围：1-全公司，2-部门内 |
| scope_id | VARCHAR | 32 | 是 | NULL | 范围ID（部门ID或'ALL'） |
| stat_period | VARCHAR | 10 | 否 | - | 统计周期：YYYY-MM |
| user_id | VARCHAR | 32 | 否 | - | 员工ID |
| rank_no | INT | - | 否 | - | 排名名次 |
| rank_value | DECIMAL | 18,2 | 否 | 0.00 | 排行指标值 |
| trend | TINYINT | 1 | 是 | 0 | 趋势：-1-下降，0-持平，1-上升 |
| prev_rank | INT | - | 是 | NULL | 上期排名 |
| snapshot_time | DATETIME | - | 否 | CURRENT_TIMESTAMP | 快照时间 |

**索引设计：**
- 主键：snapshot_id
- 唯一索引：(rank_type, rank_scope, scope_id, stat_period, user_id)
- 组合索引：(rank_type, stat_period, rank_no)
- 组合索引：(user_id, stat_period)

---

## 三、指标计算逻辑

### 3.1 收入目标完成度

**计算公式：**
```
收入目标完成度 = (实际累计收入 / 收入目标) × 100%
```

**SQL实现：**
```sql
SELECT 
    u.user_id,
    u.user_name,
    t.revenue_target AS target_amount,
    COALESCE(SUM(r.revenue_amount), 0) AS actual_amount,
    ROUND(
        COALESCE(SUM(r.revenue_amount), 0) / t.revenue_target * 100, 
        2
    ) AS completion_rate
FROM sys_user u
INNER JOIN perf_target t ON u.user_id = t.user_id
LEFT JOIN perf_record r ON u.user_id = r.user_id 
    AND r.record_date BETWEEN '2024-01-01' AND '2024-01-31'
WHERE t.target_period = '2024-01'
    AND t.target_type = 1
GROUP BY u.user_id, u.user_name, t.revenue_target;
```

**边界处理：**
- 目标值为0或NULL时，完成度显示为N/A
- 实际值超过目标值150%时，标记为"超额完成"
- 支持按日/月/季度/年度动态计算

---

### 3.2 客户新增数量

**计算公式：**
```
客户新增数量 = COUNT(DISTINCT cust_id) 
               WHERE first_contact_date >= 周期开始日期
               AND cust_status IN (2, 3)
```

**统计维度：**
- 累计新增：从周期开始到当前日期的累计值
- 目标对比：实际新增数 / 目标新增数

**SQL实现：**
```sql
SELECT 
    u.user_id,
    COUNT(DISTINCT c.cust_id) AS new_customer_count,
    t.customer_target AS target_count,
    ROUND(
        COUNT(DISTINCT c.cust_id) / t.customer_target * 100,
        2
    ) AS customer_completion_rate
FROM sys_user u
LEFT JOIN crm_customer c ON u.user_id = c.owner_id
    AND c.first_contact_date >= '2024-01-01'
    AND c.first_contact_date <= '2024-01-31'
    AND c.cust_status IN (2, 3)
LEFT JOIN perf_target t ON u.user_id = t.user_id
    AND t.target_period = '2024-01'
    AND t.target_type = 1
GROUP BY u.user_id, t.customer_target;
```

---

### 3.3 成交额

**计算公式：**
```
成交额 = SUM(deal_amount) 
        WHERE record_date BETWEEN 周期开始 AND 周期结束
```

**统计口径：**
- 合同签约金额为准
- 支持按客户/产品/区域等多维度聚合
- 大金额订单（>100万）单独标记

**SQL实现：**
```sql
SELECT 
    u.user_id,
    u.user_name,
    SUM(r.deal_amount) AS total_deal_amount,
    SUM(r.deal_count) AS total_deal_count,
    ROUND(AVG(r.deal_amount), 2) AS avg_deal_amount
FROM sys_user u
LEFT JOIN perf_record r ON u.user_id = r.user_id
    AND r.record_date BETWEEN '2024-01-01' AND '2024-01-31'
GROUP BY u.user_id, u.user_name;
```

---

### 3.4 客户满意度

**计算公式：**
```
客户满意度 = (平均评分 / 5) × 100%

其中：平均评分 = SUM(eval_score) / COUNT(eval_id)
```

**评分转换规则：**
- 5星 = 5.00分
- 4星 = 4.00分
- 3星 = 3.00分
- 2星 = 2.00分
- 1星 = 1.00分

**SQL实现：**
```sql
SELECT 
    u.user_id,
    u.user_name,
    COUNT(e.eval_id) AS eval_count,
    ROUND(AVG(e.eval_score), 2) AS avg_score,
    ROUND(AVG(e.eval_score) / 5 * 100, 2) AS satisfaction_rate
FROM sys_user u
LEFT JOIN sat_evaluation e ON u.user_id = e.user_id
    AND e.eval_time BETWEEN '2024-01-01 00:00:00' AND '2024-01-31 23:59:59'
GROUP BY u.user_id, u.user_name
HAVING COUNT(e.eval_id) >= 5;  -- 最少5个评价才计算满意度
```

**特殊处理：**
- 评价数<5时，显示"样本不足"
- 差评（<=3分）自动触发预警通知

---

## 四、排行榜算法说明

### 4.1 排行榜类型定义

| 排行类型 | 标识 | 排序依据 | 更新时间 |
|----------|------|----------|----------|
| 收入排行榜 | REVENUE | 收入金额 DESC | 每日凌晨2:00 |
| 新增客户排行榜 | NEW_CUSTOMER | 新增客户数 DESC | 每日凌晨2:00 |
| 成交额排行榜 | DEAL_AMOUNT | 成交额 DESC | 每日凌晨2:00 |

### 4.2 排名计算算法

#### 4.2.1 基础排名算法（标准竞争排名）

```python
def calculate_ranking(user_stats, rank_type):
    """
    标准竞争排名（1224规则）
    - 相同数值排名相同
    - 下一名次跳过重复排名
    """
    # 按指标值降序排序
    sorted_stats = sorted(user_stats, key=lambda x: x['value'], reverse=True)
    
    current_rank = 1
    prev_value = None
    
    for i, stat in enumerate(sorted_stats):
        if stat['value'] != prev_value:
            current_rank = i + 1
        stat['rank'] = current_rank
        prev_value = stat['value']
    
    return sorted_stats
```

#### 4.2.2 密集排名算法（可选）

```python
def calculate_dense_ranking(user_stats):
    """
    密集排名（1223规则）
    - 相同数值排名相同
    - 下一名次不跳过
    """
    sorted_stats = sorted(user_stats, key=lambda x: x['value'], reverse=True)
    
    current_rank = 1
    prev_value = None
    
    for stat in sorted_stats:
        if prev_value is not None and stat['value'] < prev_value:
            current_rank += 1
        stat['rank'] = current_rank
        prev_value = stat['value']
    
    return sorted_stats
```

### 4.3 趋势计算逻辑

```python
def calculate_trend(current_rank, previous_rank):
    """
    计算排名趋势
    Returns: -1(下降), 0(持平), 1(上升)
    """
    if previous_rank is None:
        return 0  # 无历史数据
    
    if current_rank < previous_rank:
        return 1   # 排名上升（数值变小）
    elif current_rank > previous_rank:
        return -1  # 排名下降（数值变大）
    else:
        return 0   # 排名持平
```

### 4.4 排行榜生成SQL

#### 收入排行榜
```sql
-- 生成月度收入排行榜并存储快照
INSERT INTO rank_snapshot (
    snapshot_id, rank_type, rank_scope, scope_id, 
    stat_period, user_id, rank_no, rank_value, trend, prev_rank
)
SELECT 
    UUID() AS snapshot_id,
    1 AS rank_type,  -- 收入榜
    1 AS rank_scope, -- 全公司
    'ALL' AS scope_id,
    '2024-01' AS stat_period,
    user_id,
    RANK() OVER (ORDER BY total_revenue DESC) AS rank_no,
    total_revenue AS rank_value,
    NULL AS trend,
    NULL AS prev_rank
FROM perf_summary
WHERE summary_month = '2024-01';
```

#### 部门内排行榜
```sql
-- 各部门内部排名
INSERT INTO rank_snapshot (...)
SELECT 
    UUID(),
    1,
    2,  -- 部门内
    d.dept_id,
    '2024-01',
    s.user_id,
    RANK() OVER (PARTITION BY d.dept_id ORDER BY s.total_revenue DESC),
    s.total_revenue,
    NULL,
    NULL
FROM perf_summary s
INNER JOIN sys_user u ON s.user_id = u.user_id
INNER JOIN sys_dept d ON u.dept_id = d.dept_id
WHERE s.summary_month = '2024-01';
```

### 4.5 排行榜刷新策略

| 策略项 | 配置 |
|--------|------|
| 刷新频率 | 每日凌晨2:00 |
| 刷新方式 | 全量重新计算 + 增量更新 |
| 并发控制 | 单线程执行，避免数据竞争 |
| 容错处理 | 失败重试3次，超过则告警 |
| 历史保留 | 保留最近12个月快照 |

### 4.6 TopN榜单截取

```sql
-- 获取收入榜Top 10
SELECT 
    s.rank_no,
    u.user_name,
    d.dept_name,
    s.rank_value AS revenue_amount,
    CASE s.trend 
        WHEN 1 THEN '↑' 
        WHEN -1 THEN '↓' 
        ELSE '-' 
    END AS trend_icon,
    s.prev_rank
FROM rank_snapshot s
INNER JOIN sys_user u ON s.user_id = u.user_id
INNER JOIN sys_dept d ON u.dept_id = d.dept_id
WHERE s.rank_type = 1
    AND s.rank_scope = 1
    AND s.stat_period = '2024-01'
ORDER BY s.rank_no
LIMIT 10;
```

---

## 五、趋势分析图表数据模型

### 5.1 月度趋势数据

```sql
-- 个人月度趋势（最近12个月）
SELECT 
    summary_month,
    total_revenue,
    total_deal_amount,
    total_new_customers,
    avg_satisfaction,
    completion_rate
FROM perf_summary
WHERE user_id = 'USER001'
    AND summary_month >= DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 12 MONTH), '%Y-%m')
ORDER BY summary_month;
```

### 5.2 同比环比计算

```sql
-- 同比环比计算视图
WITH monthly_data AS (
    SELECT 
        summary_month,
        total_revenue,
        LAG(total_revenue, 1) OVER (ORDER BY summary_month) AS mom_revenue,  -- 环比
        LAG(total_revenue, 12) OVER (ORDER BY summary_month) AS yoy_revenue  -- 同比
    FROM perf_summary
    WHERE user_id = 'USER001'
)
SELECT 
    summary_month,
    total_revenue,
    ROUND((total_revenue - mom_revenue) / mom_revenue * 100, 2) AS mom_rate,
    ROUND((total_revenue - yoy_revenue) / yoy_revenue * 100, 2) AS yoy_rate
FROM monthly_data
WHERE mom_revenue IS NOT NULL;
```

### 5.3 预测分析算法

采用简单移动平均法（SMA）进行趋势预测：

```python
def predict_next_month(historical_data, window=3):
    """
    基于移动平均预测下月业绩
    """
    if len(historical_data) < window:
        return None
    
    # 取最近window个月的平均值
    recent_data = historical_data[-window:]
    prediction = sum(recent_data) / len(recent_data)
    
    # 添加增长趋势因子
    if len(historical_data) >= window * 2:
        older_avg = sum(historical_data[-window*2:-window]) / window
        trend_factor = (sum(recent_data) / window) / older_avg if older_avg > 0 else 1
        prediction *= trend_factor
    
    return round(prediction, 2)
```

---

## 六、数据一致性与约束

### 6.1 外键约束

| 主表 | 从表 | 外键字段 | 级联操作 |
|------|------|----------|----------|
| sys_user | perf_target | user_id | CASCADE DELETE |
| sys_user | perf_record | user_id | CASCADE DELETE |
| sys_user | crm_customer | owner_id | SET NULL |
| sys_dept | sys_user | dept_id | RESTRICT |
| perf_target | sat_evaluation | target_id | CASCADE DELETE |

### 6.2 检查约束

```sql
-- 业绩记录金额不能为负
ALTER TABLE perf_record 
ADD CONSTRAINT chk_amount_positive 
CHECK (revenue_amount >= 0 AND deal_amount >= 0);

-- 满意度评分范围检查
ALTER TABLE sat_evaluation 
ADD CONSTRAINT chk_score_range 
CHECK (eval_score >= 1.00 AND eval_score <= 5.00);

-- 目标完成率不能超过合理范围（允许超额，但不超过500%）
ALTER TABLE perf_summary 
ADD CONSTRAINT chk_completion_rate 
CHECK (completion_rate >= 0 AND completion_rate <= 500);
```

### 6.3 触发器设计

```sql
-- 自动更新汇总表（可选，也可用定时任务）
DELIMITER $$
CREATE TRIGGER trg_after_perf_insert 
AFTER INSERT ON perf_record
FOR EACH ROW
BEGIN
    -- 调用存储过程更新月度汇总
    CALL sp_update_monthly_summary(NEW.user_id, NEW.record_date);
END$$
DELIMITER ;
```

---

## 七、性能优化建议

### 7.1 索引优化
- 所有时间字段建立索引，支持时间范围查询
- 金额字段根据查询频率考虑建立索引
- 复合查询使用覆盖索引

### 7.2 分区策略
- `perf_record` 表按 `record_date` 按月分区
- `perf_summary` 表按 `summary_month` 按年分区

### 7.3 缓存策略
- 排行榜数据缓存24小时
- 个人业绩看板数据缓存1小时
- 趋势分析数据缓存4小时

### 7.4 读写分离
- 报表查询走只读副本
- 数据写入走主库

---

## 八、附录

### 8.1 枚举值定义

| 枚举名称 | 值 | 说明 |
|----------|-----|------|
| target_type | 1 | 月度目标 |
| target_type | 2 | 季度目标 |
| target_type | 3 | 年度目标 |
| rank_type | 1 | 收入排行榜 |
| rank_type | 2 | 新增客户排行榜 |
| rank_type | 3 | 成交额排行榜 |
| rank_scope | 1 | 全公司 |
| rank_scope | 2 | 部门内 |

### 8.2 数据字典版本

| 版本 | 日期 | 修改内容 | 作者 |
|------|------|----------|------|
| v1.0 | 2024-01 | 初始版本 | 数据架构组 |

---

*文档结束*

---

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

---

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

---

# 业务支持中心 - 队伍状况模块数据建模方案

## 一、概述

本方案为业务支持中心的队伍状况模块设计完整的数据模型，涵盖机构经纪团队管理、研究所协同、资管协同三大业务域。

---

## 二、实体关系图（ER图文字描述）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            队伍状况模块 ER图                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   员工(Staff)   │     │   团队(Team)    │     │  部门(Department)│
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ PK staff_id     │◄────┤ PK team_id      │◄────┤ PK dept_id      │
│    name         │     │    team_name    │     │    dept_name    │
│    position     │     │ FK dept_id      │     │    manager_id   │
│    team_id      │────►│    team_leader  │     │                 │
│    status       │     │                 │     │                 │
│    workload_pct │     │                 │     │                 │
└────────┬────────┘     └─────────────────┘     └─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  在线状态记录   │     │   工作日志      │     │   技能标签      │
│ (OnlineStatus)  │     │  (WorkLog)      │     │  (SkillTag)     │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ PK status_id    │     │ PK log_id       │     │ PK tag_id       │
│ FK staff_id     │     │ FK staff_id     │     │ FK staff_id     │
│    status       │     │    log_date     │     │    skill_name   │
│    start_time   │     │    work_item    │     │    proficiency  │
│    end_time     │     │    duration_min │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           协同业务域                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│  协同需求       │◄────────┤   协同记录      │────────►│  满意度评价     │
│(CollabRequest)  │   1:1   │ (CollabRecord)  │   1:1   │ (Satisfaction)  │
├─────────────────┤         ├─────────────────┤         ├─────────────────┤
│ PK request_id   │         │ PK record_id    │         │ PK eval_id      │
│    request_type │         │ FK request_id   │         │ FK record_id    │
│    requester    │         │ FK staff_id     │         │    score        │
│    title        │         │    start_time   │         │    comment      │
│    priority     │         │    end_time     │         │    eval_time    │
│    status       │         │    status       │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
         │                           │
         │ N:1                       │ N:1
         ▼                           ▼
┌─────────────────┐         ┌─────────────────┐
│   研究所        │         │   资管项目      │
│ (ResearchInst)  │         │  (AssetMgmt)    │
├─────────────────┤         ├─────────────────┤
│ PK inst_id      │         │ PK project_id   │
│    inst_name    │         │    project_name │
│    contact      │         │    project_type │
│    dept         │         │    manager      │
└─────────────────┘         │    start_date   │
                            │    end_date     │
                            │    progress_pct │
                            └─────────────────┘
                                     │
                                     │ 1:N
                                     ▼
                            ┌─────────────────┐
                            │  项目成果       │
                            │(ProjectOutput)  │
                            ├─────────────────┤
                            │ PK output_id    │
                            │ FK project_id   │
                            │    output_type  │
                            │    description  │
                            │    create_date  │
                            └─────────────────┘
```

### 关系说明

| 关系 | 类型 | 描述 |
|------|------|------|
| 员工 ↔ 团队 | N:1 | 一个团队包含多名员工 |
| 团队 ↔ 部门 | N:1 | 一个部门包含多个团队 |
| 员工 ↔ 在线状态 | 1:N | 一名员工有多条状态记录 |
| 员工 ↔ 工作日志 | 1:N | 一名员工有多条工作记录 |
| 员工 ↔ 技能标签 | 1:N | 一名员工有多个技能标签 |
| 协同需求 ↔ 协同记录 | 1:1 | 一个需求对应一条处理记录 |
| 协同记录 ↔ 满意度评价 | 1:1 | 一条记录对应一个评价 |
| 协同需求 ↔ 研究所 | N:1 | 多个需求可能来自同一研究所 |
| 协同记录 ↔ 资管项目 | N:1 | 多条记录可能关联同一项目 |
| 资管项目 ↔ 项目成果 | 1:N | 一个项目有多个成果 |

---

## 三、数据表结构设计

### 3.1 核心人员表

#### 3.1.1 员工表 (staff)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| staff_id | VARCHAR(32) | PK, NOT NULL | 员工唯一标识 |
| name | VARCHAR(50) | NOT NULL | 姓名 |
| employee_no | VARCHAR(20) | UNIQUE | 工号 |
| department_id | VARCHAR(32) | FK | 所属部门ID |
| team_id | VARCHAR(32) | FK | 所属团队ID |
| position | VARCHAR(50) | NOT NULL | 职位（如：经理/专员/助理） |
| role_type | TINYINT | DEFAULT 1 | 角色类型：1-机构经纪，2-研究所，3-资管 |
| phone | VARCHAR(20) | | 联系电话 |
| email | VARCHAR(100) | | 邮箱 |
| entry_date | DATE | | 入职日期 |
| status | TINYINT | DEFAULT 1 | 在职状态：0-离职，1-在职，2-休假 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |
| updated_at | DATETIME | ON UPDATE NOW() | 更新时间 |

#### 3.1.2 部门表 (department)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| dept_id | VARCHAR(32) | PK, NOT NULL | 部门唯一标识 |
| dept_name | VARCHAR(100) | NOT NULL | 部门名称 |
| dept_code | VARCHAR(20) | UNIQUE | 部门编码 |
| manager_id | VARCHAR(32) | FK | 部门负责人ID |
| parent_id | VARCHAR(32) | FK | 上级部门ID |
| sort_order | INT | DEFAULT 0 | 排序顺序 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |

#### 3.1.3 团队表 (team)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| team_id | VARCHAR(32) | PK, NOT NULL | 团队唯一标识 |
| team_name | VARCHAR(100) | NOT NULL | 团队名称 |
| team_code | VARCHAR(20) | UNIQUE | 团队编码 |
| dept_id | VARCHAR(32) | FK, NOT NULL | 所属部门ID |
| leader_id | VARCHAR(32) | FK | 团队负责人ID |
| max_members | INT | DEFAULT 15 | 团队最大人数 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |

### 3.2 状态与负载表

#### 3.2.1 在线状态实时表 (staff_online_status)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| status_id | VARCHAR(32) | PK, NOT NULL | 状态记录ID |
| staff_id | VARCHAR(32) | FK, NOT NULL, INDEX | 员工ID |
| current_status | TINYINT | NOT NULL | 当前状态：1-在线，2-忙碌，3-离开，4-离线 |
| workload_pct | DECIMAL(5,2) | DEFAULT 0.00 | 当前工作负载百分比(0-100) |
| active_task_count | INT | DEFAULT 0 | 当前活跃任务数 |
| status_start_time | DATETIME | NOT NULL | 当前状态开始时间 |
| last_heartbeat | DATETIME | | 最后心跳时间 |
| updated_at | DATETIME | ON UPDATE NOW() | 更新时间 |

#### 3.2.2 状态变更历史表 (status_history)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| history_id | VARCHAR(32) | PK, NOT NULL | 历史记录ID |
| staff_id | VARCHAR(32) | FK, NOT NULL, INDEX | 员工ID |
| from_status | TINYINT | | 原状态 |
| to_status | TINYINT | NOT NULL | 新状态 |
| change_time | DATETIME | NOT NULL, INDEX | 变更时间 |
| change_reason | VARCHAR(200) | | 变更原因 |

#### 3.2.3 工作负载明细表 (workload_detail)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| workload_id | VARCHAR(32) | PK, NOT NULL | 负载记录ID |
| staff_id | VARCHAR(32) | FK, NOT NULL, INDEX | 员工ID |
| task_type | TINYINT | NOT NULL | 任务类型：1-机构经纪，2-研究所协同，3-资管协同 |
| task_id | VARCHAR(32) | NOT NULL | 关联任务ID |
| task_name | VARCHAR(200) | NOT NULL | 任务名称 |
| workload_weight | DECIMAL(5,2) | NOT NULL | 任务权重(占负载百分比) |
| start_time | DATETIME | | 任务开始时间 |
| expected_end | DATETIME | | 预计完成时间 |
| actual_end | DATETIME | | 实际完成时间 |
| status | TINYINT | DEFAULT 1 | 任务状态：1-进行中，2-已完成，3-暂停 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |

### 3.3 研究所协同表

#### 3.3.1 研究所信息表 (research_institute)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| inst_id | VARCHAR(32) | PK, NOT NULL | 研究所ID |
| inst_name | VARCHAR(100) | NOT NULL | 研究所名称 |
| inst_code | VARCHAR(20) | UNIQUE | 研究所编码 |
| research_field | VARCHAR(200) | | 研究领域 |
| contact_person | VARCHAR(50) | | 联系人 |
| contact_phone | VARCHAR(20) | | 联系电话 |
| status | TINYINT | DEFAULT 1 | 状态：1-正常，0-停用 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |

#### 3.3.2 协同需求表 (collab_request)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| request_id | VARCHAR(32) | PK, NOT NULL | 需求ID |
| request_no | VARCHAR(30) | UNIQUE, NOT NULL | 需求编号（如：REQ20240307XXXX） |
| request_type | TINYINT | NOT NULL | 需求类型：1-数据支持，2-研究报告，3-路演支持，4-其他 |
| source_type | TINYINT | NOT NULL | 来源类型：1-研究所，2-资管 |
| source_id | VARCHAR(32) | NOT NULL | 来源ID |
| requester_name | VARCHAR(50) | NOT NULL | 需求提出人 |
| requester_contact | VARCHAR(50) | | 联系方式 |
| title | VARCHAR(200) | NOT NULL | 需求标题 |
| description | TEXT | | 需求描述 |
| priority | TINYINT | DEFAULT 2 | 优先级：1-紧急，2-高，3-中，4-低 |
| expected_finish | DATETIME | | 期望完成时间 |
| status | TINYINT | DEFAULT 1 | 状态：1-待分配，2-处理中，3-待验收，4-已完成，5-已关闭 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |
| created_by | VARCHAR(32) | | 创建人 |

#### 3.3.3 协同服务记录表 (collab_service_record)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| record_id | VARCHAR(32) | PK, NOT NULL | 记录ID |
| request_id | VARCHAR(32) | FK, NOT NULL, UNIQUE | 关联需求ID |
| staff_id | VARCHAR(32) | FK, NOT NULL | 处理人员ID |
| receive_time | DATETIME | NOT NULL | 接收时间 |
| start_time | DATETIME | | 实际开始时间 |
| end_time | DATETIME | | 完成时间 |
| service_content | TEXT | | 服务内容描述 |
| deliverables | TEXT | | 交付物说明 |
| actual_workload | DECIMAL(5,2) | | 实际工作量（小时） |
| status | TINYINT | DEFAULT 1 | 状态：1-处理中，2-已完成，3-已取消 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |

#### 3.3.4 满意度评价表 (satisfaction_evaluation)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| eval_id | VARCHAR(32) | PK, NOT NULL | 评价ID |
| record_id | VARCHAR(32) | FK, NOT NULL, UNIQUE | 关联服务记录ID |
| overall_score | TINYINT | NOT NULL | 综合评分（1-5分） |
| timeliness_score | TINYINT | | 及时性评分（1-5分） |
| quality_score | TINYINT | | 质量评分（1-5分） |
| attitude_score | TINYINT | | 服务态度评分（1-5分） |
| comment | VARCHAR(500) | | 评价内容 |
| evaluator_name | VARCHAR(50) | | 评价人 |
| eval_time | DATETIME | DEFAULT NOW() | 评价时间 |
| is_anonymous | TINYINT | DEFAULT 0 | 是否匿名：0-否，1-是 |

### 3.4 资管协同表

#### 3.4.1 资管项目表 (asset_mgmt_project)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| project_id | VARCHAR(32) | PK, NOT NULL | 项目ID |
| project_no | VARCHAR(30) | UNIQUE, NOT NULL | 项目编号 |
| project_name | VARCHAR(200) | NOT NULL | 项目名称 |
| project_type | TINYINT | NOT NULL | 项目类型：1-产品开发，2-投研支持，3-系统对接，4-其他 |
| manager_id | VARCHAR(32) | FK | 项目负责人ID |
| partner_dept | VARCHAR(100) | | 合作部门 |
| start_date | DATE | NOT NULL | 项目开始日期 |
| planned_end_date | DATE | | 计划完成日期 |
| actual_end_date | DATE | | 实际完成日期 |
| progress_pct | DECIMAL(5,2) | DEFAULT 0.00 | 当前进度百分比 |
| status | TINYINT | DEFAULT 1 | 状态：1-筹备中，2-进行中，3-验收中，4-已完成，5-已暂停 |
| priority | TINYINT | DEFAULT 2 | 优先级：1-紧急，2-高，3-中，4-低 |
| description | TEXT | | 项目描述 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |

#### 3.4.2 项目进度跟踪表 (project_progress)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| progress_id | VARCHAR(32) | PK, NOT NULL | 进度记录ID |
| project_id | VARCHAR(32) | FK, NOT NULL, INDEX | 关联项目ID |
| milestone_name | VARCHAR(100) | NOT NULL | 里程碑名称 |
| planned_date | DATE | | 计划完成日期 |
| actual_date | DATE | | 实际完成日期 |
| progress_pct | DECIMAL(5,2) | NOT NULL | 此阶段进度占比 |
| status | TINYINT | DEFAULT 1 | 状态：1-未开始，2-进行中，3-已完成，4-延期 |
| remark | VARCHAR(500) | | 备注 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |

#### 3.4.3 项目成果记录表 (project_output)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| output_id | VARCHAR(32) | PK, NOT NULL | 成果ID |
| project_id | VARCHAR(32) | FK, NOT NULL, INDEX | 关联项目ID |
| output_type | TINYINT | NOT NULL | 成果类型：1-文档，2-系统，3-报告，4-数据，5-其他 |
| output_name | VARCHAR(200) | NOT NULL | 成果名称 |
| description | TEXT | | 成果描述 |
| file_url | VARCHAR(500) | | 附件链接 |
| create_date | DATE | NOT NULL | 成果产出日期 |
| creator_id | VARCHAR(32) | FK | 创建人ID |
| is_key_output | TINYINT | DEFAULT 0 | 是否关键成果：0-否，1-是 |
| created_at | DATETIME | DEFAULT NOW() | 创建时间 |

---

## 四、负载计算模型

### 4.1 负载计算公式

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         员工工作负载计算模型                                 │
└─────────────────────────────────────────────────────────────────────────────┘

总负载 = Σ(任务权重 × 时间系数 × 难度系数)

其中：
┌────────────────────────────────────────────────────────┐
│ 任务权重(TaskWeight)                                    │
├────────────────────────────────────────────────────────┤
│ 基础权重 = 任务预估工时 / 日标准工时(8h)                │
│                                                         │
│ 权重调整因子：                                          │
│ • 高优先级任务：权重 × 1.2                              │
│ • 紧急任务：权重 × 1.5                                  │
│ • 跨团队协作：权重 × 1.1                                │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│ 时间系数(TimeFactor)                                    │
├────────────────────────────────────────────────────────┤
│ • 距截止日期 > 3天：1.0                                 │
│ • 距截止日期 1-3天：1.2                                 │
│ • 截止日期当天：1.5                                     │
│ • 已延期：2.0                                           │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│ 难度系数(DifficultyFactor)                              │
├────────────────────────────────────────────────────────┤
│ • 常规任务：1.0                                         │
│ • 复杂任务：1.2                                         │
│ • 创新/探索性任务：1.5                                  │
└────────────────────────────────────────────────────────┘
```

### 4.2 负载等级划分

| 负载百分比 | 等级 | 状态颜色 | 处理建议 |
|------------|------|----------|----------|
| 0% - 30% | 轻载 | 🟢 绿色 | 可接受新任务 |
| 31% - 60% | 正常 | 🔵 蓝色 | 正常工作中 |
| 61% - 80% | 高载 | 🟡 黄色 | 谨慎分配任务 |
| 81% - 95% | 满载 | 🟠 橙色 | 不推荐新任务 |
| 96% - 100% | 超载 | 🔴 红色 | 需调整任务分配 |

### 4.3 团队负载统计

```sql
-- 团队实时负载查询示例
SELECT 
    t.team_id,
    t.team_name,
    COUNT(s.staff_id) AS total_members,
    SUM(CASE WHEN sos.current_status = 1 THEN 1 ELSE 0 END) AS online_count,
    SUM(CASE WHEN sos.current_status = 2 THEN 1 ELSE 0 END) AS busy_count,
    ROUND(AVG(sos.workload_pct), 2) AS avg_workload_pct,
    MAX(sos.workload_pct) AS max_workload_pct
FROM team t
LEFT JOIN staff s ON t.team_id = s.team_id
LEFT JOIN staff_online_status sos ON s.staff_id = sos.staff_id
WHERE s.status = 1
GROUP BY t.team_id, t.team_name;
```

### 4.4 负载预警机制

| 预警级别 | 触发条件 | 通知方式 | 响应时间 |
|----------|----------|----------|----------|
| 提示 | 个人负载 > 80% | 系统消息 | - |
| 警告 | 个人负载 > 90% 或团队平均 > 75% | 站内信 + 邮件 | 4小时内 |
| 紧急 | 个人负载 > 95% 或任务延期 | 短信 + 电话 | 1小时内 |

---

## 五、协同效率指标

### 5.1 核心KPI指标体系

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        协同效率指标体系                                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  一级指标                    二级指标                      计算方式         │
├─────────────────────────────────────────────────────────────────────────────┤
│                              ├─ 需求响应时间      接收时间 - 创建时间        │
│  响应效率 (20%)              ├─ 任务启动时间      开始时间 - 接收时间        │
│                              └─ 平均首次响应      AVG(响应时间)             │
├─────────────────────────────────────────────────────────────────────────────┤
│                              ├─ 按时完成率        按时完成数/总完成数        │
│  处理效率 (30%)              ├─ 平均处理时长      AVG(完成时间-开始时间)     │
│                              └─ 任务吞吐量        完成任务数/工作时长        │
├─────────────────────────────────────────────────────────────────────────────┤
│                              ├─ 满意度评分        AVG(overall_score)        │
│  质量指标 (25%)              ├─ 返工率            返工次数/总交付次数        │
│                              └─ 投诉率            投诉次数/总服务次数        │
├─────────────────────────────────────────────────────────────────────────────┤
│                              ├─ 资源利用率        实际工作量/可用工时        │
│  资源效率 (15%)              ├─ 负载均衡度        1 - 标准差/平均值          │
│                              └─ 技能匹配度        匹配任务数/总分配数        │
├─────────────────────────────────────────────────────────────────────────────┤
│                              ├─ 项目按期完成率    按期完成项目/总项目数      │
│  项目协同 (10%)              ├─ 里程碑达成率      达成里程碑/总里程碑        │
│                              └─ 成果交付率        实际交付成果/计划成果      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 详细指标计算

#### 5.2.1 研究所协同指标

| 指标名称 | 计算公式 | 目标值 | 权重 |
|----------|----------|--------|------|
| 需求响应及时率 | (30分钟内响应的需求数 / 总需求数) × 100% | ≥ 90% | 15% |
| 平均处理时长 | SUM(完成时间 - 开始时间) / 完成需求数 | ≤ 4小时 | 20% |
| 按时交付率 | (按时完成需求数 / 总完成需求数) × 100% | ≥ 85% | 20% |
| 平均满意度 | SUM(overall_score) / 评价数 | ≥ 4.5分 | 25% |
| 协同成功率 | (成功完成的协同数 / 总协同数) × 100% | ≥ 95% | 20% |

#### 5.2.2 资管协同指标

| 指标名称 | 计算公式 | 目标值 | 权重 |
|----------|----------|--------|------|
| 项目按期完成率 | (按期完成项目数 / 总完成项目数) × 100% | ≥ 80% | 30% |
| 里程碑达成率 | (按期达成里程碑数 / 总里程碑数) × 100% | ≥ 85% | 25% |
| 成果交付完整率 | (实际交付成果数 / 计划成果数) × 100% | ≥ 90% | 20% |
| 项目质量评分 | AVG(项目验收评分) | ≥ 4.0分 | 15% |
| 资源利用效率 | 实际有效工时 / 计划投入工时 | ≥ 85% | 10% |

### 5.3 协同效率评分模型

```
协同效率总分 = Σ(各项指标得分 × 指标权重)

┌────────────────────────────────────────────────────────┐
│ 指标得分计算规则                                        │
├────────────────────────────────────────────────────────┤
│ 达成率/满意度类指标：                                   │
│   得分 = min(100, (实际值 / 目标值) × 100)              │
│                                                         │
│ 时长类指标（越小越好）：                                │
│   得分 = max(0, (目标值 / 实际值) × 100)                │
│                                                         │
│ 评分等级：                                              │
│   90-100分：优秀 🏆                                    │
│   80-89分： 良好 👍                                     │
│   70-79分： 合格 ✓                                      │
│   60-69分： 待改进 ⚠️                                   │
│   <60分：   不合格 ❌                                   │
└────────────────────────────────────────────────────────┘
```

### 5.4 实时仪表盘指标

| 指标 | 更新频率 | 数据来源 |
|------|----------|----------|
| 在线人数/总人数 | 实时 | staff_online_status |
| 当前处理中需求数 | 实时 | collab_request |
| 今日已完成任务数 | 5分钟 | collab_service_record |
| 平均负载百分比 | 实时 | staff_online_status |
| 今日满意度平均分 | 15分钟 | satisfaction_evaluation |
| 进行中项目数 | 30分钟 | asset_mgmt_project |

### 5.5 效率改进建议触发条件

| 场景 | 触发条件 | 建议措施 |
|------|----------|----------|
| 负载不均 | 团队内负载标准差 > 20% | 重新分配任务，考虑技能匹配 |
| 响应延迟 | 平均响应时间 > 30分钟 | 增加在线人员，优化排班 |
| 满意度下降 | 近7天平均满意度 < 4.0 | 服务质量复盘，技能培训 |
| 延期频发 | 延期率 > 15% | 评估工作量，调整排期 |
| 资源闲置 | 在线人员负载 < 30%占比 > 30% | 任务分配优化，人员调配 |

---

## 六、数据字典补充

### 6.1 状态枚举值

| 枚举类型 | 值 | 含义 |
|----------|-----|------|
| staff.status | 0 | 离职 |
| staff.status | 1 | 在职 |
| staff.status | 2 | 休假 |
| current_status | 1 | 在线 |
| current_status | 2 | 忙碌 |
| current_status | 3 | 离开 |
| current_status | 4 | 离线 |
| request_type | 1 | 数据支持 |
| request_type | 2 | 研究报告 |
| request_type | 3 | 路演支持 |
| request_type | 4 | 其他 |
| collab_request.status | 1 | 待分配 |
| collab_request.status | 2 | 处理中 |
| collab_request.status | 3 | 待验收 |
| collab_request.status | 4 | 已完成 |
| collab_request.status | 5 | 已关闭 |
| project_type | 1 | 产品开发 |
| project_type | 2 | 投研支持 |
| project_type | 3 | 系统对接 |
| project_type | 4 | 其他 |

### 6.2 索引设计建议

| 表名 | 索引字段 | 索引类型 | 说明 |
|------|----------|----------|------|
| staff | team_id + status | 组合索引 | 团队人员查询 |
| staff_online_status | staff_id | 唯一索引 | 员工状态查询 |
| staff_online_status | current_status | 普通索引 | 按状态统计 |
| collab_request | status + priority | 组合索引 | 待处理需求查询 |
| collab_request | source_id + source_type | 组合索引 | 来源查询 |
| collab_service_record | staff_id + end_time | 组合索引 | 员工工作量统计 |
| asset_mgmt_project | status + progress_pct | 组合索引 | 项目进度查询 |

---

## 七、总结

本数据建模方案完整覆盖了业务支持中心队伍状况模块的三大业务域：

1. **机构经纪团队**：支持12人团队的人员信息、在线状态、工作负载管理
2. **研究所协同**：涵盖需求管理、服务记录、满意度评价全流程
3. **资管协同**：实现项目跟踪、进度管理、成果记录闭环

通过科学的负载计算模型和多维度的协同效率指标体系，为团队管理决策提供数据支撑。

---

*文档版本：v1.0*  
*创建时间：2024年*  
*适用模块：业务支持中心 - 队伍状况模块*

---

# 业务支持中心 - 风险提示模块 数据建模方案

## 文档信息
- **文档版本**: v1.0
- **创建日期**: 2026-03-07
- **适用范围**: 业务支持中心风险提示模块

---

## 1. 实体关系图（ER图）

### 1.1 核心实体概览

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   客户信息表    │     │   持仓明细表    │     │ 集中度预警记录  │
│   (customer)    │     │   (position)    │     │ (concentration_ │
│                 │     │                 │     │    _alert)      │
└────────┬────────┘     └────────┬────────┘     └─────────────────┘
         │                       │
         │    1:N                │ 1:N
         └───────────────────────┘
         
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   舆情数据源    │     │   舆情分析表    │     │ 舆情趋势分析    │
│ (sentiment_src) │────▶│ (sentiment_ana) │────▶│(sentiment_trend)│
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │
         │
         ▼
┌─────────────────┐
│  舆情传播轨迹   │
│ (sentiment_spread)│
└─────────────────┘

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   合规检查项    │     │  合规检查记录   │     │  整改跟踪记录   │
│(compliance_item)│────▶│(compliance_chk) │────▶│(rectify_track)  │
│                 │ 1:N │                 │ 1:N │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │
         │
         ▼
┌─────────────────┐
│  合规检查模板   │
│(compliance_tpl) │
└─────────────────┘
```

### 1.2 实体关系详细说明

#### 1.2.1 集中度风险模块
- **客户信息表 (customer)** → **持仓明细表 (position)**: 一对多关系，一个客户可持有多个产品
- **持仓明细表 (position)** → **集中度预警记录 (concentration_alert)**: 一对多关系，一个持仓可能触发多次预警
- **客户信息表 (customer)** → **集中度预警记录 (concentration_alert)**: 一对多关系，直接关联客户与预警

#### 1.2.2 舆情风险模块
- **舆情数据源 (sentiment_source)** → **舆情分析表 (sentiment_analysis)**: 一对多关系，一个数据源产生多条舆情
- **舆情分析表 (sentiment_analysis)** → **舆情趋势分析 (sentiment_trend)**: 一对多关系，按时间维度聚合
- **舆情分析表 (sentiment_analysis)** → **舆情传播轨迹 (sentiment_spread)**: 一对多关系，追踪传播路径

#### 1.2.3 合规检查模块
- **合规检查项 (compliance_item)** → **合规检查记录 (compliance_check)**: 一对多关系，一个检查项可多次检查
- **合规检查记录 (compliance_check)** → **整改跟踪记录 (rectify_track)**: 一对多关系，一次检查可对应多轮整改
- **合规检查模板 (compliance_template)** → **合规检查项 (compliance_item)**: 一对多关系，模板包含多个检查项

---

## 2. 数据表结构设计

### 2.1 集中度风险模块

#### 表 2.1.1: 客户信息表 (risk_customer)
| 字段名 | 字段类型 | 约束 | 说明 |
|--------|----------|------|------|
| customer_id | VARCHAR(32) | PK, NOT NULL | 客户唯一标识 |
| customer_code | VARCHAR(64) | UK, NOT NULL | 客户编码 |
| customer_name | VARCHAR(128) | NOT NULL | 客户名称 |
| customer_type | TINYINT | NOT NULL | 客户类型: 1-个人, 2-机构, 3-产品 |
| risk_level | TINYINT | DEFAULT 3 | 客户风险等级: 1-5级 |
| total_assets | DECIMAL(20,4) | DEFAULT 0 | 总资产（元）|
| total_position | DECIMAL(20,4) | DEFAULT 0 | 总持仓市值（元）|
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | ON UPDATE CURRENT_TIMESTAMP | 更新时间 |
| status | TINYINT | DEFAULT 1 | 状态: 0-禁用, 1-正常 |

#### 表 2.1.2: 持仓明细表 (risk_position)
| 字段名 | 字段类型 | 约束 | 说明 |
|--------|----------|------|------|
| position_id | VARCHAR(32) | PK, NOT NULL | 持仓唯一标识 |
| customer_id | VARCHAR(32) | FK, NOT NULL | 客户ID |
| product_code | VARCHAR(32) | NOT NULL | 产品代码 |
| product_name | VARCHAR(128) | NOT NULL | 产品名称 |
| product_type | TINYINT | NOT NULL | 产品类型: 1-股票, 2-债券, 3-基金, 4-衍生品 |
| position_qty | DECIMAL(18,4) | NOT NULL | 持仓数量 |
| position_cost | DECIMAL(20,4) | NOT NULL | 持仓成本（元）|
| market_value | DECIMAL(20,4) | NOT NULL | 市值（元）|
| position_ratio | DECIMAL(5,4) | NOT NULL | 持仓占比(小数) |
| position_date | DATE | NOT NULL | 持仓日期 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

#### 表 2.1.3: 集中度阈值配置表 (risk_concentration_threshold)
| 字段名 | 字段类型 | 约束 | 说明 |
|--------|----------|------|------|
| threshold_id | VARCHAR(32) | PK, NOT NULL | 阈值配置ID |
| customer_type | TINYINT | NOT NULL | 客户类型 |
| product_type | TINYINT | NOT NULL | 产品类型 |
| warning_level_1 | DECIMAL(5,4) | DEFAULT 0.3 | 一级预警阈值(30%) |
| warning_level_2 | DECIMAL(5,4) | DEFAULT 0.5 | 二级预警阈值(50%) |
| warning_level_3 | DECIMAL(5,4) | DEFAULT 0.7 | 三级预警阈值(70%) |
| is_active | TINYINT | DEFAULT 1 | 是否启用: 0-否, 1-是 |
| effective_date | DATE | NOT NULL | 生效日期 |
| expiry_date | DATE | NULL | 失效日期 |
| created_by | VARCHAR(32) | NOT NULL | 创建人 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

#### 表 2.1.4: 集中度预警记录表 (risk_concentration_alert)
| 字段名 | 字段类型 | 约束 | 说明 |
|--------|----------|------|------|
| alert_id | VARCHAR(32) | PK, NOT NULL | 预警唯一标识 |
| customer_id | VARCHAR(32) | FK, NOT NULL | 客户ID |
| position_id | VARCHAR(32) | FK, NOT NULL | 持仓ID |
| product_code | VARCHAR(32) | NOT NULL | 产品代码 |
| current_ratio | DECIMAL(5,4) | NOT NULL | 当前持仓占比 |
| threshold_ratio | DECIMAL(5,4) | NOT NULL | 触发阈值 |
| warning_level | TINYINT | NOT NULL | 预警级别: 1-3级 |
| alert_status | TINYINT | DEFAULT 1 | 预警状态: 1-未处理, 2-处理中, 3-已处理, 4-已忽略 |
| alert_date | DATE | NOT NULL | 预警日期 |
| alert_time | DATETIME | NOT NULL | 预警时间 |
| handler_id | VARCHAR(32) | NULL | 处理人ID |
| handled_at | DATETIME | NULL | 处理时间 |
| handle_remark | VARCHAR(500) | NULL | 处理备注 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

---

### 2.2 舆情风险模块

#### 表 2.2.1: 舆情数据源配置表 (risk_sentiment_source)
| 字段名 | 字段类型 | 约束 | 说明 |
|--------|----------|------|------|
| source_id | VARCHAR(32) | PK, NOT NULL | 数据源ID |
| source_name | VARCHAR(64) | NOT NULL | 数据源名称 |
| source_type | TINYINT | NOT NULL | 类型: 1-新闻, 2-社交媒体, 3-论坛, 4-自媒体, 5-其他 |
| source_url | VARCHAR(255) | NULL | 源地址 |
| crawl_frequency | INT | DEFAULT 300 | 爬取频率(秒) |
| is_active | TINYINT | DEFAULT 1 | 是否启用 |
| weight_factor | DECIMAL(3,2) | DEFAULT 1.0 | 权重系数 |
| reliability_score | DECIMAL(3,2) | DEFAULT 0.8 | 可信度评分 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

#### 表 2.2.2: 舆情分析表 (risk_sentiment_analysis)
| 字段名 | 字段类型 | 约束 | 说明 |
|--------|----------|------|------|
| analysis_id | VARCHAR(32) | PK, NOT NULL | 分析记录ID |
| source_id | VARCHAR(32) | FK, NOT NULL | 数据源ID |
| external_id | VARCHAR(64) | UK | 外部唯一标识 |
| title | VARCHAR(255) | NOT NULL | 舆情标题 |
| content | TEXT | NOT NULL | 舆情内容 |
| content_url | VARCHAR(500) | NULL | 原文链接 |
| publish_time | DATETIME | NOT NULL | 发布时间 |
| crawl_time | DATETIME | NOT NULL | 爬取时间 |
| sentiment_score | DECIMAL(5,4) | NOT NULL | 情感评分: -1~1 |
| sentiment_label | TINYINT | NOT NULL | 情感标签: 1-负面, 2-中性, 3-正面 |
| confidence | DECIMAL(3,2) | NOT NULL | 置信度 |
| keywords | VARCHAR(500) | NULL | 提取关键词(JSON数组) |
| related_products | VARCHAR(500) | NULL | 相关产品代码(JSON数组) |
| related_customers | VARCHAR(500) | NULL | 相关客户ID(JSON数组) |
| is_important | TINYINT | DEFAULT 0 | 是否重要: 0-否, 1-是 |
| view_count | INT | DEFAULT 0 | 阅读量/热度 |
| share_count | INT | DEFAULT 0 | 转发量 |
| comment_count | INT | DEFAULT 0 | 评论量 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

#### 表 2.2.3: 舆情趋势分析表 (risk_sentiment_trend)
| 字段名 | 字段类型 | 约束 | 说明 |
|--------|----------|------|------|
| trend_id | VARCHAR(32) | PK, NOT NULL | 趋势记录ID |
| analysis_id | VARCHAR(32) | FK, NOT NULL | 关联分析ID |
| product_code | VARCHAR(32) | NULL | 产品代码 |
| customer_id | VARCHAR(32) | NULL | 客户ID |
| trend_date | DATE | NOT NULL | 趋势日期 |
| sentiment_avg | DECIMAL(5,4) | NOT NULL | 平均情感分 |
| sentiment_volatility | DECIMAL(5,4) | NULL | 情感波动率 |
| mention_count | INT | DEFAULT 0 | 提及次数 |
| trend_direction | TINYINT | NOT NULL | 趋势方向: 1-上升, 2-平稳, 3-下降 |
| heat_index | INT | DEFAULT 0 | 热度指数 |
| warning_flag | TINYINT | DEFAULT 0 | 预警标志: 0-无, 1-一级, 2-二级, 3-三级 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

#### 表 2.2.4: 舆情传播轨迹表 (risk_sentiment_spread)
| 字段名 | 字段类型 | 约束 | 说明 |
|--------|----------|------|------|
| spread_id | VARCHAR(32) | PK, NOT NULL | 传播记录ID |
| analysis_id | VARCHAR(32) | FK, NOT NULL | 关联分析ID |
| parent_spread_id | VARCHAR(32) | FK, NULL | 父级传播ID(溯源) |
| spread_platform | VARCHAR(32) | NOT NULL | 传播平台 |
| spread_time | DATETIME | NOT NULL | 传播时间 |
| spread_depth | INT | DEFAULT 1 | 传播深度/层级 |
| spread_scope | INT | DEFAULT 0 | 传播范围/影响人数 |
| spread_velocity | DECIMAL(10,2) | NULL | 传播速度(人/小时) |
| geographic_info | VARCHAR(255) | NULL | 地域信息 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

---

### 2.3 合规检查模块

#### 表 2.3.1: 合规检查项表 (risk_compliance_item)
| 字段名 | 字段类型 | 约束 | 说明 |
|--------|----------|------|------|
| item_id | VARCHAR(32) | PK, NOT NULL | 检查项ID |
| item_code | VARCHAR(32) | UK, NOT NULL | 检查项编码 |
| item_name | VARCHAR(128) | NOT NULL | 检查项名称 |
| item_category | TINYINT | NOT NULL | 检查类别: 1-适当性, 2-反洗钱, 3-信息披露, 4-交易行为, 5-其他 |
| item_description | VARCHAR(500) | NULL | 检查项描述 |
| check_rules | TEXT | NULL | 检查规则(JSON) |
| risk_level | TINYINT | DEFAULT 2 | 风险等级: 1-高, 2-中, 3-低 |
| check_frequency | VARCHAR(20) | DEFAULT 'daily' | 检查频率: daily/weekly/monthly/quarterly |
| is_active | TINYINT | DEFAULT 1 | 是否启用 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

#### 表 2.3.2: 合规检查记录表 (risk_compliance_check)
| 字段名 | 字段类型 | 约束 | 说明 |
|--------|----------|------|------|
| check_id | VARCHAR(32) | PK, NOT NULL | 检查记录ID |
| item_id | VARCHAR(32) | FK, NOT NULL | 检查项ID |
| customer_id | VARCHAR(32) | FK, NULL | 客户ID(可选) |
| product_code | VARCHAR(32) | NULL | 产品代码(可选) |
| check_date | DATE | NOT NULL | 检查日期 |
| check_period_start | DATE | NULL | 检查期间开始 |
| check_period_end | DATE | NULL | 检查期间结束 |
| check_result | TINYINT | NOT NULL | 检查结果: 1-通过, 2-不通过, 3-异常, 4-需关注 |
| check_details | TEXT | NULL | 检查详情(JSON) |
| issues_found | TEXT | NULL | 发现问题描述 |
| issue_count | INT | DEFAULT 0 | 问题数量 |
| checker_id | VARCHAR(32) | NOT NULL | 检查人ID |
| checker_name | VARCHAR(64) | NOT NULL | 检查人姓名 |
| check_method | TINYINT | NOT NULL | 检查方式: 1-自动, 2-人工, 3-混合 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

#### 表 2.3.3: 整改跟踪记录表 (risk_rectify_track)
| 字段名 | 字段类型 | 约束 | 说明 |
|--------|----------|------|------|
| track_id | VARCHAR(32) | PK, NOT NULL | 跟踪记录ID |
| check_id | VARCHAR(32) | FK, NOT NULL | 关联检查记录ID |
| issue_type | TINYINT | NOT NULL | 问题类型 |
| issue_desc | VARCHAR(500) | NOT NULL | 问题描述 |
| rectify_measure | VARCHAR(500) | NULL | 整改措施 |
| responsible_person | VARCHAR(32) | NOT NULL | 责任人ID |
| responsible_dept | VARCHAR(64) | NULL | 责任部门 |
| deadline | DATE | NOT NULL | 整改期限 |
| rectify_status | TINYINT | DEFAULT 1 | 整改状态: 1-未开始, 2-进行中, 3-待验收, 4-已完成, 5-已延期 |
| rectify_progress | INT | DEFAULT 0 | 整改进度(%) |
| actual_complete_date | DATE | NULL | 实际完成日期 |
| verify_result | TINYINT | NULL | 验收结果: 1-通过, 2-不通过 |
| verifier_id | VARCHAR(32) | NULL | 验收人ID |
| verified_at | DATETIME | NULL | 验收时间 |
| remark | VARCHAR(500) | NULL | 备注 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

#### 表 2.3.4: 合规检查模板表 (risk_compliance_template)
| 字段名 | 字段类型 | 约束 | 说明 |
|--------|----------|------|------|
| template_id | VARCHAR(32) | PK, NOT NULL | 模板ID |
| template_name | VARCHAR(128) | NOT NULL | 模板名称 |
| template_type | TINYINT | NOT NULL | 模板类型: 1-日常, 2-专项, 3-应急 |
| item_list | TEXT | NOT NULL | 包含检查项ID列表(JSON数组) |
| description | VARCHAR(500) | NULL | 模板描述 |
| is_active | TINYINT | DEFAULT 1 | 是否启用 |
| created_by | VARCHAR(32) | NOT NULL | 创建人 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

---

## 3. 风险计算模型

### 3.1 集中度风险计算模型

#### 3.1.1 客户持仓集中度计算

```
单一产品集中度 = 单一产品市值 / 客户总资产 × 100%

产品类别集中度 = Σ(该类别产品市值) / 客户总资产 × 100%

行业集中度 = Σ(该行业产品市值) / 客户总资产 × 100%
```

#### 3.1.2 集中度风险评分模型

```python
def calculate_concentration_risk_score(position_ratio, threshold_ratio):
    """
    集中度风险评分计算
    分数范围: 0-100, 分数越高风险越大
    """
    
    # 基础风险分 (0-40分)
    base_score = min(40, (position_ratio / threshold_ratio) * 20)
    
    # 超限倍数风险分 (0-30分)
    if position_ratio > threshold_ratio:
        exceed_multiple = position_ratio / threshold_ratio
        exceed_score = min(30, (exceed_multiple - 1) * 15)
    else:
        exceed_score = 0
    
    # 持仓规模风险分 (0-30分)
    position_scale_score = min(30, position_ratio * 30)
    
    total_score = base_score + exceed_score + position_scale_score
    return min(100, total_score)
```

#### 3.1.3 风险等级判定

| 风险得分 | 风险等级 | 预警级别 | 处理时限 |
|----------|----------|----------|----------|
| 0-30 | 低风险 | 无需预警 | - |
| 31-50 | 中低风险 | 三级预警(蓝色) | 3个工作日 |
| 51-70 | 中风险 | 二级预警(黄色) | 1个工作日 |
| 71-90 | 高风险 | 二级预警(橙色) | 4小时 |
| 91-100 | 极高风险 | 一级预警(红色) | 立即处理 |

---

### 3.2 舆情风险计算模型

#### 3.2.1 情感分析评分

```
情感得分 = 基础情感分 × 置信度 × 权重系数

其中:
- 基础情感分: [-1, 1]区间, -1为极度负面, 1为极度正面
- 置信度: 模型输出的置信概率 [0, 1]
- 权重系数: 根据数据源可信度设置

情感标签判定:
- 负面: 情感得分 < -0.3
- 中性: -0.3 ≤ 情感得分 ≤ 0.3  
- 正面: 情感得分 > 0.3
```

#### 3.2.2 舆情热度指数计算

```python
def calculate_heat_index(view_count, share_count, comment_count, time_decay_factor):
    """
    舆情热度指数计算
    """
    
    # 基础热度 (加权求和)
    base_heat = view_count * 0.3 + share_count * 0.5 + comment_count * 0.2
    
    # 时间衰减因子 (越新的舆情权重越高)
    # time_decay_factor = e^(-λ×Δt), λ为衰减系数, Δt为时间差(小时)
    
    heat_index = base_heat * time_decay_factor
    
    return heat_index
```

#### 3.2.3 舆情风险综合评分

```python
def calculate_sentiment_risk_score(sentiment_score, heat_index, spread_velocity, reliability):
    """
    舆情风险综合评分
    分数范围: 0-100
    """
    
    # 情感风险分 (0-40分) - 负面情感分数越高
    if sentiment_score < 0:
        sentiment_risk = abs(sentiment_score) * 40 * reliability
    else:
        sentiment_risk = 0
    
    # 热度风险分 (0-30分) - 热度越高风险越大
    heat_normalized = min(heat_index / 10000, 1.0)  # 归一化
    heat_risk = heat_normalized * 30
    
    # 传播风险分 (0-30分) - 传播速度越快风险越大
    if spread_velocity:
        spread_normalized = min(spread_velocity / 1000, 1.0)
        spread_risk = spread_normalized * 30
    else:
        spread_risk = 0
    
    total_risk = sentiment_risk + heat_risk + spread_risk
    return min(100, total_risk)
```

#### 3.2.4 舆情趋势预警判定

```python
def detect_sentiment_trend_warning(current_avg, previous_avg, volatility, mention_count):
    """
    舆情趋势预警检测
    """
    
    # 情感下降预警
    sentiment_drop = previous_avg - current_avg
    
    if sentiment_drop > 0.5 and current_avg < -0.5:
        return 'LEVEL_1'  # 一级预警: 情感急剧恶化
    elif sentiment_drop > 0.3 and current_avg < -0.3:
        return 'LEVEL_2'  # 二级预警: 情感明显恶化
    elif volatility > 0.4 and mention_count > 100:
        return 'LEVEL_3'  # 三级预警: 波动较大且提及增多
    
    return None
```

---

### 3.3 合规检查风险计算模型

#### 3.3.1 单项检查风险评分

```
单项风险分 = 基础风险分 × 严重系数 × 影响范围系数

其中:
- 基础风险分: 根据检查项预设风险等级确定 (高=30, 中=20, 低=10)
- 严重系数: 根据具体问题严重程度 (轻微=1, 一般=1.5, 严重=2, 极严重=3)
- 影响范围系数: 根据涉及客户/资金规模 (单个=1, 多个=1.5, 全部=2)
```

#### 3.3.2 客户合规风险综合评分

```python
def calculate_compliance_risk_score(check_results, weights=None):
    """
    客户合规风险综合评分
    check_results: [{item_id, result, severity, scope}, ...]
    """
    
    if weights is None:
        weights = {
            'anti_money_laundering': 0.3,  # 反洗钱权重
            'suitability': 0.25,           # 适当性权重
            'disclosure': 0.2,             # 信息披露权重
            'trading_behavior': 0.15,      # 交易行为权重
            'other': 0.1                   # 其他权重
        }
    
    total_score = 0
    category_scores = {}
    
    for result in check_results:
        # 单项风险计算
        base_score = get_base_score_by_risk_level(result['risk_level'])
        severity_factor = get_severity_factor(result['severity'])
        scope_factor = get_scope_factor(result['scope'])
        
        item_score = base_score * severity_factor * scope_factor
        
        # 按类别累加
        category = result['item_category']
        if category not in category_scores:
            category_scores[category] = []
        category_scores[category].append(item_score)
    
    # 加权求和
    for category, scores in category_scores.items():
        avg_score = sum(scores) / len(scores) if scores else 0
        weight = weights.get(category, 0.1)
        total_score += avg_score * weight
    
    return min(100, total_score)
```

#### 3.3.3 整改逾期风险计算

```
整改逾期风险分 = 基础分 × 逾期天数系数 × 问题严重系数

逾期天数系数:
- 1-3天: 1.0
- 4-7天: 1.5
- 8-15天: 2.0
- 16-30天: 3.0
- >30天: 5.0

问题严重系数:
- 一般问题: 1.0
- 重要问题: 2.0
- 重大问题: 5.0
```

---

## 4. 预警规则定义

### 4.1 集中度风险预警规则

#### 4.1.1 阈值触发规则

| 规则编号 | 规则名称 | 触发条件 | 预警级别 | 通知方式 | 响应时限 |
|----------|----------|----------|----------|----------|----------|
| CONC-001 | 单产品超限预警 | 单一产品持仓占比 > 30% | 三级 | 系统消息 | 3日 |
| CONC-002 | 单产品严重超限 | 单一产品持仓占比 > 50% | 二级 | 系统消息+短信 | 1日 |
| CONC-003 | 单产品极度过剩 | 单一产品持仓占比 > 70% | 一级 | 系统消息+短信+电话 | 立即 |
| CONC-004 | 类别集中度超限 | 同类产品持仓占比 > 60% | 三级 | 系统消息 | 3日 |
| CONC-005 | 类别集中度严重 | 同类产品持仓占比 > 80% | 二级 | 系统消息+短信 | 1日 |
| CONC-006 | 单日新增超限 | 单日新增持仓导致超限 | 二级 | 系统消息+短信 | 1日 |
| CONC-007 | 连续超限预警 | 连续3个交易日超限 | 一级 | 系统消息+短信+电话 | 立即 |

#### 4.1.2 动态阈值规则

```python
# 动态阈值调整规则
def get_dynamic_threshold(customer_risk_level, market_volatility):
    """
    根据客户风险等级和市场波动率动态调整阈值
    """
    base_thresholds = {
        'level_1': 0.25,  # 保守型客户
        'level_2': 0.30,
        'level_3': 0.35,
        'level_4': 0.40,
        'level_5': 0.50   # 激进型客户
    }
    
    # 市场波动率调整
    volatility_adjustment = {
        'low': 1.1,      # 波动率低, 放宽阈值
        'normal': 1.0,
        'high': 0.9,     # 波动率高, 收紧阈值
        'extreme': 0.8
    }
    
    base = base_thresholds.get(customer_risk_level, 0.35)
    adj = volatility_adjustment.get(market_volatility, 1.0)
    
    return base * adj
```

---

### 4.2 舆情风险预警规则

#### 4.2.1 情感分析预警规则

| 规则编号 | 规则名称 | 触发条件 | 预警级别 | 通知方式 | 响应时限 |
|----------|----------|----------|----------|----------|----------|
| SENT-001 | 负面舆情监测 | 情感分 < -0.3 且 热度 > 100 | 三级 | 系统消息 | 4小时 |
| SENT-002 | 严重负面舆情 | 情感分 < -0.6 且 热度 > 500 | 二级 | 系统消息+短信 | 1小时 |
| SENT-003 | 极负面舆情爆发 | 情感分 < -0.8 且 热度 > 1000 | 一级 | 系统消息+短信+电话 | 15分钟 |
| SENT-004 | 负面情感激增 | 单日负面情感数量增长 > 100% | 二级 | 系统消息+短信 | 1小时 |
| SENT-005 | 传播速度异常 | 传播速度 > 1000人/小时 | 二级 | 系统消息+短信 | 1小时 |
| SENT-006 | 多平台传播 | 同时在3个以上平台传播 | 三级 | 系统消息 | 4小时 |
| SENT-007 | 权威媒体关注 | 权威媒体发布负面舆情 | 一级 | 系统消息+短信+电话 | 15分钟 |

#### 4.2.2 趋势预警规则

```python
# 舆情趋势预警规则
sentiment_trend_rules = [
    {
        'rule_id': 'SENT-TREND-001',
        'name': '情感趋势恶化预警',
        'condition': {
            'sentiment_drop_3d': '> 0.3',      # 3日情感下降 > 0.3
            'current_sentiment': '< -0.3',      # 当前情感 < -0.3
        },
        'level': 2,
        'notify': ['system', 'sms']
    },
    {
        'rule_id': 'SENT-TREND-002',
        'name': '负面舆情持续积累',
        'condition': {
            'consecutive_negative_days': '>= 3',  # 连续3日负面
            'total_mentions': '> 50',             # 总提及数 > 50
        },
        'level': 2,
        'notify': ['system', 'sms']
    },
    {
        'rule_id': 'SENT-TREND-003',
        'name': '舆情波动异常',
        'condition': {
            'sentiment_volatility': '> 0.5',      # 情感波动率 > 0.5
            'heat_acceleration': '> 200%',        # 热度增速 > 200%
        },
        'level': 1,
        'notify': ['system', 'sms', 'call']
    }
]
```

#### 4.2.3 关键词触发规则

| 规则编号 | 触发关键词 | 匹配方式 | 预警级别 | 说明 |
|----------|------------|----------|----------|------|
| KEY-001 | 跑路/暴雷/诈骗/传销 | 精确/模糊 | 一级 | 涉及资金安全 |
| KEY-002 | 亏损严重/血本无归 | 模糊匹配 | 二级 | 客户投诉类 |
| KEY-003 | 监管处罚/立案调查 | 模糊匹配 | 一级 | 监管风险 |
| KEY-004 | 高管离职/人事变动 | 模糊匹配 | 三级 | 经营风险 |
| KEY-005 | 产品延期/兑付困难 | 模糊匹配 | 二级 | 流动性风险 |
| KEY-006 | 客户姓名+投诉/维权 | 组合匹配 | 二级 | 客户维权 |

---

### 4.3 合规检查预警规则

#### 4.3.1 检查结果预警规则

| 规则编号 | 规则名称 | 触发条件 | 预警级别 | 通知方式 | 响应时限 |
|----------|----------|----------|----------|----------|----------|
| COMP-001 | 检查不通过 | 检查结果 = 不通过 | 三级 | 系统消息 | 3日 |
| COMP-002 | 检查异常 | 检查结果 = 异常 | 二级 | 系统消息+短信 | 1日 |
| COMP-003 | 重大问题发现 | 发现重大级别问题 | 一级 | 系统消息+短信+电话 | 立即 |
| COMP-004 | 批量检查异常 | 同一批次异常率 > 20% | 二级 | 系统消息+短信 | 1日 |
| COMP-005 | 高频问题预警 | 同一问题7日内重复出现 | 二级 | 系统消息+短信 | 1日 |
| COMP-006 | 反洗钱异常 | AML检查异常 | 一级 | 系统消息+短信+电话 | 立即 |
| COMP-007 | 适当性不匹配 | 适当性检查发现不匹配 | 二级 | 系统消息+短信 | 1日 |

#### 4.3.2 整改跟踪预警规则

| 规则编号 | 规则名称 | 触发条件 | 预警级别 | 通知方式 | 响应时限 |
|----------|----------|----------|----------|----------|----------|
| RECT-001 | 整改到期提醒 | 距到期日 = 3日 | 三级 | 系统消息 | - |
| RECT-002 | 整改临期预警 | 距到期日 = 1日 | 二级 | 系统消息+短信 | - |
| RECT-003 | 整改逾期 | 当前日期 > 整改期限 | 一级 | 系统消息+短信+邮件 | 立即 |
| RECT-004 | 整改延期 | 申请延期次数 > 1次 | 二级 | 系统消息+短信 | - |
| RECT-005 | 整改进度滞后 | 进度 < 预期进度 × 0.7 | 三级 | 系统消息 | - |
| RECT-006 | 验收不通过 | 整改验收不通过 | 二级 | 系统消息+短信 | 3日 |
| RECT-007 | 长期逾期 | 逾期 > 30日 | 一级 | 系统消息+短信+邮件 | 立即 |

#### 4.3.3 整改规则定义

```python
# 整改期限计算规则
def calculate_rectify_deadline(issue_type, severity, issue_count):
    """
    根据问题类型、严重程度和数量计算整改期限
    """
    
    # 基础期限 (工作日)
    base_deadlines = {
        'anti_money_laundering': {'critical': 3, 'major': 5, 'normal': 10},
        'suitability': {'critical': 5, 'major': 10, 'normal': 15},
        'disclosure': {'critical': 2, 'major': 5, 'normal': 10},
        'trading_behavior': {'critical': 3, 'major': 7, 'normal': 10},
        'other': {'critical': 5, 'major': 10, 'normal': 20}
    }
    
    # 数量调整系数
    quantity_factor = {
        (0, 1): 1.0,
        (2, 5): 1.2,
        (6, 10): 1.5,
        (11, float('inf')): 2.0
    }
    
    base = base_deadlines.get(issue_type, {}).get(severity, 10)
    factor = 1.0
    for (min_cnt, max_cnt), f in quantity_factor.items():
        if min_cnt <= issue_count <= max_cnt:
            factor = f
            break
    
    return int(base * factor)
```

---

### 4.4 预警升级与降级规则

#### 4.4.1 预警升级规则

```python
alert_escalation_rules = {
    'level_3_to_2': {
        'conditions': [
            '未在时限内处理',
            '同类预警24小时内重复触发 >= 3次',
            '关联风险同时触发'
        ],
        'action': '升级至二级预警，增加通知方式'
    },
    'level_2_to_1': {
        'conditions': [
            '未在时限内处理',
            '风险评分上升 > 20分',
            '引发次生风险'
        ],
        'action': '升级至一级预警，启动应急响应'
    }
}
```

#### 4.4.2 预警降级/解除规则

| 规则 | 适用场景 | 触发条件 | 操作 |
|------|----------|----------|------|
| 主动降级 | 风险已缓解 | 连续3日风险评分 < 阈值 × 0.8 | 降一级 |
| 主动解除 | 风险已消除 | 风险根因已解决且验证通过 | 解除预警 |
| 自动解除 | 时效到期 | 预警触发后7日未升级且风险下降 | 系统提醒人工确认 |
| 误报解除 | 系统误判 | 人工核实确认为误报 | 标记误报并解除 |

---

### 4.5 预警通知配置

#### 4.5.1 通知渠道配置

```yaml
notification_channels:
  system_message:
    enabled: true
    priority: high
    target: [risk_manager, compliance_officer, customer_manager]
    
  sms:
    enabled: true
    priority: critical
    template_id: "RISK_ALERT_001"
    target: [customer_manager_mobile, risk_manager_mobile]
    
  email:
    enabled: true
    priority: high
    template_id: "RISK_ALERT_EMAIL_001"
    target: [risk_dept_email]
    
  phone_call:
    enabled: true
    priority: emergency
    target: [risk_manager_phone, on_duty_phone]
    trigger_condition: "level_1 OR continuous_level_2"
```

#### 4.5.2 通知频率控制

```python
# 同类型预警频率控制
def should_send_notification(alert_type, last_sent_time, alert_level):
    """
    判断是否应该发送通知 (防止消息轰炸)
    """
    cooldown_periods = {
        1: timedelta(minutes=15),   # 一级预警: 15分钟冷却
        2: timedelta(hours=1),      # 二级预警: 1小时冷却
        3: timedelta(hours=4)       # 三级预警: 4小时冷却
    }
    
    if last_sent_time is None:
        return True
    
    cooldown = cooldown_periods.get(alert_level, timedelta(hours=1))
    return datetime.now() - last_sent_time >= cooldown
```

---

## 5. 附录

### 5.1 索引设计建议

```sql
-- 客户信息表索引
CREATE INDEX idx_customer_type ON risk_customer(customer_type);
CREATE INDEX idx_customer_risk_level ON risk_customer(risk_level);

-- 持仓明细表索引
CREATE INDEX idx_position_customer ON risk_position(customer_id);
CREATE INDEX idx_position_date ON risk_position(position_date);
CREATE INDEX idx_position_product ON risk_position(product_code);

-- 集中度预警记录表索引
CREATE INDEX idx_alert_customer ON risk_concentration_alert(customer_id);
CREATE INDEX idx_alert_date ON risk_concentration_alert(alert_date);
CREATE INDEX idx_alert_status ON risk_concentration_alert(alert_status);
CREATE INDEX idx_alert_level ON risk_concentration_alert(warning_level);

-- 舆情分析表索引
CREATE INDEX idx_sentiment_source ON risk_sentiment_analysis(source_id);
CREATE INDEX idx_sentiment_time ON risk_sentiment_analysis(publish_time);
CREATE INDEX idx_sentiment_label ON risk_sentiment_analysis(sentiment_label);
CREATE INDEX idx_sentiment_products ON risk_sentiment_analysis(related_products(100));

-- 合规检查记录表索引
CREATE INDEX idx_check_item ON risk_compliance_check(item_id);
CREATE INDEX idx_check_customer ON risk_compliance_check(customer_id);
CREATE INDEX idx_check_date ON risk_compliance_check(check_date);
CREATE INDEX idx_check_result ON risk_compliance_check(check_result);

-- 整改跟踪记录表索引
CREATE INDEX idx_track_check ON risk_rectify_track(check_id);
CREATE INDEX idx_track_status ON risk_rectify_track(rectify_status);
CREATE INDEX idx_track_deadline ON risk_rectify_track(deadline);
```

### 5.2 数据归档策略

| 数据表 | 归档周期 | 保留时长 | 归档方式 |
|--------|----------|----------|----------|
| 持仓明细表 | 每日 | 2年 | 分区归档 |
| 集中度预警记录 | 每月 | 5年 | 分区归档 |
| 舆情分析表 | 每周 | 1年(全量) + 3年(摘要) | 冷热分离 |
| 舆情趋势分析 | 每月 | 3年 | 压缩归档 |
| 合规检查记录 | 每季度 | 10年 | 分区归档 |
| 整改跟踪记录 | 每季度 | 10年 | 分区归档 |

---

## 文档变更记录

| 版本 | 日期 | 修改人 | 修改内容 |
|------|------|--------|----------|
| v1.0 | 2026-03-07 | - | 初始版本，完成三大风险模块的数据建模设计 |

---

*文档结束*

---

# 业务支持中心 - 业绩看板模块数据建模方案

## 文档信息

| 项目 | 内容 |
|------|------|
| 模块名称 | 业绩看板模块 |
| 所属系统 | 业务支持中心 |
| 版本 | V1.0 |
| 创建日期 | 2026-03-07 |

---

## 一、实体关系图（ER图文字描述）

### 1.1 核心实体概览

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   dim_customer  │     │  dim_date       │     │  dim_target     │
│   【客户维度】   │     │  【日期维度】    │     │  【目标维度】    │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         │                       │                       │
         └───────────┬───────────┴───────────┬───────────┘
                     │                       │
                     ▼                       ▼
         ┌─────────────────────────────────────────┐
         │         fact_business_performance        │
         │          【业务业绩事实表】               │
         └─────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│  agg_monthly    │     │  agg_quarterly  │
│ 【月度聚合表】   │     │ 【季度聚合表】   │
└─────────────────┘     └─────────────────┘
```

### 1.2 实体关系详细说明

#### 维度表（Dimension Tables）

| 维度表 | 主键 | 说明 |
|--------|------|------|
| `dim_customer` | customer_id | 客户维度表，存储客户基础信息 |
| `dim_date` | date_key | 日期维度表，支持时间序列分析 |
| `dim_target` | target_id | 目标维度表，存储各类业绩目标 |

#### 事实表（Fact Tables）

| 事实表 | 外键关系 | 说明 |
|--------|----------|------|
| `fact_business_performance` | date_key, customer_id, target_id | 业务业绩明细事实表 |
| `agg_monthly_performance` | date_key（月级别）, customer_id | 月度聚合统计表 |
| `agg_quarterly_performance` | date_key（季度级别）, customer_id | 季度聚合统计表 |

### 1.3 关系定义

```
dim_customer (1) ────< (N) fact_business_performance
      │                           │
      │                           │
      │                     (N) >──┴──< (N)
      │                         dim_date
      │                           │
      │                     (N) >─┴──< (1)
      │                       dim_target
      │
      └── (1) ────< (N) agg_monthly_performance
      │
      └── (1) ────< (N) agg_quarterly_performance
```

**关系说明：**
- 一个客户可对应多条业绩记录（1:N）
- 一个日期可对应多条业绩记录（1:N）
- 一个目标可对应多条业绩记录（1:N）
- 客户与聚合表为1:N关系
- 日期维度通过date_key关联，支持不同粒度（日/月/季/年）

---

## 二、数据表结构设计

### 2.1 维度表

#### 2.1.1 客户维度表 (dim_customer)

```sql
CREATE TABLE dim_customer (
    -- 主键
    customer_id         VARCHAR(32)     PRIMARY KEY COMMENT '客户唯一标识',
    
    -- 客户基础信息
    customer_code       VARCHAR(50)     NOT NULL COMMENT '客户编码',
    customer_name       VARCHAR(200)    NOT NULL COMMENT '客户名称',
    customer_short_name VARCHAR(100)    COMMENT '客户简称',
    
    -- 客户分类
    customer_type       VARCHAR(20)     COMMENT '客户类型（企业/个人/政府）',
    industry_code       VARCHAR(20)     COMMENT '行业编码',
    industry_name       VARCHAR(100)    COMMENT '行业名称',
    region_code         VARCHAR(20)     COMMENT '区域编码',
    region_name         VARCHAR(100)    COMMENT '区域名称',
    
    -- 客户等级
    customer_level      VARCHAR(10)     COMMENT '客户等级（A/B/C/D）',
    is_key_customer     TINYINT(1)      DEFAULT 0 COMMENT '是否重点客户（1是0否）',
    
    -- 生命周期
    first_deal_date     DATE            COMMENT '首次成交日期',
    status              VARCHAR(20)     DEFAULT 'active' COMMENT '状态（active/inactive）',
    
    -- 元数据
    create_time         DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time         DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 约束
    UNIQUE KEY uk_customer_code (customer_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='客户维度表';
```

#### 2.1.2 日期维度表 (dim_date)

```sql
CREATE TABLE dim_date (
    -- 主键
    date_key            INT             PRIMARY KEY COMMENT '日期键（格式：YYYYMMDD）',
    
    -- 基础日期
    full_date           DATE            NOT NULL COMMENT '完整日期',
    
    -- 年份维度
    year_num            INT             NOT NULL COMMENT '年份',
    year_name           VARCHAR(10)     NOT NULL COMMENT '年份名称（如：2026年）',
    
    -- 季度维度
    quarter_num         TINYINT         NOT NULL COMMENT '季度（1-4）',
    quarter_name        VARCHAR(10)     NOT NULL COMMENT '季度名称（如：Q1）',
    quarter_key         INT             NOT NULL COMMENT '季度键（格式：YYYYQ）',
    year_quarter        VARCHAR(10)     NOT NULL COMMENT '年季度（如：2026Q1）',
    
    -- 月份维度
    month_num           TINYINT         NOT NULL COMMENT '月份（1-12）',
    month_name          VARCHAR(10)     NOT NULL COMMENT '月份名称（如：1月）',
    month_key           INT             NOT NULL COMMENT '月份键（格式：YYYYMM）',
    year_month          VARCHAR(10)     NOT NULL COMMENT '年月（如：2026-01）',
    
    -- 周维度
    week_num            TINYINT         NOT NULL COMMENT '周数（1-53）',
    week_key            INT             COMMENT '周键（格式：YYYYWNN）',
    
    -- 日维度
    day_num             TINYINT         NOT NULL COMMENT '日（1-31）',
    day_of_week         TINYINT         NOT NULL COMMENT '星期几（1-7，周一为1）',
    day_name            VARCHAR(10)     NOT NULL COMMENT '星期名称（如：周一）',
    
    -- 业务标识
    is_workday          TINYINT(1)      DEFAULT 1 COMMENT '是否工作日（1是0否）',
    is_month_end        TINYINT(1)      DEFAULT 0 COMMENT '是否月末（1是0否）',
    is_quarter_end      TINYINT(1)      DEFAULT 0 COMMENT '是否季末（1是0否）',
    is_year_end         TINYINT(1)      DEFAULT 0 COMMENT '是否年末（1是0否）',
    
    -- 同比环比
    same_date_last_year INT             COMMENT '去年同期日期键',
    
    -- 索引
    UNIQUE KEY uk_full_date (full_date),
    INDEX idx_year_month (year_num, month_num),
    INDEX idx_quarter (year_num, quarter_num)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='日期维度表';
```

#### 2.1.3 目标维度表 (dim_target)

```sql
CREATE TABLE dim_target (
    -- 主键
    target_id           VARCHAR(32)     PRIMARY KEY COMMENT '目标唯一标识',
    
    -- 目标定义
    target_type         VARCHAR(30)     NOT NULL COMMENT '目标类型（revenue_income/revenue_progress/customer_new）',
    target_name         VARCHAR(100)    NOT NULL COMMENT '目标名称',
    target_desc         VARCHAR(500)    COMMENT '目标描述',
    
    -- 目标周期
    target_year         INT             NOT NULL COMMENT '目标年度',
    target_period_type  VARCHAR(10)     NOT NULL COMMENT '周期类型（year/quarter/month）',
    target_period       VARCHAR(20)     NOT NULL COMMENT '目标周期（如：2026、2026Q1、202601）',
    
    -- 目标数值
    target_value        DECIMAL(18,2)   NOT NULL COMMENT '目标值',
    target_unit         VARCHAR(10)     DEFAULT '元' COMMENT '目标单位',
    warning_threshold   DECIMAL(5,2)    DEFAULT 0.80 COMMENT '预警阈值（如0.8表示80%预警）',
    
    -- 责任归属
    owner_dept          VARCHAR(50)     COMMENT '责任部门',
    owner_id            VARCHAR(32)     COMMENT '责任人ID',
    owner_name          VARCHAR(50)     COMMENT '责任人姓名',
    
    -- 状态
    status              VARCHAR(20)     DEFAULT 'active' COMMENT '状态（active/archived）',
    
    -- 元数据
    create_time         DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time         DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='目标维度表';
```

### 2.2 事实表

#### 2.2.1 业务业绩明细事实表 (fact_business_performance)

```sql
CREATE TABLE fact_business_performance (
    -- 主键
    performance_id      VARCHAR(32)     PRIMARY KEY COMMENT '业绩记录唯一标识',
    
    -- 维度外键
    date_key            INT             NOT NULL COMMENT '日期维度键',
    customer_id         VARCHAR(32)     NOT NULL COMMENT '客户维度键',
    
    -- 业务度量
    revenue_amount      DECIMAL(18,2)   DEFAULT 0 COMMENT '收入金额（元）',
    cost_amount         DECIMAL(18,2)   DEFAULT 0 COMMENT '成本金额（元）',
    profit_amount       DECIMAL(18,2)   DEFAULT 0 COMMENT '利润金额（元）',
    
    -- 客户相关
    is_new_customer     TINYINT(1)      DEFAULT 0 COMMENT '是否新客户（1是0否）',
    customer_deal_count INT             DEFAULT 0 COMMENT '客户成交次数',
    
    -- 业务分类
    business_type       VARCHAR(30)     COMMENT '业务类型',
    product_category    VARCHAR(50)     COMMENT '产品分类',
    
    -- 元数据
    create_time         DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    -- 索引
    INDEX idx_date_customer (date_key, customer_id),
    INDEX idx_customer_date (customer_id, date_key),
    INDEX idx_date_key (date_key),
    
    -- 外键约束
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='业务业绩明细事实表';
```

### 2.3 聚合表

#### 2.3.1 月度业绩聚合表 (agg_monthly_performance)

```sql
CREATE TABLE agg_monthly_performance (
    -- 主键
    agg_id              VARCHAR(32)     PRIMARY KEY COMMENT '聚合记录唯一标识',
    
    -- 维度键
    month_key           INT             NOT NULL COMMENT '月份键（YYYYMM）',
    customer_id         VARCHAR(32)     COMMENT '客户ID（NULL表示汇总）',
    
    -- 收入指标
    revenue_amount      DECIMAL(18,2)   DEFAULT 0 COMMENT '当月收入',
    revenue_ytd         DECIMAL(18,2)   DEFAULT 0 COMMENT '年度累计收入',
    revenue_yoy_growth  DECIMAL(8,4)    COMMENT '同比增长率',
    revenue_mom_growth  DECIMAL(8,4)    COMMENT '环比增长率',
    
    -- 客户指标
    customer_count      INT             DEFAULT 0 COMMENT '客户数',
    new_customer_count  INT             DEFAULT 0 COMMENT '新增客户数',
    active_customer_count INT           DEFAULT 0 COMMENT '活跃客户数',
    
    -- 目标相关
    revenue_target      DECIMAL(18,2)   DEFAULT 0 COMMENT '收入目标',
    target_progress     DECIMAL(5,2)    COMMENT '目标完成进度（%）',
    
    -- 排名
    revenue_rank        INT             COMMENT '收入排名',
    customer_growth_rank INT            COMMENT '客户增长排名',
    
    -- 元数据
    calc_time           DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '计算时间',
    
    -- 索引
    UNIQUE KEY uk_month_customer (month_key, customer_id),
    INDEX idx_month_key (month_key),
    INDEX idx_customer_id (customer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='月度业绩聚合表';
```

#### 2.3.2 季度业绩聚合表 (agg_quarterly_performance)

```sql
CREATE TABLE agg_quarterly_performance (
    -- 主键
    agg_id              VARCHAR(32)     PRIMARY KEY COMMENT '聚合记录唯一标识',
    
    -- 维度键
    quarter_key         INT             NOT NULL COMMENT '季度键（YYYYQ）',
    customer_id         VARCHAR(32)     COMMENT '客户ID（NULL表示汇总）',
    
    -- 收入指标
    revenue_amount      DECIMAL(18,2)   DEFAULT 0 COMMENT '当季收入',
    revenue_ytd         DECIMAL(18,2)   DEFAULT 0 COMMENT '年度累计收入',
    revenue_yoy_growth  DECIMAL(8,4)    COMMENT '同比增长率',
    revenue_qoq_growth  DECIMAL(8,4)    COMMENT '环比增长率',
    
    -- 客户指标
    customer_count      INT             DEFAULT 0 COMMENT '客户数',
    new_customer_count  INT             DEFAULT 0 COMMENT '新增客户数',
    
    -- 目标相关
    revenue_target      DECIMAL(18,2)   DEFAULT 0 COMMENT '收入目标',
    target_progress     DECIMAL(5,2)    COMMENT '目标完成进度（%）',
    
    -- 对比
    prev_quarter_amount DECIMAL(18,2)   COMMENT '上季度收入',
    same_quarter_last_year DECIMAL(18,2) COMMENT '去年同期收入',
    
    -- 元数据
    calc_time           DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '计算时间',
    
    -- 索引
    UNIQUE KEY uk_quarter_customer (quarter_key, customer_id),
    INDEX idx_quarter_key (quarter_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='季度业绩聚合表';
```

#### 2.3.3 客户业绩排名表 (agg_customer_ranking)

```sql
CREATE TABLE agg_customer_ranking (
    -- 主键
    rank_id             VARCHAR(32)     PRIMARY KEY COMMENT '排名记录唯一标识',
    
    -- 维度键
    period_key          INT             NOT NULL COMMENT '周期键（YYYYMM或YYYYQ）',
    period_type         VARCHAR(10)     NOT NULL COMMENT '周期类型（month/quarter）',
    customer_id         VARCHAR(32)     NOT NULL COMMENT '客户ID',
    
    -- 收入排名
    revenue_rank        INT             NOT NULL COMMENT '收入排名',
    revenue_amount      DECIMAL(18,2)   DEFAULT 0 COMMENT '收入金额',
    revenue_share       DECIMAL(5,2)    COMMENT '收入占比（%）',
    revenue_contrib     VARCHAR(10)     COMMENT '贡献等级（TOP3/MIDDLE/TAIL）',
    
    -- 客户增长排名
    customer_growth_rank INT            COMMENT '客户增长排名',
    new_deal_count      INT             DEFAULT 0 COMMENT '新成交次数',
    
    -- 元数据
    calc_time           DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '计算时间',
    
    -- 索引
    UNIQUE KEY uk_period_customer (period_key, period_type, customer_id),
    INDEX idx_period_rank (period_key, period_type, revenue_rank)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='客户业绩排名表';
```

---

## 三、指标计算逻辑

### 3.1 业务概览指标

| 指标名称 | 指标编码 | 计算逻辑 | 数据来源 |
|----------|----------|----------|----------|
| **收入数据** | revenue_total | SUM(revenue_amount) | fact_business_performance |
| **客户数量** | customer_count | COUNT(DISTINCT customer_id) | dim_customer WHERE status='active' |
| **同比增长** | revenue_yoy | (本期收入 - 同期收入) / 同期收入 × 100% | agg_monthly_performance.revenue_yoy_growth |

#### 3.1.1 计算示例

```sql
-- 收入数据（当前月）
SELECT 
    SUM(revenue_amount) AS revenue_total
FROM fact_business_performance fp
JOIN dim_date dd ON fp.date_key = dd.date_key
WHERE dd.year_month = '2026-02';
-- 结果示例：8,540,000 元

-- 客户数量（活跃客户）
SELECT COUNT(DISTINCT customer_id) AS customer_count
FROM dim_customer
WHERE status = 'active';
-- 结果示例：23 家

-- 同比增长率
SELECT 
    (curr.revenue_amount - prev.revenue_amount) / prev.revenue_amount * 100 AS yoy_growth
FROM (
    SELECT SUM(revenue_amount) AS revenue_amount
    FROM fact_business_performance fp
    JOIN dim_date dd ON fp.date_key = dd.date_key
    WHERE dd.year_month = '2026-02'
) curr,
(
    SELECT SUM(revenue_amount) AS revenue_amount
    FROM fact_business_performance fp
    JOIN dim_date dd ON fp.date_key = dd.date_key
    WHERE dd.year_month = '2025-02'
) prev;
-- 结果示例：+12%
```

### 3.2 业绩指标

| 指标名称 | 指标编码 | 计算逻辑 | 数据来源 |
|----------|----------|----------|----------|
| **收入目标进度** | revenue_progress | 累计收入 / 收入目标 × 100% | agg_monthly_performance |
| **新增客户目标** | customer_new_progress | 新增客户数 / 新增客户目标 × 100% | dim_customer + dim_target |

#### 3.2.1 计算示例

```sql
-- 收入目标进度
SELECT 
    ROUND(SUM(revenue_ytd) / SUM(revenue_target) * 100, 2) AS progress_pct
FROM agg_monthly_performance
WHERE month_key = 202602;
-- 结果示例：68%

-- 新增客户目标进度
SELECT 
    ROUND(
        (SELECT COUNT(*) FROM dim_customer 
         WHERE first_deal_date >= '2026-01-01' 
         AND first_deal_date <= '2026-02-28')
        / 
        (SELECT target_value FROM dim_target 
         WHERE target_type = 'customer_new' 
         AND target_year = 2026) * 100, 
    2) AS customer_new_progress;
-- 结果示例：50%
```

### 3.3 趋势分析指标

#### 3.3.1 月度趋势

```sql
-- 近12个月收入趋势
SELECT 
    dd.year_month,
    COALESCE(SUM(fp.revenue_amount), 0) AS revenue_amount,
    LAG(COALESCE(SUM(fp.revenue_amount), 0)) OVER (ORDER BY dd.month_key) AS prev_month_revenue,
    ROUND(
        (COALESCE(SUM(fp.revenue_amount), 0) - LAG(COALESCE(SUM(fp.revenue_amount), 0)) OVER (ORDER BY dd.month_key))
        / NULLIF(LAG(COALESCE(SUM(fp.revenue_amount), 0)) OVER (ORDER BY dd.month_key), 0) * 100,
        2
    ) AS mom_growth_rate
FROM dim_date dd
LEFT JOIN fact_business_performance fp ON dd.date_key = fp.date_key
WHERE dd.month_key BETWEEN 202503 AND 202602
GROUP BY dd.month_key, dd.year_month
ORDER BY dd.month_key;
```

#### 3.3.2 季度对比

```sql
-- 季度对比分析
SELECT 
    dd.year_quarter,
    SUM(fp.revenue_amount) AS revenue_amount,
    SUM(fp.revenue_amount) - LAG(SUM(fp.revenue_amount)) OVER (ORDER BY dd.quarter_key) AS qoq_diff,
    ROUND(
        (SUM(fp.revenue_amount) - LAG(SUM(fp.revenue_amount)) OVER (ORDER BY dd.quarter_key))
        / NULLIF(LAG(SUM(fp.revenue_amount)) OVER (ORDER BY dd.quarter_key), 0) * 100,
        2
    ) AS qoq_growth_rate
FROM fact_business_performance fp
JOIN dim_date dd ON fp.date_key = dd.date_key
WHERE dd.year_num = 2026
GROUP BY dd.quarter_key, dd.year_quarter
ORDER BY dd.quarter_key;
```

### 3.4 排行榜指标

#### 3.4.1 收入排行

```sql
-- TOP10 收入排行
SELECT 
    dc.customer_id,
    dc.customer_name,
    SUM(fp.revenue_amount) AS revenue_amount,
    RANK() OVER (ORDER BY SUM(fp.revenue_amount) DESC) AS revenue_rank,
    ROUND(SUM(fp.revenue_amount) * 100.0 / SUM(SUM(fp.revenue_amount)) OVER (), 2) AS revenue_share
FROM fact_business_performance fp
JOIN dim_customer dc ON fp.customer_id = dc.customer_id
JOIN dim_date dd ON fp.date_key = dd.date_key
WHERE dd.year_month = '2026-02'
GROUP BY dc.customer_id, dc.customer_name
ORDER BY revenue_amount DESC
LIMIT 10;
```

#### 3.4.2 客户增长排行

```sql
-- 客户增长排行（按新增交易次数）
SELECT 
    dc.customer_id,
    dc.customer_name,
    COUNT(DISTINCT fp.date_key) AS deal_count,
    SUM(fp.revenue_amount) AS revenue_amount,
    RANK() OVER (ORDER BY COUNT(DISTINCT fp.date_key) DESC, SUM(fp.revenue_amount) DESC) AS growth_rank
FROM fact_business_performance fp
JOIN dim_customer dc ON fp.customer_id = dc.customer_id
JOIN dim_date dd ON fp.date_key = dd.date_key
WHERE dd.year_month = '2026-02'
GROUP BY dc.customer_id, dc.customer_name
ORDER BY deal_count DESC, revenue_amount DESC
LIMIT 10;
```

### 3.5 业绩分析指标

#### 3.5.1 TOP3客户贡献

```sql
-- TOP3客户贡献分析
WITH customer_revenue AS (
    SELECT 
        dc.customer_id,
        dc.customer_name,
        SUM(fp.revenue_amount) AS revenue_amount
    FROM fact_business_performance fp
    JOIN dim_customer dc ON fp.customer_id = dc.customer_id
    JOIN dim_date dd ON fp.date_key = dd.date_key
    WHERE dd.year_month = '2026-02'
    GROUP BY dc.customer_id, dc.customer_name
),
total_revenue AS (
    SELECT SUM(revenue_amount) AS total FROM customer_revenue
)
SELECT 
    cr.customer_id,
    cr.customer_name,
    cr.revenue_amount,
    ROUND(cr.revenue_amount * 100.0 / tr.total, 2) AS revenue_share,
    'TOP3' AS contrib_level
FROM customer_revenue cr
CROSS JOIN total_revenue tr
ORDER BY cr.revenue_amount DESC
LIMIT 3;
```

#### 3.5.2 尾部客户分析

```sql
-- 尾部客户分析（收入排名后30%）
WITH customer_revenue AS (
    SELECT 
        dc.customer_id,
        dc.customer_name,
        SUM(fp.revenue_amount) AS revenue_amount,
        ROW_NUMBER() OVER (ORDER BY SUM(fp.revenue_amount) DESC) AS row_num,
        COUNT(*) OVER () AS total_count
    FROM fact_business_performance fp
    JOIN dim_customer dc ON fp.customer_id = dc.customer_id
    JOIN dim_date dd ON fp.date_key = dd.date_key
    WHERE dd.year_month = '2026-02'
    GROUP BY dc.customer_id, dc.customer_name
),
total_revenue AS (
    SELECT SUM(revenue_amount) AS total FROM customer_revenue
)
SELECT 
    cr.customer_id,
    cr.customer_name,
    cr.revenue_amount,
    ROUND(cr.revenue_amount * 100.0 / tr.total, 2) AS revenue_share,
    cr.row_num AS rank_num,
    'TAIL' AS contrib_level
FROM customer_revenue cr
CROSS JOIN total_revenue tr
WHERE cr.row_num > cr.total_count * 0.7  -- 后30%
ORDER BY cr.revenue_amount ASC;
```

---

## 四、分析模型定义

### 4.1 星型模型（Star Schema）

```
                    ┌─────────────────┐
                    │   dim_target    │
                    │   【目标维度】   │
                    └────────┬────────┘
                             │
                             │
┌─────────────────┐          │         ┌─────────────────┐
│   dim_customer  │◄─────────┼────────►│  dim_date       │
│   【客户维度】   │          │         │  【日期维度】    │
└────────┬────────┘          │         └────────┬────────┘
         │                   │                  │
         │                   │                  │
         │         ┌─────────┴─────────┐        │
         │         │                   │        │
         └────────►│ fact_business     │◄───────┘
                   │ _performance      │◄───────┐
                   │【业绩事实表】      │        │
                   └─────────┬─────────┘        │
                             │                  │
                             │                  │
                             ▼                  │
                   ┌─────────────────┐          │
                   │  agg_monthly    │◄─────────┘
                   │ _performance    │
                   │【月度聚合表】    │
                   └─────────────────┘
```

### 4.2 分析维度矩阵

| 分析主题 | 时间维度 | 客户维度 | 度量指标 |
|----------|----------|----------|----------|
| 业务概览 | 当前月 | 全体客户 | 收入总额、客户数、同比增长 |
| 业绩指标 | 年度累计 | 全体客户 | 目标进度、新增客户率 |
| 月度趋势 | 近12个月 | 全体客户 | 月度收入、环比增长率 |
| 季度对比 | 本季vs上季 | 全体客户 | 季度收入、同比增长率 |
| 收入排行 | 当前月 | TOP N客户 | 收入金额、占比 |
| 客户增长排行 | 当前月 | TOP N客户 | 成交次数、收入金额 |
| TOP3客户分析 | 当前月 | TOP3客户 | 收入金额、贡献占比 |
| 尾部客户分析 | 当前月 | 后30%客户 | 收入金额、风险标识 |

### 4.3 数据流架构

```
┌─────────────────────────────────────────────────────────────┐
│                        数据源层                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  CRM系统      │  │  财务系统     │  │  订单系统     │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
└─────────┼─────────────────┼─────────────────┼───────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────┐
│                        ETL处理层                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  数据清洗 → 数据转换 → 数据加载                          │ │
│  │  (Extract)  (Transform)  (Load)                         │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        数据仓库层                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  dim_customer │  │  dim_date    │  │  dim_target  │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │        fact_business_performance                       │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        聚合计算层                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ agg_monthly  │  │ agg_quarterly│  │ agg_customer │       │
│  │ _performance │  │ _performance │  │ _ranking     │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        应用展示层                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  业绩看板     │  │  数据报表     │  │  API服务      │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### 4.4 更新频率定义

| 数据表 | 更新类型 | 更新频率 | 数据延迟 |
|--------|----------|----------|----------|
| dim_customer | 增量更新 | 每日 | T+1 |
| dim_date | 预生成 | 每年初 | - |
| dim_target | 全量更新 | 目标调整时 | 实时 |
| fact_business_performance | 增量更新 | 每日 | T+1 |
| agg_monthly_performance | 增量计算 | 每日 | T+1 |
| agg_quarterly_performance | 增量计算 | 每日 | T+1 |
| agg_customer_ranking | 全量计算 | 每日 | T+1 |

### 4.5 数据质量校验规则

| 校验项目 | 校验规则 | 告警级别 |
|----------|----------|----------|
| 收入数据完整性 | 收入金额 >= 0 | 错误 |
| 客户ID有效性 | 客户ID必须在dim_customer中存在 | 错误 |
| 日期一致性 | 日期键必须符合dim_date定义 | 错误 |
| 同比增长合理性 | 同比增长率范围 [-50%, 200%] | 警告 |
| 目标进度合理性 | 目标进度范围 [0%, 150%] | 警告 |
| 排名连续性 | 排名必须连续无断号 | 警告 |

---

## 五、附录

### 5.1 术语表

| 术语 | 说明 |
|------|------|
| YTD | Year To Date，年度累计 |
| YoY | Year over Year，同比增长 |
| MoM | Month over Month，环比增长 |
| QoQ | Quarter over Quarter，环比增长 |
| T+1 | 数据延迟1天 |
| DIM | Dimension，维度表 |
| FACT | Fact，事实表 |
| AGG | Aggregate，聚合表 |

### 5.2 索引策略

为提高查询性能，建议在以下字段建立索引：

1. **事实表索引**：
   - 组合索引：`date_key + customer_id`
   - 单列索引：`date_key`, `customer_id`

2. **聚合表索引**：
   - 唯一索引：`month_key + customer_id`
   - 分区索引：按月份分区

3. **维度表索引**：
   - 主键索引：`customer_id`, `date_key`, `target_id`
   - 唯一索引：`customer_code`, `full_date`

---

**文档结束**

---

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


---

# 附录D：潜客挖掘数据模型（新增）

## D.1 潜客挖掘数据源表 (prospecting_data_sources)

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

## D.2 潜客挖掘结果表 (prospecting_results)

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

## D.3 挖掘规则配置表 (prospecting_rules)

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

## D.4 六大挖掘规则设计

### D.4.1 规模匹配规则（权重25%）

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

### D.4.2 策略匹配规则（权重25%）

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

### D.4.3 区域匹配规则（权重15%）

| 规则ID | 规则名称 | 条件 | 评分 |
|--------|----------|------|------|
| REGION_001 | 核心区域 | 注册地在北京/上海/深圳 | 15分 |
| REGION_002 | 重点区域 | 注册地在杭州/广州/成都/南京 | 12分 |
| REGION_003 | 一般区域 | 其他省会城市 | 8分 |
| REGION_004 | 就近服务 | 与当前客户经理同区域 | +5分（额外加分） |

### D.4.4 合规筛选规则（权重20%）

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

### D.4.5 活跃度评估规则（权重10%）

| 规则ID | 规则名称 | 条件 | 评分 |
|--------|----------|------|------|
| ACTIVITY_001 | 高活跃 | 近6个月新发产品≥3只 | 10分 |
| ACTIVITY_002 | 中活跃 | 近6个月新发产品1-2只 | 6分 |
| ACTIVITY_003 | 低活跃 | 近6个月无新发产品 | 2分 |
| ACTIVITY_004 | 沉睡唤醒 | 历史活跃但近1年无新发 | 5分（特殊标记） |

**数据源映射：**
- 朝阳永续：产品备案时间序列
- 基金业协会：产品备案公示

### D.4.6 竞争态势规则（权重5%）

| 规则ID | 规则名称 | 条件 | 评分 |
|--------|----------|------|------|
| COMPETE_001 | 空白客户 | 无券商合作记录 | 5分 |
| COMPETE_002 | 他行客户 | 有合作但可替换 | 3分 |
| COMPETE_003 | 我行客户 | 已在我司开户 | 过滤排除 |
| COMPETE_004 | 流失风险 | 近6个月交易量下降>50% | 4分（挽回机会） |

## D.5 挖掘流程设计

### D.5.1 批量挖掘流程

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

### D.5.2 实时挖掘流程

触发条件：
- 新员工入职（分配区域客户）
- 客户主动询价（官网/电话）
- 市场活动报名（展会/路演）
- 竞品客户流失预警

处理逻辑：
1. 实时查询三大数据源（公司机构客户库、朝阳永续、基金业协会）
2. 即时计算匹配度
3. 推送给责任员工
4. 24小时内必须响应

---

**更新时间**: 2026-03-07  
**更新内容**: 新增潜客挖掘数据模型、六大挖掘规则、批量/实时挖掘流程
