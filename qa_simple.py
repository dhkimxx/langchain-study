from __future__ import annotations

import argparse

from chains.retriever_simple_chain import get_simple_retriever
from utils.logger import get_logger
from chains.qa_chain import build_simple_qa_chain
from chains.factory import new_chat
from utils.app_config import CONFIG


logger = get_logger(__name__)


def answer_simple_question(query: str, top_k: int = 5) -> str:
    # retriever (embedding provider)
    emb_cfg = CONFIG.get_chain_config("retriever")
    retriever = get_simple_retriever(
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
        temperature=0.2,
        api_key=chat_cfg.get("api_key"),
    )

    chain = build_simple_qa_chain(retriever, llm)

    result = chain.invoke(query)

    # 검색된 문서 링크 리스트를 후처리로 보강 출력 (LLM 출력이 누락될 경우 대비)
    # docs = retriever.get_relevant_documents(query)
    # lines = []
    # for i, d in enumerate(docs, 1):
    #     title = d.metadata.get("title", "(제목 없음)")
    #     link = d.metadata.get("link", "")
    #     lines.append(f'{i}. "{title}" — <{link}>')

    # final = result.strip()
    # if lines:
    #     final = final + "\n\n" + "\n".join(lines)
    return result


def main():
    parser = argparse.ArgumentParser(description="Tech Blog QA")
    parser.add_argument("-q", "--query", required=True, help="사용자 질문")
    parser.add_argument("-k", "--top-k", type=int, default=5, help="검색 문서 수")
    args = parser.parse_args()

    output = answer_simple_question(args.query, top_k=args.top_k)
    print(output)


if __name__ == "__main__":
    main()
