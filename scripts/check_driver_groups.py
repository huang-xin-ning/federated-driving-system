#!/usr/bin/env python3
"""Check whether DMD metadata supports driver-grouped evaluation."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from federated_driving.dmd_groups import grouped_split_is_feasible, inspect_driver_groups
from federated_driving.task_spec import load_task_spec


def main() -> int:
    if len(sys.argv) != 3:
        print(
            "Usage: .venv/bin/python scripts/check_driver_groups.py <metadata-dir> <task-spec.json>",
            file=sys.stderr,
        )
        return 2

    coverage = inspect_driver_groups(sys.argv[1])
    spec = load_task_spec(sys.argv[2])
    required = spec.minimum_distinct_groups
    print(f"annotation_file_count: {coverage.annotation_file_count}")
    print(f"driver_ids: {coverage.driver_ids}")
    print(f"distinct_driver_count: {coverage.distinct_driver_count}")
    print(f"minimum_distinct_groups: {required}")
    print(f"grouped_split_feasible: {grouped_split_is_feasible(coverage, required)}")
    print("Video extraction: NOT PERFORMED")
    print("Training: NOT STARTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
