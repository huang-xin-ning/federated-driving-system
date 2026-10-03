#!/usr/bin/env python3
"""Print local manifest coverage without reading images or video."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from federated_driving.manifest import load_manifest, summarize_manifest


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: .venv/bin/python scripts/check_manifest.py <manifest.csv>", file=sys.stderr)
        return 2
    summary = summarize_manifest(load_manifest(sys.argv[1]))
    print(f"row_count: {summary.row_count}")
    print(f"label_counts: {summary.label_counts}")
    print(f"driver_ids: {summary.driver_ids}")
    print("Image loading: NOT PERFORMED")
    print("Training: NOT STARTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
