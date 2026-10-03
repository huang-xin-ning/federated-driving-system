"""Synthetic clipped FedAvg composition for unit-tested arithmetic."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .fedavg import FedAvgResult, NumericUpdate, aggregate_fedavg
from .update_clipping import clip_l2


@dataclass(frozen=True)
class ClippedFedAvgResult:
    """Aggregation result plus non-sensitive clipping diagnostics."""

    aggregation: FedAvgResult
    maximum_norm: float
    clipped_client_count: int


def aggregate_clipped_fedavg(
    updates: Sequence[NumericUpdate], maximum_norm: float
) -> ClippedFedAvgResult:
    """Clip each synthetic vector, then apply sample-count-weighted FedAvg.

    This composes arithmetic primitives only. It does not train models or
    constitute differential privacy, secure aggregation, or encrypted transport.
    """
    clipped_updates: list[NumericUpdate] = []
    clipped_client_count = 0
    for update in updates:
        clipped = clip_l2(update.vector, maximum_norm)
        if clipped.was_clipped:
            clipped_client_count += 1
        clipped_updates.append(NumericUpdate(update.metadata, clipped.vector))
    return ClippedFedAvgResult(
        aggregation=aggregate_fedavg(tuple(clipped_updates)),
        maximum_norm=maximum_norm,
        clipped_client_count=clipped_client_count,
    )
