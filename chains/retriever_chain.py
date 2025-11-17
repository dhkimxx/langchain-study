from __future__ import annotations

from typing import List

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

from utils.env_loader import AppSettings

_COLLECTION_NAME = "techletter_posts"


def build_embeddings(settings: AppSettings) -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(model=settings.embedding_model)


def ingest_documents(
    docs: List[Document],
    *,
    settings: AppSettings,
) -> None:
    embeddings = build_embeddings(settings)
    Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=settings.vector_db_path,
        collection_name=_COLLECTION_NAME,
    )


def get_retriever(*, settings: AppSettings, k: int = 5):
    embeddings = build_embeddings(settings)
    db = Chroma(
        persist_directory=settings.vector_db_path,
        embedding_function=embeddings,
        collection_name=_COLLECTION_NAME,
    )
    return db.as_retriever(search_kwargs={"k": k})
