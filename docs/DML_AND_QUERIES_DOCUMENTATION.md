# FitCheck — DML Operations & Advanced SQL Queries Documentation

This document fulfills **DBMS Level 3 Evaluation Rubric Items 6 & 7: DML Operations (4 Marks) and Complex SQL Queries (4 Marks)**.

- **Executable SQL Script:** [`database/fitcheck_dml.sql`](file:///C:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/database/fitcheck_dml.sql)
- **Authoritative Seed Dataset:** [`database/seeds/seed_data.sql`](file:///C:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/database/seeds/seed_data.sql) and [`database/seeds/review_seeds.sql`](file:///C:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/database/seeds/review_seeds.sql)

---

## 1. DML Operations Demonstration (Rubric Item 6)

### 1.1 `INSERT` Operations
Demonstrates insertion across strong, dependent, and associative tables with referential integrity:
- `INSERT INTO USER`: Registers user account with hashed bcrypt credentials and role enforcement (`USER` or `ADMIN`).
- `INSERT INTO BODY_PROFILE`: Creates the 1:1 dependent profile enforcing positive measurements (`waist > 0`, `hip > 0`).
- `INSERT INTO PURCHASE`: Captures a purchase outcome (`KEPT`, `RETURNED`, `EXCHANGED`) and fit satisfaction (`GOOD`, `AVERAGE`, `POOR`).
- `INSERT INTO FIT_REVIEW`: Captures public crowd reviews and localized fit ratings (`overall_fit`, `waist_fit`, etc.).

### 1.2 `UPDATE` Operations
- Body Profile update: Modifies waist measurement with automatic timestamp update (`updated_at = CURRENT_TIMESTAMP`). Validated by trigger `trg_before_body_profile_update`.
- Purchase status update: Updates outcome from `KEPT` to `EXCHANGED` when a customer returns an ill-fitting size.

### 1.3 `DELETE` Operations
- Cascading verification: Removing disposable test records cleanly without leaving orphaned records.

### 1.4 `SELECT` Operations
- Targeted single-table and joined projections for user dashboards.

---

## 2. Multi-Table JOIN Queries (Rubric Item 7)

### 2.1 4-Table Inner Join: Full Garment Measurement Catalog
Traverses the complete commercial catalog hierarchy:
`BRAND -> GARMENT -> GARMENT_SIZE -> GARMENT_MEASUREMENT`

```sql
SELECT 
    b.brand_name,
    b.sizing_system,
    g.garment_name,
    g.garment_category,
    g.fit_type,
    s.size_label,
    m.measurement_type,
    m.measurement_value,
    m.unit
FROM BRAND b
INNER JOIN GARMENT g ON b.brand_id = g.brand_id
INNER JOIN GARMENT_SIZE s ON g.garment_id = s.garment_id
INNER JOIN GARMENT_MEASUREMENT m ON s.garment_size_id = m.garment_size_id
ORDER BY b.brand_name, g.garment_name, s.garment_size_id, m.measurement_type;
```

### 2.2 Left Outer Join: Identifying Unreviewed / Cold-Start Garment Sizes
Uses `LEFT JOIN FIT_REVIEW` to determine which sizes have sparse review coverage (<= 2 reviews) to trigger cold-start caveat warnings in recommendation output.

---

## 3. Aggregates with `GROUP BY` and `HAVING` (Rubric Item 7)

### Brand Return Rate Consistency Analysis
Computes return percentages per brand for all brands with at least 3 historical customer purchases. Identifies brands with sizing volatility or vanity sizing discrepancies.

```sql
SELECT 
    b.brand_name,
    COUNT(p.purchase_id) AS total_purchases,
    SUM(CASE WHEN p.outcome = 'KEPT' THEN 1 ELSE 0 END) AS kept_count,
    SUM(CASE WHEN p.outcome = 'RETURNED' THEN 1 ELSE 0 END) AS return_count,
    ROUND(SUM(CASE WHEN p.outcome = 'RETURNED' THEN 1 ELSE 0 END) * 100.0 / COUNT(p.purchase_id), 2) AS return_rate_pct
FROM BRAND b
JOIN GARMENT g ON b.brand_id = g.brand_id
JOIN GARMENT_SIZE s ON g.garment_id = s.garment_id
JOIN PURCHASE p ON s.garment_size_id = p.garment_size_id
GROUP BY b.brand_id, b.brand_name
HAVING total_purchases >= 3
ORDER BY return_rate_pct DESC;
```

---

## 4. Nested & Correlated Subqueries (Rubric Item 7)

### 4.1 Nested Subquery with `IN`
Identifies garments that have received customer feedback flagged as `TOO_SMALL` or `TOO_LARGE`:
```sql
SELECT g.garment_id, g.garment_name, g.garment_category
FROM GARMENT g
WHERE g.garment_id IN (
    SELECT s.garment_id
    FROM GARMENT_SIZE s
    WHERE s.garment_size_id IN (
        SELECT r.garment_size_id
        FROM FIT_REVIEW r
        WHERE r.overall_fit IN ('TOO_SMALL', 'TOO_LARGE')
    )
);
```

### 4.2 Correlated Subquery
Finds users whose current body profile waist is smaller than the average waist of garments they have successfully `KEPT` (indicating preference for looser cuts or vanity sizing allowances):
```sql
SELECT u.user_id, u.name, bp.waist AS user_waist
FROM `USER` u
JOIN BODY_PROFILE bp ON u.user_id = bp.user_id
WHERE bp.waist IS NOT NULL
  AND bp.waist < (
      SELECT AVG(m.measurement_value)
      FROM PURCHASE p
      JOIN GARMENT_SIZE s ON p.garment_size_id = s.garment_size_id
      JOIN GARMENT_MEASUREMENT m ON s.garment_size_id = m.garment_size_id
      WHERE p.user_id = u.user_id
        AND p.outcome = 'KEPT'
        AND m.measurement_type = 'waist'
  );
```

---

## 5. Common Table Expressions (CTE) & Recursive Queries (Rubric Item 7)

### 5.1 Standard CTE: Sizing Delta Calculation
Ranks sizes in an unfamiliar brand based on combined waist and hip dimensional deltas relative to authenticated user reference dimensions.

### 5.2 Recursive CTE: Sizing Gradation Progression
Generates a recursive sequence of nominal apparel sizes stepping up by 2 nominal size units and 2.54 cm (1 inch) waist progression from base size 24 up to size 36:
```sql
WITH RECURSIVE SizeProgression AS (
    SELECT 1 AS step_index, 24 AS nominal_size, 61.00 AS waist_cm, 'Base Size (XS)' AS classification
    UNION ALL
    SELECT step_index + 1, nominal_size + 2, ROUND(waist_cm + 2.54, 2),
        CASE 
            WHEN step_index + 1 <= 2 THEN 'Small (S)'
            WHEN step_index + 1 <= 4 THEN 'Medium (M)'
            WHEN step_index + 1 <= 6 THEN 'Large (L)'
            ELSE 'Plus (XL+)'
        END
    FROM SizeProgression
    WHERE step_index < 7
)
SELECT step_index, nominal_size, waist_cm, ROUND(waist_cm / 2.54, 1) AS waist_inches, classification
FROM SizeProgression;
```
