from __future__ import annotations

from typing import Iterable, List, Optional, Tuple

from .api_client import TechLetterClient, PaginationPostDTO, PostDTO
from .date_utils import parse_published_at


def fetch_all_posts(client: TechLetterClient, page_size: int = 100, page_limit: Optional[int] = None) -> List[PostDTO]:
    """왜: 공통 페이지네이션 수집 로직을 재사용해 일관성과 중복 제거.
    page_limit로 최대 페이지를 제한할 수 있음.
    """
    page = 1
    results: List[PostDTO] = []
    while True:
        resp: PaginationPostDTO = client.list_posts(page=page, page_size=page_size)
        results.extend(resp.data)
        if not resp.data:
            break
        if resp.page * resp.page_size >= resp.total:
            break
        if page_limit and page >= page_limit:
            break
        page += 1
    return results


def filter_posts_by_datetime_range(posts: Iterable[PostDTO], start_dt, end_dt) -> List[PostDTO]:
    """왜: 주간 범위에 해당하는 포스트만 필터링한다."""
    filtered: List[PostDTO] = []
    for p in posts:
        dt = parse_published_at(p.published_at) if p.published_at else None
        if not dt:
            continue
        if start_dt <= dt <= end_dt:
            filtered.append(p)
    return filtered
