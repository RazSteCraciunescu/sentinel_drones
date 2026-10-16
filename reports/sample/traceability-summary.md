# Traceability Summary

## Baseline

- Requirements: 36
- Traceability links: 50
- Requirements with at least one named evidence item: 36
- Requirements with pytest evidence: 32
- Quality-process requirements evidenced by configuration, workflow, or validation tooling: 4
- Unknown requirement references: 0
- Uncovered requirement IDs: 0

## Coverage by area

| Area | Evidence pattern |
| --- | --- |
| Functional API | API tests and OpenAPI checks |
| Mission safety | Unit and API boundary tests |
| Telemetry and recovery | API, resilience, and property tests |
| Authentication and authorization | Security matrix tests |
| Command integrity | API freshness, enum, and replay tests |
| Audit integrity | Unit tamper-detection tests and API access tests |
| Quality gates | Coverage configuration, CI workflows, security workflow, and repository checker |

## Review note

Traceability demonstrates that every baseline requirement has an identified verification path. It does not prove that every requirement is correct, independent, complete, or valid for real flight. Requirement quality and the adequacy of each oracle still require human review.
