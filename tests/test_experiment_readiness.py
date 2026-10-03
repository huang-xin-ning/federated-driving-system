"""Tests for the consolidated experiment preflight gate."""

from __future__ import annotations

import unittest

from federated_driving.experiment_plan import ExperimentPlan
from federated_driving.experiment_readiness import assess_experiment_readiness
from federated_driving.manifest import ManifestSummary
from federated_driving.task_spec import TaskSpec


class ExperimentReadinessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.task = TaskSpec(
            "binary-task",
            "DMD",
            {"safe": "safe_drive", "drink": "distraction"},
            (),
            "driver_id",
            3,
            "disjoint driver groups",
        )

    def plan(self, status: str = "authorized", minimum_clients: int = 2) -> ExperimentPlan:
        return ExperimentPlan(
            "demo",
            "binary-task",
            "v1",
            "sha256:example",
            status,
            7,
            minimum_clients,
            "test only",
        )

    def test_allows_five_group_authorized_plan(self) -> None:
        summary = ManifestSummary(
            10,
            {"safe_drive": 5, "distraction": 5},
            ("a", "b", "c", "d", "e"),
        )

        report = assess_experiment_readiness(summary, self.task, self.plan())

        self.assertTrue(report.ready)
        self.assertEqual(report.reasons, ())

    def test_blocks_pending_authorization_and_insufficient_groups(self) -> None:
        summary = ManifestSummary(
            10,
            {"safe_drive": 5, "distraction": 5},
            ("a",),
        )

        report = assess_experiment_readiness(summary, self.task, self.plan("pending_authorization"))

        self.assertFalse(report.ready)
        self.assertIn("data use status is pending_authorization, not authorized", report.reasons)
        self.assertIn("task requires 3 driver groups, found 1", report.reasons)

    def test_blocks_three_groups_when_two_clients_are_required(self) -> None:
        summary = ManifestSummary(
            10,
            {"safe_drive": 5, "distraction": 5},
            ("a", "b", "c"),
        )

        report = assess_experiment_readiness(summary, self.task, self.plan())

        self.assertFalse(report.ready)
        self.assertIn("requires at least 2 training driver groups, found 1", report.reasons)

    def test_blocks_task_mismatch(self) -> None:
        summary = ManifestSummary(
            10,
            {"safe_drive": 5, "distraction": 5},
            ("a", "b", "c", "d", "e"),
        )
        plan = ExperimentPlan("demo", "wrong-task", "v1", "sha256:x", "authorized", 7, 2, "test")

        report = assess_experiment_readiness(summary, self.task, plan)

        self.assertFalse(report.ready)
        self.assertIn("experiment task wrong-task does not match task spec binary-task", report.reasons)
