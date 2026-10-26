# FitCheck — Advanced Database Concepts Documentation

This document fulfills **DBMS Level 3 Evaluation Rubric Item 8: Advanced Database Concepts (Procedure, Function, Trigger, View, Transaction, CTE, Indexing) (6 Marks)**.

- **Source SQL File:** [`database/queries/advanced_concepts.sql`](file:///C:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/database/queries/advanced_concepts.sql)

---

## 1. Stored Function: `fn_convert_to_cm`

### Purpose:
Normalizes multi-unit garment measurement inputs into centimeters so that comparisons across brands with mixed metric (`cm`) and imperial (`in`) conventions are strictly comparable.

### Definition:
```sql
CREATE FUNCTION fn_convert_to_cm(val DECIMAL(6,2), unit VARCHAR(5))
RETURNS DECIMAL(6,2)
DETERMINISTIC
BEGIN
    IF LOWER(unit) = 'in' THEN
        RETURN ROUND(val * 2.54, 2);
    ELSE
        RETURN val;
    END IF;
END;
```

### Demonstration Execution & Expected Output:
```sql
SELECT 
    fn_convert_to_cm(28.50, 'in') AS waist_28_5_in_to_cm,
    fn_convert_to_cm(72.00, 'cm') AS waist_72_cm_to_cm;
```
**Expected Output:**
| waist_28_5_in_to_cm | waist_72_cm_to_cm |
|---|---|
| 72.39 | 72.00 |

---

## 2. Stored Procedure: `sp_recommend_size_for_waist`

### Purpose:
Calculates the optimal garment size for a target garment given the customer's waist measurement and fit preference (`TIGHT`, `REGULAR`, `RELAXED`), incorporating appropriate ease allowance:
- `TIGHT`: 0.00 cm ease
- `REGULAR`: 1.50 cm ease
- `RELAXED`: 3.00 cm ease

### Definition:
```sql
CREATE PROCEDURE sp_recommend_size_for_waist(
    IN p_garment_id INT,
    IN p_user_waist DECIMAL(5,2),
    IN p_preferred_fit VARCHAR(20)
)
BEGIN
    DECLARE v_ease DECIMAL(4,2) DEFAULT 0.00;
    IF p_preferred_fit = 'TIGHT' THEN SET v_ease = 0.00;
    ELSEIF p_preferred_fit = 'RELAXED' THEN SET v_ease = 3.00;
    ELSE SET v_ease = 1.50; END IF;

    SELECT 
        s.garment_size_id,
        s.size_label,
        m.measurement_value AS garment_waist_cm,
        (p_user_waist + v_ease) AS target_waist_with_ease,
        ROUND(ABS(m.measurement_value - (p_user_waist + v_ease)), 2) AS delta_cm
    FROM GARMENT_SIZE s
    JOIN GARMENT_MEASUREMENT m ON s.garment_size_id = m.garment_size_id
    WHERE s.garment_id = p_garment_id
      AND m.measurement_type = 'waist'
    ORDER BY delta_cm ASC
    LIMIT 1;
END;
```

### Demonstration Invocation:
```sql
CALL sp_recommend_size_for_waist(1, 71.00, 'REGULAR');
```
**Expected Output:**
Recommends the size whose garment waist is closest to `71.00 + 1.50 = 72.50 cm` (e.g. Levi's 501 Size 28).

---

## 3. Database Triggers

### 3.1 Validation Trigger: `trg_before_body_profile_update`
- **Timing:** `BEFORE UPDATE ON BODY_PROFILE`
- **Action:** Validates that measurements (`waist`, `hip`, `thigh`, `inseam`, `height`) are strictly positive (> 0). Raises `SQLSTATE '45000'` with informative error message if negative or zero values are submitted.

### 3.2 Audit Lifecycle Triggers: `trg_after_review_insert`, `trg_after_review_update`, `trg_after_review_delete`
- **Timing:** `AFTER INSERT / UPDATE / DELETE ON FIT_REVIEW`
- **Target Table:** `REVIEW_AUDIT (audit_id, review_id, action, user_id, changed_at, details)`
- **Lineage Tracking:** Automatically logs creation, content modifications, and deletions for compliance, vector sync synchronization, and moderation tracking.

### Safe Before-and-After Demonstration Workflow:
1. `INSERT INTO FIT_REVIEW (...)` -> Generates `REVIEW_AUDIT` row with `action = 'INSERT'`.
2. `UPDATE FIT_REVIEW SET overall_fit = 'SLIGHTLY_LARGE' (...)` -> Generates `REVIEW_AUDIT` row with `action = 'UPDATE'`.
3. `DELETE FROM FIT_REVIEW (...)` -> Generates `REVIEW_AUDIT` row with `action = 'DELETE'`.
4. Inspecting `SELECT * FROM REVIEW_AUDIT WHERE review_id = @test_review_id` displays the complete, untampered historical data lineage.

---

## 4. Database View: `vw_garment_catalog_summary`

### Purpose:
Provides an aggregated, read-optimized projection joining `BRAND`, `GARMENT`, and `GARMENT_SIZE` with `GROUP_CONCAT` of available sizes for fast catalog browsing without application-side JOIN overhead.

```sql
CREATE VIEW vw_garment_catalog_summary AS
SELECT 
    g.garment_id,
    b.brand_name,
    g.garment_name,
    g.garment_category,
    g.fit_type,
    COUNT(s.garment_size_id) AS total_sizes,
    GROUP_CONCAT(s.size_label ORDER BY s.garment_size_id SEPARATOR ', ') AS available_sizes
FROM GARMENT g
JOIN BRAND b ON g.brand_id = b.brand_id
LEFT JOIN GARMENT_SIZE s ON g.garment_id = s.garment_id
GROUP BY g.garment_id, b.brand_name, g.garment_name, g.garment_category, g.fit_type;
```

---

## 5. ACID Transaction Semantics

### Demonstration:
- **Commit:**
  ```sql
  START TRANSACTION;
  INSERT INTO PURCHASE (user_id, garment_size_id, outcome, fit_satisfaction, fit_preference)
  VALUES (1, 1, 'KEPT', 'GOOD', 'REGULAR');
  COMMIT;
  ```
- **Rollback:**
  ```sql
  START TRANSACTION;
  INSERT INTO PURCHASE (user_id, garment_size_id, outcome, fit_satisfaction, fit_preference)
  VALUES (1, 1, 'RETURNED', 'POOR', 'TIGHT');
  ROLLBACK; -- Row is immediately undone and not persisted
  ```

---

## 6. Query Plan & Performance Indexing (`EXPLAIN`)

Query performance is safeguarded through explicit B-tree indexes:
- `idx_garment_brand` on `GARMENT(brand_id)`
- `idx_garment_size_garment` on `GARMENT_SIZE(garment_id)`
- `idx_measurement_size` on `GARMENT_MEASUREMENT(garment_size_id)`
- `idx_purchase_user` & `idx_purchase_size` on `PURCHASE`
- `idx_review_size` on `FIT_REVIEW`

Running `EXPLAIN` confirms index-driven lookups avoiding full table scans.
