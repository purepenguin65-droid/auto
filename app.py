from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import get_config
from news_collector import collect_news

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
    return {"news_days": cfg.news_days, "max_articles": cfg.news_max_articles}


@app.get("/api/search")
async def api_search(keyword: str = Query(..., min_length=1)):
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


@app.post("/api/search")
async def api_search_post(keyword: str = Form(...)):
    keyword = keyword.strip()
    if not keyword:
        raise HTTPException(status_code=400, detail="키워드를 입력해 주세요.")

    cfg = get_config()
    try:
        articles = collect_news(keyword)
        return JSONResponse({
            "success": True,
            "keyword": keyword,
            "days": cfg.news_days,
            "count": len(articles),
            "articles": [a.to_dict() for a in articles],
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 수집 실패: {e}") from e
