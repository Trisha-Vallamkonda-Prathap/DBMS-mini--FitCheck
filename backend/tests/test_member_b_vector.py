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
    _search_vectors_fallback,
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


def test_vector_fallback_similarity_scoring_and_ranking():
    """
    Regression test for fallback vector cosine similarity scoring semantics:
    - Positive cosine similarity remains positive in [0, 1].
    - Zero similarity evaluates to 0.0.
    - Negative cosine similarity clamps consistently to 0.0 and NEVER becomes positive.
    - Ranking strictly orders results by raw cosine similarity (higher similarity first).
    - Category filtering is honored in fallback mode.
    """
    dim = 4
    # Query vector: unit vector along dimension 0
    query_vector = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)

    # Candidate 1: strongly positive similarity (dot = 0.90)
    v1 = np.array([0.90, 0.43588989, 0.0, 0.0], dtype=np.float32)  # norm = 1.0
    # Candidate 2: moderately positive similarity (dot = 0.40)
    v2 = np.array([0.40, 0.91651513, 0.0, 0.0], dtype=np.float32)  # norm = 1.0
    # Candidate 3: orthogonal / zero similarity (dot = 0.0)
    v3 = np.array([0.0, 1.0, 0.0, 0.0], dtype=np.float32)           # norm = 1.0
    # Candidate 4: mild negative similarity (dot = -0.30)
    v4 = np.array([-0.30, 0.9539392, 0.0, 0.0], dtype=np.float32)  # norm = 1.0
    # Candidate 5: strong negative similarity (dot = -0.80)
    v5 = np.array([-0.80, 0.60, 0.0, 0.0], dtype=np.float32)       # norm = 1.0

    mock_redis = MagicMock()
    # Mock keys present in Redis
    mock_redis.scan_iter.return_value = [
        b"review_vector:1",
        b"review_vector:2",
        b"review_vector:3",
        b"review_vector:4",
        b"review_vector:5",
    ]

    mock_db = {
        b"review_vector:1": {
            b"review_id": b"1",
            b"overall_fit": b"TRUE_TO_SIZE",
            b"review_embedding": v1.tobytes(),
        },
        b"review_vector:2": {
            b"review_id": b"2",
            b"overall_fit": b"TRUE_TO_SIZE",
            b"review_embedding": v2.tobytes(),
        },
        b"review_vector:3": {
            b"review_id": b"3",
            b"overall_fit": b"SLIGHTLY_SMALL",
            b"review_embedding": v3.tobytes(),
        },
        b"review_vector:4": {
            b"review_id": b"4",
            b"overall_fit": b"TOO_SMALL",
            b"review_embedding": v4.tobytes(),
        },
        b"review_vector:5": {
            b"review_id": b"5",
            b"overall_fit": b"TOO_SMALL",
            b"review_embedding": v5.tobytes(),
        },
    }

    mock_redis.hgetall.side_effect = lambda k: mock_db.get(k, {})

    hits = _search_vectors_fallback(
        query_vector=query_vector,
        k=5,
        redis_client=mock_redis,
    )

    assert len(hits) == 5

    # Check ranking order: candidate 1 > 2 > 3 > 4 > 5
    ranked_ids = [h[0] for h in hits]
    assert ranked_ids == [1, 2, 3, 4, 5], f"Ranking failed: expected [1, 2, 3, 4, 5], got {ranked_ids}"

    # Check score semantics
    scores = {h[0]: h[1] for h in hits}
    # Positive scores match cosine similarity
    assert np.isclose(scores[1], 0.90, atol=1e-3)
    assert np.isclose(scores[2], 0.40, atol=1e-3)
    # Zero score is 0.0
    assert scores[3] == 0.0
    # Negative cosine similarity MUST clamp to 0.0 (never become a positive number)
    assert scores[4] == 0.0, f"Negative similarity became non-zero: {scores[4]}"
    assert scores[5] == 0.0, f"Negative similarity became non-zero: {scores[5]}"

    # Verify filter functionality
    filtered_hits = _search_vectors_fallback(
        query_vector=query_vector,
        k=5,
        overall_fit_filter="TRUE_TO_SIZE",
        redis_client=mock_redis,
    )
    assert len(filtered_hits) == 2
    assert [h[0] for h in filtered_hits] == [1, 2]

