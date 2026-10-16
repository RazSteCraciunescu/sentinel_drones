from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.api


def post_command(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    payload: dict[str, Any],
):
    return client.post(
        "/api/v1/commands/safe",
        headers=headers["operator"],
        json=payload,
    )


def test_hold_command_is_accepted(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    command_payload: Callable[..., dict[str, Any]],
) -> None:
    response = post_command(client, headers, command_payload())

    assert response.status_code == 202
    assert response.json()["resulting_mode"] == "hold"


def test_return_home_command_changes_mode(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    command_payload: Callable[..., dict[str, Any]],
) -> None:
    response = post_command(
        client,
        headers,
        command_payload(command_id="CMD-002", action="return_home"),
    )

    assert response.status_code == 202
    assert response.json()["resulting_mode"] == "return_home"


def test_land_command_changes_mode(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    command_payload: Callable[..., dict[str, Any]],
) -> None:
    response = post_command(
        client,
        headers,
        command_payload(command_id="CMD-003", action="land"),
    )

    assert response.json()["resulting_mode"] == "landed"


@pytest.mark.security
def test_expired_command_is_rejected(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    command_payload: Callable[..., dict[str, Any]],
) -> None:
    issued_at = (datetime.now(UTC) - timedelta(seconds=16)).isoformat()
    response = post_command(client, headers, command_payload(issued_at=issued_at, ttl_seconds=15))

    assert response.status_code == 409
    assert response.json()["detail"] == "Command has expired"


@pytest.mark.security
def test_duplicate_command_id_is_rejected(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    command_payload: Callable[..., dict[str, Any]],
) -> None:
    first = post_command(client, headers, command_payload())
    second = post_command(client, headers, command_payload())

    assert first.status_code == 202
    assert second.status_code == 409
    assert second.json()["detail"] == "Duplicate command_id rejected"


def test_unknown_drone_command_is_rejected(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    command_payload: Callable[..., dict[str, Any]],
) -> None:
    response = post_command(client, headers, command_payload(drone_id="UAS-999"))

    assert response.status_code == 404


@pytest.mark.security
def test_unsupported_action_is_rejected_by_schema(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    command_payload: Callable[..., dict[str, Any]],
) -> None:
    response = post_command(client, headers, command_payload(action="continue_mission"))

    assert response.status_code == 422


@pytest.mark.security
def test_future_command_is_rejected(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    command_payload: Callable[..., dict[str, Any]],
) -> None:
    issued_at = (datetime.now(UTC) + timedelta(seconds=10)).isoformat()
    response = post_command(client, headers, command_payload(issued_at=issued_at))

    assert response.status_code == 409
    assert response.json()["detail"] == "Command timestamp is too far in the future"


@pytest.mark.security
def test_command_timestamp_requires_timezone(
    client: TestClient,
    headers: dict[str, dict[str, str]],
    command_payload: Callable[..., dict[str, Any]],
) -> None:
    response = post_command(
        client,
        headers,
        command_payload(issued_at="2026-09-12T12:00:00"),
    )

    assert response.status_code == 422


@pytest.mark.security
def test_runtime_can_set_a_shorter_command_ttl_limit(
    command_payload: Callable[..., dict[str, Any]],
) -> None:
    from sentinel_uas.app import create_app
    from sentinel_uas.config import Settings

    settings = Settings(max_command_ttl_seconds=10)
    with TestClient(create_app(settings)) as strict_client:
        response = strict_client.post(
            "/api/v1/commands/safe",
            headers={"X-Lab-Token": settings.operator_token},
            json=command_payload(ttl_seconds=15),
        )

    assert response.status_code == 422
    assert response.json()["detail"] == "Command TTL exceeds the lab maximum"
