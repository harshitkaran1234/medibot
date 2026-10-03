from fastapi.testclient import TestClient

from medibot.main import app

client = TestClient(app)


def test_healthcheck():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"success": True, "message": "healthy"}
