from __future__ import annotations

from typing import List


def filter_by_title_crop(text: str, *, title: str, margin_chars: int = 0) -> str:
    """왜: 제목 이전의 내비게이션/소개 영역을 잘라내고 본문 근처만 남기기 위함.

    - title이 본문 내에 등장하면 그 이전은 모두 제거한다.
    - title을 찾지 못하면 원문을 그대로 반환한다.
    """
    if not text or not title:
        return text

    idx = text.find(title.strip())
    if idx == -1:
        return text

    start = max(0, idx - margin_chars)
    return text[start:]


_FILTER_KEYWORDS = [
    "sitemap",
    "sign up",
    "signup",
    "sign in",
    "login",
    "logout",
    "follow",
    "팔로우",
    "공유",
    "share",
    "댓글",
    "comment",
    "tag",
    "tags",
    "category",
    "categories",
    "홈",
    "메뉴",
    "목록",
    # 공통적인 헤더/푸터 UI 문구들
    "open in app",
    "medium logo",
    "write",
    "search",
    "subscribe",
    "text to speech",
    "clap icon",
    "response icon",
    "recommended",
    "see all",
    "see more",
    "more from",
    # 사이트 푸터 내비게이션에 자주 등장하는 키워드들
    "help",
    "status",
    "about",
    "careers",
    "press",
    "blog",
    "privacy",
    "rules",
    "terms",
]


def _is_noise_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True

    if len(stripped) <= 3:
        return True

    lower = stripped.lower()

    # 내비/버튼/푸터성 키워드가 포함되고 너무 짧으면 제거
    if len(stripped) < 40 and any(kw in lower for kw in _FILTER_KEYWORDS):
        return True

    # 기호/숫자 위주인 짧은 라인 제거
    if len(stripped) < 25:
        letters = sum(ch.isalpha() for ch in stripped)
        digits = sum(ch.isdigit() for ch in stripped)
        others = len(stripped) - letters - digits
        if others > letters + digits:
            return True

    return False


def filter_by_line_heuristics(text: str) -> str:
    """왜: 한 줄씩 검토해 네비/버튼/잡음 라인을 제거해 본문 비중을 높이기 위함.

    - 매우 짧고 의미 없는 줄 제거
    - 내비게이션/공유/팔로우 등 UI성 키워드 포함 줄 제거
    - 기호/숫자 위주의 짧은 줄 제거
    """
    if not text:
        return text

    lines = text.splitlines()
    kept: List[str] = []

    for line in lines:
        if _is_noise_line(line):
            continue

        kept.append(line)

    cleaned = "\n".join(kept).strip()
    return cleaned or text
