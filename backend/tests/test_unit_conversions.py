import pytest
from backend.app.services.recommendation_service import normalize_to_cm, INCHES_TO_CM


def test_normalize_cm_identity():
    """Validates that cm measurements remain unchanged with proper rounding."""
    assert normalize_to_cm(70.0, "cm") == 70.0
    assert normalize_to_cm(95.555, "cm") == 95.56
    assert normalize_to_cm(100.0, "CM") == 100.0


def test_normalize_inches_to_cm():
    """Validates accurate conversion from inches to centimeters (1 in = 2.54 cm)."""
    # 28 inches = 71.12 cm
    assert normalize_to_cm(28.0, "in") == 71.12
    # 30 inches = 76.2 cm
    assert normalize_to_cm(30.0, "inch") == 76.20
    # 32 inches = 81.28 cm
    assert normalize_to_cm(32.0, "inches") == 81.28
    # 26.5 inches = 67.31 cm
    assert normalize_to_cm(26.5, "IN") == 67.31


def test_zero_and_precision():
    """Validates edge cases in unit normalization."""
    assert normalize_to_cm(0.0, "cm") == 0.0
    assert normalize_to_cm(1.0, "in") == round(INCHES_TO_CM, 2)
