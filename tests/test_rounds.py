"""Tests for non-sensitive federated round validation."""

from __future__ import annotations

import unittest

from federated_driving.domain import ModelUpdate
from federated_driving.rounds import validate_round


def update(client_id: str, version: str = "v0", samples: int = 10) -> ModelUpdate:
    return ModelUpdate(client_id, version, samples, {"loss": 0.5})


class RoundValidationTests(unittest.TestCase):
    def test_summary_counts_clients_and_samples(self) -> None:
        summary = validate_round([update("client-a", samples=10), update("client-b", samples=20)])
        self.assertEqual(summary.base_model_version, "v0")
        self.assertEqual(summary.participant_count, 2)
        self.assertEqual(summary.total_sample_count, 30)

    def test_rejects_mixed_model_versions(self) -> None:
        with self.assertRaisesRegex(ValueError, "same base_model_version"):
            validate_round([update("client-a", "v0"), update("client-b", "v1")])

    def test_rejects_duplicate_client(self) -> None:
        with self.assertRaisesRegex(ValueError, "only one update"):
            validate_round([update("client-a"), update("client-a")])


if __name__ == "__main__":
    unittest.main()
