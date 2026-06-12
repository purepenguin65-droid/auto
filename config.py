import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

ENV_PATH = Path(__file__).parent / ".env"


def _env(key: str, default: str = "") -> str:
    return os.getenv(key, default) or default


@dataclass
class Config:
    gemini_api_key: str = field(default_factory=lambda: _env("GEMINI_API_KEY"))
    gemini_model: str = field(default_factory=lambda: _env("GEMINI_MODEL", "gemini-2.5-flash-lite"))

    news_days: int = field(default_factory=lambda: int(_env("NEWS_DAYS", "7")))
    news_max_articles: int = field(default_factory=lambda: int(_env("NEWS_MAX_ARTICLES", "30")))

    def validate_gemini(self) -> None:
        if not self.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY가 설정되지 않았습니다. "
                "Vercel 환경변수 또는 .env 파일에 API 키를 추가해 주세요."
            )


def get_config() -> Config:
    load_dotenv(ENV_PATH, override=True)
    return Config()
