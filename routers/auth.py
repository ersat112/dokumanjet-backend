from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from database import get_db
from models import User
from schemas import UserCreate, UserLogin, Token
import os

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Ortam değişkenlerinden JWT ayarlarını al
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 60))


# Şifre hashleme
def get_password_hash(password):
return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
return pwd_context.verify(plain_password, hashed_password)


# JWT Token oluşturma
def create_access_token(data: dict, expires_delta: timedelta = None):
to_encode = data.copy()
expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
to_encode.update({"exp": expire})
return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Kayıt işlemi
@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
db_user = db.query(User).filter(User.email == user.email).first()
if db_user:
raise HTTPException(status_code=400, detail="Bu e-posta zaten kayıtlı.")

hashed_pw = get_password_hash(user.password)
new_user = User(email=user.email, hashed_password=hashed_pw)
db.add(new_user)
db.commit()
db.refresh(new_user)

access_token = create_access_token(data={"sub": new_user.email})
return {"access_token": access_token, "token_type": "bearer"}


# Giriş işlemi
@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
db_user = db.query(User).filter(User.email == user.email).first()
if not db_user or not verify_password(user.password, db_user.hashed_password):
raise HTTPException(status_code=401, detail="Geçersiz e-posta veya şifre.")

access_token = create_access_token(data={"sub": db_user.email})
return {"access_token": access_token, "token_type": "bearer"}
