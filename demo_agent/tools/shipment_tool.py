from __future__ import annotations

from pathlib import Path

from demo_agent.tools.base import load_json


class ShipmentTool:
    """基于本地物流 fixture 提供订单物流查询能力。"""

    def __init__(self, fixtures_dir: str | Path):
        shipments = load_json(Path(fixtures_dir) / "shipments.json", [])
        self._by_tracking = {item["tracking_no"].upper(): item for item in shipments}
        self._by_order = {item["order_id"].upper(): item for item in shipments}

    def query(self, order_id: str | None = None, tracking_no: str | None = None) -> dict:
        shipment = None
        if tracking_no:
            shipment = self._by_tracking.get(tracking_no.upper())
        if shipment is None and order_id:
            shipment = self._by_order.get(order_id.upper())

        if not shipment:
            return {
                "found": False,
                "order_id": order_id.upper() if order_id else None,
                "tracking_no": tracking_no.upper() if tracking_no else None,
            }
        return {"found": True, **shipment}
