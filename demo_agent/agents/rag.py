from __future__ import annotations

import re

from demo_agent.knowledge.retriever import KeywordRetriever
from demo_agent.schemas.models import AgentResponse


class RAGAgent:
    """负责从企业知识库检索相关片段，并生成带来源引用的知识型回复。"""

    def __init__(self, retriever: KeywordRetriever):
        self.retriever = retriever

    def answer(self, query: str) -> AgentResponse:
        results = self.retriever.search(query, top_k=3)
        if not results:
            return AgentResponse(
                response="知识库中没有找到足够可靠的信息，建议转人工客服确认。",
                sources=[],
                metadata={"retrieval_count": 0},
            )

        top = results[0].chunk
        snippets = _select_relevant_sentences(top.content, query)
        response = f"{snippets}\n\n来源：{top.citation}"
        return AgentResponse(
            response=response,
            sources=[item.chunk.citation for item in results],
            metadata={"retrieval_count": len(results), "top_score": results[0].score},
        )


def _select_relevant_sentences(content: str, query: str) -> str:
    sentences = [part.strip() for part in re.split(r"(?<=[。！？.!?])\s*", content) if part.strip()]
    if not sentences:
        return content[:400]

    keywords = [kw for kw in ["退款", "退货", "物流", "配送", "商品", "售后", "保修", "会员", "发票", "地址"] if kw in query]
    selected = [s for s in sentences if any(kw in s for kw in keywords)]
    if not selected:
        selected = sentences[:2]
    return " ".join(selected[:3])
