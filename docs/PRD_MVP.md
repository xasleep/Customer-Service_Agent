# demoAgent MVP PRD

## 1. Executive Summary

demoAgent MVP is a Python-based ecommerce customer support demo for a virtual enterprise knowledge base. It will turn the current learning-oriented multi-agent idea into a smaller, more credible, and testable project: users can ask ecommerce support questions, the system routes intent, retrieves answers from local knowledge files with citations, calls mock enterprise tools for orders and tickets, applies privacy and service-policy checks, and exposes both CLI and API entry points. The goal is not production readiness; the goal is a clean MVP that demonstrates real architecture, realistic fake data, and automated verification.

## 2. Problem Statement

### Who Has This Problem?

- Developers or learners who want a stronger Python AI agent demo than the existing generated-looking sample.
- Interview candidates who need a believable project narrative backed by runnable code and tests.
- Reviewers or interviewers who want to see whether the system can handle enterprise support scenarios beyond hardcoded responses.

### What Is The Problem?

The existing Python implementation demonstrates many concepts, but the business data and system behavior are still too shallow for a convincing demo:

- Knowledge is mostly hardcoded or small.
- Tool calls return fixed mock values.
- Retrieval quality is hard to evaluate.
- The project has broad architecture but limited realistic test data.
- It is easy to describe, but harder to prove through repeatable tests.

### Why Is It Painful?

- The system can look AI-generated because the architecture is broad but the domain depth is thin.
- Without a virtual enterprise knowledge base and fixtures, RAG behavior cannot be tested reliably.
- Without deterministic tests, improvements may be cosmetic rather than meaningful.
- Without a tighter MVP scope, the project can drift into another oversized demo.

### Evidence

- Current code contains mock order, ticket, risk, and knowledge handlers.
- Existing documentation already marks several production features as planned rather than implemented.
- The strongest improvement opportunity is to make the Python version smaller, cleaner, and test-driven around a virtual enterprise dataset.

## 3. Target Users & Personas

### Primary Persona: AI Backend Learner

- Role: Developer improving a Python AI agent project.
- Goal: Build a runnable project that demonstrates multi-agent orchestration, RAG, tool use, memory, and compliance.
- Pain points: Wants realistic behavior without needing real enterprise systems or paid infrastructure.
- Success looks like: Can run local tests and show a working CLI/API demo.

### Secondary Persona: Technical Interview Reviewer

- Role: Senior engineer, interviewer, or reviewer.
- Goal: Understand whether the project has engineering substance.
- Pain points: Skeptical of generic generated agent demos.
- Success looks like: Sees clear module boundaries, realistic fixtures, cited RAG answers, and automated tests.

### Jobs To Be Done

- When testing an AI customer support system locally, I want realistic company knowledge and customer data, so that I can verify routing, retrieval, and tool behavior without real integrations.
- When presenting the project, I want a concise demo path with reliable outputs, so that the project feels engineered rather than assembled from templates.

## 4. Strategic Context

### Business Goals

- Create a stronger Python MVP that can replace or improve the existing `python-impl` demo.
- Make the project credible as a portfolio or interview artifact.
- Keep the implementation local-first and testable without relying on network services.

### Why Now?

The existing folder already contains a three-language multi-agent sample and a detailed guide. The next highest-value step is not adding more languages or more features; it is building one focused Python MVP with realistic fake enterprise data, tests, and clear boundaries.

### Competitive / Reference Context

Most agent demos show broad concepts but fail on repeatability. demoAgent should differentiate by having:

- A visible virtual enterprise knowledge base.
- Deterministic fixtures for business tools.
- Evaluated RAG answers with source citations.
- Multi-turn scenarios that prove memory and entity carryover.

## 5. Solution Overview

### High-Level Solution

Build a local Python project under `demoAgent/` that implements a multi-agent customer support assistant for a fictional enterprise. The assistant will support knowledge questions, order queries, refund/ticket creation, and compliance-safe responses. The MVP should work through a command-line chat and a simple FastAPI endpoint.

### MVP Architecture

```text
User message
  -> Supervisor
  -> Intent Agent
  -> RAG Agent or Tool Agent
  -> Compliance Agent
  -> Final response with citations/tool result
```

### Key Features

1. Virtual enterprise knowledge base
   - Markdown files under `data/knowledge_base/`.
   - Example domains: product policy, refund policy, logistics, account guide, compliance rules, internal support SOP.
   - Each answer from RAG should include one or more cited source chunks.

2. Retrieval pipeline
   - Load Markdown documents.
   - Chunk documents.
   - Use deterministic local retrieval for MVP, such as BM25 or keyword scoring.
   - Return `source`, `chunk_id`, `score`, and `content`.

3. Agent orchestration
   - `IntentAgent`: classify requests into `knowledge`, `order`, `ticket`, `compliance`, or `clarify`.
   - `RAGAgent`: answer based on retrieved knowledge only.
   - `ToolAgent`: call local fixture-backed enterprise tools.
   - `ComplianceAgent`: detect PII, forbidden claims, and unsafe financial language.
   - `Supervisor`: coordinate flow and synthesize the final response.

4. Mock enterprise tools
   - `order_tool`: query local `orders.json`.
   - `ticket_tool`: create/query tickets in memory or local JSON.
   - `user_tool`: query local `users.json`.
   - `risk_tool`: return risk level based on configurable rules.

5. Session memory
   - Track `last_intent`, `last_order_id`, `last_product`, `accumulated_entities`, and `turn_count`.
   - Support simple multi-turn follow-ups such as "那它什么时候到?" after an order query.

6. Entry points
   - CLI: `python -m demo_agent.chat_cli`
   - API: `POST /api/chat`
   - Health check: `GET /health`

7. Automated tests and evaluation set
   - Unit tests for retrieval, tools, compliance, routing, and memory.
   - Evaluation cases in `tests/eval_cases.json`.
   - MVP acceptance should be based on tests, not manual inspection alone.

### Suggested Folder Structure

```text
demoAgent/
  docs/
    PRD_MVP.md
  demo_agent/
    app.py
    chat_cli.py
    agents/
      supervisor.py
      intent.py
      rag.py
      tool_agent.py
      compliance.py
    knowledge/
      loader.py
      chunker.py
      retriever.py
    tools/
      order_tool.py
      ticket_tool.py
      user_tool.py
      risk_tool.py
    memory/
      session_memory.py
    schemas/
      state.py
      models.py
  data/
    knowledge_base/
      products.md
      refund_policy.md
      logistics.md
      account_guide.md
      compliance_rules.md
      support_sop.md
    fixtures/
      orders.json
      users.json
      tickets.json
  tests/
    eval_cases.json
    test_retriever.py
    test_tools.py
    test_intent.py
    test_memory.py
    test_compliance.py
    test_chat_flow.py
```

## 6. Success Metrics

### Primary Metric

MVP automated evaluation pass rate:

- Target: at least 85% of curated `eval_cases.json` scenarios pass.
- Pass means the system chooses the expected route, returns the expected tool result or cited knowledge source, and avoids unsafe output.

### Secondary Metrics

- Retrieval citation accuracy: at least 90% of knowledge questions cite the expected source document.
- Multi-turn memory pass rate: at least 4 of 5 scripted multi-turn scenarios pass.
- Compliance detection pass rate: at least 90% of unsafe/PII test cases are flagged or sanitized.
- Local setup time: a new developer can run tests within 5 minutes after installing dependencies.

### Guardrail Metrics

- No answer should claim facts not present in the knowledge base or tool fixtures.
- No test should require a real enterprise system, real Redis, real vector DB, or network access.
- LLM use should be optional or isolated behind an interface so deterministic tests still run without an API key.

## 7. User Stories & Requirements

### Epic Hypothesis

We believe that building a local, testable multi-agent customer support MVP with a virtual enterprise knowledge base will make demoAgent more credible than the original broad sample because it replaces hardcoded responses with realistic fixtures, cited retrieval, and automated acceptance tests.

### Story 1: Load A Virtual Enterprise Knowledge Base

As a developer, I want the system to load Markdown knowledge files, so that RAG behavior can be tested against realistic company documents.

Acceptance criteria:

- The loader reads all `.md` files from `data/knowledge_base/`.
- Each document is split into chunks with stable `source` and `chunk_id`.
- Empty files or malformed files do not crash startup.
- A unit test verifies at least five documents are loaded.

### Story 2: Retrieve Relevant Knowledge With Citations

As a support user, I want answers to cite source documents, so that I can trust where the response came from.

Acceptance criteria:

- A refund question retrieves `refund_policy.md`.
- A logistics question retrieves `logistics.md`.
- A product question retrieves `products.md`.
- Each RAG response includes source metadata.
- If no relevant source is found, the assistant says it cannot find the answer and suggests escalation.

### Story 3: Route User Requests To The Correct Agent

As a system operator, I want user messages routed by intent, so that knowledge questions and business actions are handled differently.

Acceptance criteria:

- Product/policy questions route to `RAGAgent`.
- Order status questions route to `ToolAgent`.
- Refund creation requests route to `ToolAgent` ticket flow.
- Unsafe financial promises route through compliance handling.
- Low-confidence messages trigger a clarification response.

### Story 4: Query Mock Enterprise Tools

As a support user, I want to check an order or create a ticket, so that business tasks are represented in the demo.

Acceptance criteria:

- Querying a known order ID returns status, product, amount, and delivery estimate.
- Querying an unknown order ID returns a clear not-found response.
- Creating a ticket returns a stable ticket ID and stores the ticket for later query.
- Tool behavior is covered by unit tests using local fixtures.

### Story 5: Support Multi-Turn Follow-Up

As a user, I want the assistant to remember the order or product from the previous turn, so that I do not have to repeat myself.

Acceptance criteria:

- After "查询订单 ORD1001", a follow-up "它什么时候到?" uses `ORD1001`.
- The memory stores `last_order_id`, `last_intent`, and `turn_count`.
- Memory is scoped by `session_id`.
- A test verifies two separate sessions do not share memory.

### Story 6: Apply Compliance Checks

As a fictional enterprise, I want all outgoing answers checked for unsafe content, so that the demo does not produce obviously non-compliant replies.

Acceptance criteria:

- Phone numbers, ID numbers, and bank card numbers are masked.
- Unsupported service promises such as "当天必达" and "百分百赔付" are flagged.
- Compliance failure returns a safe escalation response.
- Safe answers pass without unnecessary blocking.

### Story 7: Provide CLI And API Demo Paths

As a developer, I want both CLI and API entry points, so that I can test quickly and demo externally.

Acceptance criteria:

- CLI supports interactive chat with a session ID.
- FastAPI exposes `POST /api/chat` and `GET /health`.
- API response includes `response`, `intent`, `session_id`, `sources`, and `tool_calls`.
- API can run without Redis or external services.

### Functional Requirements

- FR-01: The system must run locally with file-based knowledge and fixtures.
- FR-02: The system must support deterministic tests without an LLM API key.
- FR-03: The system must return cited sources for knowledge answers.
- FR-04: The system must expose tool call traces in the response object.
- FR-05: The system must preserve per-session memory.
- FR-06: The system must include a curated evaluation dataset.

### Non-Functional Requirements

- NFR-01: Startup should complete in under 3 seconds for the local fixture set.
- NFR-02: Unit tests should run without network access.
- NFR-03: Module boundaries should be simple enough for interview explanation.
- NFR-04: New dependencies should be minimal and justified.
- NFR-05: The project should avoid hidden global state except explicit session memory.

## 8. Out Of Scope

Not included in MVP:

- Real enterprise integrations with order, CRM, payment, or ticketing systems.
- Production vector databases such as Milvus, Pinecone, or Elasticsearch.
- Streaming responses.
- Web UI.
- Authentication, authorization, rate limiting, and API gateway behavior.
- Java or Go implementations.
- Full LangGraph parity with the original project.
- Production observability stack such as Jaeger deployment.
- Fine-tuning, agent self-reflection, or autonomous planning loops.

Future consideration:

- Optional OpenAI or local embedding retriever.
- Web demo UI.
- Docker Compose.
- Evaluation dashboard.
- More realistic customer journey scenarios.

## 9. Dependencies & Risks

### Technical Dependencies

- Python 3.11+.
- `pytest` for tests.
- `fastapi` and `uvicorn` for API mode.
- Optional: LLM provider adapter for non-deterministic generation.
- Local Markdown and JSON fixture files.

### Risks And Mitigations

- Risk: The project becomes too broad again.
  - Mitigation: Keep MVP limited to RAG, tools, memory, compliance, CLI/API, and tests.

- Risk: RAG answers hallucinate without a real LLM guard.
  - Mitigation: For MVP, use extractive or template-grounded answers in deterministic mode; require citations.

- Risk: Retrieval quality is weak with keyword-only search.
  - Mitigation: Start with a small controlled knowledge base and evaluation cases; add BM25 or embeddings later.

- Risk: Mock enterprise data feels fake.
  - Mitigation: Create coherent fixtures with repeated users, orders, products, policies, and edge cases.

- Risk: Compliance blocks too much.
  - Mitigation: Separate detection, sanitization, and blocking rules; cover safe and unsafe examples in tests.

- Risk: LLM dependency makes tests flaky.
  - Mitigation: Use interface-based model adapters and deterministic fake model responses for tests.

## 10. Open Questions

- Should MVP use a pure deterministic response generator first, or include optional LLM generation behind a flag?
- Should retrieval start with BM25/keyword scoring only, or include FAISS from the beginning?
- Should tickets persist to a local JSON file, SQLite, or in-memory store for MVP?
- Should the project copy pieces from `code/python-impl`, or be a cleaner reimplementation with similar concepts?
- What fictional enterprise domain should be used first: e-commerce, financial services, or a hybrid marketplace?
- What is the minimum evaluation set size for MVP acceptance: 20, 30, or 50 cases?

## Proposed MVP Milestones

### Milestone 1: Project Skeleton And Fixtures

- Create package structure.
- Add knowledge base Markdown files.
- Add order/user/ticket JSON fixtures.
- Add initial README and run commands.

### Milestone 2: Retrieval And Tools

- Implement loader, chunker, retriever.
- Implement order, ticket, user, and risk tools.
- Add unit tests for retrieval and tools.

### Milestone 3: Agent Flow

- Implement state schema, intent routing, supervisor, RAG agent, tool agent, compliance agent.
- Add CLI.
- Add multi-turn memory.

### Milestone 4: API And Evaluation

- Add FastAPI app.
- Add `eval_cases.json`.
- Add end-to-end chat flow tests.
- Document MVP demo script.

## MVP Acceptance Checklist

- [ ] `python -m pytest` passes locally without network access.
- [ ] CLI can answer at least one knowledge question with a citation.
- [ ] CLI can query one known order and one unknown order.
- [ ] A two-turn order follow-up works through session memory.
- [ ] Compliance masks PII and blocks forbidden financial promises.
- [ ] API returns structured fields: response, intent, session_id, sources, tool_calls.
- [ ] README explains setup, demo commands, and fixture data.
