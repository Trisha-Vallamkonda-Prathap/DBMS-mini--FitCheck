-- ============================================================
-- FITCHECK — ADVANCED DATABASE CONCEPTS TEMPLATE
-- Covers: Stored Procedures, Functions, Triggers, Views, Transactions
-- Derived from DBMS Level 3 Evaluation Rubric (Item 8: 6 Marks)
-- ============================================================

USE fitcheck;

-- ------------------------------------------------------------
-- 1. DATABASE VIEW: vw_garment_catalog_summary
-- Provides an aggregated catalog view joining Brand, Garment,
-- and available Size ranges for front-end catalog browsing.
-- ------------------------------------------------------------
DROP VIEW IF EXISTS vw_garment_catalog_summary;

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

-- ------------------------------------------------------------
-- 2. STORED FUNCTION: fn_convert_to_cm
-- Converts inches to centimeters; returns cm directly if already in cm.
-- Formula: 1 inch = 2.54 cm
-- ------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_convert_to_cm;

DELIMITER //
CREATE FUNCTION fn_convert_to_cm(val DECIMAL(6,2), unit VARCHAR(5))
RETURNS DECIMAL(6,2)
DETERMINISTIC
BEGIN
    IF LOWER(unit) = 'in' THEN
        RETURN ROUND(val * 2.54, 2);
    ELSE
        RETURN val;
    END IF;
END //
DELIMITER ;

-- ------------------------------------------------------------
-- 3. STORED PROCEDURE: sp_recommend_size_for_waist
-- Input: Target Garment ID, User Waist in cm, User Preferred Fit
-- Output: Size Label with minimal waist discrepancy and fit clearance
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_recommend_size_for_waist;

DELIMITER //
CREATE PROCEDURE sp_recommend_size_for_waist(
    IN p_garment_id INT,
    IN p_user_waist DECIMAL(5,2),
    IN p_preferred_fit VARCHAR(20)
)
BEGIN
    DECLARE v_ease DECIMAL(4,2) DEFAULT 0.00;

    -- Adjust recommended dimensional ease based on fit preference
    IF p_preferred_fit = 'TIGHT' THEN
        SET v_ease = 0.00;
    ELSEIF p_preferred_fit = 'RELAXED' THEN
        SET v_ease = 3.00;
    ELSE
        SET v_ease = 1.50; -- Regular ease
    END IF;

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
END //
DELIMITER ;

-- ------------------------------------------------------------
-- 4. TRIGGER: trg_before_body_profile_update
-- Ensures measurement integrity before updates on BODY_PROFILE.
-- Validates that provided dimensions are strictly positive values.
-- ------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_before_body_profile_update;

DELIMITER //
CREATE TRIGGER trg_before_body_profile_update
BEFORE UPDATE ON BODY_PROFILE
FOR EACH ROW
BEGIN
    IF (NEW.waist IS NOT NULL AND NEW.waist <= 0) OR
       (NEW.hip IS NOT NULL AND NEW.hip <= 0) OR
       (NEW.height IS NOT NULL AND NEW.height <= 0) OR
       (NEW.thigh IS NOT NULL AND NEW.thigh <= 0) OR
       (NEW.inseam IS NOT NULL AND NEW.inseam <= 0) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Integrity Error: Body profile measurements must be strictly positive numbers.';
    END IF;
END //
DELIMITER ;

-- ------------------------------------------------------------
-- 5. ATOMIC TRANSACTION: Purchase Recording with Fit Verification
-- Demonstrates ACID transaction semantics for purchase logging
-- ------------------------------------------------------------
-- START TRANSACTION;
-- INSERT INTO PURCHASE (user_id, garment_size_id, outcome, fit_satisfaction, fit_preference)
-- VALUES (1, 5, 'KEPT', 'GOOD', 'REGULAR');
-- COMMIT;


-- ============================================================
-- 6. AUDIT TABLE & TRIGGERS (Member B Contribution)
-- Demonstrates Rubric Item 8: Meaningful Database Trigger
-- Tracks lifecycle changes (INSERT, UPDATE, DELETE) on FIT_REVIEW
-- for data lineage, review moderation, and vector index sync auditing.
-- ============================================================

CREATE TABLE IF NOT EXISTS REVIEW_AUDIT (
    audit_id INT NOT NULL AUTO_INCREMENT,
    review_id INT NOT NULL,
    action VARCHAR(10) NOT NULL,
    user_id INT NULL,
    changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    details TEXT NULL,

    CONSTRAINT pk_review_audit PRIMARY KEY (audit_id),
    INDEX idx_audit_review (review_id)
) ENGINE = InnoDB;

-- Trigger: After Review Insert
DROP TRIGGER IF EXISTS trg_after_review_insert;

DELIMITER //
CREATE TRIGGER trg_after_review_insert
AFTER INSERT ON FIT_REVIEW
FOR EACH ROW
BEGIN
    INSERT INTO REVIEW_AUDIT (review_id, action, user_id, details)
    VALUES (
        NEW.review_id,
        'INSERT',
        NEW.user_id,
        CONCAT('Created review for size ', NEW.garment_size_id, '; overall_fit: ', NEW.overall_fit)
    );
END //
DELIMITER ;

-- Trigger: After Review Update
DROP TRIGGER IF EXISTS trg_after_review_update;

DELIMITER //
CREATE TRIGGER trg_after_review_update
AFTER UPDATE ON FIT_REVIEW
FOR EACH ROW
BEGIN
    INSERT INTO REVIEW_AUDIT (review_id, action, user_id, details)
    VALUES (
        NEW.review_id,
        'UPDATE',
        NEW.user_id,
        CONCAT('Updated review; overall_fit changed from ', OLD.overall_fit, ' to ', NEW.overall_fit)
    );
END //
DELIMITER ;

-- Trigger: After Review Delete
DROP TRIGGER IF EXISTS trg_after_review_delete;

DELIMITER //
CREATE TRIGGER trg_after_review_delete
AFTER DELETE ON FIT_REVIEW
FOR EACH ROW
BEGIN
    INSERT INTO REVIEW_AUDIT (review_id, action, user_id, details)
    VALUES (
        OLD.review_id,
        'DELETE',
        OLD.user_id,
        CONCAT('Deleted review by user ', OLD.user_id, ' for size ', OLD.garment_size_id)
    );
END //
DELIMITER ;

-- ============================================================
-- REVIEW AUDIT TABLE + DELETE AUDIT TRIGGER
-- Records review deletions for administrative audit evidence.
-- ============================================================

CREATE TABLE IF NOT EXISTS REVIEW_AUDIT (
    audit_id INT AUTO_INCREMENT PRIMARY KEY,
    review_id INT NOT NULL,
    action VARCHAR(20) NOT NULL,
    user_id INT NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details TEXT
);
