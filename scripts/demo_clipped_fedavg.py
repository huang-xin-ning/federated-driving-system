#!/usr/bin/env python3
"""Demonstrate synthetic clipping followed by FedAvg without training."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from federated_driving.clipped_fedavg import aggregate_clipped_fedavg
from federated_driving.domain import ModelUpdate
from federated_driving.fedavg import NumericUpdate


def main() -> int:
    updates = (
        NumericUpdate(ModelUpdate("client-001", "synthetic-v0", 10, {}), (3.0, 4.0)),
        NumericUpdate(ModelUpdate("client-002", "synthetic-v0", 30, {}), (1.0, 0.0)),
    )
    result = aggregate_clipped_fedavg(updates, maximum_norm=2.0)
    print(
        json.dumps(
            {
                "maximum_norm": result.maximum_norm,
                "clipped_client_count": result.clipped_client_count,
                "aggregated_synthetic_vector": result.aggregation.vector,
                "participant_count": result.aggregation.summary.participant_count,
                "training": "NOT STARTED",
                "notice": "Synthetic arithmetic demonstration only; not differential privacy or secure aggregation.",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
