"""Tests for writing disjoint driver-level split manifests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from federated_driving.group_split import GroupSplitPlan
from federated_driving.manifest import ManifestRow
from federated_driving.split_manifest import (
    partition_rows,
    validate_split_coverage,
    write_split_manifests,
)


def row(driver_id: str, label: str, frame: int) -> ManifestRow:
    return ManifestRow("s1", "a.json", "a.mp4", driver_id, frame, label)


class SplitManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.plan = GroupSplitPlan(("a",), ("b",), ("c",), 42)
        self.rows = (
            row("a", "safe_drive", 1),
            row("a", "distraction", 2),
            row("b", "safe_drive", 3),
            row("b", "distraction", 4),
            row("c", "safe_drive", 5),
            row("c", "distraction", 6),
        )

    def test_partitions_rows_without_driver_overlap(self) -> None:
        partitions = partition_rows(self.rows, self.plan)

        self.assertEqual({item.driver_id for item in partitions["train"]}, {"a"})
        self.assertEqual({item.driver_id for item in partitions["validation"]}, {"b"})
        self.assertEqual({item.driver_id for item in partitions["test"]}, {"c"})

    def test_rejects_unassigned_driver(self) -> None:
        with self.assertRaisesRegex(ValueError, "not assigned exactly once"):
            partition_rows(self.rows + (row("outside", "safe_drive", 7),), self.plan)

    def test_requires_each_split_to_have_task_labels(self) -> None:
        partitions = partition_rows(self.rows, self.plan)
        summaries = validate_split_coverage(partitions, ("safe_drive", "distraction"))

        self.assertEqual(summaries["train"].label_counts, {"distraction": 1, "safe_drive": 1})
        with self.assertRaisesRegex(ValueError, "validation split is missing"):
            validate_split_coverage(
                {**partitions, "validation": (row("b", "safe_drive", 3),)},
                ("safe_drive", "distraction"),
            )

    def test_writes_local_csv_manifests(self) -> None:
        partitions = partition_rows(self.rows, self.plan)
        validate_split_coverage(partitions, ("safe_drive", "distraction"))
        with tempfile.TemporaryDirectory() as directory:
            paths = write_split_manifests(partitions, directory)
            train_text = paths["train"].read_text(encoding="utf-8")

        self.assertIn("driver_id", train_text)
        self.assertIn(",a,1,safe_drive", train_text)
