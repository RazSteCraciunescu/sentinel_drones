# Security Incident Tabletop

This exercise is for the local repository and development process. It does not cover operational UAS response.

## Scenario

A maintainer notices three signals on the same day:

1. The public repository accidentally contained a non-default token in an earlier commit.
2. A scheduled dependency audit reports a high-severity issue in a transitive package.
3. The assurance endpoint reports `audit_chain_valid=false` during a local demonstration.

## Objectives

- Separate credential exposure, supply-chain risk, and evidence-integrity symptoms rather than assuming one cause.
- Practice containment without destroying useful evidence.
- Decide what can be trusted and what must be rebuilt.
- Produce clear internal and public communication appropriate to a portfolio project.

## Discussion injects

### Inject 1 - Token exposure

The token was removed from the latest file, but remains in Git history.

Questions:

- Which tokens must be rotated?
- How will history, forks, Actions logs, local clones, and screenshots be considered?
- Does rotation alone address any data or action already exposed?
- Which preventive control failed: secret handling, review, scanning, or all three?

### Inject 2 - Dependency finding

The vulnerable package is used only by a development tool, and no exploitability analysis is available yet.

Questions:

- Is it present in the runtime image, CI only, or a developer environment?
- Can the affected feature be disabled without hiding the finding?
- What evidence supports upgrade, pin, removal, or temporary acceptance?
- How will reproducibility and rollback be preserved?

### Inject 3 - Invalid audit chain

A developer says they edited an in-memory event during a debugging session.

Questions:

- Can current events be trusted after arbitrary process memory modification?
- Should the service be restarted before further demonstration?
- What other evidence exists in request logs or test output?
- Does the event expose a documentation, code, or access-control gap?

## Expected response outline

1. Record time, reporter, version, environment, and known facts.
2. Preserve relevant commits, logs, workflow output, package lock state, and screenshots.
3. Revoke or replace all affected lab secrets and inspect exposure paths.
4. Determine dependency reachability and affected builds; apply the safest verified remediation.
5. Treat the modified in-memory audit store as untrusted and rebuild the lab from known source.
6. Run the full release checklist and security workflow.
7. Update the risk register, threat model, tests, and preventive controls.
8. Communicate scope and limitations without claiming that local hash linkage prevented compromise.

## Success criteria

- No operational system or external target is involved.
- Evidence is preserved before cleanup.
- Decisions are tied to observed scope and documented uncertainty.
- The team does not suppress a scanner or rewrite history without an explicit rationale.
- Follow-up work has owners and verification.
