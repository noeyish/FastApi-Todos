from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import decode_access_token
from models.todo import TodoCreate, TodoUpdate, TodoResponse
from models.user import User
from services import todo_service

router = APIRouter(prefix="/todos", tags=["todos"])
bearer = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다.")
    return user


@router.get("", response_model=list[TodoResponse])
def list_todos(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return todo_service.get_todos(db, current_user.id)


@router.post("", response_model=TodoResponse, status_code=201)
def create_todo(todo_in: TodoCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return todo_service.create_todo(db, todo_in, current_user.id)


@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo_in: TodoUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    todo = todo_service.update_todo(db, todo_id, todo_in, current_user.id)
    if not todo:
        raise HTTPException(status_code=404, detail="할 일을 찾을 수 없습니다.")
    return todo


@router.delete("/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    todo_service.delete_todo(db, todo_id, current_user.id)


@router.patch("/{todo_id}/toggle", response_model=TodoResponse)
def toggle_todo(todo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    todo = todo_service.toggle_todo(db, todo_id, current_user.id)
    if not todo:
        raise HTTPException(status_code=404, detail="할 일을 찾을 수 없습니다.")
    return todo
