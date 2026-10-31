from conftest import client, auth_headers
from main import app
import pytest


# def test_login_unknown_user_returns_401(client):
#     response = client.post("/login", data={"username": "nobody@example.com", "password": "whatever"})
#     assert response.status_code == 401
#     assert response.json()["detail"] == "Invalid Credentials!"

# def test_login_with_no_credentials_422(client):
#     response = client.post("/login")
#     assert response.status_code == 422

# def test_register_user_201(client):
#     response = client.post("/register", json={"email": "chocolate@test.com", "password": "NewAcc2026!!"})
#     data = response.json()
#     assert response.status_code == 201
#     assert "id" in data
#     assert data["email"] == "chocolate@test.com"
#     assert "hashed_password" not in data
#     assert "password" not in data



def test_get_empty_list_of_applications(client, auth_headers):
    response = client.get("/get_applications", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_login_success_returns_token(client, auth_headers):
    response = client.post("/login", data={"username": "chocolate@test.com", "password": "NewAcc2026!!"})
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"

def test_login_wrong_password_returns_401(client, auth_headers):
    response = client.post("/login", data={"username": "chocolate@test.com", "password": "WrongPass1!"})
    assert response.status_code == 401

def test_register_duplicate_email_returns_400(client, auth_headers):
    response = client.post("/register", json={"email": "chocolate@test.com", "password": "NewAcc2026!!"})
    assert response.status_code == 400


@pytest.mark.parametrize("bad_password", ["short1!", "nouppercase1!", "NOLOWERCASE1!", "NoDigits!!", "NoSpecial123"])
def test_register_weak_password_returns_422(client, bad_password):
    response = client.post("/register", json={"email": "weak@test.com", "password": bad_password})
    assert response.status_code == 422