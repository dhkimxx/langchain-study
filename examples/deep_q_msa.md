MSA(Microservices Architecture)는 수십여 개의 독립적인 서비스들이 연결되어 있으며 각 서비스가 자체적으로 DB를 관리하는 아키텍처를 의미합니다. [MSA 환경에서 네트워크 예외를 잘 다루는 방법](https://tech.kakaopay.com/post/msa-transaction/) 이는 기능, 역할, 관리 비용에 초점을 맞춰 도메인을 분리하는 것이 핵심입니다. [OMS의 최적화된 마이크로서비스 아키텍처 디자인](http://thefarmersfront.github.io/blog/oms-msa-architecture-1/)

MSA 환경에서 효율적인 운영과 안정성 확보를 위해 다음과 같은 측면들이 중요하게 다뤄집니다.

1.  **글로벌 트랜잭션 및 데이터 일관성 관리**:

    - MSA는 각 서비스가 독립적인 DB를 가지므로, 여러 서비스에 걸쳐 트랜잭션에 참여할 때 데이터 일관성을 보장하는 것이 중요합니다. 이를 글로벌 트랜잭션 또는 분산 트랜잭션이라고 합니다. [MSA 환경에서 네트워크 예외를 잘 다루는 방법](https://tech.kakaopay.com/post/msa-transaction/)
    - 특히 결제와 같은 민감한 도메인에서는 이중 결제, 결제 취소 오류 등 고객 불편을 야기하는 예외 상황을 방지하기 위해 엄격한 관리가 필수적입니다. [MSA 환경에서 네트워크 예외를 잘 다루는 방법](https://tech.kakaopay.com/post/msa-transaction/)
    - Saga 패턴과 같은 다양한 분산 트랜잭션 관리 방식이 제시되지만, 기본적으로 서비스 간 네트워크 요청을 주고받는 형태가 됩니다. [MSA 환경에서 네트워크 예외를 잘 다루는 방법](https://tech.kakaopay.com/post/msa-transaction/)

2.  **네트워크 예외 처리**:

    - MSA 환경에서는 같은 요청이 두 번 이상 발생하거나, 네트워크 순서가 뒤집히거나, 각종 타임아웃, 인프라 문제 등으로 인한 네트워크 통신 예외 상황이 발생할 수 있습니다. [MSA 환경에서 네트워크 예외를 잘 다루는 방법](https://tech.kakaopay.com/post/msa-transaction/)
    - 이러한 예외를 안전하게 다루기 위해 API를 요청하는 입장에서는 '알 수 없는 에러'를 처리해야 하며, API를 제공하는 입장에서는 '멱등성(Idempotent)'을 보장하는 API를 제공해야 합니다. [MSA 환경에서 네트워크 예외를 잘 다루는 방법](https://tech.kakaopay.com/post/msa-transaction/)

3.  **관측 가능성(Observability) 확보**:

    - Kafka 기반의 MSA 또는 이벤트 기반 아키텍처에서는 Kafka와 서비스 간의 관계를 정확히 모니터링하는 것이 장애에 취약한 구조를 보완하는 데 필수적입니다. [토스증권의 수 천개 실시간 데이터 파이프라인 운영방법 #2: MSA 환경 Observability 높이기](https://toss.tech/article/MSA-observability)
    - 수많은 서비스 Pod와 Kafka Topic 간의 연결 관계(Producer/Consumer Client와 Broker의 연결)를 파악하고 시각화하여 전체 시스템의 가시성을 높이는 노력이 필요합니다. [토스증권의 수 천개 실시간 데이터 파이프라인 운영방법 #2: MSA 환경 Observability 높이기](https://toss.tech/article/MSA-observability)

4.  **데이터 관리 및 최적화**:

    - 각 도메인으로부터 풀필먼트 처리에 필요한 최소한의 정보만을 동기화하고, 이를 자체 데이터와 결합하여 의미 있는 정보로 재가공하여 제공하는 전략이 중요합니다. [OMS의 최적화된 마이크로서비스 아키텍처 디자인](http://thefarmersfront.github.io/blog/oms-msa-architecture-1/)
    - `Shared Cache`를 활용하여 MSA 전체적으로 자주 활용되는 데이터를 공용으로 관리하고, 담당 MSA는 write, 다른 도메인은 read-only로 조회하게 함으로써 내부 MSA 호출 트래픽을 감소시킬 수 있습니다. [OMS의 최적화된 마이크로서비스 아키텍처 디자인](http://thefarmersfront.github.io/blog/oms-msa-architecture-1/)
    - `Shared Cache` 장애 시 트래픽이 각 MSA로 흘러가는 위험을 줄이기 위해, MSA의 auto scale out 룰을 보수적으로 설정하고, AS-IS 지표를 기준으로 인스턴스 스펙을 조정하며, 캐시의 메모리 사용량을 최적화해야 합니다. [OMS의 최적화된 마이크로서비스 아키텍처 디자인](http://thefarmersfront.github.io/blog/oms-msa-architecture-1/)

5.  **운영 효율성 및 안정성**:
    - MSA는 작은 단위로 일단위 최소 1~2번, 많을 때는 10번 이상 배포 버전을 관리할 수 있어 신속한 기능 반영이 가능합니다. [OMS의 최적화된 마이크로서비스 아키텍처 디자인](http://thefarmersfront.github.io/blog/oms-msa-architecture-1/)
    - 라이브러리 버전업이나 dependency 업데이트 시, 가장 영향도가 적은 서비스로 카나리 테스트를 진행하여 안전하게 전체 시스템의 버전을 최신화할 수 있습니다. [OMS의 최적화된 마이크로서비스 아키텍처 디자인](http://thefarmersfront.github.io/blog/oms-msa-architecture-1/)
    - 인프라 레벨부터 애플리케이션까지 전 계층에서 카나리 배포를 지원하여 안정적인 서비스 구동이 가능합니다. [20년 레거시를 넘어 미래를 준비하는 시스템 만들기](https://toss.tech/article/payments-legacy-1)
    - 로깅, 모니터링 등 전사 공통 기능을 common library로 작성하고 런타임에 자동 주입하거나, 자동 코드 수정 및 Pull Request 생성 시스템을 통해 라이브러리 버전을 최신으로 유지하여 개발 효율성을 높일 수 있습니다. [20년 레거시를 넘어 미래를 준비하는 시스템 만들기](https://toss.tech/article/payments-legacy-1)
    - 모든 엔지니어가 모든 MSA에 대한 동일한 컨텍스트를 유지하는 것이 중요하며, 이를 통해 설계 단계에서의 비효율을 줄이고 효율적인 의사소통을 가능하게 합니다. [OMS의 최적화된 마이크로서비스 아키텍처 디자인](http://thefarmersfront.github.io/blog/oms-msa-architecture-1/)
