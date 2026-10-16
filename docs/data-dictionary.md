# Data Dictionary

## Naming and units

- Identifiers are uppercase ASCII letters, digits, and hyphens, 3-64 characters.
- Coordinates are fictional Cartesian metres, not latitude/longitude.
- Altitude is a synthetic metre value relative to an unspecified local reference.
- Percentages use 0-100 inclusive.
- Timestamps must include a timezone and are normalized by normal datetime comparison.
- All thresholds are lab configuration values, not operational recommendations.

## Mission request

| Field | Type / range | Meaning |
| --- | --- | --- |
| `mission_id` | Identifier | Unique label supplied by the caller for a validation attempt |
| `drone_id` | Identifier | Seeded synthetic aircraft identifier |
| `mission_type` | Enum | Search and rescue, infrastructure inspection, supply delivery, perimeter observation, or training |
| `waypoints` | 1-50 objects | Ordered synthetic route points |
| `waypoints[].x_m` | -10,000 to 10,000 | East/west-like local axis; operating envelope is narrower |
| `waypoints[].y_m` | -10,000 to 10,000 | North/south-like local axis; operating envelope is narrower |
| `waypoints[].altitude_m` | 0-500 | Requested synthetic altitude; configured ceiling is narrower |
| `battery_pct` | 0-100 | Reported launch battery |
| `estimated_duration_min` | >0 to 240 | Simplified duration input for the reserve estimate |
| `reserve_battery_pct` | 0-100 | Requested recovery reserve |
| `link_quality_pct` | 0-100 | Simplified launch-link indicator |

## Telemetry frame

| Field | Type / range | Meaning |
| --- | --- | --- |
| `drone_id` | Identifier | Aircraft whose synthetic state is being reported |
| `sequence` | 0 to 2,147,483,647 | Per-aircraft monotonic ordering value |
| `sent_at` | Timezone-aware datetime | Caller-declared creation time used for freshness checks |
| `x_m`, `y_m` | -10,000 to 10,000 | Synthetic position |
| `altitude_m` | 0-500 | Synthetic altitude; values above the configured ceiling request recovery |
| `battery_pct` | 0-100 | Current simplified battery indicator |
| `link_quality_pct` | 0-100 | Current simplified link indicator |
| `sensor_confidence` | 0-1 | Abstract confidence indicator for exercising a hold decision |
| `mode` | Enum | Reported mode before the lab applies any fail-safe result |

## Safe command request

| Field | Type / range | Meaning |
| --- | --- | --- |
| `command_id` | Identifier | Idempotency key within the current process state |
| `drone_id` | Identifier | Target synthetic aircraft |
| `action` | Enum | `hold`, `return_home`, or `land` only |
| `issued_at` | Timezone-aware datetime | Freshness reference |
| `ttl_seconds` | 1-30 | Maximum accepted age from issue time |
| `reason` | 5-200 characters | Human-readable rationale recorded in the audit event |

## Assurance metrics

| Field | Meaning |
| --- | --- |
| `drones_total` | Seeded aircraft count |
| `drones_active` | Aircraft currently in active, hold, or return-home modes |
| `audit_events` | Number of process-local audit events |
| `audit_chain_valid` | Result of recomputing the local hash chain |
| `rejected_missions` | Mission decisions that were not approved |
| `rejected_commands` | Command requests rejected after schema validation |
| `rejected_telemetry_frames` | Telemetry requests rejected after schema validation |
