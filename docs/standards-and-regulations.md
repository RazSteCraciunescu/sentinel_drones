# Standards and Regulatory Context

## Scope note

This document is a reading map for a software QA portfolio. It does not decide which law or standard applies to a specific aircraft, operator, mission, organization, or military system. Applicability depends on the system, intended use, operational category, airspace, authority, contract, and certification basis. Use current official material and qualified legal, safety, security, and airworthiness specialists for real work.

## European and Romanian UAS context

### EASA Easy Access Rules for UAS

The EASA consolidated UAS rules cover Commission Implementing Regulation (EU) 2019/947, associated acceptable means of compliance and guidance material, and Commission Delegated Regulation (EU) 2019/945. The June 2026 revision includes the SORA 2.5 package.

Official source:

- https://www.easa.europa.eu/en/document-library/easy-access-rules/easy-access-rules-unmanned-aircraft-systems

Portfolio relevance:

- operational categories and risk-proportionate thinking;
- documented limitations and authorization assumptions;
- traceable operational and technical mitigations;
- keeping current with later amendments rather than relying on a copied summary.

### Romanian Civil Aeronautical Authority

The Romanian Civil Aeronautical Authority publishes national UAS legislation and links to European rules and local requirements.

Official source:

- https://www.caa.ro/pages/legislatie-drone

Portfolio relevance:

- demonstrates that Romanian operation requires current national and EU context;
- separates software assurance from permission to operate;
- avoids implying that a generic test suite authorizes a mission.

## Cybersecurity and software assurance references

### NIST Cybersecurity Framework 2.0

CSF 2.0 organizes cybersecurity outcomes under Govern, Identify, Protect, Detect, Respond, and Recover.

Official source:

- https://www.nist.gov/cyberframework
- https://doi.org/10.6028/NIST.CSWP.29

This repository uses the functions as a lightweight coverage lens in `docs/threat-model.md`.

### NIST work on uncrewed systems

NIST published a 2024 paper discussing cybersecurity and AI risk-management challenges for increasingly connected and automated uncrewed systems, with references to CSF 2.0 and the AI Risk Management Framework.

Official source:

- https://www.nist.gov/publications/cybersecurity-and-ai-risk-managment-uncrewed-systems-challenges-and-opportunities-using
- https://doi.org/10.52202/075106-0003

Portfolio relevance:

- connected autonomy creates combined cyber, AI, and safety concerns;
- controls need system context rather than generic API testing alone;
- public-safety, inspection, transport, and delivery scenarios are useful high-consequence examples without adding weapon logic.

### CISA UAS cybersecurity guidance

CISA publishes UAS cybersecurity resources emphasizing risk management, secure design, data protection, and connectivity concerns.

Official source:

- https://www.cisa.gov/topics/physical-security/be-air-aware/uas-cybersecurity

Portfolio relevance:

- treat platform, controller, data, network, cloud, update, and supply-chain paths as a system;
- define security requirements before deployment;
- avoid assuming that physical possession is the only meaningful threat.

### OWASP API Security Top 10 - 2023

Official source:

- https://owasp.org/API-Security/editions/2023/en/0x11-t10/

Relevant themes include broken authentication, broken object or function authorization, unrestricted resource consumption, security misconfiguration, API inventory, and unsafe consumption of external APIs. The lab directly exercises authentication, function-level role checks, bounded inputs, and contract inventory. It records rate limiting and third-party API trust as future work rather than claiming complete OWASP coverage.

## Aviation security process references

### RTCA DO-326A

DO-326A is an airworthiness security process specification intended to address intentional unauthorized electronic interaction affecting aircraft safety. It belongs to a wider family of aeronautical security material and is a paid standard.

Official catalogue source:

- https://my.rtca.org/productdetails?id=a1B36000001IcfuEAC

### EUROCAE ED-202A

ED-202A is the EUROCAE airworthiness security process specification counterpart/reference in this domain.

Official catalogue source:

- https://www.eurocae.net/product/ed-202a-airworthiness-security-process-specification/

Portfolio relevance for both:

- security risk should connect to safety impact and the development lifecycle;
- evidence, assumptions, verification, and continuing-airworthiness concerns matter;
- citing a standard is not the same as complying with it. This repository neither reproduces paid content nor claims conformity.

## Broader EU cyber context

### NIS2 Directive

Official source:

- https://eur-lex.europa.eu/eli/dir/2022/2555/oj

### Cyber Resilience Act

Official source:

- https://eur-lex.europa.eu/eli/reg/2024/2847/oj

These instruments may be relevant to organizations or products depending on scope and classification. They are listed to show awareness of governance, vulnerability handling, supply-chain, and product-security obligations. No applicability conclusion is made for this lab.

## Practical use in this repository

| Reference theme | Repository evidence |
| --- | --- |
| Risk governance | `qa/risk-register.csv`, `qa/fmea.csv`, ADRs |
| System and API protection | RBAC, bounded schemas, freshness and replay checks |
| Detection and evidence | rejection counters, audit-chain verification, CI scans |
| Response and recovery | deterministic fail-safe decisions, reset, defect process |
| Safety-security connection | threat model, safety case, multi-hazard tests |
| Lifecycle assurance | requirements, traceability, CI, Dependabot, reports |
| Honest applicability | explicit simulation boundary and known gaps |

## Suggested study order

1. EASA Easy Access Rules and Romanian CAA pages for operating context.
2. NIST CSF 2.0 for cybersecurity governance vocabulary.
3. NIST uncrewed-systems paper for system-specific risk framing.
4. OWASP API Security Top 10 for API abuse cases.
5. Public overviews and official catalogues for aviation security-process standards.
6. Organization-specific engineering, legal, safety, and certification material under appropriate access controls.
