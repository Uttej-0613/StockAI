from fastapi.testclient import TestClient
from backend.main import app
import backend.main as main
from backend.services import storage


def _test_settings(tmp_path, api_key=None):
    class TestSettings:
        database_path = str(tmp_path / "stockai-test.db")
        environment = "test"
        max_upload_bytes = 1024
        cors_origins = ["http://testserver"]
        def __init__(self):
            self.api_key = api_key
        def ensure_data_dir(self):
            tmp_path.mkdir(parents=True, exist_ok=True)
    return TestSettings()


def test_health_readiness_and_watchlist(monkeypatch, tmp_path):
    settings = _test_settings(tmp_path)
    monkeypatch.setattr(main, "get_settings", lambda: settings)
    monkeypatch.setattr(storage, "get_settings", lambda: settings)
    with TestClient(app) as client:
        assert client.get("/api/v1/health").status_code == 200
        assert client.get("/api/v1/ready").status_code == 200
        assert client.post("/api/v1/watchlist", json={"symbol": "TCS.NS"}).status_code == 200
        assert "TCS.NS" in client.get("/api/v1/watchlist").json()["symbols"]


def test_api_key_is_enforced_when_configured(monkeypatch, tmp_path):
    settings = _test_settings(tmp_path, api_key="test-secret")
    monkeypatch.setattr(main, "get_settings", lambda: settings)
    monkeypatch.setattr(storage, "get_settings", lambda: settings)
    with TestClient(app) as client:
        assert client.get("/api/v1/health").status_code == 200
        assert client.get("/api/v1/watchlist").status_code == 401
        response = client.get("/api/v1/watchlist", headers={"X-API-Key": "test-secret"})
        assert response.status_code == 200


def test_document_upload_size_is_bounded(monkeypatch, tmp_path):
    settings = _test_settings(tmp_path)
    monkeypatch.setattr(main, "get_settings", lambda: settings)
    monkeypatch.setattr(storage, "get_settings", lambda: settings)
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/documents/ingest",
            files={"file": ("notes.txt", b"x" * 1025, "text/plain")},
        )
        assert response.status_code == 413
