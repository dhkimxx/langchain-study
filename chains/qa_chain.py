from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

from utils.text_utils import format_docs_for_prompt


_SYSTEM_PROMPT = (
    "당신은 Tech Blog QA Assistant입니다. 사용자의 개발 질문에 대해, 검색된 컨텍스트만을 근거로 한국어로 간결하게 답하세요.\n"
    "- 추천 이유를 1~2문장으로 제시하세요.\n"
    "- 관련 글을 (제목 + URL + 요약) 리스트로 함께 제시하세요.\n"
    "- 확실하지 않으면 모른다고 말하고, 대안을 제안하세요.\n"
)


def build_qa_chain(
    retriever, model_name: str = "gemini-2.5-flash", temperature: float = 0.2
):
    llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _SYSTEM_PROMPT),
            ("human", "질문: {question}\n\n검색 컨텍스트:\n{context}\n\n"),
        ]
    )

    chain = (
        {
            "context": retriever | (lambda docs: format_docs_for_prompt(docs)),
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain
