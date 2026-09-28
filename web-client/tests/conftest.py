import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def app_client(tmp_path, monkeypatch):
    from app.config import settings

    static_dir = tmp_path / "static"
    templates_dir = tmp_path / "templates"
    static_dir.mkdir()
    templates_dir.mkdir()
    monkeypatch.setattr(settings, "STATIC_DIR", static_dir)
    monkeypatch.setattr(settings, "TEMPLATES_DIR", templates_dir)

    from app.main import app
    with TestClient(app) as client:
        yield client