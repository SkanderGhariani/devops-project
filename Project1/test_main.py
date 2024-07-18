# Project1/test_main.py

from fastapi.testclient import TestClient
from main import app, Base, engine, SessionLocal
import pytest
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_poker_sessions.db"
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def client():
    # Create the database
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    # Drop the database
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_create_user(client):
    response = client.post("/users/", json={"username": "testuser"})
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_create_session(client, db):
    # Create a user first
    response = client.post("/users/", json={"username": "testuser"})
    user_id = response.json()["id"]
    
    # Create a poker session
    session_data = {
        "user_id": user_id,
        "session_date": "2023-07-01",
        "buy_in": 100.0,
        "winnings": 200.0
    }
    response = client.post("/sessions/", json=session_data)
    assert response.status_code == 200
    assert response.json()["buy_in"] == 100.0
    assert response.json()["winnings"] == 200.0
    assert response.json()["profit"] == 100.0

def test_read_user_sessions(client, db):
    # Create a user first
    response = client.post("/users/", json={"username": "testuser2"})
    user_id = response.json()["id"]
    
    # Create a poker session
    session_data = {
        "user_id": user_id,
        "session_date": "2023-07-01",
        "buy_in": 100.0,
        "winnings": 200.0
    }
    client.post("/sessions/", json=session_data)
    
    # Read sessions for the user
    response = client.get(f"/users/{user_id}/sessions/")
    assert response.status_code == 200
    assert len(response.json()) > 0
