"""
FitCheck — Redis Stack Vector Ingestion Runner
Iterates over all FIT_REVIEW records in MySQL, generates 384-dimensional dense
embeddings using sentence-transformers/all-MiniLM-L6-v2, and indexes them in Redis Stack.
Idempotent: Re-running this script updates existing vector hashes in place.
"""

import sys
import logging
from backend.app.core.database import SessionLocal
from backend.app.models import FitReview
from backend.app.services.vector_service import upsert_review_vector, ensure_vector_index

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("seed_vectors")


def seed_review_vectors():
    db = SessionLocal()
    try:
        reviews = db.query(FitReview).all()
        if not reviews:
            logger.info("No FIT_REVIEW records found in MySQL. Please run seed_db first.")
            return

        logger.info(f"Found {len(reviews)} FIT_REVIEW records in MySQL. Ingesting into Redis Stack...")
        success_count = 0
        for rev in reviews:
            ok = upsert_review_vector(
                review_id=rev.review_id,
                garment_size_id=rev.garment_size_id,
                overall_fit=rev.overall_fit,
                review_text=rev.review_text,
            )
            if ok:
                success_count += 1

        logger.info(f"Ingestion complete: {success_count}/{len(reviews)} review vectors indexed in Redis.")
    except Exception as e:
        logger.error(f"Error during vector seeding: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_review_vectors()
