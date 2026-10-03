"""Tests for candidate-frame planning from DMD metadata."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from federated_driving.sample_index import plan_sample_index
from federated_driving.task_spec import load_task_spec


class SampleIndexTests(unittest.TestCase):
    def test_counts_sampled_frames_and_excludes_conflicts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            task_path = root / "task.json"
            task_path.write_text(
                json.dumps(
                    {
                        "task_name": "demo",
                        "source_dataset": "DMD",
                        "label_mapping": {"safe": "safe_drive", "drink": "distraction"},
                        "excluded_source_labels": [],
                        "split_policy": {
                            "group_by": "driver_id",
                            "minimum_distinct_groups": 3,
                            "note": "separate groups",
                        },
                    }
                ),
                encoding="utf-8",
            )
            (root / "record_rgb_ann_distraction.json").write_text(
                json.dumps(
                    {
                        "openlabel": {
                            "actions": {
                                "safe": {"type": "safe", "frame_intervals": [{"frame_start": 0, "frame_end": 9}]},
                                "drink": {"type": "drink", "frame_intervals": [{"frame_start": 6, "frame_end": 14}]},
                                "short": {"type": "safe", "frame_intervals": [{"frame_start": 20, "frame_end": 20}]},
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            plan = plan_sample_index(
                root, load_task_spec(task_path), frame_stride=3, minimum_interval_frames=2
            )

        self.assertEqual(plan.candidate_counts, {"distraction": 1, "safe_drive": 2})
        self.assertEqual(plan.conflicting_frame_count, 2)
        self.assertEqual(plan.ignored_short_interval_count, 1)
