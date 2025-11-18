from __future__ import annotations

import json
import time
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from utils.aggregate import aggregate_text
from utils.api_client import TechLetterClient
from utils.doc_builders import build_document_from_full_text
from utils.app_config import CONFIG


def _ensure_dir(p: str | Path) -> Path:
    path = Path(p)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _write_json(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _launch_driver() -> webdriver.Chrome:
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,2000")
    opts.add_argument("--lang=ko-KR")
    opts.add_argument(
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    )
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=opts)


def _fetch_html(url: str, wait_seconds: float = 8.0) -> str:
    """왜: HTML 원문 단계를 기록하기 위해 간단히 렌더링 후 HTML을 수집한다."""
    driver = _launch_driver()
    try:
        driver.get(url)
        time.sleep(wait_seconds)
        return driver.page_source
    finally:
        driver.quit()


if __name__ == "__main__":
    client = TechLetterClient(base_url=CONFIG.techletter_base_url)
    resp = client.list_posts(page=1, page_size=5)

    logs_dir = _ensure_dir("outputs/stage_logs")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=150)

    for idx, post in enumerate(resp.data, 1):
        blog = (post.blog_name or "unknown").replace("/", "_").replace("\\", "_")
        base = f"{blog}-{idx}"

        # 1) HTML 단계
        try:
            html = _fetch_html(post.link)
            _write_json(
                logs_dir / f"{base}-html.json",
                {
                    "stage": "html",
                    "post_index": idx,
                    "title": post.title,
                    "link": post.link,
                    "html_length": len(html or ""),
                    "html": html,
                },
            )
        except Exception as e:
            _write_json(
                logs_dir / f"{base}-html.json",
                {
                    "stage": "html",
                    "post_index": idx,
                    "title": post.title,
                    "link": post.link,
                    "error": f"html_fetch_failed: {e}",
                },
            )
            continue

        # 2) Text 단계 (aggregate_text 사용: 챌린지 우회 포함)
        try:
            text = aggregate_text(post.link)
            _write_json(
                logs_dir / f"{base}-text.json",
                {
                    "stage": "text",
                    "post_index": idx,
                    "title": post.title,
                    "link": post.link,
                    "text_length": len(text or ""),
                    "text": text,
                },
            )
        except Exception as e:
            _write_json(
                logs_dir / f"{base}-text.json",
                {
                    "stage": "text",
                    "post_index": idx,
                    "title": post.title,
                    "link": post.link,
                    "error": f"text_extract_failed: {e}",
                },
            )
            continue

        # 3) Document 단계
        doc = build_document_from_full_text(post, text)
        _write_json(
            logs_dir / f"{base}-document.json",
            {
                "stage": "document",
                "post_index": idx,
                "title": post.title,
                "link": post.link,
                "metadata": doc.metadata,
                "content_length": len(doc.page_content or ""),
                "page_content": doc.page_content,
            },
        )

        # 4) Chunked documents 단계
        chunks = splitter.split_documents([doc])
        chunks_payload = {
            "stage": "chunks",
            "post_index": idx,
            "title": post.title,
            "link": post.link,
            "chunks_count": len(chunks),
            "chunks": [
                {
                    "chunk_index": i,
                    "content_length": len(ch.page_content or ""),
                    "page_content": ch.page_content,
                    "metadata": ch.metadata,
                }
                for i, ch in enumerate(chunks, 1)
            ],
        }
        _write_json(logs_dir / f"{base}-chunks.json", chunks_payload)
