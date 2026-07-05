from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from typing import Any


class SessionMemory:
    """按 session_id 保存多轮对话中的轻量工作记忆。"""

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = defaultdict(dict)

    def get(self, session_id: str) -> dict[str, Any]:
        return deepcopy(self._store.get(session_id, {}))

    def update(self, session_id: str, data: dict[str, Any]) -> None:
        current = self._store[session_id]
        for key, value in data.items():
            if key == "accumulated_entities":
                merged = dict(current.get("accumulated_entities", {}))
                merged.update(value or {})
                current[key] = merged
            else:
                current[key] = value
        current["turn_count"] = int(current.get("turn_count", 0)) + 1

    def clear(self, session_id: str) -> None:
        self._store.pop(session_id, None)
