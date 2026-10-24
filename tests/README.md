# FitCheck — Testing Strategy & Verification Plan

This test strategy supports Rubric Item 13 (Testing, Verification Evidence, and Demonstration).

---

## 1. Testing Pyramid

```
       /  End-to-End (E2E)  \       -> Full user journey (Next.js -> FastAPI -> MySQL + Redis)
      /   Integration Tests   \     -> API Endpoints, DB Queries, Redis Vector Search
     /      Unit Test Suites    \   -> Mathematical tolerance formulas, auth password hashing
```

---

## 2. Test Suites Overview

### A. Backend Unit & Health Tests (`backend/tests/`)
- `test_health.py`: Validates FastAPI application booting, route definitions, and graceful degradation when external services are uninitialized.
- Auth tests: Validate bcrypt hashing, JWT token expiration, and role rejection (`403 Forbidden` when `USER` accesses admin routes).

### B. Relational Database Verification (`database/queries/`)
- DDL Constraint Tests: Verify that negative measurements, invalid enums, and blank review strings are rejected by MySQL `CHECK` constraints.
- Foreign Key Action Tests: Verify that deleting a `GARMENT_SIZE` cascades to its measurements while preventing deletion of garments referenced in `PURCHASE`.
- Complex Query Verification: Run `database/queries/advanced_queries.sql` to validate execution plans (`EXPLAIN`) and index utilization (`idx_garment_brand`, `idx_measurement_size`).

### C. Vector Store Tests (`vector-search/`)
- Test HNSW index creation (`FT.CREATE`).
- Test vector embedding ingestion (`HSET`) with 384-dimensional FLOAT32 payloads.
- Test KNN similarity search with and without tag filters.
- Test RUD lifecycle (Read, Update, Delete) on Redis Hashes.
