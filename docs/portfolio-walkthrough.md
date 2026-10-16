# Portfolio Walkthrough

## Two-minute explanation

“Sentinel UAS Assurance Lab is a simulation-only QA and cyber-resilience project for high-consequence drone software. I built a small FastAPI system so the test evidence is executable rather than a collection of documents. It validates synthetic missions, rejects stale or replayed data, applies deterministic fail-safe decisions, enforces server-side roles, and records a tamper-evident audit chain. The repository connects requirements, test cases, risks, FMEA, threat modeling, automated tests, performance profiles, and CI security gates. It intentionally contains no real flight protocol, radio, target, payload, or weapon-control logic.”

## Ten-minute demonstration

1. Show the README boundary and skill table.
2. Run `python tools/check_traceability.py`.
3. Run the pytest suite with coverage.
4. Open Swagger and approve a nominal mission.
5. Move one waypoint outside x 500 and show rejection.
6. Submit a fresh telemetry frame, then replay its sequence.
7. Submit a degraded-link frame and explain the `return_home` decision.
8. Show the role matrix by denying an observer an operator function.
9. Read the audit event list and explain what the hash chain can and cannot prove.
10. Open the risk register and discuss the accepted battery-model limitation instead of overstating the prototype.

## Skills demonstrated

- Senior-level risk-based QA and test strategy.
- API, schema, contract, negative, and boundary testing.
- Python, FastAPI, pytest, fixtures, parameterization, property tests, and coverage.
- Authentication, authorization, replay, freshness, idempotency, input hardening, and audit evidence.
- Safety case, FMEA, threat model, risk register, and requirements traceability.
- Postman, Playwright, k6, Locust, Docker, PowerShell, Git, and GitHub Actions.
- Ruff, mypy, Bandit, dependency audit, CodeQL, Dependabot, and container hardening.
- Honest scoping, residual-risk decisions, and regulatory research relevant to Romania and the EU.

## Interview questions and defensible answers

### Why not connect it to a real drone simulator or MAVLink?

The portfolio goal is assurance practice without publishing operational control material. A synthetic interface makes safety, security, and evidence logic reviewable on any machine. Real protocol or hardware integration would require a different threat model, lab controls, legal review, domain expertise, and representative system validation.

### Is the audit log secure?

It is a process-local hash chain that makes accidental or simple modification detectable. It does not prevent a privileged attacker from rewriting memory and recomputing the entire chain, and it disappears on restart. Durable signed remote logging is recorded as a required evolution for higher assurance.

### Why is 96% coverage not proof of quality?

Coverage shows which code paths were executed, not whether the requirements, oracles, data, and safety policy are correct. The project combines coverage with traceability, boundaries, decision tables, property tests, exploratory charters, FMEA, threat modeling, and explicit residual risks.

### Why accept static tokens?

They keep the lab deterministic and easy to run. The design does not present them as production security. The risk register calls for short-lived identity, stronger lifecycle controls, and named attribution before deployment.

### What is the most important open risk?

The simplified battery estimate has low external validity. It is useful for testing a reserve gate but cannot predict real recovery margin. The FMEA gives it the highest RPN and the repository explicitly limits the result to simulation.

### What would you build next?

Persistent idempotency and evidence, signed configuration, explicit rejection audit events, rate limiting, SBOM/provenance, accessibility checks, and an isolated software-in-the-loop adapter governed by a new safety and security assessment.
