from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from demo_agent.knowledge.chunker import chunk_documents
from demo_agent.knowledge.loader import load_markdown_documents
from demo_agent.schemas.models import DocumentChunk, RetrievalResult


DOMAIN_TERMS = [
    "退款", "退货", "售后", "赔付", "补偿", "物流", "配送", "订单", "到货",
    "账户", "地址", "身份证", "客服", "工单", "投诉", "发票", "保修", "会员",
    "耳机", "净化器", "咖啡机", "滤芯", "质保", "优惠", "活动",
]
STOP_TERMS = {"规则", "政策", "流程", "时间", "客服", "商品", "问题"}


class KeywordRetriever:
    """Small deterministic retriever for local MVP tests."""

    # 用途：在不依赖外部向量库或 LLM 的情况下，对本地知识库片段做确定性关键词检索。

    def __init__(self, chunks: list[DocumentChunk]):
        self.chunks = chunks
        self._chunk_terms = {chunk.citation: Counter(tokenize(chunk.content + " " + chunk.title)) for chunk in chunks}

    @classmethod
    def from_kb_dir(cls, kb_dir: str | Path) -> "KeywordRetriever":
        documents = load_markdown_documents(kb_dir)
        return cls(chunk_documents(documents))

    def search(self, query: str, top_k: int = 3) -> list[RetrievalResult]:
        query_terms = Counter(tokenize(query))
        if not query_terms:
            return []

        scored: list[RetrievalResult] = []
        for chunk in self.chunks:
            score = self._score(query, query_terms, chunk)
            if score > 0:
                scored.append(RetrievalResult(chunk=chunk, score=score))

        scored.sort(key=lambda item: (-item.score, item.chunk.source, item.chunk.chunk_id))
        return scored[:top_k]

    def _score(self, query: str, query_terms: Counter[str], chunk: DocumentChunk) -> float:
        terms = self._chunk_terms[chunk.citation]
        score = 0.0
        for term, count in query_terms.items():
            if term in STOP_TERMS:
                continue
            if term in terms:
                score += min(count, 3) * (1.0 + min(terms[term], 3) * 0.2)

        content = chunk.content.lower()
        normalized_query = query.lower()
        for term in DOMAIN_TERMS:
            if term in normalized_query and term in content:
                score += 2.5

        if any(term in query for term in ["物流", "配送", "到货", "送达"]) and chunk.source == "logistics.md":
            score += 4.0
        if any(term in query for term in ["退款", "退货", "售后退款"]) and chunk.source == "refund_policy.md":
            score += 4.0
        if any(term in query for term in ["保修", "质保", "商品", "滤芯", "耳机", "咖啡机", "净化器"]) and chunk.source == "products.md":
            score += 4.0
        if any(term in query for term in ["会员", "账户", "发票", "地址"]) and chunk.source == "member_account.md":
            score += 4.0
        if any(term in query for term in ["承诺", "赔付", "内部价", "当天必达", "隐私"]) and chunk.source == "compliance_rules.md":
            score += 4.0

        if "什么时候" in query and ("到货" in content or "预计送达" in content):
            score += 2.0
        return score


def tokenize(text: str) -> list[str]:
    normalized = text.lower()
    tokens = re.findall(r"[a-z0-9]+", normalized)
    tokens.extend(term for term in DOMAIN_TERMS if term in normalized)

    chinese = re.findall(r"[\u4e00-\u9fff]{2,}", normalized)
    for segment in chinese:
        tokens.extend(segment[i : i + 2] for i in range(max(len(segment) - 1, 0)))

    return tokens
