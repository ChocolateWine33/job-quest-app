from conftest import client
from main import app




# def test_login_unknown_user_returns_401(client):
#     response = client.post("/login", data={"username": "nobody@example.com", "password": "whatever"})
#     assert response.status_code == 401
#     assert response.json()["detail"] == "Invalid Credentials!"

# def test_login_with_no_credentials_422(client):
#     response = client.post("/login")
#     assert response.status_code == 422

def test_register_user_201(client):
    response = client.post("/register", json={"email": "chocolate@test.com", "password": "NewAcc2026!!"})
    data = response.json()
    assert response.status_code == 201
    assert "id" in data
    assert data["email"] == "chocolate@test.com"
