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
| **Relational Database** | **MySQL 8.0 (InnoDB)** | Relational source of truth, 8 core normalized tables plus REVIEW_AUDIT, ACID transactions, CHECK constraints, FK cascades |
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
│   │   ├── models/                    # SQLAlchemy ORM models matching the 8 core tables and REVIEW_AUDIT
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
│   ├── ENTITY_EXPLANATION.md          # Comprehensive breakdown of all entities, weak entity proofs & cardinalities
│   ├── diagrams/
│   │   ├── conceptual_er_diagram.png  # Current black-and-white Chen ER diagram (no legend)
│   │   ├── conceptual_er_diagram.pdf  # Academic Chen Conceptual ER Diagram (Vector PDF)
│   │   ├── conceptual_er_diagram.svg  # Scalable Vector Graphics Chen ERD (Double Rect/Diamonds/Dashed Keys)
│   │   ├── relational_schema.jpeg     # Current relational schema, including REVIEW_AUDIT
│   │   ├── relational_schema_diagram.png # Print-ready Logical Relational Schema Diagram (PNG)
│   │   ├── relational_schema_diagram.pdf # Print-ready Logical Relational Schema Diagram (PDF)
│   │   ├── relational_schema_diagram.svg # Scalable Vector Graphics Logical Relational Schema
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

### Step 1: Python Environment and Configuration
From the repository root:
```powershell
python -m venv backend/.venv
. backend/.venv/Scripts/Activate.ps1
python -m pip install -r backend/requirements.txt
Copy-Item .env.example .env
```
Reuse an existing environment and `.env` if already configured. Set your local MySQL credentials and a random `SECRET_KEY` in `.env`. Keep real credentials out of Git. If a password contains URL-reserved characters, use a URL-encoded password in an explicit `DATABASE_URL`.

### Step 2: Initialize a Disposable MySQL Database and Load Seeds
The schema scripts drop and recreate tables. Use a fresh, disposable development database, never a database containing important records.

From the repository root, open an administrative MySQL client:
```powershell
mysql -u root -p
```
Then run inside MySQL, in this order:
```sql
SOURCE database/fitcheck_ddl.sql;
SOURCE database/seeds/seed_data.sql;
SOURCE database/seeds/review_seeds.sql;
SOURCE database/queries/advanced_concepts.sql;
```
The DDL creates nine tables, including `REVIEW_AUDIT`. The advanced SQL script installs the view, function, procedure, body-profile validation trigger and three review-audit triggers; it also executes disposable demonstrations. Apply it as an administrator, not as the runtime application user.

For database-level RBAC, open `database/queries/rbac_setup.sql`, replace its password placeholders locally with your chosen credentials, and execute its statements in the administrative client. Do not commit those credentials. Configure `.env` to use the restricted `fitcheck_user` account. The older `database/init_dev_mysql.sql` grants broad development privileges and must not be used as evidence of least-privilege RBAC.

On a clean database, the seed baseline is 10 users (including the admin), 8 body profiles, 5 brands, 14 garments, 70 sizes, 310 measurements, 30 purchases and 40 reviews. Audit demonstrations can add audit rows. Verify with:
```sql
USE fitcheck;
SHOW TABLES;
SHOW TRIGGERS;
SELECT COUNT(*) AS measurements FROM GARMENT_MEASUREMENT;
SELECT COUNT(*) AS reviews FROM FIT_REVIEW;
```
Run `SHOW TRIGGERS` as an administrator; the restricted runtime account may not be allowed to see trigger metadata.

The alternative Python seed runner is `python -m backend.app.scripts.seed_db`. It loads both seed files but does not install the advanced SQL objects or RBAC. Stable IDs are documented in [the ID manifest](database/seeds/ID_MANIFEST.md).

### Step 3: Redis Stack and Vector Ingestion
Install Docker and start Redis Stack with RediSearch enabled:
```powershell
docker run -d --name fitcheck-redis -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
```
If that container already exists, use `docker start fitcheck-redis` instead. If Redis Stack already runs locally, use that instance and configure `.env` accordingly. Ordinary Redis can use the application's scan fallback, but Redis Stack is required to demonstrate HNSW indexing.

With the Python environment activated and MySQL seeded:
```powershell
python -m backend.app.scripts.seed_vectors
docker exec fitcheck-redis redis-cli ping
docker exec fitcheck-redis redis-cli FT.INFO fit_review_idx
python vector-search/demo_vector_rud.py
```
Expect `PONG`, an HNSW index with 384-dimensional FLOAT32 vectors and COSINE distance, and 40 indexed review vectors for the clean seed baseline. The first embedding operation may download MiniLM and require internet access. Test records can increase the counts in an existing local database.

### Step 4: Backend Verification and API Server
```powershell
# From the repository root, with the backend environment activated:
python -m pytest backend/tests -q
# Latest verification: 59 passed (dependency deprecation warnings only).
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```
The automated suite uses SQLite and mocked Redis operations for much of its coverage. Also verify live MySQL, Redis Stack, audit triggers and the UI for the final demo.

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
- Includes demo login shortcuts for Priya #2, Ananya #3 and Admin #1 (synthetic demo accounts; password `password123`)
- Real-time cross-brand size ranking, fit verdicts, dimensional deltas, evidence citations, and body profile / purchase editors.

---

## 6. Rubric Tracking & Defense Notes

Current submission diagrams: [Chen ER diagram](docs/diagrams/conceptual_er_diagram.png) and [relational schema](docs/diagrams/relational_schema.jpeg). `er_diagram.png` is an identical copy of the current Chen ER diagram. Existing PDF/SVG and older relational PNG variants are preserved reference assets and have not been regenerated from these final images.

Real application screenshots and capture details are available in [docs/screenshots](docs/screenshots/README.md).

Every requirement from the official PES University evaluation rubric is tracked in [`docs/rubric_tracking.md`](docs/rubric_tracking.md).
Key viva talking points and technology justifications are detailed in [`docs/database_justification.md`](docs/database_justification.md).
Complex SQL examples (Joins, Aggregates with HAVING, Correlated Subqueries, CTEs) are provided in [`database/queries/advanced_queries.sql`](database/queries/advanced_queries.sql).
Advanced database concepts (Stored procedures, functions, triggers, views, transactions) are provided in [`database/queries/advanced_concepts.sql`](database/queries/advanced_concepts.sql).
