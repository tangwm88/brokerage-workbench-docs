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
