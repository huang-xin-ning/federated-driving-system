"""Interfaces for future federated-learning components."""

from __future__ import annotations

from typing import Protocol, Sequence

from .domain import ModelUpdate


class UpdateAggregator(Protocol):
    """Defines the server boundary without selecting an ML library."""

    def aggregate(self, updates: Sequence[ModelUpdate]) -> str:
        """Validate updates and return the next model version identifier."""
