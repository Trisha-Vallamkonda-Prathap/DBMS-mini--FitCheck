"""
FitCheck — Redis Stack Vector Index Schema & Query Helper
Defines the HNSW vector index for Fit Review semantic search.
"""

from typing import List, Dict, Any, Optional
import numpy as np

INDEX_NAME = "fit_review_idx"
DOC_PREFIX = "review_vector:"
VECTOR_DIM = 384
DISTANCE_METRIC = "COSINE"


def create_vector_index(redis_client) -> bool:
    """
    Creates the Redis Stack HNSW vector search index if it does not already exist.
    """
    try:
        from redis.commands.search.field import (
            TextField,
            NumericField,
            TagField,
            VectorField,
        )
        from redis.commands.search.indexDefinition import IndexDefinition, IndexType

        # Check if index already exists
        try:
            redis_client.ft(INDEX_NAME).info()
            return True  # Already exists
        except Exception:
            pass  # Index does not exist, proceed to create

        schema = (
            NumericField("review_id", sortable=True),
            NumericField("user_id", sortable=True),
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
        return True
    except Exception as e:
        print(f"Error creating Redis vector index: {e}")
        return False


def build_knn_query(k: int = 5, overall_fit_filter: Optional[str] = None) -> str:
    """
    Builds a RediSearch query string combining vector similarity and optional metadata filters.
    """
    filter_expr = f"(@overall_fit:{{{overall_fit_filter}}})" if overall_fit_filter else "*"
    return f"({filter_expr})=>[KNN {k} @review_embedding $vec AS vector_score]"
