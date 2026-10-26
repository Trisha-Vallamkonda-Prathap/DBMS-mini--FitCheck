"""
FitCheck — Vector Database & Semantic Fit Intelligence Service
Manages 384-dimensional dense review embeddings (sentence-transformers/all-MiniLM-L6-v2)
and HNSW vector index operations (Create, Read, Update, Delete) in Redis Stack.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from backend.app.core.config import settings
from backend.app.core.redis import get_redis_client, ping_redis

logger = logging.getLogger(__name__)

INDEX_NAME = settings.REDIS_INDEX_NAME or "fit_review_idx"
DOC_PREFIX = "review_vector:"
VECTOR_DIM = settings.EMBEDDING_DIMENSION or 384
DISTANCE_METRIC = "COSINE"

# Lazy-loaded singleton for SentenceTransformer
_embedding_model = None


def get_embedding_model():
    """Returns the cached SentenceTransformer model instance (lazy loaded)."""
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME} ({VECTOR_DIM} dimensions)...")
        _embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
    return _embedding_model


def compute_embedding(text: str) -> np.ndarray:
    """Computes a 384-dimensional normalized float32 embedding vector for the given text."""
    model = get_embedding_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return np.array(embedding, dtype=np.float32)


def ensure_vector_index(redis_client=None) -> bool:
    """
    Ensures that the HNSW vector search index exists in Redis Stack.
    Creates it if not already present.
    """
    if redis_client is None:
        if not ping_redis():
            return False
        redis_client = get_redis_client()

    try:
        from redis.commands.search.field import (
            TextField,
            NumericField,
            TagField,
            VectorField,
        )
        try:
            from redis.commands.search.index_definition import IndexDefinition, IndexType
        except ImportError:
            from redis.commands.search.indexDefinition import IndexDefinition, IndexType

        try:
            redis_client.ft(INDEX_NAME).info()
            return True  # Index already exists
        except Exception:
            pass  # Index does not exist, proceed to create

        schema = (
            NumericField("review_id", sortable=True),
            NumericField("garment_size_id", sortable=True),
            TagField("overall_fit"),
            TextField("review_text"),
            VectorField(
                "review_embedding",
                "HNSW",
                {
                    "TYPE": "FLOAT32",
                    "DIM": VECTOR_DIM,
                    "DISTANCE_METRIC": DISTANCE_METRIC,
                    "INITIAL_CAP": 1000,
                    "M": 16,
                    "EF_CONSTRUCTION": 200,
                },
            ),
        )
        definition = IndexDefinition(prefix=[DOC_PREFIX], index_type=IndexType.HASH)
        redis_client.ft(INDEX_NAME).create_index(schema, definition=definition)
        logger.info(f"Created Redis Stack vector index: {INDEX_NAME}")
        return True
    except Exception as e:
        logger.warning(f"Could not create Redis vector index '{INDEX_NAME}': {e}")
        return False


def get_vector_key(review_id: int) -> str:
    """Returns the deterministic Redis key for a review vector."""
    return f"{DOC_PREFIX}{review_id}"


def upsert_review_vector(
    review_id: int,
    garment_size_id: int,
    overall_fit: str,
    review_text: str,
    redis_client=None,
    embedding: Optional[np.ndarray] = None,
) -> bool:
    """
    CREATE / UPDATE operation:
    Generates embedding for review_text (or uses provided) and upserts
    the review hash into Redis Stack under deterministic key 'review_vector:{review_id}'.
    Idempotent. Fails gracefully if Redis is unavailable.
    """
    try:
        if redis_client is None:
            if not ping_redis():
                logger.warning("Redis is not reachable; skipping vector upsert.")
                return False
            redis_client = get_redis_client()

        ensure_vector_index(redis_client)

        if embedding is None:
            embedding = compute_embedding(review_text)

        key = get_vector_key(review_id)
        redis_client.hset(
            key,
            mapping={
                "review_id": review_id,
                "garment_size_id": garment_size_id,
                "overall_fit": overall_fit,
                "review_text": review_text,
                "review_embedding": embedding.tobytes(),
            },
        )
        logger.info(f"Upserted vector for review_id={review_id} in Redis under key '{key}'.")
        return True
    except Exception as e:
        logger.warning(f"Failed to upsert vector for review_id={review_id}: {e}")
        return False


def delete_review_vector(review_id: int, redis_client=None) -> bool:
    """
    DELETE operation:
    Removes the vector record for the given review_id from Redis Stack.
    Fails gracefully if Redis is unavailable.
    """
    try:
        if redis_client is None:
            if not ping_redis():
                logger.warning("Redis is not reachable; skipping vector delete.")
                return False
            redis_client = get_redis_client()

        key = get_vector_key(review_id)
        deleted_count = redis_client.delete(key)
        logger.info(f"Deleted vector key '{key}' from Redis (keys removed: {deleted_count}).")
        return deleted_count > 0
    except Exception as e:
        logger.warning(f"Failed to delete vector for review_id={review_id}: {e}")
        return False


def search_review_vectors(
    query_text: str,
    k: int = 5,
    overall_fit_filter: Optional[str] = None,
    redis_client=None,
) -> List[Tuple[int, float]]:
    """
    READ / SEMANTIC SEARCH operation:
    Embeds query_text, performs KNN vector search in Redis Stack,
    and returns a list of (review_id, similarity_score) sorted by highest similarity first.

    Redis COSINE distance metric:
      distance = 1 - cosine_similarity (for normalized vectors in range [0, 2])
      similarity = 1.0 - distance
    """
    try:
        if redis_client is None:
            if not ping_redis():
                logger.warning("Redis is not reachable; returning empty search results.")
                return []
            redis_client = get_redis_client()

        ensure_vector_index(redis_client)

        from redis.commands.search.query import Query

        query_vector = compute_embedding(query_text)
        filter_expr = f"@overall_fit:{{{overall_fit_filter}}}" if overall_fit_filter else "*"
        query_str = f"({filter_expr})=>[KNN {k} @review_embedding $vec AS vector_score]"

        q = (
            Query(query_str)
            .sort_by("vector_score")
            .return_fields("review_id", "vector_score")
            .paging(0, k)
            .dialect(2)
        )

        results = redis_client.ft(INDEX_NAME).search(q, query_params={"vec": query_vector.tobytes()})

        hits: List[Tuple[int, float]] = []
        for doc in results.docs:
            try:
                r_id = int(getattr(doc, "review_id"))
                distance = float(getattr(doc, "vector_score"))
                # Convert cosine distance to similarity score in [0, 1]
                similarity = max(0.0, min(1.0, 1.0 - distance))
                hits.append((r_id, round(similarity, 4)))
            except (ValueError, AttributeError) as parse_err:
                logger.warning(f"Error parsing search result document: {parse_err}")

        return hits
    except Exception as e:
        logger.warning(f"Error executing Redis vector search: {e}")
        return []
