from __future__ import annotations

import argparse
import shutil
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from chains.retriever_deep_chain import ingest_deep_documents
from utils.logger import get_logger
from utils.api_client import TechLetterClient, PostDTO
from utils.data_loader import fetch_all_posts
from utils.doc_builders import build_document_from_full_text
from utils.aggregate import aggregate_text
from utils.app_config import CONFIG


logger = get_logger(__name__)


def _safe_fetch_full_text(post: PostDTO) -> str | None:
    try:
        return aggregate_text(post.link)
    except Exception as e:
        logger.warning(f"본문 수집 실패: {post.link} - {e}")
        return None


def run_deep_ingest(
    reset: bool = False,
    limit: int | None = None,
    page_limit: int | None = None,
) -> None:
    if reset:
        shutil.rmtree(CONFIG.vector_db_path, ignore_errors=True)

    client = TechLetterClient(base_url=CONFIG.techletter_base_url)
    posts: List[PostDTO] = fetch_all_posts(client, page_size=100, page_limit=page_limit)
    if limit:
        posts = posts[: max(1, limit)]

    logger.info(f"수집 대상 포스트 수(전체): {len(posts)}")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=150)
    did_any = False
    for i, p in enumerate(posts):
        full = _safe_fetch_full_text(p)
        print(f"[{i}/{len(posts)}] {p.title} text loaded")
        if not full:
            continue
        doc = build_document_from_full_text(p, full)

        print("splitting")
        chunks = splitter.split_documents([doc])

        print("ingesting")
        emb_cfg = CONFIG.get_chain_config("embedding")
        ingest_deep_documents(
            chunks,
            persist_dir=CONFIG.vector_db_path,
            provider=emb_cfg["provider"],
            model_name=emb_cfg["model_name"],
            api_key=emb_cfg.get("api_key"),
        )
        did_any = True

    if not did_any:
        logger.warning("인덱싱할 본문 문서가 없습니다.")
        return

    logger.info("딥 임베딩 및 인덱싱 완료")


def main():
    parser = argparse.ArgumentParser(description="Tech-Letter 전체 본문 기반 딥 인덱싱")
    parser.add_argument("--reset", action="store_true", help="딥 컬렉션 초기화")
    parser.add_argument(
        "--limit", type=int, default=None, help="처리할 포스트 최대 개수"
    )
    parser.add_argument(
        "--page-limit", type=int, default=None, help="페이지네이션 페이지 최대 개수"
    )
    args = parser.parse_args()

    run_deep_ingest(
        reset=args.reset,
        limit=args.limit,
        page_limit=args.page_limit,
    )


if __name__ == "__main__":
    main()
