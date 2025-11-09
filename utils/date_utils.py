from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional

_KST = timezone(timedelta(hours=9))


def now_kst() -> datetime:
    """왜: 한국 시간 기준으로 주간 계산을 일관되게 하기 위함."""
    return datetime.now(tz=_KST)


def last_n_days_range(days: int = 7, *, end: Optional[datetime] = None) -> Tuple[datetime, datetime]:
    """끝 시간(end) 포함 구간 [start, end]."""
    end_dt = end or now_kst()
    start_dt = end_dt - timedelta(days=days)
    return start_dt, end_dt


def parse_published_at(value: str) -> Optional[datetime]:
    """왜: API의 published_at 문자열을 비교 가능한 datetime으로 변환한다.
    포맷이 다양할 수 있어 ISO-8601 우선, 실패 시 일부 일반 포맷을 시도.
    실패하면 None.
    """
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S%z", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            dt = datetime.strptime(value, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(_KST)
        except Exception:
            continue
    return None
