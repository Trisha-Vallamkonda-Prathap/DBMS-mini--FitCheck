# FitCheck — Recommendation Logic, Privacy Enforcement, and Defect Audit

**Date:** 2026-10-26  
**Status:** Complete Audit & Verification  
**Repository:** `DBMS-mini--FitCheck`  

---

## 1. Architecture & End-to-End Data Flow

The recommendation engine translates multi-brand catalogue specifications and authenticated customer evidence into calibrated, explainable size recommendations without compromising user privacy.

```
+-----------------------------------------------------------------------------------+
| Next.js Frontend (Page.tsx)                                                       |
|  - Authenticated Session Token (JWT in Authorization Header)                     |
|  - Target Garment Selection (garment_id)                                          |
|  - Optional Manual Measurement Overrides                                         |
+-----------------------------------------------------------------------------------+
                                    |
                                    v POST /api/v1/recommendations
+-----------------------------------------------------------------------------------+
| FastAPI Authorization Gateway (backend/app/api/v1/endpoints/recommendations.py)    |
|  - Resolves current_user strictly from verified JWT token                         |
|  - Rejects guest queries that attempt to pass client-supplied user_id (401)       |
|  - Enforces strict user isolation: current_user.user_id passed to service          |
+-----------------------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------------------+
| FitCheck Recommendation Engine (backend/app/services/recommendation_service.py)   |
|                                                                                   |
| 1. Personal Calibration (Current User Only):                                      |
|    - SELECT * FROM BODY_PROFILE WHERE user_id = :current_user_id                  |
|    - SELECT * FROM PURCHASE JOIN GARMENT_SIZE JOIN GARMENT                        |
|        WHERE user_id = :current_user_id AND outcome = 'KEPT'                      |
|        AND fit_satisfaction IN ('GOOD', 'AVERAGE')                                |
|    - Negative Experience Caveats:                                                 |
|        WHERE user_id = :current_user_id AND (outcome = 'RETURNED' OR POOR fit)     |
|                                                                                   |
| 2. Public Review Evidence (All Reviewers — Strictly Public Columns Only):         |
|    - SELECT * FROM FIT_REVIEW JOIN GARMENT_SIZE                                   |
|        WHERE GARMENT_SIZE.garment_id = :target_garment_id                          |
|    - Extracts: overall_fit, waist_fit, hip_fit, review_text                       |
|    - NEVER joins or accesses reviewers' BODY_PROFILE or private PURCHASE tables   |
|                                                                                   |
| 3. Target Garment Catalogue Ladder:                                               |
|    - BRAND -> GARMENT -> GARMENT_SIZE -> GARMENT_MEASUREMENT                      |
|    - Compares target size dimensions against synthesized reference dimensions     |
|                                                                                   |
| 4. Dimensional Delta & Exponential Decay Match Scoring:                           |
|    - effective_delta = sum(weight_i * |garment_dim - ref_dim|) / sum(weights)     |
|    - base_score = 100 * exp(-effective_delta / 4.0)                              |
|    - blended_score = 0.85 * base_score + 0.15 * community_score                   |
|                                                                                   |
| 5. Explainable Ladder Output:                                                     |
|    - Ranked sizes, dimensional deltas, verdict, notes, citations, caveats        |
+-----------------------------------------------------------------------------------+
```

---

## 2. Implemented Scoring Formula & Evidence Weights

### A. Personal Dimensional Synthesis
1. **Body Profile Dimensions with Anatomical Ease:**
   - Ease allowances based on `preferred_fit`:
     - `TIGHT`: Waist +0.0 cm, Hip +0.5 cm, Thigh +0.0 cm, Rise +0.0 cm
     - `REGULAR`: Waist +1.5 cm, Hip +2.5 cm, Thigh +1.5 cm, Rise +1.0 cm
     - `RELAXED`: Waist +3.0 cm, Hip +4.5 cm, Thigh +3.0 cm, Rise +2.0 cm
2. **Purchase History Ground Truth Weighting:**
   - Kept purchases with `fit_satisfaction == 'GOOD'`: Weight **1.0** (Strong empirical evidence)
   - Kept purchases with `fit_satisfaction == 'AVERAGE'`: Weight **0.5** (Secondary positive evidence)
   - Returned/Exchanged items (`outcome != 'KEPT'`): Weight **0.0** (Excluded from positive fit ground truth; triggers brand return warning caveat instead)
3. **Reference Blend:**
   - Both profile & kept purchases present: **60% past purchase ground truth + 40% body profile**
   - Kept purchases only: **100% past purchase ground truth**
   - Body profile only: **100% body profile + ease allowance**

### B. Dimensional Comparison Weights
Compatible dimensions are evaluated with normalized importance weights:
- **Waist:** 0.40
- **Hip:** 0.32
- **Thigh:** 0.12
- **Inseam:** 0.10
- **Rise:** 0.06

$$\text{effective\_delta} = \frac{\sum w_i \cdot |\text{garment\_value}_i - \text{ref\_value}_i|}{\sum w_i}$$

$$\text{base\_score} = 100 \cdot e^{-\frac{\text{effective\_delta}}{4.0}}$$

### C. Public Community Review Consensus Fusion
When verified customer reviews exist for a target garment size:
- `overall_fit` scoring weights:
  - `TRUE_TO_SIZE`: **100.0**
  - `SLIGHTLY_SMALL` / `SLIGHTLY_LARGE`: **75.0**
  - `TOO_SMALL` / `TOO_LARGE`: **40.0**
- Evidence Fusion:
  - If reviews exist for size: $$\text{final\_score} = 0.85 \cdot \text{base\_score} + 0.15 \cdot \text{community\_score}$$
  - If no reviews for that size: $$\text{final\_score} = \text{base\_score}$$ (no uncalibrated penalty)

---

## 3. Evidence Source Mapping & Privacy Enforcement

| Evidence Source | Consuming Module & Query | Privacy Status | Verification |
| :--- | :--- | :--- | :--- |
| **Current User Body Profile** | `recommendation_service.py` -> `db.query(BodyProfile).filter(BodyProfile.user_id == user_id)` | **Private (Isolated)** | **VERIFIED** |
| **Current User Purchases** | `recommendation_service.py` -> `db.query(Purchase).filter(Purchase.user_id == user_id, Purchase.outcome == 'KEPT')` | **Private (Isolated)** | **VERIFIED** |
| **Current User Negative Fits** | `recommendation_service.py` -> `db.query(Purchase).filter(Purchase.user_id == user_id, outcome == 'RETURNED')` | **Private (Isolated)** | **VERIFIED** |
| **Other Customers' Body Profiles** | None. Never queried or joined. | **Strictly Excluded** | **VERIFIED** (Case 4 test passed) |
| **Other Customers' Purchases** | None. Never queried or joined. | **Strictly Excluded** | **VERIFIED** (Case 4 test passed) |
| **Public Customer Reviews** | `recommendation_service.py` -> `db.query(FitReview).join(GarmentSize).filter(GarmentSize.garment_id == target_garment_id)` | **Public Data Only** | **VERIFIED** (Case 3 test passed) |
| **Catalogue Sizing & Measurements** | `recommendation_service.py` -> `GarmentSize.measurements` | **Public Catalogue** | **VERIFIED** (Case 7 test passed) |

---

## 4. Review Retrieval & Vector Search Behavior

1. **Redis Server Status:**
   - Redis server is natively running on port `6379`.
   - Verified via `ping_redis() == True` and `GET /api/v1/health` returning `{"status":"healthy","mysql_connected":true,"redis_connected":true}`.
2. **Review Vectors & Indexing:**
   - 41 review vectors ingested with 384-dimensional dense embeddings (`sentence-transformers/all-MiniLM-L6-v2`) under `review_vector:{id}` keys in Redis.
   - Vector Search Execution:
     - Primary: Attempts RediSearch `FT.SEARCH` index query.
     - Fallback: Gracefully scans `review_vector:*` hashes directly in Redis, deserializes float32 embeddings, and calculates cosine similarity via NumPy.
     - Live execution verified: querying `"tight waist"` against Redis returns top hits `[(20, 0.7076), (23, 0.6992), (17, 0.6631)]`.

---

## 5. Verified Defects & Fixes Applied

1. **Defect 1: Client-Supplied `user_id` Spoofing Risk**
   - *Issue:* An unauthenticated or malicious caller could pass `request.user_id` in the JSON body.
   - *Fix:* In `recommendations.py`, `request.user_id` is unconditionally overridden by `current_user.user_id` for authenticated callers, and set to `None` for guest callers.
   - *Status:* **VERIFIED FIXED**.
2. **Defect 2: Public Reviews Ignored in Size Recommendation**
   - *Issue:* Recommendations were based solely on dimensional math without considering public community fit sentiment.
   - *Fix:* Integrated `target_reviews` into `compute_size_recommendation`, applying a 15% consensus weighting and qualitative notes.
   - *Status:* **VERIFIED FIXED**.
3. **Defect 3: Cold-Start Brand Return Caveat Overwriting**
   - *Issue:* During cold start, setting `caveats = ["Uncalibrated: ..."]` erased previously generated return-history warnings.
   - *Fix:* Updated cold-start returns to append caveats (`caveats = caveats + [...]`), preserving return notices.
   - *Status:* **VERIFIED FIXED**.
4. **Defect 4: Purchase Form Dropdown Lacked Relational Hierarchy**
   - *Issue:* Purchase logger did not provide a cascaded `Brand -> Garment -> Size` selection.
   - *Fix:* Implemented 3-level cascaded dropdown in `frontend/src/app/page.tsx` with clear foreign key display (`PURCHASE.garment_size_id`).
   - *Status:* **VERIFIED FIXED**.
5. **Defect 5: Vector Search Failed when RediSearch FT Module Missing**
   - *Issue:* If the native Redis binary lacked `FT.CREATE`, semantic search failed instead of reading Redis vectors.
   - *Fix:* Added `_search_vectors_fallback` in `vector_service.py` to scan Redis hashes and compute cosine similarity.
   - *Status:* **VERIFIED FIXED**.

---

## 6. Cold-Start and Low-Evidence Behavior

- **No Personal Profile or Purchases (Cold Start):**
  - If public reviews exist for the target garment: The engine ranks sizes by customer `TRUE_TO_SIZE` consensus and honestly reports confidence as `"LOW"`.
  - If no reviews exist: The engine selects the median catalogue size with confidence `"INSUFFICIENT_DATA"` and transparent caveats.
- **Sparse Personal Measurements:**
  - If only waist is provided, only waist weights are activated, normalizing composite delta by active weights (`applied_weight_sum`).

---

## 7. Test Evidence (Section 6 Audit Cases)

Automated test suite `backend/tests/test_recommendation_audit_cases.py`:
- `test_case_1_personalized_recommendation_consumed`: **PASSED**
- `test_case_2_returned_item_not_positive_fit`: **PASSED**
- `test_case_3_public_review_evidence_used_safely`: **PASSED**
- `test_case_4_strict_cross_user_privacy`: **PASSED**
- `test_case_5_cold_start_graceful`: **PASSED**
- `test_case_6_missing_review_service_graceful`: **PASSED**
- `test_case_7_correct_target_garment_sizes`: **PASSED**
- `test_case_8_purchase_id_mapping`: **PASSED**
Result: **8 of 8 passed (100%)**.
