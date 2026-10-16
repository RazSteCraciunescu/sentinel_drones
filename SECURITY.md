# Security policy

## Scope

This project is a synthetic QA lab. It does not connect to real aircraft, radios, autopilots, payloads, or operational networks.

Security reports are welcome for the code in this repository, especially:

- authentication or authorization bypass;
- command replay or freshness failures;
- audit-chain integrity defects;
- unsafe input handling;
- dependency or container weaknesses;
- accidental exposure of non-lab secrets.

## Reporting

Do not open a public issue for a vulnerability that could affect a deployed fork. Use GitHub private vulnerability reporting when enabled, or contact the repository owner privately.

Include:

1. affected version or commit;
2. reproducible local-lab steps;
3. expected and actual result;
4. impact within this simulation boundary;
5. a suggested fix when available.

## Safe-research boundary

Do not test against real UAS, aviation infrastructure, military systems, public networks, radio links, or third-party services. Reports containing operational intrusion, interference, payload, targeting, or weaponization instructions are outside this project's scope.

## Supported versions

This is a portfolio lab rather than a production product. Only the current default branch is maintained.
