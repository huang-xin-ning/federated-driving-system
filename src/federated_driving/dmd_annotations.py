"""Read-only summaries for DMD OpenLABEL annotation metadata."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True)
class AnnotationSummary:
    """Non-sensitive aggregate description of one annotation file."""

    source_name: str
    frame_count: int
    driver_count: int
    action_interval_counts: Mapping[str, int]
    action_frame_counts: Mapping[str, int]


def inspect_annotation(path: str | Path) -> AnnotationSummary:
    """Summarize OpenLABEL actions without reading video or creating samples."""
    source_path = Path(path)
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    try:
        openlabel = payload["openlabel"]
    except KeyError as error:
        raise ValueError(f"{source_path} has no openlabel root") from error
    if not isinstance(openlabel, dict):
        raise ValueError(f"{source_path} has an invalid openlabel root")

    frames = _mapping(openlabel.get("frames", {}), "frames", source_path)
    objects = _mapping(openlabel.get("objects", {}), "objects", source_path)
    actions = _mapping(openlabel.get("actions", {}), "actions", source_path)
    driver_count = sum(
        1 for item in objects.values() if isinstance(item, dict) and item.get("type") == "driver"
    )
    interval_counts: Counter[str] = Counter()
    frame_counts: Counter[str] = Counter()
    for action in actions.values():
        if not isinstance(action, dict):
            continue
        action_type = action.get("type")
        if not isinstance(action_type, str) or not action_type:
            continue
        for interval in action.get("frame_intervals", []):
            if not isinstance(interval, dict):
                raise ValueError(f"{source_path} contains an invalid frame interval")
            start, end = interval.get("frame_start"), interval.get("frame_end")
            if not isinstance(start, int) or not isinstance(end, int) or end < start:
                raise ValueError(f"{source_path} contains an invalid frame range")
            interval_counts[action_type] += 1
            frame_counts[action_type] += end - start + 1

    return AnnotationSummary(
        source_name=source_path.name,
        frame_count=len(frames),
        driver_count=driver_count,
        action_interval_counts=dict(sorted(interval_counts.items())),
        action_frame_counts=dict(sorted(frame_counts.items())),
    )


def inspect_annotation_directory(path: str | Path) -> tuple[AnnotationSummary, ...]:
    """Inspect JSON metadata files below *path* in stable name order."""
    root = Path(path)
    if not root.is_dir():
        raise ValueError(f"annotation directory does not exist: {root}")
    return tuple(inspect_annotation(item) for item in sorted(root.rglob("*.json")))


def _mapping(value: object, field_name: str, source_path: Path) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{source_path} has an invalid {field_name} field")
    return value
