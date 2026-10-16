from collections.abc import Callable
from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.mark.security
def test_missing_token_is_rejected(client: TestClient) -> None:
    response = client.get("/api/v1/fleet")

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing X-Lab-Token"


@pytest.mark.security
def test_invalid_token_is_rejected(client: TestClient) -> None:
    response = client.get("/api/v1/fleet", headers={"X-Lab-Token": "wrong-token"})

    assert response.status_code == 401


@pytest.mark.security
def test_observer_cannot_submit_command(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    command_payload: Callable[..., dict[str, Any]],
) -> None:
    response = client.post(
        "/api/v1/commands/safe",
        headers=headers["observer"],
        json=command_payload(),
    )

    assert response.status_code == 403


@pytest.mark.security
def test_auditor_cannot_submit_mission(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    mission_payload: Callable[..., dict[str, Any]],
) -> None:
    response = client.post(
        "/api/v1/missions/validate",
        headers=headers["auditor"],
        json=mission_payload(),
    )

    assert response.status_code == 403


@pytest.mark.security
def test_operator_cannot_read_audit_log(
    client: TestClient,
    headers: dict[str, dict[str, str]],
) -> None:
    response = client.get("/api/v1/audit/events", headers=headers["operator"])

    assert response.status_code == 403


@pytest.mark.security
def test_auditor_can_read_audit_log(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    mission_payload: Callable[..., dict[str, Any]],
) -> None:
    client.post(
        "/api/v1/missions/validate",
        headers=headers["operator"],
        json=mission_payload(),
    )
    response = client.get("/api/v1/audit/events", headers=headers["auditor"])

    assert response.status_code == 200
    assert response.json()[0]["action"] == "mission.validate"


@pytest.mark.security
def test_only_maintainer_can_reset(
    client: TestClient,
    headers: dict[str, dict[str, str]],
) -> None:
    denied = client.post("/api/v1/simulation/reset", headers=headers["operator"])
    allowed = client.post("/api/v1/simulation/reset", headers=headers["maintainer"])

    assert denied.status_code == 403
    assert allowed.status_code == 204
