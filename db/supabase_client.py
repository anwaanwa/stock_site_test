import os
import logging
from datetime import datetime, timezone
from supabase import create_client, Client

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Supabase 테이블 이름
TABLE_CRAWL_RESULTS = "crawl_results"


def get_client() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise EnvironmentError("환경 변수 SUPABASE_URL 또는 SUPABASE_KEY 가 설정되지 않았습니다.")
    return create_client(url, key)


def save_result(posts: list[dict], analysis: str) -> None:
    """
    크롤링 결과와 AI 분석 내용을 Supabase에 저장합니다.

    테이블 스키마 (Supabase에서 직접 생성 필요):
        CREATE TABLE crawl_results (
            id          BIGSERIAL PRIMARY KEY,
            crawled_at  TIMESTAMPTZ NOT NULL,
            post_count  INTEGER NOT NULL,
            posts       JSONB NOT NULL,
            analysis    TEXT NOT NULL
        );

    Args:
        posts:    크롤러가 반환한 게시글 리스트
        analysis: Gemini 분석 결과 텍스트
    """
    client = get_client()

    data = {
        "crawled_at": datetime.now(timezone.utc).isoformat(),
        "post_count": len(posts),
        "posts": posts,
        "analysis": analysis,
    }

    response = client.table(TABLE_CRAWL_RESULTS).insert(data).execute()
    logger.info(f"Supabase 저장 완료 - id: {response.data[0].get('id')}")
