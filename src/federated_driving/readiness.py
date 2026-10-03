"""Training-readiness gate for manifest-based experiments."""

from __future__ import annotations

from dataclasses import dataclass

from .manifest import ManifestSummary
from .task_spec import TaskSpec


@dataclass(frozen=True)
class ReadinessReport:
    ready_for_grouped_training: bool
    reasons: tuple[str, ...]


def assess_readiness(summary: ManifestSummary, spec: TaskSpec) -> ReadinessReport:
    """Assess only manifest coverage; it does not start training."""
    reasons: list[str] = []
    if summary.row_count == 0:
        reasons.append("manifest contains no samples")
    missing_labels = set(spec.target_labels) - set(summary.label_counts)
    if missing_labels:
        reasons.append(f"missing target labels: {', '.join(sorted(missing_labels))}")
    if len(summary.driver_ids) < spec.minimum_distinct_groups:
        reasons.append(
            f"requires {spec.minimum_distinct_groups} driver groups, found {len(summary.driver_ids)}"
        )
    return ReadinessReport(not reasons, tuple(reasons))
