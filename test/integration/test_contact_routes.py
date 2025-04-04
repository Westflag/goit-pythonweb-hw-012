from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Реєстрація та логін для отримання токена
def get_token():
    email = "contactuser@example.com"
    password = "12345678"
    client.post("/api/v1/auth/signup", json={"email": email, "password": password})
    response = client.post("/api/v1/auth/login", data={"username": email, "password": password})
    return response.json()["access_token"]

def test_create_contact():
    token = get_token()
    response = client.post(
        "/api/v1/contacts/contacts/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone_number": "+123456789",
            "birthday": "1990-01-01",
            "additional_info": "Test info"
        }
    )
    print(response)
    assert response.status_code == 201
    assert response.json()["email"] == "john.doe@example.com"

def test_get_contacts():
    token = get_token()
    response = client.get("/api/v1/contacts/contacts/", headers={"Authorization": f"Bearer {token}"})
    print(response)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_search_contact():
    token = get_token()
    response = client.get("/api/v1/contacts/contacts/search?first_name=John", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    results = response.json()
    assert any("John" in contact["first_name"] for contact in results)

def test_update_contact():
    token = get_token()
    contacts = client.get("/api/v1/contacts/contacts/", headers={"Authorization": f"Bearer {token}"}).json()
    if contacts:
        contact_id = contacts[0]["id"]
        response = client.put(
            f"/api/v1/contacts/contacts/{contact_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "first_name": "Johnny",
                "last_name": "Doe",
                "email": "johnny.doe@example.com",
                "phone_number": "+987654321",
                "birthday": "1990-01-01",
                "additional_info": "Updated info"
            }
        )
        assert response.status_code == 200
        assert response.json()["first_name"] == "Johnny"

def test_delete_contact():
    token = get_token()
    contacts = client.get("/api/v1/contacts/contacts/", headers={"Authorization": f"Bearer {token}"}).json()
    if contacts:
        contact_id = contacts[0]["id"]
        response = client.delete(f"/api/v1/contacts/contacts/{contact_id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["detail"] == "Contact deleted"

