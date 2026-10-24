"""
FitCheck — Fit Review & Semantic Search API Endpoints (Member B)
Implements:
- Authenticated Review CRUD with MySQL persistence
- Automatic Redis Stack vector index synchronization (Create, Update, Delete)
- KNN Semantic Review Search with authoritative MySQL relational JOINs
- Admin Review Audit Log inspection
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.core.database import get_db
from backend.app.api.deps import get_current_user, require_admin
from backend.app.models import (
    User,
    FitReview,
    GarmentSize,
    Garment,
    Brand,
    ReviewAudit,
)
from backend.app.schemas import (
    FitReviewCreate,
    FitReviewUpdate,
    FitReviewOut,
    ReviewSearchRequest,
    ReviewSearchResult,
    ReviewAuditOut,
)
from backend.app.services.vector_service import (
    upsert_review_vector,
    delete_review_vector,
    search_review_vectors,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def _format_review_out(review: FitReview, db: Session) -> FitReviewOut:
    """Helper to attach joined garment, brand, and size metadata to a FitReviewOut object."""
    size_row = (
        db.query(GarmentSize, Garment, Brand)
        .join(Garment, GarmentSize.garment_id == Garment.garment_id)
        .join(Brand, Garment.brand_id == Brand.brand_id)
        .filter(GarmentSize.garment_size_id == review.garment_size_id)
        .first()
    )

    garment_name = size_row[1].garment_name if size_row else None
    brand_name = size_row[2].brand_name if size_row else None
    size_label = size_row[0].size_label if size_row else None

    return FitReviewOut(
        review_id=review.review_id,
        user_id=review.user_id,
        garment_size_id=review.garment_size_id,
        overall_fit=review.overall_fit,
        waist_fit=review.waist_fit,
        hip_fit=review.hip_fit,
        thigh_fit=review.thigh_fit,
        length_fit=review.length_fit,
        review_text=review.review_text,
        created_at=review.created_at,
        garment_name=garment_name,
        brand_name=brand_name,
        size_label=size_label,
    )


# ------------------------------------------------------------
# 1. POST /api/v1/reviews - Create Review & Sync Vector
# ------------------------------------------------------------
@router.post(
    "/reviews",
    response_model=FitReviewOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new fit review (Authenticated)",
)
def create_review(
    review_in: FitReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Creates a new FIT_REVIEW in MySQL, derives ownership from authenticated user,
    and automatically indexes its 384-d embedding in Redis Stack.
    """
    # 1. Validate garment_size_id exists
    garment_size = db.query(GarmentSize).filter(GarmentSize.garment_size_id == review_in.garment_size_id).first()
    if not garment_size:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Garment size ID {review_in.garment_size_id} does not exist in catalogue.",
        )

    # 2. Persist in MySQL
    new_review = FitReview(
        user_id=current_user.user_id,
        garment_size_id=review_in.garment_size_id,
        overall_fit=review_in.overall_fit,
        waist_fit=review_in.waist_fit,
        hip_fit=review_in.hip_fit,
        thigh_fit=review_in.thigh_fit,
        length_fit=review_in.length_fit,
        review_text=review_in.review_text,
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    # 3. Synchronize Redis Stack vector index (CREATE)
    try:
        upsert_review_vector(
            review_id=new_review.review_id,
            garment_size_id=new_review.garment_size_id,
            overall_fit=new_review.overall_fit,
            review_text=new_review.review_text,
        )
    except Exception as e:
        logger.warning(f"Vector sync warning on create: {e}")

    return _format_review_out(new_review, db)


# ------------------------------------------------------------
# 2. GET /api/v1/reviews/mine - Current User Reviews
# ------------------------------------------------------------
@router.get(
    "/reviews/mine",
    response_model=List[FitReviewOut],
    summary="List authenticated user's reviews",
)
def get_my_reviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves all reviews authored by the currently authenticated user with joined garment/brand metadata."""
    reviews = (
        db.query(FitReview)
        .filter(FitReview.user_id == current_user.user_id)
        .order_by(desc(FitReview.created_at))
        .all()
    )
    return [_format_review_out(r, db) for r in reviews]


# ------------------------------------------------------------
# 3. GET /api/v1/garment-sizes/{id}/reviews - Reviews for Size
# ------------------------------------------------------------
@router.get(
    "/garment-sizes/{size_id}/reviews",
    response_model=List[FitReviewOut],
    summary="List reviews for a specific garment size",
)
def get_reviews_for_garment_size(
    size_id: int,
    db: Session = Depends(get_db),
):
    """Retrieves all reviews for a specific garment size ID with product context."""
    size_exists = db.query(GarmentSize).filter(GarmentSize.garment_size_id == size_id).first()
    if not size_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Garment size ID {size_id} not found.",
        )

    reviews = (
        db.query(FitReview)
        .filter(FitReview.garment_size_id == size_id)
        .order_by(desc(FitReview.created_at))
        .all()
    )
    return [_format_review_out(r, db) for r in reviews]


# ------------------------------------------------------------
# 4. PATCH /api/v1/reviews/{review_id} - Update & Sync Vector
# ------------------------------------------------------------
@router.patch(
    "/reviews/{review_id}",
    response_model=FitReviewOut,
    summary="Update review (Owner or Admin)",
)
def update_review(
    review_id: int,
    review_in: FitReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Updates an existing FIT_REVIEW. Restricted to the author or an ADMIN.
    If review_text or overall_fit changes, regenerates the Redis Stack vector.
    """
    review = db.query(FitReview).filter(FitReview.review_id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review ID {review_id} not found.",
        )

    # Authorization guard: Owner or Admin
    if review.user_id != current_user.user_id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to modify this review.",
        )

    text_changed = False
    if review_in.overall_fit is not None:
        review.overall_fit = review_in.overall_fit
    if review_in.waist_fit is not None:
        review.waist_fit = review_in.waist_fit
    if review_in.hip_fit is not None:
        review.hip_fit = review_in.hip_fit
    if review_in.thigh_fit is not None:
        review.thigh_fit = review_in.thigh_fit
    if review_in.length_fit is not None:
        review.length_fit = review_in.length_fit
    if review_in.review_text is not None and review_in.review_text != review.review_text:
        review.review_text = review_in.review_text
        text_changed = True

    db.commit()
    db.refresh(review)

    # Synchronize Redis Stack vector index (UPDATE)
    try:
        upsert_review_vector(
            review_id=review.review_id,
            garment_size_id=review.garment_size_id,
            overall_fit=review.overall_fit,
            review_text=review.review_text,
        )
    except Exception as e:
        logger.warning(f"Vector sync warning on update: {e}")

    return _format_review_out(review, db)


# ------------------------------------------------------------
# 5. DELETE /api/v1/reviews/{review_id} - Delete & Remove Vector
# ------------------------------------------------------------
@router.delete(
    "/reviews/{review_id}",
    summary="Delete review (Owner or Admin)",
)
def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Deletes a review from MySQL (trigger logs into REVIEW_AUDIT)
    and removes its vector hash from Redis Stack.
    Restricted to author or ADMIN.
    """
    review = db.query(FitReview).filter(FitReview.review_id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review ID {review_id} not found.",
        )

    # Authorization guard: Owner or Admin
    if review.user_id != current_user.user_id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this review.",
        )

    db.delete(review)
    db.commit()

    # Synchronize Redis Stack vector index (DELETE)
    try:
        delete_review_vector(review_id)
    except Exception as e:
        logger.warning(f"Vector sync warning on delete: {e}")

    return {
        "success": True,
        "message": f"Review {review_id} successfully deleted from MySQL and vector index.",
    }


# ------------------------------------------------------------
# 6. POST /api/v1/reviews/search - Semantic Vector Search
# ------------------------------------------------------------
@router.post(
    "/reviews/search",
    response_model=List[ReviewSearchResult],
    summary="Semantic Vector Search for Fit Experiences",
)
def search_reviews(
    search_req: ReviewSearchRequest,
    db: Session = Depends(get_db),
):
    """
    Natural Language Semantic Search:
    1. Embeds the query using sentence-transformers/all-MiniLM-L6-v2.
    2. Performs KNN cosine vector retrieval in Redis Stack index 'fit_review_idx'.
    3. Retrieves authoritative relational records via 4-table MySQL JOIN:
       FIT_REVIEW -> GARMENT_SIZE -> GARMENT -> BRAND.
    4. Returns ranked results with semantic similarity scores and full context.
    """
    limit = search_req.limit or 5
    vector_hits = search_review_vectors(
        query_text=search_req.query,
        k=limit,
        overall_fit_filter=search_req.overall_fit,
    )

    if vector_hits:
        # Extract IDs and map scores
        hit_ids = [h[0] for h in vector_hits]
        score_map = {h[0]: h[1] for h in vector_hits}

        # Multi-table MySQL JOIN: Relational source of truth
        rows = (
            db.query(FitReview, GarmentSize, Garment, Brand)
            .join(GarmentSize, FitReview.garment_size_id == GarmentSize.garment_size_id)
            .join(Garment, GarmentSize.garment_id == Garment.garment_id)
            .join(Brand, Garment.brand_id == Brand.brand_id)
            .filter(FitReview.review_id.in_(hit_ids))
            .all()
        )

        results = []
        for review, size, garment, brand in rows:
            results.append(
                ReviewSearchResult(
                    review_id=review.review_id,
                    user_id=review.user_id,
                    garment_size_id=review.garment_size_id,
                    size_label=size.size_label,
                    garment_name=garment.garment_name,
                    brand_name=brand.brand_name,
                    overall_fit=review.overall_fit,
                    waist_fit=review.waist_fit,
                    hip_fit=review.hip_fit,
                    thigh_fit=review.thigh_fit,
                    length_fit=review.length_fit,
                    review_text=review.review_text,
                    similarity_score=score_map.get(review.review_id, 0.0),
                    created_at=review.created_at,
                )
            )

        # Preserve vector similarity ranking order
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results

    # Graceful fallback: If Redis Stack is offline or empty, search MySQL review_text
    query_pattern = f"%{search_req.query.strip()}%"
    filter_q = db.query(FitReview, GarmentSize, Garment, Brand)\
        .join(GarmentSize, FitReview.garment_size_id == GarmentSize.garment_size_id)\
        .join(Garment, GarmentSize.garment_id == Garment.garment_id)\
        .join(Brand, Garment.brand_id == Brand.brand_id)\
        .filter(FitReview.review_text.ilike(query_pattern))

    if search_req.overall_fit:
        filter_q = filter_q.filter(FitReview.overall_fit == search_req.overall_fit)

    fallback_rows = filter_q.limit(limit).all()
    results = []
    for review, size, garment, brand in fallback_rows:
        results.append(
            ReviewSearchResult(
                review_id=review.review_id,
                user_id=review.user_id,
                garment_size_id=review.garment_size_id,
                size_label=size.size_label,
                garment_name=garment.garment_name,
                brand_name=brand.brand_name,
                overall_fit=review.overall_fit,
                waist_fit=review.waist_fit,
                hip_fit=review.hip_fit,
                thigh_fit=review.thigh_fit,
                length_fit=review.length_fit,
                review_text=review.review_text,
                similarity_score=0.75,  # Relational text match fallback score
                created_at=review.created_at,
            )
        )
    return results


# ------------------------------------------------------------
# 7. GET /api/v1/admin/audit-logs - Admin Audit Trail (Admin only)
# ------------------------------------------------------------
@router.get(
    "/admin/audit-logs",
    response_model=List[ReviewAuditOut],
    summary="Inspect review lifecycle audit records (Admin only)",
)
def get_review_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Inspects audit entries written by database triggers on FIT_REVIEW.
    Requires ADMIN privileges. Demonstrates dual-layer RBAC and trigger execution.
    """
    logs = (
        db.query(ReviewAudit)
        .order_by(desc(ReviewAudit.changed_at))
        .limit(limit)
        .all()
    )
    return logs
