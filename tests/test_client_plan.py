"""Tests for simulated federated client planning."""

from __future__ import annotations

import unittest

from federated_driving.client_plan import plan_federated_clients
from federated_driving.group_split import GroupSplitPlan


class ClientPlanTests(unittest.TestCase):
    def test_assigns_each_training_group_to_one_client(self) -> None:
        plan = GroupSplitPlan(("driver-a", "driver-b", "driver-c"), ("driver-d",), ("driver-e",), 9)

        result = plan_federated_clients(plan)

        self.assertEqual(
            result.clients,
            (
                result.clients[0].__class__("client-001", ("driver-a",)),
                result.clients[1].__class__("client-002", ("driver-b",)),
                result.clients[2].__class__("client-003", ("driver-c",)),
            ),
        )
        self.assertEqual(result.validation_groups, ("driver-d",))
        self.assertEqual(result.test_groups, ("driver-e",))

    def test_rejects_insufficient_training_groups(self) -> None:
        plan = GroupSplitPlan(("driver-a",), ("driver-b",), ("driver-c",), 9)

        with self.assertRaisesRegex(ValueError, "requires at least 2 training"):
            plan_federated_clients(plan)

    def test_rejects_invalid_minimum_clients(self) -> None:
        plan = GroupSplitPlan(("driver-a", "driver-b"), ("driver-c",), ("driver-d",), 9)

        with self.assertRaisesRegex(ValueError, "minimum_clients"):
            plan_federated_clients(plan, 1)
