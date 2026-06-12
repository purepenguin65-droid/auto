import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

ENV_PATH = Path(__file__).parent / ".env"


def _env(key: str, default: str = "") -> str:
    return os.getenv(key, default) or default


@dataclass
class Config:
    news_days: int = field(default_factory=lambda: int(_env("NEWS_DAYS", "7")))
    news_max_articles: int = field(default_factory=lambda: int(_env("NEWS_MAX_ARTICLES", "30")))


def get_config() -> Config:
    load_dotenv(ENV_PATH, override=True)
    return Config()
