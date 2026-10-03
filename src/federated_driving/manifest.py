"""Validated reader for local frame manifests."""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True)
class ManifestRow:
    session_path: str
    annotation_file: str
    video_filename: str
    driver_id: str
    frame_index: int
    target_label: str


@dataclass(frozen=True)
class ManifestSummary:
    row_count: int
    label_counts: Mapping[str, int]
    driver_ids: tuple[str, ...]


def load_manifest(path: str | Path) -> tuple[ManifestRow, ...]:
    """Load a CSV manifest and validate its minimum schema."""
    source = Path(path)
    with source.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        required = {
            "session_path",
            "annotation_file",
            "video_filename",
            "driver_id",
            "frame_index",
            "target_label",
        }
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("manifest does not contain required columns")
        rows = tuple(_row(item, source) for item in reader)
    return rows


def summarize_manifest(rows: tuple[ManifestRow, ...]) -> ManifestSummary:
    """Return non-sensitive class and driver coverage statistics."""
    return ManifestSummary(
        row_count=len(rows),
        label_counts=dict(sorted(Counter(row.target_label for row in rows).items())),
        driver_ids=tuple(sorted({row.driver_id for row in rows})),
    )


def _row(item: Mapping[str, str], source: Path) -> ManifestRow:
    try:
        frame_index = int(item["frame_index"])
    except (KeyError, ValueError) as error:
        raise ValueError(f"{source} contains an invalid frame_index") from error
    values = (
        item.get("session_path", ""),
        item.get("annotation_file", ""),
        item.get("video_filename", ""),
        item.get("driver_id", ""),
        item.get("target_label", ""),
    )
    if frame_index < 0 or any(not value for value in values):
        raise ValueError(f"{source} contains an incomplete manifest row")
    return ManifestRow(values[0], values[1], values[2], values[3], frame_index, values[4])
