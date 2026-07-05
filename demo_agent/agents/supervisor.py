from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from demo_agent.agents.compliance import ComplianceAgent
from demo_agent.agents.intent import IntentAgent
from demo_agent.agents.rag import RAGAgent
from demo_agent.agents.tool_agent import ToolAgent
from demo_agent.knowledge.retriever import KeywordRetriever
from demo_agent.memory.session_memory import SessionMemory
from demo_agent.schemas.models import AgentResponse
from demo_agent.schemas.state import GraphState
from demo_agent.tools.registry import ToolRegistry

try:  # pragma: no cover - exercised when langgraph is installed locally.
    from langgraph.graph import END, StateGraph
except ImportError:  # pragma: no cover - keeps local deterministic tests runnable.
    END = "__end__"
    StateGraph = None


PROJECT_ROOT = Path(__file__).resolve().parents[2]
HIGH_VALUE_ORDER_THRESHOLD = 5000.0


class _FallbackGraph:
    """Small local runner used only when LangGraph is not installed."""

    def __init__(self, supervisor: "Supervisor") -> None:
        self.supervisor = supervisor

    def invoke(self, initial_state: GraphState) -> GraphState:
        state: GraphState = dict(initial_state)
        for node in (self.supervisor._init_context, self.supervisor._classify_intent):
            state.update(node(state))

        business_route = self.supervisor._route_after_intent(state)
        business_nodes = {
            "clarify": self.supervisor._clarify_node,
            "presales": self.supervisor._presales_node,
            "order": self.supervisor._order_node,
            "logistics": self.supervisor._logistics_node,
            "aftersales": self.supervisor._aftersales_node,
            "ticket": self.supervisor._ticket_node,
            "knowledge": self.supervisor._knowledge_node,
        }
        state.update(business_nodes[business_route](state))

        for node in (self.supervisor._risk_review, self.supervisor._compliance_review):
            state.update(node(state))

        generation_route = self.supervisor._route_after_compliance(state)
        generation_nodes = {
            "llm_polish": self.supervisor._llm_polish,
            "template_fallback": self.supervisor._template_fallback,
        }
        state.update(generation_nodes[generation_route](state))

        for node in (self.supervisor._synthesize, self.supervisor._update_memory):
            state.update(node(state))

        return state


class Supervisor:
    """LangGraph 驱动的电商客服中央编排器。"""

    def __init__(
        self,
        retriever: KeywordRetriever | None = None,
        tools: ToolRegistry | None = None,
        memory: SessionMemory | None = None,
        model_name: str = "opai-gpt5.4",
        model_client: Any | None = None,
        high_value_order_threshold: float = HIGH_VALUE_ORDER_THRESHOLD,
    ):
        self.memory = memory or SessionMemory()
        self.model_name = model_name
        self.model_client = model_client
        self.high_value_order_threshold = high_value_order_threshold
        self.intent_agent = IntentAgent()
        self.rag_agent = RAGAgent(retriever or KeywordRetriever.from_kb_dir(PROJECT_ROOT / "data" / "knowledge_base"))
        self.tool_agent = ToolAgent(tools or ToolRegistry(PROJECT_ROOT / "data" / "fixtures"))
        self.compliance_agent = ComplianceAgent()
        self.graph = self._build_graph()

    def chat(self, message: str, user_id: str = "anonymous", session_id: str = "default") -> dict:
        initial_state: GraphState = {"message": message, "user_id": user_id, "session_id": session_id}
        final_state = self.graph.invoke(initial_state)
        return final_state["response_payload"]

    def _build_graph(self):
        if StateGraph is None:
            return _FallbackGraph(self)

        graph = StateGraph(GraphState)
        graph.add_node("init_context", self._init_context)
        graph.add_node("classify_intent", self._classify_intent)
        graph.add_node("clarify", self._clarify_node)
        graph.add_node("presales", self._presales_node)
        graph.add_node("order", self._order_node)
        graph.add_node("logistics", self._logistics_node)
        graph.add_node("aftersales", self._aftersales_node)
        graph.add_node("ticket", self._ticket_node)
        graph.add_node("knowledge", self._knowledge_node)
        graph.add_node("risk_review", self._risk_review)
        graph.add_node("compliance_review", self._compliance_review)
        graph.add_node("llm_polish", self._llm_polish)
        graph.add_node("template_fallback", self._template_fallback)
        graph.add_node("synthesize", self._synthesize)
        graph.add_node("update_memory", self._update_memory)

        graph.set_entry_point("init_context")
        graph.add_edge("init_context", "classify_intent")
        graph.add_conditional_edges(
            "classify_intent",
            self._route_after_intent,
            {
                "clarify": "clarify",
                "presales": "presales",
                "order": "order",
                "logistics": "logistics",
                "aftersales": "aftersales",
                "ticket": "ticket",
                "knowledge": "knowledge",
            },
        )
        graph.add_edge("clarify", "risk_review")
        graph.add_edge("presales", "risk_review")
        graph.add_edge("order", "risk_review")
        graph.add_edge("logistics", "risk_review")
        graph.add_edge("aftersales", "risk_review")
        graph.add_edge("ticket", "risk_review")
        graph.add_edge("knowledge", "risk_review")
        graph.add_edge("risk_review", "compliance_review")
        graph.add_conditional_edges(
            "compliance_review",
            self._route_after_compliance,
            {
                "llm_polish": "llm_polish",
                "template_fallback": "template_fallback",
            },
        )
        graph.add_edge("llm_polish", "synthesize")
        graph.add_edge("template_fallback", "synthesize")
        graph.add_edge("synthesize", "update_memory")
        graph.add_edge("update_memory", END)
        return graph.compile()

    def _init_context(self, state: GraphState) -> GraphState:
        session_id = state.get("session_id", "default")
        return {
            "memory_snapshot": self.memory.get(session_id),
            "current_node": "init_context",
        }

    def _classify_intent(self, state: GraphState) -> GraphState:
        memory = state.get("memory_snapshot", {})
        intent = self.intent_agent.classify(state["message"], memory)
        if memory.get("last_order_id") and "order_id" not in intent.entities:
            intent.entities["order_id"] = memory["last_order_id"]
        return {
            "intent_result": intent,
            "current_node": "classify_intent",
        }

    def _route_after_intent(self, state: GraphState) -> str:
        intent = state.get("intent_result")
        if intent is None or intent.intent == "clarify" or intent.confidence < 0.5:
            return "clarify"
        if intent.intent in {"presales", "order", "logistics", "aftersales", "ticket"}:
            return intent.intent
        return "knowledge"

    def _clarify_node(self, state: GraphState) -> GraphState:
        return {
            "agent_response": AgentResponse("请补充说明您要咨询的产品、订单号或需要办理的业务。"),
            "current_node": "clarify",
        }

    def _presales_node(self, state: GraphState) -> GraphState:
        intent = state["intent_result"]
        response = self.tool_agent.handle_presales(intent.entities.get("product"))
        return {
            "agent_response": response,
            "current_node": "presales",
        }

    def _order_node(self, state: GraphState) -> GraphState:
        intent = state["intent_result"]
        entities = intent.entities
        order_id = entities.get("order_id")
        if not order_id:
            response = AgentResponse("请提供订单号，例如 ORD1001。")
        else:
            response = self.tool_agent.handle_order(state["user_id"], order_id)
        return {
            "agent_response": response,
            "current_node": "order",
        }

    def _logistics_node(self, state: GraphState) -> GraphState:
        intent = state["intent_result"]
        response = self.tool_agent.handle_logistics(
            order_id=intent.entities.get("order_id"),
            tracking_no=intent.entities.get("tracking_no"),
        )
        return {
            "agent_response": response,
            "current_node": "logistics",
        }

    def _aftersales_node(self, state: GraphState) -> GraphState:
        intent = state["intent_result"]
        response = self.tool_agent.handle_after_sales(
            order_id=intent.entities.get("order_id"),
            request_id=intent.entities.get("request_id"),
        )
        return {
            "agent_response": response,
            "current_node": "aftersales",
        }

    def _ticket_node(self, state: GraphState) -> GraphState:
        intent = state["intent_result"]
        order_id = intent.entities.get("order_id")
        category = "refund" if "退" in state["message"] else "general"
        response = self.tool_agent.create_ticket(state["user_id"], category, state["message"], order_id=order_id)
        return {
            "agent_response": response,
            "current_node": "ticket",
        }

    def _knowledge_node(self, state: GraphState) -> GraphState:
        return {
            "agent_response": self.rag_agent.answer(state["message"]),
            "current_node": "knowledge",
        }

    def _risk_review(self, state: GraphState) -> GraphState:
        reasons: list[str] = []
        message = state["message"]
        response = state.get("agent_response")
        intent = state.get("intent_result")

        if response:
            for call in response.tool_calls:
                if not call.success:
                    reasons.append("information_missing")
                amount = call.result.get("amount", call.result.get("price"))
                if isinstance(amount, (int, float)) and amount >= self.high_value_order_threshold:
                    reasons.append("high_value_order")

        if intent and intent.intent in {"ticket", "aftersales"} and any(term in message for term in ["投诉", "纠纷", "理赔", "赔偿", "退款失败"]):
            reasons.append("sensitive_after_sales")

        if any(term in message for term in ["投诉", "生气", "愤怒", "差评", "曝光", "报警", "骗子"]):
            reasons.append("strong_negative_emotion")

        deduped = list(dict.fromkeys(reasons))
        return {
            "need_handoff": bool(deduped),
            "risk_reasons": deduped,
            "current_node": "risk_review",
        }

    def _compliance_review(self, state: GraphState) -> GraphState:
        response = state.get("agent_response") or AgentResponse("抱歉，暂时无法处理您的请求，请稍后重试。")
        passed, reviewed_response, violations = self.compliance_agent.review(response.response)
        risk_reasons = list(state.get("risk_reasons", []))
        if not passed and "compliance_failed" not in risk_reasons:
            risk_reasons.append("compliance_failed")
        return {
            "compliance_passed": passed,
            "compliance_violations": violations,
            "final_response": reviewed_response,
            "sources": response.sources,
            "tool_calls": [asdict(call) for call in response.tool_calls],
            "need_handoff": state.get("need_handoff", False) or not passed,
            "risk_reasons": risk_reasons,
            "current_node": "compliance_review",
        }

    def _route_after_compliance(self, state: GraphState) -> str:
        if self.model_client is not None and state.get("compliance_passed", True):
            return "llm_polish"
        return "template_fallback"

    def _llm_polish(self, state: GraphState) -> GraphState:
        return {
            "generation_mode": f"llm:{self.model_name}",
            "current_node": "llm_polish",
        }

    def _template_fallback(self, state: GraphState) -> GraphState:
        response = state.get("final_response")
        if not response and state.get("agent_response"):
            response = state["agent_response"].response
        return {
            "final_response": response or "抱歉，暂时无法处理您的请求，请稍后重试。",
            "generation_mode": "template_fallback",
            "current_node": "template_fallback",
        }

    def _synthesize(self, state: GraphState) -> GraphState:
        intent = state["intent_result"]
        payload = {
            "response": state.get("final_response", ""),
            "intent": intent.intent,
            "confidence": intent.confidence,
            "session_id": state["session_id"],
            "compliance_passed": state.get("compliance_passed", True),
            "compliance_violations": state.get("compliance_violations", []),
            "sources": state.get("sources", []),
            "tool_calls": state.get("tool_calls", []),
            "need_handoff": state.get("need_handoff", False),
            "risk_reasons": state.get("risk_reasons", []),
            "generation_mode": state.get("generation_mode", "template_fallback"),
            "model": self.model_name,
        }
        return {
            "response_payload": payload,
            "current_node": "synthesize",
        }

    def _update_memory(self, state: GraphState) -> GraphState:
        intent = state["intent_result"]
        data = {
            "last_intent": intent.intent,
            "accumulated_entities": intent.entities,
        }
        if "order_id" in intent.entities:
            data["last_order_id"] = intent.entities["order_id"]
        if "product" in intent.entities:
            data["last_product"] = intent.entities["product"]
        if "request_id" in intent.entities:
            data["last_request_id"] = intent.entities["request_id"]
        if "tracking_no" in intent.entities:
            data["last_tracking_no"] = intent.entities["tracking_no"]
        self.memory.update(state["session_id"], data)
        return {
            "memory_updated": True,
            "current_node": "update_memory",
        }
