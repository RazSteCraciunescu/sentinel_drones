from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from threading import RLock
from uuid import uuid4

from sentinel_uas.models import AuditEvent, DroneMode, DroneSnapshot, Role

GENESIS_HASH = "0" * 64


@dataclass(frozen=True)
class AuditDraft:
    actor_role: Role
    action: str
    object_id: str
    decision: str
    reason: str


class AuditLog:
    """Small append-only hash chain for test evidence.

    This makes accidental or unsophisticated modification visible. It is not a replacement for
    signed remote logging or write-once storage.
    """

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []
        self._lock = RLock()

    @staticmethod
    def _digest(payload: dict[str, str]) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()

    def append(self, draft: AuditDraft) -> AuditEvent:
        with self._lock:
            previous_hash = self._events[-1].event_hash if self._events else GENESIS_HASH
            event_id = f"EVT-{uuid4().hex[:12].upper()}"
            occurred_at = datetime.now(UTC)
            payload = {
                "event_id": event_id,
                "occurred_at": occurred_at.isoformat(),
                "actor_role": draft.actor_role.value,
                "action": draft.action,
                "object_id": draft.object_id,
                "decision": draft.decision,
                "reason": draft.reason,
                "previous_hash": previous_hash,
            }
            event = AuditEvent(**payload, event_hash=self._digest(payload))
            self._events.append(event)
            return event

    def list(self) -> list[AuditEvent]:
        with self._lock:
            return list(self._events)

    def verify(self) -> bool:
        with self._lock:
            expected_previous = GENESIS_HASH
            for event in self._events:
                if event.previous_hash != expected_previous:
                    return False
                payload = {
                    "event_id": event.event_id,
                    "occurred_at": event.occurred_at.isoformat(),
                    "actor_role": event.actor_role.value,
                    "action": event.action,
                    "object_id": event.object_id,
                    "decision": event.decision,
                    "reason": event.reason,
                    "previous_hash": event.previous_hash,
                }
                if self._digest(payload) != event.event_hash:
                    return False
                expected_previous = event.event_hash
            return True


class LabState:
    def __init__(self) -> None:
        self._lock = RLock()
        self.audit = AuditLog()
        self.drones: dict[str, DroneSnapshot] = {}
        self.command_ids: set[str] = set()
        self.rejected_missions = 0
        self.rejected_commands = 0
        self.rejected_telemetry_frames = 0
        self.reset()

    def reset(self) -> None:
        with self._lock:
            self.drones = {
                "UAS-001": DroneSnapshot(
                    drone_id="UAS-001",
                    call_sign="ALPHA-ONE",
                    mode=DroneMode.STANDBY,
                    battery_pct=86,
                    link_quality_pct=94,
                    x_m=0,
                    y_m=0,
                    altitude_m=0,
                ),
                "UAS-002": DroneSnapshot(
                    drone_id="UAS-002",
                    call_sign="BRAVO-TWO",
                    mode=DroneMode.MAINTENANCE,
                    battery_pct=48,
                    link_quality_pct=0,
                    x_m=0,
                    y_m=0,
                    altitude_m=0,
                ),
                "UAS-003": DroneSnapshot(
                    drone_id="UAS-003",
                    call_sign="CHARLIE-THREE",
                    mode=DroneMode.STANDBY,
                    battery_pct=73,
                    link_quality_pct=88,
                    x_m=-25,
                    y_m=15,
                    altitude_m=0,
                ),
            }
            self.command_ids = set()
            self.rejected_missions = 0
            self.rejected_commands = 0
            self.rejected_telemetry_frames = 0
            self.audit = AuditLog()

    def get_drone(self, drone_id: str) -> DroneSnapshot | None:
        with self._lock:
            return self.drones.get(drone_id)

    def list_drones(self) -> list[DroneSnapshot]:
        with self._lock:
            return sorted(self.drones.values(), key=lambda item: item.drone_id)

    def update_drone(self, drone_id: str, **changes: object) -> DroneSnapshot:
        with self._lock:
            current = self.drones[drone_id]
            updated = current.model_copy(update=changes)
            self.drones[drone_id] = updated
            return updated

    def claim_command_id(self, command_id: str) -> bool:
        with self._lock:
            if command_id in self.command_ids:
                return False
            self.command_ids.add(command_id)
            return True
