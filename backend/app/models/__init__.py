from datetime import datetime, date
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Numeric,
    Date,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    func,
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class User(Base):
    __tablename__ = "USER"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(10), nullable=False, default="USER")
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint("role IN ('USER', 'ADMIN')", name="chk_user_role"),
    )

    # Relationships
    body_profile = relationship("BodyProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    purchases = relationship("Purchase", back_populates="user")
    reviews = relationship("FitReview", back_populates="user")


class BodyProfile(Base):
    __tablename__ = "BODY_PROFILE"

    profile_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("USER.user_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        unique=True,
    )
    height = Column(Numeric(5, 2), nullable=True)
    waist = Column(Numeric(5, 2), nullable=True)
    hip = Column(Numeric(5, 2), nullable=True)
    thigh = Column(Numeric(5, 2), nullable=True)
    inseam = Column(Numeric(5, 2), nullable=True)
    preferred_fit = Column(String(20), nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        CheckConstraint("height IS NULL OR height > 0", name="chk_profile_height"),
        CheckConstraint("waist IS NULL OR waist > 0", name="chk_profile_waist"),
        CheckConstraint("hip IS NULL OR hip > 0", name="chk_profile_hip"),
        CheckConstraint("thigh IS NULL OR thigh > 0", name="chk_profile_thigh"),
        CheckConstraint("inseam IS NULL OR inseam > 0", name="chk_profile_inseam"),
        CheckConstraint("preferred_fit IS NULL OR preferred_fit IN ('TIGHT', 'REGULAR', 'RELAXED')", name="chk_profile_fit"),
    )

    user = relationship("User", back_populates="body_profile")


class Brand(Base):
    __tablename__ = "BRAND"

    brand_id = Column(Integer, primary_key=True, autoincrement=True)
    brand_name = Column(String(100), nullable=False, unique=True)
    sizing_system = Column(String(20), nullable=False)

    __table_args__ = (
        CheckConstraint("sizing_system IN ('ALPHA', 'NUMERIC', 'WAIST_BASED')", name="chk_brand_sizing"),
    )

    garments = relationship("Garment", back_populates="brand")


class Garment(Base):
    __tablename__ = "GARMENT"

    garment_id = Column(Integer, primary_key=True, autoincrement=True)
    brand_id = Column(
        Integer,
        ForeignKey("BRAND.brand_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    garment_name = Column(String(150), nullable=False)
    garment_category = Column(String(30), nullable=False)
    fit_type = Column(String(30), nullable=False)
    description = Column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint("garment_category IN ('Jeans', 'Trousers')", name="chk_garment_category"),
        CheckConstraint(
            "fit_type IN ('STRAIGHT', 'SLIM', 'SKINNY', 'WIDE_LEG', 'RELAXED', 'BOOTCUT', 'FLARED', 'OTHER')",
            name="chk_garment_fit",
        ),
    )

    brand = relationship("Brand", back_populates="garments")
    sizes = relationship("GarmentSize", back_populates="garment")


class GarmentSize(Base):
    __tablename__ = "GARMENT_SIZE"

    garment_size_id = Column(Integer, primary_key=True, autoincrement=True)
    garment_id = Column(
        Integer,
        ForeignKey("GARMENT.garment_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    size_label = Column(String(20), nullable=False)

    __table_args__ = (
        UniqueConstraint("garment_id", "size_label", name="uq_garment_size"),
    )

    garment = relationship("Garment", back_populates="sizes")
    measurements = relationship("GarmentMeasurement", back_populates="garment_size", cascade="all, delete-orphan")
    purchases = relationship("Purchase", back_populates="garment_size")
    reviews = relationship("FitReview", back_populates="garment_size")


class GarmentMeasurement(Base):
    __tablename__ = "GARMENT_MEASUREMENT"

    measurement_id = Column(Integer, primary_key=True, autoincrement=True)
    garment_size_id = Column(
        Integer,
        ForeignKey("GARMENT_SIZE.garment_size_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    measurement_type = Column(String(20), nullable=False)
    measurement_value = Column(Numeric(6, 2), nullable=False)
    unit = Column(String(5), nullable=False, default="cm")

    __table_args__ = (
        UniqueConstraint("garment_size_id", "measurement_type", name="uq_size_measurement"),
        CheckConstraint("measurement_type IN ('waist', 'hip', 'thigh', 'inseam', 'rise')", name="chk_measurement_type"),
        CheckConstraint("measurement_value > 0", name="chk_measurement_value"),
        CheckConstraint("unit IN ('cm', 'in')", name="chk_measurement_unit"),
    )

    garment_size = relationship("GarmentSize", back_populates="measurements")


class Purchase(Base):
    __tablename__ = "PURCHASE"

    purchase_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("USER.user_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    garment_size_id = Column(
        Integer,
        ForeignKey("GARMENT_SIZE.garment_size_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    purchase_date = Column(Date, nullable=False, default=date.today)
    outcome = Column(String(10), nullable=False)
    fit_satisfaction = Column(String(10), nullable=True)
    fit_preference = Column(String(20), nullable=True)

    __table_args__ = (
        CheckConstraint("outcome IN ('KEPT', 'RETURNED', 'EXCHANGED')", name="chk_purchase_outcome"),
        CheckConstraint("fit_satisfaction IS NULL OR fit_satisfaction IN ('GOOD', 'AVERAGE', 'POOR')", name="chk_purchase_satisfaction"),
        CheckConstraint("fit_preference IS NULL OR fit_preference IN ('TIGHT', 'REGULAR', 'RELAXED')", name="chk_purchase_preference"),
    )

    user = relationship("User", back_populates="purchases")
    garment_size = relationship("GarmentSize", back_populates="purchases")


class FitReview(Base):
    __tablename__ = "FIT_REVIEW"

    review_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("USER.user_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    garment_size_id = Column(
        Integer,
        ForeignKey("GARMENT_SIZE.garment_size_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    overall_fit = Column(String(20), nullable=False)
    waist_fit = Column(String(10), nullable=True)
    hip_fit = Column(String(10), nullable=True)
    thigh_fit = Column(String(10), nullable=True)
    length_fit = Column(String(10), nullable=True)
    review_text = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "overall_fit IN ('TOO_SMALL', 'SLIGHTLY_SMALL', 'TRUE_TO_SIZE', 'SLIGHTLY_LARGE', 'TOO_LARGE')",
            name="chk_review_overall_fit",
        ),
        CheckConstraint("waist_fit IS NULL OR waist_fit IN ('TIGHT', 'GOOD', 'LOOSE')", name="chk_review_waist_fit"),
        CheckConstraint("hip_fit IS NULL OR hip_fit IN ('TIGHT', 'GOOD', 'LOOSE')", name="chk_review_hip_fit"),
        CheckConstraint("thigh_fit IS NULL OR thigh_fit IN ('TIGHT', 'GOOD', 'LOOSE')", name="chk_review_thigh_fit"),
        CheckConstraint("length_fit IS NULL OR length_fit IN ('SHORT', 'GOOD', 'LONG')", name="chk_review_length_fit"),
        CheckConstraint("CHAR_LENGTH(TRIM(review_text)) > 0", name="chk_review_text"),
    )

    user = relationship("User", back_populates="reviews")
    garment_size = relationship("GarmentSize", back_populates="reviews")


class ReviewAudit(Base):
    __tablename__ = "REVIEW_AUDIT"

    audit_id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(Integer, nullable=False, index=True)
    action = Column(String(10), nullable=False)
    user_id = Column(Integer, nullable=True)
    changed_at = Column(DateTime, nullable=False, server_default=func.now())
    details = Column(Text, nullable=True)
