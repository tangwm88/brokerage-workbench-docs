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
