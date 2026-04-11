from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base
from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional


# ORM 모델
class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, default="")
    completed = Column(Boolean, default=False)
    priority = Column(String, default="medium")  # low | medium | high
    due_date = Column(Date, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User")


# Pydantic 스키마
class TodoCreate(BaseModel):
    title: str
    description: str = ""
    priority: str = "medium"
    due_date: Optional[date] = None


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None


class TodoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    completed: bool
    priority: str
    due_date: Optional[date] = None
    user_id: int
