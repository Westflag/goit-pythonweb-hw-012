from fastapi.testclient import TestClient
from app.main import app
from faker import Faker

fake = Faker()

client = TestClient(app)

def test_register_user():
    email = fake.email()
    response = client.post("/api/v1/auth/signup", json={
        "email": email,
        "password": "securepass"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == email
    print(data)
    assert "id" in data

def test_login_fail():
    response = client.post("/api/v1/auth/login", data={
        "username": "fake@example.com",
        "password": "wrongpass"
    })
    assert response.status_code == 401

def test_login_success():
    # Ensure user exists before login
    client.post("/api/v1/auth/signup", json={
        "email": "contactuser@example.com",
        "password": "12345678"
    })

    response = client.post("/api/v1/auth/login", data={
        "username": "contactuser@example.com",
        "password": "12345678"
    })
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data