"""Tests for project foundations; runs with Python's standard library."""

from __future__ import annotations

import unittest

from federated_driving.domain import DataUseStatus, ModelUpdate, ProjectConfig


class DomainTests(unittest.TestCase):
    def test_pending_data_cannot_train(self) -> None:
        config = ProjectConfig(
            project_name="demo",
            data_use_status=DataUseStatus.PENDING_AUTHORIZATION,
            model_version="untrained",
        )
        self.assertFalse(config.training_is_permitted())

    def test_model_update_requires_positive_sample_count(self) -> None:
        with self.assertRaises(ValueError):
            ModelUpdate("client-a", "v0", 0, {})


if __name__ == "__main__":
    unittest.main()
