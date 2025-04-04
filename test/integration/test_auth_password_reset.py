from fastapi.testclient import TestClient
from app.main import app
from faker import Faker
import time

client = TestClient(app)
fake = Faker()

def test_password_reset_flow():
    # Реєстрація користувача
    email = fake.email()
    password = "initialPass123"
    client.post("/api/v1/auth/signup", json={"email": email, "password": password})

    # Запит на скидання пароля
    reset_request = client.post("/api/v1/auth/request-password-reset", json={"email": email})
    assert reset_request.status_code == 200

    # Генеруємо токен вручну, як у реальному email
    from app.services.auth_service import AuthService
    auth_service = AuthService()
    token = auth_service.create_access_token({"sub": email})

    # Скидання пароля
    new_password = "newSecurePass123"
    reset_response = client.post("/api/v1/auth/reset-password", json={
        "token": token,
        "new_password": new_password
    })
    assert reset_response.status_code == 200

    # Перевірка логіну з новим паролем
    login_response = client.post("/api/v1/auth/login", data={
        "username": email,
        "password": new_password
    })
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()

def test_reset_with_invalid_token():
    # Використання фейкового токена
    invalid_token = "this.is.not.valid.jwt"
    new_password = "somepass123"
    response = client.post("/api/v1/auth/reset-password", json={
        "token": invalid_token,
        "new_password": new_password
    })
    assert response.status_code == 400 or response.status_code == 422
    assert "detail" in response.json()
