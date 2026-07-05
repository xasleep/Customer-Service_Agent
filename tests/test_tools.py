from pathlib import Path

from demo_agent.tools.registry import ToolRegistry


ROOT = Path(__file__).resolve().parents[1]


def test_order_tool_returns_known_order():
    tools = ToolRegistry(ROOT / "data" / "fixtures")

    result = tools.order.query("ORD1001")

    assert result["found"] is True
    assert result["product"] == "智能净化器"
    assert result["eta"] == "2026-07-06"


def test_order_tool_returns_not_found_for_unknown_order():
    tools = ToolRegistry(ROOT / "data" / "fixtures")

    result = tools.order.query("ORD9999")

    assert result["found"] is False
    assert result["order_id"] == "ORD9999"


def test_product_tool_returns_known_product():
    tools = ToolRegistry(ROOT / "data" / "fixtures")

    result = tools.product.query("智能净化器")

    assert result["found"] is True
    assert result["stock"] == 26
    assert result["price"] == 1299.0


def test_shipment_tool_returns_order_logistics():
    tools = ToolRegistry(ROOT / "data" / "fixtures")

    result = tools.shipment.query(order_id="ORD1001")

    assert result["found"] is True
    assert result["tracking_no"] == "SF1234567890"
    assert result["status_label"] == "运输中"


def test_after_sales_tool_returns_return_request():
    tools = ToolRegistry(ROOT / "data" / "fixtures")

    result = tools.after_sales.query(order_id="ORD1003")

    assert result["found"] is True
    assert result["request_id"] == "RR1002"
    assert result["status_label"] == "审核中"


def test_ticket_tool_creates_stable_demo_ticket():
    tools = ToolRegistry(ROOT / "data" / "fixtures")

    result = tools.ticket.create("u1001", "refund", "申请退款", order_id="ORD1003")

    assert result["ticket_id"] == "TK-DEMO-0002"
    assert result["status"] == "created"
    assert result["order_id"] == "ORD1003"
