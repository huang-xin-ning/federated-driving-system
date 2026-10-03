#!/usr/bin/env python3
"""Print a simulated federated client plan without starting training."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from federated_driving.client_plan import plan_federated_clients
from federated_driving.group_split import plan_group_split
from federated_driving.manifest import load_manifest, summarize_manifest
from federated_driving.task_spec import load_task_spec


def main() -> int:
    if len(sys.argv) not in (4, 5):
        print(
            "Usage: .venv/bin/python scripts/plan_federated_clients.py "
            "<manifest.csv> <task-spec.json> <integer-seed> [minimum-clients]",
            file=sys.stderr,
        )
        return 2
    try:
        rows = load_manifest(sys.argv[1])
        spec = load_task_spec(sys.argv[2])
        seed = int(sys.argv[3])
        minimum_clients = int(sys.argv[4]) if len(sys.argv) == 5 else 2
        groups = summarize_manifest(rows).driver_ids
        if len(groups) < spec.minimum_distinct_groups:
            raise ValueError(f"task requires {spec.minimum_distinct_groups} driver groups, found {len(groups)}")
        client_plan = plan_federated_clients(
            plan_group_split(groups, seed), minimum_clients
        )
    except ValueError as error:
        print(f"Cannot plan federated clients: {error}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "clients": [
                    {"client_id": client.client_id, "driver_ids": client.driver_ids}
                    for client in client_plan.clients
                ],
                "validation_groups": client_plan.validation_groups,
                "test_groups": client_plan.test_groups,
                "training": "NOT STARTED",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
