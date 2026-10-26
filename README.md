# FitCheck — Cross-Brand Women's Apparel Fit Intelligence System

> **Course:** DBMS Experiential Learning – Level 3 MiniProject  
> **Institution:** PES University, Department of Computer Science & Engineering (Aug–Dec 2026)  
> **Evaluation Rubric Weight:** 50 Marks

FitCheck is a database-driven cross-brand sizing intelligence system. It tackles the real-world dilemma of "vanity sizing" in women's apparel by recommending likely equivalent sizes in unfamiliar brands using structured physical garment measurements and successful purchase history in **MySQL 8.0**, augmented by semantic vector search in **Redis Stack** to retrieve nuanced fit experiences and localized garment issues.

---

## 1. Target Architecture & Technology Stack

| Layer | Technology | Primary Functionality |
|---|---|---|
| **Frontend** | **Next.js 14 + TypeScript** | Responsive web UI, measurement entry, recommendation dashboard, semantic review explorer |
| **Backend / API** | **Python FastAPI** | REST API, dimensional tolerance calculation, dual-layer authentication, vector coordination |
| **Relational Database** | **MySQL 8.0 (InnoDB)** | Relational source of truth, 8 normalized tables, ACID transactions, CHECK constraints, FK cascades |
| **Vector Database** | **Redis Stack (RediSearch)** | HNSW vector index, 384-dimensional dense review embeddings (`all-MiniLM-L6-v2`), KNN search |
| **Database Access** | **SQLAlchemy 2.0 + PyMySQL** | Connection pooling, typed ORM models, transaction management, raw SQL execution |
| **Security & RBAC** | **JWT + Bcrypt + MySQL Roles** | Dual-layer RBAC: FastAPI token role verification (`USER`, `ADMIN`) + database least-privilege grants |
| **Version Control** | **Git / GitHub** | Clean branch management, atomic commits, tracked individual contributions |

---

## 2. Repository Layout

```
DBMS-mini--FitCheck/
├── .env.example                       # Safe environment variables template
├── .gitignore                         # Python, Node, OS, secrets, and cache exclusions
├── README.md                          # Main project guide, setup & architecture
│
├── backend/                           # FastAPI Application Service
│   ├── requirements.txt               # Pinned Python dependencies
│   ├── app/
│   │   ├── main.py                    # Application factory, CORS, router mounting
│   │   ├── core/                      # Config, security (JWT/bcrypt), DB & Redis connectors
│   │   ├── models/                    # SQLAlchemy ORM models matching all 8 SQL tables
│   │   ├── schemas/                   # Pydantic request/response validation schemas
│   │   ├── api/                       # API router & dependencies (get_db, RBAC)
│   │   │   └── v1/endpoints/          # Auth and Health check endpoints
│   │   └── services/                  # Business logic (sizing engine, vector service)
│   └── tests/                         # Backend test suite (health, auth)
│
├── frontend/                          # Next.js TypeScript Web Application
│   ├── package.json                   # Dependencies & build scripts
│   ├── tsconfig.json                  # TypeScript compiler settings
│   ├── next.config.js                 # Next.js runtime configuration
│   └── src/app/                       # App Router pages, layout, and globals.css
│
├── database/                          # Relational Database Artifacts
│   ├── fitcheck_ddl.sql               # Standalone canonical DDL & DDL demonstrations (CREATE, ALTER, DROP)
│   ├── fitcheck_dml.sql               # Standalone DML operations, 4-way joins, aggregates, subqueries, recursive CTE
│   ├── fitcheck_setup.sql             # MySQL 8.0 DDL setup script (preserved canonical)
│   ├── queries/                       # Documented SQL queries & advanced database concepts
│   │   ├── advanced_queries.sql       # Multi-table JOINs, GROUP BY/HAVING, correlated subqueries, CTEs
│   │   ├── advanced_concepts.sql      # Stored procedures, functions, triggers, views, transactions
│   │   ├── vector_commands.redis      # Redis CLI commands for vector index and RUD operations
│   │   └── rbac_setup.sql             # MySQL database-level roles & least-privilege grants
│   └── seeds/                         # Seeding guide and scripts for realistic sizing data
│
├── vector-search/                     # Vector Database Specifications & Live Demo
│   ├── README.md                      # Architecture, embedding model (all-MiniLM-L6-v2), HNSW specs
│   ├── demo_vector_rud.py             # Live runnable Python script verifying Vector RUD operations
│   └── schema.py                      # Redis Stack HNSW vector index definition & query helper
│
├── docs/                              # Project Documentation & Viva Defense
│   ├── FINAL_RUBRIC_COMPLIANCE_MATRIX.md # Line-by-line audit across all 14 rubric items & 17 requirements
│   ├── FINAL_DEMONSTRATION_GUIDE.md   # Step-by-step viva presentation & execution instructions
│   ├── DDL_DOCUMENTATION.md           # DDL schema, constraints, referential actions, and SHOW CREATE TABLE
│   ├── DML_AND_QUERIES_DOCUMENTATION.md # DML operations, joins, aggregates, and recursive queries
│   ├── ADVANCED_SQL_CONCEPTS.md       # Stored procedures, functions, triggers, views, and transactions
│   ├── NOSQL_VECTOR_DOCUMENTATION.md  # Redis Stack vector schema, HNSW indexing, and RUD lifecycle
│   ├── AUTHENTICATION_AND_RBAC.md     # Dual-tier security: JWT auth + MySQL engine RBAC
│   ├── RECOMMENDATION_LOGIC_AUDIT.md  # Recommendation scoring equations, weights, and privacy boundaries
│   ├── architecture.md                # Detailed component architecture & workflows
│   ├── schema_documentation.md        # Comprehensive data dictionary, constraints & entity classifications
│   ├── database_justification.md      # Relational vs Vector polyglot justification for viva defense
│   ├── diagrams/
│   │   ├── er_diagram.png             # Print-ready high-resolution Conceptual ER Diagram (PNG)
│   │   ├── er_diagram.pdf             # Print-ready Conceptual ER Diagram (PDF)
│   │   ├── er_diagram.svg             # Scalable Vector Graphics ER Diagram
│   │   ├── relational_schema.png      # Print-ready Relational Schema Diagram (PNG)
│   │   ├── relational_schema.pdf      # Print-ready Relational Schema Diagram (PDF)
│   │   ├── relational_schema.svg      # Scalable Vector Graphics Relational Schema
│   │   └── dbms_mini_v4.drawio        # Canonical Draw.io ER diagram (preserved)
│   └── requirements/                  # Course requirements & evaluation rubric PDFs
│       ├── DBMS Level 3 Project Requirements.pdf
│       └── DBMS Level 3.pdf
│
└── tests/                             # Integration & verification strategy
    └── README.md                      # End-to-end testing guidelines
```

> **Note on Reference Files:** The four original reference files placed in the project root (`DBMS Level 3 Project Requirements.pdf`, `DBMS Level 3.pdf`, `dbms_mini_v4.drawio`, `fitcheck_setup.sql`) are strictly preserved in their original root location. Exact byte-for-byte canonical copies have also been placed in `database/`, `docs/diagrams/`, and `docs/requirements/` for structured version control.

---

## 3. Prerequisites & Environment Setup

### Prerequisites
- **Operating System:** Windows 10/11 (PowerShell), macOS, or Linux.
- **Python:** 3.10+ (Recommended: 3.11).
- **Node.js:** 18.x or 20.x LTS.
- **MySQL Server:** MySQL 8.0.16+ running locally on port 3306.
- **Redis Stack:** Redis Stack Server (with RediSearch module) running on port 6379 (can be run via Docker or native Windows binary).

---

## 4. Step-by-Step Setup Instructions (Windows PowerShell)

### Step 1: Environment Configuration
Copy the template configuration to create your local `.env`:
```powershell
Copy-Item .env.example .env
```
Open `.env` and fill in your local MySQL root/user password and Redis configuration.

---

### Step 2: Safe Database Initialization & Deterministic Seeding (MySQL)
> **IMPORTANT SAFETY NOTICE:** The setup script `database/fitcheck_setup.sql` contains `DROP TABLE IF EXISTS` statements. Do **not** run this against an existing production database with live data.

To initialize a fresh local database and load the Member A deterministic dataset:
```powershell
# Open MySQL Command Line Client as root or admin:
mysql -u root -p

# Within MySQL prompt, execute DDL schema setup:
source c:/Users/Trisha V P/DBMS-mini--FitCheck/database/fitcheck_setup.sql;

# Next, load deterministic Member A seed data (idempotent INSERT IGNORE):
source c:/Users/Trisha V P/DBMS-mini--FitCheck/database/seeds/seed_data.sql;
```
Or seed via the automated Python runner:
```powershell
python -m backend.app.scripts.seed_db
```
To verify table creation and row counts:
```sql
USE fitcheck;
SHOW TABLES;
SELECT 'USER' AS tbl, COUNT(*) FROM `USER` UNION ALL
SELECT 'BODY_PROFILE', COUNT(*) FROM BODY_PROFILE UNION ALL
SELECT 'BRAND', COUNT(*) FROM BRAND UNION ALL
SELECT 'GARMENT', COUNT(*) FROM GARMENT UNION ALL
SELECT 'GARMENT_SIZE', COUNT(*) FROM GARMENT_SIZE UNION ALL
SELECT 'GARMENT_MEASUREMENT', COUNT(*) FROM GARMENT_MEASUREMENT UNION ALL
SELECT 'PURCHASE', COUNT(*) FROM PURCHASE;
```
Expected output: 8 tables created; 10 users, 8 body profiles, 5 brands, 14 garments, 70 garment sizes, 310 garment measurements, 30 purchases.

---

### Step 3: Member A ID Manifest for Cross-Team Handoff
All stable, deterministic IDs used for users, brands, garments, sizes, measurements, and purchases are documented in [`database/seeds/ID_MANIFEST.md`](file:///c:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/database/seeds/ID_MANIFEST.md).
Member B uses these exact IDs to link `FIT_REVIEW` records and vector embeddings.

---

### Step 4: Backend Setup & Verification
```powershell
# Run the complete automated test suite (21 unit and integration tests):
cmd /c "set PYTHONPATH=. && pytest backend/tests"

# Start development API server:
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Base URL: `http://127.0.0.1:8000/api/v1`
- Interactive OpenAPI Docs: `http://127.0.0.1:8000/api/v1/docs`
- Health Check: `http://127.0.0.1:8000/api/v1/health`

#### Member A Endpoints Implemented:
- `GET  /api/v1/brands` — Catalogue brand listing and sizing systems.
- `GET  /api/v1/garments?brand_id=&category=` — Filtered garment catalogue.
- `GET  /api/v1/garments/{id}` — Garment details with sizes and measurements.
- `GET  /api/v1/garments/{id}/sizes` — Physical dimensional ladder for garment sizes.
- `GET  /api/v1/profile` — User body profile retrieval.
- `PUT  /api/v1/profile` — Upsert body profile with boundary and relational validation.
- `GET  /api/v1/purchases` — User purchase history with joined garment and brand metadata.
- `POST /api/v1/purchases` — Purchase outcome recording with FK validation.
- `POST /api/v1/recommendations` — Explainable cross-brand size recommendation engine.

---

### Step 5: Frontend Setup & Demo
```powershell
# Navigate to frontend:
cd frontend

# Install Node dependencies (if not already installed)
npm install

# Start Next.js development server
npm run dev

# Or build production bundle to verify types:
npm run build
```
- Open browser at `http://localhost:3000`
- Includes interactive Demo Persona selector (Priya #2, Ananya #3, Kavya #5, Lakshmi #10 [cold start])
- Real-time cross-brand size ranking, fit verdicts, dimensional deltas, evidence citations, and body profile / purchase editors.

---

## 6. Rubric Tracking & Defense Notes

Every requirement from the official PES University evaluation rubric is tracked in [`docs/rubric_tracking.md`](file:///c:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/docs/rubric_tracking.md).
Key viva talking points and technology justifications are detailed in [`docs/database_justification.md`](file:///c:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/docs/database_justification.md).
Complex SQL examples (Joins, Aggregates with HAVING, Correlated Subqueries, CTEs) are provided in [`database/queries/advanced_queries.sql`](file:///c:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/database/queries/advanced_queries.sql).
Advanced database concepts (Stored procedures, functions, triggers, views, transactions) are provided in [`database/queries/advanced_concepts.sql`](file:///c:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/database/queries/advanced_concepts.sql).
