from fastapi.testclient import TestClient
from main import app  # Ensure the path to the main file is correct

client = TestClient(app)

def test_create_user():
    response = client.post("/users/", json={"username": "testuser"})
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_read_user_sessions():
    response = client.get("/users/1/sessions/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
