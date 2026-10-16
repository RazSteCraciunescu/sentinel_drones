# Contributing

Contributions should preserve the simulation-only boundary and add measurable assurance value.

## Before opening a pull request

```bash
python -m pip install -e ".[dev]"
pytest --cov=sentinel_uas --cov-report=term-missing
ruff check .
mypy src
python tools/validate_repository.py
python tools/check_traceability.py
python tools/risk_score.py
```

## Change expectations

- Add or update a requirement when behavior changes.
- Add traceability from the requirement to executable evidence.
- Add negative tests for security- or safety-relevant paths.
- Update the threat model or FMEA when the attack surface or hazard model changes.
- Keep test data synthetic.
- Do not add real flight-control, radio, targeting, payload, or countermeasure procedures.

Small, focused changes are preferred. A pull request should explain the risk being reduced, not only the code being changed.
