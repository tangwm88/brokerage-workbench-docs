# Anthropic Financial Services 代码库研究报告

> **研究对象**：github.com/anthropics/financial-services  
> **研究日期**：2026-06-30  
> **研究员**：Kimi Claw  
> **GitHub 镜像**：https://github.com/tangwm88/financial-services

---

## 一、仓库全景概览

### 1.1 定位与性质

Anthropic 官方开源的**金融服务智能体参考实现**。覆盖投资银行、股票研究、私募股权、财富管理、基金运营、合规运营六大垂直领域。

**核心特征**：
- **纯 markdown + YAML，零构建步骤** — 所有技能、代理定义、工作流均以文本文件形式存在
- **一份源码，两种部署** — 同一套 skills/agent 定义，既可通过 Claude Cowork 插件安装，也可通过 Claude Managed Agents API 无头部署
- **11个 MCP 数据连接器** — 对接 S&P Kensho、FactSet、Daloopa、Morningstar、Moody's 等主流金融数据提供商
- **Apache 2.0 开源协议**

### 1.2 目录结构

```
plugins/
  agent-plugins/        # 9个命名智能体（端到端工作流）
    pitch-agent/        # 投行 pitch 全流程：comps → DCF → deck
    market-researcher/  # 行业研究：sector overview + comps + ideas
    earnings-reviewer/  # 业绩回顾：transcript → model update → note draft
    model-builder/      # 财务模型：DCF/LBO/3-statement in Excel
    valuation-reviewer/ # 估值审阅：GP packages → valuation → LP reporting
    gl-reconciler/      # 总账对账：GL vs subledger → break tracing
    month-end-closer/   # 月末关账：accruals → roll-forwards → commentary
    statement-auditor/  # 报表审计：LP statement audit
    kyc-screener/       # KYC 筛查：doc parse → rules engine → flag gaps

  vertical-plugins/     # 按垂直领域分组的技能源文件
    financial-analysis/ # 核心：comps, DCF, LBO, 3-statement, Excel audit
    investment-banking/ # CIM, teaser, pitch deck, buyer list, merger model
    equity-research/    # earnings note, initiation, model update, thesis
    private-equity/     # sourcing, screening, DD, IC memo, portfolio monitoring
    wealth-management/  # client review, financial plan, rebalancing, TLH
    fund-admin/         # GL recon, break trace, accruals, NAV tie-out
    operations/         # KYC doc parse, rules evaluation

  partner-built/        # 合作伙伴插件
    lseg/               # 债券 RV、swap 曲线、FX carry、期权波动率
    spglobal/           # tear sheet、earnings preview、funding digest

managed-agent-cookbooks/  # 无头部署模板（每个智能体一个目录）
  pitch-agent/          # agent.yaml + subagents/ + steering-examples.json
  gl-reconciler/        # 含安全分层设计（reader → orchestrator → resolver）
  ...

scripts/
  deploy-managed-agent.sh   # 一键部署到 /v1/agents
  check.py                  # 清单校验（manifest、引用、版本漂移）
  validate.py               # JSON schema 校验
  orchestrate.py            # 事件循环编排（handoff_request 路由）
  sync-agent-skills.py      # 垂直技能 → 智能体包同步
```

---

## 二、核心设计范式分析

### 2.1 技能（Skill）定义范式

每个技能是一个**自包含目录**，核心文件为 `SKILL.md`：

```yaml
---
name: comps-analysis
description: |
  Build institutional-grade comparable company analyses...
  
  **Perfect for:**
  - Public company valuation
  - Benchmarking performance vs. peers
  
  **Not ideal for:**
  - Private companies without public peers
  - Pre-revenue startups
---

# Comparable Company Analysis

## ⚠️ CRITICAL: Data Source Priority (READ FIRST)

**ALWAYS follow this data source hierarchy:**
1. **FIRST: Check for MCP data sources**
2. **DO NOT use web search** if MCP available
3. **ONLY if MCPs unavailable:** Bloomberg, SEC EDGAR
4. **NEVER use web search as primary source**

## Core Philosophy
**"Build the right structure first, then let the data tell the story."**

## Section 1: Document Structure & Setup
### Header Block (Rows 1-3)
...

## Section 2: Operating Statistics & Financial Metrics
### Core Columns
1. **Company** - Names with consistent formatting
2. **Revenue** - Size metric
...

## ⚠️ CRITICAL: Formulas Over Hardcodes
- Every derived value MUST be an Excel formula
- The only hardcoded values: raw input data
- Every hardcoded input gets a cell comment with source

## Section 3: Valuation Multiples & Investment Metrics
...

## Output Checklist
- [ ] All companies truly comparable
- [ ] Formulas reference cells, not hardcoded values
- [ ] All hard-coded inputs have comments with source
- [ ] Statistics include Max, 75th, Med, 25th, Min
```

**关键设计特征**：

| 特征 | 说明 | 与我方对比 |
|------|------|-----------|
| **YAML frontmatter** | name + description（含适用/不适用场景） | 类似，我方 SKILL.md 也采用此格式 |
| **分层结构** | Overview → 核心原则 → 分步骤执行 → 检查清单 | 我方五步法更宏观，此范式更微观（单任务级） |
| **CRITICAL 标记** | 用 ⚠️ 标记不可违背的规则（数据源优先级、公式规范） | **可借鉴**：将合规/质量红线显性化标注 |
| **反模式清单** | 明确列出 "NEVER DO THESE" | **可借鉴**：将常见错误模式作为反面教材写入技能 |
| **检查清单** | 交付前必须逐项勾选的 checklist | **可借鉴**：嵌入动作模型的验收环节 |
| **引用文件** | reference/ 子目录存放支撑材料（formula、template、terminology） | **可借鉴**：将参考资料与主技能分离，便于更新 |

### 2.2 智能体（Agent）定义范式

**Agent 定义 = system prompt + skills 清单 + 工具配置 + 子代理列表**

以 Pitch Agent 为例：

```markdown
# Pitch Agent

## What you produce
Given a target company ticker/name and situation, deliver:
1. **Excel valuation workbook** — comps, precedents, DCF, football field
2. **Pitch deck** — on bank's PowerPoint template

## Workflow
1. **Scope the ask.** Confirm target, sector, situation.
2. **Write situation overview.** Invoke `sector-overview` skill.
3. **Pull data.** Use CapIQ MCP for multiples, filings.
4. **Spread peer set.** Invoke `comps-analysis` skill.
5. **Stand up sponsor case.** Invoke `lbo-model` skill.
6. **Build model.** Invoke `dcf-model`, `3-statement-model`.
7. **Generate football field.** Min/median/max from each methodology.
8. **Populate deck.** Invoke `pitch-deck` skill against template.
9. **Run deck QC.** Invoke `ib-check-deck`.

## Guardrails
- **No external communications.** No email or messaging tools.
- **Cite every number.** Flag as `[UNSOURCED]` if can't source.
- **Stop and surface for review** after Excel built and after deck generated.

## Skills this agent uses
`sector-overview` · `comps-analysis` · `lbo-model` · `dcf-model` · `3-statement-model` · `audit-xls` · `pitch-deck` · `ib-check-deck` · `deck-refresh`
```

**关键设计特征**：

| 特征 | 说明 | 与我方对比 |
|------|------|-----------|
| **触发条件** | 由用户显式调用（"first-draft pitch on a name"） | 我方规定动作也有触发条件（事件-触发-步骤） |
| **步骤链** | 9步线性流程，每步调用一个 skill | 类似我方动作模型的"步骤"，但更细粒度 |
| **技能调用** | 用反引号标注 `` `skill-name` ``，明确依赖关系 | 我方动作模型也有"调用模型"环节 |
| **质量关卡** | 第7步后和第9步后必须人工 review | **可借鉴**：在关键节点设置"停止并等待确认" |
| **防护栏** | 明确列出禁止事项（no external comms, cite every number） | 类似我方三句话法（可以/必须确认/不） |

### 2.3 无头部署（Managed Agent）范式

`managed-agent-cookbooks/pitch-agent/agent.yaml`：

```yaml
name: pitch-agent
model: claude-opus-4-7

system:
  file: ../../plugins/agent-plugins/pitch-agent/agents/pitch-agent.md
  append: "You are running headless. Produce files in ./out/; do not assume an open Office document."

tools:
  - type: agent_toolset_20260401
    default_config: { enabled: false }
    configs:
      - { name: read,  enabled: true }
      - { name: grep,  enabled: true }
      - { name: glob,  enabled: true }
  - { type: mcp_toolset, mcp_server_name: capiq,   default_config: { enabled: true } }
  - { type: mcp_toolset, mcp_server_name: daloopa, default_config: { enabled: true } }

mcp_servers:
  - { type: url, name: capiq,   url: "${CAPIQ_MCP_URL}" }
  - { type: url, name: daloopa, url: "${DALOOPA_MCP_URL}" }

skills:
  - { from_plugin: ../../plugins/agent-plugins/pitch-agent }

callable_agents:
  - { manifest: ./subagents/researcher.yaml }
  - { manifest: ./subagents/modeler.yaml }
  - { manifest: ./subagents/deck-writer.yaml }   # only leaf with Write
```

**关键设计特征**：

| 特征 | 说明 | 与我方对比 |
|------|------|-----------|
| **模型选型** | 显式指定 `claude-opus-4-7` | 我方未明确模型选型标准 |
| **工具白名单** | 默认全关，按需开启（read/grep/glob + MCP） | **可借鉴**：最小权限原则 |
| **MCP 连接器** | 声明式配置，环境变量注入 URL | 我方需评估是否引入 MCP 标准 |
| **子代理分层** | researcher（读）→ modeler（算）→ deck-writer（写） | **可借鉴**：读写分离的安全设计 |
| **安全分层** | GL Reconciler 分 reader/orchestrator/resolver 三层 | **强烈借鉴**：不可信文档隔离机制 |

### 2.4 MCP 连接器架构

`.mcp.json` 集中配置所有数据连接器：

```json
{
  "mcpServers": {
    "daloopa":     { "type": "http", "url": "https://mcp.daloopa.com/server/mcp" },
    "sp-global":   { "type": "http", "url": "https://kfinance.kensho.com/integrations/mcp" },
    "factset":     { "type": "http", "url": "https://mcp.factset.com/mcp" },
    "moodys":      { "type": "http", "url": "https://api.moodys.com/genai-ready-data/m1/mcp" },
    "lseg":        { "type": "http", "url": "https://api.analytics.lseg.com/lfa/mcp" },
    "pitchbook":   { "type": "http", "url": "https://premium.mcp.pitchbook.com/mcp" }
  }
}
```

**关键设计特征**：

| 特征 | 说明 |
|------|------|
| **统一协议** | 所有连接器遵循 MCP（Model Context Protocol）标准 |
| **声明式配置** | 一个 JSON 文件声明所有连接器，无需代码 |
| **数据源优先级** | SKILL.md 中强制规定 MCP > Bloomberg > SEC > web search |
| **审计追溯** | 每个 hardcoded input 必须有 cell comment 标注来源 |

---

## 三、与我方方法论的对照分析

### 3.1 架构层对照

| 维度 | Anthropic FSI | 我方现状 | 差距/机会 |
|------|--------------|---------|----------|
| **技能定义** | SKILL.md（YAML frontmatter + markdown 指令） | SKILL.md（类似格式） | **基本持平** |
| **技能分层** | vertical-plugins（源）→ agent-plugins（ bundle） | skills/ 目录（独立） | **需改进**：缺少"源→bundle"同步机制 |
| **智能体定义** | agents/<slug>.md（system prompt + workflow） | 规定动作模型（事件-触发-步骤-输出-异常-时限） | **互补**：Anthropic 偏"单任务流"，我方偏"规定动作框架" |
| **子代理编排** | callable_agents（YAML 声明 + handoff_request 事件） | 未明确设计 | **差距**：我方需设计子代理通信协议 |
| **数据连接** | MCP 标准（声明式 JSON 配置） | 未标准化（各业务线自行对接） | **差距**：建议评估 MCP 兼容性 |
| **部署模式** | Cowork 插件 + Managed Agents API（双模式） | 工作台化（前端调用） | **差距**：缺少无头部署能力 |
| **安全分层** | reader/orchestrator/resolver 三层隔离 | 三句话法（合规边界） | **互补**：Anthropic 偏"技术隔离"，我方偏"合规规则" |
| **质量校验** | check.py + validate.py + 预提交钩子 | 交叉验证报告（人工评审） | **差距**：缺少自动化校验工具链 |

### 3.2 业务覆盖对照

| 业务领域 | Anthropic FSI 覆盖 | 我方覆盖 | 可借鉴内容 |
|----------|-------------------|---------|-----------|
| **投资银行** | ✅ pitch deck, CIM, teaser, merger model, buyer list | ✅ 债券发行、定增 | **高价值**：pitch-deck 技能（PPT 模板填充规范）、merger model 技能 |
| **股票研究** | ✅ earnings note, initiation, model update, thesis tracker | ⚠️ 研究所智能体（规划中） | **高价值**：earnings-analysis 工作流、model-update 规范 |
| **财富管理** | ✅ client review, financial plan, rebalancing, TLH | ⚠️ 财富管理智能体（规划中） | **中价值**：client-review 会议准备框架、portfolio-rebalance 逻辑 |
| **资产管理** | ✅ fund admin（GL recon, NAV tie-out, variance） | ✅ 资管产品销售、产品创设 | **中价值**：fund-admin 运营技能（可映射到产品运营） |
| **私募股权** | ✅ DD checklist, IC memo, returns analysis, value creation | ❌ 未覆盖 | **高价值**：IC memo 结构、returns analysis 模板、DD checklist |
| **合规运营** | ✅ KYC screener（doc parse → rules → flag） | ✅ 三句话法 | **中价值**：KYC 文档解析 + 规则引擎模式 |
| **债券销售交易** | ⚠️ partner-built/LSEG（bond RV, swap curve, FX carry） | ✅ 债券发行、销售交易 | **高价值**：LSEG 债券 RV 技能、swap curve 分析 |

### 3.3 方法论细节对照

#### A. 五步法 vs Anthropic Workflow

| 五步法（我方） | Anthropic 对应 | 评价 |
|--------------|---------------|------|
| Step 1: 业务目标（经营什么？关键动作？衡量指标？） | 隐含在 agent 的 "What you produce" 和 "Scope the ask" | Anthropic 缺少显式的业务目标蒸馏环节 |
| Step 2: 标杆分析（找标杆、拆做法、评差距、定借鉴） | 隐含在 skill 的 reference/ 目录 | **可改进**：我方标杆分析更系统，Anthropic 偏"参考文件" |
| Step 3: 数据关联（动作需要什么数据？在哪？怎么拿？） | 显式的 MCP 配置 + 数据源优先级 | **Anthropic 更优**：数据关联通过 MCP 标准化 |
| Step 4: 模型定义（角色体系 + 分析模型 + 动作模型） | agents/<slug>.md + skills/ | **基本对齐**：我方更强调"角色-模型"关系，Anthropic 更强调"技能-工具"配置 |
| Step 5: 交叉验证（自洽、标杆、可执行、裁判挑刺） | check.py + validate.py + 人工 review 关卡 | **互补**：Anthropic 有自动化校验工具，我方有人工裁判机制 |

#### B. 三句话法 vs Anthropic Guardrails

| 我方三句话法 | Anthropic Guardrails | 融合建议 |
|------------|---------------------|---------|
| **可以**：内部数据分析、客户分析更新 → AI 全自动 | "No external communications"（禁止对外通讯） | **对齐**：双方都限制了 Agent 的对外行为边界 |
| **必须确认**：投资建议、合规审查 → AI生成→人工审核→确认 | "Stop and surface for review"（关键节点必须人工确认） | **对齐**：双方都设置了人工确认关卡 |
| **不**：预测股价、代客下单 → AI 直接拒绝 | "Cite every number"（无法溯源则标记 UNSOURCED） | **互补**：我方是"拒绝型"边界，Anthropic 是"标记型"边界 |

#### C. 禁用词语表 vs Anthropic 语言风格

Anthropic 的 SKILL.md 中：
- ✅ 使用具体动词（"Build"、"Populate"、"Reconcile"）
- ✅ 避免互联网黑话（无"对齐"、"场景"、"逻辑"）
- ✅ 具体化描述（"Revenue (LTM)" 而非 "收入指标"）
- ✅ 白话表达（"How much market pays per dollar of sales" 解释 EV/Revenue）

**结论**：Anthropic 的语言风格与我方禁用词语表高度一致，可作为参考标杆。

---

## 四、可直接借鉴的具体内容

### 4.1 高优先级（立即可用）

#### 1. GL Reconciler 安全分层设计

**来源**：`managed-agent-cookbooks/gl-reconciler/README.md`

```
| Tier       | Touches untrusted docs? | Tools | Connectors |
|------------|------------------------|-------|------------|
| reader     | Yes                    | Read, Grep only | None |
| Orchestrator| No                    | Read, Grep, Glob, Agent | Read-only GL + subledger MCPs |
| resolver (Write-holder) | No | Read, Write, Edit | None |
```

**借鉴价值**：
- 处理不可信文档（客户/交易对手提供的文件）时的**标准安全模式**
- reader 层只读 + 返回 schema 校验后的 JSON
- resolver（写持有者）永远不接触外部文件
- **可直接映射到我方**：投行承揽材料、客户开户资料、交易对手确认函等场景

#### 2. 数据源优先级规范

**来源**：`skills/comps-analysis/SKILL.md`

```
**ALWAYS follow this data source hierarchy:**
1. FIRST: Check for MCP data sources
2. DO NOT use web search if MCP available
3. ONLY if MCPs unavailable: Bloomberg Terminal, SEC EDGAR
4. NEVER use web search as primary source
```

**借鉴价值**：
- 明确的数据源优先级 = **可追溯 + 可审计**
- 每个 hardcoded input 必须有 cell comment 标注来源
- **可直接嵌入我方**：债券定价数据、企业财务数据、市场交易数据等场景

#### 3. 反模式（Anti-Patterns）清单

**来源**：`skills/pitch-deck/SKILL.md`

```markdown
### Anti-Pattern 1: Populating Data INTO Placeholder Boxes
**What happens:** Template has colored instruction boxes... Model replaces text but KEEPS THE COLORED BOX.
**Why it's wrong:** The colored box IS the placeholder.
**Recognition test:** If your populated slide has large colored rectangles filled with data...

### Anti-Pattern 2: Text-Based "Tables"
**What happens:** Model creates table-like content using | characters instead of actual table objects.
**Why it's wrong:** This is NOT a table.
**Recognition test:** If you're typing | characters...
```

**借鉴价值**：
- 将**常见错误模式**作为反面教材写入技能
- 每个反模式配 "Recognition test"（如何识别）+ "Correct approach"（正确做法）
- **可直接用于我方**：债券募集书常见错误、适当性匹配常见误操作、客户分析常见偏差

#### 4. 输出检查清单（Output Checklist）

**来源**：`skills/comps-analysis/SKILL.md`

```markdown
## Output Checklist
Before delivering a comp analysis, verify:
- [ ] All companies are truly comparable
- [ ] Data is from consistent time periods
- [ ] Formulas reference cells, not hardcoded values
- [ ] All hard-coded input cells have comments with source
- [ ] Statistics include at least 5 metrics (Max, 75th, Med, 25th, Min)
- [ ] Sanity checks pass (margins logical, multiples reasonable)
- [ ] Date stamp is current ("As of [Date]")
```

**借鉴价值**：
- 交付前的**强制性自检清单**
- 可嵌入我方动作模型的"验收标准"环节
- **建议**：每个规定动作配一个 Output Checklist

### 4.2 中优先级（需适配后使用）

#### 5. 子代理编排模式（callable_agents）

**来源**：`managed-agent-cookbooks/*/agent.yaml`

```yaml
callable_agents:
  - { manifest: ./subagents/researcher.yaml }   # 只读
  - { manifest: ./subagents/modeler.yaml }      # 计算
  - { manifest: ./subagents/deck-writer.yaml }  # 唯一写权限
```

**借鉴价值**：
- 将复杂任务拆分为**专用子代理**，各司其职
- 通过 `handoff_request` 事件进行代理间通信
- **需适配**：我方底座层需支持多智能体编排协议（MCP/A2A 或自研）

#### 6. 部署脚本（deploy-managed-agent.sh）

**来源**：`scripts/deploy-managed-agent.sh`

```bash
# 一键部署流程：
# 1. 解析 agent.yaml（YAML → JSON）
# 2. 上传 skills（zip → /v1/skills）
# 3. 递归创建子代理（POST /v1/agents）
# 4. 创建编排器代理（引用子代理 ID）
# 5. 输出 agent ID + console URL
```

**借鉴价值**：
- 从代码到运行实例的**自动化部署流水线**
- 包含 dry-run 模式（--dry-run）用于验证
- **需适配**：我方需开发类似的"模型包 → 运行实例"部署脚本

#### 7. 校验工具链（check.py + validate.py）

**来源**：`scripts/check.py`

```python
# 校验内容：
# 1. 每个 manifest 的语法正确性
# 2. system.file / skills.path / callable_agents.manifest 引用可解析
# 3. agent-plugins/<slug>/skills/ 与 vertical-plugins/ 源文件无漂移
# 4. 预提交钩子自动 bump 版本号
```

**借鉴价值**：
- **自动化质量门禁**：提交前自动校验引用完整性、版本一致性
- **漂移检测**：确保 bundle 与 source 同步
- **需适配**：开发我方版 check.py，校验业务模型的交叉引用、禁用词、三句话法合规

### 4.3 低优先级（参考思路）

#### 8. Partner-built 插件模式

LSEG、S&P Global 作为第三方贡献 skills，通过 `.mcp.json` 接入各自数据源。

**借鉴思路**：我方合作券商、数据供应商（Wind、同花顺）可按此模式贡献垂直技能。

#### 9. Microsoft 365 集成

`claude-for-msft-365-install/` 提供 Excel/PowerPoint/Word/Outlook 插件的管理员工具。

**借鉴思路**：我方工作台若需集成 Office 套件，可参考其 manifest 生成和 Azure AD 配置流程。

---

## 五、对我方智能体建设的具体建议

### 5.1 立即行动（本周可落地）

| 行动项 | 具体内容 | 负责人 |
|--------|---------|--------|
| **引入反模式清单** | 在债券发行、定增、资管产品销售的动作模型中，添加"常见错误模式"章节 | 模型设计师 |
| **输出检查清单标准化** | 每个规定动作配一个 Output Checklist（5-10项），作为交付前强制自检 | 模型设计师 |
| **数据源优先级规范** | 在涉及外部数据的技能中（债券定价、企业分析），明确 MCP/内部系统/公开数据的优先级 | 技术团队 |
| **CRITICAL 标记规范** | 在 SKILL.md 中，用 ⚠️ 标记不可违背的规则（合规红线、质量红线） | 模型设计师 |

### 5.2 短期规划（1个月内）

| 行动项 | 具体内容 | 依赖 |
|--------|---------|------|
| **开发 check.py 工具** | 自动化校验：引用完整性、禁用词检查、三句话法合规、版本漂移检测 | 开发团队 |
| **评估 MCP 兼容性** | 技术团队评估底座是否引入 MCP 作为数据连接标准 | 技术团队 |
| **设计子代理分层** | 参考 GL Reconciler 的安全分层，设计"读-算-写"分离的代理架构 | 架构师 |
| **翻译适配关键技能** | 将 pitch-deck、comps-analysis、earnings-analysis 等技能翻译为中文并适配国内监管要求 | 业务专家 |

### 5.3 中期规划（3个月内）

| 行动项 | 具体内容 | 依赖 |
|--------|---------|------|
| **建立 Partner-built 机制** | 设计第三方（数据供应商、合作券商）贡献 skills 的标准和接入流程 | 产品团队 |
| **开发部署脚本** | 实现从"模型包（JSON + Markdown）"到"运行实例"的一键部署 | 开发团队 |
| **集成 Office 插件** | 评估 Excel/PowerPoint 自动化生成的需求（Pitch Deck、CIM、IC Memo） | 产品团队 |

---

## 六、关键文件速查

| 文件路径 | 内容 | 借鉴价值 |
|---------|------|---------|
| `plugins/vertical-plugins/financial-analysis/skills/comps-analysis/SKILL.md` | 可比公司分析完整规范 | ⭐⭐⭐ 数据源优先级、公式规范、检查清单 |
| `plugins/vertical-plugins/investment-banking/skills/pitch-deck/SKILL.md` | Pitch Deck 模板填充规范 | ⭐⭐⭐ 反模式清单、PPT 格式化标准 |
| `plugins/vertical-plugins/private-equity/skills/ic-memo/SKILL.md` | 投委会备忘录结构 | ⭐⭐⭐ 结构化文档框架、风险披露规范 |
| `managed-agent-cookbooks/gl-reconciler/README.md` | 安全分层设计 | ⭐⭐⭐ 不可信文档隔离、读写分离 |
| `plugins/vertical-plugins/fund-admin/skills/gl-recon/SKILL.md` | 总账对账流程 | ⭐⭐ 匹配逻辑、差异分类、输出规范 |
| `plugins/vertical-plugins/wealth-management/skills/client-review/SKILL.md` | 客户回顾准备 | ⭐⭐ 会议框架、绩效归因、行动项 |
| `scripts/deploy-managed-agent.sh` | 部署脚本 | ⭐⭐ 自动化部署、dry-run 模式 |
| `scripts/check.py` | 校验工具 | ⭐⭐ 引用校验、漂移检测、版本管理 |
| `plugins/vertical-plugins/financial-analysis/.mcp.json` | MCP 连接器配置 | ⭐⭐ 数据源标准化、声明式配置 |

---

## 七、结论

Anthropic 的 financial-services 仓库是一份**高质量的金融智能体参考实现**，其核心价值在于：

1. **技能定义的工程化**：YAML frontmatter + markdown 指令 + 引用文件 + 检查清单，形成完整的"技能即代码"范式
2. **安全设计的分层化**：reader（只读）→ orchestrator（编排）→ resolver（写）的三层隔离，尤其适用于处理不可信外部文档
3. **数据连接的标准化**：MCP 协议统一对接 11 个金融数据提供商，声明式配置替代代码集成
4. **质量控制的自动化**：check.py + validate.py + 预提交钩子，形成从开发到部署的完整工具链

**对我方的最大启示**：
- 我们的**五步法 + 蒸馏智能体 + 规定动作**方法论在"业务理解深度"上优于 Anthropic（他们有流程但缺少业务目标蒸馏环节）
- 但在**工程化落地**上，Anthropic 领先一步（MCP 标准、部署脚本、校验工具链、安全分层）
- **建议策略**：方法论保持我方优势（五步法、三句话法、禁用词表），工程实现借鉴 Anthropic（MCP 兼容、子代理编排、自动化校验）

---

*报告生成时间：2026-06-30 10:50*  
*GitHub 镜像：https://github.com/tangwm88/financial-services*
