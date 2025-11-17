from typing import Literal
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.embeddings.base import Embeddings
from langchain.schema import BaseRetriever
from langchain.chat_models.base import BaseChatModel
import os

Provider = Literal["google", "openai"]


def new_embedding(provider: Provider, model_name: str) -> Embeddings:
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
) -> BaseRetriever:
    if not os.path.exists(persist_dir):
        os.makedirs(persist_dir)

    embeddings = new_embedding(provider, model_name)
    vectordb = Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings,
        collection_name=collection_name,
    )
    return vectordb.as_retriever(search_kwargs={"k": k})


def new_chat(
    provider: Provider, model_name: str, temperature: float = 1.0
) -> BaseChatModel:
    p = provider.lower()
    if p == "google":
        return ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
    if p == "openai":
        return ChatOpenAI(model=model_name, temperature=temperature)
    raise ValueError(f"unknown provider: {provider}")
