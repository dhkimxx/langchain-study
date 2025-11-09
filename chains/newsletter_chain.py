from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI


_SYSTEM_PROMPT = (
    "당신은 Tech Blog 주간 뉴스레터 편집자입니다. 다음 컨텍스트(최근 포스트들)를 기반으로 '주간 요약'을 한국어로 작성하세요.\n"
    "- 맥락에 포함된 정보만 사용하고, 추측/환상을 추가하지 마세요.\n"
    "- 마크다운으로 구성합니다.\n"
    "- 섹션 예시: # 주간 요약(YYYY-MM-DD ~ YYYY-MM-DD), ## 핵심 트렌드(3~5개 불릿), ## 추천 글(제목 + URL + 1~2문장 요약), ## 한 줄 총평.\n"
    "- 각 추천 글은 반드시 제목과 원문 URL을 포함하세요. 요약은 컨텍스트 요약을 간결히 재구성하세요.\n"
)


def build_newsletter_chain(model_name: str = "gemini-2.5-flash", temperature: float = 0.3):
    """왜: 주간 뉴스레터 생성을 표준화된 체인으로 제공한다."""
    llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _SYSTEM_PROMPT),
            (
                "human",
                "기간: {start} ~ {end}\n\n컨텍스트(최근 포스트들):\n{context}\n\n"
                "요청: 위 기간의 주요 트렌드를 요약하고, 추천 글 목록(제목+URL+요약)을 생성하세요.",
            ),
        ]
    )

    chain = prompt | llm | StrOutputParser()
    return chain
