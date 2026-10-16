import pytest

from sentinel_uas.models import Role
from sentinel_uas.store import AuditDraft, AuditLog, GENESIS_HASH, LabState


@pytest.mark.unit
def test_first_audit_event_points_to_genesis_hash() -> None:
    log = AuditLog()

    event = log.append(
        AuditDraft(
            actor_role=Role.OPERATOR,
            action="mission.validate",
            object_id="MSN-001",
            decision="approved",
            reason="test",
        )
    )

    assert event.previous_hash == GENESIS_HASH
    assert log.verify() is True


@pytest.mark.unit
def test_audit_events_form_a_hash_chain() -> None:
    log = AuditLog()
    first = log.append(AuditDraft(Role.OPERATOR, "one", "OBJ-1", "accepted", "first"))
    second = log.append(AuditDraft(Role.AUDITOR, "two", "OBJ-2", "observed", "second"))

    assert second.previous_hash == first.event_hash
    assert log.verify() is True


@pytest.mark.unit
def test_list_returns_a_copy() -> None:
    log = AuditLog()
    log.append(AuditDraft(Role.OPERATOR, "one", "OBJ-1", "accepted", "first"))

    external = log.list()
    external.clear()

    assert len(log.list()) == 1


@pytest.mark.unit
def test_lab_reset_restores_seed_state() -> None:
    state = LabState()
    assert state.claim_command_id("CMD-001") is True
    assert state.claim_command_id("CMD-001") is False

    state.reset()

    assert len(state.list_drones()) == 3
    assert state.claim_command_id("CMD-001") is True


@pytest.mark.unit
def test_audit_verifier_detects_previous_hash_tampering() -> None:
    log = AuditLog()
    log.append(AuditDraft(Role.OPERATOR, "one", "OBJ-1", "accepted", "first"))
    log._events[0] = log._events[0].model_copy(update={"previous_hash": "f" * 64})

    assert log.verify() is False


@pytest.mark.unit
def test_audit_verifier_detects_event_content_tampering() -> None:
    log = AuditLog()
    log.append(AuditDraft(Role.OPERATOR, "one", "OBJ-1", "accepted", "first"))
    log._events[0] = log._events[0].model_copy(update={"reason": "changed"})

    assert log.verify() is False
