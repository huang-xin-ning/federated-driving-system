"""Domain types that do not depend on a training framework."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping


class DataUseStatus(str, Enum):
    """Whether a data source can be used by this project."""

    PENDING_AUTHORIZATION = "pending_authorization"
    AUTHORIZED_RESEARCH = "authorized_research"
    AUTHORIZED_DEPLOYMENT = "authorized_deployment"
    PROHIBITED = "prohibited"

    @property
    def training_allowed(self) -> bool:
        """Training requires explicit authorization."""
        return self in {
            DataUseStatus.AUTHORIZED_RESEARCH,
            DataUseStatus.AUTHORIZED_DEPLOYMENT,
        }


@dataclass(frozen=True)
class ModelUpdate:
    """Metadata for a future client-to-server federated update.

    This type deliberately contains no raw samples or model weights.
    """

    client_id: str
    base_model_version: str
    sample_count: int
    metrics: Mapping[str, float]

    def __post_init__(self) -> None:
        if not self.client_id.strip():
            raise ValueError("client_id must not be empty")
        if self.sample_count <= 0:
            raise ValueError("sample_count must be greater than zero")


@dataclass(frozen=True)
class ProjectConfig:
    """Small, serializable configuration for local development."""

    project_name: str
    data_use_status: DataUseStatus
    model_version: str

    def training_is_permitted(self) -> bool:
        return self.data_use_status.training_allowed
