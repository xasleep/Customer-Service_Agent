from __future__ import annotations


class RiskTool:
    """根据动作和金额用固定规则模拟企业风控风险分级。"""

    def check(self, user_id: str, action: str, amount: float = 0.0) -> dict:
        if amount >= 50000:
            risk_level = "high"
        elif amount >= 10000:
            risk_level = "medium"
        else:
            risk_level = "low"
        return {
            "user_id": user_id,
            "action": action,
            "amount": amount,
            "risk_level": risk_level,
            "requires_manual_review": risk_level == "high",
        }
