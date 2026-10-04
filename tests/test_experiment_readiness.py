"""Tests for the consolidated experiment preflight gate."""

from __future__ import annotations

import unittest

from federated_driving.experiment_plan import ExperimentPlan
from federated_driving.domain import DataUseStatus
from federated_driving.experiment_readiness import assess_experiment_readiness
from federated_driving.manifest import ManifestRow
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

    def plan(
        self, status: DataUseStatus = DataUseStatus.AUTHORIZED_RESEARCH, minimum_clients: int = 2
    ) -> ExperimentPlan:
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

    def rows(self, labels_by_driver: dict[str, tuple[str, ...]]) -> tuple[ManifestRow, ...]:
        return tuple(
            ManifestRow("session", "annotations.json", "video.mp4", driver, frame, label)
            for driver, labels in labels_by_driver.items()
            for frame, label in enumerate(labels)
        )

    def test_allows_five_group_authorized_plan(self) -> None:
        rows = self.rows({driver: ("safe_drive", "distraction") for driver in "abcde"})

        report = assess_experiment_readiness(rows, self.task, self.plan())

        self.assertTrue(report.ready)
        self.assertEqual(report.reasons, ())

    def test_blocks_pending_authorization_and_insufficient_groups(self) -> None:
        rows = self.rows({"a": ("safe_drive", "distraction")})

        report = assess_experiment_readiness(
            rows, self.task, self.plan(DataUseStatus.PENDING_AUTHORIZATION)
        )

        self.assertFalse(report.ready)
        self.assertIn("data use status is pending_authorization, not authorized for training", report.reasons)
        self.assertIn("task requires 3 driver groups, found 1", report.reasons)

    def test_blocks_three_groups_when_two_clients_are_required(self) -> None:
        rows = self.rows({driver: ("safe_drive", "distraction") for driver in "abc"})

        report = assess_experiment_readiness(rows, self.task, self.plan())

        self.assertFalse(report.ready)
        self.assertIn("requires at least 2 training driver groups, found 1", report.reasons)

    def test_blocks_task_mismatch(self) -> None:
        rows = self.rows({driver: ("safe_drive", "distraction") for driver in "abcde"})
        plan = ExperimentPlan(
            "demo", "wrong-task", "v1", "sha256:x", DataUseStatus.AUTHORIZED_RESEARCH, 7, 2, "test"
        )

        report = assess_experiment_readiness(rows, self.task, plan)

        self.assertFalse(report.ready)
        self.assertIn("experiment task wrong-task does not match task spec binary-task", report.reasons)

    def test_blocks_split_missing_a_label_even_when_manifest_has_both(self) -> None:
        rows = self.rows({
            "a": ("safe_drive", "distraction"),
            "b": ("safe_drive", "distraction"),
            "c": ("safe_drive", "distraction"),
            "d": ("safe_drive", "distraction"),
            "e": ("safe_drive",),
        })

        report = assess_experiment_readiness(rows, self.task, self.plan())

        self.assertFalse(report.ready)
        self.assertTrue(any("missing target labels" in reason for reason in report.reasons))
