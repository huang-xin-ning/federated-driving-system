#!/usr/bin/env python3
"""Print a candidate DMD frame-sampling plan without reading video."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from federated_driving.sample_index import plan_sample_index
from federated_driving.task_spec import load_task_spec


def main() -> int:
    if len(sys.argv) != 4:
        print(
            "Usage: .venv/bin/python scripts/plan_dmd_samples.py <metadata-dir> <task-spec.json> <index-plan.json>",
            file=sys.stderr,
        )
        return 2

    metadata_directory, task_path, plan_path = sys.argv[1:]
    settings = json.loads(Path(plan_path).read_text(encoding="utf-8"))
    plan = plan_sample_index(
        metadata_directory,
        load_task_spec(task_path),
        frame_stride=settings["frame_stride"],
        minimum_interval_frames=settings["minimum_interval_frames"],
    )
    for key, value in asdict(plan).items():
        print(f"{key}: {value}")
    print("Video extraction: NOT PERFORMED")
    print("Training: NOT STARTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
