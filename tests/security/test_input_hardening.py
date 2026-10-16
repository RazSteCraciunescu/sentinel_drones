from collections.abc import Callable
from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.mark.security
def test_identifier_rejects_path_like_content(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    mission_payload: Callable[..., dict[str, Any]],
) -> None:
    response = client.post(
        "/api/v1/missions/validate",
        headers=headers["operator"],
        json=mission_payload(mission_id="../../etc/passwd"),
    )

    assert response.status_code == 422


@pytest.mark.security
def test_extra_command_field_is_rejected(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    command_payload: Callable[..., dict[str, Any]],
) -> None:
    payload = command_payload(command_id="CMD-EXTRA")
    payload["admin_override"] = True
    response = client.post(
        "/api/v1/commands/safe",
        headers=headers["operator"],
        json=payload,
    )

    assert response.status_code == 422
    fleet = client.get("/api/v1/fleet", headers=headers["operator"]).json()
    uas_001 = next(item for item in fleet if item["drone_id"] == "UAS-001")
    assert uas_001["mode"] == "standby"


@pytest.mark.security
def test_reason_length_is_bounded(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    command_payload: Callable[..., dict[str, Any]],
) -> None:
    response = client.post(
        "/api/v1/commands/safe",
        headers=headers["operator"],
        json=command_payload(reason="x" * 201),
    )

    assert response.status_code == 422


@pytest.mark.security
def test_waypoint_count_is_bounded(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    mission_payload: Callable[..., dict[str, Any]],
) -> None:
    waypoints = [{"x_m": 0, "y_m": 0, "altitude_m": 20}] * 51
    response = client.post(
        "/api/v1/missions/validate",
        headers=headers["operator"],
        json=mission_payload(waypoints=waypoints),
    )

    assert response.status_code == 422
