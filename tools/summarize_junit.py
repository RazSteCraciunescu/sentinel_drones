from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Print a compact JUnit XML summary")
    parser.add_argument("report", type=Path)
    args = parser.parse_args()

    root = ET.parse(args.report).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
    totals = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0, "time": 0.0}
    for suite in suites:
        for key in ("tests", "failures", "errors", "skipped"):
            totals[key] += int(suite.attrib.get(key, 0))
        totals["time"] += float(suite.attrib.get("time", 0))

    print(
        "JUnit summary: "
        f"tests={totals['tests']} failures={totals['failures']} "
        f"errors={totals['errors']} skipped={totals['skipped']} "
        f"time={totals['time']:.2f}s"
    )
    return 1 if totals["failures"] or totals["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
