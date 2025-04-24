from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from database import get_db
from models import Favorite, User
from schemas import FavoriteCreate, FavoriteOut
import os

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# JWT Ayarları
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Token’dan kullanıcıyı doğrula
def get_current_user_email(token: str = Depends(oauth2_scheme)) -> str:
try:
payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
email: str = payload.get("sub")
if not email:
raise HTTPException(status_code=401, detail="Token geçersiz.")
return email
except JWTError:
raise HTTPException(status_code=401, detail="Kimlik doğrulama başarısız.")

# Favori ekle
@router.post("/", response_model=FavoriteOut)
def add_favorite(fav: FavoriteCreate, db: Session = Depends(get_db), user_email: str = Depends(get_current_user_email)):
new_fav = Favorite(keyword=fav.keyword, user_email=user_email)
db.add(new_fav)
db.commit()
db.refresh(new_fav)
return new_fav

# Favorileri listele
@router.get("/", response_model=list[FavoriteOut])
def list_favorites(db: Session = Depends(get_db), user_email: str = Depends(get_current_user_email)):
return db.query(Favorite).filter(Favorite.user_email == user_email).all()
Models.py
from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class User(Base):
__tablename__ = "users"

id = Column(Integer, primary_key=True, index=True)
email = Column(String, unique=True, index=True, nullable=False)
hashed_password = Column(String, nullable=False)

class Favorite(Base):
__tablename__ = "favorites"

id = Column(Integer, primary_key=True, index=True)
keyword = Column(String, nullable=False)
user_email = Column(String, ForeignKey("users.email"), nullable=False)
Schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List

# === Authentication ===
class UserCreate(BaseModel):
email: EmailStr
password: str

class UserLogin(BaseModel):
email: EmailStr
password: str

class Token(BaseModel):
access_token: str
token_type: str

# === Arama Sonucu ===
class SearchResult(BaseModel):
id: int
title: str
content: str
score: float

# === Favoriler ===
class FavoriteCreate(BaseModel):
keyword: str

class FavoriteOut(BaseModel):
id: int
keyword: str
user_email: EmailStr
