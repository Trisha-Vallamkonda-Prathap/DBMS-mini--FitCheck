# FitCheck — Database Technology Choice & Justification

## 1. Project Context & Data Problem

In women's apparel e-commerce, sizing across brands lacks standard definitions ("vanity sizing"). A size "M" or "28" in Zara, Levi's, and H&M represents divergent physical dimensions across the waist, hip, thigh, and inseam. Furthermore:
1. **Garment measurements and purchase logs** are strictly structured, tabular, and interrelated. Sizing ladders, numeric tolerances, user body profiles, and purchase outcomes require mathematical precision, relational integrity, and ACID transactional consistency.
2. **User fit reviews and fit complaints** are unstructured and semantic. Customers describe fit using natural language nuances (e.g., *"curves out too much at the hip"*, *"waistband gapes when bending over"*, *"fabric stretches out after an hour"*). Traditional exact-string or SQL `LIKE` queries fail to capture synonymous physical sensations and garment-specific fit issues.

To solve this, FitCheck utilizes a **Polyglot Persistence Architecture**: combining **MySQL 8.0** (Relational SQL) and **Redis Stack** (Vector Search Engine).

---

## 2. SQL Database Selection: MySQL 8.0

### Role in Architecture
MySQL serves as the **source of truth** for all structured entities, transactional state, and relational dependencies.

### Why MySQL for FitCheck?
1. **Strict Referential Integrity and Normalized Relational Modeling (3NF):**
   - Enforces foreign key constraints across 8 normalized tables (`BRAND` -> `GARMENT` -> `GARMENT_SIZE` -> `GARMENT_MEASUREMENT`).
   - Sizing data has cascading dependencies: deleting a garment size must cascade to its physical measurements (`ON DELETE CASCADE`), while brands and garments with purchase history are protected (`ON DELETE RESTRICT`).
2. **Domain-Level Validation and CHECK Constraints:**
   - MySQL 8.0 natively enforces `CHECK` constraints (e.g., positive measurements `measurement_value > 0`, restricted sizing systems `('ALPHA', 'NUMERIC', 'WAIST_BASED')`, and standardized review values).
   - This ensures malformed data is rejected at the database level before business logic executes.
3. **Complex Analytical & Sizing Ladder Queries:**
   - Determining size equivalence requires multi-way relational `JOIN` operations across measurements, `GROUP BY` aggregations, correlated subqueries evaluating historical `KEPT` purchase satisfaction, and Common Table Expressions (CTEs) to rank size proximity.
4. **ACID Transaction Guarantees:**
   - Recording a purchase or updating a body profile alongside fit preferences demands atomic durability, preventing inconsistent sizing records.

---

## 3. Vector Database Selection: Redis Stack (RedisSearch Vector Similarity)

### Role in Architecture
Redis Stack serves as the **semantic retrieval and fit sentiment engine**, storing dense vector embeddings of customer fit reviews and garment feedback.

### Why Redis Stack Vector Search?
1. **Dense Semantic Embedding Retrieval:**
   - Raw user reviews are embedded into high-dimensional vector representations using the `sentence-transformers/all-MiniLM-L6-v2` model (384-dimensional dense vectors).
   - Redis Stack implements Hierarchical Navigable Small World (**HNSW**) and **FLAT** vector indexing algorithms, enabling Approximate Nearest Neighbor (ANN) search with millisecond latency.
2. **Hybrid Search (Vector Similarity + Relational Metadata Filters):**
   - Redis Stack allows combined vector distance queries and metadata tag filtering (e.g., *Find reviews semantically similar to "waist gaps when sitting" exclusively for `brand_id: 2` and `garment_category: "Jeans"`*).
3. **In-Memory Low Latency for Real-Time Recommenders:**
   - As an in-memory data store with native vector extensions, Redis delivers sub-5ms query times, ensuring size recommendations and semantic review summaries load seamlessly alongside page transitions.
4. **Complete RUD Operations:**
   - Supports atomic vector index creation (`FT.CREATE`), real-time insertion (`HSET` / `JSON.SET`), updates upon review editing, and direct deletion upon review removal.

---

## 4. Why Not a Single Paradigm?

| Requirement | Relational Alone (MySQL) | Vector DB Alone (e.g., Pinecone/Chroma) | Polyglot (MySQL + Redis Stack) |
|---|---|---|---|
| **Exact dimensional math & tolerances** | Excellent (DECIMAL precision, constraints) | Poor (unstructured, lacks schema constraints) | **Best-in-class** (MySQL handles math) |
| **Referential integrity (FKs, CASCADE)** | Native, guaranteed | None (no relational links) | **Best-in-class** (MySQL enforces graph) |
| **Semantic nuance & synonym retrieval** | Ineffective (SQL `LIKE` misses context) | Native, highly effective | **Best-in-class** (Redis vector search) |
| **ACID purchase & profile transactions** | Full ACID compliance | Eventual consistency or non-transactional | **Full ACID for state, low-latency vectors** |
| **Hybrid query speed** | Slow on text embeddings | Fast on vectors, incapable of relational joins | **Optimized two-stage pipeline** |

---

## 5. Defense Summary for Viva

When asked: *"Why did you use both MySQL and a vector database instead of storing everything in one system?"*

> **Viva Answer:**
> *"Garment sizing and apparel fit have two fundamentally different data profiles. Physical garment specs (waist, hip, inseam in centimeters) require relational integrity, exact numeric constraints, and multi-table joins to compute dimensional tolerances — MySQL 8.0 guarantees this with ACID durability and strict foreign keys.
> In contrast, user fit complaints (such as 'waist gapes when sitting' or 'stretches out after 20 minutes') are nuanced natural language. SQL `LIKE` queries fail on synonyms and contextual sentiment. Storing vector embeddings in Redis Stack allows us to perform real-time Approximate Nearest Neighbor (HNSW) vector search to pull semantically identical fit experiences, while MySQL anchors user identity, purchases, and verified dimensions."*
