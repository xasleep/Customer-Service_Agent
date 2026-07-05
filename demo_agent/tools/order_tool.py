from __future__ import annotations

from pathlib import Path

from demo_agent.tools.base import load_json


class OrderTool:
    """基于本地订单 fixture 提供订单查询能力。"""

    def __init__(self, fixtures_dir: str | Path):
        self.orders = {item["order_id"]: item for item in load_json(Path(fixtures_dir) / "orders.json", [])}

    def query(self, order_id: str) -> dict:
        order = self.orders.get(order_id.upper())
        if not order:
            return {"found": False, "order_id": order_id.upper(), "message": "未找到该订单"}
        return {"found": True, **order}
