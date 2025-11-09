from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

import requests
from pydantic import BaseModel
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class TechLetterAPIError(Exception):
    pass


class BlogDTO(BaseModel):
    id: str
    name: str
    url: str


class PaginationBlogDTO(BaseModel):
    data: List[BlogDTO]
    page: int
    page_size: int
    total: int


class PostDTO(BaseModel):
    blog_id: str
    blog_name: str
    categories: List[str] | None = None
    id: str
    link: str
    published_at: str
    summary: str
    tags: List[str] | None = None
    thumbnail_url: Optional[str] = None
    title: str
    view_count: Optional[int] = None


class PaginationPostDTO(BaseModel):
    data: List[PostDTO]
    page: int
    page_size: int
    total: int


class TechLetterClient:
    """왜: 외부 API 접근을 캡슐화해 타임아웃/재시도/에러처리를 일관되게 적용한다."""

    def __init__(self, base_url: str, timeout: int = 10, max_retries: int = 3):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        retry = Retry(
            total=max_retries,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _get(self, path: str, params: Optional[dict] = None) -> dict:
        url = f"{self.base_url}{path}"
        try:
            res = self.session.get(url, params=params, timeout=self.timeout)
            res.raise_for_status()
            return res.json()
        except requests.RequestException as e:
            raise TechLetterAPIError(f"GET {url} 실패: {e}") from e

    def list_blogs(self, page: int = 1, page_size: int = 100) -> PaginationBlogDTO:
        data = self._get("/blogs", params={"page": page, "page_size": page_size})
        return PaginationBlogDTO(**data)

    def list_posts(
        self,
        page: int = 1,
        page_size: int = 100,
        *,
        categories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        blog_id: Optional[str] = None,
        blog_name: Optional[str] = None,
    ) -> PaginationPostDTO:
        params: dict = {"page": page, "page_size": page_size}
        if categories:
            params["categories"] = ",".join(categories)
        if tags:
            params["tags"] = ",".join(tags)
        if blog_id:
            params["blog_id"] = blog_id
        if blog_name:
            params["blog_name"] = blog_name
        data = self._get("/posts", params=params)
        return PaginationPostDTO(**data)
