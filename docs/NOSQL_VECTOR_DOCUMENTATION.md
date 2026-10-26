# FitCheck — NoSQL & Vector Database Implementation Documentation

This document fulfills **DBMS Level 3 Evaluation Rubric Items 4 & 9: NoSQL / Vector Database Creation (4 Marks) and NoSQL / Vector Feature RUD (7 Marks)**.

- **Redis Vector Commands:** [`database/queries/vector_commands.redis`](file:///C:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/database/queries/vector_commands.redis)
- **Live Vector RUD Script:** [`vector-search/demo_vector_rud.py`](file:///C:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/vector-search/demo_vector_rud.py)
- **Vector Schema Definition:** [`vector-search/schema.py`](file:///C:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/vector-search/schema.py)
- **Vector Service Implementation:** [`backend/app/services/vector_service.py`](file:///C:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/backend/app/services/vector_service.py)

---

## 1. NoSQL & Vector Database Architecture

FitCheck utilizes **Redis Stack** as an in-memory NoSQL and Vector database alongside relational MySQL:
- **Key Prefix:** `review_vector:{review_id}`
- **Storage Primitive:** Redis Hash (`HSET`)
- **Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2`
- **Embedding Dimensionality:** 384 dimensions (`FLOAT32`)
- **Distance Metric:** `COSINE` distance
- **Indexing Algorithm:** `HNSW` (Hierarchical Navigable Small World graphs with `M=16`, `EF_CONSTRUCTION=200`)
- **Metadata Tag Fields:** `review_id` (Numeric), `garment_size_id` (Numeric), `overall_fit` (Tag), `review_text` (Text)

```
+-----------------------------------------------------------------------------------------+
|                                    REDIS HASH                                           |
| Key: review_vector:25                                                                   |
| Fields:                                                                                 |
|   • review_id:        25                                                                |
|   • garment_size_id:  3                                                                 |
|   • overall_fit:      "TOO_SMALL"                                                       |
|   • review_text:      "Waistband has zero stretch; feels at least one full size small."  |
|   • review_embedding: [384 x 4 bytes = 1,536 bytes binary IEEE 754 float32 blob]       |
+-----------------------------------------------------------------------------------------+
```

---

## 2. Technology Justification (Rubric Item 5)

Why combine relational MySQL with Redis Vector Store?
1. **Relational MySQL (ACID Ground Truth):** Guarantees strict transactional integrity for apparel purchases, customer body measurements, referential cascaded constraints, and multi-table joins across the brand catalog.
2. **Redis Stack Vector Store (Semantic Intelligence):** Relational SQL full-text search is lexical and keyword-dependent; it cannot match semantically equivalent apparel complaints such as `"pinching hips"`, `"constricting waistband"`, and `"runs small"`. Dense vector similarity enables semantic retrieval of crowd fit sentiment without keyword exactness.
3. **Strict Privacy Isolation:** Review vectors and metadata contain **zero** private customer body measurements, personal body profiles, or private purchase history. Vectors store exclusively the public review text, the reviewed garment size, and public overall fit rating.

---

## 3. Vector Database Creation & Indexing (Rubric Item 4 — 4 Marks)

The RediSearch index is created with:
```redis
FT.CREATE fit_review_idx 
    ON HASH PREFIX 1 "review_vector:" 
    SCHEMA 
        review_id NUMERIC SORTABLE 
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

## 4. Vector Feature RUD Operations (Rubric Item 9 — 7 Marks)

All 5 core operations are verified live in [`vector-search/demo_vector_rud.py`](file:///C:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/vector-search/demo_vector_rud.py):

### 4.1 CREATE / UPSERT Operation
Generates a normalized 384-dimensional dense embedding vector from review text and stores the hash into Redis:
```python
upsert_review_vector(
    review_id=99999,
    garment_size_id=1,
    overall_fit="SLIGHTLY_SMALL",
    review_text="The denim is rigid at first and waist feels quite snug."
)
```
- **Redis Command:** `HSET review_vector:99999 review_id 99999 garment_size_id 1 overall_fit "SLIGHTLY_SMALL" review_text "..." review_embedding <384d binary>`

### 4.2 READ: Direct Key Lookup
Fetches the vector hash by `review_id`:
```python
record = get_review_vector(99999)
# Returns: {'review_id': '99999', 'garment_size_id': '1', 'overall_fit': 'SLIGHTLY_SMALL', 'has_embedding': True, 'embedding_dim': 384}
```
- **Redis Command:** `HGETALL review_vector:99999`

### 4.3 READ: Semantic Similarity KNN Search
Embeds a query string and retrieves top-k semantically closest reviews:
```python
hits = search_review_vectors(query_text="snug tight waist rigid denim", k=3)
# Returns: [(99999, 0.7397), (1, 0.671), (27, 0.61)]
```
- **RediSearch Command:**
  ```redis
  FT.SEARCH fit_review_idx "(*)=>[KNN 3 @review_embedding $vec AS vector_score]" PARAMS 2 vec <blob> SORTBY vector_score DIALECT 2
  ```
- **Graceful Fallback Mode:** If the native RediSearch C module is unavailable in the environment, the service transparently switches to `_search_vectors_fallback`, which scans `review_vector:*` hashes directly and computes cosine similarity via NumPy vector dot product. Both modes return identical top-k rankings.

### 4.4 UPDATE Operation
Re-embeds modified text and updates metadata in-place:
```python
upsert_review_vector(
    review_id=99999,
    garment_size_id=1,
    overall_fit="TRUE_TO_SIZE",
    review_text="After breaking in for a week, waist stretches to comfortable true-to-size."
)
```

### 4.5 DELETE Operation
Removes the review hash from Redis:
```python
delete_review_vector(99999)
```
- **Redis Command:** `DEL review_vector:99999`
- Post-deletion verification confirms `get_review_vector(99999) is None`.

---

## 5. Live Demonstration Instructions

To execute the live vector RUD demonstration during evaluation:
```powershell
python vector-search/demo_vector_rud.py
```
**Expected Output:**
```
=================================================================
FITCHECK — REDIS VECTOR STORE RUD DEMONSTRATION
=================================================================
[OK] Redis connection: LIVE on 127.0.0.1:6379

[1/5] CREATE / UPSERT OPERATION:
      Upsert status: True

[2/5] READ OPERATION (Direct Key Lookup):
      Fetched Record: {'garment_size_id': '1', 'overall_fit': 'SLIGHTLY_SMALL', 'review_id': '99999', 'has_embedding': True, 'embedding_dim': 384}

[3/5] READ OPERATION (Semantic KNN Similarity Search):
      Search Query: 'snug tight waist rigid denim'
      Top Results (review_id, similarity): [(99999, 0.7397), (1, 0.671), (27, 0.61)]

[4/5] UPDATE OPERATION (Modify Text & Re-Embed):
      Update status: True
      Updated Record: {'overall_fit': 'TRUE_TO_SIZE', 'has_embedding': True, 'embedding_dim': 384}

[5/5] DELETE OPERATION (Remove Vector from Redis):
      Delete status: True
      Post-delete Verification (Expected None): None

=================================================================
[SUCCESS] ALL 5 VECTOR RUD OPERATIONS VERIFIED SUCCESSFULLY AGAINST REDIS
=================================================================
```
