from __future__ import annotations

from pathlib import Path

from demo_agent.tools.base import load_json


class TicketTool:
    """基于本地 fixture 和内存状态提供工单创建与查询能力。"""

    def __init__(self, fixtures_dir: str | Path):
        self._tickets: dict[str, dict] = {
            item["ticket_id"]: item for item in load_json(Path(fixtures_dir) / "tickets.json", [])
        }
        self._counter = len(self._tickets) + 1

    def create(self, user_id: str, category: str, summary: str, order_id: str | None = None) -> dict:
        ticket_id = f"TK-DEMO-{self._counter:04d}"
        self._counter += 1
        ticket = {
            "ticket_id": ticket_id,
            "user_id": user_id,
            "category": category,
            "summary": summary,
            "order_id": order_id,
            "status": "created",
        }
        self._tickets[ticket_id] = ticket
        return ticket

    def query(self, ticket_id: str) -> dict:
        ticket = self._tickets.get(ticket_id.upper())
        if not ticket:
            return {"found": False, "ticket_id": ticket_id.upper()}
        return {"found": True, **ticket}
