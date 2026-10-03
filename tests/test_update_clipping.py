"""Tests for synthetic L2 update clipping."""

from __future__ import annotations

import unittest

from federated_driving.update_clipping import clip_l2


class UpdateClippingTests(unittest.TestCase):
    def test_keeps_vector_within_limit(self) -> None:
        result = clip_l2((1.0, 2.0), 3.0)

        self.assertEqual(result.vector, (1.0, 2.0))
        self.assertFalse(result.was_clipped)

    def test_scales_vector_to_limit(self) -> None:
        result = clip_l2((3.0, 4.0), 2.0)

        self.assertEqual(result.original_norm, 5.0)
        self.assertAlmostEqual(result.vector[0], 1.2)
        self.assertAlmostEqual(result.vector[1], 1.6)
        self.assertTrue(result.was_clipped)

    def test_rejects_invalid_norm_limit(self) -> None:
        with self.assertRaisesRegex(ValueError, "maximum_norm"):
            clip_l2((1.0,), 0.0)

    def test_rejects_non_finite_values(self) -> None:
        with self.assertRaisesRegex(ValueError, "finite"):
            clip_l2((float("inf"),), 1.0)
