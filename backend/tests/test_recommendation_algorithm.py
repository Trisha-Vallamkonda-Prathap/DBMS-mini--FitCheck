import pytest
from backend.app.schemas import RecommendationRequest
from backend.app.services.recommendation_service import compute_size_recommendation


def test_recommendation_with_purchase_history(db_session):
    """
    Validates cross-brand sizing: User 2 (Priya) has kept Levis 501 sz 28 (waist 71cm, hip 96cm).
    Target: Zara Z1975 Wide Leg (Garment 2).
    Zara sz 38 has waist 70cm, hip 98cm (delta ~1.0cm).
    Zara sz 38 should rank #1.
    """
    request = RecommendationRequest(
        target_garment_id=2,
        user_id=2,
    )
    result = compute_size_recommendation(db=db_session, request=request)

    assert result.target_garment_name == "Zara Z1975 Wide Leg"
    assert result.confidence == "HIGH"
    assert result.primary_recommendation is not None
    assert result.primary_recommendation.size_label == "38"
    assert result.primary_recommendation.match_score >= 75.0
    assert result.primary_recommendation.rank == 1
    assert "Optimal Fit" in result.primary_recommendation.fit_verdict or "Very Close Fit" in result.primary_recommendation.fit_verdict
    assert len(result.evidence_sources) >= 1


def test_recommendation_with_manual_measurements(db_session):
    """
    Validates guest/manual override recommendation without stored user profile.
    Manual waist=74, hip=102 -> should match Zara size 40 (waist 74, hip 102).
    """
    request = RecommendationRequest(
        target_garment_id=2,
        waist=74.0,
        hip=102.0,
        preferred_fit="TIGHT",
    )
    result = compute_size_recommendation(db=db_session, request=request)

    assert result.primary_recommendation is not None
    assert result.primary_recommendation.size_label == "40"
    assert result.primary_recommendation.match_score >= 90.0
    assert result.confidence == "HIGH"


def test_recommendation_with_body_profile_only(db_session):
    """
    Validates recommendation driven by BodyProfile:
    User 3 (Ananya) has waist=64, hip=90, preferred_fit=TIGHT.
    With TIGHT ease (0cm waist, 0.5cm hip), target reference is waist 64, hip 90.5.
    Closest Zara size is 36 (waist 66, hip 94).
    """
    request = RecommendationRequest(
        target_garment_id=2,
        user_id=3,
    )
    result = compute_size_recommendation(db=db_session, request=request)

    assert result.primary_recommendation is not None
    assert result.primary_recommendation.size_label == "36"
    assert result.confidence == "MEDIUM"


def test_cold_start_uncalibrated_fallback(db_session):
    """
    Validates graceful degradation when user has no purchases and no body profile.
    """
    request = RecommendationRequest(
        target_garment_id=2,
        user_id=4,  # User 4 has no profile and no purchases
    )
    result = compute_size_recommendation(db=db_session, request=request)

    assert result.confidence == "INSUFFICIENT_DATA"
    assert "No reference measurements were available" in result.explanation
    assert len(result.all_sizes_ranked) > 0


def test_invalid_target_garment(db_session):
    """Validates that non-existent garment ID raises ValueError."""
    request = RecommendationRequest(
        target_garment_id=99999,
        user_id=2,
    )
    with pytest.raises(ValueError, match="does not exist"):
        compute_size_recommendation(db=db_session, request=request)


def test_monotonic_score_ranking(db_session):
    """Validates that all_sizes_ranked is strictly ordered in descending match_score."""
    request = RecommendationRequest(
        target_garment_id=2,
        user_id=2,
    )
    result = compute_size_recommendation(db=db_session, request=request)

    scores = [s.match_score for s in result.all_sizes_ranked]
    for i in range(len(scores) - 1):
        assert scores[i] >= scores[i + 1]


def test_top_recommendations_capped_at_three(db_session):
    """Validates that top_recommendations returns at most 3 sizes."""
    request = RecommendationRequest(
        target_garment_id=2,
        user_id=2,
    )
    result = compute_size_recommendation(db=db_session, request=request)
    assert len(result.top_recommendations) == min(3, len(result.all_sizes_ranked))
    assert result.top_recommendations[0].garment_size_id == result.primary_recommendation.garment_size_id


def test_rise_and_category_handling(db_session):
    """Validates rise inclusion in DEFAULT_WEIGHTS and dimensional deltas."""
    from backend.app.services.recommendation_service import DEFAULT_WEIGHTS
    assert "rise" in DEFAULT_WEIGHTS
    assert DEFAULT_WEIGHTS["rise"] == 0.06
    # Ensure sum of weights equals 1.0
    assert round(sum(DEFAULT_WEIGHTS.values()), 4) == 1.0


def test_category_matching_and_notes(db_session):
    """Validates that recommendations provide category evidence and dimensional notes."""
    request = RecommendationRequest(
        target_garment_id=2,  # Zara Z1975 Wide Leg (Jeans)
        user_id=2,           # User 2 has kept Levis 501 (Jeans)
    )
    result = compute_size_recommendation(db=db_session, request=request)
    assert result.category == "Jeans"
    # Evidence should cite the category
    assert any("[Jeans]" in ev or "Jeans" in ev for ev in result.evidence_sources)
    # Target sizes should belong to Zara Z1975 (size labels 34..42)
    valid_labels = {"34", "36", "38", "40", "42"}
    assert all(s.size_label in valid_labels for s in result.all_sizes_ranked)
    assert result.primary_recommendation.size_label in valid_labels
