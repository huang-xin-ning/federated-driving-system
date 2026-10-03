#!/usr/bin/env python3
"""Run a synthetic FedAvg arithmetic demonstration without training."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from federated_driving.domain import ModelUpdate
from federated_driving.fedavg import NumericUpdate, aggregate_fedavg


def main() -> int:
    updates = (
        NumericUpdate(ModelUpdate("client-001", "synthetic-v0", 10, {}), (1.0, 2.0)),
        NumericUpdate(ModelUpdate("client-002", "synthetic-v0", 30, {}), (3.0, 6.0)),
    )
    result = aggregate_fedavg(updates)
    print(
        json.dumps(
            {
                "base_model_version": result.summary.base_model_version,
                "participant_count": result.summary.participant_count,
                "total_sample_count": result.summary.total_sample_count,
                "aggregated_synthetic_vector": result.vector,
                "training": "NOT STARTED",
                "notice": "This is arithmetic over hard-coded synthetic vectors, not model training.",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
