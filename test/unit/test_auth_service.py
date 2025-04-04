import os

import faker
import pytest
from cloudinary.provisioning import delete_user

from app.database import get_db
from app.services.auth_service import AuthService, SECRET_KEY
from jose import jwt, JWSError
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

auth_service = AuthService()

def test_password_hashing():
    password = "secure123"
    hashed = auth_service.get_password_hash(password)
    assert hashed != password
    assert auth_service.verify_password(password, hashed)


def test_verify_wrong_password():
    password = "secure123"
    wrong_password = "wrongpass"
    hashed = auth_service.get_password_hash(password)
    assert not auth_service.verify_password(wrong_password, hashed)


def test_create_access_token_format():
    data = {"sub": "user@example.com"}
    token = auth_service.create_access_token(data)
    assert isinstance(token, str)
    decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    assert decoded["sub"] == "user@example.com"


def test_access_token_expiry():
    data = {"sub": "user@example.com"}
    token = auth_service.create_access_token(data, expires_delta=timedelta(seconds=1))
    decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    assert "exp" in decoded

def test_register_duplicate_user():
    db: Session = next(get_db())
    email = faker.Faker().email()
    user_data = type("UserData", (), {"email": email, "password": "12345678"})()

    # Створюємо користувача
    auth_service.register_user(user_data, db)

    # Повторна реєстрація має викликати HTTPException
    with pytest.raises(Exception) as exc:
        auth_service.register_user(user_data, db)

    assert "already exists" in str(exc.value)