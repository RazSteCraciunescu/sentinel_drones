from __future__ import annotations

import argparse
import json
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path


def parse_start_time(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--start-time must be an ISO 8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise argparse.ArgumentTypeError("--start-time must include a timezone")
    return parsed.astimezone(UTC).replace(microsecond=0)


def generate(output: Path, frames: int, seed: int, started: datetime) -> None:
    rng = random.Random(seed)
    x_m = 0.0
    y_m = 0.0
    battery = 95.0

    with output.open("w", encoding="utf-8") as handle:
        for sequence in range(1, frames + 1):
            x_m += rng.uniform(-4, 4)
            y_m += rng.uniform(-4, 4)
            battery = max(0, battery - rng.uniform(0.08, 0.2))
            frame = {
                "drone_id": "UAS-001",
                "sequence": sequence,
                "sent_at": (started + timedelta(seconds=sequence)).isoformat(),
                "x_m": round(x_m, 2),
                "y_m": round(y_m, 2),
                "altitude_m": round(35 + rng.uniform(-2, 2), 2),
                "battery_pct": round(battery, 2),
                "link_quality_pct": round(rng.uniform(75, 98), 2),
                "sensor_confidence": round(rng.uniform(0.82, 0.99), 3),
                "mode": "active",
            }
            handle.write(json.dumps(frame, separators=(",", ":")) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate seeded synthetic telemetry JSONL")
    parser.add_argument("--output", type=Path, default=Path("test-data/generated-telemetry.jsonl"))
    parser.add_argument("--frames", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--start-time",
        type=parse_start_time,
        help="ISO 8601 timestamp; defaults to the current UTC time",
    )
    args = parser.parse_args()
    if args.frames < 1 or args.frames > 100_000:
        parser.error("--frames must be between 1 and 100000")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    started = args.start_time or datetime.now(UTC).replace(microsecond=0)
    generate(args.output, args.frames, args.seed, started)
    print(f"Wrote {args.frames} frames to {args.output}")


if __name__ == "__main__":
    main()
