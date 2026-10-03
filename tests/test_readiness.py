"""Tests for the grouped-training readiness gate."""

from __future__ import annotations

import unittest

from federated_driving.manifest import ManifestSummary
from federated_driving.readiness import assess_readiness
from federated_driving.task_spec import TaskSpec


class ReadinessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = TaskSpec(
            "demo", "DMD", {"safe": "safe_drive", "drink": "distraction"}, (), "driver_id", 3, "separate groups"
        )

    def test_blocks_single_driver_manifest(self) -> None:
        report = assess_readiness(
            ManifestSummary(10, {"safe_drive": 5, "distraction": 5}, ("driver-a",)),
            self.spec,
        )
        self.assertFalse(report.ready_for_grouped_training)
        self.assertIn("requires 3 driver groups, found 1", report.reasons)

    def test_allows_complete_three_driver_manifest(self) -> None:
        report = assess_readiness(
            ManifestSummary(10, {"safe_drive": 5, "distraction": 5}, ("a", "b", "c")),
            self.spec,
        )
        self.assertTrue(report.ready_for_grouped_training)
        self.assertEqual(report.reasons, ())
