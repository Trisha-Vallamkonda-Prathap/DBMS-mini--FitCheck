from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator


# ------------------------------------------------------------
# Authentication & User Schemas
# ------------------------------------------------------------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None


class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)
    role: Optional[str] = "USER"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(UserBase):
    user_id: int
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# ------------------------------------------------------------
# Body Profile Schemas
# ------------------------------------------------------------
class BodyProfileBase(BaseModel):
    height: Optional[float] = Field(None, gt=0, le=250)
    waist: Optional[float] = Field(None, gt=0, le=180)
    hip: Optional[float] = Field(None, gt=0, le=220)
    thigh: Optional[float] = Field(None, gt=0, le=120)
    inseam: Optional[float] = Field(None, gt=0, le=120)
    preferred_fit: Optional[str] = Field(None, pattern="^(TIGHT|REGULAR|RELAXED)$")


class BodyProfileCreate(BodyProfileBase):
    pass


class BodyProfileUpdate(BodyProfileBase):
    pass


class BodyProfileOut(BodyProfileBase):
    profile_id: int
    user_id: int
    updated_at: datetime

    class Config:
        from_attributes = True


# ------------------------------------------------------------
# Brand & Garment Catalogue Schemas
# ------------------------------------------------------------
class BrandBase(BaseModel):
    brand_name: str = Field(..., max_length=100)
    sizing_system: str = Field(..., pattern="^(ALPHA|NUMERIC|WAIST_BASED)$")


class BrandOut(BrandBase):
    brand_id: int

    class Config:
        from_attributes = True


class GarmentMeasurementBase(BaseModel):
    measurement_type: str = Field(..., pattern="^(waist|hip|thigh|inseam|rise)$")
    measurement_value: float = Field(..., gt=0)
    unit: str = Field(default="cm", pattern="^(cm|in)$")


class GarmentMeasurementOut(GarmentMeasurementBase):
    measurement_id: int
    garment_size_id: int

    class Config:
        from_attributes = True


class GarmentSizeBase(BaseModel):
    size_label: str = Field(..., max_length=20)


class GarmentSizeOut(GarmentSizeBase):
    garment_size_id: int
    garment_id: int
    measurements: List[GarmentMeasurementOut] = []

    class Config:
        from_attributes = True


class GarmentBase(BaseModel):
    brand_id: int
    garment_name: str = Field(..., max_length=150)
    garment_category: str = Field(..., pattern="^(Jeans|Trousers)$")
    fit_type: str = Field(..., pattern="^(STRAIGHT|SLIM|SKINNY|WIDE_LEG|RELAXED|BOOTCUT|FLARED|OTHER)$")
    description: Optional[str] = None


class GarmentOut(GarmentBase):
    garment_id: int
    brand: Optional[BrandOut] = None

    class Config:
        from_attributes = True


class GarmentDetailOut(GarmentOut):
    sizes: List[GarmentSizeOut] = []

    class Config:
        from_attributes = True


# ------------------------------------------------------------
# Purchase History Schemas
# ------------------------------------------------------------
class PurchaseBase(BaseModel):
    garment_size_id: int
    purchase_date: Optional[date] = None
    outcome: str = Field(..., pattern="^(KEPT|RETURNED|EXCHANGED)$")
    fit_satisfaction: Optional[str] = Field(None, pattern="^(GOOD|AVERAGE|POOR)$")
    fit_preference: Optional[str] = Field(None, pattern="^(TIGHT|REGULAR|RELAXED)$")


class PurchaseCreate(PurchaseBase):
    pass


class PurchaseOut(PurchaseBase):
    purchase_id: int
    user_id: int
    purchase_date: date
    garment_name: Optional[str] = None
    brand_name: Optional[str] = None
    size_label: Optional[str] = None

    class Config:
        from_attributes = True


# ------------------------------------------------------------
# Recommendation Schemas
# ------------------------------------------------------------
class RecommendationRequest(BaseModel):
    target_garment_id: int
    user_id: Optional[int] = None
    waist: Optional[float] = Field(None, gt=0, le=180)
    hip: Optional[float] = Field(None, gt=0, le=220)
    thigh: Optional[float] = Field(None, gt=0, le=120)
    inseam: Optional[float] = Field(None, gt=0, le=120)
    preferred_fit: Optional[str] = Field(None, pattern="^(TIGHT|REGULAR|RELAXED)$")


class DimensionalDelta(BaseModel):
    dimension: str
    garment_value_cm: float
    reference_value_cm: float
    delta_cm: float


class SizeScoreBreakdown(BaseModel):
    garment_size_id: int
    size_label: str
    match_score: float
    rank: int
    fit_verdict: str
    deltas: List[DimensionalDelta] = []
    notes: List[str] = []


class RecommendationResponse(BaseModel):
    target_garment_id: int
    target_garment_name: str
    target_brand_name: str
    category: str
    fit_type: str
    primary_recommendation: Optional[SizeScoreBreakdown] = None
    top_recommendations: List[SizeScoreBreakdown] = []
    all_sizes_ranked: List[SizeScoreBreakdown] = []
    evidence_sources: List[str] = []
    confidence: str
    explanation: str
    caveats: List[str] = []


# ------------------------------------------------------------
# Health & Status Schemas
# ------------------------------------------------------------
class HealthStatus(BaseModel):
    status: str
    environment: str
    mysql_connected: bool
    redis_connected: bool
    timestamp: datetime


# ------------------------------------------------------------
# Fit Review & Semantic Search Schemas (Member B)
# ------------------------------------------------------------
OVERALL_FIT_PATTERN = "^(TOO_SMALL|SLIGHTLY_SMALL|TRUE_TO_SIZE|SLIGHTLY_LARGE|TOO_LARGE)$"
WAIST_FIT_PATTERN = "^(TIGHT|GOOD|LOOSE)$"
HIP_FIT_PATTERN = "^(TIGHT|GOOD|LOOSE)$"
THIGH_FIT_PATTERN = "^(TIGHT|GOOD|LOOSE)$"
LENGTH_FIT_PATTERN = "^(SHORT|GOOD|LONG)$"


class FitReviewBase(BaseModel):
    garment_size_id: int
    overall_fit: str = Field(..., pattern=OVERALL_FIT_PATTERN)
    waist_fit: Optional[str] = Field(None, pattern=WAIST_FIT_PATTERN)
    hip_fit: Optional[str] = Field(None, pattern=HIP_FIT_PATTERN)
    thigh_fit: Optional[str] = Field(None, pattern=THIGH_FIT_PATTERN)
    length_fit: Optional[str] = Field(None, pattern=LENGTH_FIT_PATTERN)
    review_text: str = Field(...)

    @field_validator("review_text")
    @classmethod
    def validate_non_whitespace(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Review text cannot be empty or whitespace only.")
        return v.strip()


class FitReviewCreate(FitReviewBase):
    pass


class FitReviewUpdate(BaseModel):
    overall_fit: Optional[str] = Field(None, pattern=OVERALL_FIT_PATTERN)
    waist_fit: Optional[str] = Field(None, pattern=WAIST_FIT_PATTERN)
    hip_fit: Optional[str] = Field(None, pattern=HIP_FIT_PATTERN)
    thigh_fit: Optional[str] = Field(None, pattern=THIGH_FIT_PATTERN)
    length_fit: Optional[str] = Field(None, pattern=LENGTH_FIT_PATTERN)
    review_text: Optional[str] = None

    @field_validator("review_text")
    @classmethod
    def validate_non_whitespace(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Review text cannot be empty or whitespace only.")
        return v.strip() if v is not None else None


class FitReviewOut(FitReviewBase):
    review_id: int
    user_id: int
    created_at: datetime
    garment_name: Optional[str] = None
    brand_name: Optional[str] = None
    size_label: Optional[str] = None

    class Config:
        from_attributes = True


class ReviewSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: Optional[int] = Field(5, ge=1, le=50)
    overall_fit: Optional[str] = Field(None, pattern=OVERALL_FIT_PATTERN)

    @field_validator("query")
    @classmethod
    def validate_query_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Query string cannot be empty.")
        return v.strip()


class ReviewSearchResult(BaseModel):
    review_id: int
    user_id: int
    garment_size_id: int
    size_label: str
    garment_name: str
    brand_name: str
    overall_fit: str
    waist_fit: Optional[str] = None
    hip_fit: Optional[str] = None
    thigh_fit: Optional[str] = None
    length_fit: Optional[str] = None
    review_text: str
    similarity_score: float
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewAuditOut(BaseModel):
    audit_id: int
    review_id: int
    action: str
    user_id: Optional[int] = None
    changed_at: datetime
    details: Optional[str] = None

    class Config:
        from_attributes = True
