from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# .env dosyasından veritabanı bağlantısını al
DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy bağlantısı
engine = create_engine(DATABASE_URL)

# Session yapılandırması
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM taban sınıfı
Base = declarative_base()

# Dependency: DB session aç/kapat
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
