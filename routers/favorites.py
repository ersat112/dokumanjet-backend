from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from database import get_db
from models import Favorite, User
from schemas import FavoriteCreate, FavoriteOut
import os

router = APIRouter()

# JWT token okuma ayarı
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Ortamdan JWT bilgileri alınır
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Token'dan kullanıcıyı doğrulama
def get_current_user_email(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token geçersiz.")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Kimlik doğrulama başarısız.")

# === FAVORİ EKLE ===
@router.post("/", response_model=FavoriteOut)
def add_favorite(
    fav: FavoriteCreate,
    db: Session = Depends(get_db),
    user_email: str = Depends(get_current_user_email)
):
    new_fav = Favorite(keyword=fav.keyword, user_email=user_email)
    db.add(new_fav)
    db.commit()
    db.refresh(new_fav)
    return new_fav

# === FAVORİLERİ LİSTELE ===
@router.get("/", response_model=list[FavoriteOut])
def list_favorites(
    db: Session = Depends(get_db),
    user_email: str = Depends(get_current_user_email)
):
    return db.query(Favorite).filter(Favorite.user_email == user_email).all()
