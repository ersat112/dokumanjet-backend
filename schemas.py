from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from datetime import datetime

# === Authentication Schemas ===
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Kullanıcı şifresi, en az 8 karakter.")

class UserLogin(UserBase):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

# === Search Schemas ===
class SearchItem(BaseModel):
    id: int
    title: str
    snippet: str = Field(..., alias="content")
    url: Optional[str] = None
    score: float

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

class SearchResponse(BaseModel):
    results: List[SearchItem]

# === Favorites Schemas ===
class FavoriteCreate(BaseModel):
    keyword: str = Field(..., description="Favori arama anahtar kelimesi.")

class FavoriteOut(BaseModel):
    id: int
    keyword: str
    created_at: datetime
    # İlişkili kullanıcı bilgisi (opsiyonel client tarafında gösterim için)
    user: Optional[Dict[str, str]] = None

    class Config:
        orm_mode = True

# === News Schemas ===
class NewsArticle(BaseModel):
    title: str
    description: Optional[str]
    url: str
    url_to_image: Optional[str] = Field(None, alias="urlToImage")
    published_at: Optional[datetime] = Field(None, alias="publishedAt")
    source_name: Optional[str] = Field(None, alias="source")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

class NewsResponse(BaseModel):
    articles: List[NewsArticle]

# === Weather Schemas ===
class WeatherInfo(BaseModel):
    city: str
    temperature: float
    humidity: int
    wind_speed: float
    description: str

    class Config:
        orm_mode = True

# === OCR Schemas ===
class OcrResult(BaseModel):
    text: str

    class Config:
        orm_mode = True
