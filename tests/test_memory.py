from demo_agent.memory.session_memory import SessionMemory


def test_memory_merges_entities_and_is_session_scoped():
    memory = SessionMemory()

    memory.update("s1", {"accumulated_entities": {"order_id": "ORD1001"}, "last_order_id": "ORD1001"})
    memory.update("s1", {"accumulated_entities": {"product": "智能净化器"}})

    s1 = memory.get("s1")
    s2 = memory.get("s2")

    assert s1["accumulated_entities"] == {"order_id": "ORD1001", "product": "智能净化器"}
    assert s1["turn_count"] == 2
    assert s2 == {}

