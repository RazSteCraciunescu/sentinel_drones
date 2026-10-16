.PHONY: install run test unit security resilience coverage quality audit validate e2e docker clean

install:
	python -m pip install -e ".[dev]"

run:
	python -m uvicorn sentinel_uas.app:app --host 127.0.0.1 --port 8080

test:
	pytest

unit:
	pytest -m unit

security:
	pytest -m security
	bandit -c pyproject.toml -r src
	pip-audit

resilience:
	pytest -m resilience

coverage:
	pytest --cov=sentinel_uas --cov-report=xml --cov-report=term-missing

quality:
	ruff check .
	mypy src

validate:
	python tools/validate_repository.py
	python tools/check_traceability.py
	python tools/risk_score.py

audit:
	python tools/risk_score.py

e2e:
	npm run test:e2e

docker:
	docker compose up --build

clean:
	python -c "import shutil; [shutil.rmtree(p, ignore_errors=True) for p in ['.pytest_cache', '.mypy_cache', '.ruff_cache', 'htmlcov', 'reports/local', 'test-results', 'playwright-report']]"
