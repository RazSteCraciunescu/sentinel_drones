# ADR-0001: Keep the project simulation-only

- Status: Accepted
- Date: 2026-09-12

## Context

The project is intended to demonstrate senior QA, safety, and cybersecurity practices for high-consequence UAS software. Adding real command protocols, radio procedures, payload logic, targeting, or operational data would create safety, security, legal, and ethical risks and would make the repository harder to review safely.

## Decision

Use a synthetic Cartesian environment, seeded in-memory aircraft, abstract quality indicators, and exactly three non-weapon safety actions: `hold`, `return_home`, and `land`. Do not include real flight-control integration or instructions for interfering with real systems.

## Consequences

- The repository is reproducible on an ordinary PC and safe to review publicly.
- QA practices remain executable rather than purely theoretical.
- Results cannot be generalized to real flight, radio, navigation, or payload behavior.
- A real simulator or hardware adapter would require a separate architecture, threat model, hazard analysis, governance path, and access controls.
