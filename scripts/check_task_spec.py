#!/usr/bin/env python3
"""Print a task definition without accessing video or starting training."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from federated_driving.task_spec import load_task_spec


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: .venv/bin/python scripts/check_task_spec.py <task-spec.json>", file=sys.stderr)
        return 2

    spec = load_task_spec(sys.argv[1])
    print(f"Task: {spec.task_name}")
    print(f"Source dataset: {spec.source_dataset}")
    print(f"Target labels: {', '.join(spec.target_labels)}")
    print(f"Mapped source actions: {len(spec.label_mapping)}")
    print(f"Excluded source actions: {', '.join(spec.excluded_source_labels) or 'none'}")
    print(
        f"Split policy: group by {spec.group_by}; "
        f"at least {spec.minimum_distinct_groups} distinct groups required."
    )
    print("Training: NOT STARTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
