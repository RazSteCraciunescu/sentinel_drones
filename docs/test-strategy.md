# Test Strategy

## Objective

Provide repeatable evidence that the simulation service enforces its stated safety and security invariants, rejects malformed or unauthorized requests, behaves predictably during degraded conditions, and remains traceable from requirement to test evidence.

This is a risk-based software assurance strategy. It is not a flight-test plan and does not qualify hardware, radio links, navigation performance, or real-world operations.

## Quality risks driving the strategy

The highest-impact lab risks are:

- approving a mission outside the configured safety envelope;
- using stale, future-dated, replayed, or out-of-order state data;
- allowing an unauthorized role to perform a protected operation;
- accepting an expired or duplicate command;
- selecting an inconsistent fail-safe when hazards overlap;
- losing confidence in audit evidence or traceability;
- introducing vulnerable dependencies or unsafe build changes.

The detailed scores and ownership are in `qa/risk-register.csv`. Failure modes and detection controls are in `qa/fmea.csv`.

## Scope

### In scope

- REST API behavior and OpenAPI contract;
- mission boundary decisions;
- telemetry freshness, ordering, and range checks;
- deterministic fail-safe selection;
- role-based endpoint access;
- command freshness and idempotency;
- audit-chain integrity;
- seeded fleet state and reset behavior;
- dashboard smoke behavior;
- repository data quality and traceability;
- static analysis, dependency audit, and CI evidence;
- local performance smoke profiles.

### Out of scope

- aircraft dynamics, propulsion, battery chemistry, payload behavior, or airworthiness;
- radio-frequency testing, signal interference, or communication-protocol exploitation;
- real coordinates, restricted-area data, operators, credentials, or mission data;
- autonomous target recognition or weapon functions;
- certification or regulatory approval.

## Test levels

| Level | Purpose | Primary evidence |
| --- | --- | --- |
| Unit | Isolate safety decisions and audit-chain behavior | `tests/unit/` |
| API | Verify status codes, payloads, state changes, and negative paths | `tests/api/` |
| Contract | Detect accidental interface or safe-command expansion | `tests/contract/` |
| Security | Exercise authentication, role separation, replay, freshness, and hostile inputs | `tests/security/` |
| Resilience | Verify degraded-link, battery, geofence, restricted-zone, and multi-hazard behavior | `tests/resilience/` |
| Property | Generate broad ranges around telemetry invariants | `tests/property/` |
| Browser | Confirm the dashboard can display fleet and assurance information | `tests/e2e/` |
| Performance smoke | Establish a repeatable local workload and alert on obvious regressions | `performance/` |
| Static and supply-chain | Lint, type-check, scan source, and audit dependencies | GitHub Actions and local runners |

## Test design techniques

- **Equivalence partitioning:** valid and invalid percentages, known and unknown aircraft, supported and unsupported roles.
- **Boundary-value analysis:** altitude ceiling, geofence edges, restricted-zone edges, TTL, timestamp windows, sequence values, list size, and text length.
- **Decision tables:** role versus endpoint; overlapping telemetry hazards versus expected fail-safe.
- **State transition testing:** standby, hold, return-home, landed, and maintenance behavior.
- **Error guessing:** missing token, wrong token, duplicate ID, naive timestamp, extra fields, malformed JSON, and oversized input.
- **Property-based testing:** ranges of battery, link quality, coordinates, and confidence against stable invariants.
- **Exploratory testing:** charters in `docs/exploratory-charters.md` target ambiguity, recovery, observability, and misuse resistance.

## Safety invariants

The release candidate must preserve these invariants:

1. A waypoint outside the configured geofence cannot receive an approved mission decision.
2. A waypoint above the configured altitude ceiling cannot receive an approved mission decision.
3. A waypoint inside the configured restricted zone cannot receive an approved mission decision.
4. Launch link quality below the configured minimum cannot receive an approved mission decision.
5. Telemetry above the configured altitude ceiling selects `return_home`.
6. A known aircraft in maintenance cannot receive an approved mission decision.
7. A duplicate or older telemetry sequence cannot update state.
8. A stale or excessively future-dated frame cannot update state.
9. A critical battery decision has priority over lower-severity telemetry conditions.
10. Only `hold`, `return_home`, and `land` exist in the command contract.
11. A command ID cannot be accepted twice in one lab state.
12. Role checks occur server-side for every protected operation.
13. Audit-chain verification fails when a stored event is modified without recomputing the chain.
14. Every active requirement has at least one traceability link.

## Test data

All included data is synthetic. Identifiers use the `UAS-###`, `MSN-###`, and `CMD-###` patterns. Coordinates are Cartesian metres in a fictional square from -500 to 500. The restricted rectangle is fictional. No dataset should contain real facilities, units, operations, frequencies, credentials, or personal data.

Reusable samples are in `test-data/`. Unit and API tests create fresh timestamps at runtime to avoid brittle fixtures.

## Environments

| Environment | Purpose | Notes |
| --- | --- | --- |
| Local Python | Fast feedback for unit, API, security, and resilience tests | In-memory state resets per test fixture |
| Local browser | Dashboard smoke and interaction checks | Playwright starts the API automatically |
| Docker Compose | Container behavior and local deployment demonstration | Read-only filesystem, dropped capabilities |
| GitHub Actions | Independent quality and security gates | Python 3.12; Chromium browser job |

## Entry criteria

A change is ready for verification when:

- behavior and risk are understood;
- affected requirement and acceptance criteria are identified;
- synthetic test data is available;
- safety boundaries remain explicit;
- the service installs in a clean supported environment.

## Exit criteria

A change is releasable to the portfolio branch when:

- all P1 tests pass;
- the automated suite passes with at least 85% branch-aware coverage;
- no active requirement lacks traceability;
- repository validators pass;
- no unresolved critical or high-severity security finding remains;
- risk and FMEA records are updated when behavior changes;
- limitations and residual risk are documented.

## Defect severity

| Severity | Definition | Example |
| --- | --- | --- |
| S1 Critical | A safety/security invariant is bypassed or evidence is materially untrustworthy | Mission outside geofence approved; authorization bypass |
| S2 High | Major control fails with a viable workaround or a recovery decision is wrong | Duplicate telemetry updates state under common conditions |
| S3 Medium | Incorrect behavior with limited consequence in the lab | Counter not updated; unclear rejection reason |
| S4 Low | Cosmetic, documentation, or minor usability defect | Dashboard alignment issue |

Priority is set separately and considers exposure, likelihood, test-blocking impact, and portfolio value.

## Metrics

The project tracks:

- pass/fail/skip counts by test layer;
- branch-aware code coverage;
- requirements with automated evidence;
- open risks by score and status;
- rejected mission, command, and telemetry counters;
- audit-chain validity;
- performance error rate and latency percentiles when a load profile is run;
- age of unresolved S1/S2 defects.

Metrics support decisions; they do not replace review of failed scenarios and residual risk.

## Regression cadence

- Every pull request: repository validation, traceability, lint, type check, full pytest suite, browser smoke, Bandit, dependency audit, and CodeQL.
- Weekly: scheduled security workflow and dependency update review.
- Before a tagged portfolio release: clean-environment install, Docker run, Postman smoke, exploratory charter, risk review, and evidence summary.
