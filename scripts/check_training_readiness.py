#!/usr/bin/env python3
"""Evaluate local manifest readiness without starting a training run."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from federated_driving.manifest import load_manifest, summarize_manifest
from federated_driving.readiness import assess_readiness
from federated_driving.task_spec import load_task_spec


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: .venv/bin/python scripts/check_training_readiness.py <manifest.csv> <task-spec.json>", file=sys.stderr)
        return 2
    report = assess_readiness(
        summarize_manifest(load_manifest(sys.argv[1])),
        load_task_spec(sys.argv[2]),
    )
    print(f"ready_for_grouped_training: {report.ready_for_grouped_training}")
    print(f"reasons: {report.reasons or ('none',)}")
    print("Training: NOT STARTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
