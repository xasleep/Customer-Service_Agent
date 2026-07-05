from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Protocol


class ModelClient(Protocol):
    """Small interface used by Supervisor to polish grounded tool responses."""

    def polish(self, payload: dict[str, Any]) -> str:
        """Return a customer-service reply based on structured context."""


class ModelUnavailableError(RuntimeError):
    """Raised when the configured model adapter cannot produce a reply."""


class HttpChatModelClient:
    """Minimal OpenAI-compatible HTTP chat adapter.

    The endpoint is intentionally configurable because `opai-gpt5.4` is treated
    as an environment-specific model id in this demo.
    """

    def __init__(self, endpoint: str, api_key: str, model_name: str, timeout_seconds: float = 15.0) -> None:
        self.endpoint = endpoint
        self.api_key = api_key
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds

    @classmethod
    def from_env(cls, model_name: str) -> "HttpChatModelClient | None":
        endpoint = os.getenv("OPAI_BASE_URL") or os.getenv("OPAI_CHAT_ENDPOINT")
        api_key = os.getenv("OPAI_API_KEY")
        if not endpoint or not api_key:
            return None
        return cls(endpoint=endpoint, api_key=api_key, model_name=os.getenv("MODEL_NAME", model_name))

    def polish(self, payload: dict[str, Any]) -> str:
        body = {
            "model": self.model_name,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是电商平台买家自助客服。只基于给定结构化结果回复，"
                        "不要虚构库存、物流、退款或赔付承诺。"
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(payload, ensure_ascii=False),
                },
            ],
        }
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
            raise ModelUnavailableError(str(exc)) from exc

        text = _extract_text(data)
        if not text:
            raise ModelUnavailableError("model response did not contain text")
        return text


def _extract_text(data: dict[str, Any]) -> str:
    choices = data.get("choices")
    if isinstance(choices, list) and choices:
        message = choices[0].get("message", {})
        if isinstance(message, dict) and isinstance(message.get("content"), str):
            return message["content"]
        if isinstance(choices[0].get("text"), str):
            return choices[0]["text"]

    for key in ("output_text", "response", "text"):
        if isinstance(data.get(key), str):
            return data[key]
    return ""
