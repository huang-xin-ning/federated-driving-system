"""Tests for stable manifest fingerprints."""

from __future__ import annotations

import unittest

from federated_driving.manifest import ManifestRow
from federated_driving.manifest_fingerprint import fingerprint_manifest


class ManifestFingerprintTests(unittest.TestCase):
    def test_is_stable_when_row_order_changes(self) -> None:
        first = ManifestRow("s1", "a.json", "a.mp4", "driver-a", 1, "safe_drive")
        second = ManifestRow("s1", "a.json", "a.mp4", "driver-b", 2, "distraction")

        identifier_one, summary_one = fingerprint_manifest((first, second))
        identifier_two, summary_two = fingerprint_manifest((second, first))

        self.assertEqual(identifier_one, identifier_two)
        self.assertTrue(identifier_one.startswith("sha256:"))
        self.assertEqual(summary_one, summary_two)

    def test_changes_when_label_assignment_changes(self) -> None:
        original = ManifestRow("s1", "a.json", "a.mp4", "driver-a", 1, "safe_drive")
        changed = ManifestRow("s1", "a.json", "a.mp4", "driver-a", 1, "distraction")

        original_identifier, _ = fingerprint_manifest((original,))
        changed_identifier, _ = fingerprint_manifest((changed,))

        self.assertNotEqual(original_identifier, changed_identifier)
