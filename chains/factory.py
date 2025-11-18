from typing import Literal
import os

from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.embeddings.base import Embeddings
from langchain_core.retrievers import BaseRetriever
from langchain.chat_models.base import BaseChatModel


Provider = Literal["google", "openai"]


def _ensure_provider_env(provider: Provider, api_key: str | None) -> None:
    p = provider.lower()
    if p == "google":
        if api_key:
            os.environ.setdefault("GOOGLE_API_KEY", api_key)
    elif p == "openai":
        if api_key:
            os.environ.setdefault("OPENAI_API_KEY", api_key)
    else:
        raise ValueError(f"unknown provider: {provider}")


def new_embedding(
    provider: Provider, model_name: str, api_key: str | None = None
) -> Embeddings:
    _ensure_provider_env(provider, api_key)
    p = provider.lower()
    if p == "google":
        return GoogleGenerativeAIEmbeddings(model=model_name)
    if p == "openai":
        return OpenAIEmbeddings(model=model_name)
    raise ValueError(f"unknown provider: {provider}")


def new_retriever(
    provider: Provider,
    model_name: str,
    persist_dir: str,
    collection_name: str,
    k: int = 10,
    api_key: str | None = None,
) -> BaseRetriever:
    if not os.path.exists(persist_dir):
        os.makedirs(persist_dir)

    embeddings = new_embedding(provider, model_name, api_key=api_key)
    vectordb = Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings,
        collection_name=collection_name,
    )
    return vectordb.as_retriever(search_kwargs={"k": k})


def new_chat(
    provider: Provider,
    model_name: str,
    temperature: float = 1.0,
    api_key: str | None = None,
) -> BaseChatModel:
    _ensure_provider_env(provider, api_key)
    p = provider.lower()
    if p == "google":
        return ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
    if p == "openai":
        return ChatOpenAI(model=model_name, temperature=temperature)
    raise ValueError(f"unknown provider: {provider}")
