# FitCheck — Relational Schema Documentation & Data Dictionary

This document details the normalized relational database schema implemented in `database/fitcheck_setup.sql` and visualized in `docs/diagrams/dbms_mini_v4.drawio`, `docs/diagrams/er_diagram.png`, and `docs/diagrams/relational_schema.png`.

### Print-Ready Artifacts:
- **Conceptual ER Diagram:** [docs/diagrams/er_diagram.pdf](file:///C:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/docs/diagrams/er_diagram.pdf) | [docs/diagrams/er_diagram.png](file:///C:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/docs/diagrams/er_diagram.png) | [docs/diagrams/er_diagram.svg](file:///C:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/docs/diagrams/er_diagram.svg)
- **Relational Schema & Constraints:** [docs/diagrams/relational_schema.pdf](file:///C:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/docs/diagrams/relational_schema.pdf) | [docs/diagrams/relational_schema.png](file:///C:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/docs/diagrams/relational_schema.png) | [docs/diagrams/relational_schema.svg](file:///C:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/docs/diagrams/relational_schema.svg)
- **Draw.io Source Diagram:** [docs/diagrams/dbms_mini_v4.drawio](file:///C:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/docs/diagrams/dbms_mini_v4.drawio)

---

## 1. Schema Overview & Entity Classification

The database is built on **MySQL 8.0+** using the `InnoDB` storage engine for ACID compliance, row-level locking, and foreign key enforcement.

```
       +------------------+           +------------------+
       |       USER       | <-------- |   BODY_PROFILE   |
       +------------------+ (1:0..1)  +------------------+
         |              |
  (1:N)  |              | (1:N)
         v              v
   +----------+   +------------+
   | PURCHASE |   | FIT_REVIEW |  <=====>  [Redis Vector Hash: review_vector:{id}]
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

### Formal Classification of Entities (Strong vs Dependent / Weak)

In strict accordance with relational database theory and the DBMS Level 3 evaluation criteria, entities in FitCheck are categorized based on existence dependency and identifier autonomy:

1. **Strong (Regular) Entities:**
   - **`USER`**: Possesses autonomous existence with surrogate primary key `user_id`. Users exist independently of whether they have logged a body profile, purchase, or review.
   - **`BRAND`**: Autonomous catalog entity with primary key `brand_id` and unique commercial name `brand_name`. Does not depend on the existence of any garment style.
   - **`GARMENT`**: Autonomous apparel style entity identified by `garment_id`. While it references `BRAND(brand_id)` via a mandatory foreign key, it represents a distinct commercial entity with its own independent primary key and lifecycle.

2. **Dependent / Subordinate Entities:**
   - **`BODY_PROFILE`**: Exists in a strict 1-to-0..1 subordinate relationship with `USER`. It shares `user_id` as a foreign key with `ON DELETE CASCADE`. A body profile cannot exist without an underlying registered user.
   - **`GARMENT_SIZE`**: Subordinate entity whose business identity is discriminated by `(garment_id, size_label)`. Size labels (e.g. "28", "M", "32W 30L") are meaningful only within the scope of a specific `GARMENT`.
   - **`GARMENT_MEASUREMENT`**: Dependent measurement specification entity linked to `GARMENT_SIZE` with `ON DELETE CASCADE`. Each row specifies a physical dimension (`waist`, `hip`, `thigh`, etc.) for a specific garment size.

3. **Associative / Transactional Entities:**
   - **`PURCHASE`**: Models the many-to-many relationship between `USER` and `GARMENT_SIZE`, recording historical acquisition dates, outcomes (`KEPT`, `RETURNED`, `EXCHANGED`), and personalized fit satisfaction (`GOOD`, `AVERAGE`, `POOR`).
   - **`FIT_REVIEW`**: Models the many-to-many relationship between `USER` and `GARMENT_SIZE`, capturing public natural-language fit reviews and localized categorical ratings (`overall_fit`, `waist_fit`, etc.). Synchronized to Redis Stack for semantic vector search.

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
