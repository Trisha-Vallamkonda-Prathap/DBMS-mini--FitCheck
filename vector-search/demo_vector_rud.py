"""
FitCheck — NoSQL / Vector Database RUD Demonstration Script
Demonstrates Rubric Item 9: "NoSQL/Vector feature, RUD (7 Marks)"

Executes live against Redis:
1. CREATE / UPSERT: Ingest a new review embedding.
2. READ (Direct): Lookup vector metadata by review_id.
3. READ (Search): Execute KNN semantic similarity search against indexed reviews.
4. UPDATE: Modify review text and re-embed in Redis.
5. DELETE: Remove the review vector from Redis.
"""

import sys
import os
from pathlib import Path
import logging

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("vector_demo")

from backend.app.core.redis import ping_redis, get_redis_client
from backend.app.services.vector_service import (
    upsert_review_vector,
    get_review_vector,
    search_review_vectors,
    delete_review_vector,
)


def run_rud_demo():
    print("=" * 65)
    print("FITCHECK — REDIS VECTOR STORE RUD DEMONSTRATION")
    print("=" * 65)

    if not ping_redis():
        print("ERROR: Redis is not reachable on port 6379.")
        sys.exit(1)

    print("[OK] Redis connection: LIVE on 127.0.0.1:6379\n")

    demo_review_id = 99999
    demo_size_id = 1
    demo_initial_text = "RUD Demonstration: The denim is rigid at first and waist feels quite snug."
    demo_fit = "SLIGHTLY_SMALL"

    # 1. CREATE / UPSERT
    print("[1/5] CREATE / UPSERT OPERATION:")
    success = upsert_review_vector(
        review_id=demo_review_id,
        garment_size_id=demo_size_id,
        overall_fit=demo_fit,
        review_text=demo_initial_text,
    )
    print(f"      Upsert status: {success}")
    assert success, "Upsert failed!"

    # 2. READ (Direct Lookup)
    print("\n[2/5] READ OPERATION (Direct Key Lookup):")
    record = get_review_vector(demo_review_id)
    print(f"      Fetched Record: {record}")
    assert record is not None, "Direct lookup returned None!"
    assert record.get("has_embedding") is True, "Embedding missing!"

    # 3. READ (Semantic Vector Similarity Search)
    print("\n[3/5] READ OPERATION (Semantic KNN Similarity Search):")
    query = "snug tight waist rigid denim"
    hits = search_review_vectors(query_text=query, k=3)
    print(f"      Search Query: '{query}'")
    print(f"      Top Results (review_id, similarity): {hits}")
    assert len(hits) > 0, "Semantic search returned zero results!"

    # 4. UPDATE
    print("\n[4/5] UPDATE OPERATION (Modify Text & Re-Embed):")
    updated_text = "RUD Demonstration: After breaking in for a week, waist stretches to comfortable true-to-size."
    updated_fit = "TRUE_TO_SIZE"
    up_success = upsert_review_vector(
        review_id=demo_review_id,
        garment_size_id=demo_size_id,
        overall_fit=updated_fit,
        review_text=updated_text,
    )
    print(f"      Update status: {up_success}")
    updated_record = get_review_vector(demo_review_id)
    print(f"      Updated Record: {updated_record}")
    assert updated_record.get("overall_fit") == "TRUE_TO_SIZE"

    # 5. DELETE
    print("\n[5/5] DELETE OPERATION (Remove Vector from Redis):")
    del_success = delete_review_vector(demo_review_id)
    print(f"      Delete status: {del_success}")
    assert del_success is True, "Delete operation failed!"
    post_delete = get_review_vector(demo_review_id)
    print(f"      Post-delete Verification (Expected None): {post_delete}")
    assert post_delete is None, "Record still exists after deletion!"

    print("\n" + "=" * 65)
    print("[SUCCESS] ALL 5 VECTOR RUD OPERATIONS VERIFIED SUCCESSFULLY AGAINST REDIS")
    print("=" * 65)


if __name__ == "__main__":
    run_rud_demo()
