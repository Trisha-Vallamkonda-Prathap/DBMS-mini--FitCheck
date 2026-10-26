# FitCheck — Official Final Project Demonstration & Viva Defense Guide

This guide provides the complete, ordered demonstration script for the **DBMS Experiential Learning – Level 3 Project Evaluation (50 Marks Total)**.

---

## 0. Quick Environment Pre-Flight Check

Before starting the viva presentation, confirm that MySQL, Redis, FastAPI backend, and Next.js frontend are running:

```powershell
# In PowerShell (Repository Root: C:\Users\Trisha V P\DBMS-mini--FitCheck)

# 1. Check live backend health (MySQL + Redis connectivity)
python -c "import requests; print(requests.get('http://127.0.0.1:8000/api/v1/health').json())"
# Expected Output: {'status': 'healthy', 'mysql_connected': True, 'redis_connected': True, ...}

# 2. Run the Vector RUD verification
python vector-search/demo_vector_rud.py
# Expected Output: [SUCCESS] ALL 5 VECTOR RUD OPERATIONS VERIFIED SUCCESSFULLY AGAINST REDIS
```

---

## 1. Demonstration Phase 1: Conceptual Design & Relational Schema (5 Marks)
**Rubric Items 1 & 2**

### Deliverables to Present:
1. **Conceptual ER Diagram:** Open [`docs/diagrams/er_diagram.png`](file:///C:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/docs/diagrams/er_diagram.png) or [`docs/diagrams/er_diagram.pdf`](file:///C:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/docs/diagrams/er_diagram.pdf).
   - **Key Defense Points:**
     - 8 entities clearly classified into Strong entities (`USER`, `BRAND`, `GARMENT`), Dependent entities (`BODY_PROFILE`, `GARMENT_SIZE`, `GARMENT_MEASUREMENT`), and Associative entities (`PURCHASE`, `FIT_REVIEW`).
     - Explicit cardinalities (`1:0..1` for User-to-Profile, `1:N` for Brand-to-Garment, Garment-to-Size, Size-to-Measurement).
     - Strict cross-user privacy boundary: user profile and purchase tables represent private ground truth, while fit review text is synchronized to Redis for public consensus scoring.
2. **Relational Schema Diagram:** Open [`docs/diagrams/relational_schema.png`](file:///C:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/docs/diagrams/relational_schema.png).
   - **Key Defense Points:**
     - 3NF / BCNF normalization: Sizing conventions belong to `BRAND`; style names belong to `GARMENT`; size labels belong to `GARMENT_SIZE`; physical dimensions belong to `GARMENT_MEASUREMENT`.
     - Candidate keys: `UQ(garment_id, size_label)` and `UQ(garment_size_id, measurement_type)` prevent duplicate sizing specs at the database engine level.
     - Referential actions: `ON DELETE CASCADE` on dependent measurements; `ON DELETE RESTRICT` on business catalog entities and transaction history.

---

## 2. Demonstration Phase 2: DDL, Schema Constraints & RBAC (8 Marks)
**Rubric Items 3 & 12**

### Files to Present:
- DDL Script: [`database/fitcheck_ddl.sql`](file:///C:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/database/fitcheck_ddl.sql)
- RBAC Script: [`database/queries/rbac_setup.sql`](file:///C:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/database/queries/rbac_setup.sql)

### Live Commands to Execute in MySQL Client:
```sql
USE fitcheck;

-- 1. Inspect table structure and constraints
SHOW CREATE TABLE GARMENT_MEASUREMENT\G
SHOW CREATE TABLE FIT_REVIEW\G

-- 2. Verify Database-Level RBAC Roles
SHOW GRANTS FOR 'fitcheck_user'@'localhost' USING 'fitcheck_app_role';
SHOW GRANTS FOR 'fitcheck_admin'@'localhost' USING 'fitcheck_admin_role';

-- 3. Demonstrate Principle of Least Privilege:
-- fitcheck_user can perform DML:
SELECT COUNT(*) FROM FIT_REVIEW;

-- But fitcheck_user is strictly denied DDL (DROP command denied):
-- DROP TABLE FIT_REVIEW; -> ERROR 1142 (42000): DROP command denied
```

---

## 3. Demonstration Phase 3: DML, Joins, Aggregates & Advanced Queries (8 Marks)
**Rubric Items 6 & 7**

### File to Present:
- [`database/fitcheck_dml.sql`](file:///C:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/database/fitcheck_dml.sql)

### Queries to Execute Live in MySQL:

1. **4-Table Catalog Join:**
   ```sql
   SELECT b.brand_name, g.garment_name, s.size_label, m.measurement_type, m.measurement_value, m.unit
   FROM BRAND b
   JOIN GARMENT g ON b.brand_id = g.brand_id
   JOIN GARMENT_SIZE s ON g.garment_id = s.garment_id
   JOIN GARMENT_MEASUREMENT m ON s.garment_size_id = m.garment_size_id
   WHERE b.brand_name = 'Levi\'s' AND s.size_label = '28';
   ```

2. **Brand Return Rate Aggregate (GROUP BY & HAVING):**
   ```sql
   SELECT b.brand_name, COUNT(p.purchase_id) AS total_purchases,
          ROUND(SUM(CASE WHEN p.outcome = 'RETURNED' THEN 1 ELSE 0 END) * 100.0 / COUNT(p.purchase_id), 2) AS return_rate_pct
   FROM BRAND b
   JOIN GARMENT g ON b.brand_id = g.brand_id
   JOIN GARMENT_SIZE s ON g.garment_id = s.garment_id
   JOIN PURCHASE p ON s.garment_size_id = p.garment_size_id
   GROUP BY b.brand_id, b.brand_name
   HAVING total_purchases >= 3;
   ```

3. **Recursive Sizing Gradation CTE:**
   ```sql
   WITH RECURSIVE SizeProgression AS (
       SELECT 1 AS step_index, 24 AS nominal_size, 61.00 AS waist_cm, 'Base Size (XS)' AS classification
       UNION ALL
       SELECT step_index + 1, nominal_size + 2, ROUND(waist_cm + 2.54, 2),
           CASE WHEN step_index + 1 <= 2 THEN 'Small (S)'
                WHEN step_index + 1 <= 4 THEN 'Medium (M)'
                ELSE 'Large (L)' END
       FROM SizeProgression WHERE step_index < 5
   )
   SELECT * FROM SizeProgression;
   ```

---

## 4. Demonstration Phase 4: Advanced SQL Concepts (Stored Procedure, Function, Triggers) (6 Marks)
**Rubric Item 8**

### File to Present:
- [`database/queries/advanced_concepts.sql`](file:///C:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/database/queries/advanced_concepts.sql)

### Live Executable Demonstrations:

1. **Stored Function Execution (`fn_convert_to_cm`):**
   ```sql
   SELECT fn_convert_to_cm(28.50, 'in') AS inches_to_cm, fn_convert_to_cm(72.00, 'cm') AS cm_unchanged;
   -- Output: 72.39 | 72.00
   ```

2. **Stored Procedure Execution (`sp_recommend_size_for_waist`):**
   ```sql
   CALL sp_recommend_size_for_waist(1, 71.00, 'REGULAR');
   -- Recommends optimal size for Levi's 501 factoring in 1.50cm regular ease
   ```

3. **Safe Before-and-After Trigger Verification:**
   ```sql
   -- Insert temporary review (Triggers trg_after_review_insert)
   INSERT INTO FIT_REVIEW (user_id, garment_size_id, overall_fit, review_text)
   VALUES (1, 1, 'TRUE_TO_SIZE', 'Live trigger demo review');
   SET @rev_id = LAST_INSERT_ID();

   -- Inspect audit row automatically created in REVIEW_AUDIT
   SELECT * FROM REVIEW_AUDIT WHERE review_id = @rev_id;

   -- Clean up test review
   DELETE FROM FIT_REVIEW WHERE review_id = @rev_id;

   -- Final audit row verifies delete action was logged
   SELECT * FROM REVIEW_AUDIT WHERE review_id = @rev_id;
   ```

---

## 5. Demonstration Phase 5: NoSQL & Redis Vector Store RUD (11 Marks)
**Rubric Items 4 & 9**

### Live Command to Execute in Terminal:
```powershell
python vector-search/demo_vector_rud.py
```
**Demonstrates all 5 vector lifecycle operations live:**
1. **CREATE / UPSERT:** Inserts review 99999 with 384-dimensional dense float32 vector embedding into Redis hash `review_vector:99999`.
2. **READ (Direct):** Reads vector key and confirms `embedding_dim = 384`.
3. **READ (Semantic Search):** Queries natural-language complaint `"snug tight waist rigid denim"`, returning top matches with cosine similarity scores.
4. **UPDATE:** Modifies text, updates metadata, re-embeds vector in Redis.
5. **DELETE:** Deletes key and confirms key no longer exists.

---

## 6. Demonstration Phase 6: Next.js Frontend & Full User Workflow (5 Marks)
**Rubric Items 10 & 11**

Open browser at `http://localhost:3000`:
1. **Authentication Gate:** The application requires authentication before accessing user profile or recommendations. Sign in with demo account (`emily@example.com` / `password123`) or register a new user.
2. **Body Profile Tab:** Shows user's private body measurements (`waist`, `hip`, `thigh`, `inseam`). Updates trigger validation.
3. **Purchase History Tab:** Displays past purchases. Notice the cascaded `Brand -> Garment -> Size` dropdown selector mapping directly to normalized `garment_size_id`.
4. **Cross-Brand Recommendation Tab:**
   - Select target garment (e.g. *Zara Z1975 Wide Leg*).
   - Generates ranked size recommendation fusing:
     - 85% Authenticated user's personal calibration (`BODY_PROFILE` + kept `PURCHASE` records).
     - 15% Public crowd review consensus (`FIT_REVIEW` ratings from other customers).
   - Zero private data leakage: Never joins or infers other users' body measurements.
5. **Semantic Fit Review Search:** Enter fit complaints (e.g. `"runs small in waist"`) to search crowd feedback powered by live Redis embeddings.

---

## 7. Automated Test Verification Summary

To demonstrate automated test coverage to the evaluator:
```powershell
# 1. Run 8-case adversarial audit suite (Personalization, returns, cold-start, privacy boundary):
python -m pytest backend/tests/test_recommendation_audit_cases.py -v

# 2. Run full backend suite (55 tests across Member A and Member B components):
python -m pytest backend/tests -v
```
**Result:** **55 of 55 tests pass (100%)**
