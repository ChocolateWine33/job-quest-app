from fastapi.testclient import TestClient
from main import app



client = TestClient(app)


def test_login_unknown_user_returns_401():
    response = client.post("/login", data={"username": "nobody@example.com", "password": "whatever"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid Credentials!"

def test_login_with_no_credentials_422():
    response = client.post("/login")
    assert response.status_code == 422

