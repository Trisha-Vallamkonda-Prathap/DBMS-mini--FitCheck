# FitCheck — Academic Entity-Relationship (ER) & Relational Schema Specification

## 1. Academic Model Overview & Notation System

The FitCheck database system is modeled conceptually using the formal **Chen Entity-Relationship (ER) Notation** taught in standard Computer Science DBMS curricula and mapped systematically to a **Third Normal Form (3NF) Relational Schema**.

### 1.1 Conceptual ER Notation (Chen Methodology)
Following standard academic DBMS conventions:
- **Strong Entities** are represented by **single solid rectangles** with autonomous primary key attributes.
- **Weak Entities** are represented by **double solid rectangles**, denoting existence and identification dependency on an owning strong entity.
- **Standard Relationships** are represented by **single diamonds** connecting participating entities.
- **Identifying Relationships** for weak entities are represented by **double diamonds**, linking the weak entity to its owner entity.
- **Attributes** are represented by **ovals** connected to their entity or relationship.
- **Primary Key Attributes** are indicated by a **solid underline** beneath the attribute name.
- **Partial Keys / Discriminators** of weak entities are indicated by a **dashed underline** beneath the discriminator attribute name.
- **Derived / Computed Attributes** are represented by **dashed ovals** (e.g., `return_rate` derived virtually from purchases).
- **Participation Constraints** are depicted using **double lines for Total Participation** (mandatory existence) and **single lines for Partial Participation** (optional existence).
- **Cardinalities** ($1:1$, $1:N$, $M:N$) are explicitly labeled on relationship lines.

---

## 2. Comprehensive Entity Breakdown

| Entity Name | Classification | Primary / Surrogate Key | Partial Key / Discriminator | Owning Entity | Identifying Relationship |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`USER`** | Strong Entity | `user_id` | — | None | None |
| **`BODY_PROFILE`** | Weak (Dependent) | `profile_id` (surrogate) | `user_id` | `USER` | `Has_Profile` (1:1, Double Diamond) |
| **`BRAND`** | Strong Entity | `brand_id` | — | None | None |
| **`GARMENT`** | Strong Entity | `garment_id` | — | None | None |
| **`GARMENT_SIZE`** | **Genuine Weak Entity** | `garment_size_id` (surrogate) | **`size_label`** | `GARMENT` | **`Offers_Size` (1:N, Double Diamond)** |
| **`GARMENT_MEASUREMENT`** | **Genuine Weak Entity** | `measurement_id` (surrogate) | **`measurement_type`** | `GARMENT_SIZE` | **`Has_Measurement` (1:N, Double Diamond)** |
| **`PURCHASE`** | Strong / Associative | `purchase_id` | — | None | None |
| **`FIT_REVIEW`** | Strong / Associative | `review_id` | — | None | None |

---

### Entity 1: `USER` (Strong Entity)
- **Purpose**: Represents registered system users (shoppers and administrators) who maintain body profiles, purchase garments, and submit fit reviews.
- **Classification**: Strong Entity. Possesses an autonomous unique identifier (`user_id`).
- **Attributes**:
  - `user_id` (PK, solid underline): Unique integer identifying each registered account.
  - `name`: Full legal or display name of the user.
  - `email`: Unique email address used for credential-based authentication.
  - `password_hash`: Secure salted password hash (Argon2 / PBKDF2 / bcrypt).
  - `role`: Role-Based Access Control tier (`user` or `admin`).
  - `created_at`: Account registration timestamp.
- **Relationships**:
  - `Has_Profile` (1:1 Identifying): Each user has at most one personal body measurement profile.
  - `Makes` (1:N): A user places zero or more garment purchase orders.
  - `Writes` (1:N): A user authors zero or more fit reviews.

---

### Entity 2: `BODY_PROFILE` (Weak / Dependent Entity)
- **Purpose**: Stores physical biometric body measurements (height, waist, hip, thigh, inseam) and sizing preferences for personalized size recommendation calibration.
- **Classification**: Weak / Dependent Entity.
- **Academic Justification**:
  - **Existence Dependency**: A body profile cannot exist without an owning user account.
  - **Identification Dependency**: A body profile is semantically identified by the `user_id` of the account to which it belongs.
  - **Relational Mapping**: In MySQL physical design, `body_profiles` contains a surrogate primary key `profile_id` alongside `user_id INT UNIQUE NOT NULL FOREIGN KEY REFERENCES users(user_id) ON DELETE CASCADE`.
- **Attributes**:
  - `profile_id` (PK, surrogate): Internal identifier.
  - `height`: User height in centimeters.
  - `waist`: Waist circumference in inches.
  - `hip`: Hip circumference in inches.
  - `thigh`: Thigh circumference in inches.
  - `inseam`: Leg inseam length in inches.
  - `preferred_fit`: Customer preference tag (`Tight`, `Regular`, `Loose`, `Oversized`).
- **Participation**: Total participation in `Has_Profile` identifying relationship (a profile cannot exist without a user).

---

### Entity 3: `BRAND` (Strong Entity)
- **Purpose**: Represents apparel manufacturers and fashion labels (e.g., Levi's, Nike, Zara) whose garments are catalogued and analyzed.
- **Classification**: Strong Entity. Identified autonomously by `brand_id`.
- **Attributes**:
  - `brand_id` (PK, solid underline): Unique brand identifier.
  - `brand_name`: Unique legal brand name (`UNIQUE`).
  - `sizing_system`: National/regional sizing convention (e.g., `US`, `UK`, `EU`, `Asian`).
  - `return_rate` (Derived Attribute, dashed oval): Computed dynamically from historical order returns for garments manufactured by this brand.
- **Relationships**:
  - `Produces` (1:N): A brand manufactures multiple distinct garment designs.

---

### Entity 4: `GARMENT` (Strong Entity)
- **Purpose**: Represents an abstract clothing style or model line produced by a brand (e.g., "501 Original Fit Jeans").
- **Classification**: Strong Entity. Identified autonomously by `garment_id`.
- **Attributes**:
  - `garment_id` (PK, solid underline): Unique style identifier.
  - `garment_name`: Descriptive garment style name.
  - `garment_category`: Apparel category (`Jeans`, `Shirt`, `Jacket`, `Dress`, etc.).
  - `fit_type`: Style cut classification (`Slim`, `Straight`, `Relaxed`, `Skinny`).
  - `description`: Detailed textile, fabric composition, and care notes.
- **Relationships**:
  - `Produces` (N:1): Manufactured by an owning `BRAND`.
  - `Offers_Size` (1:N Identifying): The owning strong entity for weak entity `GARMENT_SIZE`.

---

### Entity 5: `GARMENT_SIZE` (Genuine Academic Weak Entity)
- **Purpose**: Represents a specific manufactured physical size offering for a garment style (e.g., "32W 30L", "Medium", "Large").
- **Classification**: **Genuine Weak Entity**.
- **Formal Academic Proof**:
  1. **Existence Dependency**: A size variant cannot exist in isolation. The label `"32W 30L"` or `"Medium"` has zero ontological or commercial meaning without knowing which specific garment style it belongs to.
  2. **Identification Dependency**: A size has no autonomous natural primary key. Its natural identity is defined strictly in the context of its parent garment:
     $$\text{Candidate Key} = \{\text{garment\_id}, \text{size\_label}\}$$
  3. **Discriminator / Partial Key**: The attribute `size_label` (denoted with a **dashed underline** in the conceptual ERD) acts as the discriminator among all sizes offered for a particular garment.
  4. **Identifying Relationship**: The relationship `Offers_Size` is an **identifying relationship** (denoted with a **double diamond** and **total participation double line** on the weak entity side).
- **Attributes**:
  - `size_label` (Partial Key / Discriminator, **dashed underline**): Size designation string (e.g. `'30'`, `'32'`, `'M'`, `'L'`).
  - `garment_size_id` (Surrogate Implementation PK): Retained in the physical relational model to prevent compound foreign key propagation into child tables (`purchases`, `fit_reviews`, `garment_measurements`).
- **Relational Integrity Mapping**:
  - Table: `garment_sizes`
  - Composite Unique Constraint: `CONSTRAINT uq_garment_size UNIQUE (garment_id, size_label)`
  - Referential Action: `FOREIGN KEY (garment_id) REFERENCES garments(garment_id) ON DELETE CASCADE`
  - When an owning garment is deleted, all its associated weak size entities are automatically purged by the database engine.

---

### Entity 6: `GARMENT_MEASUREMENT` (Second-Order Weak Entity)
- **Purpose**: Records exact physical fabric dimensions (waist flat lay, front rise, inseam, hip width) for a specific manufactured garment size.
- **Classification**: **Second-Order Weak Entity**.
- **Formal Academic Proof**:
  1. **Existence Dependency**: A physical dimension measurement of $32.50\text{ inches}$ cannot exist without the specific size offering of the garment it measures.
  2. **Identification Dependency**: Identified jointly by the parent size (`garment_size_id`) and the anatomical dimension measured (`measurement_type`).
  3. **Partial Key / Discriminator**: `measurement_type` (denoted with a **dashed underline** in the conceptual ERD; e.g., `'waist'`, `'hip'`, `'thigh'`, `'inseam'`).
  4. **Identifying Relationship**: `Has_Measurement` (denoted with a **double diamond** and **total participation double line**).
- **Attributes**:
  - `measurement_type` (Partial Key / Discriminator, **dashed underline**): Name of measured dimension (`waist`, `hip`, `thigh`, etc.).
  - `measurement_value`: Numerical dimension magnitude (e.g. `32.50`).
  - `unit`: Measurement unit (`in` or `cm`).
  - `measurement_id` (Surrogate Implementation PK).
- **Relational Integrity Mapping**:
  - Table: `garment_measurements`
  - Composite Unique Constraint: `CONSTRAINT uq_garment_size_measure UNIQUE (garment_size_id, measurement_type)`
  - Referential Action: `FOREIGN KEY (garment_size_id) REFERENCES garment_sizes(garment_size_id) ON DELETE CASCADE`

---

### Entity 7: `PURCHASE` (Associative / Strong Entity)
- **Purpose**: Records historical transactions where a user acquired a specific garment size, including return outcomes and fit satisfaction ratings.
- **Classification**: Strong / Associative Entity. Maintains an independent surrogate key `purchase_id` with transaction timestamp.
- **Attributes**:
  - `purchase_id` (PK, solid underline): Unique order record identifier.
  - `purchase_date`: Timestamp when order was placed.
  - `outcome`: Categorical outcome (`kept` or `returned`).
  - `fit_satisfaction`: Numeric satisfaction score (1 to 5).
  - `fit_preference`: Sizing calibration recorded at checkout (`Tight`, `Regular`, `Loose`).
- **Relationships**:
  - `Makes` (N:1): User who made the purchase (`FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE`).
  - `Includes` (N:1): Specific size purchased (`FOREIGN KEY (garment_size_id) REFERENCES garment_sizes(garment_size_id) ON DELETE RESTRICT`).

---

### Entity 8: `FIT_REVIEW` (Associative / Strong Entity)
- **Purpose**: User-generated reviews evaluating whether a garment size fits True to Size, Runs Small, or Runs Large, with granular feedback on waist, hip, and length.
- **Classification**: Strong / Associative Entity. Maintains an independent surrogate key `review_id`.
- **Attributes**:
  - `review_id` (PK, solid underline): Unique review record identifier.
  - `overall_fit`: Qualitative rating (`Runs Small`, `True to Size`, `Runs Large`).
  - `waist_fit`, `hip_fit`, `length_fit`: Granular segment fit classifications.
  - `review_text`: Natural language review feedback (embedded into Redis vector store).
  - `rating`: Star rating (1 to 5).
  - `created_at`: Review submission timestamp.
- **Relationships**:
  - `Writes` (N:1): Author user (`FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE`).
  - `Reviews` (N:1): Target garment size evaluated (`FOREIGN KEY (size_id) REFERENCES garment_sizes(garment_size_id) ON DELETE RESTRICT`).

---

## 3. Relational Mapping & Weak Entity Transformation Summary

Under formal DBMS relational translation rules (Elmasri & Navathe / Silberschatz, Korth & Sudarshan):

1. **Mapping of Regular Strong Entities**:
   - Each strong entity $E$ is mapped to a relation $R$ containing all simple attributes of $E$. The primary key of $R$ is the primary key of $E$.
   - Relations: `users`, `brands`, `garments`.

2. **Mapping of Weak Entities**:
   - For each weak entity $W$ with owner strong entity $O$, create a relation $R$ containing all simple attributes of $W$.
   - Include the primary key of the owner relation $O$ as a foreign key attribute in $R$.
   - The primary key of $R$ is conceptually the composite key:
     $$\text{PK}(R) = \{\text{PK}(O), \text{Discriminator}(W)\}$$
   - **Academic Implementation Choice**:
     To maintain maximum relational performance and avoid wide composite foreign keys across multi-level hierarchies (such as foreign keys referencing 3 or 4 columns down into `purchases` and `fit_reviews`), FitCheck implements an **indexed surrogate primary key** while strictly enforcing the composite candidate key via a `UNIQUE` constraint and `ON DELETE CASCADE`.
     
     ```sql
     -- Conceptually: PK = (garment_id, size_label)
     -- Physical 3NF Mapping:
     CREATE TABLE garment_sizes (
         garment_size_id INT AUTO_INCREMENT PRIMARY KEY,
         garment_id INT NOT NULL,
         size_label VARCHAR(20) NOT NULL,
         is_available BOOLEAN DEFAULT TRUE,
         stock_quantity INT DEFAULT 0,
         CONSTRAINT uq_garment_size UNIQUE (garment_id, size_label),
         CONSTRAINT fk_size_garment FOREIGN KEY (garment_id)
             REFERENCES garments(garment_id) ON DELETE CASCADE
     );
     ```
   - This physical mapping strictly guarantees:
     1. **Uniqueness**: No duplicate size labels can exist within the same garment.
     2. **Existence Dependency**: Dropping a garment automatically drops all its sizes via `CASCADE`.
     3. **Referential Efficiency**: Foreign keys from transactions reference the lightweight 4-byte integer `garment_size_id`.

---

## 4. Deliverable Artifact File Index

| Deliverable | File Path | Format | Description |
| :--- | :--- | :--- | :--- |
| **Conceptual ER Diagram (Chen)** | [`docs/diagrams/conceptual_er_diagram.svg`](file:///c:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/docs/diagrams/conceptual_er_diagram.svg) | Vector SVG | Master Chen Conceptual ERD |
| **Conceptual ER Diagram (Print PNG)** | [`docs/diagrams/conceptual_er_diagram.png`](file:///c:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/docs/diagrams/conceptual_er_diagram.png) | 200 DPI PNG | High-Resolution Print Export |
| **Conceptual ER Diagram (Vector PDF)** | [`docs/diagrams/conceptual_er_diagram.pdf`](file:///c:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/docs/diagrams/conceptual_er_diagram.pdf) | Vector PDF | Academic Print-Ready PDF |
| **Relational Schema Diagram** | [`docs/diagrams/relational_schema_diagram.svg`](file:///c:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/docs/diagrams/relational_schema_diagram.svg) | Vector SVG | Master Logical Relational Schema |
| **Relational Schema Diagram (Print PNG)**| [`docs/diagrams/relational_schema_diagram.png`](file:///c:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/docs/diagrams/relational_schema_diagram.png) | 200 DPI PNG | High-Resolution Print Export |
| **Relational Schema Diagram (Vector PDF)**| [`docs/diagrams/relational_schema_diagram.pdf`](file:///c:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/docs/diagrams/relational_schema_diagram.pdf) | Vector PDF | Academic Print-Ready PDF |
| **Entity Explanation Document** | [`docs/ENTITY_EXPLANATION.md`](file:///c:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/docs/ENTITY_EXPLANATION.md) | Markdown | Formal Academic Entity Breakdown |
| **Physical DDL SQL Specification** | [`database/fitcheck_ddl.sql`](file:///c:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/database/fitcheck_ddl.sql) | SQL Script | Complete DDL with Constraints |
| **Physical DML SQL Specification** | [`database/fitcheck_dml.sql`](file:///c:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/database/fitcheck_dml.sql) | SQL Script | Complete Seed Data & Samples |
| **Advanced SQL Concepts** | [`database/queries/advanced_concepts.sql`](file:///c:/Users/Trisha%20V%20P/DBMS-mini--FitCheck/database/queries/advanced_concepts.sql) | SQL Script | Correlated queries, CTEs, Triggers |
