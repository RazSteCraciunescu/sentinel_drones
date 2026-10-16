# Hands-On Lab Guide

## Lab 0 - Prepare the project

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Run the core checks:

```powershell
python tools\validate_repository.py
python tools\check_traceability.py
pytest --cov=sentinel_uas --cov-report=term-missing
```

Start the service:

```powershell
python -m uvicorn sentinel_uas.app:app --host 127.0.0.1 --port 8080
```

Open `http://127.0.0.1:8080/docs`.

## Lab 1 - Establish the nominal path

1. Call `GET /health` without a token.
2. Authorize Swagger with `operator-local-token` in the `X-Lab-Token` field.
3. Submit a mission from `test-data/mission_samples.json` that remains inside the lab envelope.
4. Record the approval decision and projected recovery battery.
5. Read the audit endpoint using `auditor-local-token`.

**Learning point:** A positive test establishes that the system is testable. It does not demonstrate that controls reject unsafe input.

## Lab 2 - Boundary analysis

Take the nominal mission and change one value at a time:

- altitude: 120, then 120.001;
- x coordinate: 500, then 500.001;
- restricted-zone coordinate: x 100 and y 0;
- battery: 30, then 29.999;
- launch link: 55, then 54.999.

Record whether the implementation matches the acceptance criteria and whether the rejection reason is useful. Do not treat a threshold passing test as evidence that the threshold is correct for real flight.

## Lab 3 - Replay and ordering

1. Submit a fresh telemetry frame for `UAS-001` with sequence 10.
2. Submit sequence 10 again.
3. Submit sequence 9.
4. Submit sequence 11.
5. Read the fleet and assurance metrics.

**Expected:** The first and fourth frames are accepted. Duplicate and older frames return HTTP 409 and cannot overwrite the latest state.

## Lab 4 - Degraded conditions

Create fresh frames that trigger one condition at a time:

| Condition | Example | Expected lab action |
| --- | --- | --- |
| Critical battery | 12% | `land` |
| Outside geofence | x 501 | `return_home` |
| Restricted zone | x 150, y 0 | `return_home` |
| Degraded link | 29% | `return_home` |
| Low confidence | 0.39 | `hold` |

Then combine critical battery with every other condition. Confirm that the documented priority is stable.

## Lab 5 - Authorization matrix

Try the following with each token:

- read fleet;
- validate a mission;
- submit telemetry;
- submit a safe command;
- read audit events;
- reset the simulation.

Compare the results with `docs/architecture.md`. Distinguish missing or invalid authentication (401) from an authenticated role lacking permission (403).

## Lab 6 - Command freshness and idempotency

1. Submit a fresh `hold` command with a unique ID.
2. Repeat the same ID.
3. Submit an already expired command.
4. Submit a command timestamp more than the permitted future skew.
5. Try a command action outside the schema.

**Expected:** Only the first request is accepted. Invalid action vocabulary fails schema validation before domain processing.

## Lab 7 - Audit integrity

Run the audit unit tests:

```powershell
pytest tests\unit\test_audit.py -vv
```

Read `src/sentinel_uas/store.py` and explain:

- what fields contribute to each hash;
- how the previous hash links events;
- what mutation the test detects;
- why an in-memory SHA-256 chain is tamper-evident but not tamper-proof.

## Lab 8 - Traceability and change impact

1. Choose one safety requirement.
2. Find its test case in `qa/test-cases.csv`.
3. Find its evidence link in `qa/traceability.csv`.
4. Locate the executable test and implementation.
5. Propose a behavior change and list every artifact that should be reviewed.

Run:

```powershell
python tools\check_traceability.py
```

## Lab 9 - Browser and performance smoke

Install browser dependencies:

```powershell
npm install
npx playwright install chromium
npm run test:e2e
```

For a local k6 smoke run:

```powershell
k6 run performance\k6_smoke.js
```

Record environment, commit, workload, latency percentiles, failures, and limitations. Do not compare results from different machines as though they were controlled benchmarks.

## Lab 10 - Make a defensible enhancement

Choose one backlog item:

- audit authenticated rejection paths;
- reject unexpected object properties explicitly;
- add rate limiting for local abuse testing;
- persist command idempotency and sequences in a local database;
- generate an SBOM in CI;
- add configuration schema and drift check;
- add accessibility checks to the dashboard;
- add a second implementation of the mission decision as a test oracle.

For the change, update requirements, tests, traceability, risk/FMEA where relevant, and the architecture decision record. Avoid adding real flight protocols, weapon functions, or operational data.
