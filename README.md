# Tech Blog QA Assistant

Tech-Letter API의 테크 블로그 요약 데이터를 벡터화해 검색하고, 자연어 답변을 생성하는 질의응답 도구입니다. 질문에 맞는 관련 글을 찾아 제목·URL·간단 요약을 함께 제공합니다.

## 주요 기능

- **질문 기반 검색**: 자연어 질문으로 관련 포스트 검색
- **추천 근거 포함**: 왜 추천하는지 1~2문장으로 설명
- **결과 포맷**: (제목 + URL + 요약) 리스트 출력

## 아키텍처

1. Tech-Letter API 수집(REST)
2. 문서 합성 및 청킹(요약 중심)
3. 임베딩(Google Embeddings) → ChromaDB 저장
4. LangChain Retriever → Gemini 2.5 Flash 생성 응답

## 기술 스택

- Python 3.11
- LangChain, ChromaDB
- Gemini 2.5 Flash, Google Embeddings

## 설정

.env 또는 config.yaml로 설정합니다. `.env` 예시:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
TECHLETTER_BASE_URL=http://<host>:<port>/api/v1
VECTOR_DB_PATH=./data/vector_store
GEMINI_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=models/text-embedding-004
```

- 참고: `GEMINI_API_KEY`는 내부에서 `GOOGLE_API_KEY`로 매핑됩니다.

## 설치

```bash
# (선택) 가상환경 생성
python -m venv .venv && source .venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 환경 파일 준비
cp .env.example .env  # 실제 값으로 수정
```

## 실행 방법

1. 데이터 수집 및 인덱싱(최초 1회)

```bash
python main.py ingest --reset
```

2. 질의응답 실행

```bash
python main.py qa -q "리액트 상태관리 관련 글 보여줘" -k 3
```

## 동작

- ingest: `/posts`를 페이지네이션 수집 → 텍스트 합성 → RecursiveCharacterTextSplitter 청킹 → 임베딩 → ChromaDB 저장
- qa: Retriever로 관련 문서 조회 → Gemini 2.5 Flash가 답변 생성(제목+URL+요약 포함)

## 시연 결과(예시)

- 수집 로그(예):

```
INFO | ingest | 수집된 포스트 수: 173
INFO | ingest | 임베딩 및 인덱싱 완료
```

- 질의응답 예시:

```
질문: 마이크로서비스 아키텍처 관련 글 추천해줘

관련 글 3개를 찾았어요 👇
1. "MSA에서 트랜잭션 관리하기" — <https://tech.sktelecom.com/post/msa-transaction>
   요약: 분산 트랜잭션과 사가 패턴을 활용한 일관성 전략을 설명합니다.
2. "Spring Cloud Gateway로 MSA 구성하기" — <https://blog.coupang.io/post/spring-cloud>
   요약: API Gateway, 서비스 디스커버리, 라우팅 구성을 다룹니다.
3. "MSA 장애 대응 전략" — <https://engineering.linecorp.com/post/msa-failure>
   요약: 장애 전파 차단과 회복 탄력성 패턴을 소개합니다.
```
