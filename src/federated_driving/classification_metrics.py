"""Framework-independent metrics for future classification evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import chain
from typing import Sequence


@dataclass(frozen=True)
class BinaryClassificationMetrics:
    """Metrics for a declared positive class and two-label task."""

    labels: tuple[str, str]
    confusion_matrix: tuple[tuple[int, int], tuple[int, int]]
    accuracy: float
    precision: float
    recall: float
    f1: float


def binary_metrics(
    actual: Sequence[str], predicted: Sequence[str], labels: tuple[str, str]
) -> BinaryClassificationMetrics:
    """Calculate metrics from aligned labels; the second label is positive."""
    if len(labels) != 2 or labels[0] == labels[1] or any(not label for label in labels):
        raise ValueError("labels must contain exactly two distinct non-empty values")
    if not actual or len(actual) != len(predicted):
        raise ValueError("actual and predicted must be non-empty and have the same length")
    allowed = set(labels)
    if any(value not in allowed for value in chain(actual, predicted)):
        raise ValueError("actual and predicted values must be declared labels")

    negative, positive = labels
    true_negative = sum(a == negative and p == negative for a, p in zip(actual, predicted))
    false_positive = sum(a == negative and p == positive for a, p in zip(actual, predicted))
    false_negative = sum(a == positive and p == negative for a, p in zip(actual, predicted))
    true_positive = sum(a == positive and p == positive for a, p in zip(actual, predicted))
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    return BinaryClassificationMetrics(
        labels,
        ((true_negative, false_positive), (false_negative, true_positive)),
        (true_negative + true_positive) / len(actual),
        precision,
        recall,
        f1,
    )
