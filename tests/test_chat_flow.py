import json
from pathlib import Path

from demo_agent.agents.supervisor import Supervisor


ROOT = Path(__file__).resolve().parents[1]


def test_knowledge_question_returns_citation():
    supervisor = Supervisor()

    result = supervisor.chat("智能净化器的保修规则是什么？", user_id="u1001", session_id="s-knowledge")

    assert result["intent"] == "knowledge"
    assert "来源：" in result["response"]
    assert any(source.startswith("products.md#") for source in result["sources"])


def test_order_query_returns_tool_call():
    supervisor = Supervisor()

    result = supervisor.chat("订单 ORD1001 什么时候到？", user_id="u1001", session_id="s-order")

    assert result["intent"] == "order"
    assert "2026-07-06" in result["response"]
    assert result["tool_calls"][0]["name"] == "order.query"
    assert result["model"] == "opai-gpt5.4"
    assert result["generation_mode"] == "template_fallback"
    assert result["need_handoff"] is False


def test_multi_turn_order_follow_up_uses_session_memory():
    supervisor = Supervisor()

    first = supervisor.chat("查询订单 ORD1001", user_id="u1001", session_id="s-memory")
    second = supervisor.chat("那它什么时候到？", user_id="u1001", session_id="s-memory")

    assert first["intent"] == "order"
    assert second["intent"] == "order"
    assert "ORD1001" in second["response"]


def test_missing_order_marks_handoff_risk():
    supervisor = Supervisor()

    result = supervisor.chat("订单 ORD9999 什么时候到？", user_id="u1001", session_id="s-missing-order")

    assert result["intent"] == "order"
    assert result["need_handoff"] is True
    assert "information_missing" in result["risk_reasons"]
    assert result["tool_calls"][0]["success"] is False


def test_presales_query_uses_product_tool():
    supervisor = Supervisor()

    result = supervisor.chat("智能净化器现在有库存吗？", user_id="u1001", session_id="s-presales")

    assert result["intent"] == "presales"
    assert "库存 26 件" in result["response"]
    assert result["tool_calls"][0]["name"] == "product.query"


def test_logistics_query_uses_shipment_tool():
    supervisor = Supervisor()

    result = supervisor.chat("物流 ORD1001 到哪里了？", user_id="u1001", session_id="s-logistics")

    assert result["intent"] == "logistics"
    assert "顺丰速运" in result["response"]
    assert result["tool_calls"][0]["name"] == "shipment.query"


def test_after_sales_query_uses_after_sales_tool():
    supervisor = Supervisor()

    result = supervisor.chat("退款进度 ORD1003 怎么样？", user_id="u1001", session_id="s-after-sales")

    assert result["intent"] == "aftersales"
    assert "RR1002" in result["response"]
    assert result["tool_calls"][0]["name"] == "after_sales.query"


def test_eval_cases_pass_core_expectations():
    cases = json.loads((ROOT / "tests" / "eval_cases.json").read_text(encoding="utf-8"))
    supervisor = Supervisor()
    passed = 0

    for index, case in enumerate(cases):
        result = supervisor.chat(case["message"], user_id="u1001", session_id=f"eval-{index}")
        if result["intent"] != case["expected_intent"]:
            continue
        if "expected_source" in case and any(src.startswith(case["expected_source"] + "#") for src in result["sources"]):
            passed += 1
        elif "expected_tool" in case and any(call["name"] == case["expected_tool"] for call in result["tool_calls"]):
            passed += 1

    assert passed / len(cases) >= 0.85
