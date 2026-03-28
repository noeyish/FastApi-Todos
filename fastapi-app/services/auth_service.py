from sqlalchemy.orm import Session
from models.user import User, UserCreate


def get_user_by_email(db: Session, email: str) -> User | None:
    # TODO: 구현
    raise NotImplementedError


def create_user(db: Session, user_in: UserCreate) -> User:
    # TODO: 구현
    raise NotImplementedError


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    # TODO: 구현
    raise NotImplementedError
