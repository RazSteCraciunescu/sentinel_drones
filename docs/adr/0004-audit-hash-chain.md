# ADR-0004: Use a hash chain as local tamper-evidence

- Status: Accepted with limitations
- Date: 2026-09-12

## Context

The lab needs reviewable evidence that demonstrates integrity concepts without operating a database, key-management system, or remote log service.

## Decision

Each event includes the prior event hash. A canonical JSON representation is hashed with SHA-256, and a verifier recomputes the chain.

## Consequences

- Accidental or simple historical modification can be detected.
- The mechanism demonstrates evidence-linking and supports unit testing.
- It does not prevent deletion, full-chain replacement, memory compromise, or loss on restart.
- Documentation must say “tamper-evident,” never “tamper-proof.”
