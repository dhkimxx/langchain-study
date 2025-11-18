from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Optional, List

from utils.logger import get_logger
from utils.api_client import TechLetterClient, PostDTO
from utils.data_loader import fetch_all_posts, filter_posts_by_datetime_range
from chains.newsletter_chain import build_newsletter_chain
from chains.factory import new_chat
from utils.app_config import CONFIG


logger = get_logger(__name__)
_KST = timezone(timedelta(hours=9))


@dataclass
class NewsletterResult:
    content: str
    selected_count: int
    total_count: int


def _parse_cli_date(date_str: Optional[str]) -> Optional[datetime]:
    if not date_str:
        return None
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.replace(tzinfo=_KST)
    except Exception as e:
        raise ValueError(f"날짜 파싱 실패(YYYY-MM-DD 기대): {date_str}") from e


def _format_posts_for_context(posts: List[PostDTO]) -> str:
    parts: List[str] = []
    for p in posts:
        tags = ", ".join(p.tags or [])
        parts.append(
            f"- {p.title} — {p.link}\n" f"  요약: {p.summary}\n" f"  태그: {tags}"
        )
    return "\n".join(parts)


def generate_ai_weekly_newsletter(
    *,
    days: int = 7,
    start: Optional[str] = None,
    end: Optional[str] = None,
    limit: int = 100,
) -> NewsletterResult:
    """왜: 최근 기간의 포스트를 요약한 주간 뉴스레터 콘텐츠를 생성한다."""
    client = TechLetterClient(base_url=CONFIG.techletter_base_url)

    end_dt = _parse_cli_date(end) or datetime.now(tz=_KST)
    start_dt = _parse_cli_date(start) or (end_dt - timedelta(days=days))

    all_posts = fetch_all_posts(client)
    ranged = filter_posts_by_datetime_range(all_posts, start_dt, end_dt)

    def _sort_key(p: PostDTO):
        return -(p.view_count or 0)

    ranged.sort(key=_sort_key)
    selected = ranged[: max(1, limit)]

    if not selected:
        logger.warning("선택된 포스트가 없습니다. 조건을 완화해 보세요.")

    context = _format_posts_for_context(selected)

    chat_cfg = CONFIG.get_chain_config("chat")
    llm = new_chat(
        chat_cfg["provider"],
        chat_cfg["model_name"],
        temperature=0.3,
        api_key=chat_cfg.get("api_key"),
    )
    chain = build_newsletter_chain(llm)
    rendered = chain.invoke(
        {
            "start": start_dt.strftime("%Y-%m-%d"),
            "end": end_dt.strftime("%Y-%m-%d"),
            "context": context,
        }
    )

    return NewsletterResult(
        content=rendered, selected_count=len(selected), total_count=len(ranged)
    )
