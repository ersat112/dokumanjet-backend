import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.responses import JSONResponse
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.openapi.utils import get_openapi

# Routers
from routers.auth import router as auth_router
from routers.search import router as search_router
from routers.favorites import router as favorites_router
from routers.news import router as news_router
from routers.weather import router as weather_router
from routers.ocr import router as ocr_router

from database import engine
from models import Base

# Load environment variables
load_dotenv()

# Settings
environment = os.getenv("ENV", "production")
ALLOWED_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost,http://localhost:3000,https://dokumanjet.com"
).split(",")
ALLOWED_HOSTS = os.getenv(
    "TRUSTED_HOSTS",
    "localhost,dokumanjet.com"
).split(",")

# Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("dokumanjet")

# App initialization
app = FastAPI(
    title="DokumanJet API",
    description="Yapay zekâ destekli belge arama platformu",
    version="5.1"
)

# Database table creation
Base.metadata.create_all(bind=engine)

# Middlewares
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Custom OpenAPI for JWT authentication

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
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
            method.setdefault("security", [{"BearerAuth": []}])
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Global exception handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on path {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Sunucu hatası oluştu."}
    )

# Health check endpoint
@app.get("/health", tags=["Monitor"])
async def health_check():
    return {"status": "ok", "env": environment}

# Include routers
app.include_router(auth_router)
app.include_router(search_router)
app.include_router(favorites_router)
app.include_router(news_router)
app.include_router(weather_router)
app.include_router(ocr_router)

# Root endpoint with rate limit
@app.get("/")
@limiter.limit("10/minute")
async def root(request: Request):
    """
    Ana giriş endpoint'i, dakikada 10 istekle sınırlıdır.
    """
    return {"message": "DokumanJet API v5.1 Aktif"}
