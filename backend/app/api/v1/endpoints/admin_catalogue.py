"""ADMIN catalogue writes using the existing database constraints."""
from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.api.deps import require_admin
from backend.app.core.database import get_db
from backend.app.models import Garment, GarmentSize, GarmentMeasurement, User
from backend.app.schemas import GarmentSizeOut, GarmentMeasurementOut

router = APIRouter(prefix="/admin")


class CatalogueSizeCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    size_label: str = Field(..., min_length=1, max_length=20)

    @field_validator("size_label")
    @classmethod
    def nonblank_label(cls, value):
        if not value.strip():
            raise ValueError("Size label cannot be blank.")
        return value.strip()


class CatalogueMeasurementCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    measurement_type: Literal["waist", "hip", "thigh", "inseam", "rise"]
    measurement_value: Decimal = Field(..., gt=0, max_digits=6, decimal_places=2)
    unit: Literal["cm", "in"] = "cm"


@router.post("/garments/{garment_id}/sizes", response_model=GarmentSizeOut, status_code=status.HTTP_201_CREATED)
def add_size(
    garment_id: int, size: CatalogueSizeCreate,
    current_admin: User = Depends(require_admin), db: Session = Depends(get_db),
):
    if db.get(Garment, garment_id) is None:
        raise HTTPException(404, "Garment not found.")
    row = GarmentSize(garment_id=garment_id, size_label=size.size_label)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "This size already exists for the garment, or the garment is no longer available.") from None
    db.refresh(row)
    return row


@router.post("/garment-sizes/{garment_size_id}/measurements", response_model=GarmentMeasurementOut, status_code=status.HTTP_201_CREATED)
def add_measurement(
    garment_size_id: int, measurement: CatalogueMeasurementCreate,
    current_admin: User = Depends(require_admin), db: Session = Depends(get_db),
):
    if db.get(GarmentSize, garment_size_id) is None:
        raise HTTPException(404, "Size not found.")
    row = GarmentMeasurement(garment_size_id=garment_size_id, **measurement.model_dump())
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "That measurement type already exists for this size, or the size is no longer available.") from None
    db.refresh(row)
    return row


@router.delete("/garment-sizes/{garment_size_id}")
def delete_size(
    garment_size_id: int,
    current_admin: User = Depends(require_admin), db: Session = Depends(get_db),
):
    try:
        # Core DELETE bypasses ORM delete-orphan cascades: MySQL deletes measurements.
        result = db.execute(delete(GarmentSize.__table__).where(GarmentSize.garment_size_id == garment_size_id))
        if result.rowcount == 0:
            raise HTTPException(404, "Size not found.")
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "This size cannot be deleted because it is referenced by existing purchases or fit reviews.") from None
    return {"success": True}


@router.delete("/garments/{garment_id}")
def delete_garment(
    garment_id: int,
    current_admin: User = Depends(require_admin), db: Session = Depends(get_db),
):
    try:
        # Attempt only the parent deletion; let the existing FK reject dependent sizes.
        result = db.execute(delete(Garment.__table__).where(Garment.garment_id == garment_id))
        if result.rowcount == 0:
            raise HTTPException(404, "Garment not found.")
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "This garment cannot be deleted because it still has catalogue sizes. Remove its sizes first.") from None
    return {"success": True}
