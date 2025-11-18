from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.chat_models.base import BaseChatModel

from utils.doc_builders import format_docs_for_deep_prompt


DEEP_QA_SYSTEM_PROMPT = (
    "당신은 Tech Blog DeepSearch 어시스턴트입니다. 제공된 문서 컨텍스트만을 근거로 고차원 질문에 답하세요.\n"
    "출처 간 내용을 종합하여 일반화된 인사이트를 도출하세요.\n"
    "반드시 한국어로 작성하세요.\n"
    "답변에 사용된 출처들을 답변의 마지막에 포함하세요. (블로그 이름, 포스트 제목, URL) \n"
    "출처 포멧은 다음 마크다운 포멧으로 제공해야합니다: [ blog_name - title ](url)\n"
    "다음은 출처 포멧 예시입니다: \n"
    "- [무신사 - LangChain 기반 지능형 자동화 도입기](https://medium.com/musinsa-tech/example)\n"
    "- [당근마켓 - 연간 LLM 호출 비용 25% 절감, 인턴이 도전한 시맨틱 캐싱 도입 기록](https://medium.com/daangn/example)\n"
)


def build_deep_qa_chain(
    retriever,
    llm: BaseChatModel,
):
    """왜: 고차원 종합 답변 + 근거 출처를 생성하는 체인."""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", DEEP_QA_SYSTEM_PROMPT),
            (
                "human",
                "질문: {question}\n\n검색 컨텍스트(스니펫):\n{context}\n\n"
                "요청: 위 컨텍스트만을 근거로 응답 포맷에 맞춰 답하세요.",
            ),
        ]
    )

    chain = (
        {
            "context": retriever | (lambda docs: format_docs_for_deep_prompt(docs)),
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain
