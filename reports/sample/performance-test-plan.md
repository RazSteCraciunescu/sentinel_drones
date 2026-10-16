# Performance Smoke Test Plan

## Objective

Detect obvious latency, error-rate, or resource regressions in the local assurance API. This is a development smoke test, not a flight-system capacity qualification.

## Workloads

### Read-heavy smoke

- Health: 20%
- Fleet snapshot: 40%
- Assurance metrics: 40%
- One observer token
- Gradual ramp to 10 virtual users
- Five-minute steady period after warm-up

### Decision smoke

- Mission validation: 35%
- Fresh sequential telemetry: 50%
- Unique safe command: 15%
- Synthetic identifiers and current timestamps
- Per-user aircraft/sequence coordination to avoid test-data replay unless replay is the intended scenario

## Proposed local thresholds

These are regression gates for a recorded reference machine, not universal performance requirements:

- HTTP error rate below 1%, excluding deliberately rejected negative requests.
- p95 below 250 ms for read endpoints.
- p95 below 400 ms for decision endpoints.
- No invalid audit chain.
- No unexplained state or sequence conflicts.
- Stable memory after warm-up for the fixed-duration smoke.

## Tools

- `performance/k6_smoke.js` for a concise CI-friendly workload.
- `performance/locustfile.py` for an interactive mixed workload.
- Application metrics and host monitoring for diagnosis.

## Evidence to record

- Commit and configuration hash.
- CPU, RAM, OS, Python, container mode, and worker count.
- Tool version and exact command.
- Warm-up and duration.
- Requests, throughput, p50/p95/p99, error rate, and failed checks.
- Expected versus unexpected 4xx results.
- Audit-chain status and rejected counters after the run.
- Comparison only against a controlled baseline on equivalent hardware.

## Known model limitation

The single-process in-memory design avoids database and network dependencies. A good result therefore says little about a durable or distributed architecture. Re-run and redesign the workload after adding storage, identity, external services, multiple workers, or representative network conditions.
