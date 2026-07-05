from __future__ import annotations

from pathlib import Path

from demo_agent.schemas.models import Document


def load_markdown_documents(kb_dir: str | Path) -> list[Document]:
    """Load all Markdown files from a knowledge base directory."""
    root = Path(kb_dir)
    if not root.exists():
        return []

    documents: list[Document] = []
    for path in sorted(root.glob("*.md")):
        text = path.read_text(encoding="utf-8").strip()
        if text:
            documents.append(Document(source=path.name, text=text))
    return documents

