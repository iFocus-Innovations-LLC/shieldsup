"""Overlay API tests. No network and no remediation side effects."""

from __future__ import annotations

import sqlite3

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("AUDIT_DB_PATH", str(tmp_path / "audit.db"))
    monkeypatch.setenv("TOKEN_MODE", "byok")
    monkeypatch.setenv("POOL_REMAINING", "10000")
    from app.main import app

    return TestClient(app)


def _event(decision: str = "deny") -> dict:
    return {
        "actor": "analyst@example.com",
        "action": "review-control",
        "model_id": "gemini-2.0-flash",
        "approx_tokens": 120,
        "decision": decision,
    }


def test_healthz(client: TestClient) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_lists_overlay_paths(client: TestClient) -> None:
    spec = client.get("/openapi.json")
    assert spec.status_code == 200
    paths = spec.json()["paths"]
    assert "/healthz" in paths
    assert "/v1/hitl/events" in paths
    assert "/v1/metering" in paths
    assert "put" not in paths["/v1/hitl/events"]
    assert "delete" not in paths["/v1/hitl/events"]


def test_tenant_header_stub(client: TestClient) -> None:
    missing = client.get("/v1/tenant")
    assert missing.json() == {"tenant_id": "local", "isolated": False}
    named = client.get("/v1/tenant", headers={"X-Tenant-Id": "acme"})
    assert named.json()["tenant_id"] == "acme"
    assert named.json()["isolated"] is False


def test_hitl_deny_is_stored_and_not_remediated(client: TestClient) -> None:
    created = client.post(
        "/v1/hitl/events",
        headers={"X-Tenant-Id": "acme"},
        json=_event("deny"),
    )
    assert created.status_code == 201
    body = created.json()
    assert body["decision"] == "deny"
    assert body["tenant_id"] == "acme"
    assert body["token_mode"] == "byok"
    assert body["approx_tokens"] == 120
    assert body["model_id"] == "gemini-2.0-flash"
    assert body["remediation_executed"] is False
    assert body["timestamp"]

    listed = client.get("/v1/hitl/events", headers={"X-Tenant-Id": "acme"})
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert listed.json()[0]["id"] == body["id"]


def test_approve_event(client: TestClient) -> None:
    created = client.post("/v1/hitl/events", json=_event("approve"))
    assert created.status_code == 201
    assert created.json()["decision"] == "approve"
    assert created.json()["remediation_executed"] is False


def test_invalid_decision_rejected(client: TestClient) -> None:
    payload = _event()
    payload["decision"] = "execute"
    response = client.post("/v1/hitl/events", json=payload)
    assert response.status_code == 422


def test_extra_remediation_field_rejected(client: TestClient) -> None:
    payload = _event()
    payload["remediate"] = True
    response = client.post("/v1/hitl/events", json=payload)
    assert response.status_code == 422


def test_delete_is_not_allowed(client: TestClient) -> None:
    created = client.post("/v1/hitl/events", json=_event())
    event_id = created.json()["id"]
    response = client.delete(f"/v1/hitl/events/{event_id}")
    assert response.status_code == 404 or response.status_code == 405


def test_metering_byok_has_no_pool(client: TestClient) -> None:
    response = client.get("/v1/metering")
    assert response.status_code == 200
    assert response.json()["token_mode"] == "byok"
    assert response.json()["pool_remaining"] is None


def test_metering_pool_stub(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("TOKEN_MODE", "pool")
    monkeypatch.setenv("POOL_REMAINING", "42")
    response = client.get("/v1/metering", headers={"X-Tenant-Id": "acme"})
    assert response.status_code == 200
    assert response.json() == {
        "tenant_id": "acme",
        "token_mode": "pool",
        "pool_remaining": 42,
    }


def test_pool_mode_is_written_on_the_audit_event(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("TOKEN_MODE", "pool")
    created = client.post("/v1/hitl/events", json=_event("approve"))
    assert created.status_code == 201
    assert created.json()["token_mode"] == "pool"


def test_sqlite_rejects_update_and_delete(client: TestClient, tmp_path) -> None:
    client.post("/v1/hitl/events", json=_event())
    conn = sqlite3.connect(tmp_path / "audit.db")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE hitl_events SET decision = 'approve'")
    conn.rollback()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("DELETE FROM hitl_events")
