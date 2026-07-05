from __future__ import annotations

import uuid

try:
    from fastapi import FastAPI
    from pydantic import BaseModel
except ImportError:  # pragma: no cover
    FastAPI = None
    BaseModel = object

from demo_agent.agents.supervisor import Supervisor


supervisor = Supervisor()


if FastAPI is not None:
    app = FastAPI(title="demoAgent", version="0.1.0")

    class ChatRequest(BaseModel):
        message: str
        user_id: str = "anonymous"
        session_id: str | None = None

    @app.post("/api/chat")
    def chat(request: ChatRequest) -> dict:
        return supervisor.chat(
            request.message,
            user_id=request.user_id,
            session_id=request.session_id or f"api-{uuid.uuid4().hex[:8]}",
        )

    @app.get("/health")
    def health() -> dict:
        return {"status": "healthy", "version": "0.1.0"}
else:
    app = None


def main() -> None:
    if app is None:
        raise RuntimeError("fastapi and uvicorn are required for API mode")
    import uvicorn

    uvicorn.run("demo_agent.app:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()

