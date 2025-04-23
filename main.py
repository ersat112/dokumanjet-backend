from fastapi import FastAPI
from routers import auth, search, favorites, ocr, weather, news

app = FastAPI(title="DokumanJet API")

app.include_router(auth.router, prefix="/auth")
app.include_router(search.router, prefix="/search")
app.include_router(favorites.router, prefix="/favorites")
app.include_router(ocr.router, prefix="/ocr")
app.include_router(weather.router, prefix="/weather")
app.include_router(news.router, prefix="/news")