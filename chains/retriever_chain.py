from __future__ import annotations

from typing import List

from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

from utils.env_loader import AppSettings
from utils.model_utils import normalize_embedding_model_name

_COLLECTION_NAME = "techletter_posts"


def build_embeddings(settings: AppSettings) -> GoogleGenerativeAIEmbeddings:
    """왜: Gemini 임베딩을 표준화된 팩토리로 생성한다."""
    model_name = normalize_embedding_model_name(settings.embedding_model)
    return GoogleGenerativeAIEmbeddings(model=model_name)


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
