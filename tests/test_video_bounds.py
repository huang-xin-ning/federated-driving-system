"""Tests for local video-bound candidate filtering."""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from federated_driving.video_bounds import filter_manifest_by_video_bounds


class VideoBoundsTests(unittest.TestCase):
    def test_filters_missing_and_out_of_bounds_rows(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "manifest.csv"
            manifest.write_text(
                "session_path,video_filename,frame_index,target_label\n"
                "s1,video.mp4,3,safe_drive\n"
                "s1,video.mp4,5,distraction\n"
                "s2,missing.mp4,1,safe_drive\n",
                encoding="utf-8",
            )
            video = root / "videos/s1/video.mp4"
            video.parent.mkdir(parents=True)
            video.write_bytes(b"placeholder")
            output = root / "filtered.csv"
            summary = filter_manifest_by_video_bounds(
                manifest, root / "videos", output, frame_counter=lambda _: 5
            )
            with output.open(newline="", encoding="utf-8") as file:
                rows = list(csv.DictReader(file))

        self.assertEqual(summary.kept_row_count, 1)
        self.assertEqual(summary.out_of_bounds_row_count, 1)
        self.assertEqual(summary.missing_video_row_count, 1)
        self.assertEqual(rows[0]["frame_index"], "3")
