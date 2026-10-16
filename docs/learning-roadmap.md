# Ten-Week Learning Roadmap

The roadmap turns the repository into a practical study plan for a senior QA engineer moving into UAS software assurance. Each week ends with evidence that can be committed rather than passive reading notes.

## Week 1 - Domain and boundaries

Study the difference between aircraft, ground-control software, fleet services, communications, payloads, and operational procedures. Read the EASA and Romanian CAA starting material in `docs/standards-and-regulations.md`.

**Deliverable:** Redraw the context diagram and write five assumptions that would become invalid if the lab connected to hardware.

## Week 2 - Risk-based test design

Review the requirements, risk register, and FMEA. Practice boundary-value analysis, equivalence classes, state transitions, and decision tables.

**Deliverable:** Add three justified cases to `qa/test-cases.csv` and trace them without duplicating existing coverage.

## Week 3 - API and contract assurance

Use Swagger and Postman. Follow positive, negative, authentication, authorization, schema, and backward-compatibility paths.

**Deliverable:** Export a Postman run or create a concise API test report with one discovered ambiguity.

## Week 4 - Python automation

Read fixtures, parameterization, test markers, FastAPI `TestClient`, and coverage output. Modify one threshold through a test-specific `Settings` object rather than editing production defaults.

**Deliverable:** One unit test, one API test, and one regression note linked to a requirement.

## Week 5 - Cybersecurity testing

Study NIST CSF 2.0, the NIST uncrewed-systems paper, and the OWASP API Security Top 10. Review authentication, function-level authorization, replay, freshness, bounded input, and audit limitations.

**Deliverable:** Add one threat scenario, control, test, and residual-risk statement. Keep it defensive and local.

## Week 6 - Safety and resilience

Study fail-safe priority, hazard combinations, recovery assumptions, and the difference between a test oracle and an operationally valid policy.

**Deliverable:** Create a decision table for all pairwise hazard combinations and automate the highest-risk missing row.

## Week 7 - Evidence and traceability

Review the safety case, requirement matrix, audit chain, release criteria, and defect examples.

**Deliverable:** Run the traceability checker, investigate every manual link, and create an execution summary from fresh results.

## Week 8 - Performance and reliability

Learn latency percentiles, throughput, error rate, coordinated omission, warm-up, workload realism, and why a local smoke result is not a capacity claim.

**Deliverable:** Run k6 or Locust locally, record hardware and configuration, and compare two controlled builds.

## Week 9 - DevSecOps and supply chain

Review GitHub Actions permissions, dependency pinning, automated updates, CodeQL, Bandit, dependency audit, container user/capabilities, and build evidence.

**Deliverable:** Explain one CI gate failure from logs and document a defensible fix rather than disabling the gate.

## Week 10 - Portfolio demonstration

Run the release checklist from a clean clone. Use the ten-minute walkthrough and answer the interview prompts in `docs/portfolio-walkthrough.md`.

**Deliverable:** Tag a release only after tests, evidence, limitations, and residual risks agree.

## Optional next topics

- robot and UAS simulators such as Gazebo or software-in-the-loop environments, used only in isolated training scenarios;
- hardware-in-the-loop test architecture and lab safety controls;
- geospatial testing, coordinate reference systems, and map-data quality;
- time synchronization and trusted timestamps;
- signed configuration, secure update, SBOM, provenance, and vulnerability response;
- AI assurance for perception systems using synthetic or properly governed datasets;
- human factors, alerting, workload, and operator-error testing.
