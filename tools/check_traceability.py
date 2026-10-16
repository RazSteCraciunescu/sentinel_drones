from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS_FILE = ROOT / "qa" / "requirements.csv"
TRACEABILITY_FILE = ROOT / "qa" / "traceability.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    requirements = read_csv(REQUIREMENTS_FILE)
    links = read_csv(TRACEABILITY_FILE)

    requirement_ids = {row["requirement_id"] for row in requirements}
    coverage: dict[str, list[str]] = defaultdict(list)
    unknown: set[str] = set()

    for link in links:
        requirement_id = link["requirement_id"]
        if requirement_id not in requirement_ids:
            unknown.add(requirement_id)
        coverage[requirement_id].append(link["evidence"])

    uncovered = sorted(requirement_ids - coverage.keys())
    if unknown:
        print(f"Unknown requirement IDs in traceability: {', '.join(sorted(unknown))}")
    if uncovered:
        print(f"Requirements without evidence: {', '.join(uncovered)}")

    pytest_evidence = sum(
        any("tests/" in evidence for evidence in evidence_items)
        for evidence_items in coverage.values()
    )
    print(
        f"Traceability: {len(requirement_ids)} requirements, "
        f"{len(links)} links, {pytest_evidence} with pytest evidence."
    )

    if unknown or uncovered:
        return 1
    print("Traceability check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
