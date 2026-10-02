#!/usr/bin/env python3
"""Compare DMD archive entries with local annotation metadata without extraction."""

from __future__ import annotations

import sys
from dataclasses import asdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from federated_driving.dmd_archive import inspect_archive


def main() -> int:
    if len(sys.argv) != 3:
        print(
            "Usage: .venv/bin/python scripts/check_dmd_archive.py <archive.tar.gz> <metadata-directory>",
            file=sys.stderr,
        )
        return 2

    archive_path = sys.argv[1]
    metadata_directory = Path(sys.argv[2])
    if not metadata_directory.is_dir():
        print(f"Metadata directory does not exist: {metadata_directory}", file=sys.stderr)
        return 2

    names = [path.name for path in metadata_directory.rglob("*_rgb_ann_distraction.json")]
    summary = inspect_archive(archive_path, names)
    for key, value in asdict(summary).items():
        print(f"{key}: {value}")
    print("Extraction: NOT PERFORMED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
