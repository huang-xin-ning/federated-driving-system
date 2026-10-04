#!/usr/bin/env python3
"""Check all metadata gates before a future federated training experiment."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from federated_driving.experiment_plan import load_experiment_plan
from federated_driving.experiment_readiness import assess_experiment_readiness
from federated_driving.manifest import load_manifest
from federated_driving.task_spec import load_task_spec


def main() -> int:
    if len(sys.argv) != 4:
        print(
            "Usage: .venv/bin/python scripts/check_experiment_readiness.py "
            "<manifest.csv> <task-spec.json> <experiment-plan.json>",
            file=sys.stderr,
        )
        return 2
    report = assess_experiment_readiness(
        load_manifest(sys.argv[1]),
        load_task_spec(sys.argv[2]),
        load_experiment_plan(sys.argv[3]),
    )
    print(f"ready_for_experiment: {report.ready}")
    print(f"reasons: {report.reasons or ('none',)}")
    print("Training: NOT STARTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
