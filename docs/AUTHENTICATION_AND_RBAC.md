# FitCheck — Authentication & Database Role-Based Access Control (RBAC) Documentation

This document fulfills **DBMS Level 3 Evaluation Rubric Item 12: Authentication Implementation & Role-Based Access Control in Database (4 Marks)**.

- **Application Authentication Endpoints:** [`backend/app/api/v1/endpoints/auth.py`](file:///C:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/backend/app/api/v1/endpoints/auth.py)
- **Database RBAC Script:** [`database/queries/rbac_setup.sql`](file:///C:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/database/queries/rbac_setup.sql)

---

## 1. Dual-Tier Security Architecture

FitCheck enforces defense-in-depth through two distinct, decoupled security boundaries:
1. **Tier 1 (Application Level):** JWT bearer authentication with bcrypt password hashing and role enforcement (`USER` vs `ADMIN`).
2. **Tier 2 (Database Engine Level):** MySQL 8.0+ native Role-Based Access Control (RBAC) enforcing the principle of least privilege.

```
+-----------------------------------------------------------------------------------------+
|                                    APPLICATION TIER                                     |
|  [Next.js Frontend]  ===(JWT Bearer Token)===>  [FastAPI Backend Auth Middleware]        |
|                                                    • Validates token signature & expiry |
|                                                    • Resolves current authenticated user|
|                                                    • Enforces role: USER vs ADMIN       |
+-----------------------------------------------------------------------------------------+
                                           |
                               (SQL Connection Pool)
                                           v
+-----------------------------------------------------------------------------------------+
|                                    DATABASE TIER (MySQL)                                |
|  [User: fitcheck_user]  <====== Assigned Role ======  [Role: fitcheck_app_role]         |
|                                                        • Permits: SELECT, INSERT,       |
|                                                                   UPDATE, DELETE        |
|                                                        • Denies:  CREATE, ALTER, DROP   |
|                                                                                         |
|  [User: fitcheck_admin] <====== Assigned Role ======  [Role: fitcheck_admin_role]       |
|                                                        • Permits: ALL PRIVILEGES        |
+-----------------------------------------------------------------------------------------+
```

---

## 2. Application-Level Authentication (FastAPI + Next.js)

### 2.1 Password Hashing & JWT Security
- Passwords are salted and hashed using `bcrypt` (12 rounds) via `passlib[bcrypt]`. Plaintext passwords are never persisted.
- Sessions use cryptographic JSON Web Tokens (`HS256`) containing `sub` (user_id), `email`, `role`, and expiration (`exp`).
- Tokens are transmitted via `Authorization: Bearer <token>` headers.

### 2.2 Role Definitions (Minimum 2 Roles)
Enforced in database constraint `chk_user_role CHECK (role IN ('USER', 'ADMIN'))` and FastAPI dependencies:
- **`USER` Role:** Standard retail consumer. Authorized to create/read/update their own private body profile, record purchases, view recommendations, submit public reviews, and perform semantic vector search. Denied administrative endpoints.
- **`ADMIN` Role:** System administrator. Authorized to inspect catalog metadata, audit lineages, and execute administrative functions.

### 2.3 Strict Authenticated User Privacy Guarantee
All recommendation endpoints derive the target identity strictly from `current_user = Depends(get_current_active_user)`. The application rejects any client-supplied request-body `user_id`, preventing user spoofing.

---

## 3. Database-Level Role-Based Access Control (MySQL RBAC)

Documented in [`database/queries/rbac_setup.sql`](file:///C:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/database/queries/rbac_setup.sql):

### 3.1 Role Creation & Least-Privilege Grants
```sql
-- 1. Create MySQL Roles
CREATE ROLE IF NOT EXISTS 'fitcheck_app_role', 'fitcheck_admin_role';

-- 2. Grant Least-Privilege DML to Application Role (No DDL allowed)
GRANT SELECT, INSERT, UPDATE, DELETE ON fitcheck.* TO 'fitcheck_app_role';

-- 3. Grant Full Administrative Privileges to Admin Role
GRANT ALL PRIVILEGES ON fitcheck.* TO 'fitcheck_admin_role';

-- 4. Create Database Accounts
CREATE USER IF NOT EXISTS 'fitcheck_user'@'localhost' IDENTIFIED BY '...';
CREATE USER IF NOT EXISTS 'fitcheck_admin'@'localhost' IDENTIFIED BY '...';

-- 5. Assign Roles to Accounts
GRANT 'fitcheck_app_role' TO 'fitcheck_user'@'localhost';
GRANT 'fitcheck_admin_role' TO 'fitcheck_admin'@'localhost';

-- 6. Set Default Active Roles
SET DEFAULT ROLE 'fitcheck_app_role' TO 'fitcheck_user'@'localhost';
SET DEFAULT ROLE 'fitcheck_admin_role' TO 'fitcheck_admin'@'localhost';
```

---

## 4. Reproducible RBAC Verification Demonstration

During project defense, execute these queries in MySQL command-line client to demonstrate least-privilege enforcement:

```sql
-- Step A: Verify Assigned Grants
SHOW GRANTS FOR 'fitcheck_user'@'localhost' USING 'fitcheck_app_role';
SHOW GRANTS FOR 'fitcheck_admin'@'localhost' USING 'fitcheck_admin_role';

-- Step B: Test Permitted Operations for 'fitcheck_user' (Expected: SUCCESS)
SELECT COUNT(*) FROM fitcheck.FIT_REVIEW;
INSERT INTO fitcheck.FIT_REVIEW (user_id, garment_size_id, overall_fit, review_text)
VALUES (2, 3, 'TRUE_TO_SIZE', 'RBAC test review text');

-- Step C: Test Denied Operation for 'fitcheck_user' (Expected: ERROR 1142 (42000): DROP command denied)
DROP TABLE fitcheck.FIT_REVIEW;
-- Output: ERROR 1142 (42000): DROP command denied to user 'fitcheck_user'@'localhost' for table 'FIT_REVIEW'

-- Step D: Test Permitted DDL for 'fitcheck_admin' (Expected: SUCCESS)
CREATE TABLE fitcheck.audit_archive_temp (id INT);
DROP TABLE fitcheck.audit_archive_temp;
```
