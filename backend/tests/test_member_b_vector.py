"""
Unit and Integration Tests for Member B Redis Stack Vector Search & Embeddings
Covers:
- Embedding model dimension (384) and normalization
- Semantic ranking quality: relevant fit complaints rank above unrelated complaints
- Deterministic Redis vector key generation
- Full Vector RUD lifecycle (Create, Read, Update, Delete)
- Idempotent ingestion
- Clean degradation and error handling when Redis is unreachable
"""

import pytest
import numpy as np
from unittest.mock import MagicMock

from backend.app.services.vector_service import (
    compute_embedding,
    get_vector_key,
    upsert_review_vector,
    delete_review_vector,
    search_review_vectors,
    ensure_vector_index,
    VECTOR_DIM,
    INDEX_NAME,
    DOC_PREFIX,
)


def test_embedding_dimension_and_normalization():
    """Verifies that all-MiniLM-L6-v2 yields a 384-dimensional unit-normalized float32 vector."""
    text = "the waistband digs into me when sitting down"
    vec = compute_embedding(text)

    assert isinstance(vec, np.ndarray)
    assert vec.shape == (384,)
    assert vec.dtype == np.float32
    assert VECTOR_DIM == 384

    # Verify L2 normalization (norm approximately 1.0)
    norm = np.linalg.norm(vec)
    assert np.isclose(norm, 1.0, atol=1e-3)


def test_semantic_ranking_quality_differentiates_complaints():
    """
    Demonstrates rubric requirement:
    A natural-language query ('loose waist but tight upper legs') must have higher
    semantic cosine similarity to a paraphrased equivalent ('large gap at waist but thighs restrictive')
    than to an unrelated fit issue ('waist fits perfectly but trousers are much too long').
    """
    query = "loose waist but tight upper legs"
    relevant_review = "there is a large gap at my waist but my thighs feel restrictive"
    unrelated_review = "the waist fits perfectly but the trousers are much too long"

    q_vec = compute_embedding(query)
    rel_vec = compute_embedding(relevant_review)
    unrel_vec = compute_embedding(unrelated_review)

    sim_relevant = float(np.dot(q_vec, rel_vec))
    sim_unrelated = float(np.dot(q_vec, unrel_vec))

    # Relevant review must score significantly higher
    assert sim_relevant > sim_unrelated, (
        f"Semantic ranking failed: relevant ({sim_relevant:.4f}) should rank higher than unrelated ({sim_unrelated:.4f})"
    )
    assert (sim_relevant - sim_unrelated) > 0.10


def test_deterministic_vector_key_format():
    """Ensures deterministic vector key naming convention matches 'review_vector:{review_id}'."""
    assert get_vector_key(1) == "review_vector:1"
    assert get_vector_key(42) == "review_vector:42"
    assert get_vector_key(999) == "review_vector:999"


def test_vector_rud_lifecycle_mocked_redis():
    """
    Simulates the complete Vector RUD lifecycle in Redis:
    - CREATE: upsert_review_vector writes hash with 384-d float bytes
    - READ: search_review_vectors queries KNN and converts cosine distance to similarity
    - UPDATE: upsert_review_vector overwrites existing hash
    - DELETE: delete_review_vector removes hash
    """
    mock_redis = MagicMock()
    mock_ft = MagicMock()
    mock_redis.ft.return_value = mock_ft

    # 1. CREATE
    created = upsert_review_vector(
        review_id=101,
        garment_size_id=3,
        overall_fit="SLIGHTLY_SMALL",
        review_text="the waistband digs into me",
        redis_client=mock_redis,
    )
    assert created is True
    mock_redis.hset.assert_called_once()
    call_args = mock_redis.hset.call_args
    assert call_args[0][0] == "review_vector:101"
    mapping = call_args[1]["mapping"]
    assert mapping["review_id"] == 101
    assert mapping["garment_size_id"] == 3
    assert mapping["overall_fit"] == "SLIGHTLY_SMALL"
    assert len(mapping["review_embedding"]) == 384 * 4  # 384 float32 bytes = 1536 bytes

    # 2. READ (SEARCH)
    mock_doc = MagicMock()
    mock_doc.review_id = "101"
    mock_doc.vector_score = "0.15"  # Cosine distance = 0.15 => similarity = 0.85
    mock_search_res = MagicMock()
    mock_search_res.docs = [mock_doc]
    mock_ft.search.return_value = mock_search_res

    results = search_review_vectors(
        query_text="snug around the waist",
        k=5,
        redis_client=mock_redis,
    )
    assert len(results) == 1
    review_id, score = results[0]
    assert review_id == 101
    assert score == 0.85

    # 3. UPDATE (Idempotent overwrite)
    mock_redis.hset.reset_mock()
    updated = upsert_review_vector(
        review_id=101,
        garment_size_id=3,
        overall_fit="TOO_SMALL",
        review_text="Updated review text: painfully tight waistband",
        redis_client=mock_redis,
    )
    assert updated is True
    assert mock_redis.hset.call_args[0][0] == "review_vector:101"

    # 4. DELETE
    mock_redis.delete.return_value = 1
    deleted = delete_review_vector(review_id=101, redis_client=mock_redis)
    assert deleted is True
    mock_redis.delete.assert_called_with("review_vector:101")


def test_redis_failure_handled_cleanly():
    """Ensures graceful degradation when Redis is offline or throws exceptions."""
    broken_redis = MagicMock()
    broken_redis.hset.side_effect = ConnectionError("Redis connection refused")
    broken_redis.delete.side_effect = ConnectionError("Redis connection refused")
    broken_redis.ft.side_effect = ConnectionError("Redis connection refused")

    # Functions must log warnings and return safe defaults instead of crashing
    assert upsert_review_vector(1, 2, "GOOD", "Test", redis_client=broken_redis) is False
    assert delete_review_vector(1, redis_client=broken_redis) is False
    assert search_review_vectors("query", redis_client=broken_redis) == []
