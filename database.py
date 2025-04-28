import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# .env dosyasından ortam değişkenlerini yükle
load_dotenv()

# Ortam değişkenlerinden veritabanı URL'sini al
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

# SQLAlchemy Engine oluşturma (Postgres için pool_pre_ping önerilir)
engine = create_engine(
    DATABASE_URL,
    echo=False,              # True olursa SQL sorguları konsola loglanır
    pool_pre_ping=True,
    future=True
)

# Session yapılandırması
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # commit sonrası nesnelerin yaşam süresini koru
)

# ORM taban sınıfı
Base = declarative_base()

# Dependency: DB session aç/kapat

def get_db():
    """
    FastAPI dependency: her istek için yeni bir DB session oluşturur ve
    iş bitince kapatır.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
