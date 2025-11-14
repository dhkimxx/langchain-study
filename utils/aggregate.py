from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup
import re


def _render_spa(url: str, wait_time: float = 3.0) -> str:
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # headless Chrome
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Install ChromeDriver automatically, matching local Chrome version
    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)
        time.sleep(wait_time)  # wait for SPA to render
        html = driver.page_source
        return html
    finally:
        driver.quit()


def _html_to_text(html: str) -> str:
    # HTML 파싱
    soup = BeautifulSoup(html, "lxml")

    # 스크립트, 스타일 제거
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    # 텍스트 추출
    text = soup.get_text(separator="\n")

    # 공백 정리
    text = re.sub(r"\n\s*\n", "\n\n", text)  # 빈 줄 2개 이상 → 1개
    text = re.sub(r"[ \t]+", " ", text)  # 탭/중복 스페이스 제거
    text = text.strip()

    return text


def aggregate_text(url: str) -> str:
    return _html_to_text(_render_spa(url=url))


if __name__ == "__main__":
    test_url = "https://toss.tech/article/payments-legacy-3"
    html = _render_spa(test_url)
    text = _html_to_text(html)
    print(text)
