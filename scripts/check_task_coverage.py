#!/usr/bin/env python3
"""Report task-label coverage in DMD metadata without extracting video."""

from __future__ import annotations

import sys
from dataclasses import asdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from federated_driving.task_coverage import inspect_task_coverage
from federated_driving.task_spec import load_task_spec


def main() -> int:
    if len(sys.argv) != 3:
        print(
            "Usage: .venv/bin/python scripts/check_task_coverage.py <metadata-directory> <task-spec.json>",
            file=sys.stderr,
        )
        return 2

    coverage = inspect_task_coverage(sys.argv[1], load_task_spec(sys.argv[2]))
    for key, value in asdict(coverage).items():
        print(f"{key}: {value}")
    print("Video extraction: NOT PERFORMED")
    print("Training: NOT STARTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
