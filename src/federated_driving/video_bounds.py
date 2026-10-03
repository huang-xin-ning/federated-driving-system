"""Filter candidate manifests against actual local video frame bounds."""

from __future__ import annotations

import csv
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class VideoBoundsSummary:
    output_path: Path
    kept_row_count: int
    missing_video_row_count: int
    out_of_bounds_row_count: int


def filter_manifest_by_video_bounds(
    manifest_path: str | Path,
    video_root: str | Path,
    output_path: str | Path,
    *,
    frame_counter: Callable[[Path], int] | None = None,
) -> VideoBoundsSummary:
    """Keep rows whose target video exists and contains the requested frame."""
    source, root, destination = Path(manifest_path), Path(video_root), Path(output_path)
    count_frames = frame_counter or probe_frame_count
    cache: dict[Path, int] = {}
    kept: list[dict[str, str]] = []
    missing = out_of_bounds = 0

    with source.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        fields = reader.fieldnames
        required = {"session_path", "video_filename", "frame_index"}
        if not fields or not required.issubset(fields):
            raise ValueError("manifest does not contain required video-bound fields")
        for row in reader:
            video = root / row["session_path"] / row["video_filename"]
            if not video.is_file():
                missing += 1
                continue
            frame_count = cache.setdefault(video, count_frames(video))
            if int(row["frame_index"]) >= frame_count:
                out_of_bounds += 1
                continue
            kept.append(row)

    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(kept)
    return VideoBoundsSummary(destination, len(kept), missing, out_of_bounds)


def probe_frame_count(video_path: Path) -> int:
    """Read reported video frame count through local FFprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=nb_frames", "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
        capture_output=True,
        check=True,
        text=True,
    )
    try:
        count = int(result.stdout.strip())
    except ValueError as error:
        raise ValueError(f"FFprobe returned no usable frame count for {video_path}") from error
    if count < 1:
        raise ValueError(f"FFprobe returned an invalid frame count for {video_path}")
    return count
