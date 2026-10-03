"""Read-only candidate-frame planning from DMD action intervals."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .task_spec import TaskSpec


@dataclass(frozen=True)
class SampleIndexPlan:
    """Candidate frame counts derived from labels, without opening video."""

    annotation_file_count: int
    frame_stride: int
    candidate_counts: Mapping[str, int]
    conflicting_frame_count: int
    ignored_short_interval_count: int


def plan_sample_index(
    metadata_directory: str | Path,
    spec: TaskSpec,
    *,
    frame_stride: int,
    minimum_interval_frames: int,
) -> SampleIndexPlan:
    """Plan label-aligned frame indices and exclude conflicting target labels."""
    if frame_stride < 1 or minimum_interval_frames < 1:
        raise ValueError("frame_stride and minimum_interval_frames must be positive")

    root = Path(metadata_directory)
    paths = sorted(root.rglob("*_rgb_ann_distraction.json"))
    if not root.is_dir():
        raise ValueError(f"metadata directory does not exist: {root}")

    counts: Counter[str] = Counter()
    conflicts = 0
    ignored = 0
    for path in paths:
        occupancy: dict[int, set[str]] = {}
        actions = _load_actions(path)
        for action in actions.values():
            if not isinstance(action, dict):
                continue
            target_label = spec.label_for(action.get("type", ""))
            if target_label is None:
                continue
            for interval in action.get("frame_intervals", []):
                start, end = _interval(interval, path)
                if end - start + 1 < minimum_interval_frames:
                    ignored += 1
                    continue
                for frame in range(start, end + 1):
                    occupancy.setdefault(frame, set()).add(target_label)

        for frame, labels in occupancy.items():
            if frame % frame_stride != 0:
                continue
            if len(labels) == 1:
                counts[next(iter(labels))] += 1
            else:
                conflicts += 1

    return SampleIndexPlan(
        annotation_file_count=len(paths),
        frame_stride=frame_stride,
        candidate_counts=dict(sorted(counts.items())),
        conflicting_frame_count=conflicts,
        ignored_short_interval_count=ignored,
    )


def _load_actions(path: Path) -> Mapping[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    try:
        actions = payload["openlabel"]["actions"]
    except KeyError as error:
        raise ValueError(f"{path} has no openlabel actions") from error
    if not isinstance(actions, dict):
        raise ValueError(f"{path} has invalid openlabel actions")
    return actions


def _interval(value: object, path: Path) -> tuple[int, int]:
    if not isinstance(value, dict):
        raise ValueError(f"{path} contains an invalid frame interval")
    start, end = value.get("frame_start"), value.get("frame_end")
    if not isinstance(start, int) or not isinstance(end, int) or end < start:
        raise ValueError(f"{path} contains an invalid frame range")
    return start, end
