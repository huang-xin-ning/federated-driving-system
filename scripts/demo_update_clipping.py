#!/usr/bin/env python3
"""Demonstrate synthetic L2 update clipping without training."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from federated_driving.update_clipping import clip_l2


def main() -> int:
    result = clip_l2((3.0, 4.0), 2.0)
    print(
        json.dumps(
            {
                "input_synthetic_vector": (3.0, 4.0),
                "maximum_norm": 2.0,
                "original_norm": result.original_norm,
                "clipped_vector": result.vector,
                "was_clipped": result.was_clipped,
                "training": "NOT STARTED",
                "notice": "L2 clipping alone is not differential privacy or secure aggregation.",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
