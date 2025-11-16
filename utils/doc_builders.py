from __future__ import annotations

from typing import Dict, List

from langchain_core.documents import Document

from .api_client import PostDTO


def build_document_from_full_text(post: PostDTO, full_text: str) -> Document:
    """왜: 요약이 아닌 실제 본문 텍스트를 기반으로 임베딩 품질을 높이기 위함."""
    tags = ", ".join(post.tags or [])
    cats = ", ".join(post.categories or [])
    content = full_text.strip()

    metadata: Dict[str, str] = {
        "id": post.id,
        "title": post.title,
        "link": post.link,
        "blog_name": post.blog_name,
        "published_at": post.published_at,
        "tags": tags,
        "categories": cats,
    }
    return Document(page_content=content, metadata=metadata)


def format_docs_for_deep_prompt(docs: List[Document], max_chars: int = 1500) -> str:
    """왜: LLM 컨텍스트 과다를 막고 핵심만 전달하기 위해 스니펫을 생성한다."""
    parts: List[str] = []
    for d in docs:
        title = d.metadata.get("title", "(제목 없음)")
        link = d.metadata.get("link", "")
        text = d.page_content or ""
        snippet = text[:max_chars].rstrip()
        parts.append(f"- {title} — {link}\n  스니펫: {snippet}")
    return "\n\n".join(parts)
