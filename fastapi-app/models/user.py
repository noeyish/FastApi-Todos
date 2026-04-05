from sqlalchemy import Column, Integer, String
from core.database import Base
from pydantic import BaseModel, ConfigDict, EmailStr


# ORM 모델
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)


# Pydantic 스키마
class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str
