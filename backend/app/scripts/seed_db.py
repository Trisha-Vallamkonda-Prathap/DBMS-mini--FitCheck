import os
import sys
from pathlib import Path
from sqlalchemy import text
from backend.app.core.database import engine, SessionLocal
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


def seed_database():
    """Executes deterministic seed SQL scripts against the configured database."""
    seeds_dir = Path(__file__).resolve().parents[3] / "database" / "seeds"
    seed_sql_path = seeds_dir / "seed_data.sql"
    review_seeds_path = seeds_dir / "review_seeds.sql"

    if not seed_sql_path.exists():
        print(f"Error: Seed file not found at {seed_sql_path}")
        sys.exit(1)

    seed_files = [seed_sql_path]
    if review_seeds_path.exists():
        seed_files.append(review_seeds_path)

    for current_file in seed_files:
        print(f"Loading seed data from {current_file.name}...")
        with open(current_file, "r", encoding="utf-8") as f:
            sql_content = f.read()

        statements = []
        for stmt in sql_content.split(";"):
            cleaned = stmt.strip()
            if not cleaned:
                continue
            if cleaned.upper().startswith("USE "):
                continue
            statements.append(cleaned)

        print(f"Executing {len(statements)} SQL statements from {current_file.name}...")
        with engine.begin() as conn:
            for idx, stmt in enumerate(statements, 1):
                try:
                    conn.execute(text(stmt))
                except Exception as e:
                    print(f"Warning on statement {idx}: {e}")

    # Verify counts
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        profile_count = db.query(BodyProfile).count()
        brand_count = db.query(Brand).count()
        garment_count = db.query(Garment).count()
        size_count = db.query(GarmentSize).count()
        measurement_count = db.query(GarmentMeasurement).count()
        purchase_count = db.query(Purchase).count()
        review_count = db.query(FitReview).count()

        print("\n--- Seed Verification Summary ---")
        print(f"Users:                {user_count}")
        print(f"Body Profiles:        {profile_count}")
        print(f"Brands:               {brand_count}")
        print(f"Garments:             {garment_count}")
        print(f"Garment Sizes:        {size_count}")
        print(f"Garment Measurements: {measurement_count}")
        print(f"Purchases:            {purchase_count}")
        print(f"Fit Reviews:          {review_count}")
        print("---------------------------------")
        print("Deterministic seeding completed successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
