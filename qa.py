from __future__ import annotations

import argparse

from utils.env_loader import load_settings
from utils.logger import get_logger
from chains.retriever_chain import get_retriever
from chains.qa_chain import build_qa_chain


logger = get_logger(__name__)


def answer_question(query: str, top_k: int = 5) -> str:
    settings = load_settings()
    retriever = get_retriever(settings=settings, k=top_k)
    chain = build_qa_chain(retriever, model_name=settings.gemini_model)

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

    output = answer_question(args.query, top_k=args.top_k)
    print(output)


if __name__ == "__main__":
    main()
