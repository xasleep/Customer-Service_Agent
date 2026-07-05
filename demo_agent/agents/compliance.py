from __future__ import annotations

import re


PII_PATTERNS = [
    re.compile(r"1[3-9]\d{9}"),
    re.compile(r"\d{17}[\dXx]"),
    re.compile(r"\d{16,19}"),
]
FORBIDDEN_CLAIMS = ["内部价", "百分百赔付", "一定补偿", "当天必达", "绝对正品", "无条件退款"]
SAFE_PREFIXES = ["不", "不能", "不得", "禁止", "无法", "不会", "未"]


class ComplianceAgent:
    """负责审查最终回复，执行 PII 脱敏和电商客服禁用承诺拦截。"""

    def review(self, content: str) -> tuple[bool, str, list[str]]:
        violations: list[str] = []
        sanitized = mask_pii(content)
        if sanitized != content:
            violations.append("PII_MASKED")

        for claim in FORBIDDEN_CLAIMS:
            if claim in content and not _is_negated(content, claim):
                violations.append(f"FORBIDDEN_CLAIM:{claim}")

        if any(v.startswith("FORBIDDEN_CLAIM") for v in violations):
            return (
                False,
                "该回复涉及未授权服务承诺，已转人工客服处理。客服不能承诺未发布优惠、固定赔付或确定送达时间。",
                violations,
            )

        return True, sanitized, violations


def mask_pii(content: str) -> str:
    masked = content
    for pattern in PII_PATTERNS:
        masked = pattern.sub(lambda m: _mask_value(m.group(0)), masked)
    return masked


def _mask_value(value: str) -> str:
    if len(value) <= 6:
        return "*" * len(value)
    return value[:3] + "*" * (len(value) - 6) + value[-3:]


def _is_negated(content: str, claim: str) -> bool:
    index = content.find(claim)
    if index < 0:
        return False
    prefix = content[max(0, index - 4) : index]
    return any(marker in prefix for marker in SAFE_PREFIXES)
