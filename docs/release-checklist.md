# Release Checklist

## Scope and change review

- [ ] Simulation-only boundary is still accurate.
- [ ] No real aircraft, radio, payload, target, credential, location, or operational data was added.
- [ ] Changed behavior has updated requirements and acceptance criteria.
- [ ] Threat model, risk register, FMEA, and ADRs were reviewed for impact.

## Verification

- [ ] Clean environment install succeeds.
- [ ] Repository validation passes.
- [ ] Traceability check passes with no unknown or uncovered requirements.
- [ ] Ruff and mypy pass.
- [ ] Full pytest suite passes and coverage remains at or above 85%.
- [ ] Browser smoke passes in Chromium.
- [ ] Postman smoke was reviewed after API-contract changes.
- [ ] Bandit, dependency audit, and CodeQL are clean or findings are dispositioned.
- [ ] Docker image starts as a non-root user and health check passes.

## Evidence and risk

- [ ] Test result and environment are recorded in a release summary.
- [ ] No unresolved S1 or S2 defect remains.
- [ ] Open and accepted risks have a current owner and rationale.
- [ ] Sample reports are not presented as results from a different build.
- [ ] Limitations and residual risks are visible in the README and safety case.

## Packaging

- [ ] `.env`, `.venv`, caches, local reports, and browser artifacts are excluded.
- [ ] Version is consistent in `pyproject.toml`, `package.json`, package `__version__`, and changelog.
- [ ] Archive opens cleanly and contains one top-level project folder.
- [ ] GitHub Actions references and supported language versions remain current.
