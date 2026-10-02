"""Tests for read-only task coverage checks."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from federated_driving.task_coverage import inspect_task_coverage
from federated_driving.task_spec import load_task_spec


class TaskCoverageTests(unittest.TestCase):
    def test_maps_intervals_and_reports_unknown_labels(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            spec_path = root / "task.json"
            spec_path.write_text(
                json.dumps(
                    {
                        "task_name": "demo",
                        "source_dataset": "DMD",
                        "label_mapping": {
                            "driver_actions/safe_drive": "safe_drive",
                            "driver_actions/drinking": "distraction",
                        },
                        "excluded_source_labels": ["driver_actions/unclassified"],
                        "split_policy": {
                            "group_by": "driver_id",
                            "minimum_distinct_groups": 3,
                            "note": "keep groups separate",
                        },
                    }
                ),
                encoding="utf-8",
            )
            (root / "sample_rgb_ann_distraction.json").write_text(
                json.dumps(
                    {
                        "openlabel": {
                            "actions": {
                                "safe": {
                                    "type": "driver_actions/safe_drive",
                                    "frame_intervals": [{"frame_start": 0, "frame_end": 4}],
                                },
                                "drink": {
                                    "type": "driver_actions/drinking",
                                    "frame_intervals": [{"frame_start": 5, "frame_end": 7}],
                                },
                                "unknown": {
                                    "type": "gaze_on_road/looking_road",
                                    "frame_intervals": [{"frame_start": 0, "frame_end": 7}],
                                },
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            coverage = inspect_task_coverage(root, load_task_spec(spec_path))

        self.assertEqual(coverage.annotation_file_count, 1)
        self.assertEqual(coverage.mapped_interval_counts, {"distraction": 1, "safe_drive": 1})
        self.assertEqual(coverage.mapped_frame_counts, {"distraction": 3, "safe_drive": 5})
        self.assertEqual(coverage.unmapped_source_labels, ("gaze_on_road/looking_road",))
