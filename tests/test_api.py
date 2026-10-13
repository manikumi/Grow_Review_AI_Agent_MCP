from starlette.testclient import TestClient

from src.api import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "uptime_seconds" in data
    assert "config" in data


def test_connectors_endpoint():
    response = client.get("/api/connectors")
    assert response.status_code == 200
    data = response.json()
    assert "connectors" in data
    assert len(data["connectors"]) >= 4


def test_latest_pulse_endpoint():
    response = client.get("/api/pulse/latest")
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert "stats" in data
    assert "top_themes" in data
    assert "action_ideas" in data


def test_reviews_endpoint():
    response = client.get("/api/reviews")
    assert response.status_code == 200
    data = response.json()
    assert "reviews" in data
    assert isinstance(data["reviews"], list)


def test_jira_create_endpoint():
    response = client.post("/api/jira/create", json={"task": "Fix stop-loss slippage", "priority": "P1"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "ticket_id" in data
    assert data["status"] == "Created"
