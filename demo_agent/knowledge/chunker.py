from __future__ import annotations

import re

from demo_agent.schemas.models import Document, DocumentChunk


def chunk_documents(documents: list[Document], max_chars: int = 650) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for doc in documents:
        sections = _split_sections(doc.text)
        counter = 1
        for title, body in sections:
            paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
            current = ""
            for para in paragraphs:
                if current and len(current) + len(para) + 2 > max_chars:
                    chunks.append(_make_chunk(doc.source, counter, title, current))
                    counter += 1
                    current = para
                else:
                    current = para if not current else f"{current}\n\n{para}"
            if current:
                chunks.append(_make_chunk(doc.source, counter, title, current))
                counter += 1
    return chunks


def _split_sections(text: str) -> list[tuple[str, str]]:
    current_title = "general"
    current_lines: list[str] = []
    sections: list[tuple[str, str]] = []

    for line in text.splitlines():
        if line.startswith("#"):
            if current_lines:
                sections.append((current_title, "\n".join(current_lines).strip()))
                current_lines = []
            current_title = line.lstrip("#").strip() or "general"
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_title, "\n".join(current_lines).strip()))

    return sections or [("general", text)]


def _make_chunk(source: str, index: int, title: str, content: str) -> DocumentChunk:
    return DocumentChunk(
        source=source,
        chunk_id=f"chunk-{index}",
        title=title,
        content=content.strip(),
    )

