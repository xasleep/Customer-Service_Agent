from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TypedDict

from demo_agent.schemas.models import AgentResponse, IntentResult


@dataclass
class ChatState:
    """保存单轮聊天在 Supervisor 编排链路中的状态数据。"""

    message: str
    user_id: str
    session_id: str
    intent_result: IntentResult | None = None
    agent_response: AgentResponse | None = None
    compliance_passed: bool = True
    final_response: str = ""
    sources: list[str] = field(default_factory=list)
    tool_calls: list[dict] = field(default_factory=list)


class GraphState(TypedDict, total=False):
    """LangGraph 编排链路中的共享状态。"""

    message: str
    user_id: str
    session_id: str
    memory_snapshot: dict[str, Any]
    intent_result: IntentResult
    agent_response: AgentResponse
    compliance_passed: bool
    compliance_violations: list[str]
    final_response: str
    sources: list[str]
    tool_calls: list[dict[str, Any]]
    need_handoff: bool
    risk_reasons: list[str]
    current_node: str
    generation_mode: str
    model_error: str
    handoff_ticket: dict[str, Any]
    response_payload: dict[str, Any]
    memory_updated: bool
