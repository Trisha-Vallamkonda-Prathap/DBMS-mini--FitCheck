# FitCheck — Database Seeding Strategy & Data Guidelines

## 1. Objective
Populate the 8 relational tables with realistic, non-fabricated, domain-accurate apparel data reflecting real-world sizing variances across major brands (e.g., Levi's, Zara, H&M, Madewell, Mango).

## 2. Realistic Sizing Ground Truth
To ensure meaningful recommendations during evaluation and viva defense:
- **Jeans & Trousers Focus:** Bottom-wear garments have the highest return rates in e-commerce due to waist, hip, and thigh mismatches.
- **Physical Measurements (cm):**
  - **Levi's (Waist-Based):** Size 26 (Waist ~66cm, Hip ~91cm), Size 28 (Waist ~71cm, Hip ~96cm), Size 30 (Waist ~76cm, Hip ~101cm).
  - **Zara (Numeric / EU):** Size 36 / US 4 (Waist ~66cm, Hip ~94cm), Size 38 / US 6 (Waist ~70cm, Hip ~98cm).
  - **H&M (Alpha / Numeric):** Size S / 4-6 (Waist ~68cm, Hip ~92cm), Size M / 8-10 (Waist ~74cm, Hip ~98cm).

## 3. Seed Execution Order (Referential Order)
Due to foreign key dependencies, data must be inserted in this exact sequence:
1. `USER` (Default demo accounts: `admin@fitcheck.local`, `shopper1@fitcheck.local`)
2. `BODY_PROFILE` (Linked to shoppers)
3. `BRAND` (Levi's, Zara, H&M, Madewell)
4. `GARMENT` (Ribcage Straight Jeans, Z1975 Wide Leg, Wide High Jeans)
5. `GARMENT_SIZE` (26, 27, 28, 29, 30, S, M, L, 36, 38, 40)
6. `GARMENT_MEASUREMENT` (Waist, Hip, Inseam, Rise, Thigh in cm)
7. `PURCHASE` (Historic kept/returned purchases)
8. `FIT_REVIEW` (Qualitative reviews with rich vocabulary for vector search)
