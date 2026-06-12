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
            f"{i}. [{article.published.strftime('%Y-%m-%d %H:%M')}] "
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
            "overview": f"최근 {days}일간 '{keyword}' 관련 뉴스가 수집되지 않았습니다.",
            "issues": [],
        }

    client = genai.Client(api_key=cfg.gemini_api_key)
    prompt = f"""당신은 뉴스 분석 전문가입니다. '{keyword}' 키워드와 관련된 최근 {days}일간 뉴스 기사들을 분석하여 요약 보고서를 작성하세요.

## 수집된 기사
{_build_article_context(articles)}

## 작성 지침
1. overview: 3~5문장으로 핵심 동향과 주요 이슈를 종합 요약
2. issues: 가장 중요한 이슈 5~8개 선별, 각 항목:
   - title: 이슈 제목 (간결하게)
   - description: 2~3문장 설명

반드시 아래 JSON 형식만 출력 (다른 텍스트 없이):
{{
  "overview": "...",
  "issues": [
    {{"title": "...", "description": "..."}}
  ]
}}"""

    response = client.models.generate_content(
        model=cfg.gemini_model,
        contents=prompt,
    )
    return _extract_json(response.text)
