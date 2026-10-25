# FitCheck — Database Seeding Strategy & Data Guidelines

## 1. Objective

Populate the 8 relational tables with realistic, domain-appropriate synthetic apparel data that reflects cross-brand sizing variation across brands represented in the FitCheck demo dataset, including Levi's, Zara, H&M, Madewell, and Mango.

The dataset is intended strictly for academic evaluation, database testing, recommendation-engine validation, and semantic-search demonstrations.

---

## 2. Realistic Sizing Ground Truth

To ensure meaningful recommendations during evaluation and viva defense:

- **Jeans & Trousers Focus:** Bottom-wear garments are particularly sensitive to waist, hip, thigh, inseam, and rise differences, making them suitable for demonstrating cross-brand fit variation.
- **Physical Measurements (cm):**
  - **Levi's (Waist-Based):** Size 26 (Waist ~66 cm, Hip ~91 cm), Size 28 (Waist ~71 cm, Hip ~96 cm), Size 30 (Waist ~76 cm, Hip ~101 cm).
  - **Zara (Numeric / EU):** Size 36 / US 4 (Waist ~66 cm, Hip ~94 cm), Size 38 / US 6 (Waist ~70 cm, Hip ~98 cm).
  - **H&M (Alpha / Numeric):** Size S / 4-6 (Waist ~68 cm, Hip ~92 cm), Size M / 8-10 (Waist ~74 cm, Hip ~98 cm).

These values are used as realistic synthetic reference values for the academic prototype and should not be represented as current official brand sizing charts.

---

## 3. Seed Execution Order (Referential Order)

Due to foreign key dependencies, relational data must be inserted in this exact sequence:

1. `USER` (10 synthetic users + 1 admin) — Member A seed
2. `BODY_PROFILE` (8 profiles for users 2–9) — Member A seed
3. `BRAND` (5 brands: Levis, Zara, H&M, Mango, Madewell) — Member A seed
4. `GARMENT` (14 garments across Jeans and Trousers) — Member A seed
5. `GARMENT_SIZE` (70 total sizes, 5 per garment) — Member A seed
6. `GARMENT_MEASUREMENT` (310 dimensional measurements: waist, hip, thigh, inseam, rise) — Member A seed
7. `PURCHASE` (30 structured purchases with varied outcomes and satisfaction) — Member A seed
8. `FIT_REVIEW` — **Member B owned** (40 qualitative synthetic fit reviews used for semantic vector retrieval)

The stable identifiers used across the project are documented in:

`database/seeds/ID_MANIFEST.md`

Do not invent or manually guess `garment_size_id` values when adding reviews or purchases.

---

## 4. Synthetic Data Disclaimer

All personal names, emails, purchase histories, measurement profiles, fit reviews, and apparel records used by the FitCheck academic prototype are **synthetic development/demo data**.

They exist purely for:

- academic evaluation
- database testing
- recommendation-engine validation
- API testing
- Redis vector-search evaluation

No records represent real FitCheck customers.

Brand names are used to demonstrate the cross-brand sizing problem. The project must not describe the synthetic measurement values as proprietary, authoritative, or current official sizing charts from those brands.

---

## 5. Seed Execution & Safe Reset Commands

### To seed an existing clean `fitcheck` database

The project provides an application seed command:

```powershell
python -m backend.app.scripts.seed_db
```

The relational SQL seed data is stored in:

`database/seeds/seed_data.sql`

A direct MySQL import may also be used when appropriate:

```bash
mysql -u fitcheck_user -p fitcheck < database/seeds/seed_data.sql
```

### Safe Reset Procedure — Disposable Environment Only

> [!WARNING]
> Do NOT execute destructive schema recreation against production, shared, or otherwise important databases.
> The schema setup script may drop and recreate project tables.
> Only run it against a verified disposable local FitCheck development database.

Example reset workflow:

```bash
# 1. Execute the authoritative schema setup
mysql -u root -p < fitcheck_setup.sql

# 2. Populate the structured and review seed dataset
mysql -u fitcheck_user -p fitcheck < database/seeds/seed_data.sql
```

After loading the relational data, apply the project’s advanced SQL objects where required:

```sql
SOURCE database/queries/advanced_concepts.sql;
```

This creates/verifies advanced database objects including the project view, stored function, stored procedure, and FIT_REVIEW audit triggers.

---

## 6. Member B Synthetic Review Data

### Dataset

Member B owns the `FIT_REVIEW` review-intelligence component.

- **Volume:** 40 synthetic `FIT_REVIEW` records
- **Storage:** MySQL remains the relational source of truth
- **Purpose:** Evaluate semantic retrieval for natural-language apparel fit experiences
- **Examples of represented fit issues:**
  - tight waist
  - waistband gaps
  - tight thighs
  - loose hips
  - short length
  - long/dragging hem
  - comfortable fit
  - true-to-size experiences
  - fit-preference differences

The reviews use valid `user_id` and `garment_size_id` foreign keys from the deterministic project dataset and ID manifest.

### Review Fields

Each `FIT_REVIEW` uses the canonical fields:

- `review_id`
- `user_id`
- `garment_size_id`
- `overall_fit`
- `waist_fit`
- `hip_fit`
- `thigh_fit`
- `length_fit`
- `review_text`
- `created_at`

Allowed values:

**overall_fit**

- `TOO_SMALL`
- `SLIGHTLY_SMALL`
- `TRUE_TO_SIZE`
- `SLIGHTLY_LARGE`
- `TOO_LARGE`

**waist_fit / hip_fit / thigh_fit**

- `TIGHT`
- `GOOD`
- `LOOSE`

**length_fit**

- `SHORT`
- `GOOD`
- `LONG`

All review text must be non-empty.

---

## 7. Redis Stack Vector Ingestion

Redis Stack supplements MySQL with semantic retrieval. It does not replace the relational database.

### Embedding Configuration

- **Model:** `sentence-transformers/all-MiniLM-L6-v2`
- **Embedding dimension:** `384`
- **Redis index:** `fit_review_idx`
- **Similarity:** cosine-based vector search

### Start Redis Stack

Example Docker command:

```powershell
docker run -d --name fitcheck-redis -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
```

If the container already exists, do not create another one. Start the existing container if necessary:

```powershell
docker start fitcheck-redis
```

Verify connectivity:

```powershell
docker exec fitcheck-redis redis-cli ping
```

Expected:

```text
PONG
```

### Populate the Vector Index

After the MySQL review records have been loaded:

```powershell
python -m backend.app.scripts.seed_vectors
```

Verified project result:

```text
Found 40 FIT_REVIEW records in MySQL.
Ingestion complete: 40/40 review vectors indexed in Redis.
```

The ingestion process:

1. Reads authoritative `FIT_REVIEW` rows from MySQL.
2. Generates 384-dimensional MiniLM embeddings.
3. Stores review vector records in Redis Stack.
4. Uses deterministic keys such as `review_vector:<review_id>`.

---

## 8. Redis / MySQL Responsibility Boundary

FitCheck intentionally uses both relational and vector databases.

### MySQL

MySQL remains the source of truth for:

- users
- body profiles
- brands
- garments
- garment sizes
- measurements
- purchases
- fit reviews
- audit records

### Redis Stack

Redis Stack is used for:

- review embeddings
- KNN semantic retrieval
- ranking natural-language fit experiences

For semantic search, Redis returns matching review IDs and similarity information. The application then joins those IDs back to authoritative MySQL records through:

`FIT_REVIEW -> GARMENT_SIZE -> GARMENT -> BRAND`

This preserves relational integrity while still supporting semantic retrieval.

---

## 9. Review Vector Synchronization

The application keeps Redis vectors synchronized with MySQL review operations.

### Create

Creating a review:

1. persists the review in MySQL
2. generates its embedding
3. stores the vector in Redis

### Update

Updating review text:

1. updates the MySQL record
2. regenerates its embedding
3. refreshes the Redis vector

### Delete

Deleting a review:

1. deletes the MySQL review
2. removes the Redis vector
3. activates the MySQL review-audit trigger

This create/update/delete vector lifecycle is covered by automated tests.

---

## 10. Review Audit Data

Advanced SQL auditing is implemented for `FIT_REVIEW`.

Audit table:

`REVIEW_AUDIT`

The repository defines three review lifecycle triggers:

- `trg_after_review_insert`
- `trg_after_review_update`
- `trg_after_review_delete`

These record review changes for administrative inspection.

The advanced SQL objects can be reproduced from:

`database/queries/advanced_concepts.sql`

The script has been verified successfully on MySQL 8.0.

---

## 11. Database-Level RBAC

FitCheck includes separate database-level runtime and administration roles.

The RBAC setup is stored in:

`database/queries/rbac_setup.sql`

The runtime application role receives only the data permissions required by the application:

- `SELECT`
- `INSERT`
- `UPDATE`
- `DELETE`

Schema-changing privileges are reserved for the administrative database role.

Passwords in tracked setup files must remain explicit placeholders. Real local credentials belong in environment configuration and must not be committed.

---

## 12. Validation

The final integrated project has been verified using:

```powershell
python -m pytest backend/tests -v
```

Verified result:

```text
47 passed
```

The test suite covers both Member A and Member B functionality, including:

- authentication
- authorization
- review CRUD
- ownership restrictions
- audit lifecycle
- relational joins
- semantic search
- embedding configuration
- Redis vector create/update/delete behavior
- profile and purchase functionality
- recommendation logic
- unit conversion

Redis vector ingestion was also verified separately with all 40 review vectors successfully indexed.

---

## 13. Important Data Rules

When extending or resetting FitCheck data:

- Treat all included records as synthetic demo data.
- Preserve foreign-key integrity.
- Use IDs from `ID_MANIFEST.md`.
- Do not guess `garment_size_id` values.
- Keep exact schema enum values.
- Keep `size_label` as a string.
- Preserve the relationship:

  `BRAND -> GARMENT -> GARMENT_SIZE -> GARMENT_MEASUREMENT`

- Reviews reference `GARMENT_SIZE`, not a duplicated `brand_id`.
- MySQL remains the source of truth.
- Redis is supplementary semantic-search infrastructure.
- Do not commit passwords, tokens, `.env`, or other local secrets.