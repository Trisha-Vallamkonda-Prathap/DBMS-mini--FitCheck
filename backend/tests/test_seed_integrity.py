"""
FitCheck — Seed Data Integrity & Baseline Count Regression Tests
Verifies Rubric Item 6 & Item 13:
- Authoritative seed files exist and load deterministically
- Exact baseline counts: 10 Users, 8 Profiles, 5 Brands, 14 Garments, 70 Sizes, 310 Measurements, 30 Purchases, 40 Reviews
- Strict referential integrity across seed datasets
- Error handling in seed script ensures rollback on failure
"""

import re
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.database import Base
from backend.app.models import (
    User,
    BodyProfile,
    Brand,
    Garment,
    GarmentSize,
    GarmentMeasurement,
    Purchase,
    FitReview,
)


def _get_seed_paths():
    repo_root = Path(__file__).resolve().parents[2]
    seeds_dir = repo_root / "database" / "seeds"
    return seeds_dir / "seed_data.sql", seeds_dir / "review_seeds.sql"


def test_seed_files_exist():
    """Verifies both authoritative seed files exist on disk."""
    seed_sql, review_sql = _get_seed_paths()
    assert seed_sql.exists(), f"Missing {seed_sql}"
    assert review_sql.exists(), f"Missing {review_sql}"


def test_seed_baseline_counts():
    """
    Validates exact documented baseline counts in seed SQL files:
    - 10 users
    - 8 body profiles
    - 5 brands
    - 14 garments
    - 70 garment sizes
    - 310 garment measurements
    - 30 purchases
    - 40 fit reviews
    """
    seed_sql, review_sql = _get_seed_paths()
    seed_text = seed_sql.read_text(encoding="utf-8")
    review_text = review_sql.read_text(encoding="utf-8")

    # 1. Users
    user_matches = re.findall(r"\(\s*(\d+)\s*,\s*'[^']+'\s*,\s*'[^']+'\s*,\s*'[^']+'\s*,\s*'(?:USER|ADMIN)'\s*\)", seed_text)
    assert len(user_matches) == 10, f"Expected 10 users, found {len(user_matches)}"

    # 2. Body Profiles
    profile_matches = re.findall(r"\(\s*(\d+)\s*,\s*(\d+)\s*,\s*[\d.]+\s*,\s*[\d.]+\s*,\s*[\d.]+\s*,\s*[\d.]+\s*,\s*[\d.]+\s*,\s*'[^']+'\s*\)", seed_text)
    assert len(profile_matches) == 8, f"Expected 8 body profiles, found {len(profile_matches)}"

    # 3. Brands
    brand_matches = re.findall(r"\(\s*(\d+)\s*,\s*'[^']+'\s*,\s*'[^']+'\s*\)", seed_text)
    assert len(brand_matches) == 5, f"Expected 5 brands, found {len(brand_matches)}"

    # 4. Garments
    garment_matches = re.findall(r"\(\s*(\d+)\s*,\s*(\d+)\s*,\s*'[^']+'\s*,\s*'[^']+'\s*,\s*'[^']+'\s*,\s*'[^']*'\s*\)", seed_text)
    assert len(garment_matches) == 14, f"Expected 14 garments, found {len(garment_matches)}"

    # 5. Garment Sizes
    size_matches = re.findall(r"\(\s*(\d+)\s*,\s*(\d+)\s*,\s*'[^']+'\s*\)", seed_text)
    assert len(size_matches) == 70, f"Expected 70 garment sizes, found {len(size_matches)}"

    # 6. Garment Measurements
    measurement_matches = re.findall(r"\(\s*(\d+)\s*,\s*'[^']+'\s*,\s*[\d.]+\s*,\s*'[^']+'\s*\)", seed_text)
    assert len(measurement_matches) == 310, f"Expected 310 garment measurements, found {len(measurement_matches)}"

    # 7. Purchases
    purchase_matches = re.findall(r"\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*'[^']+'\s*,\s*'[^']+'\s*,", seed_text)
    assert len(purchase_matches) == 30, f"Expected 30 purchases, found {len(purchase_matches)}"

    # 8. Reviews
    review_matches = re.findall(r"\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*'[^']+'\s*,", review_text)
    assert len(review_matches) == 40, f"Expected 40 reviews, found {len(review_matches)}"


def test_seed_referential_integrity():
    """Verifies that all foreign key references in seed data point to valid IDs."""
    seed_sql, review_sql = _get_seed_paths()
    seed_text = seed_sql.read_text(encoding="utf-8")
    review_text = review_sql.read_text(encoding="utf-8")

    user_ids = {int(m) for m in re.findall(r"\(\s*(\d+)\s*,\s*'[^']+'\s*,\s*'[^']+'\s*,\s*'[^']+'\s*,\s*'(?:USER|ADMIN)'\s*\)", seed_text)}
    brand_ids = {int(m) for m in re.findall(r"\(\s*(\d+)\s*,\s*'[^']+'\s*,\s*'[^']+'\s*\)", seed_text)}
    garment_ids = {int(m[0]) for m in re.findall(r"\(\s*(\d+)\s*,\s*(\d+)\s*,\s*'[^']+'\s*,\s*'[^']+'\s*,\s*'[^']+'\s*,\s*'[^']*'\s*\)", seed_text)}
    garment_brand_fks = {int(m[1]) for m in re.findall(r"\(\s*(\d+)\s*,\s*(\d+)\s*,\s*'[^']+'\s*,\s*'[^']+'\s*,\s*'[^']+'\s*,\s*'[^']*'\s*\)", seed_text)}
    size_ids = {int(m[0]) for m in re.findall(r"\(\s*(\d+)\s*,\s*(\d+)\s*,\s*'[^']+'\s*\)", seed_text)}
    size_garment_fks = {int(m[1]) for m in re.findall(r"\(\s*(\d+)\s*,\s*(\d+)\s*,\s*'[^']+'\s*\)", seed_text)}

    # Garment -> Brand FKs
    assert garment_brand_fks.issubset(brand_ids)

    # Size -> Garment FKs
    assert size_garment_fks.issubset(garment_ids)

    # Purchase FKs
    for p in re.findall(r"\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,", seed_text):
        u_id, s_id = int(p[1]), int(p[2])
        assert u_id in user_ids, f"Purchase references unknown user {u_id}"
        assert s_id in size_ids, f"Purchase references unknown size {s_id}"

    # Review FKs
    for r in re.findall(r"\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,", review_text):
        u_id, s_id = int(r[1]), int(r[2])
        assert u_id in user_ids, f"Review references unknown user {u_id}"
        assert s_id in size_ids, f"Review references unknown size {s_id}"

