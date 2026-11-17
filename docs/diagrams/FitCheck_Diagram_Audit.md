# FitCheck diagram schema audit

Source: live MySQL INFORMATION_SCHEMA / SHOW CREATE TABLE, cross-checked with database/fitcheck_setup.sql, database/fitcheck_ddl.sql, database/queries/advanced_concepts.sql and SQLAlchemy models.
No database objects or data were changed. The setup script creates eight core tables; the DDL/advanced-concepts scripts and model additionally implement REVIEW_AUDIT.

| Relation | Primary key | Other candidate / UNIQUE keys | Classification | Identifying relationship |
|---|---|---|---|---|
| USER | user_id | (email) | Regular, independent surrogate PK | None |
| BODY_PROFILE | profile_id | (user_id) | Regular, independent surrogate PK | None |
| BRAND | brand_id | (brand_name) | Regular, independent surrogate PK | None |
| GARMENT | garment_id | None | Regular, independent surrogate PK | None |
| GARMENT_SIZE | garment_size_id | (garment_id, size_label) | Regular, independent surrogate PK | None |
| GARMENT_MEASUREMENT | measurement_id | (garment_size_id, measurement_type) | Regular, independent surrogate PK | None |
| PURCHASE | purchase_id | None | Regular, independent surrogate PK | None |
| FIT_REVIEW | review_id | None | Regular, independent surrogate PK | None |
| REVIEW_AUDIT | audit_id | None | Regular, independent surrogate PK | None |

GARMENT_SIZE and GARMENT_MEASUREMENT are existence-dependent on their parent entities, but they are modeled as regular entities because the implemented schema assigns each an independent surrogate primary key. Therefore they are not weak entities under strict Chen identification semantics.

## Complete FK / participation matrix

The internal matrix uses (min,max) participation. The final Chen image uses traditional 1/N maximum-cardinality labels instead: 1 at the parent, N at the child (1 at both ends for the UNIQUE profile FK). Double child-side lines show total participation; single parent-side lines show optional participation. Every FK is NOT NULL, but the database does not require any parent to have children.

| Constraint | Child column | Parent key | Parent participation | Child participation | ON DELETE | ON UPDATE |
|---|---|---|---|---|---|---|
| fk_profile_user | BODY_PROFILE.user_id | USER.user_id | (0,1) | (1,1) | CASCADE | CASCADE |
| fk_garment_brand | GARMENT.brand_id | BRAND.brand_id | (0,N) | (1,1) | RESTRICT | CASCADE |
| fk_size_garment | GARMENT_SIZE.garment_id | GARMENT.garment_id | (0,N) | (1,1) | RESTRICT | CASCADE |
| fk_measurement_size | GARMENT_MEASUREMENT.garment_size_id | GARMENT_SIZE.garment_size_id | (0,N) | (1,1) | CASCADE | CASCADE |
| fk_purchase_size | PURCHASE.garment_size_id | GARMENT_SIZE.garment_size_id | (0,N) | (1,1) | RESTRICT | CASCADE |
| fk_purchase_user | PURCHASE.user_id | USER.user_id | (0,N) | (1,1) | RESTRICT | CASCADE |
| fk_review_size | FIT_REVIEW.garment_size_id | GARMENT_SIZE.garment_size_id | (0,N) | (1,1) | RESTRICT | CASCADE |
| fk_review_user | FIT_REVIEW.user_id | USER.user_id | (0,N) | (1,1) | RESTRICT | CASCADE |

REVIEW_AUDIT has no FK on review_id or user_id. Both are historical values, not referential relationships. The audit triggers record review lifecycle events; history survives review deletion. The diagrams deliberately show the audit table without referential connectors and explain this in a note.

## Columns and CHECK constraints

### USER

`user_id` int NOT NULL, `name` varchar(100) NOT NULL, `email` varchar(255) NOT NULL, `password_hash` varchar(255) NOT NULL, `role` varchar(10) NOT NULL, `created_at` timestamp NOT NULL
- `chk_user_role`: `(`role` in (_cp850\'USER\',_cp850\'ADMIN\'))`

### BODY_PROFILE

`profile_id` int NOT NULL, `user_id` int NOT NULL, `height` decimal(5,2) NULL, `waist` decimal(5,2) NULL, `hip` decimal(5,2) NULL, `thigh` decimal(5,2) NULL, `inseam` decimal(5,2) NULL, `preferred_fit` varchar(20) NULL, `updated_at` timestamp NOT NULL
- `chk_profile_height`: `((`height` is null) or (`height` > 0))`
- `chk_profile_waist`: `((`waist` is null) or (`waist` > 0))`
- `chk_profile_hip`: `((`hip` is null) or (`hip` > 0))`
- `chk_profile_thigh`: `((`thigh` is null) or (`thigh` > 0))`
- `chk_profile_inseam`: `((`inseam` is null) or (`inseam` > 0))`
- `chk_profile_fit`: `((`preferred_fit` is null) or (`preferred_fit` in (_cp850\'TIGHT\',_cp850\'REGULAR\',_cp850\'RELAXED\')))`

### BRAND

`brand_id` int NOT NULL, `brand_name` varchar(100) NOT NULL, `sizing_system` varchar(20) NOT NULL
- `chk_brand_sizing`: `(`sizing_system` in (_cp850\'ALPHA\',_cp850\'NUMERIC\',_cp850\'WAIST_BASED\'))`

### GARMENT

`garment_id` int NOT NULL, `brand_id` int NOT NULL, `garment_name` varchar(150) NOT NULL, `garment_category` varchar(30) NOT NULL, `fit_type` varchar(30) NOT NULL, `description` text NULL
- `chk_garment_category`: `(`garment_category` in (_cp850\'Jeans\',_cp850\'Trousers\'))`
- `chk_garment_fit`: `(`fit_type` in (_cp850\'STRAIGHT\',_cp850\'SLIM\',_cp850\'SKINNY\',_cp850\'WIDE_LEG\',_cp850\'RELAXED\',_cp850\'BOOTCUT\',_cp850\'FLARED\',_cp850\'OTHER\'))`

### GARMENT_SIZE

`garment_size_id` int NOT NULL, `garment_id` int NOT NULL, `size_label` varchar(20) NOT NULL

### GARMENT_MEASUREMENT

`measurement_id` int NOT NULL, `garment_size_id` int NOT NULL, `measurement_type` varchar(20) NOT NULL, `measurement_value` decimal(6,2) NOT NULL, `unit` varchar(5) NOT NULL
- `chk_measurement_type`: `(`measurement_type` in (_cp850\'waist\',_cp850\'hip\',_cp850\'thigh\',_cp850\'inseam\',_cp850\'rise\'))`
- `chk_measurement_value`: `(`measurement_value` > 0)`
- `chk_measurement_unit`: `(`unit` in (_cp850\'cm\',_cp850\'in\'))`

### PURCHASE

`purchase_id` int NOT NULL, `user_id` int NOT NULL, `garment_size_id` int NOT NULL, `purchase_date` date NOT NULL, `outcome` varchar(10) NOT NULL, `fit_satisfaction` varchar(10) NULL, `fit_preference` varchar(20) NULL
- `chk_purchase_outcome`: `(`outcome` in (_cp850\'KEPT\',_cp850\'RETURNED\',_cp850\'EXCHANGED\'))`
- `chk_purchase_satisfaction`: `((`fit_satisfaction` is null) or (`fit_satisfaction` in (_cp850\'GOOD\',_cp850\'AVERAGE\',_cp850\'POOR\')))`
- `chk_purchase_preference`: `((`fit_preference` is null) or (`fit_preference` in (_cp850\'TIGHT\',_cp850\'REGULAR\',_cp850\'RELAXED\')))`

### FIT_REVIEW

`review_id` int NOT NULL, `user_id` int NOT NULL, `garment_size_id` int NOT NULL, `overall_fit` varchar(20) NOT NULL, `waist_fit` varchar(10) NULL, `hip_fit` varchar(10) NULL, `thigh_fit` varchar(10) NULL, `length_fit` varchar(10) NULL, `review_text` text NOT NULL, `created_at` timestamp NOT NULL
- `chk_review_hip_fit`: `((`hip_fit` is null) or (`hip_fit` in (_utf8mb4\'TIGHT\',_utf8mb4\'GOOD\',_utf8mb4\'LOOSE\')))`
- `chk_review_length_fit`: `((`length_fit` is null) or (`length_fit` in (_utf8mb4\'SHORT\',_utf8mb4\'GOOD\',_utf8mb4\'LONG\')))`
- `chk_review_overall_fit`: `(`overall_fit` in (_utf8mb4\'TOO_SMALL\',_utf8mb4\'SLIGHTLY_SMALL\',_utf8mb4\'TRUE_TO_SIZE\',_utf8mb4\'SLIGHTLY_LARGE\',_utf8mb4\'TOO_LARGE\'))`
- `chk_review_text`: `(char_length(trim(`review_text`)) > 0)`
- `chk_review_thigh_fit`: `((`thigh_fit` is null) or (`thigh_fit` in (_utf8mb4\'TIGHT\',_utf8mb4\'GOOD\',_utf8mb4\'LOOSE\')))`
- `chk_review_waist_fit`: `((`waist_fit` is null) or (`waist_fit` in (_utf8mb4\'TIGHT\',_utf8mb4\'GOOD\',_utf8mb4\'LOOSE\')))`

### REVIEW_AUDIT

`audit_id` int NOT NULL, `review_id` int NOT NULL, `action` varchar(20) NOT NULL, `user_id` int NOT NULL, `changed_at` timestamp NULL, `details` text NULL

## Source / rendering notes

FitCheck_Schema_Audit.json preserves the metadata used to generate both diagrams. The renderer verifies nine entities, all columns, all primary keys and all eight FK connectors. No double rectangles, double diamonds, derived attributes or multivalued attributes are invented.
The current live review_text type is represented as captured. Review Settings may legitimately switch its TEXT/MEDIUMTEXT capacity later without changing its conceptual attribute.
Live/source difference: REVIEW_AUDIT currently has action VARCHAR(20), user_id NOT NULL and changed_at TIMESTAMP NULL; the DDL template declares VARCHAR(10), user_id NULL and changed_at NOT NULL. The diagrams and snapshot follow the actual live MySQL definition; no implementation was changed. These differences do not create any foreign keys or alter audit-history semantics.
Older narrative documents and the original Draw.io reference are outside this diagram-only correction. Use the two Final images and synchronized image/vector/PDF aliases for submission.
