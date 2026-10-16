from __future__ import annotations

import json
from pathlib import Path

from sentinel_uas.app import create_app


def main() -> None:
    output = Path("reports/local/openapi.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(create_app().openapi(), indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
