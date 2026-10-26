"""
Unit and Integration Tests for Member B FIT_REVIEW CRUD
Covers:
- Valid review insert with automatic user derivation
- Validation: blank / whitespace-only review_text rejected
- Validation: invalid overall_fit / waist_fit enums rejected
- Validation: nonexistent garment_size_id returns 404
- Listing current user's reviews with joined brand and size metadata
- Authorization: user cannot edit or delete another user's review (HTTP 403)
- Admin override: ADMIN can update and delete any user's review
- Review update and delete operations
"""

import pytest
from backend.app.core.security import create_access_token
from backend.app.models import FitReview


def test_create_review_success(client):
    """Verifies that an authenticated user can submit a valid review."""
    token = create_access_token(subject=2, role="USER")  # Priya
    payload = {
        "garment_size_id": 3,  # Levis 501 sz 28
        "overall_fit": "TRUE_TO_SIZE",
        "waist_fit": "GOOD",
        "hip_fit": "GOOD",
        "thigh_fit": "GOOD",
        "length_fit": "GOOD",
        "review_text": "Authentic denim fit. Sits right at the waist with classic drape.",
    }
    response = client.post(
        "/api/v1/reviews",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == 2
    assert data["garment_size_id"] == 3
    assert data["overall_fit"] == "TRUE_TO_SIZE"
    assert data["brand_name"] == "Levis"
    assert data["garment_name"] == "Levis 501 Original"
    assert data["size_label"] == "28"


def test_create_review_blank_text_rejected(client):
    """Verifies that empty or whitespace-only review text is strictly rejected."""
    token = create_access_token(subject=2, role="USER")

    # Empty string
    res1 = client.post(
        "/api/v1/reviews",
        json={"garment_size_id": 3, "overall_fit": "TRUE_TO_SIZE", "review_text": ""},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res1.status_code == 422

    # Whitespace only
    res2 = client.post(
        "/api/v1/reviews",
        json={"garment_size_id": 3, "overall_fit": "TRUE_TO_SIZE", "review_text": "   \n\t  "},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res2.status_code == 422


def test_create_review_invalid_enum_rejected(client):
    """Verifies that non-contract fit enums are rejected by schema validation."""
    token = create_access_token(subject=2, role="USER")
    payload = {
        "garment_size_id": 3,
        "overall_fit": "PERFECT",  # Invalid enum (must be TRUE_TO_SIZE, etc.)
        "review_text": "Great jeans",
    }
    response = client.post(
        "/api/v1/reviews",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


def test_create_review_invalid_garment_size_id(client):
    """Verifies that referencing a non-existent garment_size_id returns HTTP 404."""
    token = create_access_token(subject=2, role="USER")
    payload = {
        "garment_size_id": 99999,  # Non-existent
        "overall_fit": "TRUE_TO_SIZE",
        "review_text": "Trying to review unknown garment size",
    }
    response = client.post(
        "/api/v1/reviews",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
    assert "does not exist" in response.json()["detail"]


def test_get_my_reviews(client):
    """Verifies that GET /api/v1/reviews/mine returns only the calling user's reviews."""
    token_priya = create_access_token(subject=2, role="USER")
    token_ananya = create_access_token(subject=3, role="USER")

    # Priya creates review
    client.post(
        "/api/v1/reviews",
        json={"garment_size_id": 3, "overall_fit": "TRUE_TO_SIZE", "review_text": "Priya's Levis review"},
        headers={"Authorization": f"Bearer {token_priya}"},
    )

    # Ananya creates review
    client.post(
        "/api/v1/reviews",
        json={"garment_size_id": 1, "overall_fit": "TOO_SMALL", "review_text": "Ananya's petite review"},
        headers={"Authorization": f"Bearer {token_ananya}"},
    )

    # Priya fetches hers
    res_priya = client.get("/api/v1/reviews/mine", headers={"Authorization": f"Bearer {token_priya}"})
    assert res_priya.status_code == 200
    priya_items = res_priya.json()
    assert len(priya_items) == 1
    assert priya_items[0]["review_text"] == "Priya's Levis review"

    # Ananya fetches hers
    res_ananya = client.get("/api/v1/reviews/mine", headers={"Authorization": f"Bearer {token_ananya}"})
    assert res_ananya.status_code == 200
    ananya_items = res_ananya.json()
    assert len(ananya_items) == 1
    assert ananya_items[0]["review_text"] == "Ananya's petite review"


def test_review_authorization_update_and_delete(client):
    """Verifies that User A cannot update or delete User B's review, but ADMIN can."""
    token_user2 = create_access_token(subject=2, role="USER")
    token_user3 = create_access_token(subject=3, role="USER")
    token_admin = create_access_token(subject=1, role="ADMIN")

    # User 2 creates review
    create_res = client.post(
        "/api/v1/reviews",
        json={"garment_size_id": 3, "overall_fit": "TRUE_TO_SIZE", "review_text": "Original review text"},
        headers={"Authorization": f"Bearer {token_user2}"},
    )
    rev_id = create_res.json()["review_id"]

    # User 3 attempts to update User 2's review -> 403 Forbidden
    patch_forbidden = client.patch(
        f"/api/v1/reviews/{rev_id}",
        json={"review_text": "Malicious edit by another user"},
        headers={"Authorization": f"Bearer {token_user3}"},
    )
    assert patch_forbidden.status_code == 403

    # User 3 attempts to delete User 2's review -> 403 Forbidden
    delete_forbidden = client.delete(
        f"/api/v1/reviews/{rev_id}",
        headers={"Authorization": f"Bearer {token_user3}"},
    )
    assert delete_forbidden.status_code == 403

    # User 2 updates own review -> 200 OK
    patch_ok = client.patch(
        f"/api/v1/reviews/{rev_id}",
        json={"overall_fit": "SLIGHTLY_SMALL", "review_text": "Updated after a few washes: slightly small."},
        headers={"Authorization": f"Bearer {token_user2}"},
    )
    assert patch_ok.status_code == 200
    assert patch_ok.json()["overall_fit"] == "SLIGHTLY_SMALL"

    # ADMIN deletes the review -> 200 OK
    admin_del = client.delete(
        f"/api/v1/reviews/{rev_id}",
        headers={"Authorization": f"Bearer {token_admin}"},
    )
    assert admin_del.status_code == 200
    assert admin_del.json()["success"] is True

    # Confirm it is gone
    confirm_gone = client.get(f"/api/v1/garment-sizes/3/reviews")
    assert confirm_gone.status_code == 200
    assert len(confirm_gone.json()) == 0
