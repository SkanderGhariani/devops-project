from fastapi.testclient import TestClient
from main import app 

client = TestClient(app)

def test_create_user():
    response = client.post("/users/", json={"username": "testuser"})
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_create_session():
    # Create a user first
    response = client.post("/users/", json={"username": "testuser2"})
    assert response.status_code == 200
    user_id = response.json()["id"]

    # Create a session for the user
    session_data = {
        "user_id": user_id,
        "session_date": date.today().isoformat(),
        "buy_in": 100.0,
        "winnings": 150.0
    }
    response = client.post("/sessions/", json=session_data)
    assert response.status_code == 200
    assert response.json()["user_id"] == user_id
    assert response.json()["profit"] == 50.0

def test_read_user_sessions():
    response = client.get("/users/1/sessions/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_read_specific_session():
    response = client.get("/users/1/sessions/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["user_id"] == 1

def test_update_session():
    updated_session_data = {
        "user_id": 1,
        "session_date": date.today().isoformat(),
        "buy_in": 120.0,
        "winnings": 180.0
    }
    response = client.put("/users/1/sessions/1", json=updated_session_data)
    assert response.status_code == 200
    assert response.json()["buy_in"] == 120.0
    assert response.json()["winnings"] == 180.0
    assert response.json()["profit"] == 60.0

def test_delete_session():
    response = client.delete("/users/1/sessions/1")
    assert response.status_code == 200
    assert response.json() == {"detail": "Session deleted"}