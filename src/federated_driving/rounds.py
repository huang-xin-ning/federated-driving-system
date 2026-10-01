"""Safe metadata validation for a future federated aggregation round."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .domain import ModelUpdate


@dataclass(frozen=True)
class AggregationSummary:
    """Non-sensitive summary emitted before a future aggregation step."""

    base_model_version: str
    participant_count: int
    total_sample_count: int


def validate_round(updates: Sequence[ModelUpdate]) -> AggregationSummary:
    """Validate update metadata without accessing weights or raw data."""
    if not updates:
        raise ValueError("at least one update is required")

    expected_version = updates[0].base_model_version
    client_ids = set()
    total_sample_count = 0

    for update in updates:
        if update.base_model_version != expected_version:
            raise ValueError("all updates must use the same base_model_version")
        if update.client_id in client_ids:
            raise ValueError("each client_id may submit only one update per round")
        client_ids.add(update.client_id)
        total_sample_count += update.sample_count

    return AggregationSummary(
        base_model_version=expected_version,
        participant_count=len(updates),
        total_sample_count=total_sample_count,
    )
