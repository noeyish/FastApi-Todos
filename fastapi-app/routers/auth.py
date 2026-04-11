from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import create_access_token
from models.user import UserCreate, UserResponse, UserLogin
from services.auth_service import get_user_by_email, create_user, authenticate_user

router = APIRouter(prefix="/auth", tags=["auth"])

DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
    responses={400: {"description": "이미 사용 중인 이메일입니다."}},
)
def register(user_in: UserCreate, db: DbSession):
    if get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="이미 사용 중인 이메일입니다.")
    return create_user(db, user_in)


@router.post(
    "/login",
    responses={401: {"description": "이메일 또는 비밀번호가 올바르지 않습니다."}},
)
def login(user_in: UserLogin, db: DbSession):
    user = authenticate_user(db, user_in.email, user_in.password)
    if not user:
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}
