"""Tests for task definition validation."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from federated_driving.task_spec import load_task_spec


def payload() -> dict[str, object]:
    return {
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
            "note": "keep drivers separate",
        },
    }


class TaskSpecTests(unittest.TestCase):
    def test_loads_binary_task_and_resolves_labels(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "task.json"
            path.write_text(json.dumps(payload()), encoding="utf-8")
            spec = load_task_spec(path)

        self.assertEqual(spec.target_labels, ("distraction", "safe_drive"))
        self.assertEqual(spec.label_for("driver_actions/drinking"), "distraction")
        self.assertIsNone(spec.label_for("driver_actions/unclassified"))

    def test_rejects_mapped_and_excluded_source_label(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "task.json"
            data = payload()
            data["excluded_source_labels"] = ["driver_actions/drinking"]
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "both mapped and excluded"):
                load_task_spec(path)

    def test_rejects_non_positive_group_requirement(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "task.json"
            data = payload()
            data["split_policy"]["minimum_distinct_groups"] = 0
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "positive integer"):
                load_task_spec(path)
