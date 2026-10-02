"""Read-only coverage checks between DMD metadata and a task definition."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .task_spec import TaskSpec


@dataclass(frozen=True)
class TaskCoverage:
    """Aggregate mapped action intervals; counts can overlap across action types."""

    annotation_file_count: int
    mapped_interval_counts: Mapping[str, int]
    mapped_frame_counts: Mapping[str, int]
    unmapped_source_labels: tuple[str, ...]


def inspect_task_coverage(metadata_directory: str | Path, spec: TaskSpec) -> TaskCoverage:
    """Summarize task-mapped OpenLABEL action intervals without reading video."""
    root = Path(metadata_directory)
    if not root.is_dir():
        raise ValueError(f"metadata directory does not exist: {root}")

    interval_counts: Counter[str] = Counter()
    frame_counts: Counter[str] = Counter()
    unmapped: set[str] = set()
    paths = sorted(root.rglob("*_rgb_ann_distraction.json"))

    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        try:
            actions = payload["openlabel"]["actions"]
        except KeyError as error:
            raise ValueError(f"{path} has no openlabel actions") from error
        if not isinstance(actions, dict):
            raise ValueError(f"{path} has invalid openlabel actions")

        for action in actions.values():
            if not isinstance(action, dict):
                continue
            source_label = action.get("type")
            if not isinstance(source_label, str) or not source_label:
                continue
            target_label = spec.label_for(source_label)
            if target_label is None:
                if source_label not in spec.excluded_source_labels:
                    unmapped.add(source_label)
                continue
            for interval in action.get("frame_intervals", []):
                if not isinstance(interval, dict):
                    raise ValueError(f"{path} contains an invalid frame interval")
                start, end = interval.get("frame_start"), interval.get("frame_end")
                if not isinstance(start, int) or not isinstance(end, int) or end < start:
                    raise ValueError(f"{path} contains an invalid frame range")
                interval_counts[target_label] += 1
                frame_counts[target_label] += end - start + 1

    return TaskCoverage(
        annotation_file_count=len(paths),
        mapped_interval_counts=dict(sorted(interval_counts.items())),
        mapped_frame_counts=dict(sorted(frame_counts.items())),
        unmapped_source_labels=tuple(sorted(unmapped)),
    )
