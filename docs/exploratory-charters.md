# Exploratory Test Charters

Use a 45-minute session unless the charter says otherwise. Capture setup, notes, requests, responses, observations, defects, questions, and remaining risk. Keep all data synthetic.

## EX-01 - Mission boundary ambiguity

**Mission:** Explore how the service behaves exactly on, just inside, and just outside altitude, geofence, and restricted-zone boundaries.

**Focus:** Floating-point values, inclusive versus exclusive edges, multiple invalid waypoints, reason ordering, projected battery value, and whether a rejected mission leaves correct audit evidence.

**Useful data:** `x_m` values 499.999, 500, 500.001; restricted-zone corners; altitude values 119.999, 120, 120.001.

**Exit:** The boundary policy is unambiguous, repeatable, and consistent with requirements and automated tests.

## EX-02 - Freshness and time handling

**Mission:** Explore telemetry and command behavior around accepted age, expiry, timezone offsets, leap-day dates, future skew, and rapidly repeated requests.

**Focus:** UTC versus positive/negative offsets, naive timestamps, exact threshold seconds, processing delay, and useful error messages.

**Do not:** Change the machine clock on a shared or managed computer. Generate timestamps in the request instead.

## EX-03 - Role separation

**Mission:** Attempt every protected operation with every lab role and no token.

**Focus:** 401 versus 403 consistency, response detail, OpenAPI security declaration, dashboard behavior after changing tokens, and whether any privileged data appears before authorization.

**Oracle:** The matrix in `docs/architecture.md`.

## EX-04 - Recovery decision consistency

**Mission:** Combine two or more degraded conditions and look for inconsistent or surprising fail-safe selection.

**Focus:** Critical battery plus geofence breach, low confidence plus degraded link, restricted-zone entry plus critical battery, and result after repeated frames.

**Oracle:** The documented priority in `docs/architecture.md`. Record any case where the desired policy is unclear even when the implementation is consistent.

## EX-05 - Evidence quality

**Mission:** Determine whether a reviewer can reconstruct what happened from metrics and audit events.

**Focus:** Rejected mission reason, accepted safe command, telemetry fail-safe, event order, object IDs, actor role, hash continuity, and reset behavior.

**Question:** Which rejected API paths create audit events and which only increment counters? Is that distinction justified?

## EX-06 - Input misuse resistance

**Mission:** Explore schema and parser behavior with malformed, oversized, oddly encoded, duplicate, or unexpected fields.

**Focus:** Empty arrays, 51 waypoints, long reasons, lower-case identifiers, non-finite numbers, wrong content type, invalid JSON, duplicate JSON properties, and extra object properties.

**Boundary:** Use only the local lab. The objective is defensive input assurance, not service disruption.

## EX-07 - Dashboard under degraded service

**Mission:** Explore usability when the token is missing, invalid, underprivileged, or the API is temporarily unavailable.

**Focus:** Visible error state, stale data, retry behavior, accessibility, keyboard navigation, narrow screen, and accidental token persistence.

## EX-08 - Clean-machine reproducibility

**Mission:** Follow only the README on a clean environment and note every assumption.

**Focus:** Python and Node versions, virtual environment commands, line endings, Windows paths, browser installation, Docker behavior, and generated report locations.

**Exit:** A reviewer unfamiliar with the project can reach a passing core suite and running dashboard without undocumented steps.

## Session note template

```text
Charter:
Date / tester:
Build / commit:
Environment:
Timebox:

Setup and data:

Coverage notes:

Observations and questions:

Defects / issue links:

Risks not resolved:

Follow-up:
```
