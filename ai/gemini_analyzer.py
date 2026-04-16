import os
import logging
from pathlib import Path
import google.generativeai as genai

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

PROMPT_FILE = Path(__file__).parent.parent / "config" / "prompt.txt"


def load_prompt_template() -> str:
    """config/prompt.txt 에서 프롬프트 템플릿을 불러옵니다. 주석 줄은 제외됩니다."""
    if not PROMPT_FILE.exists():
        raise FileNotFoundError(f"프롬프트 파일을 찾을 수 없습니다: {PROMPT_FILE}")

    lines = PROMPT_FILE.read_text(encoding="utf-8").splitlines()
    # '#' 로 시작하는 주석 줄 제거 후 합치기
    cleaned = "\n".join(line for line in lines if not line.startswith("#"))
    return cleaned.strip()


def build_prompt(posts: list[dict]) -> str:
    """수집된 게시글 목록을 프롬프트 템플릿에 삽입합니다."""
    template = load_prompt_template()
    titles_text = "\n".join(
        f"{i + 1}. {post['title']}" for i, post in enumerate(posts)
    )
    return template.replace("{titles}", titles_text)


def analyze(posts: list[dict]) -> str:
    """
    Gemini API를 사용해 게시글 제목 목록을 분석합니다.

    Args:
        posts: 크롤러가 반환한 게시글 딕셔너리 리스트

    Returns:
        Gemini의 분석 결과 텍스트
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("환경 변수 GEMINI_API_KEY 가 설정되지 않았습니다.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = build_prompt(posts)
    logger.info(f"Gemini 분석 요청 - 게시글 수: {len(posts)}")

    response = model.generate_content(prompt)
    result = response.text
    logger.info("Gemini 분석 완료")
    return result
