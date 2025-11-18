from __future__ import annotations

import argparse

from chains.retriever_deep_chain import get_deep_retriever
from utils.logger import get_logger
from chains.deep_qa_chain import build_deep_qa_chain
from chains.factory import new_chat
from utils.app_config import CONFIG


logger = get_logger(__name__)


def answer_deep_question(query: str, top_k: int = 8) -> str:
    # retriever (embedding provider)
    emb_cfg = CONFIG.get_chain_config("retriever")
    retriever = get_deep_retriever(
        persist_dir=CONFIG.vector_db_path,
        provider=emb_cfg["provider"],
        model_name=emb_cfg["model_name"],
        api_key=emb_cfg.get("api_key"),
        k=top_k,
    )

    # chat LLM
    chat_cfg = CONFIG.get_chain_config("chat")
    llm = new_chat(
        chat_cfg["provider"],
        chat_cfg["model_name"],
        temperature=1.0,
        api_key=chat_cfg.get("api_key"),
    )

    chain = build_deep_qa_chain(retriever, llm)
    result = chain.invoke(query)
    return result


def main():
    parser = argparse.ArgumentParser(description="DeepSearch QA")
    parser.add_argument("-q", "--query", required=True, help="사용자 질문")
    parser.add_argument("-k", "--top-k", type=int, default=8, help="검색 문서 수")
    args = parser.parse_args()

    output = answer_deep_question(args.query, top_k=args.top_k)
    print(output)


if __name__ == "__main__":
    main()
