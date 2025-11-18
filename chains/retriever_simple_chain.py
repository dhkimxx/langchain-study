from __future__ import annotations

from typing import List

from langchain_chroma import Chroma
from langchain_core.documents import Document
from .factory import new_embedding
import time

_SIMPLE_COLLECTION_NAME = "techletter_posts_simple"


def ingest_simple_documents(
    docs: List[Document],
    *,
    persist_dir: str,
    provider: str,
    model_name: str,
    api_key: str | None = None,
) -> None:
    embeddings = new_embedding(provider, model_name, api_key=api_key)
    db = Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings,
        collection_name=_SIMPLE_COLLECTION_NAME,
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
                else:
                    print(f"Retrying {attempt} after error: {e}")
                    time.sleep(2**attempt)


def get_simple_retriever(
    *,
    persist_dir: str,
    provider: str,
    model_name: str,
    api_key: str | None = None,
    k: int = 5,
):
    embeddings = new_embedding(provider, model_name, api_key=api_key)
    db = Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings,
        collection_name=_SIMPLE_COLLECTION_NAME,
    )
    return db.as_retriever(search_kwargs={"k": k})
