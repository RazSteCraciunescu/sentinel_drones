# Reports

`reports/sample/` contains reviewed examples and templates suitable for a portfolio walkthrough. Generated local evidence belongs in `reports/local/`, which is excluded from Git.

Typical local artifacts:

- `junit.xml` - machine-readable pytest result;
- `coverage.xml` - coverage input for CI or dashboards;
- Playwright HTML report and traces;
- k6 or Locust output captured with environment details;
- release execution summary.

A report should identify the commit, environment, tool versions, scope, skipped tests, deviations, result, and residual risk. Never copy a sample number into a release report without rerunning the relevant check.
