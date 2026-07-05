from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


IntentName = Literal["presales", "knowledge", "order", "logistics", "aftersales", "ticket", "compliance", "clarify"]


@dataclass(frozen=True)
class Document:
    """表示从企业知识库文件中读取的一份原始文档。"""

    source: str
    text: str


@dataclass(frozen=True)
class DocumentChunk:
    """表示文档切分后的检索片段，携带来源、标题和引用标识。"""

    source: str
    chunk_id: str
    title: str
    content: str

    @property
    def citation(self) -> str:
        return f"{self.source}#{self.chunk_id}"


@dataclass(frozen=True)
class RetrievalResult:
    """表示一次知识库检索命中的片段及其相关性分数。"""

    chunk: DocumentChunk
    score: float


@dataclass
class IntentResult:
    """表示意图识别 Agent 对用户消息的分类、置信度和实体提取结果。"""

    intent: IntentName
    confidence: float
    entities: dict[str, str] = field(default_factory=dict)
    reason: str = ""


@dataclass
class ToolCall:
    """记录一次企业工具调用的名称、入参、结果和执行状态。"""

    name: str
    arguments: dict[str, Any]
    result: dict[str, Any]
    success: bool = True
    error: str | None = None


@dataclass
class AgentResponse:
    """封装业务 Agent 输出，包括回复文本、知识引用、工具调用和附加元数据。"""

    response: str
    sources: list[str] = field(default_factory=list)
    tool_calls: list[ToolCall] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
