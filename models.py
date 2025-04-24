from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

# 1. önce User tablosu
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

# 2. sonra Favorite tablosu (user_email foreign key olarak bağlı)
class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, nullable=False)
    user_email = Column(String, ForeignKey("users.email"), nullable=False)
