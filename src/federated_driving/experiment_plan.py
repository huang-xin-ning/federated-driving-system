"""Validated metadata for a future reproducible experiment."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True)
class ExperimentPlan:
    """Records experiment inputs without loading data or training a model."""

    experiment_name: str
    task_name: str
    dataset_version: str
    manifest_identifier: str
    data_use_status: str
    split_seed: int
    minimum_federated_clients: int
    notes: str

    @property
    def training_permitted_by_data_status(self) -> bool:
        return self.data_use_status == "authorized"


def load_experiment_plan(path: str | Path) -> ExperimentPlan:
    """Load a shared experiment-plan template and validate its metadata."""
    source = Path(path)
    payload = json.loads(source.read_text(encoding="utf-8"))
    plan = ExperimentPlan(
        experiment_name=_required_string(payload.get("experiment_name"), "experiment_name"),
        task_name=_required_string(payload.get("task_name"), "task_name"),
        dataset_version=_required_string(payload.get("dataset_version"), "dataset_version"),
        manifest_identifier=_required_string(payload.get("manifest_identifier"), "manifest_identifier"),
        data_use_status=_status(payload.get("data_use_status")),
        split_seed=_integer(payload.get("split_seed"), "split_seed"),
        minimum_federated_clients=_minimum_clients(payload.get("minimum_federated_clients")),
        notes=_required_string(payload.get("notes"), "notes"),
    )
    return plan


def _required_string(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _status(value: object) -> str:
    if value not in {"pending_authorization", "authorized", "prohibited"}:
        raise ValueError("data_use_status must be pending_authorization, authorized, or prohibited")
    return str(value)


def _integer(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    return value


def _minimum_clients(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 2:
        raise ValueError("minimum_federated_clients must be an integer of at least 2")
    return value
