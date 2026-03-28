from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models.user import UserCreate, UserResponse, UserLogin

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # TODO: 구현
    raise NotImplementedError


@router.post("/login")
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    # TODO: 구현 — {"access_token": ..., "token_type": "bearer"} 반환
    raise NotImplementedError
