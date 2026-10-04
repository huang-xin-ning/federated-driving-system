#!/usr/bin/env python3
"""Demonstrate metrics with hard-coded synthetic labels, without training."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from federated_driving.classification_metrics import binary_metrics


def main() -> int:
    result = binary_metrics(
        ("safe_drive", "distraction", "distraction", "safe_drive"),
        ("safe_drive", "distraction", "safe_drive", "safe_drive"),
        ("safe_drive", "distraction"),
    )
    print(json.dumps({
        "labels": result.labels,
        "confusion_matrix": result.confusion_matrix,
        "accuracy": result.accuracy,
        "precision_for_distraction": result.precision,
        "recall_for_distraction": result.recall,
        "f1_for_distraction": result.f1,
        "training": "NOT STARTED",
        "notice": "Synthetic labels only; this is not a model evaluation result.",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
