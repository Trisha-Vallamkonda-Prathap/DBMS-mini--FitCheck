-- ============================================================
-- FITCHECK — DETERMINISTIC SEED DATA (Member A)
-- Idempotent: uses INSERT IGNORE to prevent duplicate errors.
-- Run AFTER fitcheck_setup.sql has created the schema.
-- ============================================================

USE fitcheck;

-- ============================================================
-- 1. USERS (10 fictional users + 1 admin)
-- Password hashes are bcrypt of 'password123' — for dev/demo only.
-- Member B owns authentication; these records provide FK targets.
-- ============================================================
INSERT IGNORE INTO `USER` (user_id, name, email, password_hash, role) VALUES
(1,  'Admin User',     'admin@fitcheck.local',     '$2b$12$LJ3m6gG8CwLSm5y5BeKV0eOlK.mfVi4Tz8kNfJfKfSsCq0wRy0FnG', 'ADMIN'),
(2,  'Priya Sharma',   'priya@example.com',        '$2b$12$LJ3m6gG8CwLSm5y5BeKV0eOlK.mfVi4Tz8kNfJfKfSsCq0wRy0FnG', 'USER'),
(3,  'Ananya Rao',     'ananya@example.com',       '$2b$12$LJ3m6gG8CwLSm5y5BeKV0eOlK.mfVi4Tz8kNfJfKfSsCq0wRy0FnG', 'USER'),
(4,  'Meera Patel',    'meera@example.com',        '$2b$12$LJ3m6gG8CwLSm5y5BeKV0eOlK.mfVi4Tz8kNfJfKfSsCq0wRy0FnG', 'USER'),
(5,  'Kavya Iyer',     'kavya@example.com',        '$2b$12$LJ3m6gG8CwLSm5y5BeKV0eOlK.mfVi4Tz8kNfJfKfSsCq0wRy0FnG', 'USER'),
(6,  'Riya Nair',      'riya@example.com',         '$2b$12$LJ3m6gG8CwLSm5y5BeKV0eOlK.mfVi4Tz8kNfJfKfSsCq0wRy0FnG', 'USER'),
(7,  'Sneha Gupta',    'sneha@example.com',        '$2b$12$LJ3m6gG8CwLSm5y5BeKV0eOlK.mfVi4Tz8kNfJfKfSsCq0wRy0FnG', 'USER'),
(8,  'Divya Menon',    'divya@example.com',        '$2b$12$LJ3m6gG8CwLSm5y5BeKV0eOlK.mfVi4Tz8kNfJfKfSsCq0wRy0FnG', 'USER'),
(9,  'Tara Desai',     'tara@example.com',         '$2b$12$LJ3m6gG8CwLSm5y5BeKV0eOlK.mfVi4Tz8kNfJfKfSsCq0wRy0FnG', 'USER'),
(10, 'Lakshmi Reddy',  'lakshmi@example.com',      '$2b$12$LJ3m6gG8CwLSm5y5BeKV0eOlK.mfVi4Tz8kNfJfKfSsCq0wRy0FnG', 'USER');

-- ============================================================
-- 2. BODY_PROFILE (8 profiles for users 2-9)
-- ============================================================
INSERT IGNORE INTO BODY_PROFILE (profile_id, user_id, height, waist, hip, thigh, inseam, preferred_fit) VALUES
(1, 2,  162.00, 68.00, 94.00, 54.00, 76.00, 'REGULAR'),
(2, 3,  158.00, 64.00, 90.00, 51.00, 74.00, 'TIGHT'),
(3, 4,  170.00, 74.00, 100.00, 58.00, 80.00, 'RELAXED'),
(4, 5,  165.00, 70.00, 96.00, 55.00, 78.00, 'REGULAR'),
(5, 6,  155.00, 62.00, 88.00, 50.00, 72.00, 'TIGHT'),
(6, 7,  168.00, 72.00, 98.00, 56.00, 79.00, 'REGULAR'),
(7, 8,  160.00, 66.00, 92.00, 53.00, 75.00, 'RELAXED'),
(8, 9,  163.00, 69.00, 95.00, 54.50, 77.00, 'REGULAR');

-- ============================================================
-- 3. BRANDS (5 brands)
-- ============================================================
INSERT IGNORE INTO BRAND (brand_id, brand_name, sizing_system) VALUES
(1, 'Levis',    'WAIST_BASED'),
(2, 'Zara',     'NUMERIC'),
(3, 'H&M',      'ALPHA'),
(4, 'Mango',    'NUMERIC'),
(5, 'Madewell', 'WAIST_BASED');

-- ============================================================
-- 4. GARMENTS (14 garments across 5 brands)
-- ============================================================
INSERT IGNORE INTO GARMENT (garment_id, brand_id, garment_name, garment_category, fit_type, description) VALUES
-- Levis (brand 1)
(1,  1, 'Levis 501 Original',           'Jeans',    'STRAIGHT', 'Classic straight-leg non-stretch denim'),
(2,  1, 'Levis Ribcage Straight Ankle', 'Jeans',    'STRAIGHT', 'Ultra-high rise straight ankle length'),
(3,  1, 'Levis 721 High Rise Skinny',   'Jeans',    'SKINNY',   'High-rise skinny with advanced stretch'),
-- Zara (brand 2)
(4,  2, 'Zara Z1975 Wide Leg',          'Jeans',    'WIDE_LEG', 'High-waist wide leg full-length'),
(5,  2, 'Zara Slim Fit Trousers',       'Trousers', 'SLIM',     'Tailored slim-fit formal trousers'),
(6,  2, 'Zara TRF Straight Leg',        'Jeans',    'STRAIGHT', 'Mid-rise straight casual jeans'),
-- H&M (brand 3)
(7,  3, 'H&M Wide High Jeans',          'Jeans',    'WIDE_LEG', 'High waist wide leg cotton denim'),
(8,  3, 'H&M Slim Fit Chinos',          'Trousers', 'SLIM',     'Stretch cotton slim chinos'),
(9,  3, 'H&M Skinny Regular Jeans',     'Jeans',    'SKINNY',   'Skinny fit regular waist'),
-- Mango (brand 4)
(10, 4, 'Mango Straight Jeans',         'Jeans',    'STRAIGHT', 'Medium-rise straight-cut denim'),
(11, 4, 'Mango Flared Jeans',           'Jeans',    'FLARED',   'High-waist flared cropped jeans'),
(12, 4, 'Mango Relaxed Trousers',       'Trousers', 'RELAXED',  'Pleated relaxed-fit wide trousers'),
-- Madewell (brand 5)
(13, 5, 'Madewell Perfect Vintage',     'Jeans',    'STRAIGHT', 'Non-stretch vintage inspired straight'),
(14, 5, 'Madewell Curvy High Rise',     'Jeans',    'SKINNY',   'Designed for curvy body proportions');

-- ============================================================
-- 5. GARMENT_SIZE (5 sizes per garment = 70 size records)
-- IDs 1-70 correspond to garments 1-14, 5 sizes each
-- ============================================================
INSERT IGNORE INTO GARMENT_SIZE (garment_size_id, garment_id, size_label) VALUES
-- Levis 501 Original (garment 1) — waist-based
(1,  1, '26'), (2,  1, '27'), (3,  1, '28'), (4,  1, '29'), (5,  1, '30'),
-- Levis Ribcage (garment 2)
(6,  2, '26'), (7,  2, '27'), (8,  2, '28'), (9,  2, '29'), (10, 2, '30'),
-- Levis 721 Skinny (garment 3)
(11, 3, '26'), (12, 3, '27'), (13, 3, '28'), (14, 3, '29'), (15, 3, '30'),
-- Zara Z1975 Wide Leg (garment 4) — EU numeric
(16, 4, '34'), (17, 4, '36'), (18, 4, '38'), (19, 4, '40'), (20, 4, '42'),
-- Zara Slim Fit Trousers (garment 5)
(21, 5, '34'), (22, 5, '36'), (23, 5, '38'), (24, 5, '40'), (25, 5, '42'),
-- Zara TRF Straight (garment 6)
(26, 6, '34'), (27, 6, '36'), (28, 6, '38'), (29, 6, '40'), (30, 6, '42'),
-- H&M Wide High Jeans (garment 7) — alpha
(31, 7, 'XS'), (32, 7, 'S'), (33, 7, 'M'), (34, 7, 'L'), (35, 7, 'XL'),
-- H&M Slim Fit Chinos (garment 8)
(36, 8, 'XS'), (37, 8, 'S'), (38, 8, 'M'), (39, 8, 'L'), (40, 8, 'XL'),
-- H&M Skinny Regular (garment 9)
(41, 9, 'XS'), (42, 9, 'S'), (43, 9, 'M'), (44, 9, 'L'), (45, 9, 'XL'),
-- Mango Straight (garment 10) — EU numeric
(46, 10, '34'), (47, 10, '36'), (48, 10, '38'), (49, 10, '40'), (50, 10, '42'),
-- Mango Flared (garment 11)
(51, 11, '34'), (52, 11, '36'), (53, 11, '38'), (54, 11, '40'), (55, 11, '42'),
-- Mango Relaxed Trousers (garment 12)
(56, 12, '34'), (57, 12, '36'), (58, 12, '38'), (59, 12, '40'), (60, 12, '42'),
-- Madewell Perfect Vintage (garment 13) — waist-based
(61, 13, '26'), (62, 13, '27'), (63, 13, '28'), (64, 13, '29'), (65, 13, '30'),
-- Madewell Curvy High Rise (garment 14)
(66, 14, '26'), (67, 14, '27'), (68, 14, '28'), (69, 14, '29'), (70, 14, '30');

-- ============================================================
-- 6. GARMENT_MEASUREMENT
-- 4 measurement types per size: waist, hip, thigh, inseam (all cm)
-- Rise added for selected garments.
-- Realistic women's apparel dimensions reflecting brand-specific vanity sizing.
-- ============================================================

-- Levis 501 Original (garment 1, sizes 1-5)
INSERT IGNORE INTO GARMENT_MEASUREMENT (garment_size_id, measurement_type, measurement_value, unit) VALUES
(1,'waist',66.00,'cm'),(1,'hip',91.00,'cm'),(1,'thigh',54.00,'cm'),(1,'inseam',76.00,'cm'),(1,'rise',27.00,'cm'),
(2,'waist',68.50,'cm'),(2,'hip',93.50,'cm'),(2,'thigh',55.50,'cm'),(2,'inseam',76.00,'cm'),(2,'rise',27.50,'cm'),
(3,'waist',71.00,'cm'),(3,'hip',96.00,'cm'),(3,'thigh',57.00,'cm'),(3,'inseam',76.00,'cm'),(3,'rise',28.00,'cm'),
(4,'waist',73.50,'cm'),(4,'hip',98.50,'cm'),(4,'thigh',58.50,'cm'),(4,'inseam',76.00,'cm'),(4,'rise',28.50,'cm'),
(5,'waist',76.00,'cm'),(5,'hip',101.00,'cm'),(5,'thigh',60.00,'cm'),(5,'inseam',76.00,'cm'),(5,'rise',29.00,'cm');

-- Levis Ribcage (garment 2, sizes 6-10)
INSERT IGNORE INTO GARMENT_MEASUREMENT (garment_size_id, measurement_type, measurement_value, unit) VALUES
(6,'waist',64.00,'cm'),(6,'hip',90.00,'cm'),(6,'thigh',53.00,'cm'),(6,'inseam',71.00,'cm'),(6,'rise',32.00,'cm'),
(7,'waist',66.50,'cm'),(7,'hip',92.50,'cm'),(7,'thigh',54.50,'cm'),(7,'inseam',71.00,'cm'),(7,'rise',32.50,'cm'),
(8,'waist',69.00,'cm'),(8,'hip',95.00,'cm'),(8,'thigh',56.00,'cm'),(8,'inseam',71.00,'cm'),(8,'rise',33.00,'cm'),
(9,'waist',71.50,'cm'),(9,'hip',97.50,'cm'),(9,'thigh',57.50,'cm'),(9,'inseam',71.00,'cm'),(9,'rise',33.50,'cm'),
(10,'waist',74.00,'cm'),(10,'hip',100.00,'cm'),(10,'thigh',59.00,'cm'),(10,'inseam',71.00,'cm'),(10,'rise',34.00,'cm');

-- Levis 721 Skinny (garment 3, sizes 11-15)
INSERT IGNORE INTO GARMENT_MEASUREMENT (garment_size_id, measurement_type, measurement_value, unit) VALUES
(11,'waist',64.50,'cm'),(11,'hip',89.00,'cm'),(11,'thigh',51.00,'cm'),(11,'inseam',76.00,'cm'),
(12,'waist',67.00,'cm'),(12,'hip',91.50,'cm'),(12,'thigh',52.50,'cm'),(12,'inseam',76.00,'cm'),
(13,'waist',69.50,'cm'),(13,'hip',94.00,'cm'),(13,'thigh',54.00,'cm'),(13,'inseam',76.00,'cm'),
(14,'waist',72.00,'cm'),(14,'hip',96.50,'cm'),(14,'thigh',55.50,'cm'),(14,'inseam',76.00,'cm'),
(15,'waist',74.50,'cm'),(15,'hip',99.00,'cm'),(15,'thigh',57.00,'cm'),(15,'inseam',76.00,'cm');

-- Zara Z1975 Wide Leg (garment 4, sizes 16-20)
INSERT IGNORE INTO GARMENT_MEASUREMENT (garment_size_id, measurement_type, measurement_value, unit) VALUES
(16,'waist',64.00,'cm'),(16,'hip',90.00,'cm'),(16,'thigh',56.00,'cm'),(16,'inseam',78.00,'cm'),
(17,'waist',67.00,'cm'),(17,'hip',94.00,'cm'),(17,'thigh',58.00,'cm'),(17,'inseam',78.00,'cm'),
(18,'waist',70.00,'cm'),(18,'hip',98.00,'cm'),(18,'thigh',60.00,'cm'),(18,'inseam',78.00,'cm'),
(19,'waist',74.00,'cm'),(19,'hip',102.00,'cm'),(19,'thigh',62.00,'cm'),(19,'inseam',78.00,'cm'),
(20,'waist',78.00,'cm'),(20,'hip',106.00,'cm'),(20,'thigh',64.00,'cm'),(20,'inseam',78.00,'cm');

-- Zara Slim Fit Trousers (garment 5, sizes 21-25)
INSERT IGNORE INTO GARMENT_MEASUREMENT (garment_size_id, measurement_type, measurement_value, unit) VALUES
(21,'waist',63.00,'cm'),(21,'hip',88.00,'cm'),(21,'thigh',50.00,'cm'),(21,'inseam',77.00,'cm'),
(22,'waist',66.00,'cm'),(22,'hip',92.00,'cm'),(22,'thigh',52.00,'cm'),(22,'inseam',77.00,'cm'),
(23,'waist',69.00,'cm'),(23,'hip',96.00,'cm'),(23,'thigh',54.00,'cm'),(23,'inseam',77.00,'cm'),
(24,'waist',73.00,'cm'),(24,'hip',100.00,'cm'),(24,'thigh',56.00,'cm'),(24,'inseam',77.00,'cm'),
(25,'waist',77.00,'cm'),(25,'hip',104.00,'cm'),(25,'thigh',58.00,'cm'),(25,'inseam',77.00,'cm');

-- Zara TRF Straight (garment 6, sizes 26-30)
INSERT IGNORE INTO GARMENT_MEASUREMENT (garment_size_id, measurement_type, measurement_value, unit) VALUES
(26,'waist',65.00,'cm'),(26,'hip',91.00,'cm'),(26,'thigh',53.00,'cm'),(26,'inseam',76.00,'cm'),
(27,'waist',68.00,'cm'),(27,'hip',94.00,'cm'),(27,'thigh',55.00,'cm'),(27,'inseam',76.00,'cm'),
(28,'waist',71.00,'cm'),(28,'hip',97.00,'cm'),(28,'thigh',57.00,'cm'),(28,'inseam',76.00,'cm'),
(29,'waist',74.00,'cm'),(29,'hip',100.00,'cm'),(29,'thigh',59.00,'cm'),(29,'inseam',76.00,'cm'),
(30,'waist',77.00,'cm'),(30,'hip',103.00,'cm'),(30,'thigh',61.00,'cm'),(30,'inseam',76.00,'cm');

-- H&M Wide High Jeans (garment 7, sizes 31-35)
INSERT IGNORE INTO GARMENT_MEASUREMENT (garment_size_id, measurement_type, measurement_value, unit) VALUES
(31,'waist',62.00,'cm'),(31,'hip',88.00,'cm'),(31,'thigh',52.00,'cm'),(31,'inseam',78.00,'cm'),
(32,'waist',66.00,'cm'),(32,'hip',92.00,'cm'),(32,'thigh',54.00,'cm'),(32,'inseam',78.00,'cm'),
(33,'waist',70.00,'cm'),(33,'hip',96.00,'cm'),(33,'thigh',56.00,'cm'),(33,'inseam',78.00,'cm'),
(34,'waist',74.00,'cm'),(34,'hip',100.00,'cm'),(34,'thigh',58.00,'cm'),(34,'inseam',78.00,'cm'),
(35,'waist',78.00,'cm'),(35,'hip',104.00,'cm'),(35,'thigh',60.00,'cm'),(35,'inseam',78.00,'cm');

-- H&M Slim Fit Chinos (garment 8, sizes 36-40)
INSERT IGNORE INTO GARMENT_MEASUREMENT (garment_size_id, measurement_type, measurement_value, unit) VALUES
(36,'waist',63.00,'cm'),(36,'hip',89.00,'cm'),(36,'thigh',50.00,'cm'),(36,'inseam',76.00,'cm'),
(37,'waist',67.00,'cm'),(37,'hip',93.00,'cm'),(37,'thigh',52.00,'cm'),(37,'inseam',76.00,'cm'),
(38,'waist',71.00,'cm'),(38,'hip',97.00,'cm'),(38,'thigh',54.00,'cm'),(38,'inseam',76.00,'cm'),
(39,'waist',75.00,'cm'),(39,'hip',101.00,'cm'),(39,'thigh',56.00,'cm'),(39,'inseam',76.00,'cm'),
(40,'waist',79.00,'cm'),(40,'hip',105.00,'cm'),(40,'thigh',58.00,'cm'),(40,'inseam',76.00,'cm');

-- H&M Skinny Regular (garment 9, sizes 41-45)
INSERT IGNORE INTO GARMENT_MEASUREMENT (garment_size_id, measurement_type, measurement_value, unit) VALUES
(41,'waist',62.00,'cm'),(41,'hip',87.00,'cm'),(41,'thigh',49.00,'cm'),(41,'inseam',76.00,'cm'),
(42,'waist',66.00,'cm'),(42,'hip',91.00,'cm'),(42,'thigh',51.00,'cm'),(42,'inseam',76.00,'cm'),
(43,'waist',70.00,'cm'),(43,'hip',95.00,'cm'),(43,'thigh',53.00,'cm'),(43,'inseam',76.00,'cm'),
(44,'waist',74.00,'cm'),(44,'hip',99.00,'cm'),(44,'thigh',55.00,'cm'),(44,'inseam',76.00,'cm'),
(45,'waist',78.00,'cm'),(45,'hip',103.00,'cm'),(45,'thigh',57.00,'cm'),(45,'inseam',76.00,'cm');

-- Mango Straight Jeans (garment 10, sizes 46-50)
INSERT IGNORE INTO GARMENT_MEASUREMENT (garment_size_id, measurement_type, measurement_value, unit) VALUES
(46,'waist',65.00,'cm'),(46,'hip',91.00,'cm'),(46,'thigh',53.00,'cm'),(46,'inseam',77.00,'cm'),
(47,'waist',68.00,'cm'),(47,'hip',94.00,'cm'),(47,'thigh',55.00,'cm'),(47,'inseam',77.00,'cm'),
(48,'waist',71.00,'cm'),(48,'hip',97.00,'cm'),(48,'thigh',57.00,'cm'),(48,'inseam',77.00,'cm'),
(49,'waist',74.00,'cm'),(49,'hip',100.00,'cm'),(49,'thigh',59.00,'cm'),(49,'inseam',77.00,'cm'),
(50,'waist',77.00,'cm'),(50,'hip',103.00,'cm'),(50,'thigh',61.00,'cm'),(50,'inseam',77.00,'cm');

-- Mango Flared (garment 11, sizes 51-55)
INSERT IGNORE INTO GARMENT_MEASUREMENT (garment_size_id, measurement_type, measurement_value, unit) VALUES
(51,'waist',64.00,'cm'),(51,'hip',90.00,'cm'),(51,'thigh',54.00,'cm'),(51,'inseam',74.00,'cm'),
(52,'waist',67.00,'cm'),(52,'hip',93.00,'cm'),(52,'thigh',56.00,'cm'),(52,'inseam',74.00,'cm'),
(53,'waist',70.00,'cm'),(53,'hip',96.00,'cm'),(53,'thigh',58.00,'cm'),(53,'inseam',74.00,'cm'),
(54,'waist',73.00,'cm'),(54,'hip',99.00,'cm'),(54,'thigh',60.00,'cm'),(54,'inseam',74.00,'cm'),
(55,'waist',76.00,'cm'),(55,'hip',102.00,'cm'),(55,'thigh',62.00,'cm'),(55,'inseam',74.00,'cm');

-- Mango Relaxed Trousers (garment 12, sizes 56-60)
INSERT IGNORE INTO GARMENT_MEASUREMENT (garment_size_id, measurement_type, measurement_value, unit) VALUES
(56,'waist',66.00,'cm'),(56,'hip',92.00,'cm'),(56,'thigh',56.00,'cm'),(56,'inseam',76.00,'cm'),
(57,'waist',69.00,'cm'),(57,'hip',95.00,'cm'),(57,'thigh',58.00,'cm'),(57,'inseam',76.00,'cm'),
(58,'waist',72.00,'cm'),(58,'hip',98.00,'cm'),(58,'thigh',60.00,'cm'),(58,'inseam',76.00,'cm'),
(59,'waist',75.00,'cm'),(59,'hip',101.00,'cm'),(59,'thigh',62.00,'cm'),(59,'inseam',76.00,'cm'),
(60,'waist',78.00,'cm'),(60,'hip',104.00,'cm'),(60,'thigh',64.00,'cm'),(60,'inseam',76.00,'cm');

-- Madewell Perfect Vintage (garment 13, sizes 61-65)
INSERT IGNORE INTO GARMENT_MEASUREMENT (garment_size_id, measurement_type, measurement_value, unit) VALUES
(61,'waist',66.50,'cm'),(61,'hip',92.00,'cm'),(61,'thigh',54.00,'cm'),(61,'inseam',72.00,'cm'),(61,'rise',28.00,'cm'),
(62,'waist',69.00,'cm'),(62,'hip',94.50,'cm'),(62,'thigh',55.50,'cm'),(62,'inseam',72.00,'cm'),(62,'rise',28.50,'cm'),
(63,'waist',71.50,'cm'),(63,'hip',97.00,'cm'),(63,'thigh',57.00,'cm'),(63,'inseam',72.00,'cm'),(63,'rise',29.00,'cm'),
(64,'waist',74.00,'cm'),(64,'hip',99.50,'cm'),(64,'thigh',58.50,'cm'),(64,'inseam',72.00,'cm'),(64,'rise',29.50,'cm'),
(65,'waist',76.50,'cm'),(65,'hip',102.00,'cm'),(65,'thigh',60.00,'cm'),(65,'inseam',72.00,'cm'),(65,'rise',30.00,'cm');

-- Madewell Curvy High Rise (garment 14, sizes 66-70)
INSERT IGNORE INTO GARMENT_MEASUREMENT (garment_size_id, measurement_type, measurement_value, unit) VALUES
(66,'waist',64.00,'cm'),(66,'hip',92.00,'cm'),(66,'thigh',55.00,'cm'),(66,'inseam',74.00,'cm'),(66,'rise',30.00,'cm'),
(67,'waist',66.50,'cm'),(67,'hip',94.50,'cm'),(67,'thigh',56.50,'cm'),(67,'inseam',74.00,'cm'),(67,'rise',30.50,'cm'),
(68,'waist',69.00,'cm'),(68,'hip',97.00,'cm'),(68,'thigh',58.00,'cm'),(68,'inseam',74.00,'cm'),(68,'rise',31.00,'cm'),
(69,'waist',71.50,'cm'),(69,'hip',99.50,'cm'),(69,'thigh',59.50,'cm'),(69,'inseam',74.00,'cm'),(69,'rise',31.50,'cm'),
(70,'waist',74.00,'cm'),(70,'hip',102.00,'cm'),(70,'thigh',61.00,'cm'),(70,'inseam',74.00,'cm'),(70,'rise',32.00,'cm');

-- ============================================================
-- 7. PURCHASES (30 records)
-- Successful fit evidence: outcome='KEPT' AND fit_satisfaction='GOOD'
-- ============================================================
INSERT IGNORE INTO PURCHASE (purchase_id, user_id, garment_size_id, purchase_date, outcome, fit_satisfaction, fit_preference) VALUES
-- Priya (user 2): knows Levis 28 fits well; tried Zara 38 (kept)
(1,  2, 3,  '2026-03-15', 'KEPT',      'GOOD',    'REGULAR'),   -- Levis 501 sz28
(2,  2, 8,  '2026-04-20', 'KEPT',      'GOOD',    'REGULAR'),   -- Levis Ribcage sz28
(3,  2, 18, '2026-05-10', 'KEPT',      'AVERAGE', 'TIGHT'),     -- Zara Z1975 sz38
(4,  2, 33, '2026-06-01', 'RETURNED',  'POOR',    NULL),        -- H&M Wide High M
-- Ananya (user 3): petite, prefers tight
(5,  3, 1,  '2026-02-10', 'KEPT',      'GOOD',    'TIGHT'),     -- Levis 501 sz26
(6,  3, 6,  '2026-03-22', 'KEPT',      'GOOD',    'TIGHT'),     -- Levis Ribcage sz26
(7,  3, 16, '2026-04-15', 'KEPT',      'GOOD',    'TIGHT'),     -- Zara Z1975 sz34
(8,  3, 31, '2026-05-20', 'EXCHANGED', 'AVERAGE', NULL),        -- H&M Wide High XS
-- Meera (user 4): larger, relaxed fit
(9,  4, 5,  '2026-01-20', 'KEPT',      'GOOD',    'RELAXED'),   -- Levis 501 sz30
(10, 4, 10, '2026-02-28', 'KEPT',      'GOOD',    'RELAXED'),   -- Levis Ribcage sz30
(11, 4, 20, '2026-03-30', 'KEPT',      'AVERAGE', 'REGULAR'),   -- Zara Z1975 sz42
(12, 4, 35, '2026-04-25', 'KEPT',      'GOOD',    'RELAXED'),   -- H&M Wide High XL
-- Kavya (user 5): medium
(13, 5, 3,  '2026-03-01', 'KEPT',      'GOOD',    'REGULAR'),   -- Levis 501 sz28
(14, 5, 13, '2026-04-10', 'KEPT',      'GOOD',    'REGULAR'),   -- Levis 721 sz28
(15, 5, 48, '2026-05-15', 'KEPT',      'GOOD',    'REGULAR'),   -- Mango Straight sz38
(16, 5, 63, '2026-06-20', 'KEPT',      'AVERAGE', 'TIGHT'),     -- Madewell PV sz28
-- Riya (user 6): petite, tries multiple brands
(17, 6, 1,  '2026-02-15', 'KEPT',      'GOOD',    'TIGHT'),     -- Levis 501 sz26
(18, 6, 11, '2026-03-10', 'KEPT',      'GOOD',    'TIGHT'),     -- Levis 721 sz26
(19, 6, 41, '2026-04-05', 'RETURNED',  'POOR',    NULL),        -- H&M Skinny XS
(20, 6, 51, '2026-05-12', 'KEPT',      'GOOD',    'TIGHT'),     -- Mango Flared sz34
-- Sneha (user 7): medium-large
(21, 7, 4,  '2026-01-10', 'KEPT',      'GOOD',    'REGULAR'),   -- Levis 501 sz29
(22, 7, 14, '2026-02-18', 'KEPT',      'GOOD',    'REGULAR'),   -- Levis 721 sz29
(23, 7, 23, '2026-03-25', 'KEPT',      'GOOD',    'REGULAR'),   -- Zara Slim sz38
(24, 7, 44, '2026-04-30', 'KEPT',      'AVERAGE', 'TIGHT'),     -- H&M Skinny L
-- Divya (user 8)
(25, 8, 2,  '2026-03-05', 'KEPT',      'GOOD',    'RELAXED'),   -- Levis 501 sz27
(26, 8, 7,  '2026-04-12', 'KEPT',      'GOOD',    'RELAXED'),   -- Levis Ribcage sz27
(27, 8, 47, '2026-05-20', 'KEPT',      'AVERAGE', 'REGULAR'),   -- Mango Straight sz36
-- Tara (user 9)
(28, 9, 3,  '2026-02-25', 'KEPT',      'GOOD',    'REGULAR'),   -- Levis 501 sz28
(29, 9, 53, '2026-04-08', 'KEPT',      'GOOD',    'REGULAR'),   -- Mango Flared sz38
(30, 9, 68, '2026-05-30', 'RETURNED',  'POOR',    NULL);        -- Madewell Curvy sz28

SELECT 'Seed data loaded successfully.' AS status;
