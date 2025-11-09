from __future__ import annotations

from typing import List

from langchain_core.documents import Document

from .api_client import PostDTO


def compose_post_text(post: PostDTO) -> str:
    """왜: 임베딩 품질을 위해 검색에 유의미한 필드를 일관된 포맷으로 합성한다."""
    tags = ", ".join(post.tags or [])
    cats = ", ".join(post.categories or [])
    lines = [
        f"제목: {post.title}",
        f"요약: {post.summary}",
        f"태그: {tags}" if tags else "태그: 없음",
        f"카테고리: {cats}" if cats else "카테고리: 없음",
        f"블로그: {post.blog_name}",
        f"링크: {post.link}",
    ]
    return "\n".join(lines)


def to_document(post: PostDTO) -> Document:
    return Document(
        page_content=compose_post_text(post),
        metadata={
            "id": post.id,
            "title": post.title,
            "link": post.link,
            "tags": ", ".join(post.tags or []),
            "categories": ", ".join(post.categories or []),
            "blog_name": post.blog_name,
            "published_at": post.published_at,
        },
    )


def format_docs_for_prompt(docs: List[Document]) -> str:
    parts = []
    for d in docs:
        title = d.metadata.get("title", "(제목 없음)")
        link = d.metadata.get("link", "")
        parts.append(f"- {title} — {link}\n  {d.page_content}")
    return "\n\n".join(parts)
