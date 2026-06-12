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

    smtp_host: str = field(default_factory=lambda: _env("SMTP_HOST", "smtp.gmail.com"))
    smtp_port: int = field(default_factory=lambda: int(_env("SMTP_PORT", "587")))
    smtp_user: str = field(default_factory=lambda: _env("SMTP_USER"))
    smtp_password: str = field(default_factory=lambda: _env("SMTP_PASSWORD"))
    email_from: str = field(default_factory=lambda: _env("EMAIL_FROM"))
    email_to: str = field(default_factory=lambda: _env("EMAIL_TO"))

    news_days: int = field(default_factory=lambda: int(_env("NEWS_DAYS", "7")))
    news_max_articles: int = field(default_factory=lambda: int(_env("NEWS_MAX_ARTICLES", "30")))

    def validate_gemini(self) -> None:
        if not self.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY가 설정되지 않았습니다. "
                ".env 또는 Vercel 환경변수에 API 키를 추가해 주세요."
            )

    def validate_email(self) -> None:
        missing = [
            name
            for name, val in [
                ("SMTP_USER", self.smtp_user),
                ("SMTP_PASSWORD", self.smtp_password),
                ("EMAIL_FROM", self.email_from),
            ]
            if not val
        ]
        if missing:
            raise ValueError(
                f"이메일 설정 누락: {', '.join(missing)}. .env 파일을 확인해 주세요."
            )


def get_config() -> Config:
    load_dotenv(ENV_PATH, override=True)
    return Config()
