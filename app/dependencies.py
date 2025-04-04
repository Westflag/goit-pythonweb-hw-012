import os
import json

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.redis import redis_client
from app.database import get_db
from app.models import User
from app.schemas import UserResponse

SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Отримує поточного користувача з токена, перевіряє кеш Redis перед запитом до БД.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        # Спроба дістати з кешу
        cached_user = redis_client.get(f"user:{email}")
        if cached_user:
            return UserResponse(**json.loads(cached_user))

        # Якщо не знайдено — шукаємо в базі
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        # серіалізація через Pydantic
        user_data = UserResponse.model_validate(user).model_dump()
        redis_client.setex(f"user:{email}", 3600, json.dumps(user_data))

        return UserResponse(**user_data)

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")