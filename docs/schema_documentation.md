# FitCheck — Relational Schema Documentation & Data Dictionary

This document details the normalized relational database schema implemented in `database/fitcheck_setup.sql` and visualised in `docs/diagrams/dbms_mini_v4.drawio`.

---

## 1. Schema Overview & Entity Summary

The database is built on **MySQL 8.0+** using the `InnoDB` storage engine for ACID compliance, row-level locking, and foreign key enforcement.

```
       +------------------+           +------------------+
       |       USER       | <-------- |   BODY_PROFILE   |
       +------------------+ (1:0..1)  +------------------+
         |              |
  (1:N)  |              | (1:N)
         v              v
   +----------+   +------------+
   | PURCHASE |   | FIT_REVIEW |
   +----------+   +------------+
         ^              ^
   (1:N) |              | (1:N)
         +-------+------+
                 |
        +------------------+
        |   GARMENT_SIZE   |
        +------------------+
          ^              |
    (1:N) |              | (1:N)
  +---------+      +---------------------+
  | GARMENT |      | GARMENT_MEASUREMENT |
  +---------+      +---------------------+
      ^
(1:N) |
  +-------+
  | BRAND |
  +-------+
```

---

## 2. Table-by-Table Data Dictionary

### Table 1: `USER`
Stores registered account credentials and authorization roles.

| Column | Type | Nullable | Default | Constraints / Descriptions |
|---|---|---|---|---|
| `user_id` | `INT` | NO | `AUTO_INCREMENT` | **PK** (`pk_user`). Surrogate unique identifier. |
| `name` | `VARCHAR(100)` | NO | — | User's full display name. |
| `email` | `VARCHAR(255)` | NO | — | **UNIQUE** (`uq_user_email`). Login identity. |
| `password_hash` | `VARCHAR(255)` | NO | — | Secure bcrypt-hashed password string. |
| `role` | `VARCHAR(10)` | NO | `'USER'` | **CHECK** (`chk_user_role`): `role IN ('USER', 'ADMIN')`. |
| `created_at` | `TIMESTAMP` | NO | `CURRENT_TIMESTAMP` | System creation timestamp. |

---

### Table 2: `BODY_PROFILE`
Stores user-supplied self-measurements and fit preferences. Enforces a strict 1-to-0..1 relationship with `USER`.

| Column | Type | Nullable | Default | Constraints / Descriptions |
|---|---|---|---|---|
| `profile_id` | `INT` | NO | `AUTO_INCREMENT` | **PK** (`pk_body_profile`). |
| `user_id` | `INT` | NO | — | **FK** (`fk_profile_user`) -> `USER(user_id)` **ON DELETE CASCADE ON UPDATE CASCADE**. **UNIQUE** (`uq_body_profile_user`). |
| `height` | `DECIMAL(5,2)` | YES | `NULL` | Height in cm. **CHECK**: `height IS NULL OR height > 0`. |
| `waist` | `DECIMAL(5,2)` | YES | `NULL` | Natural waist in cm. **CHECK**: `waist IS NULL OR waist > 0`. |
| `hip` | `DECIMAL(5,2)` | YES | `NULL` | Fullest hip in cm. **CHECK**: `hip IS NULL OR hip > 0`. |
| `thigh` | `DECIMAL(5,2)` | YES | `NULL` | Thigh circumference in cm. **CHECK**: `thigh IS NULL OR thigh > 0`. |
| `inseam` | `DECIMAL(5,2)` | YES | `NULL` | Leg inseam length in cm. **CHECK**: `inseam IS NULL OR inseam > 0`. |
| `preferred_fit`| `VARCHAR(20)` | YES | `NULL` | **CHECK** (`chk_profile_fit`): `preferred_fit IN ('TIGHT', 'REGULAR', 'RELAXED')`. |
| `updated_at` | `TIMESTAMP` | NO | `CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP` | Last updated timestamp. |

---

### Table 3: `BRAND`
Catalog of apparel brands and their native sizing conventions.

| Column | Type | Nullable | Default | Constraints / Descriptions |
|---|---|---|---|---|
| `brand_id` | `INT` | NO | `AUTO_INCREMENT` | **PK** (`pk_brand`). |
| `brand_name` | `VARCHAR(100)` | NO | — | **UNIQUE** (`uq_brand_name`). Brand commercial name. |
| `sizing_system`| `VARCHAR(20)`| NO | — | **CHECK** (`chk_brand_sizing`): `sizing_system IN ('ALPHA', 'NUMERIC', 'WAIST_BASED')`. |

---

### Table 4: `GARMENT`
Garment styles offered by brands within bottom-wear categories.

| Column | Type | Nullable | Default | Constraints / Descriptions |
|---|---|---|---|---|
| `garment_id` | `INT` | NO | `AUTO_INCREMENT` | **PK** (`pk_garment`). |
| `brand_id` | `INT` | NO | — | **FK** (`fk_garment_brand`) -> `BRAND(brand_id)` **ON DELETE RESTRICT ON UPDATE CASCADE**. |
| `garment_name` | `VARCHAR(150)` | NO | — | Commercial model name (e.g., "Ribcage Straight Ankle"). |
| `garment_category`| `VARCHAR(30)` | NO | — | **CHECK** (`chk_garment_category`): `IN ('Jeans', 'Trousers')`. |
| `fit_type` | `VARCHAR(30)` | NO | — | **CHECK** (`chk_garment_fit`): `IN ('STRAIGHT', 'SLIM', 'SKINNY', 'WIDE_LEG', 'RELAXED', 'BOOTCUT', 'FLARED', 'OTHER')`. |
| `description` | `TEXT` | YES | `NULL` | Garment fabric composition, stretch factor, and style notes. |

**Indexes:**
- `idx_garment_brand (brand_id)`: Accelerates brand garment filtering.

---

### Table 5: `GARMENT_SIZE`
Specific sizes manufactured for each garment style.

| Column | Type | Nullable | Default | Constraints / Descriptions |
|---|---|---|---|---|
| `garment_size_id`| `INT` | NO | `AUTO_INCREMENT` | **PK** (`pk_garment_size`). |
| `garment_id` | `INT` | NO | — | **FK** (`fk_size_garment`) -> `GARMENT(garment_id)` **ON DELETE RESTRICT ON UPDATE CASCADE**. |
| `size_label` | `VARCHAR(20)` | NO | — | Commercial size label (e.g., "28", "M", "38"). |

**Unique Constraints & Indexes:**
- **UNIQUE** (`uq_garment_size`): `(garment_id, size_label)` prevents duplicate size labels per garment.
- `idx_garment_size_garment (garment_id)`: Speeds up size list lookups per garment.

---

### Table 6: `GARMENT_MEASUREMENT`
Physical garment dimensional specifications (e.g., flat waist, hip, rise, thigh, inseam).

| Column | Type | Nullable | Default | Constraints / Descriptions |
|---|---|---|---|---|
| `measurement_id`| `INT` | NO | `AUTO_INCREMENT` | **PK** (`pk_garment_measurement`). |
| `garment_size_id`| `INT` | NO | — | **FK** (`fk_measurement_size`) -> `GARMENT_SIZE(garment_size_id)` **ON DELETE CASCADE ON UPDATE CASCADE**. |
| `measurement_type`| `VARCHAR(20)`| NO | — | **CHECK** (`chk_measurement_type`): `IN ('waist', 'hip', 'thigh', 'inseam', 'rise')`. |
| `measurement_value`| `DECIMAL(6,2)`| NO | — | **CHECK** (`chk_measurement_value`): `measurement_value > 0`. |
| `unit` | `VARCHAR(5)` | NO | `'cm'` | **CHECK** (`chk_measurement_unit`): `unit IN ('cm', 'in')`. |

**Unique Constraints & Indexes:**
- **UNIQUE** (`uq_size_measurement`): `(garment_size_id, measurement_type)` enforces at most one measurement value per type per size.
- `idx_measurement_size (garment_size_id)`: Accelerates dimensional retrieval for sizing comparisons.

---

### Table 7: `PURCHASE`
Tracks actual apparel purchases, return/exchange outcomes, and customer fit satisfaction.

| Column | Type | Nullable | Default | Constraints / Descriptions |
|---|---|---|---|---|
| `purchase_id` | `INT` | NO | `AUTO_INCREMENT` | **PK** (`pk_purchase`). |
| `user_id` | `INT` | NO | — | **FK** (`fk_purchase_user`) -> `USER(user_id)` **ON DELETE RESTRICT ON UPDATE CASCADE**. |
| `garment_size_id`| `INT` | NO | — | **FK** (`fk_purchase_size`) -> `GARMENT_SIZE(garment_size_id)` **ON DELETE RESTRICT ON UPDATE CASCADE**. |
| `purchase_date`| `DATE` | NO | `(CURRENT_DATE)` | Date item was purchased. |
| `outcome` | `VARCHAR(10)` | NO | — | **CHECK** (`chk_purchase_outcome`): `IN ('KEPT', 'RETURNED', 'EXCHANGED')`. |
| `fit_satisfaction`| `VARCHAR(10)`| YES | `NULL` | **CHECK** (`chk_purchase_satisfaction`): `IN ('GOOD', 'AVERAGE', 'POOR')`. |
| `fit_preference`| `VARCHAR(20)` | YES | `NULL` | **CHECK** (`chk_purchase_preference`): `IN ('TIGHT', 'REGULAR', 'RELAXED')`. |

**Recommendation Evidence Criteria:**
- High-confidence size evidence is defined as: `outcome = 'KEPT' AND fit_satisfaction = 'GOOD'`.

**Indexes:**
- `idx_purchase_user (user_id)`: Accelerates user fit history retrieval.
- `idx_purchase_size (garment_size_id)`: Accelerates size return rate calculations.

---

### Table 8: `FIT_REVIEW`
Customer natural-language fit reviews and localized fit ratings.

| Column | Type | Nullable | Default | Constraints / Descriptions |
|---|---|---|---|---|
| `review_id` | `INT` | NO | `AUTO_INCREMENT` | **PK** (`pk_fit_review`). |
| `user_id` | `INT` | NO | — | **FK** (`fk_review_user`) -> `USER(user_id)` **ON DELETE RESTRICT ON UPDATE CASCADE**. |
| `garment_size_id`| `INT` | NO | — | **FK** (`fk_review_size`) -> `GARMENT_SIZE(garment_size_id)` **ON DELETE RESTRICT ON UPDATE CASCADE**. |
| `overall_fit` | `VARCHAR(20)` | NO | — | **CHECK** (`chk_review_overall_fit`): `IN ('TOO_SMALL', 'SLIGHTLY_SMALL', 'TRUE_TO_SIZE', 'SLIGHTLY_LARGE', 'TOO_LARGE')`. |
| `waist_fit` | `VARCHAR(10)` | YES | `NULL` | **CHECK** (`chk_review_waist_fit`): `IN ('TIGHT', 'GOOD', 'LOOSE')`. |
| `hip_fit` | `VARCHAR(10)` | YES | `NULL` | **CHECK** (`chk_review_hip_fit`): `IN ('TIGHT', 'GOOD', 'LOOSE')`. |
| `thigh_fit` | `VARCHAR(10)` | YES | `NULL` | **CHECK** (`chk_review_thigh_fit`): `IN ('TIGHT', 'GOOD', 'LOOSE')`. |
| `length_fit` | `VARCHAR(10)` | YES | `NULL` | **CHECK** (`chk_review_length_fit`): `IN ('SHORT', 'GOOD', 'LONG')`. |
| `review_text` | `TEXT` | NO | — | Detailed written feedback. **CHECK** (`chk_review_text`): `CHAR_LENGTH(TRIM(review_text)) > 0`. |
| `created_at` | `TIMESTAMP` | NO | `CURRENT_TIMESTAMP` | Review timestamp. |

**Vector Database Synchronization:**
- Each `FIT_REVIEW` record triggers the generation of a 384-dimensional dense vector from `review_text` that is indexed into Redis Stack with metadata references (`review_id`, `garment_size_id`, `overall_fit`).

**Indexes:**
- `idx_review_user (user_id)`: Lookups for reviews written by a user.
- `idx_review_size (garment_size_id)`: Lookups for reviews written for a specific garment size.
