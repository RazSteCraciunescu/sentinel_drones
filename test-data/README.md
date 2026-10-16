# Synthetic Test Data

- `mission_samples.json` contains nominal and deliberately rejected mission examples.
- `telemetry_nominal.jsonl` contains sequential frames inside the lab envelope.
- `telemetry_faults.jsonl` contains synthetic battery, link, altitude, geofence, restricted-zone, and confidence conditions.

JSON Lines files contain one object per line. Static timestamps are examples for data review and are normally replaced with a current timezone-aware value before API submission.

Use `python tools/generate_telemetry.py` for fresh seeded data. Pass `--start-time` to reproduce the complete file byte-for-byte.

All coordinates, identifiers, and scenarios are fictional. Do not add real locations or operational data.
