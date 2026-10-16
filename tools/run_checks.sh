#!/usr/bin/env sh
set -eu

python tools/validate_repository.py
python tools/check_traceability.py
python tools/risk_score.py
ruff check .
mypy src
mkdir -p reports/local
pytest --junitxml=reports/local/junit.xml --cov=sentinel_uas --cov-report=xml:reports/local/coverage.xml --cov-report=term-missing
bandit -c pyproject.toml -r src
pip-audit

echo "All local checks passed."
