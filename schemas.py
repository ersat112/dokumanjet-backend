from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

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

# === Arama ===
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

# === Haberler ===
class NewsItem(BaseModel):
title: str
link: str
summary: str
published: datetime
source: str
