from __future__ import annotations

import json
import re

import google.genai as genai

from config import get_config
from news_collector import NewsArticle


def _build_article_context(articles: list[NewsArticle]) -> str:
    lines = []
    for i, article in enumerate(articles, 1):
        lines.append(
            f"{i}. [{article.published.strftime('%Y-%m-%d')}] "
            f"{article.title} ({article.source})\n"
            f"   {article.summary or '(요약 없음)'}"
        )
    return "\n\n".join(lines)


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def summarize_news(keyword: str, days: int, articles: list[NewsArticle]) -> dict:
    cfg = get_config()
    cfg.validate_gemini()

    if not articles:
        return {
            "headline": f"'{keyword}' 관련 최근 {days}일 뉴스 없음",
            "overview": f"최근 {days}일간 '{keyword}' 관련 뉴스가 수집되지 않았습니다.",
            "key_points": [],
            "outlook": "",
        }

    client = genai.Client(api_key=cfg.gemini_api_key)
    prompt = f"""당신은 뉴스 분석 전문가입니다. '{keyword}' 키워드 관련 최근 {days}일 뉴스 {len(articles)}건을 분석해 **A4 한 장**에 들어갈 요약 보고서를 작성하세요.

## 수집된 기사
{_build_article_context(articles)}

## 작성 지침 (간결하게, 한 장 분량)
1. headline: 핵심을 담은 한 줄 헤드라인 (30자 이내)
2. overview: 2~3문장 종합 요약
3. key_points: 핵심 이슈 4~6개, 각 항목 **한 문장** (bullet 형태)
4. outlook: 향후 주목할 점 1~2문장

기사 목록을 나열하지 말고, 분석·종합만 작성하세요.

반드시 아래 JSON만 출력:
{{
  "headline": "...",
  "overview": "...",
  "key_points": ["...", "..."],
  "outlook": "..."
}}"""

    response = client.models.generate_content(
        model=cfg.gemini_model,
        contents=prompt,
    )
    data = _extract_json(response.text)
    data["issues"] = [
        {"title": p.split(".")[0] if "." in p else p[:40], "description": p}
        for p in data.get("key_points", [])
    ]
    return data
