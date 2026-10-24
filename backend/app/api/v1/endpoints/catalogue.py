from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from backend.app.core.database import get_db
from backend.app.models import Brand, Garment, GarmentSize, GarmentMeasurement
from backend.app.schemas import (
    BrandOut,
    GarmentOut,
    GarmentDetailOut,
    GarmentSizeOut,
    GarmentMeasurementOut,
)

router = APIRouter()


@router.get("/brands", response_model=List[BrandOut])
def get_brands(db: Session = Depends(get_db)):
    """Retrieves all apparel brands in the catalogue."""
    return db.query(Brand).order_by(Brand.brand_name).all()


@router.get("/garments", response_model=List[GarmentOut])
def get_garments(
    brand_id: Optional[int] = Query(None, description="Filter by brand ID"),
    category: Optional[str] = Query(None, description="Filter by category (Jeans, Trousers)"),
    db: Session = Depends(get_db),
):
    """
    Retrieves garments in the catalogue, with optional filtering by brand and/or category.
    """
    query = db.query(Garment).options(joinedload(Garment.brand))
    if brand_id:
        query = query.filter(Garment.brand_id == brand_id)
    if category:
        query = query.filter(Garment.garment_category == category)
    return query.order_by(Garment.garment_id).all()


@router.get("/garments/{garment_id}", response_model=GarmentDetailOut)
def get_garment_detail(garment_id: int, db: Session = Depends(get_db)):
    """Retrieves complete details of a garment including available sizes and measurements."""
    garment = (
        db.query(Garment)
        .options(
            joinedload(Garment.brand),
            joinedload(Garment.sizes).joinedload(GarmentSize.measurements),
        )
        .filter(Garment.garment_id == garment_id)
        .first()
    )
    if not garment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Garment with ID {garment_id} was not found.",
        )
    return garment


@router.get("/garments/{garment_id}/sizes", response_model=List[GarmentSizeOut])
def get_garment_sizes(garment_id: int, db: Session = Depends(get_db)):
    """Retrieves all sizes and their physical dimensions for a given garment."""
    garment = db.query(Garment).filter(Garment.garment_id == garment_id).first()
    if not garment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Garment with ID {garment_id} was not found.",
        )

    sizes = (
        db.query(GarmentSize)
        .options(joinedload(GarmentSize.measurements))
        .filter(GarmentSize.garment_id == garment_id)
        .order_by(GarmentSize.garment_size_id)
        .all()
    )
    return sizes
