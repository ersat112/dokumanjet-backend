from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Favorite, User
from schemas import FavoriteCreate, FavoriteOut
from routers.auth import get_current_user

router = APIRouter(
    prefix="/api/v1/favorites",
    tags=["Favorites"]
)

@router.post("/", response_model=FavoriteOut, status_code=status.HTTP_201_CREATED)
def add_favorite(
    fav: FavoriteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Favorite:
    """
    Mevcut kullanıcı için yeni bir favori oluşturur.
    """
    new_fav = Favorite(
        keyword=fav.keyword,
        user_id=current_user.id
    )
    db.add(new_fav)
    db.commit()
    db.refresh(new_fav)
    return new_fav

@router.get("/", response_model=List[FavoriteOut])
def list_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Favorite]:
    """
    Mevcut kullanıcının favori kayıtlarını listeler.
    """
    favs = db.query(Favorite).filter(
        Favorite.user_id == current_user.id
    ).all()
    return favs

