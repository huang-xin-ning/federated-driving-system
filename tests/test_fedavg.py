"""Tests for framework-independent synthetic FedAvg arithmetic."""

from __future__ import annotations

import unittest

from federated_driving.domain import ModelUpdate
from federated_driving.fedavg import NumericUpdate, aggregate_fedavg


def update(client_id: str, samples: int, vector: tuple[float, ...], version: str = "v0") -> NumericUpdate:
    return NumericUpdate(ModelUpdate(client_id, version, samples, {}), vector)


class FedAvgTests(unittest.TestCase):
    def test_computes_sample_weighted_average(self) -> None:
        result = aggregate_fedavg(
            (
                update("a", 10, (1.0, 2.0)),
                update("b", 30, (3.0, 6.0)),
            )
        )

        self.assertEqual(result.summary.total_sample_count, 40)
        self.assertEqual(result.vector, (2.5, 5.0))

    def test_rejects_single_client(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least two"):
            aggregate_fedavg((update("a", 10, (1.0,)),))

    def test_rejects_mismatched_vector_lengths(self) -> None:
        with self.assertRaisesRegex(ValueError, "same length"):
            aggregate_fedavg((update("a", 10, (1.0,)), update("b", 10, (2.0, 3.0))))

    def test_rejects_non_finite_vector_values(self) -> None:
        with self.assertRaisesRegex(ValueError, "finite"):
            NumericUpdate(ModelUpdate("a", "v0", 1, {}), (float("nan"),))
