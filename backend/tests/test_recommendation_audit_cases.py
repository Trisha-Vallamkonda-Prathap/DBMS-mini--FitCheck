"""
FitCheck — Targeted Logic, Privacy Enforcement, and Defect Repair Tests
Covers Cases 1 through 8 from the Recommendation & Privacy Contract Audit.
"""

import pytest
from datetime import date
from sqlalchemy.orm import Session

from backend.app.models import (
    User,
    BodyProfile,
    Brand,
    Garment,
    GarmentSize,
    GarmentMeasurement,
    Purchase,
    FitReview,
)
from backend.app.schemas import RecommendationRequest
from backend.app.services.recommendation_service import (
    compute_size_recommendation,
    get_user_reference_dimensions,
)


def test_case_1_personalized_recommendation_consumed(db_session: Session):
    """
    Case 1 — Personalized recommendation:
    The authenticated user has a body profile and a previously kept garment with good fit satisfaction.
    Verify that their own private evidence is consumed and affects ranking.
    """
    # User 2 (Priya) has Profile: waist 68cm, hip 94cm, preferred_fit REGULAR (ease: waist +1.5, hip +2.5)
    # Add a kept purchase with GOOD fit satisfaction: Levis 501 Size 28 (garment_size_id=3)
    p = Purchase(
        user_id=2,
        garment_size_id=3,
        purchase_date=date(2024, 1, 15),
        outcome="KEPT",
        fit_satisfaction="GOOD",
        fit_preference="REGULAR",
    )
    db_session.add(p)
    db_session.commit()

    ref_dims, evidence, confidence = get_user_reference_dimensions(
        db=db_session,
        user_id=2,
        target_category="Jeans",
    )

    # Both body profile and kept purchase should be in evidence
    assert any("Body Profile" in e for e in evidence)
    assert any("Kept purchase" in e for e in evidence)
    assert confidence == "HIGH"
    assert "waist" in ref_dims
    assert "hip" in ref_dims

    # Compute recommendation for Zara Z1975 Wide Leg (garment_id=2)
    req = RecommendationRequest(target_garment_id=2, user_id=2)
    res = compute_size_recommendation(db=db_session, request=req)

    assert res.target_garment_id == 2
    assert res.primary_recommendation is not None
    assert res.confidence == "HIGH"
    assert len(res.all_sizes_ranked) == 4  # Sizes 34, 36, 38, 40


def test_case_2_returned_item_not_positive_fit(db_session: Session):
    """
    Case 2 — Returned item:
    The user has a returned or exchanged garment.
    Verify that it is not counted as a successful positive fit, but triggers a brand warning caveat.
    """
    # User 4 has no profile, but has a RETURNED purchase for Zara (brand_id=2, garment_size_id=6)
    p_returned = Purchase(
        user_id=4,
        garment_size_id=6,
        purchase_date=date(2024, 2, 10),
        outcome="RETURNED",
        fit_satisfaction="POOR",
        fit_preference="REGULAR",
    )
    db_session.add(p_returned)
    db_session.commit()

    ref_dims, evidence, confidence = get_user_reference_dimensions(
        db=db_session,
        user_id=4,
        target_category="Jeans",
    )

    # Returned item MUST NOT be added to reference dimensions
    assert ref_dims == {}
    assert confidence == "INSUFFICIENT_DATA"
    assert not any("Kept purchase" in e for e in evidence)

    # Computing recommendation for Zara (brand_id=2) must detect the return in caveats
    req = RecommendationRequest(target_garment_id=2, user_id=4)
    res = compute_size_recommendation(db=db_session, request=req)

    assert any("prior return" in c.lower() for c in res.caveats)


def test_case_3_public_review_evidence_used_safely(db_session: Session):
    """
    Case 3 — Public review evidence:
    Relevant public reviews exist for the target garment.
    Verify that only their permitted review content and consensus affect ranking, without loading reviewer data.
    """
    # Add public reviews for Zara Z1975 Wide Leg: Size 38 (id=8) has TRUE_TO_SIZE reviews
    r1 = FitReview(
        user_id=1,  # Admin posted review
        garment_size_id=8,
        overall_fit="TRUE_TO_SIZE",
        waist_fit="GOOD",
        hip_fit="GOOD",
        review_text="Fits exactly true to size, great cut and comfort.",
    )
    r2 = FitReview(
        user_id=3,  # Ananya posted review
        garment_size_id=8,
        overall_fit="TRUE_TO_SIZE",
        waist_fit="GOOD",
        hip_fit="GOOD",
        review_text="High rise sits comfortably at the natural waist.",
    )
    db_session.add_all([r1, r2])
    db_session.commit()

    # User 4 (cold start, no personal profile)
    req = RecommendationRequest(target_garment_id=2, user_id=4)
    res = compute_size_recommendation(db=db_session, request=req)

    # Size 38 should rank top due to positive True to Size public reviews
    assert res.primary_recommendation.garment_size_id == 8
    assert res.primary_recommendation.size_label == "38"
    assert any("Public Customer Reviews" in e for e in res.evidence_sources)
    assert any("True To Size" in n for n in res.primary_recommendation.notes)


def test_case_4_strict_cross_user_privacy(db_session: Session):
    """
    Case 4 — Strict cross-user privacy:
    Create two users (User A=2, User B=3). Hold User A's private data constant.
    Drastically change User B's body profile and purchase history.
    User A's recommendation MUST remain completely identical.
    """
    # User A baseline recommendation
    req_a = RecommendationRequest(target_garment_id=2, user_id=2)
    res_a_initial = compute_size_recommendation(db=db_session, request=req_a)

    initial_primary_id = res_a_initial.primary_recommendation.garment_size_id
    initial_score = res_a_initial.primary_recommendation.match_score

    # Mutate User B (User 3) profile wildly
    prof_b = db_session.query(BodyProfile).filter(BodyProfile.user_id == 3).first()
    if prof_b:
        prof_b.waist = 120.0
        prof_b.hip = 150.0
        prof_b.thigh = 80.0
    # Add purchases for User B
    p_b = Purchase(
        user_id=3,
        garment_size_id=9,
        outcome="KEPT",
        fit_satisfaction="GOOD",
        fit_preference="RELAXED",
    )
    db_session.add(p_b)
    db_session.commit()

    # Re-run User A's recommendation
    res_a_after = compute_size_recommendation(db=db_session, request=req_a)

    # Verify User A's recommendation is unaffected by User B's private data
    assert res_a_after.primary_recommendation.garment_size_id == initial_primary_id
    assert res_a_after.primary_recommendation.match_score == initial_score
    assert len(res_a_after.all_sizes_ranked) == len(res_a_initial.all_sizes_ranked)
    for s_init, s_after in zip(res_a_initial.all_sizes_ranked, res_a_after.all_sizes_ranked):
        assert s_init.garment_size_id == s_after.garment_size_id
        assert s_init.match_score == s_after.match_score


def test_case_5_cold_start_graceful(db_session: Session):
    """
    Case 5 — Cold start:
    The authenticated user has no profile and no purchase history, and no reviews exist.
    Verify graceful behavior without fake personal calibration.
    """
    # User 4 has no profile and no purchases
    req = RecommendationRequest(target_garment_id=1, user_id=4)
    res = compute_size_recommendation(db=db_session, request=req)

    assert res.confidence == "INSUFFICIENT_DATA"
    assert any("cold-start" in e.lower() for e in res.evidence_sources)
    assert any("uncalibrated" in c.lower() for c in res.caveats)


def test_case_6_missing_review_service_graceful(db_session: Session):
    """
    Case 6 — Missing or unavailable review service:
    Verify that missing reviews do not crash the engine or fabricate review citations.
    """
    # User 2 has profile, target garment 1 (Levis 501) has registered sizes and 0 reviews
    req = RecommendationRequest(target_garment_id=1, user_id=2)
    res = compute_size_recommendation(db=db_session, request=req)

    # Should compute normally based on personal body measurements without crashing or fabricating reviews
    assert res.target_garment_id == 1
    assert res.primary_recommendation is not None
    assert not any("Public Customer Reviews" in e for e in res.evidence_sources)


def test_case_7_correct_target_garment_sizes(db_session: Session):
    """
    Case 7 — Correct target garment:
    Verify that all recommended sizes belong strictly to the selected target garment
    and measurements are resolved through the correct relationships.
    """
    req = RecommendationRequest(target_garment_id=1, user_id=2)  # Levis 501 (Sizes 1-5)
    res = compute_size_recommendation(db=db_session, request=req)

    # Levis 501 has sizes with IDs 1, 2, 3, 4, 5
    expected_ids = {1, 2, 3, 4, 5}
    actual_ids = {s.garment_size_id for s in res.all_sizes_ranked}
    assert actual_ids == expected_ids


def test_case_8_purchase_id_mapping(db_session: Session):
    """
    Case 8 — Purchase ID mapping:
    Verify that foreign keys PURCHASE.garment_size_id -> GARMENT_SIZE -> GARMENT -> BRAND
    strictly maintain relational integrity.
    """
    # Valid size 8 is Zara Z1975 Wide Leg Size 38
    p = Purchase(
        user_id=2,
        garment_size_id=8,
        purchase_date=date(2024, 3, 1),
        outcome="KEPT",
        fit_satisfaction="GOOD",
    )
    db_session.add(p)
    db_session.commit()

    saved_p = db_session.query(Purchase).filter(Purchase.purchase_id == p.purchase_id).first()
    assert saved_p is not None
    assert saved_p.garment_size.size_label == "38"
    assert saved_p.garment_size.garment.garment_name == "Zara Z1975 Wide Leg"
    assert saved_p.garment_size.garment.brand.brand_name == "Zara"
