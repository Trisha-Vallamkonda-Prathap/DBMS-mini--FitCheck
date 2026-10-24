# FitCheck — Database Seeding Strategy & Data Guidelines

## 1. Objective
Populate the 8 relational tables with realistic, non-fabricated, domain-accurate apparel data reflecting real-world sizing variances across major brands (e.g., Levi's, Zara, H&M, Madewell, Mango).

## 2. Realistic Sizing Ground Truth
To ensure meaningful recommendations during evaluation and viva defense:
- **Jeans & Trousers Focus:** Bottom-wear garments have the highest return rates in e-commerce due to waist, hip, and thigh mismatches.
- **Physical Measurements (cm):**
  - **Levi's (Waist-Based):** Size 26 (Waist ~66cm, Hip ~91cm), Size 28 (Waist ~71cm, Hip ~96cm), Size 30 (Waist ~76cm, Hip ~101cm).
  - **Zara (Numeric / EU):** Size 36 / US 4 (Waist ~66cm, Hip ~94cm), Size 38 / US 6 (Waist ~70cm, Hip ~98cm).
  - **H&M (Alpha / Numeric):** Size S / 4-6 (Waist ~68cm, Hip ~92cm), Size M / 8-10 (Waist ~74cm, Hip ~98cm).

## 3. Seed Execution Order (Referential Order)
Due to foreign key dependencies, data must be inserted in this exact sequence:
1. `USER` (10 synthetic users + 1 admin) — Member A seed
2. `BODY_PROFILE` (8 profiles for users 2–9) — Member A seed
3. `BRAND` (5 brands: Levis, Zara, H&M, Mango, Madewell) — Member A seed
4. `GARMENT` (14 garments across Jeans and Trousers) — Member A seed
5. `GARMENT_SIZE` (70 total sizes, 5 per garment) — Member A seed
6. `GARMENT_MEASUREMENT` (310 dimensional measurements: waist, hip, thigh, inseam, rise) — Member A seed
7. `PURCHASE` (30 structured purchases with varied outcomes and satisfaction) — Member A seed
8. `FIT_REVIEW` — **Member B owned** (qualitative fit reviews and vector embeddings)

## 4. Synthetic Data Disclaimer
All personal names, emails (`@example.com`), purchase logs, and measurement profiles in `seed_data.sql` are **100% synthetic** and generated purely for academic evaluation and software testing. No real customer or proprietary brand measurement charts were copied or exposed.

## 5. Seed Execution & Safe Reset Commands

### To seed an existing, clean `fitcheck` database:
```bash
mysql -u fitcheck_user -p fitcheck < database/seeds/seed_data.sql
```

### Safe Reset Procedure (Disposable Environment Only):
> [!WARNING]
> Do NOT execute destructive schema recreation against production or shared environments!
> Only run against a verified disposable local development database.

```bash
# 1. Execute schema creation (drops and recreates tables)
mysql -u root -p < database/fitcheck_setup.sql

# 2. Populate Member A structured dataset
mysql -u fitcheck_user -p fitcheck < database/seeds/seed_data.sql
```


---

## 6. Member B Synthetic Review Data & Vector Ingestion

- **File:** `database/seeds/review_seeds.sql`
- **Volume:** 40 synthetic `FIT_REVIEW` rows
- **Disclaimer:** **DATA IS SYNTHETIC**. Generated for evaluating semantic vector retrieval on apparel fit issues (waist gap, tight thighs, hem dragging).
- **Referential Integrity:** Strictly uses foreign keys from `ID_MANIFEST.md` (`user_id` 1..10, `garment_size_id` 1..70).
- **Import Command:**
  ```bash
  mysql -u fitcheck_user -p fitcheck < database/seeds/review_seeds.sql
  ```
- **Vector Ingestion into Redis Stack:**
  After loading MySQL reviews, populate the Redis Stack vector index:
  ```bash
  python -m backend.app.scripts.seed_vectors
  ```
