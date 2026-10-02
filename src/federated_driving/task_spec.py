"""Validated task definitions for future, authorized experiments."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True)
class TaskSpec:
    """Maps source action types to research labels without reading samples."""

    task_name: str
    source_dataset: str
    label_mapping: Mapping[str, str]
    excluded_source_labels: tuple[str, ...]
    group_by: str
    minimum_distinct_groups: int
    split_note: str

    @property
    def target_labels(self) -> tuple[str, ...]:
        return tuple(sorted(set(self.label_mapping.values())))

    def label_for(self, source_label: str) -> str | None:
        """Return the target label, or None when the source label is excluded."""
        return self.label_mapping.get(source_label)


def load_task_spec(path: str | Path) -> TaskSpec:
    """Load and validate a task specification JSON file."""
    source_path = Path(path)
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    mapping = _string_mapping(payload.get("label_mapping"), "label_mapping")
    excluded = _string_list(payload.get("excluded_source_labels"), "excluded_source_labels")
    split_policy = _mapping(payload.get("split_policy"), "split_policy")
    spec = TaskSpec(
        task_name=_required_string(payload.get("task_name"), "task_name"),
        source_dataset=_required_string(payload.get("source_dataset"), "source_dataset"),
        label_mapping=mapping,
        excluded_source_labels=excluded,
        group_by=_required_string(split_policy.get("group_by"), "split_policy.group_by"),
        minimum_distinct_groups=_positive_integer(
            split_policy.get("minimum_distinct_groups"), "split_policy.minimum_distinct_groups"
        ),
        split_note=_required_string(split_policy.get("note"), "split_policy.note"),
    )
    if not spec.target_labels:
        raise ValueError("label_mapping must define at least one target label")
    if set(spec.label_mapping).intersection(spec.excluded_source_labels):
        raise ValueError("a source label cannot be both mapped and excluded")
    return spec


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return value


def _string_mapping(value: object, name: str) -> Mapping[str, str]:
    mapping = _mapping(value, name)
    if not mapping or any(not isinstance(key, str) or not isinstance(item, str) or not item for key, item in mapping.items()):
        raise ValueError(f"{name} must map non-empty strings to non-empty strings")
    return dict(mapping)


def _string_list(value: object, name: str) -> tuple[str, ...]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise ValueError(f"{name} must be a list of non-empty strings")
    return tuple(value)


def _required_string(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _positive_integer(value: object, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return value
