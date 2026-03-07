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
