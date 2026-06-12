from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import get_config
from email_sender import send_email
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
        "gemini_model": cfg.gemini_model,
        "default_email": cfg.email_to,
        "has_email": bool(cfg.smtp_user and cfg.smtp_password and cfg.email_from),
    }


async def _do_search(keyword: str) -> dict:
    keyword = keyword.strip()
    if not keyword:
        raise HTTPException(status_code=400, detail="키워드를 입력해 주세요.")

    cfg = get_config()
    try:
        articles = collect_news(keyword)
        return {
            "success": True,
            "keyword": keyword,
            "days": cfg.news_days,
            "count": len(articles),
            "articles": [a.to_dict() for a in articles],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 수집 실패: {e}") from e


def _build_report(keyword: str) -> dict:
    cfg = get_config()
    articles = collect_news(keyword)
    summary = summarize_news(keyword, cfg.news_days, articles) if articles else {
        "headline": f"'{keyword}' 관련 뉴스 없음",
        "overview": f"최근 {cfg.news_days}일간 '{keyword}' 관련 뉴스가 없습니다.",
        "key_points": [],
        "outlook": "",
        "issues": [],
    }
    subject, html = generate_report(
        keyword, cfg.news_days, articles, summary, gemini_model=cfg.gemini_model
    )
    return {
        "success": True,
        "keyword": keyword,
        "days": cfg.news_days,
        "count": len(articles),
        "subject": subject,
        "html": html,
        "summary": summary,
        "articles": [a.to_dict() for a in articles],
    }


@app.get("/api/search")
async def api_search_get(keyword: str = Query(..., min_length=1)):
    return await _do_search(keyword)


@app.post("/api/search")
async def api_search_post(keyword: str = Form(...)):
    return JSONResponse(await _do_search(keyword))


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
        return Response(
            content=data["html"],
            media_type="text/html; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="report_{keyword}.html"'},
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"보고서 생성 실패: {e}") from e


@app.post("/api/send")
async def api_send(
    subject: str = Form(...),
    html: str = Form(...),
    email: str = Form(default=""),
):
    recipient = email.strip() or get_config().email_to
    if not recipient:
        raise HTTPException(status_code=400, detail="수신 이메일을 입력해 주세요.")
    try:
        sent_to = send_email(subject, html, to=recipient)
        return JSONResponse({
            "success": True,
            "message": f"{sent_to}로 보고서를 발송했습니다.",
        })
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이메일 발송 실패: {e}") from e


@app.post("/api/report-and-send")
async def api_report_and_send(
    keyword: str = Form(...),
    email: str = Form(default=""),
):
    keyword = keyword.strip()
    if not keyword:
        raise HTTPException(status_code=400, detail="키워드를 입력해 주세요.")

    recipient = email.strip() or get_config().email_to
    if not recipient:
        raise HTTPException(status_code=400, detail="수신 이메일을 입력해 주세요.")

    try:
        data = _build_report(keyword)
        sent_to = send_email(data["subject"], data["html"], to=recipient)
        data["message"] = f"{sent_to}로 보고서를 발송했습니다."
        return JSONResponse(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
