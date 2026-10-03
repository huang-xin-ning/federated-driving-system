"""Tests for synthetic clipping followed by FedAvg."""

from __future__ import annotations

import unittest

from federated_driving.clipped_fedavg import aggregate_clipped_fedavg
from federated_driving.domain import ModelUpdate
from federated_driving.fedavg import NumericUpdate


def update(client_id: str, samples: int, vector: tuple[float, ...]) -> NumericUpdate:
    return NumericUpdate(ModelUpdate(client_id, "v0", samples, {}), vector)


class ClippedFedAvgTests(unittest.TestCase):
    def test_clips_before_weighted_average(self) -> None:
        result = aggregate_clipped_fedavg(
            (update("a", 10, (3.0, 4.0)), update("b", 30, (1.0, 0.0))),
            maximum_norm=2.0,
        )

        self.assertEqual(result.clipped_client_count, 1)
        self.assertAlmostEqual(result.aggregation.vector[0], 1.05)
        self.assertAlmostEqual(result.aggregation.vector[1], 0.4)

    def test_reuses_validation_for_mixed_versions(self) -> None:
        first = NumericUpdate(ModelUpdate("a", "v0", 1, {}), (1.0,))
        second = NumericUpdate(ModelUpdate("b", "v1", 1, {}), (1.0,))

        with self.assertRaisesRegex(ValueError, "same base_model_version"):
            aggregate_clipped_fedavg((first, second), maximum_norm=1.0)
