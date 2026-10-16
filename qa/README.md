# QA Evidence Set

The files in this directory are designed to be useful both in Git and in spreadsheet/test-management tools.

| File | Purpose |
| --- | --- |
| `requirements.csv` | Baseline functional, safety, security, resilience, and quality requirements |
| `test-cases.csv` | Human-readable test inventory with expected results and automation status |
| `traceability.csv` | Requirement-to-test and evidence links |
| `risk-register.csv` | Impact, likelihood, detectability, controls, ownership, status, and residual risk |
| `fmea.csv` | Failure modes, effects, RPN, controls, and verification |
| `control-mapping.csv` | Lightweight mapping to NIST CSF functions and OWASP API themes |
| `threat-catalog.yaml` | Structured defensive threat scenarios for review and future tooling |

Run the repository checks after editing CSV files:

```powershell
python tools\validate_repository.py
python tools\check_traceability.py
python tools\risk_score.py
```

Do not add real operations, coordinates, aircraft identifiers, credentials, employer data, or restricted information.
