from datetime import UTC, datetime

import pytest

from sentinel_uas.config import Settings
from sentinel_uas.models import SafeCommandAction, TelemetryFrame
from sentinel_uas.safety import determine_failsafe

try:
    from hypothesis import given, strategies as st
except ImportError:
    pytest.skip("hypothesis is not installed", allow_module_level=True)


@st.composite
def nominal_frames(draw: st.DrawFn) -> TelemetryFrame:
    return TelemetryFrame(
        drone_id="UAS-001",
        sequence=draw(st.integers(min_value=0, max_value=2_000_000)),
        sent_at=datetime.now(UTC),
        x_m=draw(st.floats(min_value=-499, max_value=99, allow_nan=False, allow_infinity=False)),
        y_m=draw(st.floats(min_value=-499, max_value=499, allow_nan=False, allow_infinity=False)),
        altitude_m=draw(
            st.floats(min_value=0, max_value=120, allow_nan=False, allow_infinity=False)
        ),
        battery_pct=draw(
            st.floats(min_value=12.01, max_value=100, allow_nan=False, allow_infinity=False)
        ),
        link_quality_pct=draw(
            st.floats(min_value=30, max_value=100, allow_nan=False, allow_infinity=False)
        ),
        sensor_confidence=draw(
            st.floats(min_value=0.4, max_value=1, allow_nan=False, allow_infinity=False)
        ),
        mode="active",
    )


@pytest.mark.property
@given(nominal_frames())
def test_nominal_envelope_never_requests_failsafe(frame: TelemetryFrame) -> None:
    action, _ = determine_failsafe(frame, Settings())

    assert action is None


@pytest.mark.property
@given(st.floats(min_value=0, max_value=12, allow_nan=False, allow_infinity=False))
def test_all_critical_battery_values_request_land(battery: float) -> None:
    frame = TelemetryFrame(
        drone_id="UAS-001",
        sequence=1,
        sent_at=datetime.now(UTC),
        x_m=0,
        y_m=0,
        altitude_m=20,
        battery_pct=battery,
        link_quality_pct=100,
        sensor_confidence=1,
        mode="active",
    )

    action, _ = determine_failsafe(frame, Settings())

    assert action == SafeCommandAction.LAND


@pytest.mark.property
@given(st.floats(min_value=500.01, max_value=10_000, allow_nan=False, allow_infinity=False))
def test_positive_x_geofence_breach_requests_return_home(x_m: float) -> None:
    frame = TelemetryFrame(
        drone_id="UAS-001",
        sequence=1,
        sent_at=datetime.now(UTC),
        x_m=x_m,
        y_m=0,
        altitude_m=20,
        battery_pct=80,
        link_quality_pct=100,
        sensor_confidence=1,
        mode="active",
    )

    action, _ = determine_failsafe(frame, Settings())

    assert action == SafeCommandAction.RETURN_HOME
