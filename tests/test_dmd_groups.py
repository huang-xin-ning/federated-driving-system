"""Tests for driver-group coverage checks."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from federated_driving.dmd_groups import grouped_split_is_feasible, inspect_driver_groups


class DriverGroupTests(unittest.TestCase):
    def test_collects_distinct_driver_names(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for filename, name in (("a", "driver-a"), ("b", "driver-b")):
                (root / f"{filename}_rgb_ann_distraction.json").write_text(
                    json.dumps(
                        {"openlabel": {"objects": {"0": {"type": "driver", "name": name}}}}
                    ),
                    encoding="utf-8",
                )
            coverage = inspect_driver_groups(root)

        self.assertEqual(coverage.driver_ids, ("driver-a", "driver-b"))
        self.assertFalse(grouped_split_is_feasible(coverage, 3))
        self.assertTrue(grouped_split_is_feasible(coverage, 2))

    def test_uses_object_id_when_driver_name_is_empty(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "a_rgb_ann_distraction.json").write_text(
                json.dumps({"openlabel": {"objects": {"driver-7": {"type": "driver", "name": ""}}}}),
                encoding="utf-8",
            )
            coverage = inspect_driver_groups(root)

        self.assertEqual(coverage.driver_ids, ("driver-7",))
