"""Deterministic, leakage-resistant group split planning."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class GroupSplitPlan:
    """Disjoint driver groups reserved for one future experiment."""

    train_groups: tuple[str, ...]
    validation_groups: tuple[str, ...]
    test_groups: tuple[str, ...]
    seed: int

    @property
    def all_groups(self) -> tuple[str, ...]:
        return self.train_groups + self.validation_groups + self.test_groups


def plan_group_split(driver_ids: Iterable[str], seed: int) -> GroupSplitPlan:
    """Reserve whole driver groups for train, validation, and test.

    The function deliberately plans metadata only. It does not read samples,
    write split manifests, or start a training run.
    """
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    groups = tuple(sorted(set(driver_ids)))
    if any(not group for group in groups):
        raise ValueError("driver groups must be non-empty")
    if len(groups) < 3:
        raise ValueError("at least 3 distinct driver groups are required")

    shuffled = list(groups)
    random.Random(seed).shuffle(shuffled)
    return GroupSplitPlan(
        train_groups=tuple(sorted(shuffled[2:])),
        validation_groups=(shuffled[0],),
        test_groups=(shuffled[1],),
        seed=seed,
    )
