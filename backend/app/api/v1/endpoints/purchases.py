from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from backend.app.core.database import get_db
from backend.app.models import Purchase, GarmentSize, Garment, Brand, User
from backend.app.schemas import PurchaseCreate, PurchaseOut
from backend.app.api.deps import get_optional_user

router = APIRouter()


@router.get("/purchases", response_model=List[PurchaseOut])
def get_purchases(
    user_id: Optional[int] = Query(None, description="Optional user ID for testing/demo"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves purchase history for the current user.
    Includes joined garment name, brand name, and size label.
    """
    target_user_id = current_user.user_id if current_user else user_id
    if not target_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required or provide a user_id parameter for demo/testing.",
        )

    purchases = (
        db.query(Purchase)
        .options(
            joinedload(Purchase.garment_size)
            .joinedload(GarmentSize.garment)
            .joinedload(Garment.brand)
        )
        .filter(Purchase.user_id == target_user_id)
        .order_by(Purchase.purchase_date.desc(), Purchase.purchase_id.desc())
        .all()
    )

    result = []
    for p in purchases:
        size = p.garment_size
        garment = size.garment if size else None
        brand = garment.brand if garment else None

        result.append(
            PurchaseOut(
                purchase_id=p.purchase_id,
                user_id=p.user_id,
                garment_size_id=p.garment_size_id,
                purchase_date=p.purchase_date,
                outcome=p.outcome,
                fit_satisfaction=p.fit_satisfaction,
                fit_preference=p.fit_preference,
                brand_name=brand.brand_name if brand else None,
                garment_name=garment.garment_name if garment else None,
                size_label=size.size_label if size else None,
            )
        )
    return result


@router.post("/purchases", response_model=PurchaseOut, status_code=status.HTTP_201_CREATED)
def create_purchase(
    purchase_in: PurchaseCreate,
    user_id: Optional[int] = Query(None, description="Optional user ID for testing/demo"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """
    Records a new purchase and fit outcome for the current user.
    Validates that the garment size exists.
    """
    target_user_id = current_user.user_id if current_user else user_id
    if not target_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required or provide a user_id parameter for demo/testing.",
        )

    # Validate target user exists
    user = db.query(User).filter(User.user_id == target_user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {target_user_id} was not found.",
        )

    # Validate garment_size_id exists
    garment_size = (
        db.query(GarmentSize)
        .options(joinedload(GarmentSize.garment).joinedload(Garment.brand))
        .filter(GarmentSize.garment_size_id == purchase_in.garment_size_id)
        .first()
    )
    if not garment_size:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"GarmentSize with ID {purchase_in.garment_size_id} does not exist.",
        )

    new_purchase = Purchase(
        user_id=target_user_id,
        garment_size_id=purchase_in.garment_size_id,
        purchase_date=purchase_in.purchase_date or date.today(),
        outcome=purchase_in.outcome,
        fit_satisfaction=purchase_in.fit_satisfaction,
        fit_preference=purchase_in.fit_preference,
    )
    db.add(new_purchase)
    db.commit()
    db.refresh(new_purchase)

    garment = garment_size.garment
    brand = garment.brand if garment else None

    return PurchaseOut(
        purchase_id=new_purchase.purchase_id,
        user_id=new_purchase.user_id,
        garment_size_id=new_purchase.garment_size_id,
        purchase_date=new_purchase.purchase_date,
        outcome=new_purchase.outcome,
        fit_satisfaction=new_purchase.fit_satisfaction,
        fit_preference=new_purchase.fit_preference,
        brand_name=brand.brand_name if brand else None,
        garment_name=garment.garment_name if garment else None,
        size_label=garment_size.size_label,
    )
