from __future__ import annotations

import argparse

from utils.env_loader import load_settings
from utils.logger import get_logger
from chains.retriever_deep import get_deep_retriever
from chains.deep_qa_chain import build_deep_qa_chain


logger = get_logger(__name__)


def answer_deep_question(query: str, top_k: int = 8) -> str:
    settings = load_settings()
    retriever = get_deep_retriever(settings=settings, k=top_k)
    chain = build_deep_qa_chain(retriever, model_name=settings.gemini_model)
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
