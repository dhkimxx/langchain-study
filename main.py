from __future__ import annotations

import argparse

from ingest import run_ingest
from qa import answer_question


def main():
    parser = argparse.ArgumentParser(description="Tech Blog QA Assistant CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_ingest = sub.add_parser("ingest", help="Tech-Letter 데이터 수집 및 인덱싱")
    p_ingest.add_argument("--reset", action="store_true", help="벡터 스토어 초기화")

    p_qa = sub.add_parser("qa", help="질의응답 실행")
    p_qa.add_argument("-q", "--query", required=True, help="사용자 질문")
    p_qa.add_argument("-k", "--top-k", type=int, default=5, help="검색 문서 수")

    args = parser.parse_args()

    if args.command == "ingest":
        run_ingest(reset=args.reset)
    elif args.command == "qa":
        print(answer_question(args.query, top_k=args.top_k))


if __name__ == "__main__":
    main()
