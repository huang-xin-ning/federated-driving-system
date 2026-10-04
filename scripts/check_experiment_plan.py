#!/usr/bin/env python3
"""Check reproducible experiment metadata without training."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from federated_driving.experiment_plan import load_experiment_plan


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: .venv/bin/python scripts/check_experiment_plan.py <experiment-plan.json>", file=sys.stderr)
        return 2
    plan = load_experiment_plan(sys.argv[1])
    print(f"Experiment: {plan.experiment_name}")
    print(f"Task: {plan.task_name}")
    print(f"Dataset version: {plan.dataset_version}")
    print(f"Manifest identifier: {plan.manifest_identifier}")
    print(f"Split seed: {plan.split_seed}")
    print(f"Minimum federated clients: {plan.minimum_federated_clients}")
    print(f"Data use status: {plan.data_use_status.value}")
    print("Training: NOT STARTED")
    print("Data authorization gate: PASSED" if plan.training_permitted_by_data_status else "Data authorization gate: BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
