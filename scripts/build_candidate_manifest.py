#!/usr/bin/env python3
"""Build a local DMD candidate-frame CSV without extracting video."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from federated_driving.candidate_manifest import build_candidate_manifest
from federated_driving.task_spec import load_task_spec


def main() -> int:
    if len(sys.argv) != 5:
        print("Usage: .venv/bin/python scripts/build_candidate_manifest.py <metadata-dir> <task-spec.json> <index-plan.json> <output.csv>", file=sys.stderr)
        return 2
    metadata_directory, task_path, plan_path, output_path = sys.argv[1:]
    settings = json.loads(Path(plan_path).read_text(encoding="utf-8"))
    summary = build_candidate_manifest(metadata_directory, load_task_spec(task_path), output_path, video_view=settings["video_view"], frame_stride=settings["frame_stride"], minimum_interval_frames=settings["minimum_interval_frames"])
    print(f"output_path: {summary.output_path}")
    print(f"row_count: {summary.row_count}")
    print(f"conflicting_frame_count: {summary.conflicting_frame_count}")
    print(f"ignored_short_interval_count: {summary.ignored_short_interval_count}")
    print("Video extraction: NOT PERFORMED")
    print("Training: NOT STARTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
