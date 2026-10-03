"""Framework-independent L2 clipping for synthetic federated update vectors."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt


@dataclass(frozen=True)
class ClippedVector:
    """A synthetic vector and the L2 clipping decision applied to it."""

    vector: tuple[float, ...]
    original_norm: float
    was_clipped: bool


def clip_l2(vector: tuple[float, ...], maximum_norm: float) -> ClippedVector:
    """Clip a finite synthetic vector to a positive L2 norm limit.

    This is an arithmetic building block only. It does not provide differential
    privacy, secure aggregation, encryption, or a production transport layer.
    """
    if not vector:
        raise ValueError("vector must not be empty")
    if not isfinite(maximum_norm) or maximum_norm <= 0:
        raise ValueError("maximum_norm must be a finite positive number")
    if any(not isfinite(value) for value in vector):
        raise ValueError("vector values must be finite")

    original_norm = sqrt(sum(value * value for value in vector))
    if original_norm <= maximum_norm:
        return ClippedVector(vector, original_norm, False)
    scale = maximum_norm / original_norm
    return ClippedVector(tuple(value * scale for value in vector), original_norm, True)
