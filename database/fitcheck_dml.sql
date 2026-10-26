-- ============================================================
-- FITCHECK — STANDALONE DML OPERATIONS & ADVANCED QUERIES
-- MySQL 8.0+
--
-- Covers DBMS Level 3 Evaluation Rubric:
-- Item 6: DML Operations (INSERT, UPDATE, DELETE, SELECT) (4 Marks)
-- Item 7: Nested, Correlated, Recursive Queries & Joins (4 Marks)
-- ============================================================

USE fitcheck;

-- ============================================================
-- PART 1: DML OPERATIONS (INSERT, UPDATE, DELETE, SELECT)
-- ============================================================

-- 1.1 INSERT: Registering a user and personal body profile
INSERT INTO `USER` (name, email, password_hash, role)
VALUES ('DML Demo User', 'dmldemo@fitcheck.internal', '$2b$12$e8Yk2uW5E7eU5E8k2uW5E.1234567890abcdefghijklmnopqrstuvw', 'USER');

SET @demo_user_id = LAST_INSERT_ID();

INSERT INTO BODY_PROFILE (user_id, height, waist, hip, thigh, inseam, preferred_fit)
VALUES (@demo_user_id, 168.00, 71.50, 97.00, 56.00, 76.00, 'REGULAR');

-- 1.2 INSERT: Recording a purchase transaction
INSERT INTO PURCHASE (user_id, garment_size_id, purchase_date, outcome, fit_satisfaction, fit_preference)
VALUES (@demo_user_id, 1, CURRENT_DATE, 'KEPT', 'GOOD', 'REGULAR');

SET @demo_purchase_id = LAST_INSERT_ID();

-- 1.3 INSERT: Posting a community fit review
INSERT INTO FIT_REVIEW (user_id, garment_size_id, overall_fit, waist_fit, hip_fit, thigh_fit, length_fit, review_text)
VALUES (@demo_user_id, 1, 'TRUE_TO_SIZE', 'GOOD', 'GOOD', 'GOOD', 'GOOD', 'DML test review: Waistband fits comfortably true to size with slight stretch.');

SET @demo_review_id = LAST_INSERT_ID();

-- 1.4 UPDATE: Updating user body profile with newly measured waist
UPDATE BODY_PROFILE
SET waist = 72.00,
    updated_at = CURRENT_TIMESTAMP
WHERE user_id = @demo_user_id;

-- 1.5 UPDATE: Updating purchase outcome following an exchange
UPDATE PURCHASE
SET outcome = 'EXCHANGED',
    fit_satisfaction = 'AVERAGE'
WHERE purchase_id = @demo_purchase_id;

-- 1.6 SELECT: Basic retrieval with filtering
SELECT u.name, u.email, bp.waist, bp.hip, bp.preferred_fit
FROM `USER` u
JOIN BODY_PROFILE bp ON u.user_id = bp.user_id
WHERE u.user_id = @demo_user_id;

-- 1.7 DELETE: Safe cleanup of demo test records
DELETE FROM FIT_REVIEW WHERE review_id = @demo_review_id;
DELETE FROM PURCHASE WHERE purchase_id = @demo_purchase_id;
DELETE FROM BODY_PROFILE WHERE user_id = @demo_user_id;
DELETE FROM `USER` WHERE user_id = @demo_user_id;


-- ============================================================
-- PART 2: MULTI-TABLE JOINS (INNER & OUTER)
-- ============================================================

-- 2.1 4-TABLE INNER JOIN: Complete Garment Measurement Catalog
-- Resolves Brand -> Garment -> Garment Size -> Garment Measurement
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

-- 2.2 LEFT OUTER JOIN: Identifying Garment Sizes with Low or Zero Reviews
-- Essential for calculating catalog coverage and cold-start review thresholds
SELECT 
    b.brand_name,
    g.garment_name,
    s.size_label,
    COUNT(r.review_id) AS total_reviews,
    COALESCE(AVG(CASE WHEN r.overall_fit = 'TRUE_TO_SIZE' THEN 1.0 ELSE 0.0 END) * 100, 0) AS true_to_size_pct
FROM BRAND b
JOIN GARMENT g ON b.brand_id = g.brand_id
JOIN GARMENT_SIZE s ON g.garment_id = s.garment_id
LEFT JOIN FIT_REVIEW r ON s.garment_size_id = r.garment_size_id
GROUP BY b.brand_name, g.garment_name, s.garment_size_id, s.size_label
HAVING total_reviews <= 2
ORDER BY total_reviews ASC, b.brand_name;


-- ============================================================
-- PART 3: AGGREGATE QUERIES WITH GROUP BY & HAVING
-- ============================================================

-- 3.1 Return Rate Analysis by Brand (Quality & Sizing Consistency Metric)
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


-- ============================================================
-- PART 4: NESTED & CORRELATED SUBQUERIES
-- ============================================================

-- 4.1 NESTED SUBQUERY WITH IN:
-- Find garments that have received size complaints ('TOO_SMALL' or 'TOO_LARGE')
SELECT 
    g.garment_id,
    g.garment_name,
    g.garment_category,
    g.fit_type
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

-- 4.2 CORRELATED SUBQUERY:
-- Find users whose current body profile waist is significantly smaller than
-- the average waist dimension of garments they have historically 'KEPT'
SELECT 
    u.user_id,
    u.name,
    bp.waist AS user_waist,
    (
        SELECT ROUND(AVG(m.measurement_value), 2)
        FROM PURCHASE p
        JOIN GARMENT_SIZE s ON p.garment_size_id = s.garment_size_id
        JOIN GARMENT_MEASUREMENT m ON s.garment_size_id = m.garment_size_id
        WHERE p.user_id = u.user_id
          AND p.outcome = 'KEPT'
          AND m.measurement_type = 'waist'
    ) AS avg_kept_garment_waist
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


-- ============================================================
-- PART 5: COMMON TABLE EXPRESSIONS (CTE) & RECURSIVE QUERIES
-- ============================================================

-- 5.1 STANDARD CTE: Cross-Brand Tolerance Delta Matching
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
    -- Reference dimensions from authenticated user profile or past Levi's purchase
    SELECT 70.00 AS ref_waist, 96.00 AS ref_hip
)
SELECT 
    t.brand_name,
    t.garment_name,
    t.size_label,
    t.waist_cm,
    t.hip_cm,
    ROUND(ABS(t.waist_cm - r.ref_waist) + ABS(t.hip_cm - r.ref_hip), 2) AS total_delta_cm
FROM TargetBrandSpecs t
CROSS JOIN UserReference r
ORDER BY total_delta_cm ASC
LIMIT 3;

-- 5.2 RECURSIVE CTE: Sizing Gradation Progression & Interpolation
-- Generates sizing step intervals (+2.5 cm waist steps) across size scales
-- Demonstrates Rubric Item 7: "Recursive Queries"
WITH RECURSIVE SizeProgression AS (
    -- Anchor Member: Starting base waist size (e.g., Size 24 = 61.0 cm)
    SELECT 
        1 AS step_index,
        24 AS nominal_size,
        61.00 AS waist_cm,
        'Base Size (XS)' AS classification
    
    UNION ALL
    
    -- Recursive Member: Increment by 1 size and 2.54 cm (1 inch) waist progression
    SELECT 
        step_index + 1,
        nominal_size + 2,
        ROUND(waist_cm + 2.54, 2),
        CASE 
            WHEN step_index + 1 <= 2 THEN 'Small (S)'
            WHEN step_index + 1 <= 4 THEN 'Medium (M)'
            WHEN step_index + 1 <= 6 THEN 'Large (L)'
            ELSE 'Plus (XL+)'
        END
    FROM SizeProgression
    WHERE step_index < 7 -- Terminate at 7 size gradations (up to Size 36)
)
SELECT 
    step_index,
    nominal_size,
    waist_cm,
    ROUND(waist_cm / 2.54, 1) AS waist_inches,
    classification
FROM SizeProgression;
