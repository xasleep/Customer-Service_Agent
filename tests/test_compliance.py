from demo_agent.agents.compliance import ComplianceAgent, mask_pii


def test_compliance_masks_phone_number():
    assert mask_pii("我的手机号是13812345678") == "我的手机号是138*****678"


def test_compliance_blocks_forbidden_claim():
    passed, response, violations = ComplianceAgent().review("这个订单当天必达，质量问题百分百赔付。")

    assert passed is False
    assert "未授权服务承诺" in response
    assert any(item.startswith("FORBIDDEN_CLAIM") for item in violations)


def test_compliance_allows_negated_claim_rule():
    passed, response, violations = ComplianceAgent().review("客服不得承诺当天必达。")

    assert passed is True
    assert response == "客服不得承诺当天必达。"
    assert violations == []
