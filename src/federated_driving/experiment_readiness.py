"""Single preflight gate for a future authorized federated experiment."""

from __future__ import annotations

from dataclasses import dataclass

from .client_plan import plan_federated_clients
from .experiment_plan import ExperimentPlan
from .group_split import plan_group_split
from .manifest import ManifestSummary
from .task_spec import TaskSpec


@dataclass(frozen=True)
class ExperimentReadinessReport:
    """Non-training decision and all unmet experiment prerequisites."""

    ready: bool
    reasons: tuple[str, ...]


def assess_experiment_readiness(
    summary: ManifestSummary, task: TaskSpec, plan: ExperimentPlan
) -> ExperimentReadinessReport:
    """Assess metadata prerequisites without reading videos or training."""
    reasons: list[str] = []
    if not plan.training_permitted_by_data_status:
        reasons.append(f"data use status is {plan.data_use_status}, not authorized")
    if plan.task_name != task.task_name:
        reasons.append(f"experiment task {plan.task_name} does not match task spec {task.task_name}")

    missing_labels = set(task.target_labels) - set(summary.label_counts)
    if missing_labels:
        reasons.append(f"manifest missing target labels: {', '.join(sorted(missing_labels))}")
    if len(summary.driver_ids) < task.minimum_distinct_groups:
        reasons.append(
            f"task requires {task.minimum_distinct_groups} driver groups, found {len(summary.driver_ids)}"
        )
    else:
        try:
            split_plan = plan_group_split(summary.driver_ids, plan.split_seed)
            plan_federated_clients(split_plan, plan.minimum_federated_clients)
        except ValueError as error:
            reasons.append(str(error))

    return ExperimentReadinessReport(not reasons, tuple(reasons))
