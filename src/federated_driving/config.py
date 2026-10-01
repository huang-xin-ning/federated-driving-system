"""Configuration loading with Python's standard library only."""

from __future__ import annotations

import json
from pathlib import Path

from .domain import DataUseStatus, ProjectConfig


def load_project_config(path: str | Path) -> ProjectConfig:
    """Load and validate a project configuration JSON file."""
    config_path = Path(path)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    return ProjectConfig(
        project_name=str(payload["project_name"]),
        data_use_status=DataUseStatus(payload["data_use_status"]),
        model_version=str(payload["model_version"]),
    )
