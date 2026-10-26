"""
FitCheck Academic Diagram Generator
Produces publication-grade, academically rigorous:
1. Conceptual Chen ER Diagram (genuine Chen notation with weak entities, identifying relationships, partial keys)
   -> docs/diagrams/conceptual_er_diagram.svg, .png, .pdf
2. Logical Relational Schema Diagram (tables, columns, types, PK/FK/UQ, relational mappings)
   -> docs/diagrams/relational_schema_diagram.svg, .png, .pdf
"""
import os
import fitz  # PyMuPDF

def generate_conceptual_erd():
    svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2400 1760" width="2400" height="1760" style="background:#FFFFFF; font-family:'Segoe UI', Arial, Helvetica, sans-serif;">
  <defs>
    <style>
      .title { font-size: 26px; font-weight: bold; fill: #111827; }
      .subtitle { font-size: 14px; fill: #4B5563; }
      .entity-title { font-size: 16px; font-weight: bold; text-anchor: middle; fill: #000000; }
      .rel-title { font-size: 12px; font-weight: bold; text-anchor: middle; fill: #000000; }
      .attr-text { font-size: 13px; text-anchor: middle; fill: #000000; }
      .pk-text { font-size: 13.5px; font-weight: bold; text-anchor: middle; text-decoration: underline; fill: #000000; }
      .partial-key-text { font-size: 13.5px; font-weight: bold; text-anchor: middle; fill: #000000; }
      .card-text { font-size: 16px; font-weight: bold; fill: #000000; }
    </style>
  </defs>

  <!-- Canvas Outer Border -->
  <rect x="20" y="20" width="2360" height="1720" fill="#FFFFFF" stroke="#000000" stroke-width="2"/>

  <!-- Title Header Banner -->
  <rect x="50" y="40" width="2300" height="70" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.5"/>
  <text x="1200" y="75" class="title" text-anchor="middle">FitCheck — Conceptual Entity-Relationship (ER) Diagram (Chen Notation)</text>
  <text x="1200" y="98" class="subtitle" text-anchor="middle">Academic DBMS Specification | Strong Entities, Weak Entities with Partial Keys, Identifying Relationships, and Participation Constraints</text>

  <!-- ============================================================== -->
  <!-- ENTITY 1: USER (Strong Entity) -->
  <!-- Pos: X=350, Y=230, W=180, H=60 -->
  <!-- ============================================================== -->
  <rect x="350" y="230" width="180" height="60" fill="#FFFFFF" stroke="#000000" stroke-width="2.5"/>
  <text x="440" y="267" class="entity-title" font-size="18">USER</text>

  <!-- Attributes of USER -->
  <!-- user_id (PK) -->
  <line x1="350" y1="240" x2="210" y2="160" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="190" cy="150" rx="60" ry="24" fill="#FFFFFF" stroke="#000000" stroke-width="1.8"/>
  <text x="190" y="156" class="pk-text">user_id</text>

  <!-- name -->
  <line x1="390" y1="230" x2="330" y2="140" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="320" cy="130" rx="45" ry="22" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="320" y="135" class="attr-text">name</text>

  <!-- email -->
  <line x1="440" y1="230" x2="440" y2="140" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="440" cy="130" rx="45" ry="22" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="440" y="135" class="attr-text">email</text>

  <!-- password_hash -->
  <line x1="490" y1="230" x2="550" y2="140" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="570" cy="130" rx="65" ry="24" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="570" y="135" class="attr-text">password_hash</text>

  <!-- role -->
  <line x1="530" y1="240" x2="670" y2="170" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="690" cy="160" rx="40" ry="22" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="690" y="165" class="attr-text">role</text>

  <!-- created_at -->
  <line x1="530" y1="260" x2="690" y2="230" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="710" cy="230" rx="50" ry="22" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="710" y="235" class="attr-text">created_at</text>


  <!-- ============================================================== -->
  <!-- RELATIONSHIP: Has_Profile (1:1 Identifying Relationship) -->
  <!-- Between USER (350..530, 230..290) and BODY_PROFILE (100..300, 495..555) -->
  <!-- ============================================================== -->
  <line x1="370" y1="290" x2="260" y2="380" stroke="#000000" stroke-width="1.8"/>
  <text x="330" y="325" class="card-text">1</text>

  <!-- Double Diamond for Identifying Relationship -->
  <polygon points="260,340 320,380 260,420 200,380" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <polygon points="260,346 312,380 260,414 208,380" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="260" y="385" class="rel-title">Has_Profile</text>

  <!-- Total Participation Double Line from BODY_PROFILE to Has_Profile -->
  <line x1="256" y1="420" x2="206" y2="495" stroke="#000000" stroke-width="1.5"/>
  <line x1="264" y1="420" x2="214" y2="495" stroke="#000000" stroke-width="1.5"/>
  <text x="250" y="465" class="card-text">1</text>


  <!-- ============================================================== -->
  <!-- ENTITY 2: BODY_PROFILE (Weak / Dependent Entity) -->
  <!-- Owning Entity: USER | Identified By: user_id -->
  <!-- Pos: X=100, Y=495, W=200, H=60 -->
  <!-- ============================================================== -->
  <rect x="100" y="495" width="200" height="60" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <rect x="105" y="500" width="190" height="50" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="200" y="532" class="entity-title">BODY_PROFILE</text>

  <!-- preferred_fit (placed at top-left of BODY_PROFILE) -->
  <line x1="120" y1="495" x2="70" y2="445" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="65" cy="435" rx="50" ry="22" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="65" y="440" class="attr-text" font-size="12">preferred_fit</text>

  <!-- height -->
  <line x1="120" y1="555" x2="70" y2="625" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="65" cy="635" rx="42" ry="22" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="65" y="640" class="attr-text">height</text>

  <!-- waist -->
  <line x1="160" y1="555" x2="135" y2="645" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="130" cy="655" rx="40" ry="22" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="130" y="660" class="attr-text">waist</text>

  <!-- hip -->
  <line x1="200" y1="555" x2="200" y2="655" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="200" cy="665" rx="38" ry="22" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="200" y="670" class="attr-text">hip</text>

  <!-- thigh -->
  <line x1="240" y1="555" x2="265" y2="645" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="270" cy="655" rx="40" ry="22" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="270" y="660" class="attr-text">thigh</text>

  <!-- inseam -->
  <line x1="280" y1="555" x2="330" y2="625" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="340" cy="635" rx="42" ry="22" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="340" y="640" class="attr-text">inseam</text>


  <!-- ============================================================== -->
  <!-- RELATIONSHIP: Places_Order / Makes (1:N) USER -> PURCHASE -->
  <!-- ============================================================== -->
  <line x1="440" y1="290" x2="440" y2="720" stroke="#000000" stroke-width="1.8"/>
  <text x="455" y="360" class="card-text">1</text>

  <polygon points="440,720 495,755 440,790 385,755" fill="#FFFFFF" stroke="#000000" stroke-width="1.8"/>
  <text x="440" y="760" class="rel-title">Makes</text>

  <!-- Enters PURCHASE at top center (330, 860) to avoid any overlap with attributes -->
  <line x1="440" y1="790" x2="330" y2="860" stroke="#000000" stroke-width="1.8"/>
  <text x="400" y="825" class="card-text">N</text>


  <!-- ============================================================== -->
  <!-- ENTITY 3: PURCHASE (Strong Entity) -->
  <!-- Pos: X=240, Y=860, W=180, H=60 -->
  <!-- ============================================================== -->
  <rect x="240" y="860" width="180" height="60" fill="#FFFFFF" stroke="#000000" stroke-width="2.5"/>
  <text x="330" y="897" class="entity-title" font-size="18">PURCHASE</text>

  <!-- Attributes of PURCHASE -->
  <!-- purchase_id (PK) -->
  <line x1="240" y1="875" x2="150" y2="825" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="120" cy="815" rx="60" ry="24" fill="#FFFFFF" stroke="#000000" stroke-width="1.8"/>
  <text x="120" y="821" class="pk-text">purchase_id</text>

  <!-- purchase_date -->
  <line x1="240" y1="900" x2="140" y2="900" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="110" cy="900" rx="55" ry="22" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="110" y="905" class="attr-text" font-size="12.5">purchase_date</text>

  <!-- outcome -->
  <line x1="260" y1="920" x2="160" y2="965" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="140" cy="975" rx="45" ry="22" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="140" y="980" class="attr-text">outcome</text>

  <!-- fit_satisfaction -->
  <line x1="310" y1="920" x2="260" y2="1000" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="250" cy="1015" rx="55" ry="22" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="250" y="1020" class="attr-text" font-size="12">fit_satisfaction</text>

  <!-- fit_preference -->
  <line x1="370" y1="920" x2="385" y2="1000" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="395" cy="1015" rx="55" ry="22" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="395" y="1020" class="attr-text" font-size="12">fit_preference</text>


  <!-- ============================================================== -->
  <!-- RELATIONSHIP: Writes_Review (1:N) USER -> FIT_REVIEW -->
  <!-- ============================================================== -->
  <line x1="510" y1="290" x2="680" y2="430" stroke="#000000" stroke-width="1.8"/>
  <text x="560" y="340" class="card-text">1</text>

  <polygon points="700,400 760,440 700,480 640,440" fill="#FFFFFF" stroke="#000000" stroke-width="1.8"/>
  <text x="700" y="445" class="rel-title">Writes</text>

  <line x1="720" y1="480" x2="790" y2="600" stroke="#000000" stroke-width="1.8"/>
  <text x="765" y="540" class="card-text">N</text>


  <!-- ============================================================== -->
  <!-- ENTITY 4: FIT_REVIEW (Strong Entity) -->
  <!-- Pos: X=730, Y=600, W=190, H=60 -->
  <!-- ============================================================== -->
  <rect x="730" y="600" width="190" height="60" fill="#FFFFFF" stroke="#000000" stroke-width="2.5"/>
  <text x="825" y="637" class="entity-title" font-size="18">FIT_REVIEW</text>

  <!-- Attributes of FIT_REVIEW -->
  <!-- review_id (PK) -->
  <line x1="730" y1="620" x2="620" y2="600" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="590" cy="595" rx="55" ry="24" fill="#FFFFFF" stroke="#000000" stroke-width="1.8"/>
  <text x="590" y="601" class="pk-text">review_id</text>

  <!-- overall_fit -->
  <line x1="730" y1="640" x2="630" y2="660" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="600" cy="670" rx="50" ry="22" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="600" y="675" class="attr-text">overall_fit</text>

  <!-- waist_fit -->
  <line x1="750" y1="660" x2="670" y2="725" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="650" cy="735" rx="45" ry="22" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="650" y="740" class="attr-text">waist_fit</text>

  <!-- hip_fit -->
  <line x1="800" y1="660" x2="750" y2="760" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="740" cy="775" rx="40" ry="22" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="740" y="780" class="attr-text">hip_fit</text>

  <!-- thigh_fit -->
  <line x1="840" y1="660" x2="840" y2="770" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="840" cy="785" rx="42" ry="22" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="840" y="790" class="attr-text">thigh_fit</text>

  <!-- length_fit -->
  <line x1="880" y1="660" x2="930" y2="750" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="945" cy="765" rx="45" ry="22" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="945" y="770" class="attr-text">length_fit</text>

  <!-- review_text -->
  <line x1="910" y1="660" x2="1010" y2="710" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="1035" cy="720" rx="55" ry="22" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="1035" y="725" class="attr-text">review_text</text>

  <!-- created_at (placed cleanly above FIT_REVIEW top-right) -->
  <line x1="880" y1="600" x2="930" y2="550" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="955" cy="540" rx="50" ry="22" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="955" y="545" class="attr-text">created_at</text>


  <!-- ============================================================== -->
  <!-- CATALOG HIERARCHY (RIGHT SIDE) -->
  <!-- BRAND (Strong) -> GARMENT (Strong) -> GARMENT_SIZE (Weak) -> GARMENT_MEASUREMENT (Weak) -->
  <!-- ============================================================== -->

  <!-- ENTITY 5: BRAND (Strong Entity) -->
  <!-- Pos: X=1750, Y=230, W=180, H=60 -->
  <rect x="1750" y="230" width="180" height="60" fill="#FFFFFF" stroke="#000000" stroke-width="2.5"/>
  <text x="1840" y="267" class="entity-title" font-size="18">BRAND</text>

  <!-- Attributes of BRAND -->
  <!-- brand_id (PK) -->
  <line x1="1750" y1="240" x2="1620" y2="160" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="1600" cy="150" rx="60" ry="24" fill="#FFFFFF" stroke="#000000" stroke-width="1.8"/>
  <text x="1600" y="156" class="pk-text" font-size="14.5">brand_id</text>

  <!-- brand_name -->
  <line x1="1800" y1="230" x2="1750" y2="140" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="1740" cy="130" rx="55" ry="24" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="1740" y="136" class="attr-text">brand_name</text>

  <!-- sizing_system -->
  <line x1="1860" y1="230" x2="1900" y2="140" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="1910" cy="130" rx="60" ry="24" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="1910" y="136" class="attr-text">sizing_system</text>

  <!-- Derived Attribute: return_rate (Dashed Oval) -->
  <line x1="1930" y1="240" x2="2040" y2="170" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="2060" cy="160" rx="55" ry="24" fill="#FFFFFF" stroke="#000000" stroke-width="1.5" stroke-dasharray="4,3"/>
  <text x="2060" y="165" class="attr-text" font-size="12" font-style="italic">return_rate</text>


  <!-- ============================================================== -->
  <!-- RELATIONSHIP: Produces (1:N) BRAND -> GARMENT -->
  <!-- ============================================================== -->
  <line x1="1840" y1="290" x2="1840" y2="390" stroke="#000000" stroke-width="1.8"/>
  <text x="1855" y="335" class="card-text">1</text>

  <polygon points="1840,390 1910,430 1840,470 1770,430" fill="#FFFFFF" stroke="#000000" stroke-width="1.8"/>
  <text x="1840" y="435" class="rel-title">Produces</text>

  <line x1="1840" y1="470" x2="1840" y2="570" stroke="#000000" stroke-width="1.8"/>
  <text x="1855" y="525" class="card-text">N</text>


  <!-- ============================================================== -->
  <!-- ENTITY 6: GARMENT (Strong Entity) -->
  <!-- Pos: X=1750, Y=570, W=180, H=60 -->
  <!-- ============================================================== -->
  <rect x="1750" y="570" width="180" height="60" fill="#FFFFFF" stroke="#000000" stroke-width="2.5"/>
  <text x="1840" y="607" class="entity-title" font-size="18">GARMENT</text>

  <!-- Attributes of GARMENT -->
  <!-- garment_id (PK) -->
  <line x1="1750" y1="585" x2="1610" y2="530" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="1580" cy="520" rx="60" ry="24" fill="#FFFFFF" stroke="#000000" stroke-width="1.8"/>
  <text x="1580" y="526" class="pk-text" font-size="14">garment_id</text>

  <!-- garment_name -->
  <line x1="1750" y1="610" x2="1620" y2="630" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="1590" cy="635" rx="60" ry="24" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="1590" y="640" class="attr-text">garment_name</text>

  <!-- garment_category -->
  <line x1="1930" y1="585" x2="2040" y2="540" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="2060" cy="530" rx="65" ry="24" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="2060" y="535" class="attr-text" font-size="12.5">garment_category</text>

  <!-- fit_type -->
  <line x1="1930" y1="610" x2="2050" y2="620" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="2075" cy="625" rx="50" ry="24" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="2075" y="630" class="attr-text">fit_type</text>

  <!-- description -->
  <line x1="1930" y1="625" x2="2040" y2="700" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="2065" cy="715" rx="55" ry="24" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="2065" y="720" class="attr-text">description</text>


  <!-- ============================================================== -->
  <!-- IDENTIFYING RELATIONSHIP: Offers_Size (Double Diamond) -->
  <!-- GARMENT (Owner) -> GARMENT_SIZE (Weak Entity) -->
  <!-- ============================================================== -->
  <line x1="1840" y1="630" x2="1840" y2="730" stroke="#000000" stroke-width="1.8"/>
  <text x="1855" y="675" class="card-text">1</text>

  <!-- Double Diamond -->
  <polygon points="1840,730 1915,775 1840,820 1765,775" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <polygon points="1840,736 1907,775 1840,814 1773,775" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="1840" y="780" class="rel-title">Offers_Size</text>

  <!-- Total Participation Double Line from GARMENT_SIZE to Offers_Size -->
  <line x1="1836" y1="820" x2="1836" y2="920" stroke="#000000" stroke-width="1.5"/>
  <line x1="1844" y1="820" x2="1844" y2="920" stroke="#000000" stroke-width="1.5"/>
  <text x="1855" y="875" class="card-text">N</text>


  <!-- ============================================================== -->
  <!-- ENTITY 7: GARMENT_SIZE (GENUINE WEAK ENTITY - Double Rectangle) -->
  <!-- Owning Entity: GARMENT | Partial Key: size_label (dashed underline) -->
  <!-- Pos: X=1740, Y=920, W=200, H=60 -->
  <!-- ============================================================== -->
  <rect x="1740" y="920" width="200" height="60" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <rect x="1745" y="925" width="190" height="50" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="1840" y="957" class="entity-title" font-size="17">GARMENT_SIZE</text>

  <!-- Partial Key / Discriminator Attribute: size_label (Dashed Underline) -->
  <line x1="1940" y1="945" x2="2070" y2="925" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="2100" cy="920" rx="65" ry="26" fill="#FFFFFF" stroke="#000000" stroke-width="1.8"/>
  <text x="2100" y="925" class="partial-key-text">size_label</text>
  <!-- Dashed Underline for Partial Key -->
  <line x1="2065" y1="932" x2="2135" y2="932" stroke="#000000" stroke-width="1.8" stroke-dasharray="3,3"/>

  <!-- Surrogate Key / Implementation Attribute: garment_size_id -->
  <line x1="1940" y1="960" x2="2070" y2="990" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="2105" cy="1000" rx="70" ry="24" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="2105" y="1005" class="attr-text" font-size="12">garment_size_id</text>


  <!-- ============================================================== -->
  <!-- IDENTIFYING RELATIONSHIP: Has_Measurement (Double Diamond) -->
  <!-- GARMENT_SIZE (Owner) -> GARMENT_MEASUREMENT (Weak Entity) -->
  <!-- ============================================================== -->
  <line x1="1840" y1="980" x2="1840" y2="1070" stroke="#000000" stroke-width="1.8"/>
  <text x="1855" y="1025" class="card-text">1</text>

  <!-- Double Diamond (Width 190, Height 100 for comfortable text padding) -->
  <polygon points="1840,1070 1935,1120 1840,1170 1745,1120" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <polygon points="1840,1076 1927,1120 1840,1164 1753,1120" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="1840" y="1125" class="rel-title">Has_Measurement</text>

  <!-- Total Participation Double Line from GARMENT_MEASUREMENT to Has_Measurement -->
  <line x1="1836" y1="1170" x2="1836" y2="1270" stroke="#000000" stroke-width="1.5"/>
  <line x1="1844" y1="1170" x2="1844" y2="1270" stroke="#000000" stroke-width="1.5"/>
  <text x="1855" y="1225" class="card-text">N</text>


  <!-- ============================================================== -->
  <!-- ENTITY 8: GARMENT_MEASUREMENT (WEAK ENTITY - Double Rectangle) -->
  <!-- Owning Entity: GARMENT_SIZE | Partial Key: measurement_type -->
  <!-- Pos: X=1700, Y=1270, W=280, H=60 -->
  <!-- ============================================================== -->
  <rect x="1700" y="1270" width="280" height="60" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <rect x="1705" y="1275" width="270" height="50" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="1840" y="1307" class="entity-title" font-size="16">GARMENT_MEASUREMENT</text>

  <!-- Partial Key / Discriminator: measurement_type (Dashed Underline) -->
  <line x1="1980" y1="1290" x2="2090" y2="1260" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="2120" cy="1250" rx="75" ry="26" fill="#FFFFFF" stroke="#000000" stroke-width="1.8"/>
  <text x="2120" y="1255" class="partial-key-text">measurement_type</text>
  <!-- Dashed Underline -->
  <line x1="2060" y1="1263" x2="2180" y2="1263" stroke="#000000" stroke-width="1.8" stroke-dasharray="3,3"/>

  <!-- Attribute: measurement_value -->
  <line x1="1980" y1="1310" x2="2100" y2="1325" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="2130" cy="1330" rx="70" ry="24" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="2130" y="1335" class="attr-text" font-size="12.5">measurement_value</text>

  <!-- Attribute: unit -->
  <line x1="1980" y1="1330" x2="2090" y2="1390" stroke="#000000" stroke-width="1.5"/>
  <ellipse cx="2115" cy="1400" rx="45" ry="22" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="2115" y="1405" class="attr-text">unit</text>


  <!-- ============================================================== -->
  <!-- CONNECTIONS FROM ASSOCIATIVE RELATIONSHIPS TO GARMENT_SIZE -->
  <!-- ============================================================== -->

  <!-- PURCHASE -> Includes -> GARMENT_SIZE -->
  <line x1="420" y1="890" x2="1080" y2="890" stroke="#000000" stroke-width="1.8"/>
  <text x="445" y="880" class="card-text">N</text>

  <polygon points="1130,855 1195,890 1130,925 1065,890" fill="#FFFFFF" stroke="#000000" stroke-width="1.8"/>
  <text x="1130" y="895" class="rel-title">Includes</text>

  <line x1="1195" y1="890" x2="1740" y2="940" stroke="#000000" stroke-width="1.8"/>
  <text x="1705" y="930" class="card-text">1</text>

  <!-- FIT_REVIEW -> Reviews -> GARMENT_SIZE -->
  <line x1="920" y1="630" x2="1315" y2="630" stroke="#000000" stroke-width="1.8"/>
  <text x="945" y="620" class="card-text">N</text>

  <polygon points="1380,595 1445,630 1380,665 1315,630" fill="#FFFFFF" stroke="#000000" stroke-width="1.8"/>
  <text x="1380" y="635" class="rel-title">Reviews</text>

  <line x1="1445" y1="630" x2="1750" y2="925" stroke="#000000" stroke-width="1.8"/>
  <text x="1695" y="880" class="card-text">1</text>


  <!-- ============================================================== -->
  <!-- ACADEMIC NOTATION LEGEND (BOTTOM) -->
  <!-- ============================================================== -->
  <rect x="50" y="1470" width="2300" height="240" fill="#F8FAFC" stroke="#000000" stroke-width="2"/>
  <text x="80" y="1505" font-size="18" font-weight="bold" fill="#000000">Academic Conceptual ER Notation Reference (Chen Methodology):</text>

  <!-- Row 1: Strong Entity, Weak Entity, Relationship -->
  <rect x="80" y="1530" width="130" height="42" fill="#FFFFFF" stroke="#000000" stroke-width="2"/>
  <text x="145" y="1556" font-size="13.5" font-weight="bold" text-anchor="middle">Strong Entity</text>
  <text x="225" y="1556" font-size="13" fill="#1E293B">Independent entity with autonomous primary key (e.g. USER, BRAND, GARMENT)</text>

  <rect x="830" y="1530" width="130" height="42" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <rect x="834" y="1534" width="122" height="34" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="895" y="1556" font-size="13.5" font-weight="bold" text-anchor="middle">Weak Entity</text>
  <text x="975" y="1556" font-size="13" fill="#1E293B">Existence-dependent entity identified by owner key + partial key (e.g. GARMENT_SIZE, GARMENT_MEASUREMENT)</text>

  <polygon points="1730,1525 1780,1551 1730,1577 1680,1551" fill="#FFFFFF" stroke="#000000" stroke-width="1.8"/>
  <text x="1730" y="1556" font-size="12" font-weight="bold" text-anchor="middle">Relation</text>
  <text x="1805" y="1556" font-size="13" fill="#1E293B">Standard relationship diamond connecting entities</text>

  <!-- Row 2: Identifying Relationship, Primary Key, Partial Key -->
  <polygon points="135,1605 185,1631 135,1657 85,1631" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <polygon points="135,1610 180,1631 135,1652 90,1631" fill="#FFFFFF" stroke="#000000" stroke-width="1.5"/>
  <text x="135" y="1635" font-size="10.5" font-weight="bold" text-anchor="middle">Ident_Rel</text>
  <text x="225" y="1636" font-size="13" fill="#1E293B">Double diamond identifying relationship binding weak entity to strong owner</text>

  <ellipse cx="895" cy="1631" rx="55" ry="20" fill="#FFFFFF" stroke="#000000" stroke-width="1.8"/>
  <text x="895" y="1636" font-size="12" font-weight="bold" text-anchor="middle" text-decoration="underline">primary_key</text>
  <text x="975" y="1636" font-size="13" fill="#1E293B">Primary key attribute indicated by solid underline</text>

  <ellipse cx="1730" cy="1631" rx="50" ry="20" fill="#FFFFFF" stroke="#000000" stroke-width="1.8"/>
  <text x="1730" y="1636" font-size="12" font-weight="bold" text-anchor="middle">partial_key</text>
  <line x1="1695" y1="1642" x2="1765" y2="1642" stroke="#000000" stroke-width="1.8" stroke-dasharray="3,3"/>
  <text x="1805" y="1636" font-size="13" fill="#1E293B">Discriminator attribute of weak entity indicated by dashed underline</text>

  <!-- Row 3: Derived Attribute, Total Participation, Partial Participation -->
  <ellipse cx="135" cy="1690" rx="50" ry="18" fill="#FFFFFF" stroke="#000000" stroke-width="1.5" stroke-dasharray="4,3"/>
  <text x="135" y="1694" font-size="11.5" font-style="italic" text-anchor="middle">derived_attr</text>
  <text x="225" y="1694" font-size="13" fill="#1E293B">Computed/derived attribute indicated by dashed oval</text>

  <line x1="840" y1="1690" x2="950" y2="1690" stroke="#000000" stroke-width="2"/>
  <line x1="840" y1="1695" x2="950" y2="1695" stroke="#000000" stroke-width="2"/>
  <text x="975" y="1694" font-size="13" fill="#1E293B">Double line indicating Total Participation (mandatory existence dependency)</text>

  <line x1="1680" y1="1692" x2="1780" y2="1692" stroke="#000000" stroke-width="1.8"/>
  <text x="1805" y="1694" font-size="13" fill="#1E293B">Single line indicating Partial Participation (optional association)</text>
</svg>
"""
    with open("docs/diagrams/conceptual_er_diagram.svg", "w", encoding="utf-8") as f:
        f.write(svg)

    doc = fitz.open("docs/diagrams/conceptual_er_diagram.svg")
    pdf_bytes = doc.convert_to_pdf()
    pdf_doc = fitz.open("pdf", pdf_bytes)
    pdf_doc.save("docs/diagrams/conceptual_er_diagram.pdf")

    page = pdf_doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
    pix.save("docs/diagrams/conceptual_er_diagram.png")
    print("[SUCCESS] Regenerated docs/diagrams/conceptual_er_diagram.png & .pdf (Chen ERD)")

    try:
        pix.save("docs/diagrams/er_diagram.png")
        with open("docs/diagrams/er_diagram.svg", "w", encoding="utf-8") as f:
            f.write(svg)
    except Exception as e:
        print("[NOTICE] er_diagram:", e)


def generate_relational_schema_diagram():
    svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2400 1760" width="2400" height="1760" style="background:#FFFFFF; font-family:'Segoe UI', Arial, Helvetica, sans-serif;">
  <defs>
    <style>
      .title { font-size: 26px; font-weight: bold; fill: #111827; }
      .subtitle { font-size: 14px; fill: #4B5563; }
      .table-hdr { font-size: 15px; font-weight: bold; fill: #FFFFFF; }
      .col-pk { font-size: 12px; font-weight: bold; fill: #B91C1C; }
      .col-fk { font-size: 12px; font-weight: bold; fill: #1D4ED8; }
      .col-norm { font-size: 12px; fill: #111827; }
      .col-type { font-size: 11px; fill: #6B7280; font-family: monospace; }
      .card-label { font-size: 11.5px; font-weight: bold; fill: #1E293B; }
      .legend-title { font-size: 16px; font-weight: bold; fill: #111827; }
    </style>
    <marker id="fk-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#2563EB"/>
    </marker>
    <marker id="fk-arrow-weak" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#DC2626"/>
    </marker>
  </defs>

  <!-- Canvas Outer Border -->
  <rect x="20" y="20" width="2360" height="1720" fill="#FFFFFF" stroke="#000000" stroke-width="2"/>

  <!-- Title Header Banner -->
  <rect x="50" y="40" width="2300" height="70" fill="#F1F5F9" stroke="#94A3B8" stroke-width="1.5"/>
  <text x="1200" y="75" class="title" text-anchor="middle">FitCheck — Logical Relational Database Schema Diagram (Physical Design)</text>
  <text x="1200" y="98" class="subtitle" text-anchor="middle">Normalized Relational Model (3NF) | Foreign Key Constraints, Integrity Rules, Unique Keys, and Weak Entity Mappings</text>

  <!-- ============================================================== -->
  <!-- TABLE 1: users -->
  <!-- Pos: X=80, Y=160, W=370, H=280 -->
  <!-- ============================================================== -->
  <rect x="80" y="160" width="370" height="280" fill="#FFFFFF" stroke="#1E293B" stroke-width="2" rx="4"/>
  <rect x="80" y="160" width="370" height="38" fill="#1E293B" rx="4"/>
  <text x="265" y="185" class="table-hdr" text-anchor="middle">users (Strong Entity Table)</text>

  <!-- Columns -->
  <!-- user_id (PK) -->
  <rect x="82" y="200" width="366" height="30" fill="#FEF2F2"/>
  <text x="95" y="220" class="col-pk">PK  user_id</text>
  <text x="260" y="220" class="col-type">INT AUTO_INCREMENT</text>

  <!-- name -->
  <text x="95" y="252" class="col-norm">name</text>
  <text x="260" y="252" class="col-type">VARCHAR(100) NOT NULL</text>
  <line x1="80" y1="262" x2="450" y2="262" stroke="#E2E8F0" stroke-width="1"/>

  <!-- email -->
  <text x="95" y="284" class="col-norm">email [UQ]</text>
  <text x="260" y="284" class="col-type">VARCHAR(191) UNIQUE</text>
  <line x1="80" y1="294" x2="450" y2="294" stroke="#E2E8F0" stroke-width="1"/>

  <!-- password_hash -->
  <text x="95" y="316" class="col-norm">password_hash</text>
  <text x="260" y="316" class="col-type">VARCHAR(255) NOT NULL</text>
  <line x1="80" y1="326" x2="450" y2="326" stroke="#E2E8F0" stroke-width="1"/>

  <!-- role -->
  <text x="95" y="348" class="col-norm">role</text>
  <text x="260" y="348" class="col-type">ENUM('user','admin')</text>
  <line x1="80" y1="358" x2="450" y2="358" stroke="#E2E8F0" stroke-width="1"/>

  <!-- is_active -->
  <text x="95" y="380" class="col-norm">is_active</text>
  <text x="260" y="380" class="col-type">BOOLEAN DEFAULT TRUE</text>
  <line x1="80" y1="390" x2="450" y2="390" stroke="#E2E8F0" stroke-width="1"/>

  <!-- created_at -->
  <text x="95" y="412" class="col-norm">created_at</text>
  <text x="260" y="412" class="col-type">TIMESTAMP DEFAULT NOW</text>


  <!-- ============================================================== -->
  <!-- TABLE 2: body_profiles (Weak Entity Relational Mapping) -->
  <!-- Pos: X=80, Y=510, W=370, H=340 -->
  <!-- ============================================================== -->
  <rect x="80" y="510" width="370" height="340" fill="#FFFFFF" stroke="#DC2626" stroke-width="2.2" stroke-dasharray="6,3" rx="4"/>
  <rect x="80" y="510" width="370" height="38" fill="#991B1B" rx="4"/>
  <text x="265" y="535" class="table-hdr" text-anchor="middle">body_profiles (Weak Entity Mapping)</text>

  <!-- profile_id (Surrogate PK) -->
  <rect x="82" y="550" width="366" height="30" fill="#FEF2F2"/>
  <text x="95" y="570" class="col-pk">PK  profile_id</text>
  <text x="260" y="570" class="col-type">INT AUTO_INCREMENT</text>

  <!-- user_id (FK & Identifying Key, CASCADE) -->
  <rect x="82" y="580" width="366" height="30" fill="#EFF6FF"/>
  <text x="95" y="600" class="col-fk">FK  user_id [UQ] -> users</text>
  <text x="260" y="600" class="col-type">INT (CASCADE)</text>

  <!-- height -->
  <text x="95" y="632" class="col-norm">height</text>
  <text x="260" y="632" class="col-type">DECIMAL(5,2) NULL</text>
  <line x1="80" y1="642" x2="450" y2="642" stroke="#E2E8F0" stroke-width="1"/>

  <!-- waist -->
  <text x="95" y="664" class="col-norm">waist</text>
  <text x="260" y="664" class="col-type">DECIMAL(5,2) NULL</text>
  <line x1="80" y1="674" x2="450" y2="674" stroke="#E2E8F0" stroke-width="1"/>

  <!-- hip -->
  <text x="95" y="696" class="col-norm">hip</text>
  <text x="260" y="696" class="col-type">DECIMAL(5,2) NULL</text>
  <line x1="80" y1="706" x2="450" y2="706" stroke="#E2E8F0" stroke-width="1"/>

  <!-- thigh -->
  <text x="95" y="728" class="col-norm">thigh</text>
  <text x="260" y="728" class="col-type">DECIMAL(5,2) NULL</text>
  <line x1="80" y1="738" x2="450" y2="738" stroke="#E2E8F0" stroke-width="1"/>

  <!-- inseam -->
  <text x="95" y="760" class="col-norm">inseam</text>
  <text x="260" y="760" class="col-type">DECIMAL(5,2) NULL</text>
  <line x1="80" y1="770" x2="450" y2="770" stroke="#E2E8F0" stroke-width="1"/>

  <!-- preferred_fit -->
  <text x="95" y="792" class="col-norm">preferred_fit</text>
  <text x="260" y="792" class="col-type">VARCHAR(20) DEFAULT 'Regular'</text>
  <line x1="80" y1="802" x2="450" y2="802" stroke="#E2E8F0" stroke-width="1"/>

  <!-- updated_at -->
  <text x="95" y="824" class="col-norm">updated_at</text>
  <text x="260" y="824" class="col-type">TIMESTAMP DEFAULT NOW</text>


  <!-- ============================================================== -->
  <!-- TABLE 3: purchases -->
  <!-- Pos: X=540, Y=510, W=400, H=340 -->
  <!-- ============================================================== -->
  <rect x="540" y="510" width="400" height="340" fill="#FFFFFF" stroke="#1E293B" stroke-width="2" rx="4"/>
  <rect x="540" y="510" width="400" height="38" fill="#1E293B" rx="4"/>
  <text x="740" y="535" class="table-hdr" text-anchor="middle">purchases (Associative Entity)</text>

  <!-- purchase_id (PK) -->
  <rect x="542" y="550" width="396" height="30" fill="#FEF2F2"/>
  <text x="555" y="570" class="col-pk">PK  purchase_id</text>
  <text x="740" y="570" class="col-type">INT AUTO_INCREMENT</text>

  <!-- user_id (FK) -->
  <rect x="542" y="580" width="396" height="30" fill="#EFF6FF"/>
  <text x="555" y="600" class="col-fk">FK  user_id -> users</text>
  <text x="740" y="600" class="col-type">INT (CASCADE)</text>

  <!-- garment_size_id (FK) -->
  <rect x="542" y="610" width="396" height="30" fill="#EFF6FF"/>
  <text x="555" y="630" class="col-fk">FK  garment_size_id -> sizes</text>
  <text x="740" y="630" class="col-type">INT (RESTRICT)</text>

  <!-- purchase_date -->
  <text x="555" y="662" class="col-norm">purchase_date</text>
  <text x="740" y="662" class="col-type">TIMESTAMP DEFAULT NOW</text>
  <line x1="540" y1="672" x2="940" y2="672" stroke="#E2E8F0" stroke-width="1"/>

  <!-- outcome -->
  <text x="555" y="694" class="col-norm">outcome</text>
  <text x="740" y="694" class="col-type">ENUM('kept','returned')</text>
  <line x1="540" y1="704" x2="940" y2="704" stroke="#E2E8F0" stroke-width="1"/>

  <!-- fit_satisfaction -->
  <text x="555" y="726" class="col-norm">fit_satisfaction</text>
  <text x="740" y="726" class="col-type">TINYINT (1-5)</text>
  <line x1="540" y1="736" x2="940" y2="736" stroke="#E2E8F0" stroke-width="1"/>

  <!-- fit_preference -->
  <text x="555" y="758" class="col-norm">fit_preference</text>
  <text x="740" y="758" class="col-type">VARCHAR(20)</text>
  <line x1="540" y1="768" x2="940" y2="768" stroke="#E2E8F0" stroke-width="1"/>

  <!-- notes -->
  <text x="555" y="790" class="col-norm">notes</text>
  <text x="740" y="790" class="col-type">TEXT NULL</text>


  <!-- ============================================================== -->
  <!-- TABLE 4: fit_reviews -->
  <!-- Pos: X=1010, Y=510, W=410, H=370 -->
  <!-- ============================================================== -->
  <rect x="1010" y="510" width="410" height="370" fill="#FFFFFF" stroke="#1E293B" stroke-width="2" rx="4"/>
  <rect x="1010" y="510" width="410" height="38" fill="#1E293B" rx="4"/>
  <text x="1215" y="535" class="table-hdr" text-anchor="middle">fit_reviews (Associative Review Entity)</text>

  <!-- review_id (PK) -->
  <rect x="1012" y="550" width="406" height="30" fill="#FEF2F2"/>
  <text x="1025" y="570" class="col-pk">PK  review_id</text>
  <text x="1235" y="570" class="col-type">INT AUTO_INCREMENT</text>

  <!-- user_id (FK) -->
  <rect x="1012" y="580" width="406" height="30" fill="#EFF6FF"/>
  <text x="1025" y="600" class="col-fk">FK  user_id -> users</text>
  <text x="1235" y="600" class="col-type">INT (CASCADE)</text>

  <!-- garment_id (FK) -->
  <rect x="1012" y="610" width="406" height="30" fill="#EFF6FF"/>
  <text x="1025" y="630" class="col-fk">FK  garment_id -> garments</text>
  <text x="1235" y="630" class="col-type">INT (RESTRICT)</text>

  <!-- size_id (FK) -->
  <rect x="1012" y="640" width="406" height="30" fill="#EFF6FF"/>
  <text x="1025" y="660" class="col-fk">FK  size_id -> garment_sizes</text>
  <text x="1235" y="660" class="col-type">INT (RESTRICT)</text>

  <!-- overall_fit -->
  <text x="1025" y="692" class="col-norm">overall_fit</text>
  <text x="1235" y="692" class="col-type">ENUM('True to Size',...)</text>
  <line x1="1010" y1="702" x2="1420" y2="702" stroke="#E2E8F0" stroke-width="1"/>

  <!-- waist_fit / hip_fit / length_fit -->
  <text x="1025" y="724" class="col-norm">waist_fit, hip_fit, length_fit</text>
  <text x="1235" y="724" class="col-type">VARCHAR(20)</text>
  <line x1="1010" y1="734" x2="1420" y2="734" stroke="#E2E8F0" stroke-width="1"/>

  <!-- review_text -->
  <text x="1025" y="756" class="col-norm">review_text</text>
  <text x="1235" y="756" class="col-type">TEXT NOT NULL</text>
  <line x1="1010" y1="766" x2="1420" y2="766" stroke="#E2E8F0" stroke-width="1"/>

  <!-- rating -->
  <text x="1025" y="788" class="col-norm">rating</text>
  <text x="1235" y="788" class="col-type">TINYINT (1-5)</text>
  <line x1="1010" y1="798" x2="1420" y2="798" stroke="#E2E8F0" stroke-width="1"/>

  <!-- created_at -->
  <text x="1025" y="820" class="col-norm">created_at</text>
  <text x="1235" y="820" class="col-type">TIMESTAMP DEFAULT NOW</text>


  <!-- ============================================================== -->
  <!-- TABLE 5: brands -->
  <!-- Pos: X=1900, Y=160, W=380, H=220 -->
  <!-- ============================================================== -->
  <rect x="1900" y="160" width="380" height="220" fill="#FFFFFF" stroke="#1E293B" stroke-width="2" rx="4"/>
  <rect x="1900" y="160" width="380" height="38" fill="#1E293B" rx="4"/>
  <text x="2090" y="185" class="table-hdr" text-anchor="middle">brands (Strong Entity Table)</text>

  <!-- brand_id (PK) -->
  <rect x="1902" y="200" width="376" height="30" fill="#FEF2F2"/>
  <text x="1915" y="220" class="col-pk">PK  brand_id</text>
  <text x="2100" y="220" class="col-type">INT AUTO_INCREMENT</text>

  <!-- brand_name -->
  <text x="1915" y="252" class="col-norm">brand_name [UQ]</text>
  <text x="2100" y="252" class="col-type">VARCHAR(100) UNIQUE</text>
  <line x1="1900" y1="262" x2="2280" y2="262" stroke="#E2E8F0" stroke-width="1"/>

  <!-- sizing_system -->
  <text x="1915" y="284" class="col-norm">sizing_system</text>
  <text x="2100" y="284" class="col-type">VARCHAR(50) DEFAULT 'US'</text>
  <line x1="1900" y1="294" x2="2280" y2="294" stroke="#E2E8F0" stroke-width="1"/>

  <!-- return_rate (derived view/virtual) -->
  <text x="1915" y="316" class="col-norm">return_rate (Virtual)</text>
  <text x="2100" y="316" class="col-type">DECIMAL(4,2) COMPUTED</text>


  <!-- ============================================================== -->
  <!-- TABLE 6: garments -->
  <!-- Pos: X=1900, Y=440, W=380, H=280 -->
  <!-- ============================================================== -->
  <rect x="1900" y="440" width="380" height="280" fill="#FFFFFF" stroke="#1E293B" stroke-width="2" rx="4"/>
  <rect x="1900" y="440" width="380" height="38" fill="#1E293B" rx="4"/>
  <text x="2090" y="465" class="table-hdr" text-anchor="middle">garments (Strong Entity Table)</text>

  <!-- garment_id (PK) -->
  <rect x="1902" y="480" width="376" height="30" fill="#FEF2F2"/>
  <text x="1915" y="500" class="col-pk">PK  garment_id</text>
  <text x="2100" y="500" class="col-type">INT AUTO_INCREMENT</text>

  <!-- brand_id (FK) -->
  <rect x="1902" y="510" width="376" height="30" fill="#EFF6FF"/>
  <text x="1915" y="530" class="col-fk">FK  brand_id -> brands</text>
  <text x="2100" y="530" class="col-type">INT (CASCADE)</text>

  <!-- garment_name -->
  <text x="1915" y="562" class="col-norm">garment_name</text>
  <text x="2100" y="562" class="col-type">VARCHAR(150) NOT NULL</text>
  <line x1="1900" y1="572" x2="2280" y2="572" stroke="#E2E8F0" stroke-width="1"/>

  <!-- garment_category -->
  <text x="1915" y="594" class="col-norm">garment_category</text>
  <text x="2100" y="594" class="col-type">ENUM('Jeans','Shirt',...)</text>
  <line x1="1900" y1="604" x2="2280" y2="604" stroke="#E2E8F0" stroke-width="1"/>

  <!-- fit_type -->
  <text x="1915" y="626" class="col-norm">fit_type</text>
  <text x="2100" y="626" class="col-type">VARCHAR(50)</text>
  <line x1="1900" y1="636" x2="2280" y2="636" stroke="#E2E8F0" stroke-width="1"/>

  <!-- description -->
  <text x="1915" y="658" class="col-norm">description</text>
  <text x="2100" y="658" class="col-type">TEXT NULL</text>


  <!-- ============================================================== -->
  <!-- TABLE 7: garment_sizes (GENUINE WEAK ENTITY RELATIONAL MAPPING) -->
  <!-- Owner: garments | Partial Key: size_label -->
  <!-- Relational Candidate Key: (garment_id, size_label) [UNIQUE] -->
  <!-- Surrogate PK: garment_size_id -->
  <!-- Pos: X=1900, Y=780, W=400, H=280 -->
  <!-- ============================================================== -->
  <rect x="1900" y="780" width="400" height="280" fill="#FFFFFF" stroke="#DC2626" stroke-width="2.5" stroke-dasharray="6,3" rx="4"/>
  <rect x="1900" y="780" width="400" height="38" fill="#991B1B" rx="4"/>
  <text x="2100" y="805" class="table-hdr" text-anchor="middle">garment_sizes (Weak Entity Mapping)</text>

  <!-- garment_size_id (Surrogate PK) -->
  <rect x="1902" y="820" width="396" height="30" fill="#FEF2F2"/>
  <text x="1915" y="840" class="col-pk">PK  garment_size_id</text>
  <text x="2120" y="840" class="col-type">INT AUTO_INCREMENT</text>

  <!-- garment_id (FK & Owner Component of Composite Key) -->
  <rect x="1902" y="850" width="396" height="30" fill="#EFF6FF"/>
  <text x="1915" y="870" class="col-fk">FK  garment_id -> garments</text>
  <text x="2120" y="870" class="col-type">INT (CASCADE)</text>

  <!-- size_label (Partial Key / Discriminator) -->
  <rect x="1902" y="880" width="396" height="30" fill="#FEF3C7"/>
  <text x="1915" y="900" class="col-pk" fill="#B45309">DISCRIM  size_label [PARTIAL KEY]</text>
  <text x="2170" y="900" class="col-type">VARCHAR(20)</text>

  <!-- Composite Candidate Key Constraint Note -->
  <text x="1915" y="932" class="col-norm" font-weight="bold">UQ(garment_id, size_label)</text>
  <text x="2120" y="932" class="col-type">COMPOSITE CANDIDATE PK</text>
  <line x1="1900" y1="942" x2="2300" y2="942" stroke="#E2E8F0" stroke-width="1"/>

  <!-- is_available -->
  <text x="1915" y="964" class="col-norm">is_available</text>
  <text x="2120" y="964" class="col-type">BOOLEAN DEFAULT TRUE</text>
  <line x1="1900" y1="974" x2="2300" y2="974" stroke="#E2E8F0" stroke-width="1"/>

  <!-- stock_quantity -->
  <text x="1915" y="996" class="col-norm">stock_quantity</text>
  <text x="2120" y="996" class="col-type">INT DEFAULT 0</text>


  <!-- ============================================================== -->
  <!-- TABLE 8: garment_measurements (WEAK ENTITY RELATIONAL MAPPING) -->
  <!-- Owner: garment_sizes | Partial Key: measurement_type -->
  <!-- Relational Composite PK / FK: (garment_size_id, measurement_type) -->
  <!-- Pos: X=1900, Y=1130, W=400, H=260 -->
  <!-- ============================================================== -->
  <rect x="1900" y="1130" width="400" height="260" fill="#FFFFFF" stroke="#DC2626" stroke-width="2.5" stroke-dasharray="6,3" rx="4"/>
  <rect x="1900" y="1130" width="400" height="38" fill="#991B1B" rx="4"/>
  <text x="2100" y="1155" class="table-hdr" text-anchor="middle">garment_measurements (Weak Entity)</text>

  <!-- measurement_id (Surrogate PK) -->
  <rect x="1902" y="1170" width="396" height="30" fill="#FEF2F2"/>
  <text x="1915" y="1190" class="col-pk">PK  measurement_id</text>
  <text x="2130" y="1190" class="col-type">INT AUTO_INCREMENT</text>

  <!-- garment_size_id (FK & Owner Component) -->
  <rect x="1902" y="1200" width="396" height="30" fill="#EFF6FF"/>
  <text x="1915" y="1220" class="col-fk">FK  garment_size_id -> sizes</text>
  <text x="2130" y="1220" class="col-type">INT (CASCADE)</text>

  <!-- measurement_type (Partial Key / Discriminator) -->
  <rect x="1902" y="1230" width="396" height="30" fill="#FEF3C7"/>
  <text x="1915" y="1250" class="col-pk" fill="#B45309">DISCRIM  measurement_type</text>
  <text x="2170" y="1250" class="col-type">VARCHAR(30)</text>

  <!-- Composite Constraint Note -->
  <text x="1915" y="1282" class="col-norm" font-weight="bold">UQ(garment_size_id, measurement_type)</text>
  <text x="2170" y="1282" class="col-type">COMPOSITE KEY</text>
  <line x1="1900" y1="1292" x2="2300" y2="1292" stroke="#E2E8F0" stroke-width="1"/>

  <!-- measurement_value -->
  <text x="1915" y="1314" class="col-norm">measurement_value</text>
  <text x="2130" y="1314" class="col-type">DECIMAL(5,2) NOT NULL</text>
  <line x1="1900" y1="1324" x2="2300" y2="1324" stroke="#E2E8F0" stroke-width="1"/>

  <!-- unit -->
  <text x="1915" y="1346" class="col-norm">unit</text>
  <text x="2130" y="1346" class="col-type">VARCHAR(10) DEFAULT 'in'</text>


  <!-- ============================================================== -->
  <!-- FOREIGN KEY RELATIONSHIP CONNECTOR ARROWS (Routed Outside Tables) -->
  <!-- ============================================================== -->

  <!-- 1. users -> body_profiles (1:1 Identifying Cascade) -->
  <path d="M 265 440 L 265 510" fill="none" stroke="#DC2626" stroke-width="2.2" marker-end="url(#fk-arrow-weak)"/>
  <text x="275" y="480" class="card-label" fill="#DC2626">1 : 1 (CASCADE)</text>

  <!-- 2. users -> purchases (1:N Cascade, routed through channel at x=495) -->
  <path d="M 450 220 L 495 220 L 495 600 L 540 600" fill="none" stroke="#2563EB" stroke-width="2" marker-end="url(#fk-arrow)"/>
  <text x="500" y="380" class="card-label">1 : N</text>

  <!-- 3. users -> fit_reviews (1:N Cascade, routed through top channel at y=130) -->
  <path d="M 450 200 L 480 200 L 480 130 L 980 130 L 980 600 L 1010 600" fill="none" stroke="#2563EB" stroke-width="2" marker-end="url(#fk-arrow)"/>
  <text x="730" y="120" class="card-label">1 : N (CASCADE)</text>

  <!-- 4. brands -> garments (1:N Cascade) -->
  <path d="M 2090 380 L 2090 440" fill="none" stroke="#2563EB" stroke-width="2" marker-end="url(#fk-arrow)"/>
  <text x="2100" y="415" class="card-label">1 : N</text>

  <!-- 5. garments -> garment_sizes (1:N Weak Identifying Owner Cascade) -->
  <path d="M 2090 720 L 2090 780" fill="none" stroke="#DC2626" stroke-width="2.5" marker-end="url(#fk-arrow-weak)"/>
  <text x="2100" y="755" class="card-label" fill="#DC2626">1 : N (IDENTIFYING CASCADE)</text>

  <!-- 6. garment_sizes -> garment_measurements (1:N Weak Identifying Owner Cascade) -->
  <path d="M 2090 1060 L 2090 1130" fill="none" stroke="#DC2626" stroke-width="2.5" marker-end="url(#fk-arrow-weak)"/>
  <text x="2100" y="1100" class="card-label" fill="#DC2626">1 : N (IDENTIFYING CASCADE)</text>

  <!-- 7. garment_sizes -> purchases (1:N Restrict, routed along bottom channel y=920, enters purchases at bottom center) -->
  <path d="M 1900 870 L 1600 870 L 1600 920 L 740 920 L 740 850" fill="none" stroke="#2563EB" stroke-width="1.8" marker-end="url(#fk-arrow)"/>
  <text x="1100" y="910" class="card-label">1 : N (RESTRICT)</text>

  <!-- 8. garments -> fit_reviews (1:N Restrict, enters fit_reviews at right side y=630) -->
  <path d="M 1900 500 L 1650 500 L 1650 630 L 1420 630" fill="none" stroke="#2563EB" stroke-width="1.8" marker-end="url(#fk-arrow)"/>
  <text x="1510" y="620" class="card-label">1 : N (RESTRICT)</text>

  <!-- 9. garment_sizes -> fit_reviews (1:N Restrict, enters fit_reviews at right side y=660) -->
  <path d="M 1900 840 L 1580 840 L 1580 660 L 1420 660" fill="none" stroke="#2563EB" stroke-width="1.8" marker-end="url(#fk-arrow)"/>
  <text x="1480" y="650" class="card-label">1 : N (RESTRICT)</text>


  <!-- ============================================================== -->
  <!-- RELATIONAL SCHEMA NOTATION LEGEND (BOTTOM) -->
  <!-- ============================================================== -->
  <rect x="50" y="1450" width="2300" height="260" fill="#F8FAFC" stroke="#000000" stroke-width="2"/>
  <text x="80" y="1485" class="legend-title">Relational Schema Architectural Legend &amp; Course Mapping Principles:</text>

  <!-- Item 1: Strong vs Weak Entity Relational Mapping -->
  <rect x="80" y="1510" width="30" height="20" fill="#1E293B"/>
  <text x="120" y="1525" class="col-norm" font-weight="bold">Solid Border Table:</text>
  <text x="270" y="1525" class="col-norm">Autonomous Base Table (Strong Entity with Independent Primary Key e.g., users, brands, garments)</text>

  <rect x="80" y="1545" width="30" height="20" fill="#FFFFFF" stroke="#DC2626" stroke-width="2" stroke-dasharray="4,2"/>
  <text x="120" y="1560" class="col-norm" font-weight="bold" fill="#DC2626">Dashed Border Table:</text>
  <text x="270" y="1560" class="col-norm">Weak Entity Relational Mapping (Existence-dependent table identified by Owner FK + Discriminator)</text>

  <!-- Item 2: Keys -->
  <rect x="80" y="1580" width="40" height="18" fill="#FEF2F2"/>
  <text x="85" y="1594" class="col-pk">PK</text>
  <text x="130" y="1594" class="col-norm" font-weight="bold">Primary Key (PK):</text>
  <text x="270" y="1594" class="col-norm">Surrogate primary key guaranteeing physical referential efficiency (AUTO_INCREMENT)</text>

  <rect x="80" y="1615" width="40" height="18" fill="#EFF6FF"/>
  <text x="85" y="1629" class="col-fk">FK</text>
  <text x="130" y="1629" class="col-norm" font-weight="bold">Foreign Key (FK):</text>
  <text x="270" y="1629" class="col-norm">Referential integrity link to referenced parent primary key (with CASCADE or RESTRICT rules)</text>

  <rect x="80" y="1650" width="70" height="18" fill="#FEF3C7"/>
  <text x="85" y="1664" class="col-pk" fill="#B45309">DISCRIM</text>
  <text x="160" y="1664" class="col-norm" font-weight="bold">Discriminator:</text>
  <text x="270" y="1664" class="col-norm">Weak entity partial key (e.g. size_label, measurement_type) forming composite candidate key with Owner FK</text>

  <!-- Item 3: Weak Entity Justification Note -->
  <rect x="1200" y="1510" width="1120" height="175" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5" rx="4"/>
  <text x="1220" y="1535" class="col-norm" font-weight="bold">Weak Entity Academic Resolution &amp; Relational Correspondence:</text>
  <text x="1220" y="1560" class="col-norm">• GARMENT_SIZE cannot exist without an owning GARMENT; a size label like "32W 30L" has no standalone meaning.</text>
  <text x="1220" y="1582" class="col-norm">• Conceptual Key: Composite {garment_id, size_label}. Relational implementation preserves this via UQ(garment_id, size_label).</text>
  <text x="1220" y="1604" class="col-norm">• Surrogate garment_size_id is retained to prevent bulky compound foreign keys in child tables (purchases, measurements).</text>
  <text x="1220" y="1626" class="col-norm">• GARMENT_MEASUREMENT is a second-order weak entity dependent on GARMENT_SIZE via UQ(garment_size_id, measurement_type).</text>
  <text x="1220" y="1648" class="col-norm">• Foreign Key cascades ensure full existence dependency: Deleting a GARMENT deletes all its sizes and all their measurements.</text>
</svg>
"""
    with open("docs/diagrams/relational_schema_diagram.svg", "w", encoding="utf-8") as f:
        f.write(svg)

    doc = fitz.open("docs/diagrams/relational_schema_diagram.svg")
    pdf_bytes = doc.convert_to_pdf()
    pdf_doc = fitz.open("pdf", pdf_bytes)
    pdf_doc.save("docs/diagrams/relational_schema_diagram.pdf")

    page = pdf_doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
    pix.save("docs/diagrams/relational_schema_diagram.png")
    print("[SUCCESS] Regenerated docs/diagrams/relational_schema_diagram.png & .pdf")


if __name__ == "__main__":
    generate_conceptual_erd()
    generate_relational_schema_diagram()
    print("[DONE] Both diagrams successfully updated with pristine routing!")
