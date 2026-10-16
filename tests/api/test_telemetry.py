from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.api


def post_telemetry(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    payload: dict[str, Any],
):
    return client.post(
        "/api/v1/telemetry",
        headers=headers["operator"],
        json=payload,
    )


def test_nominal_telemetry_is_accepted(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    telemetry_payload: Callable[..., dict[str, Any]],
) -> None:
    response = post_telemetry(client, headers, telemetry_payload())

    assert response.status_code == 202
    assert response.json()["failsafe_action"] is None


@pytest.mark.security
def test_replayed_sequence_is_rejected(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    telemetry_payload: Callable[..., dict[str, Any]],
) -> None:
    first = post_telemetry(client, headers, telemetry_payload(sequence=7))
    replay = post_telemetry(client, headers, telemetry_payload(sequence=7))

    assert first.status_code == 202
    assert replay.status_code == 409
    assert replay.json()["detail"] == "Replay or out-of-order telemetry detected"


@pytest.mark.security
def test_out_of_order_sequence_is_rejected(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    telemetry_payload: Callable[..., dict[str, Any]],
) -> None:
    post_telemetry(client, headers, telemetry_payload(sequence=10))
    response = post_telemetry(client, headers, telemetry_payload(sequence=9))

    assert response.status_code == 409


@pytest.mark.security
def test_stale_frame_is_rejected(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    telemetry_payload: Callable[..., dict[str, Any]],
) -> None:
    stale_time = (datetime.now(UTC) - timedelta(seconds=31)).isoformat()
    response = post_telemetry(client, headers, telemetry_payload(sent_at=stale_time))

    assert response.status_code == 409
    assert response.json()["detail"] == "Telemetry frame is stale"


@pytest.mark.security
def test_future_frame_is_rejected(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    telemetry_payload: Callable[..., dict[str, Any]],
) -> None:
    future_time = (datetime.now(UTC) + timedelta(seconds=6)).isoformat()
    response = post_telemetry(client, headers, telemetry_payload(sent_at=future_time))

    assert response.status_code == 409
    assert "future" in response.json()["detail"]


def test_unknown_drone_frame_is_rejected(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    telemetry_payload: Callable[..., dict[str, Any]],
) -> None:
    response = post_telemetry(client, headers, telemetry_payload(drone_id="UAS-999"))

    assert response.status_code == 404


@pytest.mark.security
def test_naive_timestamp_is_rejected_by_schema(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    telemetry_payload: Callable[..., dict[str, Any]],
) -> None:
    response = post_telemetry(
        client,
        headers,
        telemetry_payload(sent_at="2026-01-01T12:00:00"),
    )

    assert response.status_code == 422


def test_drone_snapshot_updates_after_telemetry(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    telemetry_payload: Callable[..., dict[str, Any]],
) -> None:
    post_telemetry(
        client,
        headers,
        telemetry_payload(sequence=14, battery_pct=65, x_m=-80, y_m=75),
    )
    response = client.get("/api/v1/fleet", headers=headers["observer"])
    uas_001 = next(item for item in response.json() if item["drone_id"] == "UAS-001")

    assert uas_001["battery_pct"] == 65
    assert uas_001["last_sequence"] == 14
    assert uas_001["x_m"] == -80
