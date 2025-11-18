from __future__ import annotations

import argparse
import shutil
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from chains.retriever_simple_chain import ingest_simple_documents
from utils.logger import get_logger
from utils.api_client import TechLetterClient, PaginationPostDTO
from utils.text_utils import to_document
from utils.app_config import CONFIG


logger = get_logger(__name__)


def _fetch_all_posts(
    client: TechLetterClient, page_size: int = 100
) -> List[PaginationPostDTO]:
    page = 1
    items: List[PaginationPostDTO] = []
    while True:
        resp = client.list_posts(page=page, page_size=page_size)
        items.append(resp)
        if not resp.data:
            break
        if resp.page * resp.page_size >= resp.total:
            break
        page += 1
    return items


def run_simple_ingest(reset: bool = False) -> None:
    if reset:
        shutil.rmtree(CONFIG.vector_db_path, ignore_errors=True)

    client = TechLetterClient(base_url=CONFIG.techletter_base_url)
    pages = _fetch_all_posts(client)

    posts = [p for page in pages for p in page.data]
    logger.info(f"수집된 포스트 수: {len(posts)}")

    docs = [to_document(p) for p in posts]
    if not docs:
        logger.warning("인덱싱할 문서가 없습니다.")
        return

    # 청크 분할: 요약 중심 문서를 적절한 크기로 나눠 검색 정밀도 향상
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    emb_cfg = CONFIG.get_chain_config("embedding")
    ingest_simple_documents(
        chunks,
        persist_dir=CONFIG.vector_db_path,
        provider=emb_cfg["provider"],
        model_name=emb_cfg["model_name"],
        api_key=emb_cfg.get("api_key"),
    )
    logger.info("임베딩 및 인덱싱 완료")


def main():
    parser = argparse.ArgumentParser(description="Tech-Letter 데이터 수집 및 인덱싱")
    parser.add_argument(
        "--reset", action="store_true", help="기존 벡터 스토어 초기화 후 재생성"
    )
    args = parser.parse_args()
    run_simple_ingest(reset=args.reset)


if __name__ == "__main__":
    main()
