-- ============================================================
-- FitCheck — Local Development Database & RBAC User Setup
-- Run as MySQL root user:
--   & "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p < database\init_dev_mysql.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS fitcheck
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;

USE fitcheck;

-- 1. Create Roles
CREATE ROLE IF NOT EXISTS 'fitcheck_app_role', 'fitcheck_admin_role';

-- 2. Grant Privileges on fitcheck database
GRANT ALL PRIVILEGES ON fitcheck.* TO 'fitcheck_admin_role';
GRANT ALL PRIVILEGES ON fitcheck.* TO 'fitcheck_app_role';

-- 3. Create or Align Local Development User
CREATE USER IF NOT EXISTS 'fitcheck_user'@'localhost' IDENTIFIED BY 'fitcheck_password';
ALTER USER 'fitcheck_user'@'localhost' IDENTIFIED BY 'fitcheck_password';

-- 4. Assign and Activate Default Role
GRANT 'fitcheck_app_role' TO 'fitcheck_user'@'localhost';
GRANT 'fitcheck_admin_role' TO 'fitcheck_user'@'localhost';
SET DEFAULT ROLE 'fitcheck_app_role', 'fitcheck_admin_role' TO 'fitcheck_user'@'localhost';

FLUSH PRIVILEGES;
