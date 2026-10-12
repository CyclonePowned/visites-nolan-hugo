import pytest
import redis
from fastapi.testclient import TestClient

from app import main


def test_root_incremente(client):
    assert client.get("/").json() == {"visites": 1}
    assert client.get("/").json() == {"visites": 2}


def test_health_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_redis_absent(monkeypatch):
    monkeypatch.setattr(main, "r", redis.Redis(host="localhost", port=1))
    response = TestClient(main.app).get("/health")
    assert response.status_code == 503


def test_metrics(client):
    client.get("/")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text


@pytest.mark.integration
def test_root_redis_reel():
    response = TestClient(main.app).get("/")
    assert response.status_code == 200


def test_reset_compteur(client):
    client.get("/")
    client.get("/")
    response = client.post("/reset")
    assert response.status_code == 200
    assert response.json() == {"visites": 0}
    response2 = client.get("/")
    assert response2.json() == {"visites": 1}


def test_root_en_tete_version(client):
    response = client.get("/")
    assert response.headers["X-Visites-Version"] == "0.1.0"
