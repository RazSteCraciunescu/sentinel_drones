from collections.abc import Callable
from typing import Any

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.api


def post_mission(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    payload: dict[str, Any],
):
    return client.post(
        "/api/v1/missions/validate",
        headers=headers["operator"],
        json=payload,
    )


def test_safe_mission_is_approved(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    mission_payload: Callable[..., dict[str, Any]],
) -> None:
    response = post_mission(client, headers, mission_payload())

    assert response.status_code == 200
    body = response.json()
    assert body["approved"] is True
    assert body["reasons"] == ["all configured safety gates passed"]
    assert body["projected_battery_at_recovery_pct"] == 79.0


def test_low_battery_mission_is_rejected(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    mission_payload: Callable[..., dict[str, Any]],
) -> None:
    response = post_mission(client, headers, mission_payload(battery_pct=29))

    assert response.status_code == 200
    assert response.json()["approved"] is False
    assert any("launch battery" in reason for reason in response.json()["reasons"])


def test_low_link_quality_mission_is_rejected(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    mission_payload: Callable[..., dict[str, Any]],
) -> None:
    response = post_mission(client, headers, mission_payload(link_quality_pct=54))

    assert response.json()["approved"] is False
    assert any("link quality" in reason for reason in response.json()["reasons"])


def test_mission_above_altitude_ceiling_is_rejected(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    mission_payload: Callable[..., dict[str, Any]],
) -> None:
    waypoints = [{"x_m": 0, "y_m": 0, "altitude_m": 121}]
    response = post_mission(client, headers, mission_payload(waypoints=waypoints))

    assert response.json()["approved"] is False
    assert "exceeds the 120 m lab ceiling" in response.json()["reasons"][0]


def test_mission_outside_geofence_is_rejected(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    mission_payload: Callable[..., dict[str, Any]],
) -> None:
    waypoints = [{"x_m": 501, "y_m": 0, "altitude_m": 50}]
    response = post_mission(client, headers, mission_payload(waypoints=waypoints))

    assert response.json()["approved"] is False
    assert any("outside" in reason for reason in response.json()["reasons"])


def test_mission_through_restricted_zone_is_rejected(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    mission_payload: Callable[..., dict[str, Any]],
) -> None:
    waypoints = [{"x_m": 150, "y_m": 0, "altitude_m": 50}]
    response = post_mission(client, headers, mission_payload(waypoints=waypoints))

    assert response.json()["approved"] is False
    assert any("restricted zone" in reason for reason in response.json()["reasons"])


def test_projected_battery_reserve_is_enforced(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    mission_payload: Callable[..., dict[str, Any]],
) -> None:
    response = post_mission(
        client,
        headers,
        mission_payload(battery_pct=50, estimated_duration_min=100, reserve_battery_pct=20),
    )

    assert response.json()["approved"] is False
    assert response.json()["projected_battery_at_recovery_pct"] == 15.0


def test_unknown_drone_is_rejected_as_a_business_decision(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    mission_payload: Callable[..., dict[str, Any]],
) -> None:
    response = post_mission(client, headers, mission_payload(drone_id="UAS-999"))

    assert response.status_code == 200
    assert response.json()["approved"] is False
    assert any("not registered" in reason for reason in response.json()["reasons"])


def test_maintenance_drone_cannot_be_planned(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    mission_payload: Callable[..., dict[str, Any]],
) -> None:
    response = post_mission(client, headers, mission_payload(drone_id="UAS-002"))

    assert response.json()["approved"] is False
    assert any("maintenance" in reason for reason in response.json()["reasons"])


def test_delivery_mission_adds_payload_control(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    mission_payload: Callable[..., dict[str, Any]],
) -> None:
    response = post_mission(
        client,
        headers,
        mission_payload(mission_type="supply_delivery"),
    )

    assert response.json()["approved"] is True
    assert any("payload mass" in item for item in response.json()["required_controls"])
