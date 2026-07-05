from __future__ import annotations

from pathlib import Path

from demo_agent.tools.after_sales_tool import AfterSalesTool
from demo_agent.tools.order_tool import OrderTool
from demo_agent.tools.product_tool import ProductTool
from demo_agent.tools.risk_tool import RiskTool
from demo_agent.tools.shipment_tool import ShipmentTool
from demo_agent.tools.ticket_tool import TicketTool
from demo_agent.tools.user_tool import UserTool


class ToolRegistry:
    """集中初始化并持有 demoAgent 可调用的所有本地企业工具。"""

    def __init__(self, fixtures_dir: str | Path):
        self.product = ProductTool(fixtures_dir)
        self.order = OrderTool(fixtures_dir)
        self.shipment = ShipmentTool(fixtures_dir)
        self.after_sales = AfterSalesTool(fixtures_dir)
        self.ticket = TicketTool(fixtures_dir)
        self.user = UserTool(fixtures_dir)
        self.risk = RiskTool()
