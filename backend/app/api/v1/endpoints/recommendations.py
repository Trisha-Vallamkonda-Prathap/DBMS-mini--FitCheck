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
    # Enforce user isolation:
    # If user_id is specified, caller must be authenticated as that user (or ADMIN)
    if request.user_id is not None:
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to access user fit history. Provide direct manual measurements for guest recommendations.",
            )
        if current_user.user_id != request.user_id and current_user.role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: Cannot request recommendations on behalf of another user.",
            )
    elif current_user is not None:
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
