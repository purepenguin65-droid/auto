from __future__ import annotations

from datetime import datetime

from jinja2 import Template

from news_collector import NewsArticle

REPORT_TEMPLATE = Template("""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>{{ subject }}</title>
  <style>
    @page { size: A4; margin: 18mm; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
      width: 210mm;
      min-height: 297mm;
      max-height: 297mm;
      margin: 0 auto;
      padding: 18mm;
      color: #262626;
      font-size: 11pt;
      line-height: 1.5;
      background: #fff;
      overflow: hidden;
    }
    .header {
      border-bottom: 3px solid #1c69d4;
      padding-bottom: 10px;
      margin-bottom: 14px;
    }
    .header-label {
      font-size: 9pt;
      font-weight: 700;
      letter-spacing: 2px;
      text-transform: uppercase;
      color: #1c69d4;
      margin-bottom: 6px;
    }
    .header h1 {
      font-size: 18pt;
      font-weight: 700;
      color: #1a2129;
      margin-bottom: 6px;
      line-height: 1.3;
    }
    .header-meta {
      font-size: 9pt;
      color: #6b6b6b;
    }
    .block { margin-bottom: 14px; }
    .block-title {
      font-size: 10pt;
      font-weight: 700;
      color: #1c69d4;
      margin-bottom: 6px;
      letter-spacing: 0.5px;
    }
    .overview {
      background: #f7f7f7;
      border-left: 4px solid #1c69d4;
      padding: 10px 12px;
      font-size: 10.5pt;
      line-height: 1.55;
    }
    .points { list-style: none; padding: 0; }
    .points li {
      position: relative;
      padding: 5px 0 5px 14px;
      font-size: 10pt;
      border-bottom: 1px solid #eee;
    }
    .points li:last-child { border-bottom: none; }
    .points li::before {
      content: '';
      position: absolute;
      left: 0;
      top: 12px;
      width: 6px;
      height: 6px;
      background: #1c69d4;
    }
    .outlook {
      background: #1a2129;
      color: #fff;
      padding: 10px 12px;
      font-size: 10pt;
    }
    .outlook .block-title { color: #bbb; margin-bottom: 4px; }
    .footer {
      position: absolute;
      bottom: 18mm;
      left: 18mm;
      right: 18mm;
      font-size: 8pt;
      color: #9a9a9a;
      text-align: center;
      border-top: 1px solid #e6e6e6;
      padding-top: 8px;
    }
    @media print {
      body { width: auto; min-height: auto; max-height: none; }
    }
  </style>
</head>
<body>
  <div class="header">
    <div class="header-label">Intelligence Brief · One Page</div>
    <h1>{{ headline }}</h1>
    <p class="header-meta">{{ keyword }} · 최근 {{ days }}일 · {{ generated_at }} · {{ article_count }}건 분석 · Gemini AI</p>
  </div>

  <div class="block">
    <div class="block-title">종합 요약</div>
    <div class="overview">{{ overview }}</div>
  </div>

  {% if key_points %}
  <div class="block">
    <div class="block-title">핵심 이슈</div>
    <ul class="points">
      {% for point in key_points %}
      <li>{{ point }}</li>
      {% endfor %}
    </ul>
  </div>
  {% endif %}

  {% if outlook %}
  <div class="block outlook">
    <div class="block-title">향후 전망</div>
    <div>{{ outlook }}</div>
  </div>
  {% endif %}

  <div class="footer">News Intelligence · Google News RSS · {{ gemini_model }}</div>
</body>
</html>""")


def generate_report(
    keyword: str,
    days: int,
    articles: list[NewsArticle],
    summary: dict | None,
    gemini_model: str = "gemini-2.5-flash-lite",
) -> tuple[str, str]:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    s = summary or {}

    subject = f"[{keyword}] 최근 {days}일 한 장 요약 보고서"
    html = REPORT_TEMPLATE.render(
        subject=subject,
        keyword=keyword,
        days=days,
        generated_at=generated_at,
        article_count=len(articles),
        headline=s.get("headline", f"{keyword} 주간 이슈 요약"),
        overview=s.get("overview", "수집된 뉴스가 없습니다."),
        key_points=s.get("key_points", []),
        outlook=s.get("outlook", ""),
        gemini_model=gemini_model,
    )
    return subject, html
