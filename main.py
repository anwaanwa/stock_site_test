import logging
import sys

from crawler.dcinside_crawler import crawl_titles
from ai.gemini_analyzer import analyze
from db.supabase_client import save_result

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def main():
    logger.info("=== 주식 갤러리 분석 시작 ===")

    # 1. 크롤링
    logger.info("[1/3] 디시인사이드 크롤링 중...")
    posts = crawl_titles(max_pages=3)
    if not posts:
        logger.warning("수집된 게시글이 없습니다. 종료합니다.")
        return

    # 2. AI 분석
    logger.info("[2/3] Gemini 분석 중...")
    analysis = analyze(posts)
    print("\n--- Gemini 분석 결과 ---")
    print(analysis)
    print("------------------------\n")

    # 3. DB 저장
    logger.info("[3/3] Supabase 저장 중...")
    save_result(posts, analysis)

    logger.info("=== 완료 ===")


if __name__ == "__main__":
    main()
