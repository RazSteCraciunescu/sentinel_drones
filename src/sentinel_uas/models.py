from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated, ClassVar

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

Identifier = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=3, max_length=64, pattern=r"^[A-Z0-9-]+$"),
]


class StrictRequestModel(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")


class Role(StrEnum):
    OBSERVER = "observer"
    OPERATOR = "operator"
    AUDITOR = "auditor"
    MAINTAINER = "maintainer"


class MissionType(StrEnum):
    SEARCH_AND_RESCUE = "search_and_rescue"
    INFRASTRUCTURE_INSPECTION = "infrastructure_inspection"
    SUPPLY_DELIVERY = "supply_delivery"
    PERIMETER_OBSERVATION = "perimeter_observation"
    TRAINING = "training"


class DroneMode(StrEnum):
    STANDBY = "standby"
    ACTIVE = "active"
    HOLD = "hold"
    RETURN_HOME = "return_home"
    LANDED = "landed"
    MAINTENANCE = "maintenance"


class SafeCommandAction(StrEnum):
    HOLD = "hold"
    RETURN_HOME = "return_home"
    LAND = "land"


class Waypoint(StrictRequestModel):
    x_m: float = Field(ge=-10_000, le=10_000)
    y_m: float = Field(ge=-10_000, le=10_000)
    altitude_m: float = Field(ge=0, le=500)


class MissionRequest(StrictRequestModel):
    mission_id: Identifier
    drone_id: Identifier
    mission_type: MissionType
    waypoints: list[Waypoint] = Field(min_length=1, max_length=50)
    battery_pct: float = Field(ge=0, le=100)
    estimated_duration_min: float = Field(gt=0, le=240)
    reserve_battery_pct: float = Field(default=20, ge=0, le=100)
    link_quality_pct: float = Field(ge=0, le=100)


class MissionDecision(BaseModel):
    mission_id: str
    approved: bool
    reasons: list[str]
    required_controls: list[str]
    projected_battery_at_recovery_pct: float


class TelemetryFrame(StrictRequestModel):
    drone_id: Identifier
    sequence: int = Field(ge=0, le=2_147_483_647)
    sent_at: datetime
    x_m: float = Field(ge=-10_000, le=10_000)
    y_m: float = Field(ge=-10_000, le=10_000)
    altitude_m: float = Field(ge=0, le=500)
    battery_pct: float = Field(ge=0, le=100)
    link_quality_pct: float = Field(ge=0, le=100)
    sensor_confidence: float = Field(ge=0, le=1)
    mode: DroneMode

    @field_validator("sent_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("sent_at must include a timezone")
        return value


class TelemetryDecision(BaseModel):
    accepted: bool
    drone_id: str
    sequence: int
    failsafe_action: SafeCommandAction | None
    reason: str


class CommandRequest(StrictRequestModel):
    command_id: Identifier
    drone_id: Identifier
    action: SafeCommandAction
    issued_at: datetime
    ttl_seconds: int = Field(ge=1, le=30)
    reason: str = Field(min_length=5, max_length=200)

    @field_validator("issued_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("issued_at must include a timezone")
        return value


class CommandDecision(BaseModel):
    accepted: bool
    command_id: str
    drone_id: str
    resulting_mode: DroneMode
    reason: str


class DroneSnapshot(BaseModel):
    drone_id: str
    call_sign: str
    mode: DroneMode
    battery_pct: float
    link_quality_pct: float
    x_m: float
    y_m: float
    altitude_m: float
    last_sequence: int | None = None
    last_seen: datetime | None = None


class AuditEvent(BaseModel):
    event_id: str
    occurred_at: datetime
    actor_role: Role
    action: str
    object_id: str
    decision: str
    reason: str
    previous_hash: str
    event_hash: str


class AssuranceMetrics(BaseModel):
    drones_total: int
    drones_active: int
    audit_events: int
    audit_chain_valid: bool
    rejected_missions: int
    rejected_commands: int
    rejected_telemetry_frames: int


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str
    simulation_only: bool = True
