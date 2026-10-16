# Sentinel UAS Assurance Lab

A simulation-only portfolio project for testing the software around high-consequence unmanned aircraft systems (UAS): mission validation, telemetry integrity, command freshness, fail-safe behavior, access control, audit evidence, and CI security checks.

The lab is intentionally separated from real aircraft, radios, autopilots, weapon systems, and operational networks. It uses synthetic coordinates and a small FastAPI service so the assurance work can be demonstrated safely and reproduced on an ordinary PC.

## Why this project exists

Drone software combines several QA domains that are often tested separately:

- safety-critical decisions under degraded conditions;
- API, contract, and data-quality testing;
- cybersecurity controls around commands and telemetry;
- deterministic recovery behavior;
- evidence, traceability, and risk management;
- CI/CD and software-supply-chain checks.

The scenario is relevant to public safety, infrastructure inspection, logistics, border monitoring, emergency response, and defense-adjacent assurance. The implementation remains non-operational: the only accepted commands are `hold`, `return_home`, and `land`.

## Demonstrated skills

| Area | Evidence in this repository |
| --- | --- |
| Risk-based QA | Risk register, FMEA, severity/likelihood scoring, quality gate |
| Safety testing | Battery reserve, altitude ceiling, geofence, restricted-zone, fail-safe priority |
| API testing | FastAPI service, pytest, Postman collection, OpenAPI checks |
| Cybersecurity testing | RBAC, token authentication, replay rejection, command TTL, input limits |
| Resilience testing | Link degradation, stale telemetry, clock skew, low sensor confidence |
| Property-based testing | Hypothesis boundary generation for safety invariants |
| Performance testing | k6 smoke profile and Locust workload |
| UI testing | Playwright checks for the local assurance dashboard |
| DevSecOps | GitHub Actions, Bandit, pip-audit, CodeQL, Dependabot |
| Test management | Requirements, traceability matrix, test cases, exploratory charters, defect examples |
| Aviation context | EASA/AACR context, SORA awareness, NIST CSF, OWASP API Security, DO-326A/ED-202A references |
| Containers | Dockerfile and Docker Compose local environment |
| Scripting | Python repository checks, telemetry generator, JUnit summarizer, PowerShell runner |

## What is implemented

The local API models a small fleet and exposes:

- `GET /health` - public liveness and simulation marker;
- `GET /api/v1/fleet` - role-protected fleet snapshot;
- `POST /api/v1/missions/validate` - pre-mission safety gate;
- `POST /api/v1/telemetry` - sequence, freshness, range, and fail-safe checks;
- `POST /api/v1/commands/safe` - short-lived, replay-protected safety commands;
- `GET /api/v1/audit/events` - role-protected hash-chained audit evidence;
- `GET /api/v1/assurance/metrics` - operational assurance counters;
- `POST /api/v1/simulation/reset` - maintainer-only lab reset.

The in-memory audit chain detects accidental or unsophisticated alteration. It is not presented as a replacement for signed remote logging or write-once evidence storage.

## Quick start on Windows 11

Open PowerShell in the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
pytest --cov=sentinel_uas --cov-report=term-missing
python -m uvicorn sentinel_uas.app:app --host 127.0.0.1 --port 8080
```

Open `http://127.0.0.1:8080` and use the local observer token:

```text
observer-local-token
```

Swagger UI is available at `http://127.0.0.1:8080/docs`.

The four default local tokens are intentionally obvious and must never be treated as production credentials:

| Role | Local token |
| --- | --- |
| Observer | `observer-local-token` |
| Operator | `operator-local-token` |
| Auditor | `auditor-local-token` |
| Maintainer | `maintainer-local-token` |

Copy `.env.example` to `.env` and replace them when experimenting with deployment settings.

## Common commands

```powershell
# Full Python suite and coverage gate
pytest --cov=sentinel_uas --cov-report=xml --cov-report=term-missing

# Only API tests
pytest -m api

# Security and abuse-case tests, including replay and freshness
pytest -m security

# Only degraded-condition tests
pytest -m resilience

# Validate repository data and traceability
python tools\validate_repository.py
python tools\check_traceability.py
python tools\risk_score.py

# Security checks
bandit -c pyproject.toml -r src
pip-audit

# Browser tests
npm install
npx playwright install chromium
npm run test:e2e
```

A one-command Windows runner is included:

```powershell
.\tools\run_checks.ps1
```

## Docker

```powershell
docker compose up --build
```

Then open `http://127.0.0.1:8080`.

## Repository map

```text
src/sentinel_uas/       FastAPI service and safety logic
tests/                  Unit, API, contract, security, resilience, and property tests
qa/                     Requirements, risks, FMEA, traceability, and test cases
docs/                   Architecture, strategy, threat model, safety case, labs, standards
postman/                 Collection and local environment
performance/             k6 and Locust workloads
tools/                   QA utilities and local runners
reports/sample/          Example execution and assessment summaries
.github/                 CI, security automation, templates, and Dependabot
```

## Assurance boundaries

This repository does **not** contain:

- flight-controller integration;
- MAVLink or vendor command sequences;
- radio-frequency procedures;
- target selection, payload actuation, or weapon logic;
- instructions for compromising, intercepting, or disrupting real systems;
- claims of regulatory certification.

It is a software QA lab, not an aircraft, counter-UAS, or weapons project.

## Suggested portfolio walkthrough

A useful demonstration takes about ten minutes:

1. Run the test suite and show the coverage gate.
2. Open the Swagger page and submit a safe mission.
3. Change one waypoint to `x_m: 501` and show the geofence rejection.
4. Submit the same telemetry sequence twice and show replay rejection.
5. Submit a low-link telemetry frame and show `return_home`.
6. Open the audit endpoint with the auditor role and explain the hash chain.
7. Open `qa/traceability.csv` and connect requirements to automated evidence.
8. Discuss the limitations in `docs/architecture.md` rather than overstating the prototype.

## Current limitations

- State is in memory and resets when the process restarts.
- Tokens are static local-lab credentials, not an identity provider.
- Coordinates are a fictional Cartesian range, not latitude/longitude.
- Battery consumption is deliberately simple and not a flight-dynamics model.
- The service validates safety decisions but does not control an aircraft.
- The dashboard is a thin assurance view, not a ground-control station.

These are deliberate boundaries for a safe, reviewable QA exercise. The backlog in `docs/lab-guide.md` describes defensible next steps.

## Standards and regulatory note

Civil UAS activity in Romania is governed by EU and national rules and must be checked against current EASA and Romanian Civil Aeronautical Authority material. Military and national-security systems may sit under different legal and certification regimes. This repository maps public assurance concepts for learning; it does not determine legal applicability or certify compliance.

See [docs/standards-and-regulations.md](docs/standards-and-regulations.md) for the source list and scope notes.

## License

Apache License 2.0. See [LICENSE](LICENSE).
