import pytest
from pydantic import ValidationError
from backend.app.schemas import BodyProfileBase, BodyProfileUpdate, PurchaseCreate


def test_valid_profile_schema():
    """Validates that valid body profile inputs are accepted."""
    profile = BodyProfileUpdate(
        height=165.0,
        waist=70.0,
        hip=96.0,
        thigh=55.0,
        inseam=78.0,
        preferred_fit="REGULAR",
    )
    assert profile.height == 165.0
    assert profile.preferred_fit == "REGULAR"


def test_invalid_negative_measurements():
    """Validates rejection of non-positive measurement dimensions."""
    with pytest.raises(ValidationError):
        BodyProfileUpdate(waist=-5.0)

    with pytest.raises(ValidationError):
        BodyProfileUpdate(height=0.0)


def test_invalid_preferred_fit_enum():
    """Validates rejection of non-supported fit enum values."""
    with pytest.raises(ValidationError):
        BodyProfileUpdate(preferred_fit="EXTRA_BAGGY")


def test_purchase_schema_validation():
    """Validates outcome and fit satisfaction enum constraints on purchase creation."""
    # Valid purchase
    p = PurchaseCreate(
        garment_size_id=1,
        outcome="KEPT",
        fit_satisfaction="GOOD",
        fit_preference="REGULAR",
    )
    assert p.outcome == "KEPT"

    # Invalid outcome
    with pytest.raises(ValidationError):
        PurchaseCreate(
            garment_size_id=1,
            outcome="DONATED",
        )
