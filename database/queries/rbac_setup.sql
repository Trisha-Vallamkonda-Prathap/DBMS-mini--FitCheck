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
GRANT EXECUTE ON fitcheck.* TO 'fitcheck_app_role';

-- 3. Grant Permissions to Admin Role
GRANT ALL PRIVILEGES ON fitcheck.* TO 'fitcheck_admin_role';

-- 4. Create Database Users (Placeholders for local deployment)
-- Note: Replace passwords with environment-provided secrets in production
CREATE USER IF NOT EXISTS 'fitcheck_user'@'localhost' IDENTIFIED BY 'fitcheck_secure_app_pass';
CREATE USER IF NOT EXISTS 'fitcheck_admin'@'localhost' IDENTIFIED BY 'fitcheck_secure_admin_pass';

-- 5. Assign Roles to Users
GRANT 'fitcheck_app_role' TO 'fitcheck_user'@'localhost';
GRANT 'fitcheck_admin_role' TO 'fitcheck_admin'@'localhost';

-- 6. Set Default Active Roles
SET DEFAULT ROLE 'fitcheck_app_role' TO 'fitcheck_user'@'localhost';
SET DEFAULT ROLE 'fitcheck_admin_role' TO 'fitcheck_admin'@'localhost';

FLUSH PRIVILEGES;

-- Verification Query:
-- SHOW GRANTS FOR 'fitcheck_user'@'localhost' USING 'fitcheck_app_role';
