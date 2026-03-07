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
