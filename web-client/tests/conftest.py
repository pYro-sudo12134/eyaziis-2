import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def mock_http():
    client = MagicMock()
    client.post = AsyncMock()
    client.get = AsyncMock()
    client.aclose = AsyncMock()
    return client


@pytest.fixture
def app_client(mock_http, tmp_path, monkeypatch):
    from app.config import settings
    static_dir = tmp_path / "static"
    templates_dir = tmp_path / "templates"
    static_dir.mkdir()
    templates_dir.mkdir()
    monkeypatch.setattr(settings, "STATIC_DIR", static_dir)
    monkeypatch.setattr(settings, "TEMPLATES_DIR", templates_dir)

    from app import api_client as api_module
    api_module.api_client._client = mock_http

    from app.main import app
    with TestClient(app) as client:
        yield client

    api_module.api_client._client = None