from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models import BodyProfile, User
from backend.app.schemas import BodyProfileUpdate, BodyProfileOut
from backend.app.api.deps import get_current_user

router = APIRouter()


@router.get("/profile", response_model=BodyProfileOut)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves the body profile for the authenticated user.
    Strictly isolated: users can only access their own profile.
    """
    profile = db.query(BodyProfile).filter(BodyProfile.user_id == current_user.user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Body profile for user '{current_user.name}' was not found.",
        )
    return profile


@router.put("/profile", response_model=BodyProfileOut)
def upsert_profile(
    profile_in: BodyProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Creates or updates the body profile for the authenticated user.
    Strictly isolated: users can only modify their own profile.
    """
    profile = db.query(BodyProfile).filter(BodyProfile.user_id == current_user.user_id).first()

    if not profile:
        profile = BodyProfile(
            user_id=current_user.user_id,
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
