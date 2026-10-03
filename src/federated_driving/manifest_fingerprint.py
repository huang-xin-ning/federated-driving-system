"""Stable local identifiers for validated frame manifests."""

from __future__ import annotations

import hashlib
import json

from .manifest import ManifestRow, ManifestSummary, summarize_manifest


def fingerprint_manifest(rows: tuple[ManifestRow, ...]) -> tuple[str, ManifestSummary]:
    """Return a SHA-256 identifier over canonical manifest row metadata.

    The identifier is for reproducibility records. It does not hash video bytes,
    copy data, or contact a remote service.
    """
    canonical_rows = sorted(
        (
            row.session_path,
            row.annotation_file,
            row.video_filename,
            row.driver_id,
            row.frame_index,
            row.target_label,
        )
        for row in rows
    )
    encoded = json.dumps(canonical_rows, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}", summarize_manifest(rows)
