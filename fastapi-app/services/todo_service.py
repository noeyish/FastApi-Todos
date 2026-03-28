from sqlalchemy.orm import Session
from models.todo import Todo, TodoCreate, TodoUpdate


def get_todos(db: Session, user_id: int) -> list[Todo]:
    # TODO: 구현
    raise NotImplementedError


def create_todo(db: Session, todo_in: TodoCreate, user_id: int) -> Todo:
    # TODO: 구현
    raise NotImplementedError


def update_todo(db: Session, todo_id: int, todo_in: TodoUpdate, user_id: int) -> Todo:
    # TODO: 구현
    raise NotImplementedError


def delete_todo(db: Session, todo_id: int, user_id: int) -> None:
    # TODO: 구현
    raise NotImplementedError


def toggle_todo(db: Session, todo_id: int, user_id: int) -> Todo:
    # TODO: 구현
    raise NotImplementedError
