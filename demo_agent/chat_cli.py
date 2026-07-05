from __future__ import annotations

import uuid

from demo_agent.agents.supervisor import Supervisor


def main() -> None:
    supervisor = Supervisor()
    session_id = f"cli-{uuid.uuid4().hex[:8]}"
    print(f"demoAgent CLI session={session_id}")
    print("输入 exit 退出。")
    while True:
        message = input("> ").strip()
        if message.lower() in {"exit", "quit"}:
            break
        result = supervisor.chat(message, user_id="cli_user", session_id=session_id)
        print(result["response"])
        if result["sources"]:
            print("sources:", ", ".join(result["sources"]))


if __name__ == "__main__":
    main()

