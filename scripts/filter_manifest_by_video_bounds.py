#!/usr/bin/env python3
"""Filter a local candidate manifest by local video availability and frame count."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from federated_driving.video_bounds import filter_manifest_by_video_bounds


def main() -> int:
    if len(sys.argv) != 4:
        print("Usage: .venv/bin/python scripts/filter_manifest_by_video_bounds.py <manifest.csv> <video-root> <output.csv>", file=sys.stderr)
        return 2
    summary = filter_manifest_by_video_bounds(*sys.argv[1:])
    for key, value in summary.__dict__.items():
        print(f"{key}: {value}")
    print("Training: NOT STARTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
