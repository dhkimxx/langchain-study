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


def aggregate_text(url: str) -> str:
    """왜: Cloudflare 등 챌린지 페이지를 고려해 커스텀 Selenium으로 본문을 획득한다."""
    driver = _launch_driver()
    try:
        driver.get(url)

        # 초기 로딩 대기 및 챌린지 통과 대기(최대 25초)
        deadline = time.time() + 25.0
        last_html = driver.page_source
        time.sleep(2.0)
        while time.time() < deadline:
            html = driver.page_source
            if not _looks_like_challenge(html):
                # 안정화를 위해 추가 짧은 대기 후 비교
                time.sleep(1.5)
                html2 = driver.page_source
                if len(html2) >= len(html) and not _looks_like_challenge(html2):
                    text = _html_to_text_via_transformer(html2)
                    if len(text) > 300:
                        return text
            # 변경 감지 없으면 잠깐 대기 후 재시도
            if len(html) == len(last_html):
                time.sleep(1.0)
            last_html = html

        # 타임아웃: 확보 가능한 범위에서 변환
        return _html_to_text_via_transformer(driver.page_source)
    finally:
        driver.quit()


if __name__ == "__main__":
    test_url = "https://toss.tech/article/payments-legacy-3"
    print(aggregate_text(test_url))
