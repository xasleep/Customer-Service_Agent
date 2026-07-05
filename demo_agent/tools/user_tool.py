from __future__ import annotations

from pathlib import Path

from demo_agent.tools.base import load_json


class UserTool:
    """基于本地用户 fixture 提供用户资料查询能力。"""

    def __init__(self, fixtures_dir: str | Path):
        self.users = {item["user_id"]: item for item in load_json(Path(fixtures_dir) / "users.json", [])}

    def query(self, user_id: str) -> dict:
        user = self.users.get(user_id)
        if not user:
            return {"found": False, "user_id": user_id}
        return {"found": True, **user}
