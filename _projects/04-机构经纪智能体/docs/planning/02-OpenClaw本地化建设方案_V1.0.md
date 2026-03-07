# 机构经纪智能体平台 - OpenClaw本地化建设开发方案

**方案版本：** V1.0  
**编制日期：** 2026年3月5日  
**技术路线：** 基于OpenClaw框架本地化部署  

---

## 一、OpenClaw本地化架构设计

### 1.1 架构全景

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OpenClaw Gateway (本地部署)                          │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                     会话管理 (Session Manager)                       │   │
│   │  - WebSocket连接管理  - 消息路由  - 状态保持  - 多轮对话上下文      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                     渠道接入层 (Channel Layer)                       │   │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│   │  │ 飞书     │  │ 企业微信 │  │ Web工作台│  │ API接入  │          │   │
│   │  │ Connector│  │ Connector│  │ Connector│  │ Endpoint │          │   │
│   │  └──────────┘  └──────────┘  └──────────┘  └──────────┘          │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│   ┌────────────────────────────────┴────────────────────────────────┐       │
│   │                    Agent Runtime (智能体运行时)                   │       │
│   │                                                                  │       │
│   │   ┌─────────────────────────────────────────────────────────┐   │       │
│   │   │           机构经纪智能体 (InstitutionBrokerageAgent)      │   │       │
│   │   │                                                          │   │       │
│   │   │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │   │       │
│   │   │   │ 协调官Node  │  │ 工具调用Node│  │ 记忆检索Node│    │   │       │
│   │   │   │ (Orchestrator)│ │ (Tool Call) │ │  (Memory)   │    │   │       │
│   │   │   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │   │       │
│   │   │          │                │                │            │   │       │
│   │   │          └────────────────┴────────────────┘            │   │       │
│   │   │                           │                             │   │       │
│   │   │                    ┌──────┴──────┐                     │   │       │
│   │   │                    │   Graph State│                     │   │       │
│   │   │                    │   (状态管理) │                     │   │       │
│   │   │                    └─────────────┘                     │   │       │
│   │   └─────────────────────────────────────────────────────────┘   │       │
│   │                                                                  │       │
│   └──────────────────────────────────────────────────────────────────┘       │
│                                    │                                         │
│   ┌────────────────────────────────┴────────────────────────────────┐       │
│   │                      Skills & Tools 扩展层                       │       │
│   │                                                                  │       │
│   │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │       │
│   │   │ 底座技能    │  │ 语料技能    │  │ 业务工具    │          │       │
│   │   │(Base Skill) │  │(CorpusSkill)│  │(Biz Tools)  │          │       │
│   │   │             │  │             │  │             │          │       │
│   │   │ • 语料查询  │  │ • 本地语料  │  │ • 开户申请  │          │       │
│   │   │ • 关系网络  │  │ • 联网舆情  │  │ • 交易查询  │          │       │
│   │   │ • 风控检查  │  │ • 语义搜索  │  │ • 客户画像  │          │       │
│   │   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │       │
│   │          │                │                │                  │       │
│   │          └────────────────┴────────────────┘                  │       │
│   │                           │                                   │       │
│   │                    ┌──────┴──────┐                           │       │
│   │                    │  Skill Registry│                          │       │
│   │                    │  (技能注册中心) │                          │       │
│   │                    └─────────────┘                           │       │
│   └────────────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         基础设施层 (Infrastructure)                          │
│                                                                              │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│   │  PostgreSQL  │  │    Redis     │  │    MinIO     │  │   Milvus     │  │
│   │  (业务数据)   │  │  (会话缓存)   │  │  (文件存储)   │  │ (向量检索)   │  │
│   └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                     底座大模型 (公司内部)                            │   │
│   │         通过OpenClaw Tool机制调用公司自动驾驶大模型底座              │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 OpenClaw核心组件映射

| OpenClaw组件 | 机构经纪智能体对应 | 说明 |
|-------------|-------------------|------|
| **Gateway** | 统一接入网关 | 管理飞书/企微/Web多渠道接入 |
| **Session** | 对话上下文管理 | 维护多轮对话状态和用户记忆 |
| **Agent** | 机构经纪智能体 | 核心业务逻辑，LangGraph编排 |
| **Skill** | 底座/语料/业务技能 | 可插拔的能力模块 |
| **Tool** | 外部API调用 | 底座接口、数据库查询等 |
| **Channel** | 客户端连接器 | 飞书/企微/Web适配器 |

---

## 二、OpenClaw本地化部署方案

### 2.1 部署架构

```yaml
# docker-compose.openclaw.yml
version: '3.8'

services:
  # OpenClaw Gateway
  openclaw-gateway:
    image: openclaw/gateway:latest
    container_name: openclaw-gateway
    ports:
      - "8080:8080"      # HTTP API
      - "8081:8081"      # WebSocket
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/openclaw
      - REDIS_URL=redis://redis:6379
      - SESSION_STORE=redis
      - LOG_LEVEL=info
    volumes:
      - ./config:/app/config
      - ./skills:/app/skills
    depends_on:
      - postgres
      - redis
    networks:
      - openclaw-net

  # Agent Runtime
  agent-runtime:
    image: openclaw/agent-runtime:latest
    container_name: agent-runtime
    environment:
      - GATEWAY_URL=http://openclaw-gateway:8080
      - MODEL_ENDPOINT=http://vllm:8000
      - BASE_ADAPTER_URL=http://base-adapter:8080
    volumes:
      - ./agents:/app/agents
      - ./skills:/app/skills
    depends_on:
      - openclaw-gateway
      - vllm
    networks:
      - openclaw-net

  # 底座适配服务
  base-adapter:
    image: institution-brokerage/base-adapter:latest
    container_name: base-adapter
    environment:
      - BASE_API_URL=https://base-api.company.com
      - CLIENT_CERT=/certs/client.crt
      - CLIENT_KEY=/certs/client.key
    volumes:
      - ./certs:/certs
    networks:
      - openclaw-net

  # vLLM推理服务
  vllm:
    image: vllm/vllm-openai:latest
    container_name: vllm
    runtime: nvidia
    environment:
      - CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
    command: >
      --model /models/qwen-72b-instruct
      --tensor-parallel-size 8
      --gpu-memory-utilization 0.85
      --max-num-seqs 256
    volumes:
      - /data/models:/models
    networks:
      - openclaw-net

  # 数据库
  postgres:
    image: postgres:15
    container_name: openclaw-postgres
    environment:
      - POSTGRES_USER=openclaw
      - POSTGRES_PASSWORD=secure_password
      - POSTGRES_DB=openclaw
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - openclaw-net

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: openclaw-redis
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    networks:
      - openclaw-net

  # Milvus向量库
  milvus:
    image: milvusdb/milvus:latest
    container_name: openclaw-milvus
    environment:
      - ETCD_ENDPOINTS=etcd:2379
      - MINIO_ADDRESS=minio:9000
    depends_on:
      - etcd
      - minio
    networks:
      - openclaw-net

volumes:
  postgres-data:
  redis-data:

networks:
  openclaw-net:
    driver: bridge
```

### 2.2 配置文件

```yaml
# config/openclaw.yaml
openclaw:
  # 网关配置
  gateway:
    host: 0.0.0.0
    port: 8080
    websocket_port: 8081
    
    # 渠道配置
    channels:
      feishu:
        enabled: true
        app_id: ${FEISHU_APP_ID}
        app_secret: ${FEISHU_APP_SECRET}
        encrypt_key: ${FEISHU_ENCRYPT_KEY}
        
      wecom:
        enabled: true
        corp_id: ${WECOM_CORP_ID}
        agent_id: ${WECOM_AGENT_ID}
        secret: ${WECOM_SECRET}
        
      web:
        enabled: true
        cors_origins: ["https://brokerage.company.com"]

  # Agent配置
  agent:
    default_agent: institution_brokerage
    agents_dir: /app/agents
    
    # 机构经纪智能体配置
    institution_brokerage:
      name: "机构经纪智能体"
      description: "机构经纪业务AI助手"
      model: local/qwen-72b
      skills:
        - base_skill
        - corpus_skill
        - business_skill
      memory:
        type: hierarchical
        session_ttl: 3600
        working_memory_limit: 10

  # 技能配置
  skills:
    base_skill:
      name: "底座能力技能"
      module: skills.base_adapter
      tools:
        - query_institution
        - check_risk
        - monitor_sentiment
        
    corpus_skill:
      name: "语料检索技能"
      module: skills.corpus_retrieval
      tools:
        - semantic_search
        - graph_query
        - news_monitor
        
    business_skill:
      name: "业务操作技能"
      module: skills.business_ops
      tools:
        - create_account_application
        - query_trading_status
        - generate_report

  # 模型配置
  models:
    local/qwen-72b:
      type: vllm
      endpoint: http://vllm:8000
      temperature: 0.7
      max_tokens: 2048
      
    local/intent-classifier:
      type: vllm
      endpoint: http://vllm:8000
      temperature: 0.1
      max_tokens: 100
```

---

## 三、机构经纪智能体Agent实现

### 3.1 Agent结构

```
agents/
└── institution_brokerage/
    ├── __init__.py
    ├── agent.py              # Agent主类
    ├── graph.py              # LangGraph状态图
    ├── nodes/
    │   ├── __init__.py
    │   ├── coordinator.py    # 协调官节点
    │   ├── prospector.py     # 客户开发员节点
    │   ├── onboarding.py     # 开户专员节点
    │   ├── trading.py        # 交易服务员节点
    │   └── service.py        # 客户关怀员节点
    ├── memory/
    │   ├── __init__.py
    │   ├── session_memory.py # 会话记忆
    │   └── long_term_memory.py # 长期记忆
    └── prompts/
        ├── coordinator.yaml  # 协调官提示词
        ├── prospector.yaml   # 客户开发员提示词
        └── ...
```

### 3.2 Agent主类实现

```python
# agents/institution_brokerage/agent.py
from openclaw.agent import BaseAgent
from openclaw.memory import HierarchicalMemory
from .graph import build_institution_brokerage_graph

class InstitutionBrokerageAgent(BaseAgent):
    """机构经纪智能体 - OpenClaw Agent实现"""
    
    def __init__(self, config):
        super().__init__(config)
        
        # 初始化记忆系统
        self.memory = HierarchicalMemory(
            session_store=config.session_store,
            vector_store=config.vector_store,
            graph_store=config.graph_store
        )
        
        # 构建LangGraph状态图
        self.graph = build_institution_brokerage_graph(
            llm=self.llm,
            skills=self.skills,
            memory=self.memory
        )
        
        # 加载提示词
        self.prompts = self._load_prompts()
    
    async def invoke(self, message: dict, context: dict) -> dict:
        """处理用户消息"""
        
        # 构建初始状态
        state = {
            "input": message["content"],
            "user_id": context["user_id"],
            "session_id": context["session_id"],
            "conversation_id": context["conversation_id"],
            "history": await self.memory.get_session_history(context["session_id"]),
            "context": {},
            "next": "coordinator"
        }
        
        # 执行状态图
        result = await self.graph.ainvoke(state)
        
        # 保存会话记忆
        await self.memory.save_turn(
            session_id=context["session_id"],
            user_input=message["content"],
            agent_output=result["output"]
        )
        
        return {
            "content": result["output"],
            "cards": result.get("cards", []),
            "actions": result.get("actions", []),
            "suggestions": result.get("suggestions", [])
        }
```

### 3.3 LangGraph状态图

```python
# agents/institution_brokerage/graph.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class AgentState(TypedDict):
    """智能体状态定义"""
    input: str
    user_id: str
    session_id: str
    conversation_id: str
    history: list
    context: dict
    intent: str = None
    current_agent: str = None
    output: str = None
    cards: list = []
    actions: list = []
    next: str

def build_institution_brokerage_graph(llm, skills, memory):
    """构建机构经纪智能体状态图"""
    
    workflow = StateGraph(AgentState)
    
    # 添加节点
    workflow.add_node("coordinator", CoordinatorNode(llm, skills, memory))
    workflow.add_node("prospector", ProspectorNode(llm, skills, memory))
    workflow.add_node("onboarding", OnboardingNode(llm, skills, memory))
    workflow.add_node("trading", TradingNode(llm, skills, memory))
    workflow.add_node("service", ServiceNode(llm, skills, memory))
    workflow.add_node("tool_call", ToolCallNode(skills))
    
    # 协调官路由逻辑
    def route_from_coordinator(state: AgentState) -> str:
        intent = state.get("intent")
        
        routing_map = {
            "introduce_customer": "prospector",
            "open_account": "onboarding",
            "trading_service": "trading",
            "customer_service": "service",
            "need_tool": "tool_call",
            "escalate": END
        }
        
        return routing_map.get(intent, "coordinator")
    
    # 添加条件边
    workflow.add_conditional_edges(
        "coordinator",
        route_from_coordinator,
        {
            "prospector": "prospector",
            "onboarding": "onboarding",
            "trading": "trading",
            "service": "service",
            "tool_call": "tool_call",
            END: END
        }
    )
    
    # 各Agent完成后返回协调官
    for node in ["prospector", "onboarding", "trading", "service"]:
        workflow.add_edge(node, "coordinator")
    
    # 工具调用后返回
    workflow.add_edge("tool_call", "coordinator")
    
    # 设置入口
    workflow.set_entry_point("coordinator")
    
    return workflow.compile()
```

---

## 四、底座对接Skill实现

### 4.1 Skill结构

```python
# skills/base_adapter/skill.py
from openclaw.skill import BaseSkill, tool

class BaseAdapterSkill(BaseSkill):
    """底座能力适配技能"""
    
    def __init__(self, config):
        super().__init__(config)
        self.base_client = BaseModelSDK(
            endpoint=config["base_api_url"],
            cert=config["client_cert"],
            key=config["client_key"]
        )
    
    @tool(name="query_institution", description="查询机构全景画像")
    async def query_institution(
        self,
        institution_name: str,
        fields: list = None
    ) -> dict:
        """查询机构信息"""
        
        result = await self.base_client.call(
            endpoint="/corpus/v1/institution/query",
            payload={
                "name": institution_name,
                "fields": fields or ["basic", "financial", "risk"]
            }
        )
        
        return {
            "name": result["name"],
            "type": result["type"],
            "scale": result["aum"],
            "risk_level": result["risk_level"],
            "related_parties": result["related"],
            "recent_news": result["news"][:5]
        }
    
    @tool(name="check_risk", description="风控合规检查")
    async def check_risk(
        self,
        institution_id: str,
        check_type: str = "account_opening"
    ) -> dict:
        """风控检查"""
        
        result = await self.base_client.call(
            endpoint="/risk/v1/check",
            payload={
                "institution_id": institution_id,
                "check_type": check_type
            }
        )
        
        return {
            "passed": result["passed"],
            "risk_score": result["score"],
            "warnings": result.get("warnings", []),
            "required_actions": result.get("actions", [])
        }
    
    @tool(name="monitor_sentiment", description="舆情监控")
    async def monitor_sentiment(
        self,
        institution_ids: list,
        alert_threshold: float = 0.7
    ) -> dict:
        """监控舆情"""
        
        return await self.base_client.call(
            endpoint="/corpus/v1/sentiment/monitor",
            payload={
                "institution_ids": institution_ids,
                "alert_threshold": alert_threshold
            }
        )
```

### 4.2 Skill注册

```yaml
# skills/base_adapter/skill.yaml
name: base_adapter
version: 1.0.0
description: 公司自动驾驶大模型底座能力适配

config:
  base_api_url: ${BASE_API_URL}
  client_cert: /certs/client.crt
  client_key: /certs/client.key
  timeout: 30

tools:
  - name: query_institution
    description: 查询机构全景画像
    parameters:
      - name: institution_name
        type: string
        required: true
      - name: fields
        type: array
        required: false
        
  - name: check_risk
    description: 风控合规检查
    parameters:
      - name: institution_id
        type: string
        required: true
      - name: check_type
        type: string
        required: false
        default: account_opening
        
  - name: monitor_sentiment
    description: 舆情监控
    parameters:
      - name: institution_ids
        type: array
        required: true
      - name: alert_threshold
        type: number
        required: false
        default: 0.7
```

---

## 五、语料检索Skill实现

### 5.1 本地语料Skill

```python
# skills/corpus_retrieval/skill.py
from openclaw.skill import BaseSkill, tool

class CorpusRetrievalSkill(BaseSkill):
    """语料检索技能"""
    
    def __init__(self, config):
        super().__init__(config)
        
        # 本地向量库
        self.vector_store = MilvusClient(
            host=config["milvus_host"],
            collection="local_corpus"
        )
        
        # 图数据库
        self.graph_store = Neo4jClient(
            uri=config["neo4j_uri"],
            auth=(config["neo4j_user"], config["neo4j_password"])
        )
        
        # Embedding模型
        self.embedder = LocalEmbedder(
            endpoint=config["embedding_endpoint"]
        )
    
    @tool(name="semantic_search", description="语义检索本地语料")
    async def semantic_search(
        self,
        query: str,
        top_k: int = 5,
        filters: dict = None
    ) -> list:
        """语义搜索"""
        
        # 查询向量化
        query_vector = await self.embedder.encode(query)
        
        # 向量检索
        results = await self.vector_store.search(
            vectors=[query_vector],
            top_k=top_k,
            filter=filters
        )
        
        return [
            {
                "content": r["entity"]["content"],
                "source": r["entity"]["source"],
                "score": r["distance"],
                "metadata": r["entity"]["metadata"]
            }
            for r in results
        ]
    
    @tool(name="graph_query", description="图数据库关系查询")
    async def graph_query(
        self,
        entity_name: str,
        relation_types: list = None
    ) -> dict:
        """关系网络查询"""
        
        cypher = """
        MATCH (e:Entity {name: $name})-[r]-(related)
        WHERE $relation_types IS NULL OR type(r) IN $relation_types
        RETURN e, r, related
        LIMIT 20
        """
        
        result = await self.graph_store.run(cypher, {
            "name": entity_name,
            "relation_types": relation_types
        })
        
        return self._format_graph_result(result)
```

---

## 六、客户端Channel实现

### 6.1 飞书Channel

```python
# channels/feishu/channel.py
from openclaw.channel import BaseChannel
from openclaw.message import Message, CardMessage

class FeishuChannel(BaseChannel):
    """飞书渠道适配器"""
    
    def __init__(self, config):
        super().__init__(config)
        self.app_id = config["app_id"]
        self.app_secret = config["app_secret"]
        self.client = FeishuClient(
            app_id=self.app_id,
            app_secret=self.app_secret
        )
    
    async def handle_webhook(self, request: dict) -> None:
        """处理飞书Webhook回调"""
        
        event_type = request.get("header", {}).get("event_type")
        
        if event_type == "im.message.receive_v1":
            message = request["event"]["message"]
            
            # 转换为OpenClaw消息格式
            oc_message = Message(
                channel="feishu",
                user_id=message["sender"]["sender_id"]["user_id"],
                chat_id=message["chat_id"],
                content=self._extract_content(message),
                message_type=message["message_type"]
            )
            
            # 发送到Agent处理
            response = await self.agent.invoke(oc_message)
            
            # 渲染飞书卡片回复
            await self.send_response(message["chat_id"], response)
    
    async def send_response(self, chat_id: str, response: dict) -> None:
        """发送飞书卡片消息"""
        
        if response.get("cards"):
            # 发送交互卡片
            card = self._build_feishu_card(response)
            await self.client.send_card(chat_id, card)
        else:
            # 发送文本消息
            await self.client.send_text(chat_id, response["content"])
    
    def _build_feishu_card(self, response: dict) -> dict:
        """构建飞书卡片"""
        
        card = {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": "📋 今日重点工作"},
                "template": "blue"
            },
            "elements": []
        }
        
        # 添加卡片内容
        for card_item in response["cards"]:
            if card_item["type"] == "business_nav":
                card["elements"].extend(self._render_nav_card(card_item))
            elif card_item["type"] == "task_list":
                card["elements"].extend(self._render_task_card(card_item))
        
        # 添加操作按钮
        if response.get("actions"):
            card["elements"].append({
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {"tag": "plain_text", "content": action["label"]},
                        "type": "primary" if action.get("primary") else "default",
                        "value": action["value"]
                    }
                    for action in response["actions"]
                ]
            })
        
        return card
```

### 6.2 Web Channel

```python
# channels/web/channel.py
from openclaw.channel import BaseChannel
from fastapi import WebSocket

class WebChannel(BaseChannel):
    """Web工作台渠道"""
    
    def __init__(self, config):
        super().__init__(config)
        self.active_connections: dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """建立WebSocket连接"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        
        # 发送欢迎消息
        await self.send_message(session_id, {
            "type": "welcome",
            "content": "欢迎使用机构经纪智能体工作台"
        })
    
    async def handle_message(self, session_id: str, data: dict):
        """处理WebSocket消息"""
        
        message = Message(
            channel="web",
            user_id=data["user_id"],
            session_id=session_id,
            content=data["content"],
            message_type="text"
        )
        
        # 发送到Agent
        response = await self.agent.invoke(message)
        
        # 发送响应
        await self.send_message(session_id, {
            "type": "agent_response",
            "content": response["content"],
            "cards": response.get("cards", []),
            "actions": response.get("actions", [])
        })
    
    async def send_message(self, session_id: str, message: dict):
        """发送WebSocket消息"""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_json(message)
```

---

## 七、部署与运维

### 7.1 一键部署脚本

```bash
#!/bin/bash
# deploy.sh - OpenClaw本地化部署脚本

echo "=== OpenClaw机构经纪智能体平台部署 ==="

# 1. 环境检查
echo "[1/5] 检查环境..."
docker --version || exit 1
nvidia-smi || echo "Warning: GPU未检测到"

# 2. 创建目录
echo "[2/5] 创建目录结构..."
mkdir -p /opt/openclaw/{config,skills,agents,certs,data}

# 3. 拷贝配置
echo "[3/5] 拷贝配置文件..."
cp config/openclaw.yaml /opt/openclaw/config/
cp -r skills/* /opt/openclaw/skills/
cp -r agents/* /opt/openclaw/agents/

# 4. 启动服务
echo "[4/5] 启动服务..."
cd /opt/openclaw
docker-compose -f docker-compose.openclaw.yml up -d

# 5. 健康检查
echo "[5/5] 健康检查..."
sleep 10
curl -f http://localhost:8080/health || exit 1

echo "=== 部署完成 ==="
echo "Gateway: http://localhost:8080"
echo "WebSocket: ws://localhost:8081"
```

### 7.2 监控指标

```yaml
# monitoring/prometheus.yml
scrape_configs:
  - job_name: 'openclaw-gateway'
    static_configs:
      - targets: ['openclaw-gateway:8080']
    metrics_path: /metrics
    
  - job_name: 'agent-runtime'
    static_configs:
      - targets: ['agent-runtime:8080']
      
  - job_name: 'vllm'
    static_configs:
      - targets: ['vllm:8000']
```

---

## 八、总结

### OpenClaw本地化方案优势

| 优势 | 说明 |
|------|------|
| **标准化** | 基于OpenClaw框架，遵循社区最佳实践 |
| **可扩展** | Skill/Tool机制，能力模块即插即用 |
| **易维护** | 统一配置管理，容器化部署 |
| **本地化** | 完全内网部署，数据不出域 |
| **底座友好** | 通过Skill机制无缝对接公司底座 |

### 实施步骤

1. **Week 1-2**: OpenClaw基础环境部署
2. **Week 3-4**: 底座Skill开发与测试
3. **Week 5-6**: 机构经纪Agent开发
4. **Week 7-8**: 多渠道Channel集成
5. **Week 9-10**: 语料系统对接
6. **Week 11-12**: 试点与优化

---

**文档版本：** V1.0  
**编制日期：** 2026年3月5日  
**技术栈：** OpenClaw + LangGraph + vLLM + 底座SDK
