# Failure Modes and Effects Analysis

The working FMEA is stored in `qa/fmea.csv`. It is intentionally compact so it can be filtered in Excel, Google Sheets, or a test-management tool.

## Scoring

Each factor uses a 1-5 scale:

- **Severity:** 1 is negligible; 5 could defeat a primary safety or security invariant.
- **Occurrence:** 1 is unlikely in the lab; 5 is expected without a control.
- **Detection:** 1 is almost certain to be detected before use; 5 is difficult to detect.
- **RPN:** severity x occurrence x detection.

The RPN is a prioritization aid, not an objective safety proof. A severity-5 failure still deserves explicit review even when its calculated RPN is moderate.

## Current priorities

| Area | Failure concern | RPN | Position |
| --- | --- | ---: | --- |
| Battery estimator | Simplified consumption model overstates recovery margin | 80 | Accepted only because the project is non-operational; requires representative calibration before any real use |
| Audit log | Evidence is lost on restart or rewritten after process compromise | 64 | Open; remote signed or write-once evidence is the defensible next step |
| Configuration | Incorrect geofence or restricted-zone values are loaded | 60 | Open; add schema, signed baseline, dual review, and configuration-drift evidence |
| Supply chain | Vulnerable or malicious dependency enters the build | 48 | Partly mitigated by automated scanning and update review |

## Review approach

1. Review the effect before debating the numerical score.
2. Confirm that each listed control is actually implemented or clearly marked as planned.
3. Link detection controls to executable evidence where possible.
4. Re-score after a control materially changes occurrence or detectability.
5. Keep residual risk explicit; do not set every item to “mitigated” merely because a test exists.

## Triggers for a new row or re-score

- new endpoint, role, command, or data source;
- changed threshold or decision priority;
- persistent storage or distributed deployment;
- external identity, mapping, weather, or fleet integration;
- new CI or release mechanism;
- defect demonstrating that an assumed control is weaker than expected.
