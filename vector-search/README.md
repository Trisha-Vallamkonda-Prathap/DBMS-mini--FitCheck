# FitCheck — Redis Stack Vector Database & Semantic Search Architecture

This document specifies the vector search architecture supporting Rubric Items 4, 8, and 9 (NoSQL/Vector Database Creation, RUD Operations, and Semantic Retrieval).

---

## 1. Vector Search Overview

| Component | Specification |
|---|---|
| **Vector Engine** | Redis Stack (`redis-stack-server`) via RediSearch Module |
| **Index Name** | `fit_review_idx` |
| **Index Storage Structure** | Redis Hashes with prefix `review_vector:` |
| **Embedding Model** | `sentence-transformers/all-MiniLM-L6-v2` |
| **Vector Dimensionality** | 384 dimensions (`FLOAT32`) |
| **Indexing Algorithm** | `HNSW` (Hierarchical Navigable Small World) |
| **Distance Metric** | `COSINE` distance |
| **Hybrid Metadata Filters** | `review_id` (NUMERIC), `garment_size_id` (NUMERIC), `overall_fit` (TAG) |

---

## 2. Why all-MiniLM-L6-v2 & 384 Dimensions?

1. **Lightweight & Fast:** 22M parameters with negligible CPU latency (~15ms per review), ideal for local evaluation without paid API keys (OpenAI/Cohere).
2. **Dense Semantic Capture:** Trained on over 1 billion sentence pairs, capturing contextual apparel phrases like *"too tight around thighs"*, *"excess fabric in waist"*, and *"gapes when seated"*.
3. **Low Memory Footprint:** 384 dimensions $\times$ 4 bytes (FLOAT32) = ~1.5 KB per indexed review, enabling instant in-memory Redis queries.

---

## 3. Redis Vector Index Definition

The index is created using RediSearch DDL:

```text
FT.CREATE fit_review_idx ON HASH PREFIX 1 "review_vector:"
SCHEMA
    review_id NUMERIC SORTABLE
    user_id NUMERIC SORTABLE
    garment_size_id NUMERIC SORTABLE
    overall_fit TAG
    review_text TEXT
    review_embedding VECTOR HNSW 6
        TYPE FLOAT32
        DIM 384
        DISTANCE_METRIC COSINE
        M 16
        EF_CONSTRUCTION 200
```

---

## 4. Full RUD Operations on Vector Store

Rubric Item 9 requires demonstrating **Read, Update, and Delete (RUD)** operations on the Vector store:

1. **Create / Insert (`HSET`):**
   When a user submits a review in MySQL, the backend computes its 384-d embedding and writes to Redis:
   ```python
   redis_client.hset(
       f"review_vector:{review_id}",
       mapping={
           "review_id": review_id,
           "garment_size_id": garment_size_id,
           "overall_fit": overall_fit,
           "review_text": review_text,
           "review_embedding": embedding.tobytes(),
       }
   )
   ```
2. **Read / Retrieve (`FT.SEARCH` with KNN):**
   Semantic query executed with hybrid filtering:
   ```text
   FT.SEARCH fit_review_idx "(@overall_fit:{TOO_SMALL})=>[KNN 5 @review_embedding $vec AS score]" PARAMS 2 vec <query_vector_bytes> SORTBY score DIALECT 2
   ```
3. **Update (`HSET` overwrite):**
   When a customer edits their review text, the backend re-embeds the text and updates the hash fields in place.
4. **Delete (`HDEL` / `DEL`):**
   When a review is removed, `redis_client.delete(f"review_vector:{review_id}")` removes the vector from the index.
