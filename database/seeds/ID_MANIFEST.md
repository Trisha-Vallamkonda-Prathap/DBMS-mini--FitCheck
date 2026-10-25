# FitCheck — ID Manifest (Member A Structured Dataset)

This manifest documents all deterministic IDs used in `database/seeds/seed_data.sql`.
Member B should use these IDs when creating FIT_REVIEW records and vector embeddings.

## Users

| user_id | name            | email                    | role  |
|---------|-----------------|--------------------------|-------|
| 1       | Admin User      | admin@fitcheck.com     | ADMIN |
| 2       | Priya Sharma    | priya@example.com        | USER  |
| 3       | Ananya Rao      | ananya@example.com       | USER  |
| 4       | Meera Patel     | meera@example.com        | USER  |
| 5       | Kavya Iyer      | kavya@example.com        | USER  |
| 6       | Riya Nair       | riya@example.com         | USER  |
| 7       | Sneha Gupta     | sneha@example.com        | USER  |
| 8       | Divya Menon     | divya@example.com        | USER  |
| 9       | Tara Desai      | tara@example.com         | USER  |
| 10      | Lakshmi Reddy   | lakshmi@example.com      | USER  |

**Password:** All users share the dev password `password123` (bcrypt hash in seed SQL).

## Body Profiles

| profile_id | user_id | height | waist | hip    | thigh | inseam | preferred_fit |
|------------|---------|--------|-------|--------|-------|--------|---------------|
| 1          | 2       | 162.00 | 68.00 | 94.00  | 54.00 | 76.00  | REGULAR       |
| 2          | 3       | 158.00 | 64.00 | 90.00  | 51.00 | 74.00  | TIGHT         |
| 3          | 4       | 170.00 | 74.00 | 100.00 | 58.00 | 80.00  | RELAXED       |
| 4          | 5       | 165.00 | 70.00 | 96.00  | 55.00 | 78.00  | REGULAR       |
| 5          | 6       | 155.00 | 62.00 | 88.00  | 50.00 | 72.00  | TIGHT         |
| 6          | 7       | 168.00 | 72.00 | 98.00  | 56.00 | 79.00  | REGULAR       |
| 7          | 8       | 160.00 | 66.00 | 92.00  | 53.00 | 75.00  | RELAXED       |
| 8          | 9       | 163.00 | 69.00 | 95.00  | 54.50 | 77.00  | REGULAR       |

## Brands

| brand_id | brand_name | sizing_system |
|----------|------------|---------------|
| 1        | Levis      | WAIST_BASED   |
| 2        | Zara       | NUMERIC       |
| 3        | H&M        | ALPHA         |
| 4        | Mango      | NUMERIC       |
| 5        | Madewell   | WAIST_BASED   |

## Garments

| garment_id | brand_id | garment_name                    | category  | fit_type  |
|------------|----------|---------------------------------|-----------|-----------|
| 1          | 1        | Levis 501 Original              | Jeans     | STRAIGHT  |
| 2          | 1        | Levis Ribcage Straight Ankle    | Jeans     | STRAIGHT  |
| 3          | 1        | Levis 721 High Rise Skinny      | Jeans     | SKINNY    |
| 4          | 2        | Zara Z1975 Wide Leg             | Jeans     | WIDE_LEG  |
| 5          | 2        | Zara Slim Fit Trousers          | Trousers  | SLIM      |
| 6          | 2        | Zara TRF Straight Leg           | Jeans     | STRAIGHT  |
| 7          | 3        | H&M Wide High Jeans             | Jeans     | WIDE_LEG  |
| 8          | 3        | H&M Slim Fit Chinos             | Trousers  | SLIM      |
| 9          | 3        | H&M Skinny Regular Jeans        | Jeans     | SKINNY    |
| 10         | 4        | Mango Straight Jeans            | Jeans     | STRAIGHT  |
| 11         | 4        | Mango Flared Jeans              | Jeans     | FLARED    |
| 12         | 4        | Mango Relaxed Trousers          | Trousers  | RELAXED   |
| 13         | 5        | Madewell Perfect Vintage        | Jeans     | STRAIGHT  |
| 14         | 5        | Madewell Curvy High Rise        | Jeans     | SKINNY    |

## Garment Size ID Mapping

Each garment has 5 sizes. IDs are sequential, 5 per garment:
- Garment 1 (Levis 501): size IDs 1–5 (labels: 26, 27, 28, 29, 30)
- Garment 2 (Levis Ribcage): size IDs 6–10 (labels: 26, 27, 28, 29, 30)
- Garment 3 (Levis 721): size IDs 11–15 (labels: 26, 27, 28, 29, 30)
- Garment 4 (Zara Z1975): size IDs 16–20 (labels: 34, 36, 38, 40, 42)
- Garment 5 (Zara Slim): size IDs 21–25 (labels: 34, 36, 38, 40, 42)
- Garment 6 (Zara TRF): size IDs 26–30 (labels: 34, 36, 38, 40, 42)
- Garment 7 (H&M Wide High): size IDs 31–35 (labels: XS, S, M, L, XL)
- Garment 8 (H&M Slim Chinos): size IDs 36–40 (labels: XS, S, M, L, XL)
- Garment 9 (H&M Skinny): size IDs 41–45 (labels: XS, S, M, L, XL)
- Garment 10 (Mango Straight): size IDs 46–50 (labels: 34, 36, 38, 40, 42)
- Garment 11 (Mango Flared): size IDs 51–55 (labels: 34, 36, 38, 40, 42)
- Garment 12 (Mango Relaxed): size IDs 56–60 (labels: 34, 36, 38, 40, 42)
- Garment 13 (Madewell PV): size IDs 61–65 (labels: 26, 27, 28, 29, 30)
- Garment 14 (Madewell Curvy): size IDs 66–70 (labels: 26, 27, 28, 29, 30)

## Purchases (30 total)

| purchase_id | user_id | garment_size_id | outcome   | fit_satisfaction | fit_preference |
|-------------|---------|-----------------|-----------|------------------|----------------|
| 1–4         | 2       | 3,8,18,33       | KEPT/RET  | GOOD/AVG/POOR    | various        |
| 5–8         | 3       | 1,6,16,31       | KEPT/EXCH | GOOD/AVG         | TIGHT          |
| 9–12        | 4       | 5,10,20,35      | KEPT      | GOOD/AVG         | RELAXED/REG    |
| 13–16       | 5       | 3,13,48,63      | KEPT      | GOOD/AVG         | REGULAR/TIGHT  |
| 17–20       | 6       | 1,11,41,51      | KEPT/RET  | GOOD/POOR        | TIGHT          |
| 21–24       | 7       | 4,14,23,44      | KEPT      | GOOD/AVG         | REGULAR/TIGHT  |
| 25–27       | 8       | 2,7,47          | KEPT      | GOOD/AVG         | RELAXED/REG    |
| 28–30       | 9       | 3,53,68         | KEPT/RET  | GOOD/POOR        | REGULAR        |

### Key Demo Scenarios for Recommendation Testing

1. **User 2 (Priya)**: Has GOOD/KEPT Levis 501 sz28 (garment_size_id=3) and Ribcage sz28 (id=8). Ask for recommendation in Zara Z1975, Mango Straight, or H&M Wide High.
2. **User 3 (Ananya)**: Petite, sz26 fits. Cross-brand recommendation to Mango/Madewell.
3. **User 5 (Kavya)**: Multi-brand evidence (Levis, Mango, Madewell). Good for comprehensive recommendation.
4. **User 10 (Lakshmi)**: No purchases, no profile — tests empty/insufficient evidence path.
