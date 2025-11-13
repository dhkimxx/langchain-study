from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

from utils.text_utils import format_docs_for_prompt


SIMPLE_QA_SYSTEM_PROMPT = (
    "당신은 Tech Blog QA Assistant입니다.\n"
    "사용자의 개발 관련 질문에 대해 제공된 검색 컨텍스트만 근거로 답변하세요.\n"
    "추가적인 추측이나 일반 지식은 사용하지 마세요.\n\n"
    "출력 형식:\n"
    "- 답변에는 번호를 붙이지 마세요. 질문에 대한 간결한 한국어 답변과 추천 이유를 3~5문장 이내로 작성하세요.\n"
    "- 관련 글 목록에만 1부터 순서대로 번호를 붙이세요. 답변과 관련 글 번호는 별개입니다.\n"
    "- 각 글 블록은 번호 + 제목 링크 + 요약 순서로 작성하고, 글 사이에는 한 줄 이상의 공백을 두어 독립적으로 표시하세요.\n\n"
    "불확실한 경우:\n"
    "- 확실하지 않으면 '확실하지 않습니다'라고 명시하고, 사용자가 시도할 수 있는 대안을 제시하세요.\n\n"
    "톤:\n"
    "- 공손하고 이해하기 쉽게 존어를 사용하여 작성하세요.\n\n"
    "출력 예시(Markdown, 관련 글 블록 번호 1부터 시작, 독립 블록):\n"
    "```\n"
    "Python은 데이터 처리와 API 서버 구축에 활용되는 인기 언어입니다. "
    "NHN Cloud 플러그인 개발과 카카오 내부 AI 교육 프로그램 사례에서 Python이 효율적으로 사용된 경험이 있습니다.\n\n"
    "1. [NHN Cloud Plugin 개발기 | Cloudforet 오픈소스 프로젝트 후기](https://meetup.nhncloud.com/posts/387)\n"
    "   \n"
    "   Linux Foundation 멘토십을 통해 Cloudforet에서 NHN Cloud 자원을 관리하는 플러그인을 개발한 과정을 소개합니다. "
    "Python API 서버 구축, NHN Cloud API 연동 및 인증 처리, 사용자 가이드 작성 등 프로젝트 경험과 성과를 공유합니다.\n\n"
    "2. [전사 AI 역량 강화를 위한 맞춤형 내부 교육 프로그램](https://tech.kakao.com/posts/758)\n"
    "   \n"
    "   카카오는 모든 구성원의 AI 역량 강화를 위해 AI 인재상 정의부터 로드맵 수립, 테크 플래그십 데이, AI Native, Basic, Advanced, Intensive 등 다각적인 교육 프로그램을 운영합니다. "
    "실습 중심 교육으로 개발자의 60% 이상이 AI 기술 적용 역량을 갖추는 성과를 보였습니다.\n"
    "```\n"
)



def build_qa_chain(
    retriever, model_name: str = "gemini-2.5-flash", temperature: float = 0.2
):
    llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SIMPLE_QA_SYSTEM_PROMPT),
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
