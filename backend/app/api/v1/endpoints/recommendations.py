from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models import User
from backend.app.schemas import RecommendationRequest, RecommendationResponse
from backend.app.services.recommendation_service import compute_size_recommendation
from backend.app.api.deps import get_optional_user

router = APIRouter()


@router.post("/recommendations", response_model=RecommendationResponse)
def get_recommendation(
    request: RecommendationRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """
    Computes an explainable cross-brand size recommendation for a target garment.
    Uses authenticated user profile/history if available, or manual request measurements.
    """
    # If request doesn't explicitly specify user_id, inherit from authenticated user
    if request.user_id is None and current_user is not None:
        request.user_id = current_user.user_id

    try:
        response = compute_size_recommendation(db=db, request=request)
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while computing size recommendations: {str(e)}",
        )
