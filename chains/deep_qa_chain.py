from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

from utils.doc_builders import format_docs_for_deep_prompt


_SYSTEM_PROMPT = (
    "당신은 Tech Blog DeepSearch 어시스턴트입니다. 제공된 문서 컨텍스트만을 근거로 고차원 질문에 답하세요.\n"
    "출처 간 내용을 종합하여 일반화된 인사이트를 도출하세요.\n"
    "반드시 한국어로 작성하세요.\n"
    "답변에 사용된 출처를 명시적으로 포함하세요. 출처 포멧은 다음 마크다운 포멧으로 제공해야합니다. [제목](URL)\n"
)


def build_deep_qa_chain(
    retriever, model_name: str, temperature: float = 1.0
):
    """왜: 고차원 종합 답변 + 근거 출처를 생성하는 체인."""
    llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _SYSTEM_PROMPT),
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
