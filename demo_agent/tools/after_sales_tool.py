from __future__ import annotations

from pathlib import Path

from demo_agent.tools.base import load_json


class AfterSalesTool:
    """基于本地售后 fixture 查询退款、退货、换货申请状态。"""

    def __init__(self, fixtures_dir: str | Path):
        requests = load_json(Path(fixtures_dir) / "return_requests.json", [])
        self._by_request = {item["request_id"].upper(): item for item in requests}
        self._by_order = {item["order_id"].upper(): item for item in requests}

    def query(self, order_id: str | None = None, request_id: str | None = None) -> dict:
        item = None
        if request_id:
            item = self._by_request.get(request_id.upper())
        if item is None and order_id:
            item = self._by_order.get(order_id.upper())

        if not item:
            return {
                "found": False,
                "order_id": order_id.upper() if order_id else None,
                "request_id": request_id.upper() if request_id else None,
            }
        return {"found": True, **item}
