from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models.todo import TodoCreate, TodoUpdate, TodoResponse
from models.user import User

router = APIRouter(prefix="/todos", tags=["todos"])


def get_current_user(db: Session = Depends(get_db)) -> User:
    # TODO: JWT 토큰 검증 후 User 반환
    raise NotImplementedError


@router.get("", response_model=list[TodoResponse])
def list_todos(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # TODO: 구현
    raise NotImplementedError


@router.post("", response_model=TodoResponse, status_code=201)
def create_todo(todo_in: TodoCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # TODO: 구현
    raise NotImplementedError


@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo_in: TodoUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # TODO: 구현
    raise NotImplementedError


@router.delete("/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # TODO: 구현
    raise NotImplementedError


@router.patch("/{todo_id}/toggle", response_model=TodoResponse)
def toggle_todo(todo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # TODO: 구현
    raise NotImplementedError
