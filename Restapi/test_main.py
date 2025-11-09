from fastapi.testclient import TestClient
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db
from core.database import Base
from schema.UserModel import User
SQLALCHEMY_TEST_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker( bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
app.dependency_overrides[get_db] = override_get_db


client = TestClient(app)

def test_create_user():
    data = {
            "id": 3,
        "name": "John",
        "email": "21ohn@gmail.com"
    }
    
    response = client.post("/add_user",json=data)
    print(response)
    assert response.status_code == 200
    assert response.json()["user"]["email"] == "21ohn@gmail.com"

    # assert response.json()['msg'] == "User Added"

def test_check_user():
    data = {
            "id": 3,
        "name": "John",
        "email": "21ohn@gmail.com"
    }
    
    response = client.post("/add_user",json=data)
    assert response.status_code == 400

def test_get_all_users():
    res = client.get("/check")
    assert res.status_code == 200
    