from __future__ import annotations

from pathlib import Path

from demo_agent.tools.base import load_json


class ProductTool:
    """基于本地商品 fixture 提供售前商品查询能力。"""

    def __init__(self, fixtures_dir: str | Path):
        products = load_json(Path(fixtures_dir) / "products.json", [])
        self.products = {item["product_id"]: item for item in products}
        self._by_name = {item["name"]: item for item in products}

    def query(self, product: str | None = None) -> dict:
        if not product:
            return {"found": True, "items": list(self.products.values())}

        normalized = product.lower()
        for item in self.products.values():
            if normalized in item["name"].lower() or item["name"].lower() in normalized:
                return {"found": True, **item}

        return {"found": False, "product": product}
