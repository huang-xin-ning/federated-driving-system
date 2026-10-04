"""Tests for framework-independent binary classification metrics."""

from __future__ import annotations

import unittest

from federated_driving.classification_metrics import binary_metrics


class ClassificationMetricsTests(unittest.TestCase):
    def test_calculates_confusion_matrix_and_metrics(self) -> None:
        result = binary_metrics(
            ("safe", "risk", "risk", "safe"),
            ("safe", "risk", "safe", "safe"),
            ("safe", "risk"),
        )
        self.assertEqual(result.confusion_matrix, ((2, 0), (1, 1)))
        self.assertEqual(result.accuracy, 0.75)
        self.assertEqual(result.precision, 1.0)
        self.assertEqual(result.recall, 0.5)
        self.assertAlmostEqual(result.f1, 2 / 3)

    def test_handles_zero_positive_predictions(self) -> None:
        result = binary_metrics(("safe", "risk"), ("safe", "safe"), ("safe", "risk"))
        self.assertEqual(result.precision, 0.0)
        self.assertEqual(result.recall, 0.0)
        self.assertEqual(result.f1, 0.0)

    def test_accepts_mixed_sequence_types(self) -> None:
        result = binary_metrics(["safe", "risk"], ("safe", "risk"), ("safe", "risk"))
        self.assertEqual(result.accuracy, 1.0)

    def test_rejects_mismatched_lengths(self) -> None:
        with self.assertRaisesRegex(ValueError, "same length"):
            binary_metrics(("safe",), ("safe", "risk"), ("safe", "risk"))

    def test_rejects_unknown_label(self) -> None:
        with self.assertRaisesRegex(ValueError, "declared labels"):
            binary_metrics(("safe", "other"), ("safe", "risk"), ("safe", "risk"))
