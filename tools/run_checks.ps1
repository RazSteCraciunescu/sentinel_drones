$ErrorActionPreference = "Stop"

Write-Host "[1/5] Repository data"
python tools\validate_repository.py
python tools\check_traceability.py
python tools\risk_score.py

Write-Host "[2/5] Python lint"
ruff check .

Write-Host "[3/5] Type checking"
mypy src

Write-Host "[4/5] Tests and coverage"
New-Item -ItemType Directory -Force -Path reports\local | Out-Null
pytest --junitxml=reports\local\junit.xml --cov=sentinel_uas --cov-report=xml:reports\local\coverage.xml --cov-report=term-missing

Write-Host "[5/5] Security checks"
bandit -c pyproject.toml -r src
pip-audit

Write-Host "All local checks passed."
