from datetime import UTC, datetime

import pytest

from sentinel_uas.config import Settings
from sentinel_uas.models import MissionRequest, SafeCommandAction, TelemetryFrame
from sentinel_uas.safety import determine_failsafe, evaluate_mission
from sentinel_uas.store import LabState


def make_mission(**changes: object) -> MissionRequest:
    data: dict[str, object] = {
        "mission_id": "MSN-UNIT-001",
        "drone_id": "UAS-001",
        "mission_type": "training",
        "waypoints": [{"x_m": -20, "y_m": 20, "altitude_m": 30}],
        "battery_pct": 80,
        "estimated_duration_min": 10,
        "reserve_battery_pct": 20,
        "link_quality_pct": 90,
    }
    data.update(changes)
    return MissionRequest.model_validate(data)


def make_frame(**changes: object) -> TelemetryFrame:
    data: dict[str, object] = {
        "drone_id": "UAS-001",
        "sequence": 1,
        "sent_at": datetime.now(UTC),
        "x_m": 0,
        "y_m": 0,
        "altitude_m": 20,
        "battery_pct": 80,
        "link_quality_pct": 90,
        "sensor_confidence": 0.9,
        "mode": "active",
    }
    data.update(changes)
    return TelemetryFrame.model_validate(data)


@pytest.mark.unit
def test_mission_with_many_waypoints_requires_independent_review() -> None:
    mission = make_mission(
        waypoints=[{"x_m": -200 + index, "y_m": 100, "altitude_m": 30} for index in range(11)]
    )

    result = evaluate_mission(mission, LabState(), Settings())

    assert result.approved is True
    assert "perform an independent route review" in result.required_controls


@pytest.mark.unit
def test_projected_battery_is_clamped_at_zero() -> None:
    mission = make_mission(battery_pct=30, estimated_duration_min=240)

    result = evaluate_mission(mission, LabState(), Settings())

    assert result.projected_battery_at_recovery_pct == 0


@pytest.mark.unit
def test_critical_battery_prioritizes_land() -> None:
    action, reason = determine_failsafe(
        make_frame(battery_pct=12, x_m=700, link_quality_pct=5),
        Settings(),
    )

    assert action == SafeCommandAction.LAND
    assert "critical battery" in reason


@pytest.mark.unit
def test_geofence_breach_triggers_return_home() -> None:
    action, _ = determine_failsafe(make_frame(x_m=-501), Settings())

    assert action == SafeCommandAction.RETURN_HOME


@pytest.mark.unit
def test_restricted_zone_triggers_return_home() -> None:
    action, reason = determine_failsafe(make_frame(x_m=120, y_m=0), Settings())

    assert action == SafeCommandAction.RETURN_HOME
    assert "restricted" in reason


@pytest.mark.unit
def test_degraded_link_triggers_return_home() -> None:
    action, _ = determine_failsafe(make_frame(link_quality_pct=29), Settings())

    assert action == SafeCommandAction.RETURN_HOME


@pytest.mark.unit
def test_low_sensor_confidence_triggers_hold() -> None:
    action, _ = determine_failsafe(make_frame(sensor_confidence=0.39), Settings())

    assert action == SafeCommandAction.HOLD


@pytest.mark.unit
def test_nominal_frame_has_no_failsafe() -> None:
    action, reason = determine_failsafe(make_frame(), Settings())

    assert action is None
    assert "inside" in reason
