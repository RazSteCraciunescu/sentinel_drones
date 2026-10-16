from collections.abc import Callable
from typing import Any

import pytest
from fastapi.testclient import TestClient


def submit(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    telemetry_payload: Callable[..., dict[str, Any]],
    **changes: Any,
):
    return client.post(
        "/api/v1/telemetry",
        headers=headers["operator"],
        json=telemetry_payload(**changes),
    )


@pytest.mark.resilience
@pytest.mark.parametrize(
    ("altitude_m", "expected_action"),
    [(120, None), (120.01, "return_home")],
)
def test_altitude_boundary_is_enforced(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    telemetry_payload: Callable[..., dict[str, Any]],
    altitude_m: float,
    expected_action: str | None,
) -> None:
    response = submit(client, headers, telemetry_payload, altitude_m=altitude_m)

    assert response.status_code == 202
    assert response.json()["failsafe_action"] == expected_action


@pytest.mark.resilience
def test_link_at_threshold_remains_nominal(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    telemetry_payload: Callable[..., dict[str, Any]],
) -> None:
    response = submit(client, headers, telemetry_payload, link_quality_pct=30)

    assert response.json()["failsafe_action"] is None


@pytest.mark.resilience
def test_link_below_threshold_requests_return_home(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    telemetry_payload: Callable[..., dict[str, Any]],
) -> None:
    response = submit(client, headers, telemetry_payload, link_quality_pct=29.9)

    assert response.json()["failsafe_action"] == "return_home"


@pytest.mark.resilience
def test_low_confidence_requests_hold(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    telemetry_payload: Callable[..., dict[str, Any]],
) -> None:
    response = submit(client, headers, telemetry_payload, sensor_confidence=0.2)

    assert response.json()["failsafe_action"] == "hold"


@pytest.mark.resilience
def test_critical_battery_requests_land(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    telemetry_payload: Callable[..., dict[str, Any]],
) -> None:
    response = submit(client, headers, telemetry_payload, battery_pct=11)

    assert response.json()["failsafe_action"] == "land"


@pytest.mark.resilience
def test_failsafe_priority_is_deterministic(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    telemetry_payload: Callable[..., dict[str, Any]],
) -> None:
    response = submit(
        client,
        headers,
        telemetry_payload,
        battery_pct=10,
        link_quality_pct=1,
        x_m=900,
        sensor_confidence=0.1,
    )

    assert response.json()["failsafe_action"] == "land"


@pytest.mark.resilience
def test_rejection_counters_are_visible_in_metrics(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    telemetry_payload: Callable[..., dict[str, Any]],
    mission_payload: Callable[..., dict[str, Any]],
    command_payload: Callable[..., dict[str, Any]],
) -> None:
    client.post(
        "/api/v1/missions/validate",
        headers=headers["operator"],
        json=mission_payload(battery_pct=1),
    )
    client.post(
        "/api/v1/commands/safe",
        headers=headers["operator"],
        json=command_payload(drone_id="UAS-999"),
    )
    submit(client, headers, telemetry_payload, sequence=3)
    submit(client, headers, telemetry_payload, sequence=3)

    response = client.get("/api/v1/assurance/metrics", headers=headers["observer"])
    body = response.json()

    assert response.status_code == 200
    assert body["drones_total"] == 3
    assert body["rejected_missions"] == 1
    assert body["rejected_commands"] == 1
    assert body["rejected_telemetry_frames"] == 1
    assert body["audit_chain_valid"] is True
