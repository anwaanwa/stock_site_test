import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# 디시인사이드 국내주식 갤러리 URL
GALLERY_URL = "https://gall.dcinside.com/board/lists/?id=stock_new1"


def get_chrome_options() -> Options:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    return options


def crawl_titles(max_pages: int = 3) -> list[dict]:
    """
    디시인사이드 주식 갤러리에서 게시글 제목 목록을 수집합니다.

    Args:
        max_pages: 크롤링할 최대 페이지 수 (기본 3페이지)

    Returns:
        게시글 정보 리스트 [{"title": str, "author": str, "views": str, "date": str}]
    """
    driver = None
    posts = []

    try:
        options = get_chrome_options()
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 10)

        for page in range(1, max_pages + 1):
            url = f"{GALLERY_URL}&page={page}"
            logger.info(f"크롤링 중: {url}")
            driver.get(url)

            # 게시글 목록 로딩 대기
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tr.ub-content")))
            time.sleep(1)

            rows = driver.find_elements(By.CSS_SELECTOR, "tr.ub-content")
            for row in rows:
                try:
                    # 공지 및 광고 제외 (말머리 없는 일반 글만)
                    gall_num = row.find_element(By.CSS_SELECTOR, "td.gall_num").text.strip()
                    if not gall_num.isdigit():
                        continue

                    title_el = row.find_element(By.CSS_SELECTOR, "td.gall_tit a")
                    title = title_el.text.strip()
                    if not title:
                        continue

                    # 댓글 수 제거 (제목 뒤에 붙는 [n] 제거)
                    if title.endswith("]") and "[" in title:
                        bracket_idx = title.rfind("[")
                        title = title[:bracket_idx].strip()

                    try:
                        author = row.find_element(By.CSS_SELECTOR, "td.gall_writer").text.strip()
                    except Exception:
                        author = ""

                    try:
                        date = row.find_element(By.CSS_SELECTOR, "td.gall_date").get_attribute("title") or \
                               row.find_element(By.CSS_SELECTOR, "td.gall_date").text.strip()
                    except Exception:
                        date = ""

                    try:
                        views = row.find_element(By.CSS_SELECTOR, "td.gall_count").text.strip()
                    except Exception:
                        views = ""

                    posts.append({
                        "title": title,
                        "author": author,
                        "date": date,
                        "views": views,
                    })

                except Exception as e:
                    logger.debug(f"행 파싱 오류 (건너뜀): {e}")
                    continue

            logger.info(f"페이지 {page} 완료 - 누적 게시글 수: {len(posts)}")
            time.sleep(1.5)  # 서버 부하 방지

    except Exception as e:
        logger.error(f"크롤링 실패: {e}")
        raise
    finally:
        if driver:
            driver.quit()

    logger.info(f"크롤링 완료. 총 {len(posts)}개 게시글 수집")
    return posts
