"""Tests for deterministic driver-level split planning."""

from __future__ import annotations

import unittest

from federated_driving.group_split import plan_group_split


class GroupSplitTests(unittest.TestCase):
    def test_uses_each_group_once(self) -> None:
        plan = plan_group_split(("driver-3", "driver-1", "driver-2", "driver-4"), 42)

        self.assertEqual(set(plan.all_groups), {"driver-1", "driver-2", "driver-3", "driver-4"})
        self.assertEqual(len(plan.all_groups), 4)
        self.assertEqual(len(plan.train_groups), 2)
        self.assertEqual(len(plan.validation_groups), 1)
        self.assertEqual(len(plan.test_groups), 1)

    def test_is_reproducible_for_a_seed(self) -> None:
        self.assertEqual(
            plan_group_split(("a", "b", "c", "d"), 7),
            plan_group_split(("d", "b", "a", "c"), 7),
        )

    def test_rejects_fewer_than_three_groups(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least 3 distinct"):
            plan_group_split(("driver-1",), 42)

    def test_rejects_non_integer_seed(self) -> None:
        with self.assertRaisesRegex(ValueError, "seed must be an integer"):
            plan_group_split(("a", "b", "c"), True)
