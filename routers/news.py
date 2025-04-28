import os
from typing import List, Optional
from datetime import datetime

import feedparser
import httpx
from fastapi import APIRouter, Query, HTTPException, status

from schemas import NewsArticle, NewsResponse

# Router tanımı
router = APIRouter(
    prefix="/api/v1/news",
    tags=["News"]
)

# RSS ve NewsAPI kaynak listesi
RSS_FEEDS = [
    os.getenv("RSS_FEED_BBC", "https://www.bbc.com/news/rss.xml"),
    os.getenv("RSS_FEED_CNN", "https://rss.cnn.com/rss/edition.rss")
]
NEWSAPI_URL = os.getenv("NEWSAPI_URL", "https://newsapi.org/v2/everything")
NEWSAPI_KEY = os.getenv("NEWS_API_KEY")

@router.get("/", response_model=NewsResponse)
async def get_news(
    q: Optional[str] = Query(None, description="Aramak istediğiniz kelime"),
    source: Optional[str] = Query("rss", regex="^(rss|api)$", description="Kaynak: 'rss' veya 'api'"),
    limit: int = Query(10, ge=1, le=50, description="Dönen haber sayısı")
) -> NewsResponse:
    """
    Haberleri RSS veya NewsAPI üzerinden getirir. 'source' parametresi ile seçim yapabilirsiniz.
    """
    items: List[NewsArticle] = []

    if source == "rss":
        for feed_url in RSS_FEEDS:
            parsed = feedparser.parse(feed_url)
            for entry in parsed.entries[:limit]:
                if q and q.lower() not in entry.title.lower():
                    continue
                try:
                    published = datetime(*entry.published_parsed[:6])
                except Exception:
                    published = datetime.utcnow()
                items.append(NewsArticle(
                    title=entry.title,
                    url=entry.link,
                    description=entry.get("summary", ""),
                    url_to_image=entry.get("media_content", [{}])[0].get("url"),
                    published_at=published,
                    source_name=parsed.feed.get("title", "RSS")
                ))
    else:
        # API kaynağı
        if not NEWSAPI_KEY:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="NEWS_API_KEY environment variable is not set"
            )
        params = {"q": q or "gündem", "apiKey": NEWSAPI_KEY, "pageSize": limit}
        async with httpx.AsyncClient() as client:
            resp = await client.get(NEWSAPI_URL, params=params, timeout=10)
        if resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="NewsAPI'den veri alınamadı."
            )
        data = resp.json()
        for article in data.get("articles", []):
            try:
                published = datetime.fromisoformat(article.get("publishedAt", ""))
            except Exception:
                published = datetime.utcnow()
            items.append(NewsArticle(
                title=article.get("title", ""),
                url=article.get("url", ""),
                description=article.get("description", ""),
                url_to_image=article.get("urlToImage"),
                published_at=published,
                source_name=article.get("source", {}).get("name")
            ))

    return NewsResponse(articles=items)
