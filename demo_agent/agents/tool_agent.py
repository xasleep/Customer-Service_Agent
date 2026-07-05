from __future__ import annotations

from demo_agent.schemas.models import AgentResponse, ToolCall
from demo_agent.tools.registry import ToolRegistry


class ToolAgent:
    """负责把订单、退款、工单等业务请求转发到本地企业工具并整理回复。"""

    def __init__(self, tools: ToolRegistry):
        self.tools = tools

    def handle_presales(self, product: str | None = None) -> AgentResponse:
        result = self.tools.product.query(product)
        call = ToolCall("product.query", {"product": product}, result, success=result.get("found", False))
        if not result.get("found"):
            return AgentResponse(f"暂未找到商品 {product}，请确认商品名称或换个关键词。", tool_calls=[call])

        if "items" in result:
            names = "、".join(item["name"] for item in result["items"])
            return AgentResponse(f"当前可咨询的商品有：{names}。您可以继续询问价格、库存或参数。", tool_calls=[call])

        stock_text = "有货" if result["stock"] > 0 else "暂时缺货"
        response = (
            f"{result['name']} 当前价格 {result['price']} 元，库存 {result['stock']} 件，{stock_text}。"
            f"核心参数：{result['specs']}。活动：{result['promotion']}。"
        )
        return AgentResponse(response=response, tool_calls=[call])

    def handle_order(self, user_id: str, order_id: str) -> AgentResponse:
        result = self.tools.order.query(order_id)
        call = ToolCall("order.query", {"order_id": order_id}, result, success=result.get("found", False))
        if not result.get("found"):
            return AgentResponse(f"未找到订单 {order_id}，请确认订单号后重试。", tool_calls=[call])

        response = (
            f"订单 {result['order_id']} 当前状态为：{result['status_label']}。"
            f"商品：{result['product']}，金额：{result['amount']} 元，"
            f"预计送达：{result['eta']}。"
        )
        return AgentResponse(response=response, tool_calls=[call])

    def handle_logistics(self, order_id: str | None = None, tracking_no: str | None = None) -> AgentResponse:
        result = self.tools.shipment.query(order_id=order_id, tracking_no=tracking_no)
        call = ToolCall(
            "shipment.query",
            {"order_id": order_id, "tracking_no": tracking_no},
            result,
            success=result.get("found", False),
        )
        if not result.get("found"):
            return AgentResponse("暂未找到对应物流信息，请确认订单号或物流单号后重试。", tool_calls=[call])

        response = (
            f"订单 {result['order_id']} 的物流由 {result['carrier']} 承运，"
            f"当前状态：{result['status_label']}。最新轨迹：{result['last_event']}。"
            f"预计送达：{result['eta']}。"
        )
        return AgentResponse(response=response, tool_calls=[call])

    def handle_after_sales(self, order_id: str | None = None, request_id: str | None = None) -> AgentResponse:
        result = self.tools.after_sales.query(order_id=order_id, request_id=request_id)
        call = ToolCall(
            "after_sales.query",
            {"order_id": order_id, "request_id": request_id},
            result,
            success=result.get("found", False),
        )
        if not result.get("found"):
            return AgentResponse("暂未找到对应售后申请，请确认订单号或售后单号，必要时可转人工处理。", tool_calls=[call])

        response = (
            f"售后申请 {result['request_id']} 当前状态：{result['status_label']}。"
            f"原因：{result['reason']}，更新时间：{result['updated_at']}。"
            f"下一步：{result['next_step']}。"
        )
        return AgentResponse(response=response, tool_calls=[call])

    def create_ticket(self, user_id: str, category: str, summary: str, order_id: str | None = None) -> AgentResponse:
        result = self.tools.ticket.create(user_id=user_id, category=category, summary=summary, order_id=order_id)
        call = ToolCall("ticket.create", {"user_id": user_id, "category": category, "order_id": order_id}, result)
        return AgentResponse(
            response=f"已创建工单 {result['ticket_id']}，类型：{category}，状态：{result['status']}。",
            tool_calls=[call],
        )

    def query_ticket(self, ticket_id: str) -> AgentResponse:
        result = self.tools.ticket.query(ticket_id)
        call = ToolCall("ticket.query", {"ticket_id": ticket_id}, result, success=result.get("found", False))
        if not result.get("found"):
            return AgentResponse(f"未找到工单 {ticket_id}。", tool_calls=[call])
        return AgentResponse(f"工单 {ticket_id} 当前状态为：{result['status']}。", tool_calls=[call])
