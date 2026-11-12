import os
import sys
from pathlib import Path
from sqlalchemy import text
from backend.app.core.database import engine, SessionLocal, Base
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

    print("Ensuring relational schema tables exist via SQLAlchemy models...")
    Base.metadata.create_all(bind=engine)

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
        try:
            with engine.begin() as conn:
                for idx, stmt in enumerate(statements, 1):
                    conn.execute(text(stmt))
        except Exception as e:
            print(f"Error executing statement in {current_file.name}: {e}")
            raise RuntimeError(f"Database seeding failed during {current_file.name}: {e}") from e

    # Verify counts against authoritative minimum baseline
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
        print(f"Users:                {user_count} (min: 10)")
        print(f"Body Profiles:        {profile_count} (min: 8)")
        print(f"Brands:               {brand_count} (min: 5)")
        print(f"Garments:             {garment_count} (min: 14)")
        print(f"Garment Sizes:        {size_count} (min: 70)")
        print(f"Garment Measurements: {measurement_count} (min: 310)")
        print(f"Purchases:            {purchase_count} (min: 30)")
        print(f"Fit Reviews:          {review_count} (min: 40)")
        print("---------------------------------")

        baseline_checks = [
            ("Users", user_count, 10),
            ("Body Profiles", profile_count, 8),
            ("Brands", brand_count, 5),
            ("Garments", garment_count, 14),
            ("Garment Sizes", size_count, 70),
            ("Garment Measurements", measurement_count, 310),
            ("Purchases", purchase_count, 30),
            ("Fit Reviews", review_count, 40),
        ]
        for name, actual, minimum in baseline_checks:
            if actual < minimum:
                raise ValueError(
                    f"Seed verification failed for {name}: found {actual}, expected at least {minimum}."
                )

        print("Deterministic seeding completed successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
