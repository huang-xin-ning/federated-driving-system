"""Framework-independent FedAvg arithmetic for synthetic numeric updates."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

from .domain import ModelUpdate
from .rounds import AggregationSummary, validate_round


@dataclass(frozen=True)
class NumericUpdate:
    """Synthetic numeric vector paired with validated federated metadata.

    The vector is for unit-tested arithmetic only. It is not a serialized
    production model, a gradient payload, or a transport protocol.
    """

    metadata: ModelUpdate
    vector: tuple[float, ...]

    def __post_init__(self) -> None:
        if not self.vector:
            raise ValueError("vector must not be empty")
        if any(not isfinite(value) for value in self.vector):
            raise ValueError("vector values must be finite")


@dataclass(frozen=True)
class FedAvgResult:
    """Sample-count-weighted average of synthetic client vectors."""

    summary: AggregationSummary
    vector: tuple[float, ...]


def aggregate_fedavg(updates: Sequence[NumericUpdate]) -> FedAvgResult:
    """Aggregate equal-length synthetic vectors with sample-count weighting."""
    if len(updates) < 2:
        raise ValueError("FedAvg requires at least two client updates")
    summary = validate_round([update.metadata for update in updates])
    expected_length = len(updates[0].vector)
    if any(len(update.vector) != expected_length for update in updates):
        raise ValueError("all update vectors must have the same length")

    values = tuple(
        sum(update.vector[index] * update.metadata.sample_count for update in updates)
        / summary.total_sample_count
        for index in range(expected_length)
    )
    return FedAvgResult(summary, values)
