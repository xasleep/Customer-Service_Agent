from __future__ import annotations

import re

from demo_agent.schemas.models import IntentResult


ORDER_RE = re.compile(r"\bORD\d{4,}\b", re.IGNORECASE)
TICKET_RE = re.compile(r"\bTK-[A-Z0-9-]+\b", re.IGNORECASE)
REQUEST_RE = re.compile(r"\bRR\d{4,}\b", re.IGNORECASE)
TRACKING_RE = re.compile(r"\b(?:SF|YT)\d{8,}\b", re.IGNORECASE)


class IntentAgent:
    """用规则识别用户意图，并抽取订单号、工单号和产品名等关键实体。"""

    def classify(self, message: str, memory: dict | None = None) -> IntentResult:
        memory = memory or {}
        text = message.lower()
        entities = self.extract_entities(message)

        if any(term in message for term in ["申请退款", "帮我退款", "帮我申请", "创建工单", "投诉", "理赔", "转人工"]):
            return IntentResult("ticket", 0.88, entities, "business action wording")

        if any(term in message for term in ["物流", "快递", "包裹", "配送进度", "到哪里", "运到哪"]):
            if "退款政策" not in message and "退货政策" not in message:
                return IntentResult("logistics", 0.9, entities, "logistics wording")

        if any(term in message for term in ["售后进度", "售后状态", "退款进度", "退货进度", "换货进度", "售后单"]):
            return IntentResult("aftersales", 0.88, entities, "after-sales status wording")

        if any(term in message for term in ["库存", "有货", "多少钱", "价格", "参数", "推荐", "适合买吗", "怎么买"]):
            return IntentResult("presales", 0.86, entities, "presales product wording")

        if "订单" in message or ("到" in message and memory.get("last_order_id")):
            if "退款政策" not in message and "退货政策" not in message:
                return IntentResult("order", 0.9, entities, "order or logistics wording")

        if any(term in message for term in ["内部价", "百分百赔付", "一定补偿", "当天必达", "身份证号", "支付卡号"]):
            return IntentResult("compliance", 0.92, entities, "compliance-sensitive wording")

        if any(term in message for term in ["政策", "规则", "流程", "产品", "商品", "退款", "退货", "配送", "保修", "会员", "发票", "售后"]):
            return IntentResult("knowledge", 0.84, entities, "knowledge wording")

        if len(message.strip()) < 4:
            return IntentResult("clarify", 0.4, entities, "message too short")

        return IntentResult("knowledge", 0.55, entities, "default to knowledge with low confidence")

    def extract_entities(self, message: str) -> dict[str, str]:
        entities: dict[str, str] = {}
        order = ORDER_RE.search(message)
        if order:
            entities["order_id"] = order.group(0).upper()
        ticket = TICKET_RE.search(message)
        if ticket:
            entities["ticket_id"] = ticket.group(0).upper()
        request = REQUEST_RE.search(message)
        if request:
            entities["request_id"] = request.group(0).upper()
        tracking = TRACKING_RE.search(message)
        if tracking:
            entities["tracking_no"] = tracking.group(0).upper()
        for product in ["智能净化器", "降噪耳机", "胶囊咖啡机"]:
            if product.lower() in message.lower():
                entities["product"] = product
                break
        return entities
