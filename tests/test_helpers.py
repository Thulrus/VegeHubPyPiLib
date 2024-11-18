"""Tests for helpers.py."""

import pytest
from vegehub.helpers import vh400_transform


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        (0.005, 0.0),  # Below noise threshold
        (0.011, 0.09999),  # Just above the noise threshold
        (1, 9.09090909091),  # Within the first segment
        (1.1, 10.0),  # First segment boundary
        (1.2, 12.5),  # Within the second segment
        (1.3, 15.0),  # Second segment boundary
        (1.5, 24.615),  # Within the third segment
        (1.82, 40.0),  # Third segment boundary
        (2, 44.736),  # Within the fourth segment
        (2.2, 50.0),  # Fourth segment boundary
        (2.6, 75.0),  # Within the fifth segment
        (3, 100.0),  # Fifth segment boundary
        (3.5, 100.0),  # Beyond the last segment
        ("1.5", 24.615),  # String input, valid conversion
        ("invalid", -1.0),  # Invalid string input
        (None, -1.0),  # None input
        ([], -1.0),  # Invalid type (list)
    ],
)
def test_vh400_transform(input_value, expected_output):
    """Test for basic values."""
    print("input_value: " + str(input_value))
    result = vh400_transform(input_value)
    print("value out: " + str(result))
    print("expected out: " + str(expected_output))
    assert pytest.approx(result, rel=1e-4) == expected_output


def test_vh400_transform_large_input():
    """Test values significantly larger than 3.0."""
    assert vh400_transform(10) == 100.0


def test_vh400_transform_negative_input():
    """Test negative input, which should result in 0.0."""
    assert vh400_transform(-1) == 0.0
