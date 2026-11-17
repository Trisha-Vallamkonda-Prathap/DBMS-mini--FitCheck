"""Deterministic black-and-white FitCheck diagrams from audited MySQL metadata.

Run with Python, Pillow and Playwright (installed Edge/Chromium).
The schema snapshot, not application data or an old diagram, drives every key,
attribute and FK. No connection to MySQL and no database writes occur here.
"""
from pathlib import Path
import json, math, html, shutil, sys
from collections import defaultdict
from PIL import Image, ImageFont

HERE = Path(__file__).resolve().parent
AUDIT_PATH = HERE / 'docs' / 'diagrams' / 'FitCheck_Schema_Audit.json'
SCHEMA = json.loads(AUDIT_PATH.read_text(encoding='utf-8'))
OUT = HERE / 'docs' / 'diagrams'
OUT.mkdir(exist_ok=True)
ORDER = ['USER', 'BODY_PROFILE', 'BRAND', 'GARMENT', 'GARMENT_SIZE', 'GARMENT_MEASUREMENT', 'PURCHASE', 'FIT_REVIEW', 'REVIEW_AUDIT']

def keys(name):
    grouped = defaultdict(list)
    for row in SCHEMA[name]['keys']:
        grouped[(row['CONSTRAINT_TYPE'], row['CONSTRAINT_NAME'])].append(row['COLUMN_NAME'])
    return dict(grouped)

def primary(name):
    return next(columns for (kind, _), columns in keys(name).items() if kind == 'PRIMARY KEY')

RELATIONS = []
for child in ORDER:
    for fk in SCHEMA[child]['foreign_keys']:
        parent = fk['REFERENCED_TABLE_NAME'].upper()
        column = next(c for c in SCHEMA[child]['columns'] if c['COLUMN_NAME'] == fk['COLUMN_NAME'])
        unique = any(cols == [fk['COLUMN_NAME']] for cols in keys(child).values())
        RELATIONS.append({**fk, 'child': child, 'parent': parent,
                          'parent_participation': '(0,1)' if unique else '(0,N)',
                          'child_participation': '(1,1)' if column['IS_NULLABLE'] == 'NO' else '(0,1)'})
assert len(SCHEMA) == 9 and len(RELATIONS) == 8
assert all(len(primary(n)) == 1 for n in ORDER)
assert not SCHEMA['REVIEW_AUDIT']['foreign_keys']

def esc(value): return html.escape(str(value), quote=True)

class SVG:
    def __init__(self, width, height, title, subtitle):
        self.w, self.h = width, height
        self.elements = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
          '<defs><marker id="arrow" viewBox="0 0 12 10" refX="11" refY="5" markerWidth="12" markerHeight="10" orient="auto"><path d="M0,0 L12,5 L0,10 Z" fill="black"/></marker></defs>',
          '<g font-family="Times New Roman,serif" fill="black" stroke="none">',
          f'<rect width="{width}" height="{height}" fill="white"/>',
          f'<rect x="22" y="22" width="{width-44}" height="{height-44}" fill="none" stroke="black" stroke-width="2"/>']
        self.text(width/2, 80, title, 43, bold=True)
        self.text(width/2, 126, subtitle, 25)
        self.path([(22,155),(width-22,155)], 1.5)

    def text(self, x,y,label,size=26,anchor='middle',bold=False,underline=False):
        self.elements.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" dominant-baseline="middle"'+(' font-weight="bold"' if bold else '')+(' text-decoration="underline"' if underline else '')+f'>{esc(label)}</text>')

    def path(self, points, width=2, arrow=False):
        self.elements.append('<path d="'+' '.join(('M' if i==0 else 'L')+f'{x},{y}' for i,(x,y) in enumerate(points))+f'" fill="none" stroke="black" stroke-width="{width}"'+(' marker-end="url(#arrow)"' if arrow else '')+'/>')

    def rectangle(self,x,y,w,h):
        self.elements.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="white" stroke="black" stroke-width="2"/>')

    def save(self,path):
        path.write_text('\n'.join(self.elements)+ '\n</g></svg>',encoding='utf-8')

FONT = ImageFont.truetype('C:/Windows/Fonts/times.ttf',26)
ENTITIES = {
 'USER':(650,400,300,86), 'BODY_PROFILE':(330,1000,320,86),
 'BRAND':(2600,400,300,86), 'GARMENT':(2600,1000,300,86),
 'GARMENT_SIZE':(2600,1640,360,86), 'GARMENT_MEASUREMENT':(2600,2260,460,86),
 'PURCHASE':(820,1710,320,86), 'FIT_REVIEW':(1420,1000,320,86),
 'REVIEW_AUDIT':(900,2390,360,86),
}
ATTRIBUTES = {
 'USER':[(270,240),(530,200),(770,190),(1040,240),(1060,370),(650,550)],
 'BODY_PROFILE':[(145,830),(120,1080),(130,1200),(290,1320),(500,1300),(640,1180),(660,1030),(560,820)],
 'BRAND':[(2250,210),(2600,195),(2990,230)],
 'GARMENT':[(2310,830),(3050,820),(3140,980),(3100,1140),(3080,1300)],
 'GARMENT_SIZE':[(2970,1550),(2990,1710)],
 'GARMENT_MEASUREMENT':[(3030,2140),(3090,2320),(2980,2470),(2580,2520)],
 'PURCHASE':[(450,1560),(350,1720),(470,1920),(750,2010),(1060,1940)],
 'FIT_REVIEW':[(1120,900),(1100,1050),(1120,1190),(1320,1320),(1600,1330),(1780,1190),(1810,1040),(1760,900)],
 'REVIEW_AUDIT':[(520,2250),(520,2390),(650,2560),(1160,2260),(1290,2390),(1120,2560)],
}
# Traditional Chen maximum-cardinality labels: parent 1, child N (or 1 for UNIQUE FK).
CHEN = {
 'fk_profile_user': ('HAS_PROFILE',(360,690),[(500,420),(360,635)],[(360,745),(330,957)],(350,505),(405,888)),
 'fk_purchase_user': ('MAKES',(840,1450),[(650,443),(840,620),(840,1395)],[(840,1505),(820,1667)],(900,715),(900,1610)),
 'fk_review_user': ('WRITES',(1210,720),[(800,400),(1100,720)],[(1320,720),(1420,957)],(1030,530),(1430,830)),
 'fk_garment_brand': ('PRODUCES',(2600,700),[(2600,443),(2600,645)],[(2600,755),(2600,957)],(2670,520),(2680,865)),
 'fk_size_garment': ('OFFERS_SIZE',(2600,1400),[(2600,1043),(2600,1345)],[(2600,1455),(2600,1597)],(2670,1210),(2680,1530)),
 'fk_measurement_size': ('HAS_MEASUREMENT',(2600,1950),[(2600,1683),(2600,1895)],[(2600,2005),(2600,2217)],(2680,1800),(2680,2100)),
 'fk_purchase_size': ('INCLUDES',(1700,1710),[(2420,1640),(2240,1710),(1810,1710)],[(1590,1710),(980,1710)],(2330,1610),(1060,1670)),
 'fk_review_size': ('REVIEWS',(2100,1000),[(2420,1640),(2280,1500),(2280,1000),(2210,1000)],[(1990,1000),(1580,1000)],(2190,1530),(1660,960)),
}

def double_path(svg,points):
    # Parallel paths denote total participation, NOT an identifying diamond.
    for shift in [-3,3]:
        adjusted=[]
        for i,(x,y) in enumerate(points):
            a=points[max(0,i-1)];b=points[min(len(points)-1,i+1)]
            length=math.hypot(b[0]-a[0],b[1]-a[1]) or 1
            adjusted.append((round(x-shift*(b[1]-a[1])/length,2),round(y+shift*(b[0]-a[0])/length,2)))
        svg.path(adjusted,1.8)

def chen():
    s=SVG(3400,2820,'FitCheck - Conceptual Entity-Relationship Diagram (Chen Notation)',
          'Traditional Chen cardinalities (1 / N); double lines = total participation, single lines = optional participation.')
    for r in RELATIONS:
        label,(x,y),parent_path,child_path,parent_label,child_label=CHEN[r['CONSTRAINT_NAME']]
        s.elements.append(f'<g data-fk="{r["CONSTRAINT_NAME"]}" data-parent="{r["parent"]}" data-child="{r["child"]}">')
        s.path(parent_path,2)
        double_path(s,child_path)
        half_width = max(110, FONT.getlength(label) * 23 / 26 / 2 + 20)
        s.elements.append(f'<polygon points="{x-half_width},{y} {x},{y-55} {x+half_width},{y} {x},{y+55}" fill="white" stroke="black" stroke-width="2"/>')
        s.text(x,y,label,23,bold=True)
        s.text(*parent_label,'1',27,bold=True)
        s.text(*child_label,'1' if r['parent_participation'] == '(0,1)' else 'N',27,bold=True)
        s.elements.append('</g>')
    for name in ORDER:
        x,y,w,h=ENTITIES[name]
        fk_columns={f['COLUMN_NAME'] for f in SCHEMA[name]['foreign_keys']}
        columns=[c for c in SCHEMA[name]['columns'] if c['COLUMN_NAME'] not in fk_columns]
        assert len(columns)==len(ATTRIBUTES[name]),name
        s.elements.append(f'<g data-entity="{name}">')
        for column,(ax,ay) in zip(columns,ATTRIBUTES[name]):
            label=column['COLUMN_NAME'];rx=max(70,FONT.getlength(label)/2+23);ry=31
            dx,dy=ax-x,ay-y
            scale=min((w/2)/abs(dx) if dx else float('inf'),(h/2)/abs(dy) if dy else float('inf'))
            ellipse_scale=1/math.sqrt((dx/rx)**2+(dy/ry)**2)
            s.path([(x+dx*scale,y+dy*scale),(ax-dx*ellipse_scale,ay-dy*ellipse_scale)],1.6)
            s.elements.append(f'<ellipse cx="{ax}" cy="{ay}" rx="{rx}" ry="{ry}" fill="white" stroke="black" stroke-width="1.7"/>')
            s.elements.append(f'<g data-attribute="{label}" data-pk="{str(label in primary(name)).lower()}">')
            s.text(ax,ay,label,26,underline=label in primary(name))
            s.elements.append('</g>')
        s.rectangle(x-w/2,y-h/2,w,h)
        s.text(x,y,name,30,bold=True)
        s.elements.append('</g>')
    s.text(900,2670,'REVIEW_AUDIT stores historical review_id and user_id values.',26)
    s.text(900,2710,'Neither identifier has a foreign key; audit history survives review deletion.',25)
    s.text(2440,2710,'All nine entities have independent primary keys.',25)
    s.text(2440,2750,'Existence dependency does not imply Chen identification dependency.',24)
    s.save(OUT/'FitCheck_ER_Diagram_Final.svg')

BOXES={'USER':(130,200),'BODY_PROFILE':(130,900),'PURCHASE':(1210,200),'FIT_REVIEW':(1210,1000),
       'GARMENT_SIZE':(2290,200),'GARMENT_MEASUREMENT':(2290,1100),'BRAND':(3370,200),
       'GARMENT':(3370,750),'REVIEW_AUDIT':(3370,1550)}
BW,HH,RH=700,64,52
def row_y(name,column):
    i=next(i for i,c in enumerate(SCHEMA[name]['columns']) if c['COLUMN_NAME']==column)
    return BOXES[name][1]+HH+(i+.5)*RH

def relational():
    s=SVG(4200,2250,'FitCheck - Relational Schema',
          'All implemented columns and enforced foreign keys; arrows run from FK rows to referenced PK rows.')
    previous=[]
    # Ports enter exact FK/PK rows, with distinct lanes and a jump at crossings.
    routes={
      'fk_profile_user':[(130,row_y('BODY_PROFILE','user_id')),(70,row_y('BODY_PROFILE','user_id')),(70,290),(130,290)],
      'fk_purchase_user':[(1210,row_y('PURCHASE','user_id')),(1050,row_y('PURCHASE','user_id')),(1050,280),(830,280)],
      'fk_review_user':[(1210,row_y('FIT_REVIEW','user_id')),(930,row_y('FIT_REVIEW','user_id')),(930,300),(830,300)],
      'fk_purchase_size':[(1910,row_y('PURCHASE','garment_size_id')),(2100,row_y('PURCHASE','garment_size_id')),(2100,278),(2290,278)],
      'fk_review_size':[(1910,row_y('FIT_REVIEW','garment_size_id')),(2040,row_y('FIT_REVIEW','garment_size_id')),(2040,302),(2290,302)],
      'fk_measurement_size':[(2290,row_y('GARMENT_MEASUREMENT','garment_size_id')),(2200,row_y('GARMENT_MEASUREMENT','garment_size_id')),(2200,290),(2290,290)],
      'fk_size_garment':[(2990,row_y('GARMENT_SIZE','garment_id')),(3200,row_y('GARMENT_SIZE','garment_id')),(3200,row_y('GARMENT','garment_id')),(3370,row_y('GARMENT','garment_id'))],
      'fk_garment_brand':[(4070,row_y('GARMENT','brand_id')),(4140,row_y('GARMENT','brand_id')),(4140,290),(4070,290)],
    }
    for r in RELATIONS:
        points=routes[r['CONSTRAINT_NAME']]
        s.elements.append(f'<g data-fk="{r["CONSTRAINT_NAME"]}" data-source="{r["child"]}.{r["COLUMN_NAME"]}" data-target="{r["parent"]}.{r["REFERENCED_COLUMN_NAME"]}">')
        # A white break on the underlying line distinguishes crossing from joining.
        for a,b in zip(points,points[1:]):
            for c,d in previous:
                cross=None
                if a[0]==b[0] and c[1]==d[1] and min(a[1],b[1])<c[1]<max(a[1],b[1]) and min(c[0],d[0])<a[0]<max(c[0],d[0]):cross=(a[0],c[1])
                if a[1]==b[1] and c[0]==d[0] and min(a[0],b[0])<c[0]<max(a[0],b[0]) and min(c[1],d[1])<a[1]<max(c[1],d[1]):cross=(c[0],a[1])
                if cross:s.elements.append(f'<circle cx="{cross[0]}" cy="{cross[1]}" r="6" fill="white"/>')
        s.path(points,2.2,True)
        previous+=list(zip(points,points[1:]))
        s.elements.append('</g>')
    for name in ORDER:
        x,y=BOXES[name];data=SCHEMA[name]
        groups=keys(name);unique=[v for (kind,_),v in groups.items() if kind=='UNIQUE']
        composites=[v for v in unique if len(v)>1]
        notes=['UNIQUE ('+', '.join(v)+')' for v in composites]
        for fk in data['foreign_keys']:
            notes += [f'{fk["COLUMN_NAME"]} -> {fk["REFERENCED_TABLE_NAME"].upper()}({fk["REFERENCED_COLUMN_NAME"]})',
                      f'ON DELETE {fk["DELETE_RULE"]}; ON UPDATE {fk["UPDATE_RULE"]}']
            relation = next(r for r in RELATIONS if r['CONSTRAINT_NAME'] == fk['CONSTRAINT_NAME'])
            notes.append(f'{relation["parent"]} {relation["parent_participation"]} -- {name} {relation["child_participation"]}')
        if name=='REVIEW_AUDIT':notes=['review_id / user_id are historical identifiers, not FKs.','Audit records survive deletion of the original review.']
        height=HH+len(data['columns'])*RH+max(18,len(notes)*33+18)
        s.elements.append(f'<g data-table="{name}">')
        s.rectangle(x,y,BW,height)
        s.text(x+BW/2,y+HH/2,name,32,bold=True)
        s.path([(x,y+HH),(x+BW,y+HH)],1.7)
        for i,column in enumerate(data['columns']):
            label=column['COLUMN_NAME'];cy=y+HH+(i+.5)*RH
            flags=[]
            if label in primary(name):flags.append('PK')
            if any(f['COLUMN_NAME']==label for f in data['foreign_keys']):flags.append('FK')
            if [label] in unique:flags.append('UQ')
            for j,combo in enumerate(composites,1):
                if label in combo:flags.append('UQ'+str(j))
            s.elements.append(f'<g data-column="{label}" data-flags="{",".join(flags)}">')
            s.text(x+18,cy,label,25,'start',underline=label in primary(name))
            datatype=column['COLUMN_TYPE'].upper()+(' NULL' if column['IS_NULLABLE']=='YES' else '')
            s.text(x+315,cy,datatype,23,'start')
            s.text(x+BW-18,cy,','.join(flags),22,'end',bold=bool(flags))
            s.elements.append('</g>')
            s.path([(x,cy+RH/2),(x+BW,cy+RH/2)],.65)
        ny=y+HH+len(data['columns'])*RH+25
        for note in notes:
            s.text(x+18,ny,note,21,'start');ny+=33
        s.elements.append('</g>')
    s.text(2100,2120,'PK = primary key; FK = enforced foreign key; UQ = single-column UNIQUE. UQ1 marks the two columns in one composite UNIQUE constraint.',25)
    s.text(2100,2160,'NULL is shown explicitly; every other column is NOT NULL. No composite primary keys and no identifying relationships are implemented.',25)
    s.text(2100,2200,'The notes make optional participation explicit; the Chen diagram shows the same design with 1/N labels and participation lines.',25)
    s.save(OUT/'FitCheck_Relational_Schema_Final.svg')

def audit_report():
    lines=['# FitCheck diagram schema audit','',
      'Source: live MySQL INFORMATION_SCHEMA / SHOW CREATE TABLE, cross-checked with database/fitcheck_setup.sql, database/fitcheck_ddl.sql, database/queries/advanced_concepts.sql and SQLAlchemy models.',
      'No database objects or data were changed. The setup script creates eight core tables; the DDL/advanced-concepts scripts and model additionally implement REVIEW_AUDIT.', '',
      '| Relation | Primary key | Other candidate / UNIQUE keys | Classification | Identifying relationship |',
      '|---|---|---|---|---|']
    for name in ORDER:
        uq=['('+', '.join(v)+')' for (kind,_),v in keys(name).items() if kind=='UNIQUE']
        lines.append(f'| {name} | {", ".join(primary(name))} | {"; ".join(uq) or "None"} | Regular, independent surrogate PK | None |')
    lines+=['','GARMENT_SIZE and GARMENT_MEASUREMENT are existence-dependent on their parent entities, but they are modeled as regular entities because the implemented schema assigns each an independent surrogate primary key. Therefore they are not weak entities under strict Chen identification semantics.', '',
      '## Complete FK / participation matrix','',
      'The internal matrix uses (min,max) participation. The final Chen image uses traditional 1/N maximum-cardinality labels instead: 1 at the parent, N at the child (1 at both ends for the UNIQUE profile FK). Double child-side lines show total participation; single parent-side lines show optional participation. Every FK is NOT NULL, but the database does not require any parent to have children.', '',
      '| Constraint | Child column | Parent key | Parent participation | Child participation | ON DELETE | ON UPDATE |',
      '|---|---|---|---|---|---|---|']
    for r in RELATIONS:
        lines.append(f'| {r["CONSTRAINT_NAME"]} | {r["child"]}.{r["COLUMN_NAME"]} | {r["parent"]}.{r["REFERENCED_COLUMN_NAME"]} | {r["parent_participation"]} | {r["child_participation"]} | {r["DELETE_RULE"]} | {r["UPDATE_RULE"]} |')
    lines+=['','REVIEW_AUDIT has no FK on review_id or user_id. Both are historical values, not referential relationships. The audit triggers record review lifecycle events; history survives review deletion. The diagrams deliberately show the audit table without referential connectors and explain this in a note.', '', '## Columns and CHECK constraints']
    for name in ORDER:
        lines += ['',f'### {name}', '', ', '.join(f'`{c["COLUMN_NAME"]}` {c["COLUMN_TYPE"]} '+('NULL' if c['IS_NULLABLE']=='YES' else 'NOT NULL') for c in SCHEMA[name]['columns'])]
        for check in SCHEMA[name]['checks']:
            lines.append(f'- `{check["CONSTRAINT_NAME"]}`: `{check["CHECK_CLAUSE"]}`')
    lines+=['','## Source / rendering notes','',
      'FitCheck_Schema_Audit.json preserves the metadata used to generate both diagrams. The renderer verifies nine entities, all columns, all primary keys and all eight FK connectors. No double rectangles, double diamonds, derived attributes or multivalued attributes are invented.',
      'The current live review_text type is represented as captured. Review Settings may legitimately switch its TEXT/MEDIUMTEXT capacity later without changing its conceptual attribute.',
      'Live/source difference: REVIEW_AUDIT currently has action VARCHAR(20), user_id NOT NULL and changed_at TIMESTAMP NULL; the DDL template declares VARCHAR(10), user_id NULL and changed_at NOT NULL. The diagrams and snapshot follow the actual live MySQL definition; no implementation was changed. These differences do not create any foreign keys or alter audit-history semantics.',
      'Older narrative documents and the original Draw.io reference are outside this diagram-only correction. Use the two Final images and synchronized image/vector/PDF aliases for submission.']
    (OUT/'FitCheck_Diagram_Audit.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

def render():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser=p.chromium.launch(channel='msedge',headless=True)
        for name,(w,h) in [('FitCheck_ER_Diagram_Final',(3400,2820)),('FitCheck_Relational_Schema_Final',(4200,2250))]:
            page=browser.new_page(viewport={'width':w,'height':h},device_scale_factor=2)
            page.set_content('<html><head><style>@page{size:'+str(w)+'px '+str(h)+'px;margin:0}html,body{margin:0;padding:0;background:white}</style></head><body>'+ (OUT/(name+'.svg')).read_text(encoding='utf-8')+'</body></html>')
            page.screenshot(path=str(OUT/(name+'.png')),full_page=True)
            page.pdf(path=str(OUT/(name+'.pdf')),width=f'{w}px',height=f'{h}px',print_background=True,margin={'top':'0','bottom':'0','left':'0','right':'0'})
            page.close()
        browser.close()

def sync_aliases():
    for canonical,aliases in [('FitCheck_ER_Diagram_Final',['conceptual_er_diagram','er_diagram']),('FitCheck_Relational_Schema_Final',['relational_schema','relational_schema_diagram'])]:
        for alias in aliases:
            for ext in ['svg','png','pdf']:
                shutil.copyfile(OUT/(canonical+'.'+ext),OUT/(alias+'.'+ext))
    with Image.open(OUT/'FitCheck_Relational_Schema_Final.png') as im:
        im.convert('RGB').save(OUT/'relational_schema.jpeg',quality=98,subsampling=0,dpi=(300,300))

if __name__=='__main__':
    chen();relational();audit_report();render();sync_aliases()
    print('Generated:',OUT)
