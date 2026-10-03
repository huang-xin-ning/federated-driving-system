#!/usr/bin/env python3
"""Create local train, validation, and test manifests without training."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from federated_driving.group_split import plan_group_split
from federated_driving.manifest import load_manifest, summarize_manifest
from federated_driving.split_manifest import (
    partition_rows,
    validate_split_coverage,
    write_split_manifests,
)
from federated_driving.task_spec import load_task_spec


def main() -> int:
    if len(sys.argv) != 5:
        print(
            "Usage: .venv/bin/python scripts/write_group_split_manifests.py "
            "<manifest.csv> <task-spec.json> <integer-seed> <output-directory>",
            file=sys.stderr,
        )
        return 2
    try:
        rows = load_manifest(sys.argv[1])
        summary = summarize_manifest(rows)
        spec = load_task_spec(sys.argv[2])
        seed = int(sys.argv[3])
        if len(summary.driver_ids) < spec.minimum_distinct_groups:
            raise ValueError(
                f"task requires {spec.minimum_distinct_groups} driver groups, found {len(summary.driver_ids)}"
            )
        plan = plan_group_split(summary.driver_ids, seed)
        partitions = partition_rows(rows, plan)
        summaries = validate_split_coverage(partitions, spec.target_labels)
        paths = write_split_manifests(partitions, sys.argv[4])
    except ValueError as error:
        print(f"Cannot write split manifests: {error}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "seed": seed,
                "files": {name: str(path) for name, path in paths.items()},
                "summaries": {
                    name: {
                        "row_count": summary.row_count,
                        "driver_ids": summary.driver_ids,
                        "label_counts": summary.label_counts,
                    }
                    for name, summary in summaries.items()
                },
                "training": "NOT STARTED",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
