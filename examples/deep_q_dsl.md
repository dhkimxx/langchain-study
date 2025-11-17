dhkim@Macbook-Pro langchain_study % python main.py deep-qa -q "DSL으로 문제 해결한 사례"

DSL(Domain-Specific Language)은 특정 도메인(문제 영역)에 특화된 언어를 사용하여 해당 도메인의 문제를 효율적이고 간결하게 해결하는 데 도움을 줍니다. 제공된 컨텍스트에는 'DSL'이라는 용어가 명시적으로 사용되지는 않았지만, 특정 도메인에 특화된 도구나 명령 체계를 활용하여 복잡한 문제를 해결하거나 효율성을 증대한 여러 사례가 있습니다.

다음은 DSL의 특성을 보여주는 문제 해결 사례입니다:

1.  **CI/CD 파이프라인의 간결한 자동화:**
    여기어때는 복잡한 CI/CD 스크립트를 간결하게 만들기 위해 Go 언어로 전용 CI Agent 이미지를 개발하고 CLI(Command Line Interface) 구조를 구현했습니다. 이 CI Agent는 프로파일에 따라 알람을 전송하고 Manifest를 자동으로 업데이트하는 등 다양한 역할을 수행하며, 100줄에 달하는 스크립트를 `/main slack --action=alarm --template=failed --profile=$PROFILE`와 같은 단 한 줄의 명령어로 실행할 수 있게 했습니다. 이는 CI/CD 도메인에 특화된 명령어를 제공하는 DSL이 복잡한 작업을 간결하고 직관적으로 관리할 수 있게 하여 효율성을 크게 높인 사례로 볼 수 있습니다.

    - 출처: [여기어때 CI/CD 개선기 Part 2: CI Pipeline 설계](https://techblog.gccompany.co.kr/%EC%97%AC%EA%B8%B0%EC%96%B4%EB%95%8C-ci-cd-%EA%B0%9C%EC%84%A0%EA%B8%B0-part-2-ci-pipeline-%EC%84%A4%EA%B3%84-902c116c4967?source=rss----18356045d353---4)

2.  **AI 에이전트의 도메인 특화 기능 활용:**
    카카오 x 한국정보과학회 AI 에이전트 경진대회에서 제시된 AI 에이전트 활용 사례들은 각 도메인에 특화된 '주요 기능(도구)'을 DSL처럼 활용하여 문제를 해결합니다. 예를 들어, 개인 비서 에이전트는 '항공/숙소/렌터카 API', '캘린더 연동', '결제 API' 등을 사용하여 복합 여행 계획 및 예약을 처리합니다. 쇼핑 에이전트는 '웹 스크래핑', '상품 DB 검색', '결제 API'를 통해 가격 비교 및 자동 구매를 수행합니다. 이처럼 각 도메인의 문제를 해결하기 위해 고안된 API나 도구들은 해당 도메인의 개념을 직접적으로 표현하고 조작할 수 있는 DSL의 역할을 수행합니다.

    - 출처: [(FAQ) 카카오 x 한국정보과학회 AI 에이전트 경진대회](https://tech.kakao.com/posts/782)

3.  **API 계약의 일관된 관리 및 자동 문서화:**
    토스페이먼츠는 SDK 개발 과정에서 문서와 실제 동작이 불일치하는 문제를 해결하기 위해 Typescript 기반의 '계약'을 활용하여 문서를 자동으로 생성했습니다. Typescript 컴파일러를 이용해 Typescript Interface와 JSDoc을 읽어 Mdx로 추출하고, 이를 정적 docs 서비스에 업로드하는 방식입니다. 이는 API 계약이라는 특정 도메인에 특화된 '언어'(Typescript Interface와 JSDoc)를 사용하여 개발 문서의 신뢰성을 높이고 히스토리 추적을 용이하게 만든 사례로, DSL이 개발 프로세스에서 발생하는 고질적인 문제를 해결하는 데 기여했음을 보여줍니다.
    - 출처: [100년 가는 프론트엔드 코드, SDK](https://toss.tech/article/payments-legacy-3)
