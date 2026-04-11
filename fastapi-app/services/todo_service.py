from sqlalchemy.orm import Session
from models.todo import Todo, TodoCreate, TodoUpdate
from typing import Optional


def get_todos(db: Session, user_id: int) -> list[Todo]:
    return db.query(Todo).filter(Todo.user_id == user_id).all()


def create_todo(db: Session, todo_in: TodoCreate, user_id: int) -> Todo:
    todo = Todo(**todo_in.model_dump(), user_id=user_id)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


def update_todo(db: Session, todo_id: int, todo_in: TodoUpdate, user_id: int) -> Optional[Todo]:
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == user_id).first()
    if not todo:
        return None
    for key, value in todo_in.model_dump(exclude_unset=True).items():
        setattr(todo, key, value)
    db.commit()
    db.refresh(todo)
    return todo


def delete_todo(db: Session, todo_id: int, user_id: int) -> None:
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == user_id).first()
    if todo:
        db.delete(todo)
        db.commit()


def toggle_todo(db: Session, todo_id: int, user_id: int) -> Optional[Todo]:
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == user_id).first()
    if not todo:
        return None
    todo.completed = not todo.completed
    db.commit()
    db.refresh(todo)
    return todo
