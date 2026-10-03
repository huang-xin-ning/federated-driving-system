#!/usr/bin/env python3
"""Print a deterministic driver-level split plan without starting training."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from federated_driving.group_split import plan_group_split
from federated_driving.manifest import load_manifest, summarize_manifest
from federated_driving.task_spec import load_task_spec


def main() -> int:
    if len(sys.argv) != 4:
        print(
            "Usage: .venv/bin/python scripts/plan_group_split.py <manifest.csv> <task-spec.json> <integer-seed>",
            file=sys.stderr,
        )
        return 2
    try:
        seed = int(sys.argv[3])
        summary = summarize_manifest(load_manifest(sys.argv[1]))
        spec = load_task_spec(sys.argv[2])
        if len(summary.driver_ids) < spec.minimum_distinct_groups:
            raise ValueError(
                f"task requires {spec.minimum_distinct_groups} driver groups, found {len(summary.driver_ids)}"
            )
        plan = plan_group_split(summary.driver_ids, seed)
    except ValueError as error:
        print(f"Cannot plan split: {error}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "seed": plan.seed,
                "train_groups": plan.train_groups,
                "validation_groups": plan.validation_groups,
                "test_groups": plan.test_groups,
                "training": "NOT STARTED",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
