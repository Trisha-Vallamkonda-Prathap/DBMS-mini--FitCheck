# FitCheck — DBMS Experiential Learning Level 3 Rubric Tracking

This checklist is directly derived from the official course rubric: **DBMS Experiential Learning – Level 3 Project Evaluation Criteria** (PES University, Department of Computer Science and Engineering, Aug–Dec 2026, 50 Marks Total).

### Status Legend
- `NOT STARTED` — Work has not yet begun.
- `IN PROGRESS` — Architecture/design drafted or partially implemented.
- `IMPLEMENTED` — Fully written in code and configuration, awaiting formal execution/verification.
- `VERIFIED` — Executed, tested with automated test suites or live evidence, and validated.

---

## Detailed Evaluation Checklist

| # | Evaluation Component (Rubric) | Max Marks | Status | Target / Implementation Files | Verification Evidence & Defense Notes |
|---|--------------------------------|-----------|--------|--------------------------------|---------------------------------------|
| 1 | **ER Diagram**<br>Comprehensive conceptual design with entities, attributes, cardinalities, keys | 2 | `VERIFIED` | `docs/diagrams/dbms_mini_v4.drawio`, `docs/schema_documentation.md` | Contains 8 core entities (`USER`, `BODY_PROFILE`, `BRAND`, `GARMENT`, `GARMENT_SIZE`, `GARMENT_MEASUREMENT`, `PURCHASE`, `FIT_REVIEW`) with complete cardinalities, primary/foreign keys. Verified matching canonical database DDL. |
| 2 | **Relational Schema**<br>Keys, relationships, normalization (3NF/BCNF), constraints | 3 | `VERIFIED` | `docs/schema_documentation.md`, `database/fitcheck_setup.sql` | Documented 1:1, 1:N relations, referential integrity rules (CASCADE vs RESTRICT), composite candidate keys (`uq_garment_size`, `uq_size_measurement`). Verified referential integrity in automated test suites. |
| 3 | **SQL Database Implementation — DDL with Constraints**<br>`CREATE`, `ALTER`, `DROP`, PK/FK, CHECK, UNIQUE, NOT NULL, Indexes | 4 | `VERIFIED` | `database/fitcheck_setup.sql`, `database/queries/advanced_concepts.sql` | Script contains complete table definitions with inline/out-of-line constraints, 8 foreign keys, numeric and enum CHECK constraints, composite UNIQUE keys, and explicit performance indexes. Safe execution instructions documented. |
| 4 | **NoSQL / Vector Database Creation**<br>Redis Stack vector index creation, embedding dimensions, distance metric | 4 | `IN PROGRESS` | `vector-search/schema.py`, `vector-search/README.md` | Redis Stack vector search index (`fit_review_idx`) defined with HNSW indexing, 384 dimensions (`all-MiniLM-L6-v2`), COSINE distance metric, and structured tag metadata for hybrid filtering. (Member B ownership). |
| 5 | **Technology Justification**<br>Justification for relational MySQL + Redis Stack vector store | 1 | `VERIFIED` | `docs/database_justification.md` | Explicit, defensible comparative justification: ACID relational constraints for structured sizing measurements and transactions vs in-memory vector index for unstructured semantic fit feedback. |
| 6 | **DML Operations**<br>`INSERT`, `UPDATE`, `DELETE`, `SELECT` with input sanitation and integrity | 4 | `VERIFIED` | `backend/app/api/v1/endpoints/`, `database/seeds/seed_data.sql`, `backend/app/scripts/seed_db.py` | Full CRUD operations across Member A entities: profile updates, purchase tracking, catalogue queries, and 310-measurement seed dataset with stable IDs. Tested via 21 pytest automated tests. |
| 7 | **Complex SQL Queries**<br>Nested, correlated, recursive queries, multi-table JOINs, aggregates, GROUP BY, HAVING, ORDER BY | 4 | `VERIFIED` | `database/queries/advanced_queries.sql`, `backend/app/services/recommendation_service.py` | Cross-brand measurement matching query (4-way JOIN), brand return rate aggregate (GROUP BY + HAVING), correlated user fit satisfaction subquery, nested subquery with IN, and tolerance matching CTE. |
| 8 | **Advanced SQL Concepts**<br>Stored procedures/functions, triggers, CTEs, transactions, views | 6 | `VERIFIED` | `database/queries/advanced_concepts.sql`, `backend/app/services/recommendation_service.py` | Stored procedure `sp_recommend_size_for_waist`, function `fn_convert_to_cm`, trigger `trg_before_body_profile_update`, catalog view `vw_garment_catalog_summary`, and atomic purchase transaction. |
| 9 | **NoSQL / Vector Feature (RUD)**<br>Vector semantic similarity search, retrieval, update, delete | 7 | `NOT STARTED` | `vector-search/`, `backend/app/services/vector_service.py` | Semantic search endpoint retrieving similar fit complaints (Member B ownership). |
| 10 | **Next.js Web Interface**<br>Interactive UI, responsive design, search, filter, forms, dashboards | 3 | `VERIFIED` | `frontend/src/app/page.tsx`, `frontend/src/app/globals.css` | Next.js 14 App Router, TypeScript, modern dark/light styling, persona switcher, recommendation dashboard, body profile editor, purchase tracker, and catalogue browser. Verified via `npm run build`. |
| 11 | **Backend/API & Database Integration**<br>FastAPI endpoints, async database sessions, error handling, env configs | 2 | `VERIFIED` | `backend/app/main.py`, `backend/app/api/v1/endpoints/`, `backend/app/services/` | FastAPI backend connected to MySQL via SQLAlchemy with connection pooling; zero hardcoded secrets; validated via Pydantic Settings and 21 automated pytest test suites. |
| 12 | **Authentication & Authorization**<br>Front-end auth, backend JWT auth, >=2 roles (USER, ADMIN), and database-level RBAC | 4 | `IMPLEMENTED` | `backend/app/core/security.py`, `backend/app/api/v1/endpoints/auth.py`, `database/queries/rbac_setup.sql` | Dual-level security: (1) Application-level JWT tokens with bcrypt hashing and role enforcement (`USER` vs `ADMIN`); (2) MySQL database-level RBAC with dedicated least-privilege users. |
| 13 | **Documentation & Git/GitHub**<br>Clean repository structure, commit hygiene, data dictionary, README setup instructions | 2 | `VERIFIED` | `README.md`, `docs/`, `database/seeds/ID_MANIFEST.md` | Comprehensive README, data dictionary, architecture diagrams, step-by-step setup guide for Windows/PowerShell, stable ID manifest for cross-team handoff. |
| 14 | **Originality, Individual Contribution, Viva Preparation**<br>Defensible architectural decisions, non-trivial problem, viva readiness | 4 | `VERIFIED` | `docs/architecture.md`, `docs/database_justification.md` | Solving the real-world "vanity sizing" dilemma in women's apparel through hybrid relational-vector intelligence. Detailed design defense rationales provided. |

---

## Mark Summary

| Category | Component Count | Total Weight | Current Status |
|----------|-----------------|--------------|----------------|
| Relational Database Design & DDL | Items 1, 2, 3 | 9 Marks | Complete & Verified (`VERIFIED`) |
| Vector Database & Tech Justification | Items 4, 5, 9 | 12 Marks | Architecture Defined & Justified (Member B boundary) |
| SQL DML, Advanced Queries & Concepts | Items 6, 7, 8 | 14 Marks | Member A Queries & Procedures Verified (`VERIFIED`) |
| Web Application & API Integration | Items 10, 11 | 5 Marks | Complete & Verified (`VERIFIED`) |
| Auth & Role-Based Access Control | Item 12 | 4 Marks | App & DB RBAC Designed & Implemented |
| Project Polish, Docs, Git & Viva Defense | Items 13, 14 | 6 Marks | Complete & Documented (`VERIFIED`) |
| **Total** | **14 Components** | **50 Marks** | **Member A End-to-End Complete** |
