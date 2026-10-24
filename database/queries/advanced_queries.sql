-- ============================================================
-- FITCHECK — ADVANCED SQL QUERIES TEMPLATE
-- Covers: Joins, Aggregates, GROUP BY, HAVING, Subqueries, CTEs
-- Derived from DBMS Level 3 Evaluation Rubric (Items 3 & 7)
-- ============================================================

USE fitcheck;

-- ------------------------------------------------------------
-- 1. MULTI-TABLE JOIN (4 Tables):
-- Retrieve complete dimensional specs for each garment size,
-- including Brand, Garment Name, Fit Type, Size, and Measurements (cm).
-- ------------------------------------------------------------
SELECT 
    b.brand_name,
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

-- ------------------------------------------------------------
-- 2. AGGREGATE WITH GROUP BY & HAVING:
-- Calculate return rates per brand. Identify brands with high return rates
-- (> 30%) across at least 3 recorded purchases.
-- ------------------------------------------------------------
SELECT 
    b.brand_name,
    COUNT(p.purchase_id) AS total_purchases,
    SUM(CASE WHEN p.outcome = 'RETURNED' THEN 1 ELSE 0 END) AS total_returns,
    ROUND(SUM(CASE WHEN p.outcome = 'RETURNED' THEN 1 ELSE 0 END) * 100.0 / COUNT(p.purchase_id), 2) AS return_rate_pct
FROM BRAND b
JOIN GARMENT g ON b.brand_id = g.brand_id
JOIN GARMENT_SIZE s ON g.garment_id = s.garment_id
JOIN PURCHASE p ON s.garment_size_id = p.garment_size_id
GROUP BY b.brand_id, b.brand_name
HAVING total_purchases >= 3
ORDER BY return_rate_pct DESC;

-- ------------------------------------------------------------
-- 3. CORRELATED SUBQUERY:
-- Find all users whose personal waist measurement is smaller than
-- the average waist measurement across all garments they have successfully 'KEPT'.
-- ------------------------------------------------------------
SELECT 
    u.user_id,
    u.name,
    bp.waist AS user_waist
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
        AND p.fit_satisfaction = 'GOOD'
        AND m.measurement_type = 'waist'
  );

-- ------------------------------------------------------------
-- 4. NESTED SUBQUERY WITH IN:
-- Retrieve garments that have received at least one review with 'TOO_SMALL'
-- fit feedback and average rating concerns.
-- ------------------------------------------------------------
SELECT 
    g.garment_id,
    g.garment_name,
    g.garment_category
FROM GARMENT g
WHERE g.garment_id IN (
    SELECT s.garment_id
    FROM GARMENT_SIZE s
    WHERE s.garment_size_id IN (
        SELECT r.garment_size_id
        FROM FIT_REVIEW r
        WHERE r.overall_fit IN ('TOO_SMALL', 'SLIGHTLY_SMALL')
    )
);

-- ------------------------------------------------------------
-- 5. COMMON TABLE EXPRESSION (CTE):
-- Cross-Brand Equivalent Size Matching CTE:
-- Given a reference user measurement (or reference size), compute the closest
-- size in an unfamiliar target brand by calculating absolute waist and hip deltas.
-- ------------------------------------------------------------
WITH TargetBrandSpecs AS (
    SELECT 
        b.brand_name,
        g.garment_name,
        s.garment_size_id,
        s.size_label,
        MAX(CASE WHEN m.measurement_type = 'waist' THEN m.measurement_value END) AS waist_cm,
        MAX(CASE WHEN m.measurement_type = 'hip' THEN m.measurement_value END) AS hip_cm
    FROM BRAND b
    JOIN GARMENT g ON b.brand_id = g.brand_id
    JOIN GARMENT_SIZE s ON g.garment_id = s.garment_id
    JOIN GARMENT_MEASUREMENT m ON s.garment_size_id = m.garment_size_id
    WHERE b.brand_name = 'Zara'
    GROUP BY b.brand_name, g.garment_name, s.garment_size_id, s.size_label
),
UserReference AS (
    -- Reference dimensions (e.g. from a Levi's Size 28 purchase)
    SELECT 70.00 AS ref_waist, 96.00 AS ref_hip
)
SELECT 
    t.brand_name,
    t.garment_name,
    t.size_label,
    t.waist_cm,
    t.hip_cm,
    ROUND(ABS(t.waist_cm - r.ref_waist) + ABS(t.hip_cm - r.ref_hip), 2) AS dimensional_delta_cm
FROM TargetBrandSpecs t
CROSS JOIN UserReference r
ORDER BY dimensional_delta_cm ASC
LIMIT 3;
