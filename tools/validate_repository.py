from __future__ import annotations

import ast
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "SECURITY.md",
    "pyproject.toml",
    "src/sentinel_uas/app.py",
    "qa/requirements.csv",
    "qa/traceability.csv",
    "qa/risk-register.csv",
    "qa/fmea.csv",
    "qa/test-cases.csv",
    "qa/control-mapping.csv",
    "qa/threat-catalog.yaml",
    "docs/test-strategy.md",
    "docs/threat-model.md",
    "docs/safety-case.md",
    "postman/Sentinel_UAS_Assurance.postman_collection.json",
    "postman/Sentinel_UAS_Local.postman_environment.json",
]

CSV_KEYS = {
    "qa/requirements.csv": "requirement_id",
    "qa/traceability.csv": "trace_id",
    "qa/risk-register.csv": "risk_id",
    "qa/fmea.csv": "fmea_id",
    "qa/test-cases.csv": "test_case_id",
    "qa/control-mapping.csv": "mapping_id",
}

EXPECTED_HEADERS = {
    "qa/requirements.csv": {
        "requirement_id",
        "area",
        "requirement",
        "priority",
        "verification_method",
        "acceptance_criteria",
        "source",
    },
    "qa/traceability.csv": {
        "trace_id",
        "requirement_id",
        "test_id",
        "evidence",
        "level",
        "automation",
        "status",
    },
    "qa/risk-register.csv": {
        "risk_id",
        "category",
        "scenario",
        "impact",
        "likelihood",
        "detectability",
        "score",
        "controls",
        "owner",
        "status",
        "residual_risk",
    },
    "qa/fmea.csv": {
        "fmea_id",
        "item",
        "failure_mode",
        "effect",
        "severity",
        "occurrence",
        "detection",
        "rpn",
        "current_controls",
        "verification",
        "owner",
    },
    "qa/test-cases.csv": {
        "test_case_id",
        "title",
        "requirement_id",
        "type",
        "priority",
        "preconditions",
        "steps",
        "expected_result",
        "automation",
        "status",
        "tags",
    },
    "qa/control-mapping.csv": {
        "mapping_id",
        "nist_csf_function",
        "owasp_api_theme",
        "control_objective",
        "evidence",
        "status",
    },
}

MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def read_csv(relative_path: str) -> tuple[list[dict[str, str]], list[str]]:
    path = ROOT / relative_path
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        return list(reader), headers


def validate_csv(relative_path: str, key: str) -> tuple[int, list[str]]:
    rows, headers = read_csv(relative_path)
    errors: list[str] = []
    if not rows:
        errors.append(f"{relative_path} has no data rows")
        return 0, errors

    expected = EXPECTED_HEADERS[relative_path]
    missing_headers = sorted(expected - set(headers))
    if missing_headers:
        errors.append(f"{relative_path} is missing columns: {', '.join(missing_headers)}")
        return len(rows), errors

    values = [row[key].strip() for row in rows]
    if any(not value for value in values):
        errors.append(f"{relative_path} contains a blank {key}")
    duplicates = sorted(value for value, count in Counter(values).items() if count > 1)
    if duplicates:
        errors.append(f"{relative_path} has duplicate {key}: {', '.join(duplicates)}")

    for row_number, row in enumerate(rows, start=2):
        blank_fields = sorted(field for field in expected if not row.get(field, "").strip())
        if blank_fields:
            errors.append(
                f"{relative_path}:{row_number} has blank fields: {', '.join(blank_fields)}"
            )
    return len(rows), errors


def validate_traceability() -> list[str]:
    errors: list[str] = []
    requirements, _ = read_csv("qa/requirements.csv")
    tests, _ = read_csv("qa/test-cases.csv")
    links, _ = read_csv("qa/traceability.csv")
    requirement_ids = {row["requirement_id"] for row in requirements}
    test_ids = {row["test_case_id"] for row in tests}

    for row in tests:
        if row["requirement_id"] not in requirement_ids:
            errors.append(
                f"{row['test_case_id']} references unknown requirement {row['requirement_id']}"
            )

    linked_requirements: set[str] = set()
    linked_tests: set[str] = set()
    for row in links:
        requirement_id = row["requirement_id"]
        test_id = row["test_id"]
        if requirement_id not in requirement_ids:
            errors.append(f"{row['trace_id']} references unknown requirement {requirement_id}")
        else:
            linked_requirements.add(requirement_id)
        if test_id not in test_ids:
            errors.append(f"{row['trace_id']} references unknown test case {test_id}")
        else:
            linked_tests.add(test_id)
        errors.extend(validate_evidence_reference(row["trace_id"], row["evidence"]))

    for requirement_id in sorted(requirement_ids - linked_requirements):
        errors.append(f"Requirement {requirement_id} has no traceability evidence")
    for test_id in sorted(test_ids - linked_tests):
        errors.append(f"Test case {test_id} has no traceability link")
    return errors


def validate_evidence_reference(owner: str, reference: str) -> list[str]:
    errors: list[str] = []
    path_text, separator, symbol = reference.partition("::")
    path_text = path_text.split("#", maxsplit=1)[0].strip()
    path = ROOT / path_text
    if not path.is_file():
        return [f"{owner} evidence path does not exist: {path_text}"]

    if separator and path.suffix == ".py":
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            return [f"{owner} evidence file has invalid Python syntax: {exc}"]
        names = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        }
        if symbol not in names:
            errors.append(f"{owner} evidence symbol does not exist: {reference}")
    return errors


def validate_control_mapping() -> list[str]:
    rows, _ = read_csv("qa/control-mapping.csv")
    errors: list[str] = []
    for row in rows:
        references = [item.strip() for item in row["evidence"].split(";") if item.strip()]
        for reference in references:
            errors.extend(validate_evidence_reference(row["mapping_id"], reference))
    return errors


def validate_fmea_math() -> list[str]:
    rows, _ = read_csv("qa/fmea.csv")
    errors: list[str] = []
    for row in rows:
        expected = int(row["severity"]) * int(row["occurrence"]) * int(row["detection"])
        if int(row["rpn"]) != expected:
            errors.append(f"{row['fmea_id']} RPN is {row['rpn']} but should be {expected}")
    return errors


def validate_json_assets() -> list[str]:
    errors: list[str] = []
    json_paths = sorted((ROOT / "postman").glob("*.json"))
    json_paths.extend(sorted((ROOT / "test-data").glob("*.json")))
    for path in json_paths:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid JSON in {path.relative_to(ROOT)}: {exc}")

    for path in sorted((ROOT / "test-data").glob("*.jsonl")):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            try:
                json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(
                    f"Invalid JSONL in {path.relative_to(ROOT)}:{line_number}: {exc}"
                )
    return errors


def validate_internal_markdown_links() -> list[str]:
    errors: list[str] = []
    for path in sorted(ROOT.rglob("*.md")):
        if any(part.startswith(".") and part not in {".github"} for part in path.parts):
            continue
        for target in MARKDOWN_LINK.findall(path.read_text(encoding="utf-8")):
            clean_target = target.split("#", maxsplit=1)[0]
            if not clean_target or clean_target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (path.parent / clean_target).resolve()
            if not resolved.exists():
                errors.append(
                    f"{path.relative_to(ROOT)} has a broken internal link: {clean_target}"
                )
    return errors


def main() -> int:
    errors: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (ROOT / relative_path).is_file():
            errors.append(f"Missing required file: {relative_path}")

    counts: dict[str, int] = {}
    for relative_path, key in CSV_KEYS.items():
        if (ROOT / relative_path).is_file():
            count, csv_errors = validate_csv(relative_path, key)
            counts[relative_path] = count
            errors.extend(csv_errors)

    if not errors:
        errors.extend(validate_traceability())
        errors.extend(validate_control_mapping())
        errors.extend(validate_fmea_math())
    errors.extend(validate_json_assets())
    errors.extend(validate_internal_markdown_links())

    if errors:
        print("Repository validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Repository validation passed.")
    for relative_path, count in counts.items():
        print(f"- {relative_path}: {count} rows")
    print("- Cross-references, evidence paths, JSON assets, FMEA math, and links: valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
