# FitCheck — Member B Verification & Handoff

## Contribution

Member B owns and implemented:

- Authentication and authorization
- USER and ADMIN application roles
- MySQL database-level RBAC
- FIT_REVIEW CRUD APIs
- Review ownership enforcement
- Redis Stack vector indexing
- Natural-language semantic review search
- MySQL + Redis integration
- Shared authentication/review frontend
- Registration/login/logout/current-user UI
- Admin audit trail
- Review audit trigger
- Member B automated tests

---

## Authentication

Implemented endpoints:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

Authentication uses Bearer JWT tokens.

Public registration always creates a `USER`.
A client cannot self-register as `ADMIN`.

Passwords are stored only as bcrypt hashes and `password_hash` is never returned by the API.

Demo accounts:

### USER

- Email: `priya@example.com`
- Password: `password123`

### ADMIN

- Email: `admin@fitcheck.com`
- Password: `password123`

Logout removes the JWT from browser storage. Since the project uses stateless JWT authentication, logout does not revoke an already stolen token.

---

## Authorization

Two application roles are supported:

- `USER`
- `ADMIN`

Backend authorization is enforced independently of frontend visibility.

Verified behavior:

- Anonymous access to protected functionality is rejected.
- USER cannot access ADMIN-only audit functionality.
- USER cannot update or delete another user's review.
- ADMIN can access the protected audit endpoint.
- User-specific review queries use the authenticated user ID rather than a client-supplied user ID.

---

## Database-Level RBAC

MySQL roles:

- `fitcheck_app_role`
- `fitcheck_admin_role`

Runtime application role is limited to required DML operations:

- SELECT
- INSERT
- UPDATE
- DELETE

The runtime role was verified to be unable to create tables.

The admin database role was verified to have schema-level privileges.

RBAC setup script:

`database/queries/rbac_setup.sql`

---

## Review API

Implemented endpoints:

- `POST /api/v1/reviews`
- `GET /api/v1/reviews/mine`
- `GET /api/v1/garment-sizes/{id}/reviews`
- `PATCH /api/v1/reviews/{id}`
- `DELETE /api/v1/reviews/{id}`
- `POST /api/v1/reviews/search`
- `GET /api/v1/admin/audit-logs`

Review fields:

- `overall_fit`
- `waist_fit`
- `hip_fit`
- `thigh_fit`
- `length_fit`
- `review_text`

Allowed values:

### overall_fit

- `TOO_SMALL`
- `SLIGHTLY_SMALL`
- `TRUE_TO_SIZE`
- `SLIGHTLY_LARGE`
- `TOO_LARGE`

### waist_fit / hip_fit / thigh_fit

- `TIGHT`
- `GOOD`
- `LOOSE`

### length_fit

- `SHORT`
- `GOOD`
- `LONG`

---

## Redis Stack Vector Search

Redis Stack is used for semantic retrieval while MySQL remains the relational source of truth.

Embedding model:

`sentence-transformers/all-MiniLM-L6-v2`

Embedding dimension:

`384`

Redis index:

`fit_review_idx`

Distance metric:

Cosine similarity.

Verified ingestion:

- 40 FIT_REVIEW rows read from MySQL
- 40/40 vectors indexed successfully in Redis Stack

Workflow:

1. Review text is persisted in MySQL.
2. The text is embedded using MiniLM.
3. The vector and review metadata are stored in Redis Stack.
4. A natural-language query is embedded.
5. Redis performs KNN vector retrieval.
6. Returned review IDs are joined back to authoritative MySQL records.
7. Brand, garment and size information are derived through:

`FIT_REVIEW -> GARMENT_SIZE -> GARMENT -> BRAND`

No fabricated SQL keyword similarity score is used as a semantic-search fallback.

---

## Vector RUD Synchronization

Verified:

### Create

Creating a review:

- inserts the review in MySQL
- generates its embedding
- inserts the vector in Redis

### Update

Updating review text:

- updates MySQL
- regenerates the embedding
- refreshes the Redis vector

### Delete

Deleting a review:

- deletes the MySQL review
- deletes its Redis vector
- fires the MySQL audit trigger

---

## Advanced Database Feature — Review Audit Trigger

Audit table:

`REVIEW_AUDIT`

Trigger:

`trg_fit_review_delete_audit`

The trigger records deleted review information for administrative inspection.

Admin endpoint:

`GET /api/v1/admin/audit-logs`

The audit path was tested end-to-end:

`review deletion -> MySQL trigger -> REVIEW_AUDIT -> ADMIN API -> frontend`

---

## Frontend

Member B frontend:

`frontend/src/app/member-b-panel.tsx`

Integrated into:

`frontend/src/app/page.tsx`

Implemented UI functionality:

- Register
- Login
- Logout
- Current-user display
- USER/ADMIN role display
- Submit fit review
- My Reviews
- Edit review
- Delete review
- Semantic vector search
- Similarity-ranked results
- Admin-protected audit trail
- Loading, success and failure messages

---

## Synthetic Data

The project uses synthetic demo data only.

Review seed data contains varied examples of:

- waist tightness
- loose fit
- thigh discomfort
- length issues
- true-to-size experiences
- fit preferences

Stable IDs are documented in:

`database/seeds/ID_MANIFEST.md`

Seed data:

`database/seeds/seed_data.sql`

---

## Reproducible Local Setup

### MySQL

Create/load the FitCheck schema using the project SQL setup.

Then load seed data:

```powershell
python -m backend.app.scripts.seed_db