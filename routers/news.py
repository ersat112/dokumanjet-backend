from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from schemas import NewsItem
import feedparser
import requests
from datetime import datetime
import os

router = APIRouter()

@router.get("/", response_model=List[NewsItem])
def get_news(
    q: Optional[str] = Query(None, description="Aramak istediğiniz kelime"),
    source: Optional[str] = Query("rss", description="Haber kaynağı: 'rss' veya 'api'")
):
    news_items = []

    if source == "rss":
        rss_feeds = [
            "https://www.bbc.com/news/rss.xml",
            "https://rss.cnn.com/rss/edition.rss"
        ]
        for feed_url in rss_feeds:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                if q and q.lower() not in entry.title.lower():
                    continue
                news_items.append(NewsItem(
                    title=entry.title,
                    link=entry.link,
                    summary=entry.get("summary", ""),
                    published=datetime(*entry.published_parsed[:6]),
                    source=feed.feed.title
                ))

    elif source == "api":
        api_key = os.getenv("NEWS_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="NEWS_API_KEY tanımlı değil.")
        url = f"https://newsapi.org/v2/everything?q={q or 'gündem'}&apiKey={api_key}"
        response = requests.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="NewsAPI ile veri alınamadı.")
        data = response.json()
        for article in data.get("articles", []):
            news_items.append(NewsItem(
                title=article["title"],
                link=article["url"],
                summary=article.get("description", ""),
                published=datetime.strptime(article["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"),
                source=article["source"]["name"]
            ))

    else:
        raise HTTPException(status_code=400, detail="Kaynak tipi 'rss' veya 'api' olmalıdır.")

    return news_items
