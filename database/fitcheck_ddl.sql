-- ============================================================
-- FITCHECK — STANDALONE DDL SCHEMA & DDL DEMONSTRATIONS
-- MySQL 8.0.16+ (InnoDB Storage Engine)
--
-- Covers DBMS Level 3 Evaluation Rubric Item 3:
-- "SQL database implementation - DDL with constraints (4 Marks)"
-- Includes: CREATE TABLE, ALTER TABLE, DROP TABLE, Constraints
-- (PK, FK, UNIQUE, CHECK, NOT NULL, DEFAULT), Performance Indexes,
-- and SHOW CREATE TABLE inspection commands.
-- ============================================================

CREATE DATABASE IF NOT EXISTS fitcheck
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;

USE fitcheck;

-- ============================================================
-- SECTION 1: CANONICAL SCHEMA CREATION (DDL)
-- ============================================================

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS REVIEW_AUDIT;
DROP TABLE IF EXISTS FIT_REVIEW;
DROP TABLE IF EXISTS PURCHASE;
DROP TABLE IF EXISTS GARMENT_MEASUREMENT;
DROP TABLE IF EXISTS GARMENT_SIZE;
DROP TABLE IF EXISTS GARMENT;
DROP TABLE IF EXISTS BRAND;
DROP TABLE IF EXISTS BODY_PROFILE;
DROP TABLE IF EXISTS `USER`;

SET FOREIGN_KEY_CHECKS = 1;

-- 1. USER: Strong Entity
CREATE TABLE `USER` (
    user_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(10) NOT NULL DEFAULT 'USER',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_user PRIMARY KEY (user_id),
    CONSTRAINT uq_user_email UNIQUE (email),
    CONSTRAINT chk_user_role
        CHECK (role IN ('USER', 'ADMIN'))
) ENGINE = InnoDB;

-- 2. BODY_PROFILE: Dependent Entity (1:0..1 with USER)
CREATE TABLE BODY_PROFILE (
    profile_id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    height DECIMAL(5,2) NULL,
    waist DECIMAL(5,2) NULL,
    hip DECIMAL(5,2) NULL,
    thigh DECIMAL(5,2) NULL,
    inseam DECIMAL(5,2) NULL,
    preferred_fit VARCHAR(20) NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_body_profile PRIMARY KEY (profile_id),
    CONSTRAINT uq_body_profile_user UNIQUE (user_id),

    CONSTRAINT fk_profile_user
        FOREIGN KEY (user_id)
        REFERENCES `USER` (user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT chk_profile_height CHECK (height IS NULL OR height > 0),
    CONSTRAINT chk_profile_waist CHECK (waist IS NULL OR waist > 0),
    CONSTRAINT chk_profile_hip CHECK (hip IS NULL OR hip > 0),
    CONSTRAINT chk_profile_thigh CHECK (thigh IS NULL OR thigh > 0),
    CONSTRAINT chk_profile_inseam CHECK (inseam IS NULL OR inseam > 0),
    CONSTRAINT chk_profile_fit
        CHECK (
            preferred_fit IS NULL
            OR preferred_fit IN ('TIGHT', 'REGULAR', 'RELAXED')
        )
) ENGINE = InnoDB;

-- 3. BRAND: Strong Entity
CREATE TABLE BRAND (
    brand_id INT NOT NULL AUTO_INCREMENT,
    brand_name VARCHAR(100) NOT NULL,
    sizing_system VARCHAR(20) NOT NULL,

    CONSTRAINT pk_brand PRIMARY KEY (brand_id),
    CONSTRAINT uq_brand_name UNIQUE (brand_name),
    CONSTRAINT chk_brand_sizing
        CHECK (sizing_system IN ('ALPHA', 'NUMERIC', 'WAIST_BASED'))
) ENGINE = InnoDB;

-- 4. GARMENT: Strong Entity
CREATE TABLE GARMENT (
    garment_id INT NOT NULL AUTO_INCREMENT,
    brand_id INT NOT NULL,
    garment_name VARCHAR(150) NOT NULL,
    garment_category VARCHAR(30) NOT NULL,
    fit_type VARCHAR(30) NOT NULL,
    description TEXT NULL,

    CONSTRAINT pk_garment PRIMARY KEY (garment_id),

    CONSTRAINT fk_garment_brand
        FOREIGN KEY (brand_id)
        REFERENCES BRAND (brand_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT chk_garment_category
        CHECK (garment_category IN ('Jeans', 'Trousers')),

    CONSTRAINT chk_garment_fit
        CHECK (
            fit_type IN (
                'STRAIGHT', 'SLIM', 'SKINNY', 'WIDE_LEG',
                'RELAXED', 'BOOTCUT', 'FLARED', 'OTHER'
            )
        ),

    INDEX idx_garment_brand (brand_id)
) ENGINE = InnoDB;

-- 5. GARMENT_SIZE: Dependent Entity
CREATE TABLE GARMENT_SIZE (
    garment_size_id INT NOT NULL AUTO_INCREMENT,
    garment_id INT NOT NULL,
    size_label VARCHAR(20) NOT NULL,

    CONSTRAINT pk_garment_size PRIMARY KEY (garment_size_id),
    CONSTRAINT uq_garment_size UNIQUE (garment_id, size_label),

    CONSTRAINT fk_size_garment
        FOREIGN KEY (garment_id)
        REFERENCES GARMENT (garment_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    INDEX idx_garment_size_garment (garment_id)
) ENGINE = InnoDB;

-- 6. GARMENT_MEASUREMENT: Dependent Entity
CREATE TABLE GARMENT_MEASUREMENT (
    measurement_id INT NOT NULL AUTO_INCREMENT,
    garment_size_id INT NOT NULL,
    measurement_type VARCHAR(20) NOT NULL,
    measurement_value DECIMAL(6,2) NOT NULL,
    unit VARCHAR(5) NOT NULL DEFAULT 'cm',

    CONSTRAINT pk_garment_measurement PRIMARY KEY (measurement_id),
    CONSTRAINT uq_size_measurement
        UNIQUE (garment_size_id, measurement_type),

    CONSTRAINT fk_measurement_size
        FOREIGN KEY (garment_size_id)
        REFERENCES GARMENT_SIZE (garment_size_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT chk_measurement_type
        CHECK (
            measurement_type IN ('waist', 'hip', 'thigh', 'inseam', 'rise')
        ),
    CONSTRAINT chk_measurement_value
        CHECK (measurement_value > 0),
    CONSTRAINT chk_measurement_unit
        CHECK (unit IN ('cm', 'in')),

    INDEX idx_measurement_size (garment_size_id)
) ENGINE = InnoDB;

-- 7. PURCHASE: Associative / Transactional Entity
CREATE TABLE PURCHASE (
    purchase_id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    garment_size_id INT NOT NULL,
    purchase_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    outcome VARCHAR(10) NOT NULL,
    fit_satisfaction VARCHAR(10) NULL,
    fit_preference VARCHAR(20) NULL,

    CONSTRAINT pk_purchase PRIMARY KEY (purchase_id),

    CONSTRAINT fk_purchase_user
        FOREIGN KEY (user_id)
        REFERENCES `USER` (user_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_purchase_size
        FOREIGN KEY (garment_size_id)
        REFERENCES GARMENT_SIZE (garment_size_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT chk_purchase_outcome
        CHECK (outcome IN ('KEPT', 'RETURNED', 'EXCHANGED')),

    CONSTRAINT chk_purchase_satisfaction
        CHECK (
            fit_satisfaction IS NULL
            OR fit_satisfaction IN ('GOOD', 'AVERAGE', 'POOR')
        ),

    CONSTRAINT chk_purchase_preference
        CHECK (
            fit_preference IS NULL
            OR fit_preference IN ('TIGHT', 'REGULAR', 'RELAXED')
        ),

    INDEX idx_purchase_user (user_id),
    INDEX idx_purchase_size (garment_size_id)
) ENGINE = InnoDB;

-- 8. FIT_REVIEW: Associative Entity with Text Feedback
CREATE TABLE FIT_REVIEW (
    review_id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    garment_size_id INT NOT NULL,
    overall_fit VARCHAR(20) NOT NULL,
    waist_fit VARCHAR(10) NULL,
    hip_fit VARCHAR(10) NULL,
    thigh_fit VARCHAR(10) NULL,
    length_fit VARCHAR(10) NULL,
    review_text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_fit_review PRIMARY KEY (review_id),

    CONSTRAINT fk_review_user
        FOREIGN KEY (user_id)
        REFERENCES `USER` (user_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_review_size
        FOREIGN KEY (garment_size_id)
        REFERENCES GARMENT_SIZE (garment_size_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT chk_review_overall_fit
        CHECK (
            overall_fit IN (
                'TOO_SMALL', 'SLIGHTLY_SMALL', 'TRUE_TO_SIZE',
                'SLIGHTLY_LARGE', 'TOO_LARGE'
            )
        ),

    CONSTRAINT chk_review_waist_fit
        CHECK (waist_fit IS NULL OR waist_fit IN ('TIGHT', 'GOOD', 'LOOSE')),
    CONSTRAINT chk_review_hip_fit
        CHECK (hip_fit IS NULL OR hip_fit IN ('TIGHT', 'GOOD', 'LOOSE')),
    CONSTRAINT chk_review_thigh_fit
        CHECK (thigh_fit IS NULL OR thigh_fit IN ('TIGHT', 'GOOD', 'LOOSE')),
    CONSTRAINT chk_review_length_fit
        CHECK (length_fit IS NULL OR length_fit IN ('SHORT', 'GOOD', 'LONG')),

    CONSTRAINT chk_review_text
        CHECK (CHAR_LENGTH(TRIM(review_text)) > 0),

    INDEX idx_review_user (user_id),
    INDEX idx_review_size (garment_size_id)
) ENGINE = InnoDB;

-- 9. REVIEW_AUDIT: Audit Lineage Table (Member B Contribution)
CREATE TABLE REVIEW_AUDIT (
    audit_id INT NOT NULL AUTO_INCREMENT,
    review_id INT NOT NULL,
    action VARCHAR(10) NOT NULL,
    user_id INT NULL,
    changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    details TEXT NULL,

    CONSTRAINT pk_review_audit PRIMARY KEY (audit_id),
    INDEX idx_audit_review (review_id)
) ENGINE = InnoDB;


-- ============================================================
-- SECTION 2: DDL DEMONSTRATIONS (ALTER, DROP, CONSTRAINTS)
-- Demonstrates required Rubric DDL capabilities on safe test tables
-- ============================================================

-- A. CREATE Demonstration Table
DROP TABLE IF EXISTS ddl_demo_table;
CREATE TABLE ddl_demo_table (
    demo_id INT NOT NULL AUTO_INCREMENT,
    demo_code VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    CONSTRAINT pk_demo PRIMARY KEY (demo_id)
) ENGINE = InnoDB;

-- B. ALTER TABLE: Add Column
ALTER TABLE ddl_demo_table
    ADD COLUMN notes VARCHAR(255) NULL AFTER status;

-- C. ALTER TABLE: Add CHECK Constraint
ALTER TABLE ddl_demo_table
    ADD CONSTRAINT chk_demo_status CHECK (status IN ('ACTIVE', 'INACTIVE', 'ARCHIVED'));

-- D. ALTER TABLE: Add Performance Index
ALTER TABLE ddl_demo_table
    ADD INDEX idx_demo_code (demo_code);

-- E. ALTER TABLE: Drop Column
ALTER TABLE ddl_demo_table
    DROP COLUMN notes;

-- F. DROP TABLE Demonstration
DROP TABLE ddl_demo_table;


-- ============================================================
-- SECTION 3: SHOW CREATE TABLE INSPECTION COMMANDS
-- Run to inspect exact generated DDL including constraints & keys
-- ============================================================
-- SHOW CREATE TABLE `USER`;
-- SHOW CREATE TABLE BODY_PROFILE;
-- SHOW CREATE TABLE BRAND;
-- SHOW CREATE TABLE GARMENT;
-- SHOW CREATE TABLE GARMENT_SIZE;
-- SHOW CREATE TABLE GARMENT_MEASUREMENT;
-- SHOW CREATE TABLE PURCHASE;
-- SHOW CREATE TABLE FIT_REVIEW;
-- SHOW CREATE TABLE REVIEW_AUDIT;
