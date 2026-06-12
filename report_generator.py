from __future__ import annotations

from datetime import datetime

from jinja2 import Template

from news_collector import NewsArticle

REPORT_TEMPLATE = Template("""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ subject }}</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&display=swap');
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', system-ui, sans-serif;
      font-weight: 300; font-size: 16px; line-height: 1.55;
      color: #3c3c3c; background: #ffffff;
      max-width: 800px; margin: 0 auto; padding: 0;
    }
    .hero {
      background: #1a2129; color: #ffffff;
      padding: 48px 32px;
    }
    .hero-label {
      font-size: 13px; font-weight: 700; letter-spacing: 1.5px;
      text-transform: uppercase; color: #bbbbbb; margin-bottom: 12px;
    }
    .hero h1 {
      font-size: 32px; font-weight: 700; line-height: 1.15;
      margin-bottom: 12px;
    }
    .hero-meta { font-size: 14px; color: #bbbbbb; }
    .section { padding: 32px; border-bottom: 1px solid #e6e6e6; }
    .section-label {
      font-size: 13px; font-weight: 700; letter-spacing: 1.5px;
      text-transform: uppercase; color: #6b6b6b; margin-bottom: 12px;
    }
    .section h2 {
      font-size: 24px; font-weight: 700; color: #262626;
      margin-bottom: 16px;
    }
    .overview {
      background: #f7f7f7; padding: 24px;
      border-left: 4px solid #1c69d4; font-size: 16px;
    }
    .issue {
      padding: 20px 0; border-bottom: 1px solid #e6e6e6;
    }
    .issue:last-child { border-bottom: none; }
    .issue-title {
      font-size: 18px; font-weight: 700; color: #262626;
      margin-bottom: 8px;
    }
    .issue-desc { font-size: 14px; color: #3c3c3c; margin-bottom: 8px; }
    .article-row {
      padding: 16px 0; border-bottom: 1px solid #e6e6e6;
    }
    .article-row:last-child { border-bottom: none; }
    .article-title { font-size: 16px; font-weight: 700; color: #262626; }
    .article-meta { font-size: 12px; color: #6b6b6b; margin: 4px 0; }
    .article-link {
      font-size: 13px; font-weight: 700; letter-spacing: 1.5px;
      text-transform: uppercase; color: #1c69d4; text-decoration: none;
    }
    .footer {
      padding: 32px; background: #f7f7f7;
      font-size: 12px; color: #9a9a9a; text-align: center;
    }
  </style>
</head>
<body>
  <div class="hero">
    <div class="hero-label">Intelligence Report</div>
    <h1>{{ keyword }} 주간 이슈 보고서</h1>
    <p class="hero-meta">수집 기간: 최근 {{ days }}일 · 생성일: {{ generated_at }} · {{ article_count }}건 수집 · Gemini AI 분석</p>
  </div>

  <div class="section">
    <div class="section-label">Overview</div>
    <h2>종합 요약</h2>
    <div class="overview">{{ overview }}</div>
  </div>

  {% if issues %}
  <div class="section">
    <div class="section-label">Key Issues</div>
    <h2>주요 이슈</h2>
    {% for issue in issues %}
    <div class="issue">
      <div class="issue-title">{{ loop.index }}. {{ issue.title }}</div>
      <div class="issue-desc">{{ issue.description }}</div>
    </div>
    {% endfor %}
  </div>
  {% endif %}

  <div class="section">
    <div class="section-label">Sources</div>
    <h2>수집 기사 목록</h2>
    {% for article in articles %}
    <div class="article-row">
      <div class="article-title">{{ loop.index }}. {{ article.title }}</div>
      <div class="article-meta">{{ article.source }} · {{ article.published }}</div>
      <a class="article-link" href="{{ article.link }}" target="_blank">기사 원문 보기 ›</a>
    </div>
    {% endfor %}
  </div>

  <div class="footer">News Intelligence · Google News RSS · Gemini AI</div>
</body>
</html>""")


def generate_report(
    keyword: str,
    days: int,
    articles: list[NewsArticle],
    summary: dict | None,
) -> tuple[str, str]:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    overview = (summary or {}).get("overview", "수집된 뉴스가 없습니다.")
    issues = (summary or {}).get("issues", [])

    article_rows = [
        {
            "title": a.title,
            "source": a.source,
            "published": a.published.strftime("%Y-%m-%d %H:%M"),
            "link": a.link,
        }
        for a in articles
    ]

    subject = f"[{keyword}] 최근 {days}일 주요 이슈 보고서 ({len(articles)}건)"
    html = REPORT_TEMPLATE.render(
        subject=subject,
        keyword=keyword,
        days=days,
        generated_at=generated_at,
        article_count=len(articles),
        overview=overview,
        issues=issues,
        articles=article_rows,
    )
    return subject, html
