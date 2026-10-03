"""Tests for local manifest validation."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from federated_driving.manifest import load_manifest, summarize_manifest


class ManifestTests(unittest.TestCase):
    def test_loads_and_summarizes_rows(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.csv"
            path.write_text(
                "session_path,annotation_file,video_filename,driver_id,frame_index,target_label\n"
                "s1,a.json,a.mp4,driver-a,2,safe_drive\n"
                "s1,a.json,a.mp4,driver-a,4,distraction\n",
                encoding="utf-8",
            )
            summary = summarize_manifest(load_manifest(path))

        self.assertEqual(summary.row_count, 2)
        self.assertEqual(summary.label_counts, {"distraction": 1, "safe_drive": 1})
        self.assertEqual(summary.driver_ids, ("driver-a",))

    def test_rejects_negative_frame_index(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.csv"
            path.write_text(
                "session_path,annotation_file,video_filename,driver_id,frame_index,target_label\n"
                "s1,a.json,a.mp4,driver-a,-1,safe_drive\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "invalid frame_index|incomplete"):
                load_manifest(path)
