from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models import BodyProfile, User
from backend.app.schemas import BodyProfileUpdate, BodyProfileOut
from backend.app.api.deps import get_optional_user, get_current_user

router = APIRouter()


@router.get("/profile", response_model=BodyProfileOut)
def get_profile(
    user_id: Optional[int] = Query(None, description="Optional user ID for testing/demo"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves the body profile for the current user.
    Uses authenticated user if available; falls back to user_id parameter for demo/testing.
    """
    target_user_id = current_user.user_id if current_user else user_id
    if not target_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required or provide a user_id parameter for demo/testing.",
        )

    profile = db.query(BodyProfile).filter(BodyProfile.user_id == target_user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Body profile for user ID {target_user_id} was not found.",
        )
    return profile


@router.put("/profile", response_model=BodyProfileOut)
def upsert_profile(
    profile_in: BodyProfileUpdate,
    user_id: Optional[int] = Query(None, description="Optional user ID for testing/demo"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """
    Creates or updates the body profile for the current user.
    """
    target_user_id = current_user.user_id if current_user else user_id
    if not target_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required or provide a user_id parameter for demo/testing.",
        )

    # Check that user exists
    user = db.query(User).filter(User.user_id == target_user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {target_user_id} does not exist.",
        )

    # Validate logical consistency: hip shouldn't be drastically smaller than waist if both provided
    if profile_in.waist is not None and profile_in.hip is not None:
        if profile_in.hip < profile_in.waist:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Hip measurement cannot be smaller than waist measurement.",
            )

    profile = db.query(BodyProfile).filter(BodyProfile.user_id == target_user_id).first()

    if not profile:
        profile = BodyProfile(
            user_id=target_user_id,
            height=profile_in.height,
            waist=profile_in.waist,
            hip=profile_in.hip,
            thigh=profile_in.thigh,
            inseam=profile_in.inseam,
            preferred_fit=profile_in.preferred_fit,
        )
        db.add(profile)
    else:
        if profile_in.height is not None:
            profile.height = profile_in.height
        if profile_in.waist is not None:
            profile.waist = profile_in.waist
        if profile_in.hip is not None:
            profile.hip = profile_in.hip
        if profile_in.thigh is not None:
            profile.thigh = profile_in.thigh
        if profile_in.inseam is not None:
            profile.inseam = profile_in.inseam
        if profile_in.preferred_fit is not None:
            profile.preferred_fit = profile_in.preferred_fit

    db.commit()
    db.refresh(profile)
    return profile
