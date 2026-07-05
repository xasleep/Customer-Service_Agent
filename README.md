# Customer-Service_Agent

Local-first Python demo for an ecommerce customer service AI Agent. The project uses a LangGraph-driven workflow, local mock ecommerce data, deterministic intent routing, tool calls, policy retrieval, session memory, and compliance checks.

## What It Demonstrates

- LangGraph `StateGraph` orchestration for customer-service flow
- Presales, order, logistics, after-sales, ticket, policy, and compliance routes
- Local Markdown knowledge retrieval with citations
- Mock ecommerce tools for products, orders, shipments, after-sales requests, tickets, users, and risk checks
- Per-session memory for multi-turn follow-up
- Template fallback when the configured model is unavailable
- Optional `opai-gpt5.4` HTTP model polishing through environment variables
- Risk handoff with automatic demo ticket creation
- CLI and FastAPI entry points
- Offline tests with local fixtures

## Quick Start

```bash
python -m pytest
python -m demo_agent.chat_cli
```

Optional API mode:

```bash
python -m demo_agent.app
```

Then call:

```bash
curl -X POST http://localhost:8000/api/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\":\"订单 ORD1001 什么时候到？\",\"user_id\":\"u1001\"}"
```

## Optional Model Configuration

The default model id is `opai-gpt5.4`. Model use is optional: without endpoint credentials, the project keeps running with deterministic template fallback.

```bash
copy .env.example .env
```

Then set:

```text
OPAI_BASE_URL=<your OpenAI-compatible chat endpoint>
OPAI_API_KEY=<your key>
MODEL_NAME=opai-gpt5.4
```

When configured, the LangGraph flow calls the model only after intent routing, local tool lookup, risk review, and compliance review. If the model call fails, the same structured result is returned through template fallback.

## Risk Handoff

The demo marks `need_handoff=true` and creates a demo handoff ticket when it detects:

- Missing business data, such as an unknown order or shipment
- High-value orders
- Sensitive after-sales situations, such as complaints or refund failure
- Strong negative emotion or escalation language
- Compliance failures

## Example Questions

- `智能净化器现在有库存吗？`
- `智能净化器的保修规则是什么？`
- `订单 ORD1001 什么时候到？`
- `物流 ORD1001 到哪里了？`
- `退款进度 ORD1003 怎么样？`
- `帮我申请 ORD1003 的退款`
- `手机号 13812345678 是我的联系方式`
- `客服能承诺当天必达吗？`
