"""Write disjoint local manifests after an approved group split plan."""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .group_split import GroupSplitPlan
from .manifest import ManifestRow


@dataclass(frozen=True)
class SplitManifestSummary:
    """Non-sensitive summary of one split manifest."""

    row_count: int
    driver_ids: tuple[str, ...]
    label_counts: Mapping[str, int]


def partition_rows(
    rows: tuple[ManifestRow, ...], plan: GroupSplitPlan
) -> Mapping[str, tuple[ManifestRow, ...]]:
    """Assign every manifest row to exactly one driver-level partition."""
    groups_by_partition = {
        "train": set(plan.train_groups),
        "validation": set(plan.validation_groups),
        "test": set(plan.test_groups),
    }
    if len(set(plan.all_groups)) != len(plan.all_groups):
        raise ValueError("split plan contains overlapping driver groups")

    partitions: dict[str, list[ManifestRow]] = {name: [] for name in groups_by_partition}
    for row in rows:
        matches = [name for name, groups in groups_by_partition.items() if row.driver_id in groups]
        if len(matches) != 1:
            raise ValueError(f"driver group is not assigned exactly once: {row.driver_id}")
        partitions[matches[0]].append(row)
    return {name: tuple(items) for name, items in partitions.items()}


def validate_split_coverage(
    partitions: Mapping[str, tuple[ManifestRow, ...]], target_labels: tuple[str, ...]
) -> Mapping[str, SplitManifestSummary]:
    """Require each future split to contain every requested task label."""
    required = set(target_labels)
    summaries: dict[str, SplitManifestSummary] = {}
    for name in ("train", "validation", "test"):
        rows = partitions.get(name, ())
        labels = Counter(row.target_label for row in rows)
        missing = required - set(labels)
        if not rows:
            raise ValueError(f"{name} split contains no samples")
        if missing:
            raise ValueError(f"{name} split is missing target labels: {', '.join(sorted(missing))}")
        summaries[name] = SplitManifestSummary(
            row_count=len(rows),
            driver_ids=tuple(sorted({row.driver_id for row in rows})),
            label_counts=dict(sorted(labels.items())),
        )
    return summaries


def write_split_manifests(
    partitions: Mapping[str, tuple[ManifestRow, ...]], output_directory: str | Path
) -> Mapping[str, Path]:
    """Write local CSV manifests after coverage has been validated."""
    destination = Path(output_directory)
    destination.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    fieldnames = (
        "session_path",
        "annotation_file",
        "video_filename",
        "driver_id",
        "frame_index",
        "target_label",
    )
    for name in ("train", "validation", "test"):
        path = destination / f"{name}.csv"
        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for row in partitions[name]:
                writer.writerow(
                    {
                        "session_path": row.session_path,
                        "annotation_file": row.annotation_file,
                        "video_filename": row.video_filename,
                        "driver_id": row.driver_id,
                        "frame_index": row.frame_index,
                        "target_label": row.target_label,
                    }
                )
        paths[name] = path
    return paths
