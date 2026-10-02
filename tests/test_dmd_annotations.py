"""Tests for read-only DMD OpenLABEL metadata inspection."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from federated_driving.dmd_annotations import inspect_annotation, inspect_annotation_directory


def write_annotation(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "openlabel": {
                    "objects": {"driver-1": {"type": "driver"}},
                    "frames": {"0": {}, "1": {}, "2": {}, "3": {}, "4": {}},
                    "actions": {
                        "road": {
                            "type": "gaze_on_road/looking_road",
                            "frame_intervals": [{"frame_start": 0, "frame_end": 4}],
                        },
                        "away": {
                            "type": "gaze_on_road/not_looking_road",
                            "frame_intervals": [{"frame_start": 2, "frame_end": 4}],
                        },
                    },
                }
            }
        ),
        encoding="utf-8",
    )


class DmdAnnotationTests(unittest.TestCase):
    def test_summarizes_action_intervals_and_frames(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "sample.json"
            write_annotation(path)
            summary = inspect_annotation(path)

        self.assertEqual(summary.frame_count, 5)
        self.assertEqual(summary.driver_count, 1)
        self.assertEqual(summary.action_interval_counts["gaze_on_road/looking_road"], 1)
        self.assertEqual(summary.action_frame_counts["gaze_on_road/looking_road"], 5)
        self.assertEqual(summary.action_frame_counts["gaze_on_road/not_looking_road"], 3)

    def test_rejects_reversed_frame_ranges(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "bad.json"
            write_annotation(path)
            data = json.loads(path.read_text(encoding="utf-8"))
            data["openlabel"]["actions"]["road"]["frame_intervals"] = [
                {"frame_start": 4, "frame_end": 3}
            ]
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid frame range"):
                inspect_annotation(path)

    def test_inspects_all_json_files_in_name_order(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            write_annotation(directory / "b.json")
            write_annotation(directory / "a.json")
            summaries = inspect_annotation_directory(directory)

        self.assertEqual([summary.source_name for summary in summaries], ["a.json", "b.json"])
