import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "app" in response.json()


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_chat_endpoint(client):
    response = client.post(
        "/api/v1/chat",
        json={"message": "hello"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "intent" in data
    assert "session_id" in data

