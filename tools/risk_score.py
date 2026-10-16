from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RISK_FILE = ROOT / "qa" / "risk-register.csv"


def main() -> int:
    with RISK_FILE.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    errors: list[str] = []
    for row in rows:
        calculated = int(row["impact"]) * int(row["likelihood"]) * int(row["detectability"])
        if calculated != int(row["score"]):
            errors.append(
                f"{row['risk_id']} score is {row['score']} but should be {calculated}"
            )
        row["calculated_score"] = str(calculated)

    for row in sorted(rows, key=lambda item: int(item["calculated_score"]), reverse=True):
        print(
            f"{row['risk_id']:>4} | {int(row['calculated_score']):>3} | "
            f"{row['status']:<11} | {row['scenario']}"
        )

    if errors:
        print("\nRisk register errors:")
        for error in errors:
            print(f"- {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
