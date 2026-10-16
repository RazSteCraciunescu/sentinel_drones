# ADR-0002: Use process-local in-memory state

- Status: Accepted for version 0.1
- Date: 2026-09-12

## Context

The lab needs deterministic setup, fast tests, and no external service dependency. Persistent storage would add migrations, concurrency, credential, and deployment concerns before they contribute to the main assurance exercises.

## Decision

Store the fleet, last telemetry sequences, command IDs, counters, and audit events in one process. Reset state for isolated tests and through a maintainer-only endpoint.

## Consequences

- Tests are fast and simple to reproduce.
- Restarting loses anti-replay state and audit evidence.
- Multiple worker processes would have inconsistent state.
- The design is unsuitable for operational evidence or distributed deployment.
- Durable idempotency, shared state, signed remote logging, backup, and recovery remain explicit backlog items.
