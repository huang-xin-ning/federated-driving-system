"""Read-only driver-group checks for leakage-safe experiment planning."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DriverGroupCoverage:
    """Distinct annotated driver identifiers observed in metadata."""

    annotation_file_count: int
    driver_ids: tuple[str, ...]

    @property
    def distinct_driver_count(self) -> int:
        return len(self.driver_ids)


def inspect_driver_groups(metadata_directory: str | Path) -> DriverGroupCoverage:
    """Read OpenLABEL driver object names without opening video."""
    root = Path(metadata_directory)
    if not root.is_dir():
        raise ValueError(f"metadata directory does not exist: {root}")
    paths = sorted(root.rglob("*_rgb_ann_distraction.json"))
    driver_ids: set[str] = set()

    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        try:
            objects = payload["openlabel"]["objects"]
        except KeyError as error:
            raise ValueError(f"{path} has no openlabel objects") from error
        if not isinstance(objects, dict):
            raise ValueError(f"{path} has invalid openlabel objects")
        for object_id, item in objects.items():
            if not isinstance(item, dict) or item.get("type") != "driver":
                continue
            name = item.get("name")
            driver_ids.add(name if isinstance(name, str) and name else str(object_id))

    return DriverGroupCoverage(
        annotation_file_count=len(paths),
        driver_ids=tuple(sorted(driver_ids)),
    )


def grouped_split_is_feasible(coverage: DriverGroupCoverage, minimum_groups: int) -> bool:
    """Return whether observed driver groups meet a configured minimum."""
    if minimum_groups < 1:
        raise ValueError("minimum_groups must be positive")
    return coverage.distinct_driver_count >= minimum_groups
