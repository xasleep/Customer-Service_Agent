from demo_agent.agents.intent import IntentAgent


def test_intent_routes_order_query():
    result = IntentAgent().classify("订单 ORD1001 什么时候到？")

    assert result.intent == "order"
    assert result.entities["order_id"] == "ORD1001"


def test_intent_routes_refund_policy_to_knowledge():
    result = IntentAgent().classify("退款政策是怎样的？")

    assert result.intent == "knowledge"


def test_intent_routes_refund_action_to_ticket():
    result = IntentAgent().classify("帮我申请 ORD1003 的退款")

    assert result.intent == "ticket"
    assert result.entities["order_id"] == "ORD1003"


def test_intent_routes_presales_query():
    result = IntentAgent().classify("智能净化器现在有库存吗？")

    assert result.intent == "presales"
    assert result.entities["product"] == "智能净化器"


def test_intent_routes_logistics_query():
    result = IntentAgent().classify("物流 ORD1001 到哪里了？")

    assert result.intent == "logistics"
    assert result.entities["order_id"] == "ORD1001"


def test_intent_routes_after_sales_query():
    result = IntentAgent().classify("退款进度 ORD1003 怎么样？")

    assert result.intent == "aftersales"
    assert result.entities["order_id"] == "ORD1003"


def test_intent_routes_follow_up_to_order_with_memory():
    result = IntentAgent().classify("那它什么时候到？", {"last_order_id": "ORD1001"})

    assert result.intent == "order"
