from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import get_config
from news_collector import collect_news
from news_summarizer import summarize_news
from report_generator import generate_report

BASE_DIR = Path(__file__).parent
app = FastAPI(title="뉴스 이슈 수집")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/api/config")
async def api_config():
    cfg = get_config()
    return {
        "news_days": cfg.news_days,
        "max_articles": cfg.news_max_articles,
        "has_gemini": bool(cfg.gemini_api_key),
    }


def _build_report(keyword: str) -> dict:
    cfg = get_config()
    articles = collect_news(keyword)
    summary = summarize_news(keyword, cfg.news_days, articles) if articles else None
    subject, html = generate_report(keyword, cfg.news_days, articles, summary)

    return {
        "success": True,
        "keyword": keyword,
        "days": cfg.news_days,
        "count": len(articles),
        "subject": subject,
        "html": html,
        "articles": [a.to_dict() for a in articles],
        "summary": summary,
    }


def _search_response(keyword: str, summarize: bool = True, with_report: bool = False) -> dict:
    cfg = get_config()
    articles = collect_news(keyword)
    result = {
        "success": True,
        "keyword": keyword,
        "days": cfg.news_days,
        "count": len(articles),
        "articles": [a.to_dict() for a in articles],
    }

    summary = None
    if summarize and articles:
        summary = summarize_news(keyword, cfg.news_days, articles)
        result["summary"] = summary

    if with_report:
        subject, html = generate_report(keyword, cfg.news_days, articles, summary)
        result["subject"] = subject
        result["report_html"] = html

    return result


@app.get("/api/report")
async def api_report(keyword: str = Query(..., min_length=1)):
    keyword = keyword.strip()
    if not keyword:
        raise HTTPException(status_code=400, detail="키워드를 입력해 주세요.")
    try:
        return _build_report(keyword)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"보고서 생성 실패: {e}") from e


@app.post("/api/report")
async def api_report_post(keyword: str = Form(...)):
    keyword = keyword.strip()
    if not keyword:
        raise HTTPException(status_code=400, detail="키워드를 입력해 주세요.")
    try:
        return JSONResponse(_build_report(keyword))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"보고서 생성 실패: {e}") from e


@app.get("/api/report/download")
async def api_report_download(keyword: str = Query(..., min_length=1)):
    keyword = keyword.strip()
    if not keyword:
        raise HTTPException(status_code=400, detail="키워드를 입력해 주세요.")
    try:
        data = _build_report(keyword)
        filename = f"report_{keyword}.html"
        return Response(
            content=data["html"],
            media_type="text/html; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"보고서 생성 실패: {e}") from e


@app.get("/api/search")
async def api_search(
    keyword: str = Query(..., min_length=1),
    summarize: bool = Query(default=True),
    report: bool = Query(default=False),
):
    keyword = keyword.strip()
    if not keyword:
        raise HTTPException(status_code=400, detail="키워드를 입력해 주세요.")
    try:
        return _search_response(keyword, summarize=summarize, with_report=report)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"처리 실패: {e}") from e


@app.post("/api/search")
async def api_search_post(
    keyword: str = Form(...),
    summarize: bool = Form(default=True),
    report: bool = Form(default=True),
):
    keyword = keyword.strip()
    if not keyword:
        raise HTTPException(status_code=400, detail="키워드를 입력해 주세요.")
    try:
        return JSONResponse(_search_response(keyword, summarize=summarize, with_report=report))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"처리 실패: {e}") from e
