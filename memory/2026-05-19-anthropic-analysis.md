# Anthropic financial-services 仓库分析报告

## 仓库概述

**来源**: https://github.com/anthropics/financial-services
**发布方**: Anthropic（Claude母公司）
**定位**: 金融服务行业智能体参考实现（投资银行、股票研究、私募股权、财富管理）
**发布时间**: 2025-2026年（持续更新）

**核心价值**: 这不是概念文档，是可直接安装使用的生产级智能体插件系统。覆盖8大金融垂直领域、11个命名Agent、50+ Skills、11个MCP数据连接器。

---

## 一、架构设计（可借鉴度：⭐⭐⭐⭐⭐）

### 1.1 四层架构

```
┌─ Agents（命名工作流智能体）        ← 投行Pitch Agent、财报Review Agent等
├─ Vertical Plugins（垂直技能包）     ← 按业务线打包的Skills + Commands
├─ Skills（领域能力单元）             ← 每个skill是一个markdown文件，含workflow
└─ Connectors（MCP数据连接器）        ← CapIQ、FactSet、S&P、Moody's等11个
```

**与我们的架构对比：**
| 维度 | Anthropic设计 | 我们公司设计 | 评估 |
|------|---------------|-------------|------|
| 分层 | Agent → Plugin → Skill → Connector | 底座大模型 → 八大应用智能体 | 底层逻辑一致，我们底座更宏大 |
| 编排 | Managed Agent API + Cowork插件 | 组织者智能体（圆桌会议） | **可借鉴其agent.yaml编排方式** |
| 连接 | MCP标准化（11个外部数据源） | 规划中 | **可直接复用MCP连接器清单** |
| 部署 | 两种模式（插件/API） | 未明确 | 可借鉴双模式思路 |

### 1.2 Agent编排机制（关键借鉴）

每个Agent的配置文件 `agent.yaml` 定义：
- **system prompt**: 角色定义（如"资深投行助理"）
- **tools**: 可调用的工具白名单（read/write/grep + MCP工具集）
- **skills**: 绑定的skill集合
- **callable_agents**: 可委托的子智能体（handoff_request机制）

**Pitch Agent示例**：
- 主Agent：负责整体工作流编排
- 子Agent：Researcher → Modeler → Deck-writer（只有writer有Write权限）
- **安全设计**：leaf worker（最底层）才有写权限，上层只读+调度

**对我们组织者智能体的借鉴：**
- 他们的"callable_agents"就是我们的"圆桌会议协同端"
- 他们的"security notes"（权限分层）对应我们的"监督式Agent"
- **建议**：给组织者智能体增加agent.yaml式编排配置，明确各子智能体权限边界

---

## 二、业务覆盖（可借鉴度：⭐⭐⭐⭐）

### 2.1 八大垂直领域

| 垂直领域 | 核心Skills | 我们公司对应业务线 |
|----------|-----------|-------------------|
| **Investment Banking** | CIM、Pitch Deck、Teaser、Merger Model、Deal Tracker | 投资银行智能体 ✅ |
| **Equity Research** | Earnings Review、Initiating Coverage、Model Update | 研究所智能体 ✅ |
| **Private Equity** | Deal Sourcing、DD Checklist、IC Memo、Portfolio Monitoring | 固收/资管（部分重叠） |
| **Wealth Management** | Client Review、Financial Plan、Rebalance、TLH | 财富管理智能体 ✅ |
| **Fund Admin** | GL Reconcile、Month-End Close、Statement Audit | 信用交易/中后台 |
| **Operations** | KYC Screener（文档解析+规则引擎） | 机构经纪/合规 |
| **Financial Analysis（核心）** | Comps、DCF、LBO、3-Statement、Excel Audit | 底座公共能力 |

**可直接复用的Skills（适配后）：**
- `comps-analysis`（可比公司分析）→ 投行/研究所通用
- `earnings-preview`（财报前瞻）→ 研究所可借鉴其"Bull/Base/Bear"三场景框架
- `kyc-rules` / `kyc-doc-parse` → 机构经纪/合规可直接借鉴
- `client-review` → 财富管理可借鉴其"会前准备+业绩回顾+话术要点"结构

### 2.2 命名Agent清单（10个）

| Agent | 功能 | 可借鉴度 |
|-------|------|----------|
| **Pitch Agent** | Comps→Precedents→LBO→Pitch Deck端到端 | ⭐⭐⭐⭐⭐ 投行可直接借鉴 |
| **Market Researcher** | 行业/主题→全景+竞品+标的选择 | ⭐⭐⭐⭐ 研究所/资管可用 |
| **Earnings Reviewer** | 财报电话会+公告→模型更新→报告草稿 | ⭐⭐⭐⭐⭐ 研究所直接复用 |
| **Model Builder** | DCF/LBO/三表/Comps→Excel实时模型 | ⭐⭐⭐⭐ 投行/研究所通用 |
| **Meeting Prep Agent** | 客户会前简报包自动生成 | ⭐⭐⭐⭐ 各业务线通用 |
| **GL Reconciler** | 发现差异→追溯根因→路由审批 | ⭐⭐⭐ 中后台可借鉴 |
| **KYC Screener** | 解析开户文档→规则引擎→标记缺口 | ⭐⭐⭐⭐ 机构经纪/合规可用 |
| **Month-End Closer** | 计提、滚动、差异说明 | ⭐⭐⭐ 中后台 |
| **Valuation Reviewer** | 接收GP包→跑估值模板→LP报告 | ⭐⭐ 资管可借鉴 |
| **Statement Auditor** | 审计LP报告→分发前检查 | ⭐⭐ 中后台 |

---

## 三、Skill定义方法（可借鉴度：⭐⭐⭐⭐⭐）

### 3.1 Skill文件结构

每个Skill是一个**独立markdown文件**，结构标准化：

```markdown
# Skill名称

description: 触发条件描述（自然语言）

## Workflow

### Step 1: [阶段名]
- 动作1
- 动作2

### Step 2: [阶段名]
- 动作1
- 动作2

## Important Notes
- 边界条件
- 安全提醒
- 输出标准
```

**与我们的"业务模型"定义对比：**
| 维度 | Anthropic Skill | 我们5月18日模型 |
|------|----------------|----------------|
| 定义方式 | markdown文件 | 口头/会议纪要定义 |
| 触发条件 | description字段（自然语言） | 未明确 |
| 工作流 | Step-by-step Workflow | "3-5个维度" |
| 质量检查 | Final Quality Checklist | 交叉验证（新定义） |
| 参考文件 | reference/子目录 | 未明确 |

**关键借鉴：**
1. **Skill文件标准化模板**：可以立即采用这种markdown格式，替代目前口头定义
2. **触发条件显性化**：每个skill的description=触发条件，大模型知道何时调用
3. **参考文件分离**：reference/子目录存放格式化标准、计算公式、XML参考等
4. **反模式检查**：明确列出"NEVER DO THESE"（如不要把数据dump进占位符框）

### 3.2 优秀Skill示例分析

**`earnings-preview`（财报前瞻）**：
- Step 1: Gather Context → Step 2: Key Metrics Framework → Step 3: Scenario Analysis → Step 4: Catalyst Checklist → Step 5: Output
- **三场景框架**：Bull/Base/Bear + 股价影响，可直接复用
- **行业差异化指标**：Tech(ARR/RPO)、Retail(同店销售)、Financials(NIM/信贷质量)

**`pitch-deck`（投行Pitch Deck制作）**：
- **Phase workflow**: Data Extraction → Content Mapping → Population → Validate→Fix→Repeat → Final Verification
- **反模式检查**：3个Critical Anti-Patterns（占位符误用、文本假表格、继承占位符配色）
- **验证清单**：17项Final Quality Checklist（数据准确性、内容映射、格式化、模板合规）
- **此skill的严谨度极高，可直接作为我们"方案生成模型"的参考**

---

## 四、MCP连接器（可借鉴度：⭐⭐⭐⭐⭐）

### 4.1 已集成数据源（11个）

| 供应商 | 类型 | MCP URL |
|--------|------|---------|
| CapIQ（S&P Capital IQ）| 公司数据/交易/财务 | mcp.kensho.com |
| FactSet | 金融数据终端 | mcp.factset.com |
| S&P Global | 研究/评级 | kfinance.kensho.com |
| Moody's | 信用评级 | api.moodys.com |
| Morningstar | 基金/股票数据 | mcp.morningstar.com |
| Daloopa | 财务模型数据 | mcp.daloopa.com |
| LSEG（原Refinitiv）| 债券/外汇/宏观 | api.analytics.lseg.com |
| PitchBook | PE/VC数据 | premium.mcp.pitchbook.com |
| MT Newswires | 新闻流 | vast-mcp.blueskyapi.com |
| Aiera | 财报会议转录 | mcp-pub.aiera.com |
| Chronograph | PE组合监控 | ai.chronograph.pe |

**对我们底座的直接借鉴：**
- 这些MCP URL可以直接纳入我们底座"统一语料"层的连接器规划
- 特别是CapIQ、FactSet、S&P Global、LSEG，是投行/研究的核心数据源
- 我们的"关系网络"设计可以借鉴其"数据连接器统一接入"模式

---

## 五、安全与合规设计（可借鉴度：⭐⭐⭐⭐⭐）

### 5.1 核心安全机制

| 机制 | Anthropic实现 | 我们当前状态 | 建议 |
|------|-------------|-----------|------|
| **Human-in-the-loop** | 每个Agent明确标注"Stop and surface for review"节点 | 监督式Agent设计 ✅ | **增加明确的"暂停点"定义** |
| **来源标注** | 每个数字标注[UNSOURCED]如果无法溯源 | 未明确 | **强制来源标注机制** |
| **权限分层** | 子Agent权限分离（writer-only有写权限） | 未明确 | **给数字员工增加权限分级** |
| **输出免责声明** | 每个文件开头声明"不构成投资建议" | 未明确 | **AI生成内容强制标识**（符合五部门新规） |
| **验证循环** | Validate→Fix→Repeat 3次循环后escalate | 交叉验证（新定义） | **结合使用：自动验证+人工升级** |

### 5.2 法律声明（可直接复用模板）

```
Nothing in this repository constitutes investment, legal, tax, or accounting advice. 
These agents draft analyst work product for review by a qualified professional. 
They do not make investment recommendations, execute transactions, bind risk, 
post to a ledger, or approve onboarding; every output is staged for human sign-off.
```

**这正好符合我们公司"监督式Agent"的定位。**

---

## 六、工程实践（可借鉴度：⭐⭐⭐⭐）

### 6.1 开发流程

| 实践 | 说明 |
|------|------|
| **文件驱动** | 全部用markdown+YAML，无构建步骤 |
| **Skill同步脚本** | `sync-agent-skills.py` 确保agent绑定的skill与vertical源文件一致 |
| **验证脚本** | `check.py` 检查所有manifest、交叉引用、skill漂移 |
| **版本管理** | `version_bump.py` + GitHub Actions自动验证 |
| **安全扫描** | `secret-scan.yml` 防止API key泄露 |

### 6.2 对我们工作流的借鉴

**建议立即引入：**
1. **Skill文件模板标准化**：每个业务模型一个markdown文件，统一格式
2. **交叉引用验证**：确保skill与agent、agent与底座之间的引用关系正确
3. **版本管理**：给每个业务模型增加版本号，追踪迭代
4. **格式化标准文件**：如`formatting-standards.md`、`calculation-standards.md`

---

## 七、与我们项目的战略契合度评估

### 7.1 高度契合点

| 维度 | 契合说明 |
|------|----------|
| **分层架构** | Agent+Skill分层与我们的"底座+八大应用"完全一致 |
| **Skill标准化** | 他们的skill=我们的"业务模型"，方法论天然契合 |
| **监督式Agent** | 他们的"human sign-off"=我们的"监督式执行" |
| **去术语化** | 他们的skill面向"业务小白"=我们的"质朴准确无歧义" |
| **模型即标准** | 他们的"skill文件=业务标准"=陶总"模型即标准，提示词即模型" |

### 7.2 我们可以做得更好的地方

| 维度 | Anthropic | 我们公司 | 优势方 |
|------|-----------|---------|--------|
| **底座定位** | 工具层（MCP连接+模型调用） | 公司级自动驾驶（预判驱动+关系网络） | **我们** ✅ |
| **组织重构** | 不涉及 | 三端角色+组织扁平化 | **我们** ✅ |
| **合规设计** | 免责声明+人工审批 | 监督式Agent+分级台账 | **我们** ✅ |
| **数据治理** | 外部连接器为主 | 200+指标统一治理+合同语料 | **我们** ✅ |
| **业务深度** | 通用金融workflow | 华创证券定制化业务场景 | **我们** ✅ |

### 7.3 我们应该直接复用的部分

**立即可用（改个名字就能用）：**
1. **MCP连接器清单**：11个数据源URL可直接纳入底座规划
2. **Skill文件模板**：markdown结构+workflow+step+notes，适用于我们所有业务模型
3. **验证清单模板**：Final Quality Checklist的17项检查点
4. **反模式清单**：3个Critical Anti-Patterns可直接翻译使用
5. **法律声明模板**：AI输出免责声明

**需要适配后使用：**
1. **10个命名Agent**：根据华创业务特点重命名和裁剪
2. **50+ Skills**：筛选与华创业务线匹配的，按5月18日"3-5维度"标准重写
3. **MCP Server部署**：需要内部化部署或接入现有数据源

**建议深入学习但暂不复制：**
1. **Managed Agent API编排**：等技术团队确认技术栈后再评估
2. **Cowork插件系统**：等E智通AI版本确定技术路线后再评估

---

## 八、行动建议

### 短期（本周，配合5月18日"一周为限"）

1. **给各条线提供Skill文件模板**
   - 基于Anthropic的markdown格式，制作华创版模板
   - 包含：description（触发条件）、Workflow（Step 1-5）、Important Notes、Final Quality Checklist

2. **将Anthropic的Skill清单作为参考对照表**
   - 投行条线：参考`pitch-agent`、`deal-tracker`、`merger-model`
   - 资管条线：参考`portfolio-monitoring`、`returns-analysis`
   - 研究所：参考`earnings-reviewer`、`market-researcher`
   - 零售/财富管理：参考`client-review`、`financial-plan`

3. **将MCP连接器清单纳入底座规划**
   - 戴豫升/林立：评估11个数据源的接入优先级

### 中期（配合630节点）

4. **建立Skill版本管理和验证流程**
   - 引入`check.py`式验证脚本
   - 每个Skill文件增加版本号
   - 交叉引用关系自动检查

5. **制作华创版"反模式清单"**
   - 翻译并定制Anthropic的3个Critical Anti-Patterns
   - 增加华创特有反模式（如"委托尽调"已被叫停）

6. **制定AI输出免责声明标准**
   - 所有数字员工/智能体输出强制附加免责声明
   - 符合五部门新规〔2026〕第9号要求

### 长期（2026Q3后）

7. **评估接入Anthropic开源生态**
   - 关注A2A协议进展（Anthropic是A2A发起方之一）
   - 评估Claude Managed Agent API与公司底座的集成可能性

---

## 九、关键结论

> **Anthropic这个仓库是目前全球最先进的金融AI智能体开源参考实现。**
> 
> 它验证了我们公司"底座+八大应用"架构的正确性，
> 提供了可直接复用的Skill模板和工程实践，
> 特别是在MCP连接、质量验证、反模式检查方面的成熟度远超我们当前水平。
> 
> **建议策略**："借其骨架，填我血肉"——采用其文件格式和工程方法，注入华创业务知识。

---

*分析完成时间：2026-05-19*
*分析者：Kimi Claw*
*来源：github.com/anthropics/financial-services 深度解析*
