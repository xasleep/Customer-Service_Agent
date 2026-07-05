# demoAgent

Local-first Python MVP for a multi-agent customer support assistant backed by a virtual enterprise knowledge base.

## What It Demonstrates

- Deterministic intent routing
- Local Markdown knowledge retrieval with citations
- Mock enterprise tools for orders, tickets, users, and risk checks
- Per-session memory for multi-turn follow-up
- Compliance checks for PII and unsafe financial claims
- CLI and optional FastAPI entry points
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

## Example Questions

- `智能净化器的保修规则是什么？`
- `订单 ORD1001 什么时候到？`
- `帮我申请 ORD1003 的退款`
- `手机号 13812345678 是我的联系方式`
- `客服能承诺当天必达吗？`
