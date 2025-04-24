from pydantic import BaseModel, EmailStr
from typing import Optional, List

# === Authentication Modelleri ===

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


# === Favori Arama ===

class FavoriteCreate(BaseModel):
keyword: str

class FavoriteOut(BaseModel):
id: int
keyword: str
user_email: EmailStr
