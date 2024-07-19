from fastapi.testclient import TestClient
from main import app  # Ensure the path to the main file is correct
from datetime import date

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

    return user_id, response.json()["id"]

def test_read_user_sessions():
    user_id, _ = test_create_session()
    response = client.get(f"/users/{user_id}/sessions/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_read_specific_session():
    user_id, session_id = test_create_session()
    response = client.get(f"/users/{user_id}/sessions/{session_id}")
    assert response.status_code == 200
    assert response.json()["id"] == session_id
    assert response.json()["user_id"] == user_id

def test_update_session():
    user_id, session_id = test_create_session()
    updated_session_data = {
        "user_id": user_id,
        "session_date": date.today().isoformat(),
        "buy_in": 120.0,
        "winnings": 180.0
    }
    response = client.put(f"/users/{user_id}/sessions/{session_id}", json=updated_session_data)
    assert response.status_code == 200
    assert response.json()["buy_in"] == 120.0
    assert response.json()["winnings"] == 180.0
    assert response.json()["profit"] == 60.0

def test_delete_session():
    user_id, session_id = test_create_session()
    response = client.delete(f"/users/{user_id}/sessions/{session_id}")
    assert response.status_code == 200
    assert response.json() == {"detail": "Session deleted"}
