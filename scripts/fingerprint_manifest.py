#!/usr/bin/env python3
"""Print a local reproducibility fingerprint for a validated manifest."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from federated_driving.manifest import load_manifest
from federated_driving.manifest_fingerprint import fingerprint_manifest


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: .venv/bin/python scripts/fingerprint_manifest.py <manifest.csv>", file=sys.stderr)
        return 2
    identifier, summary = fingerprint_manifest(load_manifest(sys.argv[1]))
    print(
        json.dumps(
            {
                "manifest_identifier": identifier,
                "row_count": summary.row_count,
                "driver_ids": summary.driver_ids,
                "label_counts": summary.label_counts,
                "training": "NOT STARTED",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
