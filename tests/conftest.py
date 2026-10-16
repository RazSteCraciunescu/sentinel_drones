from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient

from sentinel_uas.app import create_app
from sentinel_uas.config import Settings


@pytest.fixture()
def settings() -> Settings:
    return Settings()


@pytest.fixture()
def client(settings: Settings) -> TestClient:
    with TestClient(create_app(settings)) as test_client:
        yield test_client


@pytest.fixture()
def headers(settings: Settings) -> dict[str, dict[str, str]]:
    return {
        "observer": {"X-Lab-Token": settings.observer_token},
        "operator": {"X-Lab-Token": settings.operator_token},
        "auditor": {"X-Lab-Token": settings.auditor_token},
        "maintainer": {"X-Lab-Token": settings.maintainer_token},
    }


@pytest.fixture()
def mission_payload() -> Callable[..., dict[str, Any]]:
    def build(**overrides: Any) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "mission_id": "MSN-001",
            "drone_id": "UAS-001",
            "mission_type": "infrastructure_inspection",
            "waypoints": [
                {"x_m": -40, "y_m": 30, "altitude_m": 40},
                {"x_m": 40, "y_m": 30, "altitude_m": 45},
            ],
            "battery_pct": 86,
            "estimated_duration_min": 20,
            "reserve_battery_pct": 20,
            "link_quality_pct": 92,
        }
        payload.update(overrides)
        return payload

    return build


@pytest.fixture()
def telemetry_payload() -> Callable[..., dict[str, Any]]:
    def build(**overrides: Any) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "drone_id": "UAS-001",
            "sequence": 1,
            "sent_at": datetime.now(UTC).isoformat(),
            "x_m": 10,
            "y_m": 20,
            "altitude_m": 35,
            "battery_pct": 80,
            "link_quality_pct": 90,
            "sensor_confidence": 0.95,
            "mode": "active",
        }
        payload.update(overrides)
        return payload

    return build


@pytest.fixture()
def command_payload() -> Callable[..., dict[str, Any]]:
    def build(**overrides: Any) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "command_id": "CMD-001",
            "drone_id": "UAS-001",
            "action": "hold",
            "issued_at": datetime.now(UTC).isoformat(),
            "ttl_seconds": 15,
            "reason": "operator safety check",
        }
        payload.update(overrides)
        return payload

    return build
