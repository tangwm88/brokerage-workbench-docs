# 业务模型蒸馏智能体脚本

> **版本**：v1.0
> **日期**：2026-06-03
> **定位**：基于《企业级业务模型蒸馏智能体设计方案 v1.2》的可执行脚本
> **核心规则**：陶总五大反对 + 禁用词语表（不可修改）

---

## 功能

将企业业务知识（业务描述、组织架构、制度规范、历史数据）按**五步法**蒸馏为可执行的业务模型：

```
Step 1: 业务目标蒸馏（2日）→ 《业务目标清单》
Step 2: 标杆分析蒸馏（3日）→ 《标杆分析表》
Step 3: 数据关联蒸馏（3日）→ 《数据关联矩阵》
Step 4: 模型定义蒸馏（5日）→ 角色体系 + 分析模型 + 动作模型
Step 5: 交叉验证（3日）→ 《交叉验证报告》+ 模型修正版
─────────────────────────────────────────────────
合计：16个工作日，输出完整业务模型包
```

**核心规则校验**：每一步自动执行陶总五大反对检查 + 禁用词语表检查，违反则标记"不合格"需修正。

---

## 安装依赖

```bash
pip install pyyaml
```

---

## 使用方法

### 1. 使用示例数据运行（快速体验）

```bash
python distillation_agent.py --example --output ./output
```

### 2. 使用自定义输入文件运行

```bash
python distillation_agent.py --input business_desc.yaml --output ./output
```

### 3. 仅执行核心规则校验

```bash
python distillation_agent.py --input business_desc.yaml --validate-only
```

---

## 输入文件格式

输入文件为 YAML 格式，包含以下字段：

```yaml
# 业务描述
business_description:
  business_line: "业务线名称"
  core_goals:
    - name: "目标名称"
      definition: "目标定义"
      key_actions: ["关键动作1", "关键动作2", "关键动作3"]
      metrics: ["衡量指标1", "衡量指标2"]
      boundary: "边界说明"
  relationships:
    依赖: ["目标A → 目标B"]
    协同: ["目标C + 目标D → 效果"]

# 标杆分析（至少3个）
benchmarks:
  - dimension: "维度"
    benchmark_obj: "标杆对象"
    benchmark_practice: "标杆做法"
    our_status: "我方现状"
    gap: "差距"
    adoption: "借鉴决策"  # 直接采用/调整后采用/暂不采用/反面教材
    remark: "备注"

# 数据关联矩阵
data_matrix:
  - indicator: "指标名称"
    formula: "计算公式"
    data_source: "数据来源"
    access_path: "获取路径"
    auto_manual: "自动/半自动/手工"
    remark: "备注"

# 角色体系（组织者1 + 超级数字员工3-6）
roles:
  - name: "角色名称"
    source_position: "来源岗位"
    core_responsibility: "核心职责"
    service_goal: "服务目标"
    role_definition: "角色定义"
    goals: ["目标1", "目标2"]
    backstory: "背景故事"
    constraints:
      必须做: ["动作1"]
      禁止做: ["动作2"]

# 分析模型（3-5维度）
analysis_dimensions:
  - name: "维度名称"
    plain_language: "讲人话描述"
    objective_data: "客观数据来源"
    output: "输出内容"
    analysis_framework: "分析框架"

# 动作模型（事件-触发-步骤-输出-异常）
events:
  - event_name: "事件名称"
    trigger_condition: "触发条件"
    event_level: "常规/重点/重大"
    actions:
      - name: "动作名称"
        trigger: "触发条件"
        steps:
          - "步骤1"
          - "步骤2"
        output: "输出物"
        exception_handling:
          异常A: "处理方式"
        deadline: "X个工作日内"
        risk_level: "可以/必须确认/不"

# 裁判验证
referee_validation:
  referee_count: 2
  referees:
    - name: "裁判姓名"
      experience: "经验年限"
      feedback: "反馈意见"
  overall_feedback: "总体评价"
```

完整示例见 `example_bond_business.yaml`（投行债券发行业务示例）。

---

## 输出文件

运行后生成以下文件：

| 文件 | 说明 |
|------|------|
| `model_package.json` | 完整模型包（包含所有步骤结果） |
| `step1_business_goal.json` | Step 1 业务目标清单 |
| `step2_benchmark.json` | Step 2 标杆分析表 |
| `step3_data_association.json` | Step 3 数据关联矩阵 |
| `step4_model_definition.json` | Step 4 角色体系+分析模型+动作模型 |
| `step5_cross_validation.json` | Step 5 交叉验证报告 |
| `validation_logs.json` | 每步校验日志 |
| `README.md` | 可读报告（Markdown格式） |

---

## 核心规则（不可修改）

脚本内置以下核心规则，每一步自动校验：

### 陶总五大反对

1. **反对讲意义、讲作用、讲自洽，而不讲模型本身** → 检查是否有模型结构
2. **反对流程化、线性化地拆业务** → 检查是否为可调用原子库
3. **反对角色混乱、目标混乱** → 检查角色/目标是否清晰
4. **反对主观拍脑袋和甩锅给大模型** → 检查是否有客观数据支撑
5. **反对传统信息系统视角和技术自说自话** → 检查是否从角色和目的出发

### 禁用词语表

| 禁用词 | 推荐词 |
|--------|--------|
| 基本面 | 企业实际质地/财务实际状况 |
| 偏好 | 倾向/选择方向 |
| 流程 | 协同 |
| 行业 | 产业 |
| 场景 | 应用 |
| 逻辑 | 规律 |
| 对齐 | 领会 |
| 话术 | 沟通要点 |

---

## 脚本架构

```
distillation_agent.py
├── 核心规则（不可修改）
│   ├── 陶总五大反对
│   ├── 陶总八步方法论
│   └── 禁用词语表
├── 数据类定义
│   ├── BusinessGoal（业务目标）
│   ├── Benchmark（标杆分析）
│   ├── DataItem（数据关联）
│   ├── AnalysisDimension（分析维度）
│   ├── ActionItem（规定动作）
│   └── Role（角色定义）
├── 核心规则校验器（CoreRuleValidator）
│   ├── 禁用词检查
│   ├── 五大反对检查（5项）
│   └── 陶总八步映射检查
├── 五步法蒸馏引擎（DistillationEngine）
│   ├── Step 1: 业务目标蒸馏
│   ├── Step 2: 标杆分析蒸馏
│   ├── Step 3: 数据关联蒸馏
│   ├── Step 4: 模型定义蒸馏
│   └── Step 5: 交叉验证
├── 输入输出处理器（IOHandler）
│   ├── 加载输入（YAML/JSON）
│   └── 保存输出（JSON + Markdown报告）
└── 主程序入口
```

---

## 示例：快速运行

```bash
# 克隆仓库后进入脚本目录
cd scripts

# 使用示例数据运行
python distillation_agent.py --example --output ./test_output

# 查看输出
ls ./test_output
# model_package.json  step1_business_goal.json  step2_benchmark.json
# step3_data_association.json  step4_model_definition.json
# step5_cross_validation.json  validation_logs.json  README.md

# 查看可读报告
cat ./test_output/README.md
```

---

## 配套文档

- 《企业级业务模型蒸馏智能体设计方案 v1.2》—— 设计原理与规范
- 《智能体业务模型建设五步法》—— 五步法详细说明
- 《陶总关于业务模型的方法论》—— 指导思想与校准罗盘
- 《业务模型规定动作设计方法论与示例》—— 动作设计标准

---

*脚本版本：v1.0*
*创建时间：2026-06-03*
*遵循规范：禁用词语表（2026-05-30版）*
