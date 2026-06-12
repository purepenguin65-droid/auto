from __future__ import annotations

import re
import urllib.parse
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

import feedparser
import requests

from config import get_config


@dataclass
class NewsArticle:
    title: str
    link: str
    source: str
    published: datetime
    summary: str

    def to_dict(self) -> dict:
        data = asdict(self)
        data["published"] = self.published.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M")
        return data


def _parse_published(entry: dict) -> datetime | None:
    for key in ("published_parsed", "updated_parsed"):
        parsed = entry.get(key)
        if parsed:
            return datetime(*parsed[:6], tzinfo=timezone.utc)
    for key in ("published", "updated"):
        raw = entry.get(key)
        if raw:
            try:
                dt = parsedate_to_datetime(raw)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except (TypeError, ValueError):
                continue
    return None


def _extract_source(entry: dict) -> str:
    source = entry.get("source", {})
    if isinstance(source, dict) and source.get("title"):
        return source["title"]
    title = entry.get("title", "")
    match = re.search(r"\s-\s(.+)$", title)
    return match.group(1).strip() if match else "알 수 없음"


def _clean_title(title: str) -> str:
    return re.sub(r"\s-\s.+$", "", title).strip()


def _clean_summary(summary: str) -> str:
    text = re.sub(r"<[^>]+>", "", summary or "")
    return re.sub(r"\s+", " ", text).strip()


def collect_news(
    keyword: str,
    days: int | None = None,
    max_articles: int | None = None,
) -> list[NewsArticle]:
    cfg = get_config()
    days = days or cfg.news_days
    max_articles = max_articles or cfg.news_max_articles
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    query = urllib.parse.quote(f"{keyword} when:{days}d")
    url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; NewsReportBot/1.0)"}

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    feed = feedparser.parse(response.content)
    articles: list[NewsArticle] = []
    seen_titles: set[str] = set()

    for entry in feed.entries:
        published = _parse_published(entry)
        if published and published < cutoff:
            continue

        title = _clean_title(entry.get("title", ""))
        if not title or title in seen_titles:
            continue
        seen_titles.add(title)

        articles.append(
            NewsArticle(
                title=title,
                link=entry.get("link", ""),
                source=_extract_source(entry),
                published=published or datetime.now(timezone.utc),
                summary=_clean_summary(entry.get("summary", "")),
            )
        )
        if len(articles) >= max_articles:
            break

    articles.sort(key=lambda a: a.published, reverse=True)
    return articles
