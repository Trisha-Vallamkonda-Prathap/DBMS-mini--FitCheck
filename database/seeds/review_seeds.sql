-- ============================================================
-- FITCHECK — DETERMINISTIC SYNTHETIC REVIEW SEED DATA (Member B)
-- DATA IS SYNTHETIC
-- Author: Member B (Semantic Fit Intelligence Slice)
-- Idempotent: uses INSERT IGNORE on review_id
-- Foreign keys strictly target valid Member A IDs from ID_MANIFEST.md:
--   user_id: 1..10
--   garment_size_id: 1..70
-- ============================================================

USE fitcheck;

-- Notice of synthetic dataset origin
-- DATA IS SYNTHETIC: Created for academic demonstration of cross-brand fit nuances,
-- review audit trigger execution, and Redis Stack vector semantic search.

INSERT IGNORE INTO FIT_REVIEW (
    review_id,
    user_id,
    garment_size_id,
    overall_fit,
    waist_fit,
    hip_fit,
    thigh_fit,
    length_fit,
    review_text,
    created_at
) VALUES
(1,  2, 3,  'TRUE_TO_SIZE',   'GOOD',  'GOOD',  'GOOD',  'GOOD',  'Classic rigid denim that fits true to size once broken in. Waist and hips are comfortable.', '2026-03-20 10:15:00'),
(2,  2, 18, 'SLIGHTLY_SMALL', 'TIGHT', 'GOOD',  'GOOD',  'LONG',  'The waistband digs into me when sitting down even though hips fit fine. Length is somewhat long for 162cm.', '2026-05-12 14:30:00'),
(3,  3, 1,  'TRUE_TO_SIZE',   'GOOD',  'GOOD',  'GOOD',  'GOOD',  'Snug fit around the waist and hips, perfect vintage silhouette without needing alterations.', '2026-02-14 09:20:00'),
(4,  3, 16, 'TRUE_TO_SIZE',   'GOOD',  'GOOD',  'GOOD',  'LONG',  'Great high-waisted cut. Legs are very wide and long, drags on the ground without chunky platform shoes.', '2026-04-18 16:45:00'),
(5,  4, 5,  'TRUE_TO_SIZE',   'GOOD',  'GOOD',  'GOOD',  'GOOD',  'Comfortable relaxed regular waist. Authentic 501 fit with zero stretch.', '2026-01-25 11:00:00'),
(6,  4, 20, 'SLIGHTLY_LARGE', 'LOOSE', 'GOOD',  'GOOD',  'LONG',  'Runs a bit generous at the waistband. Had to wear a belt to keep them from sliding.', '2026-04-02 18:10:00'),
(7,  5, 3,  'TRUE_TO_SIZE',   'GOOD',  'GOOD',  'GOOD',  'GOOD',  'Spot on sizing in the 501s. Hugs the rear nicely with classic straight leg drape.', '2026-03-05 13:25:00'),
(8,  5, 48, 'TRUE_TO_SIZE',   'GOOD',  'GOOD',  'GOOD',  'GOOD',  'EU 38 fit matches Levis 28 waist perfectly. Great mid rise and clean straight cut.', '2026-05-18 15:40:00'),
(9,  5, 63, 'SLIGHTLY_SMALL', 'TIGHT', 'GOOD',  'TIGHT', 'GOOD',  'Snug around the waist and restrictive through the upper thighs. I recommend sizing up by one.', '2026-06-25 12:00:00'),
(10, 6, 1,  'TRUE_TO_SIZE',   'GOOD',  'GOOD',  'GOOD',  'GOOD',  'Fits true to size for petite frames. Waist is firm but molds after two wears.', '2026-02-18 17:30:00'),
(11, 6, 11, 'TRUE_TO_SIZE',   'GOOD',  'GOOD',  'GOOD',  'GOOD',  'Super flattering high rise skinny. Stretchy material makes the waist and hips very comfortable.', '2026-03-15 11:10:00'),
(12, 6, 41, 'TOO_SMALL',      'TIGHT', 'TIGHT', 'TIGHT', 'SHORT', 'Way too tight everywhere. Could barely pull them over my calves and thighs. Size up at least one size.', '2026-04-10 14:05:00'),
(13, 6, 51, 'TRUE_TO_SIZE',   'GOOD',  'GOOD',  'GOOD',  'LONG',  'Flattering flare silhouette. Fits snug on hips and thighs but hem is definitely too long.', '2026-05-15 16:20:00'),
(14, 7, 4,  'TRUE_TO_SIZE',   'GOOD',  'GOOD',  'GOOD',  'GOOD',  'Ideal fit for 72cm waist. Waistband sits comfortably without any digging.', '2026-01-15 10:50:00'),
(15, 7, 14, 'TRUE_TO_SIZE',   'GOOD',  'GOOD',  'GOOD',  'GOOD',  'Hold-in denim with plenty of stretch. Skinny leg hugs comfortably down to the ankle.', '2026-02-22 13:15:00'),
(16, 7, 23, 'TRUE_TO_SIZE',   'GOOD',  'GOOD',  'GOOD',  'GOOD',  'Sharp formal trousers. Waist is tailored cleanly with no gap at the lower back.', '2026-03-28 15:00:00'),
(17, 7, 44, 'SLIGHTLY_SMALL', 'TIGHT', 'GOOD',  'TIGHT', 'GOOD',  'Tight upper legs and restrictive around thighs, though waist measurement is manageable.', '2026-05-05 12:40:00'),
(18, 8, 2,  'TRUE_TO_SIZE',   'GOOD',  'GOOD',  'GOOD',  'GOOD',  'Standard Levis 27 fit. Non-stretch cotton feels firm on hips initially.', '2026-03-10 14:20:00'),
(19, 8, 7,  'TRUE_TO_SIZE',   'GOOD',  'GOOD',  'GOOD',  'GOOD',  'Super high rise that actually hugs a small waist without excessive gaping.', '2026-04-16 11:35:00'),
(20, 8, 47, 'SLIGHTLY_LARGE', 'LOOSE', 'GOOD',  'GOOD',  'GOOD',  'Slightly loose waist with room to spare. Comfortable for sitting all day in an office.', '2026-05-25 09:45:00'),
(21, 9, 3,  'TRUE_TO_SIZE',   'GOOD',  'GOOD',  'GOOD',  'GOOD',  'Dependable classic cut. Accurate waist and hip measurements as listed on the size chart.', '2026-02-28 16:50:00'),
(22, 9, 53, 'TRUE_TO_SIZE',   'GOOD',  'GOOD',  'GOOD',  'LONG',  'Stretches nicely across hips. Trousers are much too long and require hemming for flats.', '2026-04-12 18:00:00'),
(23, 9, 68, 'TOO_SMALL',      'TIGHT', 'GOOD',  'GOOD',  'SHORT', 'Tight waistband that pinches the stomach. The curvy hip allowance is good but waist is too small.', '2026-06-02 10:10:00'),
(24, 2, 8,  'TRUE_TO_SIZE',   'GOOD',  'GOOD',  'GOOD',  'GOOD',  'The ultra high rise cinches the natural waist nicely with no waist gap at the back.', '2026-04-25 11:00:00'),
(25, 2, 33, 'TOO_LARGE',      'LOOSE', 'LOOSE', 'GOOD',  'LONG',  'Swimming in this size. Massive gap at the waist and bagginess through the seat. Definitely size down.', '2026-06-05 15:20:00'),
(26, 3, 6,  'TRUE_TO_SIZE',   'GOOD',  'GOOD',  'GOOD',  'GOOD',  'Holds everything in securely. Very flattering rise and the length hits right at the ankle bone.', '2026-03-26 12:15:00'),
(27, 3, 31, 'SLIGHTLY_LARGE', 'LOOSE', 'GOOD',  'GOOD',  'LONG',  'Even XS has a loose waistband for a 64cm waist. Fabric is lightweight denim.', '2026-05-24 14:50:00'),
(28, 4, 10, 'TRUE_TO_SIZE',   'GOOD',  'GOOD',  'GOOD',  'GOOD',  'Firm waistband that stays up without folding over. Roomy through hips and thighs.', '2026-03-02 10:05:00'),
(29, 4, 35, 'TRUE_TO_SIZE',   'GOOD',  'GOOD',  'GOOD',  'GOOD',  'Relaxed fit is true to size for curvier figures. Comfortable wide leg drape.', '2026-04-28 17:15:00'),
(30, 5, 13, 'TRUE_TO_SIZE',   'GOOD',  'GOOD',  'GOOD',  'GOOD',  'Great stretch retention. Skinny fit that doesn\'t sag or bag out at the knees after wearing.', '2026-04-15 13:40:00'),
(31, 7, 2,  'TOO_SMALL',      'TIGHT', 'TIGHT', 'TIGHT', 'GOOD',  'Could not button the top two buttons. Way too small in the waist and hips. Need size 29.', '2026-01-20 16:30:00'),
(32, 8, 28, 'TRUE_TO_SIZE',   'GOOD',  'GOOD',  'GOOD',  'GOOD',  'Mid rise straight leg fits smoothly across waist and hips. Casual vintage blue wash.', '2026-05-10 11:45:00'),
(33, 9, 18, 'SLIGHTLY_SMALL', 'TIGHT', 'GOOD',  'GOOD',  'GOOD',  'Waist is snug and digs in after eating. Recommend sizing up for comfort.', '2026-05-14 14:10:00'),
(34, 10, 3, 'TRUE_TO_SIZE',   'GOOD',  'GOOD',  'GOOD',  'GOOD',  'First time buying Levis. Followed size guide waist measurement and it fits like a glove.', '2026-06-12 10:25:00'),
(35, 4, 60, 'TRUE_TO_SIZE',   'GOOD',  'GOOD',  'GOOD',  'LONG',  'Pleated relaxed trousers have a generous hip cut. Comfortable waistband, pants leg is long.', '2026-05-01 12:30:00'),
(36, 5, 66, 'TOO_SMALL',      'TIGHT', 'TIGHT', 'GOOD',  'GOOD',  'Waistband is suffocatingly tight. Curvy cut didn\'t help with the tight top block.', '2026-05-20 15:55:00'),
(37, 6, 36, 'TRUE_TO_SIZE',   'GOOD',  'GOOD',  'GOOD',  'GOOD',  'Clean tailored chino pants. Straight through hips with comfortable taper at ankles.', '2026-04-12 10:00:00'),
(38, 7, 58, 'TRUE_TO_SIZE',   'GOOD',  'GOOD',  'GOOD',  'LONG',  'The waist fits perfectly but the trousers are much too long. Had to take them to a tailor.', '2026-05-22 17:20:00'),
(39, 8, 62, 'SLIGHTLY_SMALL', 'LOOSE', 'GOOD',  'TIGHT', 'GOOD',  'There is a large gap at my waist but my thighs feel restrictive in this cut.', '2026-06-08 13:10:00'),
(40, 3, 21, 'TRUE_TO_SIZE',   'GOOD',  'GOOD',  'GOOD',  'GOOD',  'Snug tailored waist, sharp silhouette for workwear. Good ankle crop length.', '2026-04-20 11:30:00');

SELECT 'Synthetic fit reviews seeded successfully.' AS status;
