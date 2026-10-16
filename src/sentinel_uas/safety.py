from __future__ import annotations

from sentinel_uas.config import Settings
from sentinel_uas.models import (
    DroneMode,
    MissionDecision,
    MissionRequest,
    SafeCommandAction,
    TelemetryFrame,
)
from sentinel_uas.store import LabState


def _inside_operating_geofence(x_m: float, y_m: float, settings: Settings) -> bool:
    return (
        settings.geofence_min_x_m <= x_m <= settings.geofence_max_x_m
        and settings.geofence_min_y_m <= y_m <= settings.geofence_max_y_m
    )


def _inside_restricted_zone(x_m: float, y_m: float, settings: Settings) -> bool:
    return (
        settings.restricted_min_x_m <= x_m <= settings.restricted_max_x_m
        and settings.restricted_min_y_m <= y_m <= settings.restricted_max_y_m
    )


def evaluate_mission(
    mission: MissionRequest,
    state: LabState,
    settings: Settings,
) -> MissionDecision:
    reasons: list[str] = []
    required_controls: list[str] = [
        "record operator approval",
        "preserve mission and telemetry audit evidence",
    ]

    drone = state.get_drone(mission.drone_id)
    if drone is None:
        reasons.append("drone is not registered in the simulated fleet")
    elif drone.mode == DroneMode.MAINTENANCE:
        reasons.append("drone is in maintenance mode")

    if mission.battery_pct < settings.min_launch_battery_pct:
        reasons.append(
            f"launch battery is below {settings.min_launch_battery_pct:.0f}% minimum"
        )

    if mission.link_quality_pct < settings.min_launch_link_quality_pct:
        reasons.append(
            f"launch link quality is below {settings.min_launch_link_quality_pct:.0f}% minimum"
        )

    for index, waypoint in enumerate(mission.waypoints, start=1):
        if waypoint.altitude_m > settings.max_altitude_m:
            reasons.append(
                f"waypoint {index} exceeds the {settings.max_altitude_m:.0f} m lab ceiling"
            )
        if not _inside_operating_geofence(waypoint.x_m, waypoint.y_m, settings):
            reasons.append(f"waypoint {index} is outside the simulated operating geofence")
        if _inside_restricted_zone(waypoint.x_m, waypoint.y_m, settings):
            reasons.append(f"waypoint {index} enters the simulated restricted zone")

    projected = mission.battery_pct - (
        mission.estimated_duration_min * settings.battery_use_per_minute_pct
    )
    if projected < mission.reserve_battery_pct:
        reasons.append(
            "projected recovery battery is below the requested reserve threshold"
        )

    if mission.mission_type.value == "supply_delivery":
        required_controls.append("verify payload mass and release interlock outside this lab")
    if len(mission.waypoints) > 10:
        required_controls.append("perform an independent route review")

    return MissionDecision(
        mission_id=mission.mission_id,
        approved=not reasons,
        reasons=reasons or ["all configured safety gates passed"],
        required_controls=required_controls,
        projected_battery_at_recovery_pct=round(max(projected, 0), 2),
    )


def determine_failsafe(
    telemetry: TelemetryFrame,
    settings: Settings,
) -> tuple[SafeCommandAction | None, str]:
    if telemetry.battery_pct <= settings.critical_battery_pct:
        return SafeCommandAction.LAND, "critical battery threshold reached"
    if not _inside_operating_geofence(telemetry.x_m, telemetry.y_m, settings):
        return SafeCommandAction.RETURN_HOME, "aircraft is outside the operating geofence"
    if _inside_restricted_zone(telemetry.x_m, telemetry.y_m, settings):
        return SafeCommandAction.RETURN_HOME, "aircraft entered the restricted zone"
    if telemetry.altitude_m > settings.max_altitude_m:
        return SafeCommandAction.RETURN_HOME, "aircraft exceeds the configured altitude ceiling"
    if telemetry.link_quality_pct < settings.degraded_link_quality_pct:
        return SafeCommandAction.RETURN_HOME, "command link quality is critically degraded"
    if telemetry.sensor_confidence < 0.4:
        return SafeCommandAction.HOLD, "sensor confidence is below the assurance threshold"
    return None, "telemetry remains inside the configured safety envelope"
