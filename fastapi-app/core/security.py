from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    # TODO: 구현
    raise NotImplementedError


def verify_password(plain: str, hashed: str) -> bool:
    # TODO: 구현
    raise NotImplementedError


def create_access_token(data: dict) -> str:
    # TODO: 구현
    raise NotImplementedError


def decode_access_token(token: str) -> dict:
    # TODO: 구현
    raise NotImplementedError
