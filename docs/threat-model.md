# Threat Model

## Scope and method

This threat model covers the local API, dashboard, test clients, in-memory state, audit evidence, source repository, dependencies, and CI workflow. It uses STRIDE as a discussion structure and a simple impact-likelihood-detectability risk score in `qa/risk-register.csv`.

It deliberately excludes real aircraft, radios, navigation services, payloads, operational command networks, and any procedure for attacking or disrupting them.

## Assets

- Integrity of mission decisions.
- Integrity and freshness of telemetry state.
- Authenticity and freshness of safe commands.
- Separation of observer, operator, auditor, and maintainer privileges.
- Integrity and availability of audit evidence.
- Correct safety configuration and test evidence.
- Source, dependency, and CI integrity.
- The explicit simulation-only boundary.

## Trust boundaries and entry points

| Boundary | Entry points | Main concerns |
| --- | --- | --- |
| Client to API | Headers, JSON bodies, paths | Spoofing, malformed input, replay, resource exhaustion |
| Role to function | Protected endpoints | Broken function-level authorization |
| API to state | Validated domain objects | Incorrect transition, duplicate processing, race condition |
| State to audit | Event construction and append | Missing evidence, modification, loss |
| Repository to build | Pull requests, dependencies, actions | Malicious change, vulnerable package, workflow privilege |
| Browser to API | Token input and local responses | Accidental credential exposure, UI-only access assumptions |

## STRIDE analysis

| ID | Category | Threat scenario | Existing controls | Residual concern | Verification |
| --- | --- | --- | --- | --- | --- |
| TM-01 | Spoofing | A caller presents a guessed or disclosed local token | Constant-time comparison, four distinct role tokens, environment override | Static bearer tokens are unsuitable for deployment | Authentication negative tests |
| TM-02 | Tampering | A replayed telemetry frame overwrites a newer state | Per-aircraft monotonic sequence and freshness windows | No cryptographic origin authentication | Replay and out-of-order tests |
| TM-03 | Tampering | A duplicate command is processed twice | Claimed command-ID set and TTL | In-memory idempotency is lost after restart | Duplicate-command tests and open risk |
| TM-04 | Repudiation | A decision is made without attributable evidence | Actor role, action, object, decision, reason, timestamp, hash linkage | No named identity, signature, durable remote store, or trusted time source | Audit event and chain tests |
| TM-05 | Information disclosure | An observer reads audit reasons or privileged operations | Endpoint-specific RBAC | Tokens may appear in local browser storage or terminal history | Authorization matrix tests; local-only guidance |
| TM-06 | Denial of service | Very large or rapid requests consume resources | Schema size/range limits, bounded waypoint count | No application rate limit; single process | Input-limit tests and load profile |
| TM-07 | Elevation of privilege | An observer invokes operator or reset functions | Server-side role dependencies on every endpoint | No external identity lifecycle or MFA | Parameterized authorization tests |
| TM-08 | Tampering | Safety configuration is changed without review | Environment-based settings, boundary regressions, documented defaults | No signed configuration or four-eyes approval | Config review and boundary suite |
| TM-09 | Supply chain | A compromised package or workflow changes behavior | Dependabot, `pip-audit`, Bandit, CodeQL, review | No release signing, SBOM attestation, or hermetic build | CI security workflow |
| TM-10 | Boundary erosion | A future contributor adds operational command or protocol logic | ADR, README boundary, contract test for exact command enum, contribution policy | Human review is still necessary | Contract test and PR checklist |

## Abuse cases

### AC-01: Reuse an old telemetry frame

**Goal:** Cause the service to accept superseded state.

**Control expectation:** Reject the frame with HTTP 409 when its sequence is not greater than the last accepted value. A rejected frame must not alter aircraft state, and the rejection counter must increase.

### AC-02: Reuse a command identifier

**Goal:** Cause a safety command to be processed more than once.

**Control expectation:** Accept the first fresh command, reject the duplicate with HTTP 409, preserve the first resulting state, and increase the rejection counter.

### AC-03: Invoke a privileged endpoint with a lower role

**Goal:** Read audit evidence, submit an operator action, or reset state without the required role.

**Control expectation:** Return HTTP 403 after successful authentication. Missing or invalid authentication returns HTTP 401. The dashboard must not be treated as an authorization control.

### AC-04: Hide a hazard in malformed or extreme data

**Goal:** Bypass domain logic using invalid percentages, coordinates, timestamps, identifiers, or oversized collections.

**Control expectation:** Schema validation returns HTTP 422 before state mutation. Domain-boundary inputs still reach explicit safety checks.

### AC-05: Modify recorded evidence

**Goal:** Change a historical decision while retaining a valid-looking log.

**Control expectation:** Recomputing the chain identifies a mismatch. The documentation must not imply that a process-local hash chain prevents a privileged attacker from rewriting the whole store.

## Security requirements derived from the model

- Authenticate every endpoint except health and the static dashboard shell.
- Authorize by operation, not merely by possession of any token.
- Use bounded schemas and timezone-aware timestamps.
- Reject stale, future-skewed, duplicate, and out-of-order state-changing input.
- Keep the allowed command vocabulary closed and contract-tested.
- Record safety-relevant decisions with reason and integrity linkage.
- Run source, dependency, and workflow checks in CI.
- Preserve the simulation-only scope in code review and architecture decisions.

## NIST CSF 2.0 view

| Function | Lab examples |
| --- | --- |
| Govern | Scope boundary, risk register, FMEA, ADRs, contribution policy |
| Identify | Assets, trust boundaries, requirements, threat scenarios |
| Protect | RBAC, validation, freshness windows, bounded commands, hardened container |
| Detect | Replay rejection, audit verification, security scans, counters |
| Respond | Deterministic safe-state decisions, defect process, security reporting |
| Recover | Lab reset, reproducible test data, clean-environment rebuild |

## Review triggers

Review this model when an endpoint, role, data source, persistent store, external service, authentication mechanism, deployment target, or command type changes. A change that adds real UAS integration requires a separate project, governance path, legal review, hazard analysis, and security assessment; it is not a normal extension of this lab.
