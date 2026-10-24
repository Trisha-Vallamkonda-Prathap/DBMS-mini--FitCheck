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
)


def seed_database():
    """Executes the deterministic seed SQL script against the configured database."""
    seed_sql_path = Path(__file__).resolve().parents[3] / "database" / "seeds" / "seed_data.sql"
    if not seed_sql_path.exists():
        print(f"Error: Seed file not found at {seed_sql_path}")
        sys.exit(1)

    print(f"Loading seed data from {seed_sql_path}...")
    with open(seed_sql_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Split statements by semicolon, skipping comments and USE statements
    statements = []
    for stmt in sql_content.split(";"):
        cleaned = stmt.strip()
        if not cleaned:
            continue
        # Skip USE fitcheck if executed via connection with DB already selected
        if cleaned.upper().startswith("USE "):
            continue
        statements.append(cleaned)

    print(f"Executing {len(statements)} SQL seed statements...")
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

        print("\n--- Seed Verification Summary ---")
        print(f"Users:               {user_count}")
        print(f"Body Profiles:       {profile_count}")
        print(f"Brands:              {brand_count}")
        print(f"Garments:            {garment_count}")
        print(f"Garment Sizes:       {size_count}")
        print(f"Garment Measurements:{measurement_count}")
        print(f"Purchases:           {purchase_count}")
        print("---------------------------------")
        print("Deterministic seeding completed successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
