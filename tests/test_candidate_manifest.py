"""Tests for local candidate-frame manifest generation."""

from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from federated_driving.candidate_manifest import build_candidate_manifest
from federated_driving.task_spec import load_task_spec


class CandidateManifestTests(unittest.TestCase):
    def test_writes_only_non_conflicting_sample_rows(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            task_path = root / "task.json"
            task_path.write_text(json.dumps({"task_name": "demo", "source_dataset": "DMD", "label_mapping": {"safe": "safe_drive", "drink": "distraction"}, "excluded_source_labels": [], "split_policy": {"group_by": "driver_id", "minimum_distinct_groups": 3, "note": "separate groups"}}), encoding="utf-8")
            (root / "session_rgb_ann_distraction.json").write_text(json.dumps({"openlabel": {"objects": {"0": {"type": "driver", "name": "driver-a"}}, "actions": {"safe": {"type": "safe", "frame_intervals": [{"frame_start": 0, "frame_end": 4}]}, "drink": {"type": "drink", "frame_intervals": [{"frame_start": 3, "frame_end": 7}]}}}}), encoding="utf-8")
            output = root / "manifest.csv"
            summary = build_candidate_manifest(root, load_task_spec(task_path), output, video_view="rgb_body", frame_stride=2, minimum_interval_frames=2)
            with output.open(newline="", encoding="utf-8") as file:
                rows = list(csv.DictReader(file))

        self.assertEqual(summary.row_count, 3)
        self.assertEqual(summary.conflicting_frame_count, 1)
        self.assertEqual([row["frame_index"] for row in rows], ["0", "2", "6"])
        self.assertEqual([row["target_label"] for row in rows], ["safe_drive", "safe_drive", "distraction"])
