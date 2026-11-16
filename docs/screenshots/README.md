# FitCheck application screenshots

Captured on 17 November 2026 from the actual local FitCheck application at `http://127.0.0.1:3000`, backed by the existing MySQL database and Redis Stack instance. These are browser screenshots, not generated mockups. All displayed accounts and records are synthetic demo data.

| Screenshot | Evidence |
|---|---|
| [01-login.png](01-login.png) | Login form and built-in demo account shortcuts. |
| [02-recommendation.png](02-recommendation.png) | Priya's cross-brand recommendation: Zara size 38, evidence citations and ranked size ladder. |
| [03-body-profile.png](03-body-profile.png) | Authenticated body-profile form populated from MySQL. |
| [04-semantic-search.png](04-semantic-search.png) | Actual query `waist gaps but thighs feel tight`, with five similarity-ranked Redis/MySQL results. |
| [05-admin-audit.png](05-admin-audit.png) | ADMIN-only audit view showing four existing audit records. |

The login, recommendation and profile images show the full page; the search and audit images capture their complete visible panels. Capture actions logged into the seeded USER/ADMIN accounts and read existing data; no profile, purchase or review records were created, edited or deleted.

The local database contains additional historical demo records and is not a pristine seed baseline. These screenshots demonstrate the displayed workflows; the audit screenshot shows stored records and does not prove that every current MySQL trigger has been installed. Use the advanced SQL script and live verification steps in the [setup guide](../../README.md#4-step-by-step-setup-instructions-windows-powershell) before evaluation.

## Verification

After the documentation and image changes:

- `python -m pytest backend/tests -q`: **59 passed, 36 dependency deprecation warnings**.
- `npm run build`: **passed**, including compilation and type checking.
- Live USER login, recommendation calculation and profile retrieval succeeded.
- Live semantic search returned HTTP 200 and five results.
- Live ADMIN audit retrieval returned HTTP 200 and four records.

Backend/frontend/business logic and SQL scripts were unchanged by this cleanup. Automated tests include SQLite and mocked Redis coverage, so they supplement rather than replace a live database demonstration.
