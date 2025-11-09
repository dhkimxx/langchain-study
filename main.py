from __future__ import annotations

import argparse

from ingest import run_ingest
from qa import answer_question
from features.newsletter.generator import generate_ai_weekly_newsletter


def main():
    parser = argparse.ArgumentParser(description="Tech Blog QA Assistant CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_ingest = sub.add_parser("ingest", help="Tech-Letter 데이터 수집 및 인덱싱")
    p_ingest.add_argument("--reset", action="store_true", help="벡터 스토어 초기화")

    p_qa = sub.add_parser("qa", help="질의응답 실행")
    p_qa.add_argument("-q", "--query", required=True, help="사용자 질문")
    p_qa.add_argument("-k", "--top-k", type=int, default=5, help="검색 문서 수")

    p_news = sub.add_parser("newsletter", help="AI 주간 요약 뉴스레터 생성")
    p_news.add_argument("--days", type=int, default=7, help="요약 기간(일) 기본 7일")
    p_news.add_argument("--start", type=str, default=None, help="시작일(YYYY-MM-DD)")
    p_news.add_argument("--end", type=str, default=None, help="종료일(YYYY-MM-DD)")
    p_news.add_argument("--limit", type=int, default=50, help="최대 포스트 수(컨텍스트 제한)")

    args = parser.parse_args()

    if args.command == "ingest":
        run_ingest(reset=args.reset)
    elif args.command == "qa":
        print(answer_question(args.query, top_k=args.top_k))
    elif args.command == "newsletter":
        result = generate_ai_weekly_newsletter(
            days=args.days,
            start=args.start,
            end=args.end,
            limit=args.limit,
        )
        print(result.content)


if __name__ == "__main__":
    main()
