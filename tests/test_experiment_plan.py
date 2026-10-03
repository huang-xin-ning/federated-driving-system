"""Tests for reproducible experiment-plan metadata."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from federated_driving.experiment_plan import load_experiment_plan


class ExperimentPlanTests(unittest.TestCase):
    def payload(self) -> dict[str, object]:
        return {
            "experiment_name": "demo",
            "task_name": "binary-task",
            "dataset_version": "v1",
            "manifest_identifier": "sha256:example",
            "data_use_status": "pending_authorization",
            "split_seed": 42,
            "minimum_federated_clients": 2,
            "notes": "metadata only",
        }

    def test_loads_pending_authorization_plan(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.json"
            path.write_text(json.dumps(self.payload()), encoding="utf-8")
            plan = load_experiment_plan(path)

        self.assertEqual(plan.split_seed, 42)
        self.assertFalse(plan.training_permitted_by_data_status)

    def test_accepts_authorized_plan(self) -> None:
        payload = self.payload()
        payload["data_use_status"] = "authorized"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            plan = load_experiment_plan(path)

        self.assertTrue(plan.training_permitted_by_data_status)

    def test_rejects_single_federated_client(self) -> None:
        payload = self.payload()
        payload["minimum_federated_clients"] = 1
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "minimum_federated_clients"):
                load_experiment_plan(path)
