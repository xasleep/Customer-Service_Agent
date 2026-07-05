# 电商全链路客服 AI Agent PRD

## 1. Executive Summary

本项目将 `demoAgent/demo_agent` 改造为一个面向买家的电商全链路自助客服 AI Agent。首版覆盖售前咨询、订单履约、物流查询、售后退款/退货/换货、投诉与风险转人工等基础场景。系统以 LangGraph `StateGraph` 作为核心状态机编排，以 LangChain 作为模型、工具和消息适配层；默认模型配置为 `opai-gpt5.4`，采用“规则优先、工具查询、模型润色、模板兜底”的策略。首版仅接入本地 mock 商品、订单、物流、售后政策和工单数据，保留 CLI 与 HTTP API 两个入口，目标是在本地可运行、可演示、可测试。

## 2. Problem Statement

### Who Has This Problem?

- 买家：需要在购买前后快速获得商品、订单、物流、退款、退货和投诉处理结果。
- 开发者：需要一个能体现 LangGraph 状态编排、工具调用、客服风控与多入口服务能力的 Python demo。
- 项目维护者：希望 `demo_agent` 不只是顺序式脚本，而是具备清晰状态流转和后续扩展空间的客服 Agent。

### What Is The Problem?

当前 `demo_agent` 已经具备 CLI、FastAPI、intent、RAG、tools、memory、compliance 等基础模块，但核心链路仍是顺序式 `Supervisor.chat()` 编排，业务域也偏通用客服 demo。它还没有形成一个明确的电商买家自助客服产品形态，无法清晰表达售前、订单、物流、售后的全链路处理能力。

### Why Is It Painful?

- 客服场景天然存在多意图、多步骤、风险分流和多轮上下文，顺序式编排后续扩展会变重。
- 如果没有明确的状态机节点，调试“当前走到哪一步、为什么转人工、调用了哪些工具”会比较困难。
- 如果一开始就接真实数据库或业务 API，demo 成本会过高；但如果只硬编码回复，又无法体现真实客服链路。

### Evidence

- `demo_agent/app.py` 已提供 `/api/chat` 和 `/health`，`chat_cli.py` 已提供 CLI 入口。
- `demo_agent` 已有 `agents/`、`tools/`、`memory/`、`schemas/`、`knowledge/` 分层，适合迁移到 LangGraph 节点。
- `code/python-impl` 已使用 LangGraph `StateGraph` + checkpoint/memory 的客服编排思路，可作为工程参考。
- LangGraph 官方文档将其定位为适合 long-running、stateful workflow/agent 的底层编排基础设施，适合本项目的客服状态流转。

## 3. Target Users & Personas

### Primary Persona: 买家自助客服用户

- 角色：电商平台买家。
- 目标：直接与 AI 对话，快速解决购买前咨询、订单查询、物流跟踪、退款/退货/换货和投诉问题。
- 痛点：不想翻规则、不想等待人工客服、不确定订单或售后状态。
- 成功体验：AI 能先查数据，再用清晰客服话术回复；遇到复杂或高风险问题能明确转人工。

### Secondary Persona: Demo 开发者

- 角色：维护和演示该项目的开发者。
- 目标：用本地 mock 数据演示 LangGraph Agent 的完整客服链路。
- 痛点：希望不依赖真实业务系统，也能体现工程结构、状态流、工具调用和模型适配。
- 成功体验：通过 CLI 和 HTTP API 都能稳定演示；模型不可用时也能跑通模板兜底。

## 4. Strategic Context

### Business Goals

- 将 `demo_agent` 从通用多 Agent demo 聚焦为电商客服职能 Agent。
- 体现 LangChain + LangGraph 在客服场景中的分工：LangGraph 负责状态流转，LangChain 负责模型、消息和工具适配。
- 首版优先保证本地可运行和链路清晰，后续再接真实 API、数据库、RAG 向量检索和人工客服系统。

### Why Now?

项目已经具备基础模块和入口，最有价值的下一步不是增加更多零散能力，而是把核心编排升级为可观测、可扩展的 LangGraph 状态机，并围绕电商全链路客服统一数据、意图和转人工规则。

## 5. Solution Overview

### High-Level Solution

构建一个 LangGraph 状态机驱动的电商客服 Agent：

```text
用户消息
  -> 初始化会话状态
  -> 规则意图识别与实体抽取
  -> 根据意图路由到售前 / 订单履约 / 售后 / 知识政策 / 澄清
  -> 调用本地 mock 工具查询商品、订单、物流、售后、工单和政策
  -> 风险与转人工判断
  -> 使用 opai-gpt5.4 润色客服回复
  -> 模型不可用时使用模板兜底
  -> 输出结构化响应并更新会话记忆
```

### Architecture Direction

首版采用 LangGraph 状态机优先：

- `StateGraph` 定义客服处理链路。
- `AgentState` 记录消息、用户、会话、意图、实体、工具结果、风险结果、模型输出和最终回复。
- `conditional_edges` 根据意图和风险结果分流。
- 使用内存 checkpoint 或现有 `SessionMemory` 支持多轮上下文。
- 保留现有 `Supervisor.chat(message, user_id, session_id)` 外部接口，内部替换为 graph invocation，降低 CLI/API 改造成本。

### Proposed Graph Nodes

| Node | Responsibility |
| --- | --- |
| `init_context` | 读取 session memory，初始化 AgentState |
| `classify_intent` | 规则优先识别售前、订单、物流、售后、投诉、政策、澄清 |
| `route_by_intent` | 通过 conditional edge 路由到业务节点 |
| `presales_node` | 查询商品、库存、规格、活动、推荐信息 |
| `order_node` | 查询订单状态、支付状态、发货状态 |
| `logistics_node` | 查询物流单号、承运商、最新轨迹、ETA |
| `aftersales_node` | 查询/创建退款、退货、换货、售后工单 |
| `policy_node` | 从本地知识库检索售后政策、物流规则、会员规则 |
| `risk_review` | 判断敏感售后、信息缺失、高价值订单、强烈情绪 |
| `llm_polish` | 用 `opai-gpt5.4` 将结构化结果润色为客服话术 |
| `template_fallback` | 模型不可用或未配置时输出模板回复 |
| `synthesize` | 生成统一 API/CLI 响应结构 |
| `update_memory` | 写入 last_intent、last_order_id、last_product、last_ticket_id 等 |

### Model Strategy

默认模型配置：

```text
MODEL_PROVIDER=opai
MODEL_NAME=opai-gpt5.4
```

回复生成策略：

1. 规则识别意图和实体。
2. 工具查询本地 mock 数据。
3. 将结构化查询结果、政策片段、风险结论交给 `opai-gpt5.4` 润色。
4. 如果模型未配置、调用失败或返回异常，则使用模板回复兜底。

### Local Mock Data Scope

首版使用文件型 mock 数据，不导入数据库：

- `products.json`：商品、规格、价格、库存、售后属性。
- `orders.json`：订单号、用户、商品、金额、支付/发货/签收状态。
- `shipments.json`：物流单号、承运商、状态、ETA、最新轨迹。
- `return_requests.json`：退款、退货、换货申请状态。
- `tickets.json`：投诉、纠纷、转人工工单。
- `knowledge_base/*.md`：售后政策、物流规则、商品说明、客服 SOP。

### Entry Points

- CLI：保留 `python -m demo_agent.chat_cli`。
- HTTP API：保留 `POST /api/chat` 和 `GET /health`。

推荐 API 响应结构：

```json
{
  "response": "客服最终回复",
  "intent": "order_status",
  "confidence": 0.91,
  "session_id": "api-xxxx",
  "need_handoff": false,
  "risk_reasons": [],
  "sources": ["refund_policy.md#chunk-1"],
  "tool_calls": [
    {
      "name": "order.query",
      "arguments": {"order_id": "O202607040001"},
      "success": true
    }
  ]
}
```

## 6. Success Metrics

### Primary Metric

本地客服链路验收通过率：

- 目标：至少 85% 的预置电商客服测试问题返回符合预期的意图、工具结果、风险标记和回复结构。

### Secondary Metrics

- 售前、订单、物流、售后、政策五类基础意图均有成功样例。
- 已知订单/物流/售后单查询准确率达到 90% 以上。
- 模型不可用时，CLI 与 HTTP API 仍可通过模板回复正常完成请求。
- 高风险场景转人工命中率达到 90% 以上。
- 多轮记忆样例至少覆盖订单追问和售后追问。

### Guardrail Metrics

- 不得虚构 mock 数据中不存在的订单、物流、退款状态。
- 不得承诺“必定退款”“当天必达”“百分百赔偿”等不受政策支持的结果。
- 不得在用户情绪强烈、信息缺失或高价值订单时继续自动做最终决策。

## 7. User Stories & Requirements

### Epic Hypothesis

我们相信，将 `demo_agent` 改造为 LangGraph 状态机驱动的电商全链路买家自助客服 Agent，可以让项目更清晰地展示真实客服系统的意图路由、工具查询、多轮记忆、风险转人工和模型润色能力，因为客服场景本身需要可控流程，而不是完全依赖模型自由生成。

### Story 1: 售前商品咨询

作为买家，我想咨询商品规格、价格、库存和购买建议，以便判断是否下单。

Acceptance Criteria:

- 能识别商品咨询、价格、库存、参数、推荐类问题。
- 能从本地 `products.json` 或商品知识库返回商品信息。
- 查不到商品时要求用户补充商品名称或型号。
- 回复不得虚构库存、价格或活动。

### Story 2: 订单状态查询

作为买家，我想查询订单当前状态，以便知道是否已付款、发货或签收。

Acceptance Criteria:

- 能抽取订单号并调用订单查询工具。
- 已知订单返回订单状态、商品、金额和关键时间信息。
- 未知订单进入信息缺失风险，并提示核对订单号或转人工。
- 后续追问“它什么时候到”能复用上一轮订单号。

### Story 3: 物流查询

作为买家，我想查询包裹在哪里，以便知道预计送达时间。

Acceptance Criteria:

- 能根据订单号或物流单号查询物流 mock 数据。
- 返回承运商、物流状态、ETA 和最新轨迹。
- 物流延迟或超过规则阈值时进入风险/转人工判断。

### Story 4: 售后退款/退货/换货

作为买家，我想申请退款、退货或换货，以便处理商品问题或订单取消。

Acceptance Criteria:

- 能识别退款、退货、换货、取消订单等售后意图。
- 能查询售后政策和已有售后申请状态。
- 对明确低风险场景给出流程说明和下一步。
- 对退款失败、纠纷、投诉、赔偿诉求等敏感售后转人工。

### Story 5: 投诉与人工转接

作为买家，我在问题复杂或不满时希望转人工，以便获得进一步处理。

Acceptance Criteria:

- 用户明确要求人工时创建或返回转人工工单。
- 情绪强烈、威胁、辱骂、强烈不满时标记风险并建议人工处理。
- 高价值订单超过配置阈值时标记人工确认。
- 工单结果返回 `ticket_id` 和状态。

### Story 6: 模型润色与模板兜底

作为开发者，我希望默认使用 `opai-gpt5.4` 润色回复，同时模型不可用时 demo 不崩溃。

Acceptance Criteria:

- 模型配置集中管理，不散落在业务节点中。
- 工具结果和政策片段先结构化，再传给模型润色。
- 模型调用失败时使用模板生成同等结构的客服回复。
- 测试环境可以绕过真实模型调用。

### Story 7: CLI + HTTP API 双入口

作为开发者，我希望通过命令行和 HTTP API 都能测试客服 Agent。

Acceptance Criteria:

- CLI 可连续多轮对话并复用 session。
- HTTP API 保留 `/api/chat` 与 `/health`。
- API 返回意图、置信度、是否转人工、风险原因、来源和工具调用记录。
- 两个入口共用同一个 Supervisor/Graph 链路。

## 8. Functional Requirements

- FR-01: 系统必须使用 LangGraph 状态机表达客服主链路。
- FR-02: 系统必须保留现有 CLI 和 HTTP API 入口。
- FR-03: 系统必须支持售前、订单、物流、售后、投诉/转人工、政策问答基础能力。
- FR-04: 系统必须使用本地 mock 文件作为首版数据源。
- FR-05: 系统必须默认配置模型 `opai-gpt5.4`。
- FR-06: 系统必须采用规则优先的意图识别和工具调用策略。
- FR-07: 系统必须在模型不可用时使用模板兜底。
- FR-08: 系统必须返回工具调用记录和知识来源。
- FR-09: 系统必须支持 session 级别多轮记忆。
- FR-10: 系统必须对敏感售后、信息缺失、高价值订单、强烈情绪执行风险/转人工判断。

## 9. Non-Functional Requirements

- NFR-01: 本地 demo 不依赖真实数据库、真实订单系统或真实客服系统。
- NFR-02: 单轮请求链路应保持可读、可调试，节点职责清晰。
- NFR-03: 单元测试和基础集成测试应可在无模型密钥环境运行。
- NFR-04: 新增依赖应限制在 LangGraph/LangChain/FastAPI 相关必要范围内。
- NFR-05: 业务 mock 数据应集中管理，避免散落在 Agent 代码中。

## 10. Out Of Scope

首版不包含：

- 真实数据库接入。
- 真实商品、订单、物流、支付、CRM 或客服工单系统接入。
- Web 前端聊天页面。
- 多商家、多店铺、多租户权限。
- 自动审批真实退款、真实退货、真实赔偿。
- 向量数据库、复杂 RAG rerank、LangSmith 线上观测。
- 语音客服、图片识别、直播电商场景。

## 11. Dependencies & Risks

### Technical Dependencies

- Python 3.11+。
- FastAPI / Uvicorn。
- LangGraph。
- LangChain / langchain-openai 或兼容 `opai-gpt5.4` 的模型适配层。
- 本地 JSON fixture 和 Markdown knowledge base。

### Risks And Mitigations

- Risk: `opai-gpt5.4` 不是标准公开模型名，运行环境可能无法直接调用。
  - Mitigation: 通过配置项和模型适配层隔离；模型不可用时模板兜底。

- Risk: 状态机节点过多导致首版复杂。
  - Mitigation: 先实现核心节点：`init_context`、`classify_intent`、业务处理、`risk_review`、`llm_polish/template_fallback`、`synthesize`。

- Risk: 本地 mock 数据太薄，无法覆盖全链路。
  - Mitigation: 优先复用 `Knowledge/yuncangyouxuan_v2_fixed/fixtures` 中更完整的 products、shipments、return_requests 等数据，再按需裁剪到 `data/fixtures`。

- Risk: 规则意图识别误判。
  - Mitigation: 使用可测试关键词/正则规则起步；低置信度进入澄清节点。

- Risk: 客服回复越权承诺。
  - Mitigation: 风险节点在模型润色前后均可检查；涉及退款失败、投诉、赔偿、高价值订单统一转人工。

## 12. Open Questions

- 高价值订单阈值首版设为多少？建议默认 5000 元。
- 是否需要把 `Knowledge/yuncangyouxuan_v2_fixed` 的数据复制/清洗到 `data/fixtures`，作为唯一 mock 数据源？
- `opai-gpt5.4` 的调用方式是否兼容 `ChatOpenAI`，还是需要自定义 `BaseChatModel` 适配器？
- 售后节点首版是否只查询/创建工单，还是模拟“申请退款/退货”的状态流转？
- 是否需要保留现有 `RAGAgent` 名称，还是重命名为 `PolicyAgent` / `KnowledgeAgent` 更贴近客服业务？

## 13. Implementation Milestones

### Milestone 1: PRD 与数据收敛

- 确认本 PRD。
- 确认 mock 数据源范围。
- 确认模型环境变量和调用适配方式。

### Milestone 2: LangGraph 骨架

- 扩展 `AgentState`。
- 新增或重写 `Supervisor` 内部 graph 构建。
- 实现核心节点和 conditional routing。
- 保持 `Supervisor.chat()` 返回结构兼容 CLI/API。

### Milestone 3: 电商工具与业务节点

- 新增商品、物流、售后查询工具。
- 改造订单和工单工具。
- 实现售前、订单、物流、售后、政策节点。

### Milestone 4: 模型适配与兜底

- 新增模型配置。
- 接入 `opai-gpt5.4` 润色节点。
- 增加模板兜底节点。
- 增加模型不可用测试。

### Milestone 5: 风险转人工与验收

- 实现风险规则。
- 增加工单/转人工结果。
- 补充 CLI/API 示例。
- 增加端到端测试用例。

## 14. Acceptance Checklist

- [ ] CLI 可以完成售前、订单、物流、售后、投诉转人工样例。
- [ ] HTTP API 可以返回统一结构化响应。
- [ ] LangGraph 状态机替代顺序式客服主链路。
- [ ] 本地 mock 文件是首版唯一业务数据源。
- [ ] 默认模型名配置为 `opai-gpt5.4`。
- [ ] 模型不可用时模板兜底可用。
- [ ] 高风险场景返回 `need_handoff=true` 和风险原因。
- [ ] 多轮追问可以复用上一轮订单号或商品名。
- [ ] 测试环境不依赖真实外部服务。

## References

- LangGraph 官方文档：`StateGraph` 适合构建有状态、可持久化、可调试的 agent/workflow。
- LangGraph memory 文档：支持 thread-level persistence，用于多轮对话上下文。
- LangChain tools 文档：工具是带明确输入输出的 callable，可让 agent 查询外部数据或执行动作。
- LangChain ChatOpenAI 文档：支持 tool calling 和模型调用适配，可作为后续 `opai-gpt5.4` 兼容层参考。
