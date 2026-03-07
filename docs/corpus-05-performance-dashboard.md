# 员工业绩看板模块 - 参考语料与使用规则

> 文档编号: CORPUS-05  
> 模块名称: 员工业绩看板模块  
> 适用对象: 销售团队、管理层、HR  
> 更新日期: 2026-03-07

---

## 一、参考语料

### 1.1 业绩分析AI解读提示词

#### 系统角色设定
```
你是一位资深销售数据分析专家，拥有10年以上销售团队管理经验。
你的职责是帮助员工理解业绩数据，发现增长机会，并提供可执行的提升建议。
语气要求：专业、鼓励、建设性，避免打击员工积极性。
```

#### 业绩解读提示词模板

**【基础解读模板】**
```
请根据以下员工业绩数据生成个性化分析报告：

员工信息：
- 姓名：{employee_name}
- 部门：{department}
- 统计周期：{start_date} 至 {end_date}

核心指标：
- 收入目标：{target_revenue} 元
- 实际收入：{actual_revenue} 元
- 目标完成率：{completion_rate}%
- 新增客户数：{new_customers}
- 成交总额：{total_deals} 元
- 平均客单价：{avg_deal_value} 元

分析要求：
1. 总体评价：用1-2句话总结该员工业绩表现（达标/优秀/需努力）
2. 亮点挖掘：找出1-2个值得肯定的数据点或进步
3. 差距分析：如未达标，分析主要原因（客户量/转化率/客单价）
4. 行动建议：提供3条具体、可执行的提升建议
5. 鼓励话语：以积极正向的话结尾

输出格式：
- 使用emoji增加可读性
- 数据对比用表格呈现
- 建议部分使用编号列表
```

**【趋势分析模板】**
```
基于以下历史数据，分析员工业绩趋势：

月度数据（近6个月）：
{monthly_data}

分析维度：
1. 整体趋势判断（上升/平稳/波动/下滑）
2. 季节性因素分析
3. 与团队平均水平的对比
4. 下月业绩预测及置信区间
5. 趋势改善/维持建议
```

**【对标分析模板】**
```
请进行员工横向对比分析：

被分析员工：{employee_name}
部门平均值：
- 收入完成率：{dept_avg_completion}%
- 新增客户：{dept_avg_customers}
- 成交总额：{dept_avg_deals}

Top 10%员工平均值：
- 收入完成率：{top10_completion}%
- 新增客户：{top10_customers}
- 成交总额：{top10_deals}

分析要点：
1. 该员工在部门中的相对位置（百分位）
2. 与顶尖员工的差距量化
3. 可学习的优秀实践建议
4. 个性化追赶目标设定
```

### 1.2 业绩目标设定建议话术

#### SMART目标设定话术

**【目标设定引导话术】**
```
📌 目标设定五步法：

第一步：回顾历史（Reflect）
"回顾上个季度，您的实际业绩是{actual}，基于这个数据，我们来设定新目标。"

第二步：分析潜力（Analyze）
"根据您的客户资源池和转化率，理论上您的潜力区间是{potential_min}-{potential_max}。"

第三步：确定基准（Benchmark）
"结合公司整体增长目标{company_growth}%，您的基准目标应为{base_target}。"

第四步：挑战设定（Challenge）
"考虑到{specific_factor}，建议设定挑战目标{challenge_target}，达成将有额外奖励。"

第五步：确认承诺（Commit）
"最终确定您的季度目标为{final_target}，我们将每周跟踪进度，有困难随时沟通。"
```

**【目标沟通话术模板】**

| 场景 | 话术示例 |
|------|----------|
| 目标上调 | "基于您上季度的优秀表现（达成率{x}%），建议本季度目标上调{increase}%，新目标为{new_target}。这是对您的信任，也是成长的机会。" |
| 目标下调 | "考虑到{reason}，本季度目标调整为{new_target}。重点是夯实基础，下个季度再发力。" |
| 目标持平 | "保持{target}不变，重点在于提升质量指标（客户满意度、复购率），而非单纯追求数字。" |
| 新人目标 | "首月以学习为主，目标设定为{target}，主要是熟悉流程和积累首批客户。" |

#### 目标分解话术
```
📊 月度目标分解公式：

季度目标：{quarter_target}

建议分解：
- 首月（开拓期）：{month1} ({month1_ratio}%) - 重点：客户开发
- 次月（攻坚期）：{month2} ({month2_ratio}%) - 重点：转化成交
- 末月（冲刺期）：{month3} ({month3_ratio}%) - 重点：业绩冲刺

每周里程碑：
- Week 1-2：完成客户拜访{x}家
- Week 3：达成意向金额{y}万
- Week 4：确保签约金额{z}万

关键策略：{strategy_tips}
```

### 1.3 排行榜展示说明

#### 排行榜界面文案

**【页面标题】**
```
🏆 业绩龙虎榜 - {period}  
更新时间：{update_time} | 数据截至：{data_time}
```

**【榜单类型切换标签】**
```
💰 收入榜 | 👥 新增客户榜 | 🤝 成交额榜 | 📈 增长率榜
```

**【榜单表头说明】**
```
排名 | 员工 | 部门 | 核心指标 | 环比变化 | 上榜次数 | 操作
```

**【排名徽章说明】**
```
🥇 冠军 - 本期第1名（连续{x}期上榜）
🥈 亚军 - 本期第2名
🥉 季军 - 本期第3名
🏅 TOP 10 - 本期前10名
📌 上升 - 排名较上期上升{x}位
📍 新进榜 - 首次进入榜单
```

**【榜单底部说明】**
```
📋 榜单规则说明：
1. 统计周期：{period_desc}
2. 数据范围：{scope_desc}
3. 排名规则：按{metric}降序排列，相同数值按时间先后排序
4. 更新频率：{update_frequency}
5. 疑问反馈：请联系{contact}
```

#### 榜单通知文案

**【上榜通知】**
```
🎉 恭喜上榜！

亲爱的 {employee_name}：

您在 {period} {rank_type}榜 中获得 第{rank}名 的好成绩！

核心数据：
• 指标值：{metric_value}
• 超越 {surpass_ratio}% 的同事
• 较上期 {change_desc}

继续保持，下一个冠军就是你！🏆
```

**【排名上升通知】**
```
📈 排名上升提醒

{employee_name}，好消息！

您的排名较上期上升了 {rise_positions} 位，
目前位列 {current_rank}。

进步分析：
• 主要提升点：{improvement_point}
• 关键动作：{key_actions}

再接再厉！💪
```

### 1.4 业绩预警通知模板

#### 预警级别定义

| 级别 | 颜色 | 触发条件 | 响应时效 |
|------|------|----------|----------|
| 🔴 紧急 | 红色 | 完成率 < 50% 或 同比降幅 > 30% | 即时通知 |
| 🟠 严重 | 橙色 | 完成率 50-70% 或 环比降幅 > 20% | 当日通知 |
| 🟡 关注 | 黄色 | 完成率 70-85% 或 连续2期下滑 | 次日通知 |
| 🔵 提醒 | 蓝色 | 完成率 85-95% 或 进度落后 | 周报提醒 |

#### 预警通知模板

**【红色预警 - 紧急】**
```
🚨 业绩紧急预警

员工：{employee_name}  |  部门：{department}

⚠️ 预警信息：
• 当前完成率：{completion_rate}%（目标：{target}）
• 剩余时间：{days_left} 天
• 缺口金额：{gap_amount} 元
• 日均需完成：{daily_required} 元

🔍 风险分析：
{ai_risk_analysis}

📋 紧急行动建议：
1. {action_1}
2. {action_2}
3. {action_3}

💬 主管已收到通知，将在 {response_time} 内与您沟通。

[查看详情] [预约辅导] [资源申请]
```

**【橙色预警 - 严重】**
```
⚠️ 业绩严重预警

员工：{employee_name}

预警详情：
• 完成率：{completion_rate}%
• 主要问题：{primary_issue}
• 预计影响：{projected_impact}

📊 历史对比：
{comparison_chart}

💡 改善建议：
{suggestions}

请于 {deadline} 前制定改善计划并提交。
```

**【黄色预警 - 关注】**
```
📊 业绩关注提醒

{employee_name}，您的业绩需要关注：

当前状态：{status_desc}
趋势分析：{trend_desc}

🎯 建议关注：
{focus_points}

资源支持：如有需要，可申请 {support_options}。
```

**【蓝色提醒 - 温和】**
```
💙 业绩进度提醒

{employee_name}：

本周业绩进度 {progress}%，略低于时间进度 {time_progress}%。

温馨提示：
{tips}

下周重点：{next_week_focus}
```

#### 主管通知模板

**【团队预警汇总】**
```
📋 团队业绩预警日报 - {date}

{manager_name}，您好：

您管理的 {team_name} 有以下预警需要关注：

🔴 紧急预警（{red_count}人）：
{red_list}

🟠 严重预警（{orange_count}人）：
{orange_list}

🟡 关注提醒（{yellow_count}人）：
{yellow_list}

📈 团队整体完成率：{team_completion}%

[查看详细分析] [一键发送提醒] [发起团队会议]
```

---

## 二、数据需求

### 2.1 输入数据清单

#### A. 收入数据

| 字段名称 | 数据类型 | 说明 | 来源系统 | 更新频率 |
|----------|----------|------|----------|----------|
| revenue_id | STRING | 收入记录唯一标识 | CRM | 实时 |
| employee_id | STRING | 员工ID | HR系统 | 每日 |
| employee_name | STRING | 员工姓名 | HR系统 | 每日 |
| department_id | STRING | 部门ID | HR系统 | 每日 |
| department_name | STRING | 部门名称 | HR系统 | 每日 |
| revenue_amount | DECIMAL(18,2) | 收入金额（元） | CRM | 实时 |
| revenue_type | ENUM | 收入类型（新签/续费/增购） | CRM | 实时 |
| contract_id | STRING | 关联合同ID | CRM | 实时 |
| customer_id | STRING | 客户ID | CRM | 实时 |
| recognize_date | DATE | 收入确认日期 | 财务系统 | 每日 |
| target_period | STRING | 目标周期（2026Q1） | 目标系统 | 每月 |
| target_amount | DECIMAL(18,2) | 目标金额 | 目标系统 | 每月 |

#### B. 客户数据

| 字段名称 | 数据类型 | 说明 | 来源系统 | 更新频率 |
|----------|----------|------|----------|----------|
| customer_id | STRING | 客户唯一标识 | CRM | 实时 |
| customer_name | STRING | 客户名称 | CRM | 实时 |
| owner_id | STRING | 客户负责人ID | CRM | 实时 |
| owner_name | STRING | 客户负责人姓名 | CRM | 实时 |
| create_date | DATE | 客户创建日期 | CRM | 实时 |
| customer_status | ENUM | 客户状态（潜在客户/成交客户/流失客户） | CRM | 每日 |
| customer_source | STRING | 客户来源 | CRM | 实时 |
| industry | STRING | 所属行业 | CRM | 每日 |
| region | STRING | 所属区域 | CRM | 每日 |
| first_deal_date | DATE | 首次成交日期 | CRM | 每日 |
| last_contact_date | DATE | 最后联系日期 | CRM | 每日 |
| customer_value | ENUM | 客户等级（A/B/C/D） | CRM | 每日 |

#### C. 交易数据

| 字段名称 | 数据类型 | 说明 | 来源系统 | 更新频率 |
|----------|----------|------|----------|----------|
| deal_id | STRING | 交易/合同唯一标识 | CRM | 实时 |
| deal_name | STRING | 交易名称 | CRM | 实时 |
| employee_id | STRING | 签约员工ID | CRM | 实时 |
| customer_id | STRING | 客户ID | CRM | 实时 |
| deal_amount | DECIMAL(18,2) | 合同金额（元） | CRM | 实时 |
| deal_status | ENUM | 交易状态（商机/谈判/签约/回款/关闭） | CRM | 实时 |
| create_date | DATE | 创建日期 | CRM | 实时 |
| close_date | DATE | 签约日期 | CRM | 实时 |
| expected_close_date | DATE | 预计签约日期 | CRM | 每日 |
| product_ids | ARRAY<STRING> | 产品ID列表 | CRM | 实时 |
| payment_terms | STRING | 付款条款 | CRM | 实时 |
| profit_margin | DECIMAL(5,2) | 毛利率 | 财务系统 | 每日 |
| cost_amount | DECIMAL(18,2) | 成本金额 | 财务系统 | 每日 |

#### D. 辅助数据

| 字段名称 | 数据类型 | 说明 | 来源系统 | 更新频率 |
|----------|----------|------|----------|----------|
| work_day_calendar | DATE | 工作日历 | 内部系统 | 每年 |
| holiday_info | JSON | 节假日信息 | 内部系统 | 每年 |
| target_history | JSON | 历史目标数据 | 目标系统 | 每月 |
| employee_attr | JSON | 员工属性（工龄/职级/区域） | HR系统 | 每日 |
| product_catalog | JSON | 产品目录 | 产品系统 | 实时 |
| department_hierarchy | JSON | 部门层级关系 | HR系统 | 每日 |

### 2.2 输出数据清单

#### A. 业绩报告数据

| 输出项 | 数据格式 | 说明 | 计算方式 | 时效性 |
|--------|----------|------|----------|--------|
| performance_summary | JSON | 业绩汇总 | 聚合计算 | T+1 |
| completion_report | JSON | 完成率报告 | 实际/目标 | T+1 |
| gap_analysis | JSON | 缺口分析 | 目标-实际 | T+1 |
| contribution_analysis | JSON | 贡献度分析 | 个人/团队占比 | T+1 |
| quality_metrics | JSON | 质量指标（客单价/转化率） | 衍生计算 | T+1 |

**业绩报告数据结构示例：**
```json
{
  "report_id": "PERF_202603_emp001",
  "employee_id": "emp001",
  "period": "2026Q1",
  "summary": {
    "target_revenue": 1000000,
    "actual_revenue": 850000,
    "completion_rate": 85.0,
    "new_customers": 15,
    "total_deals": 8,
    "avg_deal_value": 106250
  },
  "breakdown": {
    "by_month": [...],
    "by_product": [...],
    "by_region": [...]
  },
  "comparison": {
    "vs_last_period": 12.5,
    "vs_same_period_last_year": 8.3,
    "vs_team_avg": 15.2
  },
  "ranking": {
    "department_rank": 5,
    "company_rank": 23,
    "percentile": 67
  }
}
```

#### B. 排名结果数据

| 输出项 | 数据格式 | 说明 | 计算方式 | 时效性 |
|--------|----------|------|----------|--------|
| revenue_ranking | ARRAY | 收入排名列表 | 排序+排名算法 | T+1 |
| customer_ranking | ARRAY | 新增客户排名 | 排序+排名算法 | T+1 |
| deal_ranking | ARRAY | 成交额排名 | 排序+排名算法 | T+1 |
| growth_ranking | ARRAY | 增长率排名 | 环比计算+排序 | T+1 |
| historical_ranks | ARRAY | 历史排名记录 | 累积存储 | 实时查询 |

**排名结果数据结构示例：**
```json
{
  "ranking_id": "RANK_202603_REV",
  "rank_type": "revenue",
  "period": "2026-03",
  "update_time": "2026-03-07T23:59:59Z",
  "total_participants": 156,
  "rankings": [
    {
      "rank": 1,
      "employee_id": "emp042",
      "employee_name": "张三",
      "department": "华东销售一部",
      "metric_value": 1580000,
      "change_from_last": 0,
      "consecutive_count": 3,
      "badge": "🥇"
    }
  ]
}
```

#### C. 趋势预测数据

| 输出项 | 数据格式 | 说明 | 计算方式 | 时效性 |
|--------|----------|------|----------|--------|
| trend_line | ARRAY | 趋势线数据 | 时间序列分析 | 每日更新 |
| seasonality_factors | JSON | 季节性因子 | 历史同期分析 | 每月更新 |
| forecast_next_month | DECIMAL | 下月预测值 | 预测模型 | 每月更新 |
| forecast_confidence | JSON | 预测置信区间 | 统计计算 | 每月更新 |
| yoy_growth_rate | DECIMAL | 同比增长率 | (本期-同期)/同期 | T+1 |
| mom_growth_rate | DECIMAL | 环比增长率 | (本期-上期)/上期 | T+1 |

**趋势预测数据结构示例：**
```json
{
  "forecast_id": "FCST_emp001_202604",
  "employee_id": "emp001",
  "current_period": "2026-03",
  "forecast_period": "2026-04",
  "historical_data": [
    {"month": "2025-10", "value": 720000},
    {"month": "2025-11", "value": 780000},
    {"month": "2025-12", "value": 950000},
    {"month": "2026-01", "value": 820000},
    {"month": "2026-02", "value": 880000},
    {"month": "2026-03", "value": 850000}
  ],
  "forecast": {
    "point_estimate": 875000,
    "confidence_80": {"lower": 820000, "upper": 930000},
    "confidence_95": {"lower": 780000, "upper": 970000}
  },
  "trend": {
    "direction": "stable",
    "slope": 0.03,
    "r_squared": 0.72
  },
  "seasonality": {
    "factor": 1.05,
    "peak_months": ["12", "06"],
    "low_months": ["02", "07"]
  }
}
```

### 2.3 数据聚合规则

#### 聚合维度矩阵

| 聚合维度 | 层级 | 字段 | 适用指标 | 聚合函数 |
|----------|------|------|----------|----------|
| 时间 | 日 | date | 收入/客户/交易 | SUM/COUNT |
| 时间 | 周 | week | 收入/客户/交易 | SUM/COUNT |
| 时间 | 月 | month | 收入/客户/交易 | SUM/COUNT |
| 时间 | 季 | quarter | 收入/客户/交易 | SUM/COUNT |
| 时间 | 年 | year | 收入/客户/交易 | SUM/COUNT |
| 组织 | 个人 | employee_id | 全量指标 | SUM/COUNT/AVG |
| 组织 | 团队 | team_id | 全量指标 | SUM/COUNT/AVG |
| 组织 | 部门 | dept_id | 全量指标 | SUM/COUNT/AVG |
| 组织 | 公司 | company | 全量指标 | SUM/COUNT/AVG |
| 业务 | 产品 | product_id | 收入/交易 | SUM/COUNT |
| 业务 | 客户类型 | customer_type | 收入/客户 | SUM/COUNT |
| 业务 | 区域 | region | 全量指标 | SUM/COUNT/AVG |
| 业务 | 渠道 | channel | 客户/交易 | SUM/COUNT |

#### 核心聚合规则

**1. 收入聚合规则**
```sql
-- 个人日收入聚合
SELECT 
    employee_id,
    recognize_date,
    SUM(revenue_amount) as daily_revenue,
    COUNT(DISTINCT contract_id) as deal_count,
    SUM(revenue_amount) / COUNT(DISTINCT contract_id) as avg_deal_value
FROM revenue_fact
WHERE recognize_date BETWEEN '{start_date}' AND '{end_date}'
GROUP BY employee_id, recognize_date;

-- 个人月度收入聚合
SELECT 
    employee_id,
    DATE_FORMAT(recognize_date, '%Y-%m') as month,
    SUM(revenue_amount) as monthly_revenue,
    SUM(CASE WHEN revenue_type = 'new' THEN revenue_amount ELSE 0 END) as new_revenue,
    SUM(CASE WHEN revenue_type = 'renewal' THEN revenue_amount ELSE 0 END) as renewal_revenue
FROM revenue_fact
GROUP BY employee_id, DATE_FORMAT(recognize_date, '%Y-%m');
```

**2. 客户聚合规则**
```sql
-- 新增客户统计（按创建日期）
SELECT 
    owner_id as employee_id,
    DATE_FORMAT(create_date, '%Y-%m') as month,
    COUNT(DISTINCT customer_id) as new_customers,
    SUM(CASE WHEN customer_value = 'A' THEN 1 ELSE 0 END) as a_level_customers
FROM customer_dim
WHERE customer_status IN ('potential', 'active')
GROUP BY owner_id, DATE_FORMAT(create_date, '%Y-%m');

-- 活跃客户统计
SELECT 
    owner_id as employee_id,
    COUNT(DISTINCT CASE WHEN last_contact_date >= DATE_SUB(CURRENT_DATE, 30) THEN customer_id END) as active_customers_30d
FROM customer_dim
GROUP BY owner_id;
```

**3. 交易聚合规则**
```sql
-- 成交统计
SELECT 
    employee_id,
    DATE_FORMAT(close_date, '%Y-%m') as month,
    COUNT(DISTINCT deal_id) as closed_deals,
    SUM(deal_amount) as total_deal_amount,
    AVG(deal_amount) as avg_deal_amount,
    SUM(CASE WHEN deal_status = 'signed' THEN deal_amount ELSE 0 END) as signed_amount
FROM deal_fact
WHERE deal_status IN ('signed', 'completed')
GROUP BY employee_id, DATE_FORMAT(close_date, '%Y-%m');

-- 商机转化统计
SELECT 
    employee_id,
    COUNT(DISTINCT CASE WHEN deal_status IN ('opportunity', 'negotiation') THEN deal_id END) as open_opportunities,
    COUNT(DISTINCT CASE WHEN deal_status = 'signed' THEN deal_id END) as converted_deals,
    COUNT(DISTINCT CASE WHEN deal_status = 'signed' THEN deal_id END) * 1.0 / 
    COUNT(DISTINCT CASE WHEN deal_status IN ('opportunity', 'negotiation', 'signed', 'lost') THEN deal_id END) as conversion_rate
FROM deal_fact
GROUP BY employee_id;
```

**4. 目标完成率计算**
```sql
-- 目标完成率
SELECT 
    t.employee_id,
    t.target_period,
    t.target_amount,
    COALESCE(SUM(r.revenue_amount), 0) as actual_amount,
    COALESCE(SUM(r.revenue_amount), 0) / t.target_amount * 100 as completion_rate
FROM target_dim t
LEFT JOIN revenue_fact r ON t.employee_id = r.employee_id 
    AND r.recognize_date BETWEEN t.period_start AND t.period_end
GROUP BY t.employee_id, t.target_period, t.target_amount;
```

---

## 三、使用规则

### 3.1 业绩指标计算规则

#### 核心指标定义

| 指标名称 | 指标代码 | 计算公式 | 单位 | 精度 | 说明 |
|----------|----------|----------|------|------|------|
| 收入目标完成率 | RPC | 实际收入 ÷ 收入目标 × 100% | % | 1位小数 | 核心KPI |
| 新增客户数 | NNC | COUNT(客户创建日期在周期内) | 人 | 整数 | 去重统计 |
| 成交总额 | TDA | SUM(签约合同金额) | 元 | 2位小数 | 含新签+续费 |
| 平均客单价 | ADV | 成交总额 ÷ 成交客户数 | 元 | 2位小数 | 衡量客户质量 |
| 客户转化率 | CVR | 成交客户数 ÷ 新增客户数 × 100% | % | 2位小数 | 衡量转化能力 |
| 销售漏斗转化率 | FCR | 各阶段转化率连乘 | % | 2位小数 | 全流程效率 |
| 回款率 | CRR | 实际回款 ÷ 成交金额 × 100% | % | 2位小数 | 资金健康度 |
| 客户复购率 | RPR | 复购客户数 ÷ 总客户数 × 100% | % | 2位小数 | 客户忠诚度 |
| 同比增长率 | YOY | (本期-去年同期) ÷ 去年同期 × 100% | % | 2位小数 | 年度对比 |
| 环比增长率 | MOM | (本期-上期) ÷ 上期 × 100% | % | 2位小数 | 月度对比 |

#### 指标计算细则

**1. 收入目标完成率计算规则**

```
计算公式：
完成率 = (实际确认收入 ÷ 目标收入) × 100%

数据口径：
- 实际收入：财务系统确认的收入金额（权责发生制）
- 目标收入：目标管理系统下达的季度/年度目标
- 统计周期：自然月/自然季度/自然年

边界规则：
- 收入确认日期以财务系统为准
- 跨期合同按确认规则分摊
- 退款冲减当期收入
- 时间截止：统计周期最后一日 23:59:59

分段评价：
- 优秀：≥120%
- 良好：100%-119%
- 达标：85%-99%
- 预警：70%-84%
- 严重：<70%
```

**2. 新增客户统计规则**

```
定义：在统计周期内首次创建的客户记录

去重规则：
- 同一客户（customer_id）在周期内多次创建仅计1次
- 客户归属以创建时的owner_id为准
- 客户状态为"潜在客户"或"成交客户"

排除规则：
- 测试数据（customer_name包含"测试"）
- 内部员工（industry = 'INTERNAL'）
- 已删除客户（is_deleted = 1）

统计时点：
- 以客户创建日期（create_date）为准
- 精确到日，不考虑时分秒
```

**3. 成交总额计算规则**

```
计算公式：
成交总额 = Σ(合同金额)

合同范围：
- 合同状态 = '已签约' 或 '已完成'
- 签约日期在统计周期内
- 非测试合同（deal_name不包含"测试"）

金额口径：
- 含税金额
- 按签约金额统计（非回款金额）
- 多币种按签约日汇率换算为人民币

分类统计：
- 新签合同：客户首次签约
- 续签合同：老客户续约
- 增购合同：老客户新增采购
```

**4. 趋势指标计算规则**

```
同比增长率（YoY）：
公式：(本期数值 - 去年同期数值) ÷ 去年同期数值 × 100%
适用：月度/季度/年度同比
注意：去年同期数值为0时，增长率标记为"N/A"

环比增长率（MoM）：
公式：(本期数值 - 上期数值) ÷ 上期数值 × 100%
适用：月度环比
上期定义：上一个自然月/季度

移动平均（MA）：
3月移动平均 = (T月 + T-1月 + T-2月) ÷ 3
用于平滑波动，识别趋势

复合增长率（CAGR）：
公式：(期末值 ÷ 期初值)^(1/年数) - 1
适用：多年度增长评估
```

### 3.2 排行榜排名规则（标准竞争排名1224）

#### 排名算法说明

**标准竞争排名（Standard Competition Ranking）- 1224规则**

```
排名规则：
1. 按核心指标值降序排列
2. 相同数值者并列同一名次
3. 下一名次跳过并列数量

示例：
排名 | 员工 | 收入 | 规则说明
-----|------|------|----------
1    | A    | 150万| 最高
1    | B    | 150万| 与A相同，并列第1
3    | C    | 140万| 跳过第2名
4    | D    | 130万| 
4    | E    | 130万| 与D相同，并列第4
6    | F    | 120万| 跳过第5名

处理规则：
- 第2名空缺时，下一名从第3开始
- 榜单显示"第1名"而非"第1/2名"
- 并列者享受相同的奖励/荣誉
```

#### 榜单生成规则

**1. 收入排行榜**
```
排序字段：monthly_revenue DESC
参与条件：
- 统计周期内有收入记录
- 非试用期员工（tenure > 1个月）
- 非离职员工（status != 'terminated'）

榜单规模：
- 默认展示Top 50
- 支持查看全部排名
- 可筛选部门/区域
```

**2. 新增客户排行榜**
```
排序字段：new_customers DESC
参与条件：
- 统计周期内有新客户记录
- 排除测试数据
- 客户需通过审核（status != 'pending'）

防刷规则：
- 同一公司多个联系人只计1次
- 低质量客户（无跟进记录）不计入
- 系统检测异常批量创建将人工审核
```

**3. 成交额排行榜**
```
排序字段：total_deal_amount DESC
参与条件：
- 统计周期内有签约记录
- 合同状态为有效
- 签约金额 > 0

特殊处理：
- 大单（>100万）标注
- 团队项目按贡献度分配
- 跨期合同按签约日期统计
```

**4. 增长率排行榜**
```
排序字段：growth_rate DESC
参与条件：
- 上期业绩 > 0（避免除零）
- 本期业绩 > 上期业绩 × 0.5（排除异常）
- 在职满2个周期

计算公式：
growth_rate = (本期 - 上期) / 上期 × 100%

特殊标注：
- 上期业绩为0且本期>0：标记为"新星"
- 增长率>100%：标记为"爆发增长"
```

#### 排名变化计算

```
排名变化 = 上期排名 - 本期排名

正值：排名上升（进步）
负值：排名下降（退步）
零值：排名不变

变化标注：
↑5：上升5位
↓3：下降3位
—：保持不变
NEW：新上榜
```

### 3.3 业绩预警阈值规则

#### 预警触发条件

**一级预警（红色 - 紧急）**
```
触发条件（满足任一）：
1. 完成率 < 50% 且 已过周期50%时间
2. 同比下降 > 30% 且 绝对值下降 > 10万
3. 连续3期（月/季）排名后10%
4. 关键客户流失金额 > 季度目标20%

通知对象：
- 本人（即时推送）
- 直接主管（即时推送）
- HRBP（次日汇总）

响应要求：
- 24小时内制定改善计划
- 48小时内主管一对一沟通
- 一周后进行进展回顾
```

**二级预警（橙色 - 严重）**
```
触发条件（满足任一）：
1. 完成率 50%-70% 且 已过周期60%时间
2. 环比下降 > 20% 且 连续2期下滑
3. 进度落后时间进度 > 15%
4. 新增客户数为0 且 已过周期30%

通知对象：
- 本人（当日推送）
- 直接主管（当日推送）

响应要求：
- 3日内提交改善计划
- 主管本周内安排辅导
```

**三级预警（黄色 - 关注）**
```
触发条件（满足任一）：
1. 完成率 70%-85%
2. 环比连续2期下滑但降幅<20%
3. 排名较上期下降 > 10位
4. 重点客户跟进逾期 > 7天

通知对象：
- 本人（次日推送）

响应要求：
- 自主调整工作节奏
- 可申请资源支持
```

**四级提醒（蓝色 - 温和）**
```
触发条件（满足任一）：
1. 完成率 85%-95%
2. 进度略低于时间进度（<10%）
3. 距目标差距 < 日均产出 × 3天

通知对象：
- 本人（周报推送）

响应要求：
- 关注最后冲刺机会
- 适当加大工作投入
```

#### 预警解除规则

```
自动解除条件：
1. 完成率提升至阈值以上（如85%→90%）
2. 新周期开始，历史预警归档
3. 员工状态变更（离职/调岗）

手动解除条件：
1. 主管确认已制定有效改善计划
2. 经数据分析排除误报（如大客户延迟签约）
3. 不可抗力因素导致（需审批）

解除通知：
- 预警解除时发送通知
- 历史预警保留可查
- 解除原因记录存档
```

### 3.4 数据更新频率规则

#### 数据更新矩阵

| 数据类型 | 实时更新 | 每日更新 | 每周更新 | 每月更新 | 来源系统 |
|----------|----------|----------|----------|----------|----------|
| 收入数据 | ✅ | ✅ | - | - | CRM/财务 |
| 客户数据 | ✅ | ✅ | - | - | CRM |
| 交易数据 | ✅ | ✅ | - | - | CRM |
| 排行榜 | - | ✅ 23:00 | - | - | 数仓 |
| 业绩报告 | - | ✅ 06:00 | - | - | 数仓 |
| 趋势预测 | - | - | - | ✅ 1日 | 数仓 |
| 预警检测 | - | ✅ 09:00/15:00 | - | - | 数仓 |
| 目标数据 | - | - | - | ✅ 1日 | 目标系统 |
| 组织数据 | - | ✅ 05:00 | - | - | HR系统 |

#### 更新时序图

```
每日更新流程：

05:00 - HR系统同步（员工/部门数据）
    ↓
06:00 - 财务系统关账确认
    ↓
06:30 - 数据仓库ETL开始
    ↓
07:00 - 数据清洗/校验完成
    ↓
07:30 - 指标计算（完成率/排名等）
    ↓
08:00 - 预警检测执行
    ↓
08:30 - 报表数据生成
    ↓
09:00 - 预警通知推送（第一批）
    ↓
...业务时间...
    ↓
23:00 - 当日最终排行榜更新
    ↓
23:30 - 备份/归档
```

#### 数据时效性说明

```
实时数据：
- 客户新增：T+0（创建后1分钟内可见）
- 合同录入：T+0（录入后1分钟内可见）
- 个人看板：T+0（刷新后即时更新）

准实时数据：
- 日业绩汇总：T+1（次日06:00更新）
- 排行榜：T+1（次日23:00更新）
- 预警通知：T+0.5（每日09:00/15:00检测）

定期数据：
- 月度报告：M+1（次月3日）
- 季度报告：Q+5（季后5日）
- 年度报告：Y+10（年后10日）
- 趋势预测：M+1（每月1日）

特殊情况：
- 月末冲刺期：排行榜每4小时更新
- 季度末：预警检测每日3次（09:00/15:00/20:00）
- 系统维护：提前通知，更新延后
```

#### 数据一致性保障

```
校验机制：
1. 每日对账：数仓与源系统金额差异<0.01%
2. 异常监控：单日波动>30%自动标记人工复核
3. 回滚机制：发现错误可在2小时内回滚重算
4. 审计日志：所有数据变更记录可追溯

容错处理：
- 源系统延迟：使用缓存数据，延迟不超过4小时
- 计算错误：降级显示历史数据，通知技术团队
- 网络故障：本地缓存支持，故障恢复后自动同步
```

---

## 四、附录

### 4.1 术语表

| 术语 | 英文 | 定义 |
|------|------|------|
| KPI | Key Performance Indicator | 关键绩效指标 |
| YoY | Year over Year | 同比增长 |
| MoM | Month over Month | 环比增长 |
| MA | Moving Average | 移动平均 |
| CAGR | Compound Annual Growth Rate | 复合年增长率 |
| RPC | Revenue Performance Completion | 收入目标完成率 |
| CVR | Conversion Rate | 转化率 |
| ARPU | Average Revenue Per User | 客均收入 |
| LTV | Lifetime Value | 客户生命周期价值 |
| T+1 | Trade+1 | 交易日后1天 |

### 4.2 版本历史

| 版本 | 日期 | 修订内容 | 修订人 |
|------|------|----------|--------|
| v1.0 | 2026-03-07 | 初始版本 | AI助手 |

### 4.3 相关文档

- 《数据字典 - 销售模块》
- 《业绩目标管理规范》
- 《销售激励政策说明》
- 《CRM系统操作手册》

---

*本文档由AI助手生成，供产品开发参考使用。*
