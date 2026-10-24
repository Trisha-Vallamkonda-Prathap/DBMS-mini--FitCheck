import math
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.models import (
    Brand,
    Garment,
    GarmentSize,
    GarmentMeasurement,
    BodyProfile,
    Purchase,
    User,
)
from backend.app.schemas import (
    RecommendationRequest,
    RecommendationResponse,
    SizeScoreBreakdown,
    DimensionalDelta,
)


# Unit conversion constant
INCHES_TO_CM = 2.54

# Dimension weights (must sum to 1.0 when all present)
DEFAULT_WEIGHTS = {
    "waist": 0.45,
    "hip": 0.35,
    "thigh": 0.12,
    "inseam": 0.08,
}

# Ease allowances (cm) added to anatomical body measurements
EASE_ALLOWANCES = {
    "TIGHT": {"waist": 0.0, "hip": 0.5, "thigh": 0.0},
    "REGULAR": {"waist": 1.5, "hip": 2.5, "thigh": 1.5},
    "RELAXED": {"waist": 3.0, "hip": 4.5, "thigh": 3.0},
}


def normalize_to_cm(value: float, unit: str) -> float:
    """Normalizes any measurement value to centimeters."""
    if unit.lower() in ("in", "inch", "inches"):
        return round(value * INCHES_TO_CM, 2)
    return round(float(value), 2)


def get_user_reference_dimensions(
    db: Session,
    user_id: Optional[int],
    manual_override: Optional[Dict[str, Any]] = None,
) -> Tuple[Dict[str, float], List[str], str]:
    """
    Synthesizes reference dimensions from:
    1. Direct manual override inputs (if provided)
    2. User's BodyProfile (anatomical ground truth + preferred fit ease)
    3. User's successful purchase history (KEPT & GOOD fit satisfaction)
    
    Returns:
        (reference_dimensions_cm, evidence_sources, confidence_level)
    """
    ref_dims: Dict[str, float] = {}
    evidence: List[str] = []
    
    # 1. Manual override inputs
    if manual_override:
        for dim in ("waist", "hip", "thigh", "inseam"):
            val = manual_override.get(dim)
            if val is not None and float(val) > 0:
                ref_dims[dim] = float(val)
        if ref_dims:
            pref_fit = manual_override.get("preferred_fit") or "REGULAR"
            ease = EASE_ALLOWANCES.get(pref_fit, EASE_ALLOWANCES["REGULAR"])
            for dim, add_ease in ease.items():
                if dim in ref_dims:
                    ref_dims[dim] = round(ref_dims[dim] + add_ease, 2)
            evidence.append(f"Direct manual input measurements (fit preference: {pref_fit})")
            return ref_dims, evidence, "HIGH"

    if not user_id:
        return {}, ["No user profile or manual measurements provided"], "INSUFFICIENT_DATA"

    # 2. Check User Body Profile
    profile = db.query(BodyProfile).filter(BodyProfile.user_id == user_id).first()
    has_profile = False
    profile_dims: Dict[str, float] = {}
    if profile:
        pref_fit = profile.preferred_fit or "REGULAR"
        ease = EASE_ALLOWANCES.get(pref_fit, EASE_ALLOWANCES["REGULAR"])
        for dim in ("waist", "hip", "thigh", "inseam"):
            val = getattr(profile, dim)
            if val is not None and float(val) > 0:
                profile_dims[dim] = round(float(val) + ease.get(dim, 0.0), 2)
                has_profile = True
        if has_profile:
            evidence.append(
                f"Body Profile (Waist: {profile.waist}cm, Hip: {profile.hip}cm, Ease: {pref_fit})"
            )

    # 3. Check Successful Purchase History (KEPT & GOOD)
    successful_purchases = (
        db.query(Purchase)
        .filter(
            Purchase.user_id == user_id,
            Purchase.outcome == "KEPT",
            Purchase.fit_satisfaction == "GOOD",
        )
        .all()
    )

    purchase_dims: Dict[str, List[float]] = {"waist": [], "hip": [], "thigh": [], "inseam": []}
    for p in successful_purchases:
        garment_size = p.garment_size
        if not garment_size:
            continue
        garment = garment_size.garment
        brand_name = garment.brand.brand_name if garment and garment.brand else "Unknown"
        evidence.append(
            f"Kept purchase: {brand_name} {garment.garment_name} (Size {garment_size.size_label})"
        )
        for m in garment_size.measurements:
            m_type = m.measurement_type.lower()
            if m_type in purchase_dims:
                val_cm = normalize_to_cm(float(m.measurement_value), m.unit)
                purchase_dims[m_type].append(val_cm)

    # Calculate average dimensions from kept purchases
    avg_purchase_dims = {
        dim: round(sum(vals) / len(vals), 2)
        for dim, vals in purchase_dims.items()
        if vals
    }

    # Synthesize reference dimensions
    if avg_purchase_dims and has_profile:
        # Blend: 60% purchase history ground truth + 40% body profile
        for dim in set(list(avg_purchase_dims.keys()) + list(profile_dims.keys())):
            p_val = avg_purchase_dims.get(dim)
            b_val = profile_dims.get(dim)
            if p_val and b_val:
                ref_dims[dim] = round(0.60 * p_val + 0.40 * b_val, 2)
            elif p_val:
                ref_dims[dim] = p_val
            elif b_val:
                ref_dims[dim] = b_val
        confidence = "HIGH"
    elif avg_purchase_dims:
        ref_dims = avg_purchase_dims
        confidence = "HIGH" if len(successful_purchases) >= 2 else "MEDIUM"
    elif has_profile:
        ref_dims = profile_dims
        confidence = "MEDIUM"
    else:
        confidence = "INSUFFICIENT_DATA"

    return ref_dims, evidence, confidence


def compute_size_recommendation(
    db: Session,
    request: RecommendationRequest,
) -> RecommendationResponse:
    """
    Executes the explainable cross-brand recommendation algorithm.
    Ranks target garment sizes against synthesized reference measurements.
    """
    target_garment = (
        db.query(Garment)
        .filter(Garment.garment_id == request.target_garment_id)
        .first()
    )
    if not target_garment:
        raise ValueError(f"Target garment with ID {request.target_garment_id} does not exist.")

    brand_name = target_garment.brand.brand_name if target_garment.brand else "Unknown"

    # Retrieve all available sizes and their measurements
    sizes = (
        db.query(GarmentSize)
        .filter(GarmentSize.garment_id == target_garment.garment_id)
        .all()
    )
    if not sizes:
        raise ValueError(f"Garment '{target_garment.garment_name}' has no registered sizes.")

    manual_inputs = {}
    if request.waist:
        manual_inputs["waist"] = request.waist
    if request.hip:
        manual_inputs["hip"] = request.hip
    if request.thigh:
        manual_inputs["thigh"] = request.thigh
    if request.inseam:
        manual_inputs["inseam"] = request.inseam
    if request.preferred_fit:
        manual_inputs["preferred_fit"] = request.preferred_fit

    ref_dims, evidence, confidence = get_user_reference_dimensions(
        db=db,
        user_id=request.user_id,
        manual_override=manual_inputs if manual_inputs else None,
    )

    caveats: List[str] = []
    if target_garment.fit_type in ("SKINNY", "SLIM"):
        caveats.append(f"Garment fit is {target_garment.fit_type}: cut is tailored closer to the body.")
    elif target_garment.fit_type in ("WIDE_LEG", "RELAXED"):
        caveats.append(f"Garment fit is {target_garment.fit_type}: silhouette has built-in generous ease.")

    # Cold start: if insufficient reference data
    if confidence == "INSUFFICIENT_DATA" or not ref_dims:
        median_idx = len(sizes) // 2
        median_size = sizes[median_idx]
        all_ranked = [
            SizeScoreBreakdown(
                garment_size_id=s.garment_size_id,
                size_label=s.size_label,
                match_score=50.0 if s.garment_size_id == median_size.garment_size_id else 40.0,
                rank=1 if s.garment_size_id == median_size.garment_size_id else 2,
                fit_verdict="Catalog Median (Cold Start)",
                deltas=[],
                notes=["No user purchase history or body profile found."],
            )
            for s in sizes
        ]
        return RecommendationResponse(
            target_garment_id=target_garment.garment_id,
            target_garment_name=target_garment.garment_name,
            target_brand_name=brand_name,
            category=target_garment.garment_category,
            fit_type=target_garment.fit_type,
            primary_recommendation=all_ranked[0],
            all_sizes_ranked=all_ranked,
            evidence_sources=["Cold-start fallback: median size selected"],
            confidence="INSUFFICIENT_DATA",
            explanation=(
                "No reference measurements were available. Please provide your body profile "
                "or log past successful purchases to receive calibrated size recommendations."
            ),
            caveats=["Recommendation is uncalibrated."],
        )

    scored_sizes: List[SizeScoreBreakdown] = []

    for size_obj in sizes:
        measurements_by_type: Dict[str, float] = {}
        for m in size_obj.measurements:
            m_type = m.measurement_type.lower()
            val_cm = normalize_to_cm(float(m.measurement_value), m.unit)
            measurements_by_type[m_type] = val_cm

        deltas: List[DimensionalDelta] = []
        weighted_delta_sum = 0.0
        applied_weight_sum = 0.0
        notes: List[str] = []

        for dim, default_weight in DEFAULT_WEIGHTS.items():
            if dim in ref_dims and dim in measurements_by_type:
                g_val = measurements_by_type[dim]
                r_val = ref_dims[dim]
                diff = round(g_val - r_val, 2)
                abs_diff = abs(diff)

                deltas.append(
                    DimensionalDelta(
                        dimension=dim,
                        garment_value_cm=g_val,
                        reference_value_cm=r_val,
                        delta_cm=diff,
                    )
                )

                weighted_delta_sum += default_weight * abs_diff
                applied_weight_sum += default_weight

                # Qualitative dimensional feedback
                if dim == "waist":
                    if diff < -1.5:
                        notes.append(f"Waist is {abs(diff):.1f}cm tighter than reference")
                    elif diff > 2.0:
                        notes.append(f"Waist is {diff:.1f}cm looser than reference")
                elif dim == "hip":
                    if diff < -2.0:
                        notes.append(f"Hip is {abs(diff):.1f}cm snugger than reference")

        # Normalize composite delta by active weights
        if applied_weight_sum > 0:
            effective_delta = weighted_delta_sum / applied_weight_sum
        else:
            effective_delta = 99.0

        # Exponential decay scoring function: score = 100 * exp(-delta / 4.0)
        score = round(max(0.0, min(100.0, 100.0 * math.exp(-effective_delta / 4.0))), 1)

        # Fit verdict
        if effective_delta <= 1.0:
            verdict = "Optimal Fit"
        elif effective_delta <= 2.2:
            verdict = "Very Close Fit"
        elif effective_delta <= 4.0:
            verdict = "Moderate Variance"
        else:
            verdict = "Poor Fit"

        scored_sizes.append(
            SizeScoreBreakdown(
                garment_size_id=size_obj.garment_size_id,
                size_label=size_obj.size_label,
                match_score=score,
                rank=0,  # Will assign after sort
                fit_verdict=verdict,
                deltas=deltas,
                notes=notes,
            )
        )

    # Sort descending by match score
    scored_sizes.sort(key=lambda s: s.match_score, reverse=True)

    # Assign ranks
    for idx, s in enumerate(scored_sizes):
        s.rank = idx + 1

    primary = scored_sizes[0] if scored_sizes else None

    # Construct transparent explanation
    ref_summary = ", ".join([f"{k.capitalize()}: {v}cm" for k, v in ref_dims.items()])
    explanation = (
        f"Recommended size '{primary.size_label}' with a {primary.match_score:.1f}% match score. "
        f"Compared against reference dimensions ({ref_summary}) synthesized from "
        f"{len(evidence)} verified data point(s)."
    )

    return RecommendationResponse(
        target_garment_id=target_garment.garment_id,
        target_garment_name=target_garment.garment_name,
        target_brand_name=brand_name,
        category=target_garment.garment_category,
        fit_type=target_garment.fit_type,
        primary_recommendation=primary,
        all_sizes_ranked=scored_sizes,
        evidence_sources=evidence,
        confidence=confidence,
        explanation=explanation,
        caveats=caveats,
    )
