-- ============================================================
-- FITCHECK — DATABASE-LEVEL ROLE-BASED ACCESS CONTROL (RBAC)
-- Demonstrates Rubric Item 12: "Role-based access control in database"
-- MySQL 8.0+
-- ============================================================

-- 1. Create MySQL Roles
CREATE ROLE IF NOT EXISTS 'fitcheck_app_role', 'fitcheck_admin_role';

-- 2. Grant Permissions to Application Role (Least-Privilege Principle)
-- The application connection only requires DML operations and procedure execution.
-- It is strictly denied DDL privileges (CREATE, DROP, ALTER) to protect schema integrity.
GRANT SELECT, INSERT, UPDATE, DELETE ON fitcheck.* TO 'fitcheck_app_role';

-- 3. Grant Permissions to Admin Role
GRANT ALL PRIVILEGES ON fitcheck.* TO 'fitcheck_admin_role';

-- 4. Create Database Users (Placeholders for local deployment)
-- Note: Replace passwords with environment-provided secrets in production
CREATE USER IF NOT EXISTS 'fitcheck_user'@'localhost' IDENTIFIED BY 'REPLACE_WITH_SECURE_APP_PASSWORD';
CREATE USER IF NOT EXISTS 'fitcheck_admin'@'localhost' IDENTIFIED BY 'REPLACE_WITH_SECURE_ADMIN_PASSWORD';

-- 5. Assign Roles to Users
GRANT 'fitcheck_app_role' TO 'fitcheck_user'@'localhost';
GRANT 'fitcheck_admin_role' TO 'fitcheck_admin'@'localhost';

-- 6. Set Default Active Roles
SET DEFAULT ROLE 'fitcheck_app_role' TO 'fitcheck_user'@'localhost';
SET DEFAULT ROLE 'fitcheck_admin_role' TO 'fitcheck_admin'@'localhost';


-- Verification Query:
-- SHOW GRANTS FOR 'fitcheck_user'@'localhost' USING 'fitcheck_app_role';


-- ============================================================
-- 7. REPRODUCIBLE LEAST-PRIVILEGE DEMONSTRATION & VERIFICATION
-- ============================================================
-- Step A: Verify Assigned Grants
-- SHOW GRANTS FOR 'fitcheck_user'@'localhost' USING 'fitcheck_app_role';
-- SHOW GRANTS FOR 'fitcheck_admin'@'localhost' USING 'fitcheck_admin_role';

-- Step B: Test Permitted Operations for 'fitcheck_user' (Expected: SUCCESS)
-- SELECT COUNT(*) FROM fitcheck.FIT_REVIEW;
-- INSERT INTO fitcheck.FIT_REVIEW (user_id, garment_size_id, overall_fit, review_text)
-- VALUES (2, 3, 'TRUE_TO_SIZE', 'RBAC test review text');

-- Step C: Test Denied Operation for 'fitcheck_user' (Expected: ERROR 1142 (42000): DROP command denied)
-- DROP TABLE fitcheck.FIT_REVIEW;
-- ALTER TABLE fitcheck.GARMENT ADD COLUMN test_col VARCHAR(10);

-- Step D: Test Permitted DDL for 'fitcheck_admin' (Expected: SUCCESS)
-- CREATE TABLE fitcheck.audit_archive_temp (id INT);
-- DROP TABLE fitcheck.audit_archive_temp;
