"""No network or model calls; every test uses a disposable local database."""

from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.core.config import Settings
from app.main import create_app


def configuration(tmp_path: Path) -> Settings:
    return Settings(
        _env_file=None,
        data_dir=tmp_path,
        llm_api_key=SecretStr("test-secret-not-a-real-credential"),
    )


def test_health_and_status_do_not_expose_secret(tmp_path: Path) -> None:
    with TestClient(create_app(configuration(tmp_path))) as client:
        health = client.get("/api/v1/health")
        assert health.status_code == 200
        assert health.json()["database"] == "connected"
        response = client.get("/api/v1/status")
        assert response.json()["model"]["key_configured"] is True
        assert "test-secret-not-a-real-credential" not in response.text


def test_space_survives_application_restart(tmp_path: Path) -> None:
    settings = configuration(tmp_path)
    with TestClient(create_app(settings)) as client:
        response = client.post(
            "/api/v1/knowledge-bases", json={"name": " IT 运维知识 ", "description": "故障排查"}
        )
        assert response.status_code == 201
        record = response.json()
        assert record["name"] == "IT 运维知识"
    with TestClient(create_app(settings)) as restarted:
        assert restarted.get("/api/v1/knowledge-bases").json() == [record]
        assert restarted.get(f"/api/v1/knowledge-bases/{record['id']}").json() == record


def test_name_validation_and_duplicate_handling(tmp_path: Path) -> None:
    with TestClient(create_app(configuration(tmp_path))) as client:
        for name in ["   ", "x" * 81]:
            assert client.post("/api/v1/knowledge-bases", json={"name": name}).status_code == 422
        assert client.post("/api/v1/knowledge-bases", json={"name": "IT"}).status_code == 201
        assert client.post("/api/v1/knowledge-bases", json={"name": "it"}).status_code == 409
        assert len(client.get("/api/v1/knowledge-bases").json()) == 1


def test_missing_space_and_planned_chat_have_explicit_errors(tmp_path: Path) -> None:
    with TestClient(create_app(configuration(tmp_path))) as client:
        identifier = str(uuid4())
        assert client.get(f"/api/v1/knowledge-bases/{identifier}").status_code == 404
        assert client.get("/api/v1/knowledge-bases/not-a-uuid").status_code == 422
        response = client.post(
            "/api/v1/chat",
            json={"knowledge_base_id": identifier, "question": "如何排查打印机离线？"},
        )
        assert response.status_code == 501
        assert "尚未实现" in response.json()["detail"]


def test_invalid_host_is_rejected(tmp_path: Path) -> None:
    with TestClient(create_app(configuration(tmp_path))) as client:
        assert (
            client.get("/api/v1/health", headers={"Host": "untrusted.example"}).status_code == 400
        )
