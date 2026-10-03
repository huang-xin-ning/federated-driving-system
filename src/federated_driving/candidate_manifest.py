"""Build local candidate-frame manifests from DMD annotations without reading video."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

from .task_spec import TaskSpec


@dataclass(frozen=True)
class ManifestBuildSummary:
    output_path: Path
    row_count: int
    conflicting_frame_count: int
    ignored_short_interval_count: int


def build_candidate_manifest(metadata_directory: str | Path, spec: TaskSpec, output_path: str | Path, *, video_view: str, frame_stride: int, minimum_interval_frames: int) -> ManifestBuildSummary:
    """Write label-aligned candidate frame rows without extracting video."""
    if not video_view.startswith("rgb_"):
        raise ValueError("video_view must start with rgb_")
    if frame_stride < 1 or minimum_interval_frames < 1:
        raise ValueError("frame_stride and minimum_interval_frames must be positive")
    root = Path(metadata_directory)
    if not root.is_dir():
        raise ValueError(f"metadata directory does not exist: {root}")

    rows: list[tuple[str, str, str, str, int, str]] = []
    conflicts = ignored = 0
    for path in sorted(root.rglob("*_rgb_ann_distraction.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        openlabel = payload.get("openlabel")
        if not isinstance(openlabel, dict):
            raise ValueError(f"{path} has an invalid openlabel root")
        driver_id = _driver_id(openlabel.get("objects"), path)
        actions = openlabel.get("actions")
        if not isinstance(actions, dict):
            raise ValueError(f"{path} has invalid openlabel actions")
        occupancy: dict[int, set[str]] = {}
        session_path = str(path.parent.relative_to(root))
        video_filename = path.name.replace("_rgb_ann_distraction.json", f"_{video_view}.mp4")
        for action in actions.values():
            if not isinstance(action, dict):
                continue
            target = spec.label_for(action.get("type", ""))
            if target is None:
                continue
            for interval in action.get("frame_intervals", []):
                start, end = _interval(interval, path)
                if end - start + 1 < minimum_interval_frames:
                    ignored += 1
                    continue
                for frame in range(start, end + 1):
                    occupancy.setdefault(frame, set()).add(target)
        for frame, labels in sorted(occupancy.items()):
            if frame % frame_stride != 0:
                continue
            if len(labels) != 1:
                conflicts += 1
                continue
            rows.append((session_path, path.name, video_filename, driver_id, frame, next(iter(labels))))

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(("session_path", "annotation_file", "video_filename", "driver_id", "frame_index", "target_label"))
        writer.writerows(rows)
    return ManifestBuildSummary(destination, len(rows), conflicts, ignored)


def _driver_id(objects: object, path: Path) -> str:
    if not isinstance(objects, dict):
        raise ValueError(f"{path} has invalid openlabel objects")
    for object_id, item in objects.items():
        if isinstance(item, dict) and item.get("type") == "driver":
            name = item.get("name")
            return name if isinstance(name, str) and name else str(object_id)
    raise ValueError(f"{path} has no driver object")


def _interval(value: object, path: Path) -> tuple[int, int]:
    if not isinstance(value, dict):
        raise ValueError(f"{path} contains an invalid frame interval")
    start, end = value.get("frame_start"), value.get("frame_end")
    if not isinstance(start, int) or not isinstance(end, int) or end < start:
        raise ValueError(f"{path} contains an invalid frame range")
    return start, end
