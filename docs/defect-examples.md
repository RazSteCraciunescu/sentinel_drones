# Sample Defect Records

These are example portfolio records based on plausible development findings. They are not claims about a deployed aircraft or third-party product.

## DEF-001 - Duplicate telemetry accepted after state reset

- **Status:** Accepted risk for lab scope
- **Severity:** S2 High
- **Priority:** P2
- **Area:** Telemetry integrity

**Precondition:** Sequence 40 for `UAS-001` was accepted, then the process or simulation state was reset.

**Steps:**

1. Submit a valid telemetry frame with sequence 40.
2. Reset the lab or restart the process.
3. Submit the same frame again.

**Expected:** A production design would retain enough anti-replay state to reject reused authenticated data across a restart.

**Actual:** The in-memory sequence state is reset, so the frame is accepted as new.

**Analysis:** This is a documented consequence of process-local state. It is unacceptable for an operational gateway but acceptable for the current isolated simulation.

**Recommended fix:** Durable per-device sequence or nonce state, authenticated messages, restart-safe idempotency, and a defined recovery procedure.

**Links:** R-02, ADR-0002.

---

## DEF-002 - Rejected unknown-aircraft telemetry lacks a detailed audit event

- **Status:** Backlog
- **Severity:** S3 Medium
- **Priority:** P3
- **Area:** Audit evidence

**Steps:**

1. Submit an otherwise valid frame for `UAS-999` with an operator token.
2. Read assurance metrics.
3. Read audit events with an auditor token.

**Expected:** The rejection counter increases and an audit event records the attempted object ID and reason.

**Actual:** The counter increases and HTTP 404 is returned, but no audit event is appended.

**Impact:** Aggregate evidence shows that a rejection occurred, but a reviewer cannot reconstruct the individual attempt.

**Recommended fix:** Add a centralized, redaction-aware rejection event after authentication and before raising domain HTTP errors. Confirm that logging malformed input cannot create a resource-exhaustion path or expose sensitive content.

---

## DEF-003 - Dashboard token remains in memory after switching role

- **Status:** Closed in example release notes
- **Severity:** S4 Low
- **Priority:** P3
- **Area:** Dashboard usability

**Steps:**

1. Enter the maintainer token and load the dashboard.
2. Replace the token text with an observer token.
3. Trigger a request before explicitly saving or reloading.

**Expected:** The visible token and request token are clearly synchronized.

**Actual:** An earlier prototype used the previously stored value for one request, causing confusing authorization results.

**Resolution:** Use one in-memory token source, update it before every request, and add a Playwright role-switch check.

---

## DEF-004 - Mission rejection reasons change order after refactor

- **Status:** Won't fix unless an external contract is introduced
- **Severity:** S4 Low
- **Priority:** P4
- **Area:** Contract semantics

**Observation:** A mission violating battery, link, altitude, and geofence gates may return all reasons in implementation order. A refactor can reorder the array without changing the decision.

**Decision:** Tests assert required reason content rather than the complete list order. If a client later treats order as priority, the API contract must define and version that behavior.
