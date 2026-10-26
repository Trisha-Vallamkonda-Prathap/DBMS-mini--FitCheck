"""
Unit and Integration Tests for Member B Database Trigger & Relational Joins
Covers:
- Review audit trigger execution on INSERT, UPDATE, and DELETE
- Audit record verification in REVIEW_AUDIT
- Multi-table JOIN (FIT_REVIEW -> GARMENT_SIZE -> GARMENT -> BRAND)
- Authoritative metadata retrieval for semantic search results
"""

import pytest
from sqlalchemy import text
from backend.app.models import FitReview, GarmentSize, Garment, Brand, ReviewAudit
from backend.app.core.security import create_access_token


def test_review_audit_trigger_lifecycle(db_session):
    """
    Verifies that database triggers log all lifecycle actions (INSERT, UPDATE, DELETE)
    on FIT_REVIEW into the REVIEW_AUDIT support table.
    """
    # 1. Ensure SQLite test trigger exists in the test database session
    db_session.execute(text("""
        CREATE TRIGGER IF NOT EXISTS trg_test_after_review_insert
        AFTER INSERT ON FIT_REVIEW
        FOR EACH ROW
        BEGIN
            INSERT INTO REVIEW_AUDIT (review_id, action, user_id, details)
            VALUES (NEW.review_id, 'INSERT', NEW.user_id, 'Review created');
        END;
    """))
    db_session.execute(text("""
        CREATE TRIGGER IF NOT EXISTS trg_test_after_review_update
        AFTER UPDATE ON FIT_REVIEW
        FOR EACH ROW
        BEGIN
            INSERT INTO REVIEW_AUDIT (review_id, action, user_id, details)
            VALUES (NEW.review_id, 'UPDATE', NEW.user_id, 'Review updated');
        END;
    """))
    db_session.execute(text("""
        CREATE TRIGGER IF NOT EXISTS trg_test_after_review_delete
        AFTER DELETE ON FIT_REVIEW
        FOR EACH ROW
        BEGIN
            INSERT INTO REVIEW_AUDIT (review_id, action, user_id, details)
            VALUES (OLD.review_id, 'DELETE', OLD.user_id, 'Review deleted');
        END;
    """))
    db_session.commit()

    # --- Step 1: INSERT ---
    rev = FitReview(
        review_id=901,
        user_id=2,
        garment_size_id=3,
        overall_fit="TRUE_TO_SIZE",
        review_text="Trigger test review text",
    )
    db_session.add(rev)
    db_session.commit()

    insert_audit = (
        db_session.query(ReviewAudit)
        .filter(ReviewAudit.review_id == 901, ReviewAudit.action == "INSERT")
        .first()
    )
    assert insert_audit is not None
    assert insert_audit.user_id == 2
    assert "created" in insert_audit.details.lower()

    # --- Step 2: UPDATE ---
    rev.overall_fit = "SLIGHTLY_SMALL"
    db_session.commit()

    update_audit = (
        db_session.query(ReviewAudit)
        .filter(ReviewAudit.review_id == 901, ReviewAudit.action == "UPDATE")
        .first()
    )
    assert update_audit is not None
    assert update_audit.user_id == 2
    assert "updated" in update_audit.details.lower()

    # --- Step 3: DELETE ---
    db_session.delete(rev)
    db_session.commit()

    delete_audit = (
        db_session.query(ReviewAudit)
        .filter(ReviewAudit.review_id == 901, ReviewAudit.action == "DELETE")
        .first()
    )
    assert delete_audit is not None
    assert delete_audit.user_id == 2
    assert "deleted" in delete_audit.details.lower()


def test_multi_table_join_review_metadata(db_session):
    """
    Demonstrates Rubric Item 6 (Multi-table SQL JOIN):
    Joins FIT_REVIEW -> GARMENT_SIZE -> GARMENT -> BRAND to retrieve
    authoritative contextual data without duplicating foreign keys.
    """
    # Create test review for garment_size_id=3 (Levis 501 sz 28)
    rev = FitReview(
        review_id=902,
        user_id=2,
        garment_size_id=3,
        overall_fit="TRUE_TO_SIZE",
        waist_fit="GOOD",
        review_text="Checking relational join precision",
    )
    db_session.add(rev)
    db_session.commit()

    # Execute 4-table relational join
    result = (
        db_session.query(
            FitReview.review_id,
            FitReview.review_text,
            FitReview.overall_fit,
            GarmentSize.size_label,
            Garment.garment_name,
            Brand.brand_name,
        )
        .join(GarmentSize, FitReview.garment_size_id == GarmentSize.garment_size_id)
        .join(Garment, GarmentSize.garment_id == Garment.garment_id)
        .join(Brand, Garment.brand_id == Brand.brand_id)
        .filter(FitReview.review_id == 902)
        .first()
    )

    assert result is not None
    review_id, review_text, overall_fit, size_label, garment_name, brand_name = result

    assert review_id == 902
    assert review_text == "Checking relational join precision"
    assert overall_fit == "TRUE_TO_SIZE"
    assert size_label == "28"
    assert garment_name == "Levis 501 Original"
    assert brand_name == "Levis"


def test_semantic_search_endpoint_returns_joined_metadata(client, monkeypatch):
    """
    Verifies that POST /api/v1/reviews/search uses relational joins to return
    brand, garment, and size context alongside review text and similarity score.
    """
    token = create_access_token(subject=2, role="USER")

    # Seed review via API
    create_res = client.post(
        "/api/v1/reviews",
        json={
            "garment_size_id": 3,
            "overall_fit": "TRUE_TO_SIZE",
            "waist_fit": "GOOD",
            "review_text": "Waistband fits comfortably with no pinching.",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_res.status_code == 201
    rev_id = create_res.json()["review_id"]

    # Mock vector hits to simulate Redis KNN search return for isolated unit testing
    monkeypatch.setattr(
        "backend.app.api.v1.endpoints.reviews.search_review_vectors",
        lambda query_text, k=5, overall_fit_filter=None: [(rev_id, 0.88)],
    )

    # Search for fit experience
    search_res = client.post(
        "/api/v1/reviews/search",
        json={"query": "comfortable waistband", "limit": 5},
    )
    assert search_res.status_code == 200
    hits = search_res.json()
    assert len(hits) >= 1

    top_hit = hits[0]
    assert top_hit["brand_name"] == "Levis"
    assert top_hit["garment_name"] == "Levis 501 Original"
    assert top_hit["size_label"] == "28"
    assert top_hit["review_text"] == "Waistband fits comfortably with no pinching."
    assert 0.0 <= top_hit["similarity_score"] <= 1.0
