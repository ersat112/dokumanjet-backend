import os
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.responses import JSONResponse
from dotenv import load_dotenv
from routers import auth, search, favorites, news, weather, ocr
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from database import engine
from models import Base

load_dotenv()

ENVIRONMENT = os.getenv("ENV", "production")
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost,http://localhost:3000,https://dokumanjet.com").split(",")
ALLOWED_HOSTS = os.getenv("TRUSTED_HOSTS", "localhost,dokumanjet.com").split(",")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("dokumanjet")

app = FastAPI(
title="DokumanJet API",
description="Yapay zekâ destekli belge arama motoru",
version="5.1"
)

Base.metadata.create_all(bind=engine)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS)
app.add_middleware(
CORSMiddleware,
allow_origins=ALLOWED_ORIGINS,
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

from fastapi.openapi.utils import get_openapi
def custom_openapi():
if app.openapi_schema:
return app.openapi_schema
openapi_schema = get_openapi(
title="DokumanJet API",
version="5.1",
description="Yapay zekâ destekli belge arama platformu",
routes=app.routes,
)
openapi_schema["components"]["securitySchemes"] = {
"BearerAuth": {
"type": "http",
"scheme": "bearer",
"bearerFormat": "JWT"
}
}
for path in openapi_schema["paths"].values():
for method in path.values():
method["security"] = [{"BearerAuth": []}]
app.openapi_schema = openapi_schema
return app.openapi_schema
app.openapi = custom_openapi

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
logger.error(f"Unhandled error on path {request.url.path}: {exc}")
return JSONResponse(
status_code=500,
content={"error": "Sunucu hatası oluştu."}
)

@app.get("/health", tags=["Monitor"])
def health_check():
return {"status": "ok", "env": ENVIRONMENT}

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])
app.include_router(favorites.router, prefix="/api/v1/favorites", tags=["Favorites"])
app.include_router(news.router, prefix="/api/v1/news", tags=["News"])
app.include_router(weather.router, prefix="/api/v1/weather", tags=["Weather"])
app.include_router(ocr.router, prefix="/api/v1/ocr", tags=["OCR"])

@app.get("/")
@limiter.limit("10/minute")
def root():
return {"message": "DokumanJet API v5.1 Aktif"}
