# Claude Code Coordinator（协调器）模式详细分析

> 分析时间：2026-03-31  
> 源代码：https://github.com/instructkr/claude-code  
> 核心文件：`src/coordinator/coordinatorMode.ts`

---

## 一、Coordinator模式概述

### 1.1 什么是Coordinator模式

Coordinator模式是Claude Code的一种**多智能体编排架构**，它引入了一个"协调器"角色，负责：
- 接收用户指令
- 分解任务并分派给多个Worker（工作智能体）
- 协调Worker之间的协作
- 合成结果并回复用户

### 1.2 核心概念对比

| 概念 | 说明 | 类比（证券公司场景） |
|------|------|---------------------|
| **Coordinator** | 协调器，负责任务分解和Worker管理 | 业务支持中心（组织者） |
| **Worker** | 执行具体任务的子智能体 | 各专业线数字员工 |
| **Agent** | 通过AgentTool生成的智能体实例 | 具体执行单元 |
| **Team** | 一组协作的Worker集合 | 项目工作组 |

---

## 二、技术实现详解

### 2.1 启动与检测

```typescript
// 环境变量控制
CLAUDE_CODE_COORDINATOR_MODE=1

// 运行时检测
export function isCoordinatorMode(): boolean {
  if (feature('COORDINATOR_MODE')) {
    return isEnvTruthy(process.env.CLAUDE_CODE_COORDINATOR_MODE)
  }
  return false
}
```

**关键设计**：
- 使用Bun的`feature()`进行代码消除（未使用功能不会打包）
- 环境变量实时读取，无缓存
- 支持会话模式切换（coordinator ↔ normal）

### 2.2 会话模式持久化

```typescript
export function matchSessionMode(
  sessionMode: 'coordinator' | 'normal' | undefined,
): string | undefined {
  const currentIsCoordinator = isCoordinatorMode()
  const sessionIsCoordinator = sessionMode === 'coordinator'

  if (currentIsCoordinator === sessionIsCoordinator) {
    return undefined  // 模式一致，无需切换
  }

  // 动态切换环境变量
  if (sessionIsCoordinator) {
    process.env.CLAUDE_CODE_COORDINATOR_MODE = '1'
  } else {
    delete process.env.CLAUDE_CODE_COORDINATOR_MODE
  }

  return sessionIsCoordinator 
    ? 'Entered coordinator mode to match resumed session.'
    : 'Exited coordinator mode to match resumed session.'
}
```

**应用场景**：
- 恢复会话时自动匹配之前的模式
- 支持会话间模式切换
- 记录切换事件用于分析

---

## 三、Coordinator工具集

### 3.1 Coordinator可用工具（白名单机制）

```typescript
export const COORDINATOR_MODE_ALLOWED_TOOLS = new Set([
  AGENT_TOOL_NAME,        // 生成Worker
  TASK_STOP_TOOL_NAME,    // 停止任务
  SEND_MESSAGE_TOOL_NAME, // 向Worker发送消息
  SYNTHETIC_OUTPUT_TOOL_NAME, // 合成输出
])
```

**设计原则**：
- Coordinator只负责**编排**，不直接执行
- 所有实际工作都通过AgentTool分派给Worker
- 严格限制工具权限，避免Coordinator"越权"

### 3.2 Worker可用工具

```typescript
export const ASYNC_AGENT_ALLOWED_TOOLS = new Set([
  FILE_READ_TOOL_NAME,    // 文件读取
  WEB_SEARCH_TOOL_NAME,   // 网络搜索
  TODO_WRITE_TOOL_NAME,   // 待办事项
  GREP_TOOL_NAME,         // 代码搜索
  WEB_FETCH_TOOL_NAME,    // 网页获取
  GLOB_TOOL_NAME,         // 文件匹配
  ...SHELL_TOOL_NAMES,    // Shell命令
  FILE_EDIT_TOOL_NAME,    // 文件编辑
  FILE_WRITE_TOOL_NAME,   // 文件写入
  NOTEBOOK_EDIT_TOOL_NAME,// 笔记本编辑
  SKILL_TOOL_NAME,        // 技能调用
  SYNTHETIC_OUTPUT_TOOL_NAME, // 合成输出
  TOOL_SEARCH_TOOL_NAME,  // 工具搜索
  ENTER_WORKTREE_TOOL_NAME, // 进入工作区
  EXIT_WORKTREE_TOOL_NAME,  // 退出工作区
])
```

**Worker禁用工具**：
- `AgentTool`：防止递归生成（嵌套Agent）
- `TaskStopTool`：需要主线程状态
- `AskUserQuestionTool`：Coordinator负责交互
- `TaskOutputTool`：防止递归

### 3.3 内部Worker工具

```typescript
const INTERNAL_WORKER_TOOLS = new Set([
  TEAM_CREATE_TOOL_NAME,    // 创建团队
  TEAM_DELETE_TOOL_NAME,    // 删除团队
  SEND_MESSAGE_TOOL_NAME,   // 消息发送
  SYNTHETIC_OUTPUT_TOOL_NAME, // 合成输出
])
```

这些工具仅供系统内部使用，普通Worker无法调用。

---

## 四、Coordinator系统提示词

### 4.1 角色定义

```
You are Claude Code, an AI assistant that orchestrates software engineering 
tasks across multiple workers.

## 1. Your Role

You are a coordinator. Your job is to:
- Help the user achieve their goal
- Direct workers to research, implement and verify code changes
- Synthesize results and communicate with the user
- Answer questions directly when possible — don't delegate work that you 
  can handle without tools
```

### 4.2 核心工具说明

**AgentTool**：生成新Worker
```
- Spawn a new worker via AgentTool
- Use subagent_type 'worker'
- Workers execute autonomously
```

**SendMessageTool**：继续已有Worker
```
- Continue an existing worker via SendMessage
- Use the agent ID as the 'to' parameter
- Worker retains full context from previous run
```

**TaskStopTool**：停止Worker
```
- Stop a running worker by task_id
- Used when approach is wrong or requirements change
- Stopped workers can be continued via SendMessage
```

### 4.3 任务工作流（四阶段）

| 阶段 | 执行者 | 目的 |
|------|--------|------|
| **Research** | Workers（并行） | 调研代码库，理解问题 |
| **Synthesis** | Coordinator | 分析发现，制定实施方案 |
| **Implementation** | Workers | 按规范执行修改 |
| **Verification** | Workers | 验证修改有效性 |

### 4.4 并发策略

```
**Parallelism is your superpower. Workers are async. Launch independent 
workers concurrently whenever possible.**

并发规则：
- Read-only tasks（调研）→ 自由并行
- Write-heavy tasks（实现）→ 同一文件集合一次一个
- Verification → 可与Implementation并行（不同文件区域）
```

---

## 五、Worker通信机制

### 5.1 任务通知格式

Worker结果通过**用户角色消息**中的XML通知返回：

```xml
<task-notification>
  <task-id>{agentId}</task-id>
  <status>completed|failed|killed</status>
  <summary>{human-readable status summary}</summary>
  <result>{agent's final text response}</result>
  <usage>
    <total_tokens>N</total_tokens>
    <tool_uses>N</tool_uses>
    <duration_ms>N</duration_ms>
  </usage>
</task-notification>
```

### 5.2 通信示例

```
User: "修复auth模块的null pointer"

Coordinator:
  AgentTool({ 
    description: "Investigate auth bug", 
    subagent_type: "worker",
    prompt: "调研src/auth/目录，找出session处理中的null pointer..."
  })
  AgentTool({ 
    description: "Research auth tests", 
    subagent_type: "worker",
    prompt: "找出与auth相关的测试文件..."
  })
  
  "正在从两个角度调研，稍后汇报发现。"

User (task-notification):
  <task-id>agent-a1b</task-id>
  <status>completed</status>
  <result>Found null pointer in src/auth/validate.ts:42...</result>

Coordinator:
  SendMessageTool({
    to: "agent-a1b",
    message: "修复src/auth/validate.ts:42的null pointer..."
  })
```

---

## 六、Worker Prompt设计规范

### 6.1 Prompt必须自包含

**错误示例**：
```
"Based on your findings, fix the auth bug"
"The worker found an issue in the auth module. Please fix it."
```

**正确示例**：
```
"Fix the null pointer in src/auth/validate.ts:42. The user field on Session 
(src/auth/types.ts:15) is undefined when sessions expire but the token remains 
cached. Add a null check before user.id access — if null, return 401 with 
'Session expired'. Commit and report the hash."
```

### 6.2 Continue vs Spawn选择策略

| 场景 | 机制 | 原因 |
|------|------|------|
| 调研文件与编辑文件完全重叠 | **Continue** | Worker已有文件上下文 |
| 调研宽泛但实现聚焦 | **Spawn fresh** | 避免探索噪音，专注上下文 |
| 修正错误或延续工作 | **Continue** | Worker有错误上下文 |
| 验证另一个Worker的代码 | **Spawn fresh** |  fresh eyes，无实现偏见 |
| 完全不同任务 | **Spawn fresh** | 无可用上下文 |

### 6.3 Prompt组成要素

每个Prompt应包含：
1. **目的声明**："This research will inform a PR description..."
2. **具体文件路径和行号**：src/auth/validate.ts:42
3. **明确的完成标准**："Run tests, commit, report hash"
4. **上下文信息**：错误消息、类型定义等

---

## 七、权限控制机制

### 7.1 Coordinator权限处理器

```typescript
async function handleCoordinatorPermission(
  params: CoordinatorPermissionParams,
): Promise<PermissionDecision | null> {
  // 1. 先尝试Permission Hooks（快速、本地）
  const hookResult = await ctx.runHooks(...)
  if (hookResult) return hookResult

  // 2. 尝试Classifier（慢速、推理）
  const classifierResult = feature('BASH_CLASSIFIER')
    ? await ctx.tryClassifier(...)
    : null
  if (classifierResult) return classifierResult

  // 3. 都失败，返回null，进入交互式对话框
  return null
}
```

**权限检查流程**：
1. **Hooks**（快速）→ 本地规则匹配
2. **Classifier**（慢速）→ AI推理判断
3. **交互式对话框** → 人工确认

### 7.2 权限模式

Worker支持不同的权限模式：
- `plan`：plan模式，需要用户确认每一步
- `auto`：自动模式，直接执行

---

## 八、对证券公司AI建设的启示

### 8.1 架构映射

| Claude Code | 证券公司场景 |
|-------------|-------------|
| Coordinator | 业务支持中心（组织者） |
| Worker | 各专业线数字员工 |
| AgentTool | 能力调用接口 |
| SendMessage | 跨智能体消息通信 |
| TaskStop | 任务终止/熔断机制 |

### 8.2 机构经纪智能体Coordinator设计

```
机构经纪Coordinator（业务支持中心）
├── Worker: 客户开发员
│   ├── 工具: 客户画像查询、线索筛选、资质初筛
│   └── 权限: 只读（客户信息）
├── Worker: 开户专员
│   ├── 工具: 准入审核、协议生成、权限配置
│   └── 权限: 读写（开户相关）
├── Worker: 交易服务员
│   ├── 工具: 算法配置、订单执行、异常监控
│   └── 权限: 交易执行（需确认）
└── Worker: 客户关怀员
    ├── 工具: 舆情监控、风险预警、对账服务
    └── 权限: 只读（风控数据）
```

### 8.3 工作流程设计

**场景：新客户引入全流程**

```
用户（客户经理）: "我要引入某私募基金客户"

Coordinator（业务支持中心）:
  
  // Phase 1: Research（并行调研）
  AgentTool({
    to: "客户开发员",
    prompt: "查询该客户工商信息、历史交易记录、关联企业..."
  })
  AgentTool({
    to: "风控专员", 
    prompt: "评估该客户风险等级，查询舆情和监管记录..."
  })
  AgentTool({
    to: "合规专员",
    prompt: "确认该客户类型是否满足准入要求..."
  })
  
  "正在并行调研客户背景、风险评估、合规审查..."

// Workers返回调研结果

Coordinator（综合研判）:
  "客户准入评估完成：
   - 资质：符合私募基金准入标准
   - 风险：低风险等级，无负面舆情
   - 合规：需补充尽调材料清单"
  
  // Phase 2: Implementation
  AgentTool({
    to: "开户专员",
    prompt: "为客户生成开户材料清单：
             1. 补充尽调问卷
             2. 风险揭示书
             3. 适当性评估表
             生成材料包并推送至客户..."
  })
```

### 8.4 关键设计要点

**1. 工具白名单机制**
- Coordinator：只能调用AgentTool，不能直接接触业务系统
- Worker：根据角色分配工具权限
- 高风险操作（如交易执行）需人工确认

**2. 上下文隔离**
```typescript
// Worktree隔离模式
AgentTool({
  isolation: 'worktree',  // 创建临时工作区
  prompt: "在该隔离环境中处理客户数据..."
})
```

**3. 消息路由**
```typescript
// 跨智能体通信
SendMessageTool({
  to: "信用交易智能体",  // 转发至其他业务线
  message: "客户申请融资融券业务..."
})
```

**4. 任务监控与熔断**
```typescript
// 异常情况自动停止
TaskStopTool({ task_id: "agent-x7q" })
```

---

## 九、技术实现建议

### 9.1 会话模式管理

```typescript
// 会话启动时检测模式
const sessionMode = loadSessionMode()  // 'coordinator' | 'normal'
matchSessionMode(sessionMode)

// 模式持久化
saveMode(isCoordinatorMode() ? 'coordinator' : 'normal')
```

### 9.2 Worker工具过滤

```typescript
// 根据角色过滤可用工具
function filterToolsForAgent(
  allTools: Tools,
  agentRole: string
): Tools {
  const allowedTools = getAllowedToolsForRole(agentRole)
  return allTools.filter(tool => allowedTools.has(tool.name))
}
```

### 9.3 任务结果通知

```typescript
// Worker任务完成通知Coordinator
interface TaskNotification {
  taskId: string
  status: 'completed' | 'failed' | 'killed'
  summary: string
  result?: string
  usage: {
    totalTokens: number
    toolUses: number
    durationMs: number
  }
}
```

---

## 十、总结

Claude Code的Coordinator模式提供了一套完整的多智能体编排方案：

1. **角色分离**：Coordinator负责编排，Worker负责执行
2. **权限控制**：严格的工具白名单，高风险操作人工确认
3. **并发优化**：Read任务并行，Write任务串行
4. **上下文管理**：支持Continue（复用上下文）和Spawn（ fresh上下文）
5. **通信机制**：XML格式的任务通知，支持跨智能体消息

对于证券公司的AI建设，可以直接借鉴其：
- 业务支持中心作为Coordinator的设计
- 专业线数字员工作为Worker的分工
- 工具白名单的权限管控机制
- 任务分派和结果合成的流程

---

*报告生成时间：2026-03-31 20:25*  
*分析工具：Kimi Claw*  
*源代码：Claude Code (Anthropic)*
