from __future__ import annotations

from typing import List

from langchain_chroma import Chroma
from langchain_core.documents import Document

from utils.env_loader import AppSettings
from chains.retriever_chain import build_embeddings
from chromadb import PersistentClient
import time

_DEEP_COLLECTION_NAME = "techletter_posts_deep"


def ingest_deep_documents(
    docs: List[Document],
    *,
    settings: AppSettings,
) -> None:
    embeddings = build_embeddings(settings)
    db = Chroma(
        persist_directory=settings.vector_db_path,
        embedding_function=embeddings,
        collection_name=_DEEP_COLLECTION_NAME,
    )

    max_retries = 5
    for idx, doc in enumerate(docs):
        attempt = 0
        while True:
            try:
                chunk_id = f"{str(doc.metadata.get('id', 'unknown'))}:{idx}"
                db.add_documents([doc], ids=[chunk_id])
                break
            except Exception as e:
                attempt += 1
                if attempt > max_retries:
                    raise
                if "429" in str(e) or "rate limit" in str(e).lower():
                    sleep_s = 2**attempt
                    time.sleep(sleep_s)
                else:
                    raise


def get_deep_retriever(*, settings: AppSettings, k: int = 8):
    embeddings = build_embeddings(settings)
    db = Chroma(
        persist_directory=settings.vector_db_path,
        embedding_function=embeddings,
        collection_name=_DEEP_COLLECTION_NAME,
    )
    return db.as_retriever(search_kwargs={"k": k})


def reset_deep_collection(*, settings: AppSettings) -> None:
    client = PersistentClient(path=settings.vector_db_path)
    try:
        client.delete_collection(_DEEP_COLLECTION_NAME)
    except Exception:
        # 컬렉션이 없거나 삭제 실패해도 전체 디렉토리를 건드리지 않는다.
        pass
