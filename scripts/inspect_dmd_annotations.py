#!/usr/bin/env python3
"""Print a read-only JSON summary of DMD OpenLABEL annotation metadata."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from federated_driving.dmd_annotations import inspect_annotation_directory


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "Usage: .venv/bin/python scripts/inspect_dmd_annotations.py <metadata-directory>",
            file=sys.stderr,
        )
        return 2

    summaries = inspect_annotation_directory(sys.argv[1])
    output = {
        "annotation_file_count": len(summaries),
        "files": [asdict(summary) for summary in summaries],
        "notice": (
            "Action types are source metadata, not an approved training-label mapping. "
            "This command does not read video files or start training."
        ),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
