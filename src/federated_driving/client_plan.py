"""Plan simulated federated clients from disjoint training driver groups."""

from __future__ import annotations

from dataclasses import dataclass

from .group_split import GroupSplitPlan


@dataclass(frozen=True)
class FederatedClient:
    """One future client that owns whole, disjoint driver groups."""

    client_id: str
    driver_ids: tuple[str, ...]


@dataclass(frozen=True)
class FederatedClientPlan:
    """Metadata-only plan for a future federated training experiment."""

    clients: tuple[FederatedClient, ...]
    validation_groups: tuple[str, ...]
    test_groups: tuple[str, ...]


def plan_federated_clients(
    split_plan: GroupSplitPlan, minimum_clients: int = 2
) -> FederatedClientPlan:
    """Assign one training driver group to each simulated client.

    A driver is never shared by clients, validation, or test. This function
    does not access samples, models, gradients, or network resources.
    """
    if isinstance(minimum_clients, bool) or not isinstance(minimum_clients, int) or minimum_clients < 2:
        raise ValueError("minimum_clients must be an integer of at least 2")
    training_groups = split_plan.train_groups
    if len(training_groups) < minimum_clients:
        raise ValueError(
            f"requires at least {minimum_clients} training driver groups, found {len(training_groups)}"
        )
    clients = tuple(
        FederatedClient(f"client-{index:03d}", (driver_id,))
        for index, driver_id in enumerate(training_groups, start=1)
    )
    return FederatedClientPlan(clients, split_plan.validation_groups, split_plan.test_groups)
