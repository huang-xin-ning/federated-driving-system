"""Tests for archive-to-metadata integrity checks."""

from __future__ import annotations

import io
import tarfile
import tempfile
import unittest
from pathlib import Path

from federated_driving.dmd_archive import inspect_archive


def add_file(archive: tarfile.TarFile, name: str) -> None:
    content = b"test"
    info = tarfile.TarInfo(name)
    info.size = len(content)
    archive.addfile(info, io.BytesIO(content))


class DmdArchiveTests(unittest.TestCase):
    def test_counts_sessions_videos_and_annotation_matches(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            archive_path = Path(directory) / "pilot.tar.gz"
            with tarfile.open(archive_path, "w:gz") as archive:
                prefix = "dmd/gA/1/s1/"
                add_file(archive, prefix + "record_rgb_ann_distraction.json")
                add_file(archive, prefix + "record_rgb_face.mp4")
                add_file(archive, prefix + "record_rgb_mosaic.avi")
            summary = inspect_archive(
                str(archive_path), ["record_rgb_ann_distraction.json"]
            )

        self.assertEqual(summary.session_count, 1)
        self.assertEqual(summary.video_count, 2)
        self.assertEqual(summary.archive_annotation_count, 1)
        self.assertEqual(summary.missing_external_annotations, ())
        self.assertEqual(summary.external_annotations_not_in_archive, ())

    def test_reports_mismatched_annotations(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            archive_path = Path(directory) / "pilot.tar.gz"
            with tarfile.open(archive_path, "w:gz") as archive:
                add_file(archive, "dmd/gA/1/s1/in_archive_rgb_ann_distraction.json")
            summary = inspect_archive(str(archive_path), ["outside_rgb_ann_distraction.json"])

        self.assertEqual(summary.missing_external_annotations, ("in_archive_rgb_ann_distraction.json",))
        self.assertEqual(
            summary.external_annotations_not_in_archive,
            ("outside_rgb_ann_distraction.json",),
        )
