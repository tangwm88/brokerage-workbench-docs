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
