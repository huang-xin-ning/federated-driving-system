"""Tests for JSON configuration validation."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from federated_driving.config import load_project_config
from federated_driving.domain import DataUseStatus


class ConfigTests(unittest.TestCase):
    def test_loads_pending_authorization_config(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "config.json"
            path.write_text(
                json.dumps(
                    {
                        "project_name": "demo",
                        "data_use_status": "pending_authorization",
                        "model_version": "untrained",
                    }
                ),
                encoding="utf-8",
            )
            config = load_project_config(path)

        self.assertEqual(config.data_use_status, DataUseStatus.PENDING_AUTHORIZATION)
        self.assertFalse(config.training_is_permitted())

    def test_rejects_unknown_data_status(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "config.json"
            path.write_text(
                '{"project_name":"demo","data_use_status":"unknown","model_version":"v0"}',
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                load_project_config(path)


if __name__ == "__main__":
    unittest.main()
