from pathlib import Path

from demo_agent.knowledge.retriever import KeywordRetriever


ROOT = Path(__file__).resolve().parents[1]


def test_retriever_loads_virtual_knowledge_base():
    retriever = KeywordRetriever.from_kb_dir(ROOT / "data" / "knowledge_base")

    assert len(retriever.chunks) >= 6
    assert {chunk.source for chunk in retriever.chunks} >= {
        "products.md",
        "refund_policy.md",
        "logistics.md",
        "member_account.md",
        "compliance_rules.md",
        "support_sop.md",
    }


def test_refund_query_returns_refund_policy_source():
    retriever = KeywordRetriever.from_kb_dir(ROOT / "data" / "knowledge_base")

    results = retriever.search("退款政策是怎样的？")

    assert results
    assert results[0].chunk.source == "refund_policy.md"


def test_logistics_query_returns_logistics_source():
    retriever = KeywordRetriever.from_kb_dir(ROOT / "data" / "knowledge_base")

    results = retriever.search("配送和到货时间规则")

    assert results
    assert results[0].chunk.source == "logistics.md"
