from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from sentinel_uas.auth import Principal, require_roles
from sentinel_uas.config import Settings
from sentinel_uas.models import (
    AssuranceMetrics,
    AuditEvent,
    CommandDecision,
    CommandRequest,
    DroneMode,
    DroneSnapshot,
    HealthResponse,
    MissionDecision,
    MissionRequest,
    Role,
    SafeCommandAction,
    TelemetryDecision,
    TelemetryFrame,
)
from sentinel_uas.safety import determine_failsafe, evaluate_mission
from sentinel_uas.store import AuditDraft, LabState

PACKAGE_DIR = Path(__file__).resolve().parent
STATIC_DIR = PACKAGE_DIR / "static"


def _now() -> datetime:
    return datetime.now(UTC)


def create_app(settings: Settings | None = None) -> FastAPI:
    runtime_settings = settings or Settings()
    app = FastAPI(
        title=runtime_settings.app_name,
        version="0.1.0",
        description=(
            "Synthetic API for QA, safety, and cyber-resilience exercises. "
            "It does not connect to real aircraft or flight-control protocols."
        ),
        license_info={"name": "Apache-2.0"},
    )
    app.state.settings = runtime_settings
    app.state.lab = LabState()
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    observer_roles = (Role.OBSERVER, Role.OPERATOR, Role.AUDITOR, Role.MAINTAINER)
    operator_roles = (Role.OPERATOR, Role.MAINTAINER)
    auditor_roles = (Role.AUDITOR, Role.MAINTAINER)

    @app.get("/", include_in_schema=False)
    async def dashboard() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/health", response_model=HealthResponse, tags=["platform"])
    async def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            service=runtime_settings.app_name,
            environment=runtime_settings.environment,
        )

    @app.get("/api/v1/fleet", response_model=list[DroneSnapshot], tags=["fleet"])
    async def fleet(
        _principal: Principal = Depends(require_roles(*observer_roles)),
    ) -> list[DroneSnapshot]:
        state: LabState = app.state.lab
        return state.list_drones()

    @app.post(
        "/api/v1/missions/validate",
        response_model=MissionDecision,
        tags=["assurance"],
    )
    async def validate_mission(
        mission: MissionRequest,
        principal: Principal = Depends(require_roles(*operator_roles)),
    ) -> MissionDecision:
        state: LabState = app.state.lab
        decision = evaluate_mission(mission, state, runtime_settings)
        if not decision.approved:
            state.rejected_missions += 1
        state.audit.append(
            AuditDraft(
                actor_role=principal.role,
                action="mission.validate",
                object_id=mission.mission_id,
                decision="approved" if decision.approved else "rejected",
                reason="; ".join(decision.reasons),
            )
        )
        return decision

    @app.post(
        "/api/v1/telemetry",
        response_model=TelemetryDecision,
        status_code=status.HTTP_202_ACCEPTED,
        tags=["telemetry"],
    )
    async def ingest_telemetry(
        frame: TelemetryFrame,
        principal: Principal = Depends(require_roles(*operator_roles)),
    ) -> TelemetryDecision:
        state: LabState = app.state.lab
        drone = state.get_drone(frame.drone_id)
        if drone is None:
            state.rejected_telemetry_frames += 1
            raise HTTPException(status_code=404, detail="Unknown drone_id")

        age_seconds = (_now() - frame.sent_at).total_seconds()
        if age_seconds > runtime_settings.max_telemetry_age_seconds:
            state.rejected_telemetry_frames += 1
            raise HTTPException(status_code=409, detail="Telemetry frame is stale")
        if age_seconds < -runtime_settings.max_clock_skew_seconds:
            state.rejected_telemetry_frames += 1
            raise HTTPException(status_code=409, detail="Telemetry frame is too far in the future")
        if drone.last_sequence is not None and frame.sequence <= drone.last_sequence:
            state.rejected_telemetry_frames += 1
            raise HTTPException(status_code=409, detail="Replay or out-of-order telemetry detected")

        failsafe_action, reason = determine_failsafe(frame, runtime_settings)
        resulting_mode = frame.mode
        if failsafe_action == SafeCommandAction.LAND:
            resulting_mode = DroneMode.LANDED
        elif failsafe_action == SafeCommandAction.RETURN_HOME:
            resulting_mode = DroneMode.RETURN_HOME
        elif failsafe_action == SafeCommandAction.HOLD:
            resulting_mode = DroneMode.HOLD

        state.update_drone(
            frame.drone_id,
            mode=resulting_mode,
            battery_pct=frame.battery_pct,
            link_quality_pct=frame.link_quality_pct,
            x_m=frame.x_m,
            y_m=frame.y_m,
            altitude_m=frame.altitude_m,
            last_sequence=frame.sequence,
            last_seen=_now(),
        )
        state.audit.append(
            AuditDraft(
                actor_role=principal.role,
                action="telemetry.ingest",
                object_id=f"{frame.drone_id}:{frame.sequence}",
                decision="failsafe" if failsafe_action else "accepted",
                reason=reason,
            )
        )
        return TelemetryDecision(
            accepted=True,
            drone_id=frame.drone_id,
            sequence=frame.sequence,
            failsafe_action=failsafe_action,
            reason=reason,
        )

    @app.post(
        "/api/v1/commands/safe",
        response_model=CommandDecision,
        status_code=status.HTTP_202_ACCEPTED,
        tags=["commands"],
    )
    async def submit_safe_command(
        command: CommandRequest,
        principal: Principal = Depends(require_roles(*operator_roles)),
    ) -> CommandDecision:
        state: LabState = app.state.lab
        drone = state.get_drone(command.drone_id)
        if drone is None:
            state.rejected_commands += 1
            raise HTTPException(status_code=404, detail="Unknown drone_id")

        age_seconds = (_now() - command.issued_at).total_seconds()
        if age_seconds < -runtime_settings.max_clock_skew_seconds:
            state.rejected_commands += 1
            raise HTTPException(
                status_code=409,
                detail="Command timestamp is too far in the future",
            )
        if age_seconds > command.ttl_seconds:
            state.rejected_commands += 1
            raise HTTPException(status_code=409, detail="Command has expired")
        if command.ttl_seconds > runtime_settings.max_command_ttl_seconds:
            state.rejected_commands += 1
            raise HTTPException(status_code=422, detail="Command TTL exceeds the lab maximum")
        if not state.claim_command_id(command.command_id):
            state.rejected_commands += 1
            raise HTTPException(status_code=409, detail="Duplicate command_id rejected")

        mode_by_action = {
            SafeCommandAction.HOLD: DroneMode.HOLD,
            SafeCommandAction.RETURN_HOME: DroneMode.RETURN_HOME,
            SafeCommandAction.LAND: DroneMode.LANDED,
        }
        resulting_mode = mode_by_action[command.action]
        state.update_drone(command.drone_id, mode=resulting_mode)
        state.audit.append(
            AuditDraft(
                actor_role=principal.role,
                action=f"command.{command.action.value}",
                object_id=command.command_id,
                decision="accepted",
                reason=command.reason,
            )
        )
        return CommandDecision(
            accepted=True,
            command_id=command.command_id,
            drone_id=command.drone_id,
            resulting_mode=resulting_mode,
            reason="safe command accepted by the simulation gateway",
        )

    @app.get(
        "/api/v1/audit/events",
        response_model=list[AuditEvent],
        tags=["audit"],
    )
    async def audit_events(
        _principal: Principal = Depends(require_roles(*auditor_roles)),
    ) -> list[AuditEvent]:
        state: LabState = app.state.lab
        return state.audit.list()

    @app.get(
        "/api/v1/assurance/metrics",
        response_model=AssuranceMetrics,
        tags=["assurance"],
    )
    async def assurance_metrics(
        _principal: Principal = Depends(require_roles(*observer_roles)),
    ) -> AssuranceMetrics:
        state: LabState = app.state.lab
        drones = state.list_drones()
        active_modes = {DroneMode.ACTIVE, DroneMode.HOLD, DroneMode.RETURN_HOME}
        return AssuranceMetrics(
            drones_total=len(drones),
            drones_active=sum(drone.mode in active_modes for drone in drones),
            audit_events=len(state.audit.list()),
            audit_chain_valid=state.audit.verify(),
            rejected_missions=state.rejected_missions,
            rejected_commands=state.rejected_commands,
            rejected_telemetry_frames=state.rejected_telemetry_frames,
        )

    @app.post("/api/v1/simulation/reset", status_code=204, tags=["platform"])
    async def reset_simulation(
        _principal: Principal = Depends(require_roles(Role.MAINTAINER)),
    ) -> None:
        state: LabState = app.state.lab
        state.reset()

    return app


app = create_app()
