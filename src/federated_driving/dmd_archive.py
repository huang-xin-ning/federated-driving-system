"""Read-only integrity checks for a DMD tar.gz archive and its annotations."""

from __future__ import annotations

import tarfile
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Iterable


@dataclass(frozen=True)
class ArchiveSummary:
    """Aggregate archive contents without extracting files."""

    session_count: int
    video_count: int
    archive_annotation_count: int
    external_annotation_count: int
    missing_external_annotations: tuple[str, ...]
    external_annotations_not_in_archive: tuple[str, ...]


def inspect_archive(archive_path: str, external_annotation_names: Iterable[str]) -> ArchiveSummary:
    """Compare archive annotation names with externally supplied metadata names."""
    external = set(external_annotation_names)
    archive_annotations: set[str] = set()
    sessions: set[str] = set()
    video_count = 0

    with tarfile.open(archive_path, mode="r:gz") as archive:
        for member in archive:
            if not member.isfile():
                continue
            path = PurePosixPath(member.name)
            if len(path.parts) >= 4:
                sessions.add("/".join(path.parts[:-1]))
            name = path.name
            if name.endswith("_rgb_ann_distraction.json"):
                archive_annotations.add(name)
            elif path.suffix.lower() in {".mp4", ".avi"}:
                video_count += 1

    return ArchiveSummary(
        session_count=len(sessions),
        video_count=video_count,
        archive_annotation_count=len(archive_annotations),
        external_annotation_count=len(external),
        missing_external_annotations=tuple(sorted(archive_annotations - external)),
        external_annotations_not_in_archive=tuple(sorted(external - archive_annotations)),
    )
