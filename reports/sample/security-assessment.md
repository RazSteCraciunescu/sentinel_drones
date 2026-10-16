# Security Assessment - Simulation Service

## Scope

A defensive review of the local API, role model, request schemas, freshness and replay controls, safe-command vocabulary, audit evidence, container settings, dependency workflow, and public-repository boundary.

No real UAS, external host, radio link, third-party account, or operational environment was tested.

## Summary

No verified critical defect was identified during the code and design review. The strongest controls are the closed command enum, endpoint-specific role checks, bounded request models, stale/future/replay rejection, deterministic recovery decisions, and explicit simulation boundary.

The design still has important residual risks that are acceptable only for a local portfolio lab.

## Findings

### SA-01 - Static bearer tokens

- Rating: Medium in a deployed service; accepted for local lab
- Observation: Four obvious default tokens map directly to roles.
- Risk: Disclosure grants the associated role and events identify only a role, not a named person.
- Existing controls: Separate role tokens, environment overrides, no production claim, protected endpoints.
- Recommendation: Use short-lived identities, managed secrets, named attribution, lifecycle controls, and stronger authentication before any deployment.

### SA-02 - Volatile replay and audit state

- Rating: High for operational evidence; accepted/open for lab
- Observation: Command IDs, telemetry sequences, and audit events are stored in process memory.
- Risk: Restarting permits reuse of earlier identifiers and loses evidence.
- Existing controls: In-process idempotency, monotonic sequence, SHA-256 chain, explicit limitation.
- Recommendation: Durable transactional state, restart-safe idempotency, trusted time, signed events, and remote write-once evidence.

### SA-03 - No cryptographic message origin

- Rating: High for a real system; out of scope for lab
- Observation: Tokens authenticate the API caller, but individual telemetry frames and commands are not signed.
- Risk: A party with the API credential can construct valid-looking data.
- Recommendation: Define device and operator identity, key lifecycle, anti-replay protocol, message authentication, revocation, and recovery under a separate system security architecture.

### SA-04 - No rate limiting

- Rating: Medium
- Observation: Field and collection sizes are bounded, but request frequency is not.
- Risk: A local or exposed service could be resource-exhausted.
- Existing controls: Schema limits, small in-memory model, performance profiles.
- Recommendation: Add rate and concurrency limits, back-pressure, observability, and abuse tests before network exposure.

### SA-05 - Supply-chain evidence is CI-dependent

- Rating: Medium
- Observation: The repository defines Bandit, dependency auditing, CodeQL, and Dependabot, but a clean security result must come from the actual workflow run.
- Recommendation: Require the security workflow, retain evidence, review updates, add an SBOM and signed provenance for releases, and avoid treating a workflow file as proof that a scan passed.

## Positive observations

- Protected endpoints distinguish authentication failure from authenticated role denial.
- Safe actions are schema-constrained and contract-tested.
- Unexpected request properties are rejected.
- Freshness, timezone, sequence, TTL, and duplicate IDs have negative tests.
- Audit-chain limitations are accurately described.
- Docker runs as a non-root user, drops Linux capabilities, disables privilege escalation, and uses a read-only filesystem.
- CI uses restricted default permissions and a separate security workflow.

## Conclusion

The project is defensible as a local QA and cyber-resilience lab. Its controls demonstrate useful engineering practices, but the identity, evidence, message-authentication, persistence, availability, and external-validity gaps prevent any operational-security claim.
