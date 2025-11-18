# Tech Blog QA Assistant

Tech-Letter API의 테크 블로그 요약 데이터를 벡터화해 검색하고, 자연어 답변을 생성하는 질의응답 도구입니다. 질문에 맞는 관련 글을 찾아 제목·URL·간단 요약을 함께 제공합니다.

## 주요 기능

- **질문 기반 검색**: 자연어 질문으로 관련 포스트 검색
- **추천 근거 포함**: 왜 추천하는지 1~2문장으로 설명
- **결과 포맷**: (제목 + URL + 요약) 리스트 출력
- **DeepSearch(고차원 답변)**: 실제 포스트 전체 본문 임베딩 기반으로 출처를 종합해 고차원 답변과 근거(제목+URL)를 제공

## 아키텍처

1. Tech-Letter API 수집(REST)
2. 문서 합성 및 청킹(요약 중심)
3. 임베딩(구글 또는 오픈AI 선택) → ChromaDB 저장
4. LangChain Retriever → LLM(구글 또는 오픈AI) 생성 응답

## 기술 스택

- Python 3.11
- LangChain, ChromaDB(langchain-chroma)
- Google Gemini/Google Embeddings 또는 OpenAI(선택형)

## 설정

config.yaml로 설정합니다. 예시는 `config-example.yaml`을 참고하세요.

```yaml
app:
  techletter_base_url: http://<host>:<port>/api/v1
  vector_db_path: ./data/vector_store

chains:
  embedding:
    provider: google # [google, openai]
    api_key: your_ai_api_key_here
    model_name: models/gemini-embedding-001

  retriever:
    provider: google # [google, openai]
    api_key: your_ai_api_key_here
    model_name: models/gemini-embedding-001

  chat:
    provider: google # [google, openai]
    api_key: your_ai_api_key_here
    model_name: gemini-2.5-flash
```

- provider별 `api_key`는 런타임에 자동으로 환경변수(Google=GOOGLE_API_KEY, OpenAI=OPENAI_API_KEY)로 매핑됩니다.
- 임베딩/리트리버 모델은 동일하게 유지하는 것을 권장합니다(차원 불일치 방지).
- 컬렉션 이름: Simple=`techletter_posts_simple`, Deep=`techletter_posts_deep`.

## 설치

```bash
# (선택) 가상환경 생성
python -m venv .venv && source .venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 설정 파일 준비
cp config-example.yaml config.yaml  # 실제 값으로 수정
```

## 실행 방법

1. 데이터 수집 및 인덱싱(Simple, 최초 1회)

```bash
python main.py ingest --reset
```

2. 질의응답 실행

```bash
python main.py qa -q "리액트 상태관리 관련 글 보여줘" -k 3
```

3. 뉴스레터 생성 (주간 요약)

```bash
# 지난 7일 요약을 표준 출력(STDOUT)으로 출력
python main.py newsletter --days 7
```

4. DeepSearch 실행 (전체 본문 기반)

```bash
# 1) 전체 본문 딥 인덱싱 (초기 1회, 시간이 오래 걸릴 수 있음)
python main.py deep-ingest --reset --limit 30 --page-limit 2   # 소량 테스트 권장

# 2) 딥 서치 QA 실행 (고차원 질문)
python main.py deep-qa -q "카프카 기반 데이터 파이프라인 안정성 전략을 종합적으로 알려줘" -k 8
```

## 동작

- ingest: `/posts` 페이지네이션 수집 → 요약 문서 청킹 → 임베딩(설정된 프로바이더) → ChromaDB 저장(Simple 컬렉션)
- qa: Retriever로 관련 문서 조회 → LLM(설정된 프로바이더)로 답변 생성(제목+URL+요약 포함)
- newsletter: 기간(KST) 내 포스트 수집 → 정렬 → LLM으로 마크다운 뉴스레터 생성(STDOUT)
- deepsearch: 실제 포스트 본문 렌더링/추출 → 본문 기반 문서 생성 → 청킹 → 딥 컬렉션에 임베딩 저장(문서 단위 add + 429 백오프) → 근거 출처를 포함한 고차원 응답 생성

## 뉴스레터 옵션

- `--days <N>`: 요약 기간(일), 기본 7
- `--start YYYY-MM-DD --end YYYY-MM-DD`: 기간 지정(미지정 시 현재 기준 `--days` 적용)
- `--limit <N>`: 컨텍스트에 포함할 최대 포스트 수(조회수 높은 순), 기본 50

## DeepSearch 옵션 및 주의사항

- deep-ingest
  - `--reset`: 벡터 스토어 경로를 초기화(기존 컬렉션 전체 삭제)
  - `--limit <N>`: 처리할 포스트 최대 개수(테스트 시 유용)
  - `--page-limit <N>`: 페이지네이션 페이지 최대 개수 제한
- deep-qa
  - `-k/--top-k <N>`: 검색 문서 수, 기본 8

주의사항

- Selenium 기반 headless Chrome으로 본문을 렌더링/추출하므로 로컬에 Chrome이 설치되어 있어야 합니다.
- 크롤링/임베딩 과정은 시간이 오래 걸리고 API 비용이 증가할 수 있습니다.
- 일부 사이트는 동적 렌더링/차단 정책으로 본문 추출이 실패할 수 있습니다(로그 경고 확인).
- 임베딩/리트리버 모델이 다르면 ChromaDB에서 차원 불일치 에러가 발생합니다. 반드시 동일 모델/차원으로 맞추세요.
- 임베딩 요청이 많을 경우 429가 발생할 수 있으며, 시스템은 문서 단위 추가 + 지수 백오프로 자동 재시도합니다.

## Chrome 설치 가이드

- Windows

  - `winget install Google.Chrome`
  - 또는 Chocolatey: `choco install googlechrome`
  - 수동 설치: https://www.google.com/chrome/

- macOS

  - Homebrew: `brew install --cask google-chrome`
  - 수동 설치: https://www.google.com/chrome/ 에서 .dmg 다운로드 후 설치

- Ubuntu
  - 패키지 설치(간단):
    ```bash
    sudo apt update
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo apt install -y ./google-chrome-stable_current_amd64.deb
    ```
  - 설치 후 `google-chrome --version`으로 확인하세요.

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
