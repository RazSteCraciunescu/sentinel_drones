# ADR-0003: Keep a closed safe-command vocabulary

- Status: Accepted
- Date: 2026-09-12

## Context

An unrestricted command endpoint would weaken the safety boundary and could drift toward real operational control. The test project only needs enough state transition behavior to demonstrate authentication, authorization, freshness, idempotency, contract testing, and evidence.

## Decision

Represent exactly three actions in the API schema: `hold`, `return_home`, and `land`. Contract tests assert the exact enum. New actions require an ADR, threat-model and safety-case update, requirements, negative tests, and explicit confirmation that the simulation-only boundary remains intact.

## Consequences

- Unsupported values fail schema validation.
- Reviewers can detect accidental expansion through OpenAPI tests.
- The command gateway remains useful for QA while avoiding mission, payload, or weapon functions.
