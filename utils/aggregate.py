from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from langchain_core.documents import Document
from langchain_community.document_transformers import Html2TextTransformer


def _launch_driver() -> webdriver.Chrome:
    """왜: headless Chrome을 일관된 옵션으로 실행한다."""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1280,2000")
    chrome_options.add_argument("--lang=ko-KR")
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    )

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)


_CF_PATTERNS = [
    # 공통/영문 메시지
    r"Cloudflare",
    r"Ray ID",
    r"Attention Required",
    r"Checking if the site connection is secure",
    r"Please wait while we verify",
    r"Please stand by",
    r"Checking your browser before accessing",
    r"DDoS protection by Cloudflare",
    r"cf-please-wait",
    r"cf-challenge",
    r"cf-browser-verification",
    r"__cf_chl",
    r"Turnstile",
    r"hCaptcha",
    r"reCAPTCHA",
    r"Are you a robot",
    r"Verify you are human",
    r"Access denied",
    # 한글 메시지
    r"사람인지 확인",
    r"사람임을 증명",
    r"로봇이 아님",
    r"브라우저를 확인",
    r"사이트 연결 보안 확인",
    r"보안을 검토",
    r"보안 검사",
    r"검증 중",
    r"확인 중",
    r"잠시만 기다려 주세요",
]


def _looks_like_challenge(html: str) -> bool:
    return any(re.search(pat, html, re.IGNORECASE) for pat in _CF_PATTERNS)


def _html_to_text_via_transformer(html: str) -> str:
    doc = Document(page_content=html)
    t = Html2TextTransformer()
    out = t.transform_documents([doc])
    texts = [d.page_content for d in out if getattr(d, "page_content", None)]
    return "\n\n".join(texts).strip()


def _fetch_html_via_selenium(url: str) -> str:
    """왜: Cloudflare/challenge를 통과한 뒤의 안정된 HTML 스냅샷을 재사용하기 위함."""
    driver = _launch_driver()
    try:
        driver.get(url)

        deadline = time.time() + 25.0
        last_html = driver.page_source
        time.sleep(2.0)
        while time.time() < deadline:
            html = driver.page_source
            if not _looks_like_challenge(html):
                # 왜: 챌린지/리다이렉트가 끝난 뒤 한 번 더 대기하여 DOM이 안정될 시간을 준다.
                time.sleep(1.5)
                html2 = driver.page_source
                if len(html2) >= len(html) and not _looks_like_challenge(html2):
                    return html2

            if len(html) == len(last_html):
                time.sleep(1.0)
            last_html = html

        # 타임아웃: 확보 가능한 범위에서 가장 최근 HTML 사용
        return driver.page_source
    finally:
        driver.quit()


def aggregate_text(url: str) -> str:
    """왜: 기존 파이프라인과 동일하게 Selenium + Html2Text 기반으로 본문 텍스트를 얻기 위함."""
    html = _fetch_html_via_selenium(url)
    return _html_to_text_via_transformer(html)


def _remove_common_noise_nodes(html: str) -> str:
    """왜: header/nav/footer/aside 등 공통 레이아웃 DOM을 제거해 노이즈를 줄이기 위함."""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        # bs4가 없으면 기존 HTML을 그대로 사용한다.
        return html

    soup = BeautifulSoup(html, "html.parser")

    # 구조적으로 노이즈 가능성이 큰 태그 제거
    for tag_name in ["script", "style", "nav", "footer", "header", "aside"]:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    # 공통적으로 많이 쓰이는 header/footer/nav/사이드바 관련 id/class 제거
    noise_keywords = [
        "header",
        "footer",
        "nav",
        "menu",
        "sidebar",
        "aside",
        "share",
        "social",
        "comment",
        "comments",
        "reply",
        "subscribe",
        "signup",
        "newsletter",
        "related",
        "recommend",
        "recommendation",
        "breadcrumb",
        "tags",
        "meta",
    ]

    for attr in ["id", "class"]:
        for kw in noise_keywords:
            for node in soup.find_all(attrs={attr: re.compile(kw, re.IGNORECASE)}):
                node.decompose()

    return str(soup)


def aggregate_text_dom_clean(url: str) -> str:
    """왜: HTML 단계에서 공통 노이즈 DOM을 제거한 뒤 텍스트를 추출하는 전략."""
    html = _fetch_html_via_selenium(url)
    cleaned_html = _remove_common_noise_nodes(html)
    return _html_to_text_via_transformer(cleaned_html)


def aggregate_text_trafilatura(url: str) -> str:
    """왜: trafilatura의 ML 기반 본문 추출기를 사용해 기사 본문만 최대한 정확히 추출하기 위함."""
    try:
        import trafilatura
    except ImportError as exc:
        raise ImportError(
            "trafilatura가 설치되어 있지 않습니다. `pip install trafilatura` 후 다시 시도해 주세요."
        ) from exc

    html = _fetch_html_via_selenium(url)
    text = trafilatura.extract(html, url=url, favor_precision=True)

    if not text:
        # 왜: 추출 실패 시 기존 aggregate_text 전략으로 안전하게 폴백한다.
        return aggregate_text(url)

    return text.strip()


if __name__ == "__main__":
    test_url = "https://toss.tech/article/payments-legacy-3"
    print(aggregate_text(test_url))
