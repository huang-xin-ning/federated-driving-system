#!/usr/bin/env python3
"""Inspect a project configuration without starting any training."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from federated_driving.config import load_project_config


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: .venv/bin/python scripts/check_config.py <config.json>", file=sys.stderr)
        return 2

    config = load_project_config(sys.argv[1])
    print(f"Project: {config.project_name}")
    print(f"Data use status: {config.data_use_status.value}")
    print(f"Model version: {config.model_version}")
    print("Training: PERMITTED" if config.training_is_permitted() else "Training: BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
