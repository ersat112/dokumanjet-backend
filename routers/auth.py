import os
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt

from database import get_db
from models import User
from schemas import UserCreate, UserLogin, Token, UserOut

# Router Tanımı
router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

# Şifreleme Context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Ayarları
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 60))

# OAuth2 Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Yardımcı Fonksiyonlar

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: datetime.timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# Endpoint: Kayıt Ol
@router.post(
    "/register",
    response_model=Token,
    status_code=status.HTTP_201_CREATED
)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
) -> Token:
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    hashed_pw = get_password_hash(user_in.password)
    user = User(email=user_in.email, hashed_password=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint: Giriş
@router.post(
    "/login",
    response_model=Token
)
def login(
    user_in: UserLogin,
    db: Session = Depends(get_db)
) -> Token:
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint: Mevcut Kullanıcı Bilgisi
@router.get(
    "/me",
    response_model=UserOut
)
def read_users_me(
    current_user: User = Depends(get_current_user)
) -> UserOut:
    return current_user
