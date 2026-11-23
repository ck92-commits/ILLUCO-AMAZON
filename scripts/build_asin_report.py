"""ILLUCO Amazon ASIN report: scorecard + reviews + competitors + keywords + PPC + creative + action plan."""
import json, sys, openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.comments import Comment
OUT = sys.argv[1]
sys.path.insert(0, 'scripts')
from links import dp, reviews, drive, link, GH, STORE, SELLER_STOREFRONT, SC, DRIVE_IMAGES
cat = {}
for x in json.load(open('data/raw/illuco_catalog.json')):
    cat.setdefault(x['asin'], x)
comp = {}
for x in json.load(open('data/raw/competitor_search.json')):
    comp.setdefault(x['asin'], x)

F = 'Arial'
HFONT = Font(name=F, bold=True, color='FFFFFF', size=10); HFILL = PatternFill('solid', fgColor='1F3864')
INFILL = PatternFill('solid', fgColor='FFF2CC'); BLUE = Font(name=F, color='0000FF', size=9)
BODY = Font(name=F, size=9); THIN = Side(style='thin', color='BFBFBF'); BOX = Border(top=THIN, bottom=THIN, left=THIN, right=THIN)
wb = openpyxl.Workbook()

def table(ws, headers, rows, widths, start=1, input_cols=()):
    for j, h in enumerate(headers, 1):
        c = ws.cell(start, j, h); c.font = HFONT; c.fill = HFILL
        c.alignment = Alignment(wrap_text=True, vertical='center'); c.border = BOX
    for i, row in enumerate(rows, start + 1):
        for j, v in enumerate(row, 1):
            c = ws.cell(i, j, v); c.font = BODY; c.border = BOX
            c.alignment = Alignment(wrap_text=True, vertical='top')
            if j in input_cols:
                c.fill = INFILL; c.font = BLUE
    for j, w in enumerate(widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(j)].width = w
    ws.freeze_panes = ws.cell(start + 1, 3)

# ---------------- Summary ----------------
s = wb.active; s.title = 'Summary'
lines = [
 ('ILLUCO Amazon Audit - ASIN Report', True),
 ('Prepared 2026-11-20 from public amazon.com / illuco.com data captured the same day. Seller Central metrics (sessions, sales, conversion, PPC) are input cells - see "How to read".', False),
 ('', False),
 ('Key findings (updated with ILLUCO account data, Nov 20)', True),
 ('1. The fog / water-repellent promise fails: 1-star "really not anti-fog or water-resistant" (3X Dark Blue 5-pack) and FBA returns "not really anti-fog", "does not stay dry when water gets sprayed", "foggy lense".', False),
 ('2. The coating gets cooked off: 1-star on B0GGDGRHRR "water shedding last for 1-2 sterilization cycles"; 20% NCX on that SKU. Sales team: customers run a standard 20-minute cycle instead of ILLUCO\'s 5 minutes at 273°F; on the 5-minute cycle the coating is rated for 100+ cycles.', False),
 ('3. The best seller (B0G2DYRY7T: 68 units, 16.8% conversion) is a standalone listing with its own 3.4 rating; B0GGDGRHRR had dropped out of its family.', False),
 ('4. The 5-pack gets the most traffic but converts at 1.3-8.3% per child (2.3% on the 861-session 1X Dark Blue) and is priced $10 above illuco.com.', False),
 ('5. Heads 1X is the top earner ($3,420, 17.4% conversion; half the units to business buyers) despite a 2.0 rating.', False),
 ('6. Sponsored Products Aug 1-Nov 20: $3,059 spend, $8,400 sales, 36.4% ACoS; the dermatoscope campaign spent $740 for 2 orders.', False),
 ('7. Sales team (Claudia): the coating is cooked off by standard 20-minute autoclave cycles because the 5-minute instructions are almost hidden; lead with High Definition, sell 2X / 3X as premium, make the 5-minute autoclave a time saver, say 100+ cycles.', False),
 ('Fix: ILLUCO_Amazon_UPLOAD.xlsx puts all mirrors except photo mirrors into four families, one pack size each (5 Pack, 1 Pack, Grand 2 Pack, Heads 5 Pack) with Color and Size as the choices, rewrites the copy to the sales direction, and adds the Grand, Double-Sided and Double-Sided head products. Amazon prices stay as they are. It goes second: ILLUCO_Amazon_STEP1_delete_parent.xlsx first deletes only IDM-HANDLE-FAMILY-PARENT (the 11/21 family that mixed pack sizes). The upload sends no images: live listings keep what they show (every live main is on pure white) and the Image List tab says which mains to shoot. Upload Check tab: 0 errors in both files.', False),
 ('', False),
 ('How to read', True),
 ('Yellow cells with blue text are inputs. Paste Seller Central numbers there; CVR, ACoS and TACoS calculate automatically.', False),
 ('"Est. monthly units" is a third-party estimate from the scraper, not Amazon data. Replace it with Business Report units.', False),
 ('Complaint causes are hypotheses until the 1-3 star review text is exported from Seller Central (amazon.com hides review text from signed-out visitors).', False),
]
for i, (t, b) in enumerate(lines, 1):
    c = s.cell(i, 1, t); c.font = Font(name=F, bold=b, size=14 if i == 1 else 10); c.alignment = Alignment(wrap_text=True)
s.column_dimensions['A'].width = 150
base_ = len(lines) + 2
s.cell(base_, 1, 'Links').font = Font(name=F, bold=True, size=10)
for k, (txt, url) in enumerate([('ILLUCO Brand Store on Amazon', STORE), ('All ILLUCO USA listings (seller storefront)', SELLER_STOREFRONT),
                                 ('illuco.com dental mirrors', 'https://illuco.com/collections/dental-mirrors'),
                                 ('The upload file (GitHub)', GH + 'ILLUCO_Amazon_UPLOAD.xlsx'),
                                 ('Grand / Double-Sided upload file (GitHub)', GH + 'listings/ILLUCO_Grand_DoubleSided_Mirrors_Amazon_Upload_READY.xlsx'),
                                 ('Drive image folder', 'https://drive.google.com/drive/folders/112-y6c3etIb17RGpJH-nvIgKgCBrRnYQ')], 1):
    link(s.cell(base_ + k, 1), url, txt, size=10)

# ---------------- ASIN Report ----------------
FAM = {
 'B0FDCGG69J': ('5-Pack with Handles', 'P1'), 'B0FCNL53JN': ('Replacement Heads 5-Pack', 'P1'),
 'B0GGD9DVP9': ('Single Mirror with Handle', 'P1'), 'B0FCPD1KKN': ('Dental Photo Mirror', 'P2'),
}
COMPLAINTS = {
 '5-Pack with Handles': ('3.4 stars (5 ratings). Evidence: 1-star "really not anti-fog or water-resistant... retains more water droplets than regular '
                         'front-surface mirrors" (3X Dark Blue); FBA returns "not really anti-fog", "does not stay dry when water gets sprayed - '
                         'the description said it does", "foggy lense". Main cause: fog / water-repellent claim. Conversion is weak (2-3% on the '
                         'highest-traffic children).',
                         'Lead with Ultra High Definition, sell 2X / 3X as premium, make the 5-minute autoclave and 100+ cycles prominent, fog secondary (upload file); merge into one family; '
                         'new images; ask supplier about coating durability.'),
 'Replacement Heads 5-Pack': ('2.0 stars, but the 1X sells best ($3,420, 17.4% conversion, half to business buyers). No complaint text available.',
                              'Title and bullets now state "Cone Socket, Handles Not Included"; compatibility image; new heads family with the '
                              'Double-Sided head; Amazon Business quantity pricing.'),
 'Single Mirror with Handle': ('Family 5.0, but 3X Dark Blue (B0GGDGRHRR) has a 1-star: "water shedding last for 1-2 sterilization cycles" and a 20% '
                               'NCX rate. Image 2 shows five mirrors on a 1-pack.',
                               'Merge all singles into one 1 Pack family; replace image 2; 5-minute autoclave message and bigger instruction card; respond to the NCX flag.'),
 'Dental Photo Mirror': ('No ratings; 20 sessions and 1 sale in the report period. Left as is (owner decision).',
                         'No change for now. Note: model number placeholder "IDMXXX" and price $165 vs $155 on illuco.com.'),
}
import csv as _csv, io as _io
def _num(v):
    v = (v or '').replace('$', '').replace(',', '').replace('%', '').strip()
    try: return float(v)
    except ValueError: return None
BR = {}
for r in _csv.DictReader(_io.StringIO(open('data/account/BusinessReport-11-20-26.csv', 'rb').read().decode('utf-8-sig'))):
    a = r['(Child) ASIN']
    if a in BR:   # keep the row with more sessions (an ASIN can appear under two parents)
        if (_num(r['Sessions - Total']) or 0) <= (BR[a]['sessions'] or 0):
            continue
    BR[a] = dict(sessions=_num(r['Sessions - Total']), units=_num(r['Units Ordered']), sales=_num(r['Ordered Product Sales']))
hdr = ['ASIN', 'Parent ASIN', 'Family', 'Variant', 'Price (live)', 'Rating', 'Ratings count', 'BSR (Dental Mirrors / category)',
       'Est. monthly units (3rd-party est.)', 'Fulfillment', 'Gallery images',
       'Sessions (Business Report 11/20)', 'Units', 'Sales ($)', 'Conversion rate', 'Ad spend ($)', 'Ad sales ($)', 'ACoS', 'TACoS',
       'Main customer complaints (evidence / hypothesis)', 'Recommended improvements', 'Priority', 'Owner', 'Status']
gal = {'B0FCZBD1KY': 7, 'B0FBPG5CS9': 5, 'B0GGDQ15DD': 6, 'B0G2DYRY7T': 4, 'B0GGDGRHRR': 6, 'B0FCNG7T9P': 5}
# Rows follow the upload: each parent, then its children (owner request 11/20). New parents and new products have
# no ASIN until Amazon processes the upload, so they are listed by SKU.
NEW_ROWS = {
    'IDM-2CD41LB': ('5 Pack family: Double-Sided', 'Double-Sided 1X, Light Blue, 5 mirrors + 5 handles', 179.00),
    'IDM-2CD41DB': ('5 Pack family: Double-Sided', 'Double-Sided 1X, Dark Blue, 5 mirrors + 5 handles', 179.00),
    'IDM-2C101LB': ('Grand 2 Pack family', 'Grand Size 10 (34mm) 1X, Light Blue, 2 mirrors + 2 handles', 124.00),
    'IDM-2C101DB': ('Grand 2 Pack family', 'Grand Size 10 (34mm) 1X, Dark Blue, 2 mirrors + 2 handles', 124.00),
    'IDM-2C102LB': ('Grand 2 Pack family', 'Grand Size 10 (34mm) 2X, Light Blue, 2 mirrors + 2 handles', 129.00),
    'IDM-2C102DB': ('Grand 2 Pack family', 'Grand Size 10 (34mm) 2X, Dark Blue, 2 mirrors + 2 handles', 129.00),
    'IDM-3CD41H': ('Heads family: Double-Sided', 'Double-Sided heads 1X, 5 pack, handles not included', 139.00),
}
NEWFAM = {}
for _a in ('B0F84VWGG5', 'B0FCZBD1KY', 'B0FCMVZH31', 'B0F84TKGLS', 'B0F857HKBG', 'B0F85B5BDC'):
    NEWFAM[_a] = '5 Pack family'
for _a in ('B0G2DYRY7T', 'B0GGF37FSB', 'B0GGDV4J6B', 'B0GGD95T8Z', 'B0GGDS9MVF', 'B0GGDGRHRR'):
    NEWFAM[_a] = '1 Pack family'
for _a in ('B0FBPG5CS9', 'B0FCHH2SQB', 'B0FCJY3H9H'):
    NEWFAM[_a] = 'Heads family'
LAYOUT = [   # one family per pack size (owner, 11/23); IDM-HANDLE-FAMILY-PARENT (11/21) is deleted before the upload
    ('parent', 'IDM-5PACK-FAMILY-PARENT', 'PARENT (new): ILLUCO UHD Dental Mirrors with Handles, 5 Pack',
     'Variation theme: Color / Size',
     '8 listings under it: 6 existing 5-packs (moved in) + 2 new Double-Sided 5-packs. Its ASIN appears after Amazon processes the upload.'),
    *[('asin', a) for a in ('B0F84VWGG5', 'B0FCZBD1KY', 'B0FCMVZH31', 'B0F84TKGLS', 'B0F857HKBG', 'B0F85B5BDC')],
    *[('new', k) for k in ('IDM-2CD41LB', 'IDM-2CD41DB')],
    ('parent', 'IDM-SINGLE-FAMILY-PARENT', 'PARENT (new): ILLUCO UHD Dental Mirror with Handle, 1 Pack',
     'Variation theme: Color / Size',
     '6 listings under it, all existing (moved in). Its ASIN appears after Amazon processes the upload.'),
    *[('asin', a) for a in ('B0G2DYRY7T', 'B0GGF37FSB', 'B0GGDV4J6B', 'B0GGD95T8Z', 'B0GGDS9MVF', 'B0GGDGRHRR')],
    ('parent', 'IDM-GRAND-FAMILY-PARENT', 'PARENT (new): ILLUCO Grand UHD Dental Mirrors with Handles, 2 Pack',
     'Variation theme: Color / Size',
     '4 listings under it, all new: they are created once GS1 shows brand ILLUCO for their UPCs.'),
    *[('new', k) for k in ('IDM-2C101LB', 'IDM-2C101DB', 'IDM-2C102LB', 'IDM-2C102DB')],
    ('parent', 'IDM-HEADS-FAMILY-PARENT', 'PARENT (live since 11/21, unchanged): ILLUCO UHD Dental Mirror Heads, 5 Pack',
     'Variation theme: Size',
     '4 listings under it: 3 existing + 1 new (Double-Sided heads).'),
    *[('asin', a) for a in ('B0FBPG5CS9', 'B0FCHH2SQB', 'B0FCJY3H9H')],
    ('new', 'IDM-3CD41H'),
    ('parent', 'B0FCPD1KKN', 'PARENT (live, unchanged): Dental Photo Mirror', 'Not in the upload (owner: left as is)',
     '5 listings under it.'),
    *[('asin', a) for a in ('B0FCNG7T9P', 'B0F86CJ7R6', 'B0F86DNNSV', 'B0FCNRP7NF', 'B0FCN9V5G4')],
    ('section', 'NOT IN A FAMILY'),
    *[('asin', a) for a in ('B0GGDQ15DD', 'B0F7YPNMWK', 'B0F81HQMD2', 'B0F7Z2TP29', 'B0FSM14R8P', 'B0F8CVN4W3')],
]
CHILD_OF_FAMILY = set()
in_family = False
rows, kinds = [], []
for entry in LAYOUT:
    kind = entry[0]
    if kind == 'parent':
        _, sku, label, theme, note = entry
        rows.append([sku, '', label, theme] + [None] * 15 + [note, '', '', '', ''])
        in_family = True
    elif kind == 'section':
        rows.append([entry[1]] + [None] * 23)
        in_family = False
    elif kind == 'new':
        sku = entry[1]; famlabel, desc, price = NEW_ROWS[sku]
        rows.append([sku, '(new)', famlabel, desc, price, None, None, 'New listing', None, 'FBA', 8, None, None, None,
                     None, None, None, None, None, 'New listing: no reviews or sales yet.',
                     'Created by the upload with the new copy and 8 kit images.', 'P1', 'Cenk', 'Not started'])
    else:
        a = entry[1]
        x = cat[a]
        par = x.get('parent_asin')
        fam, pri = FAM.get(par, (None, None))
        if a in ('B0GGDGRHRR', 'B0G2DYRY7T'):
            fam, pri = 'Single Mirror with Handle', 'P1'
        if fam is None:
            fam, pri = ('Headlight' if 'Headlight' in x['title'] else 'Dermatoscope'), 'P3'
        variant = x['title'].split('(')[-1].rstrip(')') if '(' in x['title'] else x['title'][:40]
        bsr = '; '.join(f"#{b['rank']:,} {b['category']}" for b in (x.get('best_sellers_rank') or [])) or 'None shown'
        comp_txt, fix_txt = COMPLAINTS.get(fam, ('No ratings yet.', 'Fix browse classification and attribute errors (see Attribute Fixes tab of the update sheet).'))
        if a == 'B0GGDGRHRR': comp_txt = 'Detached from its family. 1.0 star: "water shedding last for 1-2 sterilization cycles"; NCX 20% ("performance or quality not adequate"). ' + comp_txt
        if a == 'B0G2DYRY7T': comp_txt = 'BEST SELLER (68 units, 16.8% conversion) but a standalone listing with its own 3.4 rating; duplicate of B0GGDQ15DD. A+ uses photo-mirror copy. ' + comp_txt
        if a == 'B0F85B5BDC': comp_txt = 'This 3X Dark Blue variant carries the "not anti-fog or water-resistant" 1-star (with video). ' + comp_txt
        if a == 'B0FCZBD1KY': comp_txt = 'Most traffic in the line (861 sessions) but 2.3% conversion; 9 FBA returns incl. 3 fog / "not as described". ' + comp_txt
        if a == 'B0FCMVZH31': comp_txt = '600 sessions, 1.5% conversion - the weakest converter. ' + comp_txt
        if a == 'B0GGDQ15DD':
            comp_txt = 'DUPLICATE of B0G2DYRY7T: not in the upload; merge it through a Seller Support case. ' + comp_txt
        rows.append([a, par, NEWFAM.get(a, fam), variant, (float(x['price'].replace('$','').replace(',','')) if x.get('price') else None), x.get('rating'), x.get('review_count'), bsr,
                     x.get('estimated_monthly_sales'), 'FBA' if x.get('is_fba') else 'FBM / SFP', gal.get(a, len(x.get('images') or [])),
                     BR.get(a, {}).get('sessions'), BR.get(a, {}).get('units'), BR.get(a, {}).get('sales'), None, None, None, None, None,
                     comp_txt, fix_txt, pri, 'Cenk', 'Not started'])
    kinds.append(kind if kind != 'asin' and kind != 'new' else ('child' if in_family else 'single'))
hdr[1] = 'Parent ASIN (11/20 scrape)'
r_ws = wb.create_sheet('ASIN Report')
table(r_ws, hdr, rows, [26, 14, 26, 30, 9, 7, 8, 26, 10, 9, 8, 9, 8, 10, 9, 10, 10, 8, 8, 55, 50, 7, 9, 11], input_cols=(12, 13, 14, 16, 17))
for i in range(2, len(rows) + 2):
    r_ws[f'O{i}'] = f'=IFERROR(M{i}/L{i},"")'; r_ws[f'O{i}'].number_format = '0.0%'
    r_ws[f'R{i}'] = f'=IFERROR(P{i}/Q{i},"")'; r_ws[f'R{i}'].number_format = '0.0%'
    r_ws[f'S{i}'] = f'=IFERROR(P{i}/N{i},"")'; r_ws[f'S{i}'].number_format = '0.0%'
    for col in 'NPQ': r_ws[f'{col}{i}'].number_format = '$#,##0'
    r_ws[f'E{i}'].number_format = '$#,##0.00'
    for col in 'OST': r_ws[f'{col}{i}'].font = BODY
r_ws.cell(1, 25, 'Critical reviews (opens signed-in)').font = HFONT; r_ws.cell(1, 25).fill = HFILL
r_ws.cell(1, 25).alignment = Alignment(wrap_text=True); r_ws.column_dimensions['Y'].width = 16
PFILL = PatternFill(fill_type='solid', fgColor='DDEBF7'); SFILL = PatternFill(fill_type='solid', fgColor='F0EFEC')
for i, kind in zip(range(2, len(rows) + 2), kinds):
    a = r_ws[f'A{i}'].value; par = r_ws[f'B{i}'].value
    if kind in ('parent', 'section'):
        for j in range(1, 26):
            c = r_ws.cell(i, j); c.fill = PFILL if kind == 'parent' else SFILL
            c.font = Font(name=F, size=10, bold=True)
        if str(a).startswith('B0'):
            link(r_ws[f'A{i}'], dp(a))
        continue
    if kind == 'child':
        r_ws[f'A{i}'].alignment = Alignment(vertical='top', indent=2)
    if str(a).startswith('B0'):
        link(r_ws[f'A{i}'], dp(a))
        link(r_ws.cell(i, 25), reviews(a), '1-3 star reviews')
    if par and str(par).startswith('B0'):
        link(r_ws[f'B{i}'], dp(par))
r_ws['L1'].comment = Comment('Filled from BusinessReport-11-20-26.csv (Detail Page Sales and Traffic by Child Item). Paste a newer export to refresh.', 'audit')
dv = DataValidation(type='list', formula1='"Not started,In progress,Done,Blocked"', allow_blank=True)
r_ws.add_data_validation(dv); dv.add(f'X2:X{len(rows)+1}')

# ---------------- Reviews ----------------
rv = wb.create_sheet('Review Analysis')
fam_rows = [
 ['5-Pack with Handles (B0FDCGG69J)', 3.4, 5, '47% / 18% / 0% / 0% / 35%', 'Fog expectation; 3X distortion/narrow view; value at $95-140', 'B0F85B5BDC (3X Dark Blue) carries a 1-star; title says "Fog-Resistant ... no Distortion" on all magnifications'],
 ['Replacement Heads (B0FCNL53JN)', 2.0, 2, '0% / 33% / 0% / 0% / 67%', 'Handle compatibility (cone socket); heads-only confused with a kit', 'Thread type appears only inside the variation name; no compatibility image'],
 ['Single family (B0GGD9DVP9)', 5.0, 1, '100% 5-star', '-', 'Only 1 rating; image 2 shows five mirrors'],
 ['Orphan 1X single (B0G2DYRY7T)', 3.4, 3, '61% / 0% / 0% / 0% / 39%', 'Product differs from photos (black shank)? quantity/value?', 'Separate listing, separate rating; A+ copy is for photo mirrors'],
 ['Orphan 3X Dark Blue single (B0GGDGRHRR)', 1.0, 1, '100% 1-star', '3X blur/narrow field', 'Missing child of the single family'],
 ['Photo mirrors (B0FCPD1KKN)', None, 0, '-', '-', 'No reviews; enroll in Vine'],
]
table(rv, ['Family / ASIN', 'Rating', 'Ratings', '5/4/3/2/1-star share', 'Most likely complaint drivers (to confirm with review text)', 'Evidence on the listing'],
      fam_rows, [36, 7, 8, 24, 50, 60])
base = len(fam_rows) + 4
rv.cell(base - 1, 1, 'Supporting evidence from illuco.com reviews (15 x 5-star): "they do get a little foggy film on them"; "somewhat fog resistant"; "the multiple box is too expensive and unnecessary for the individual"; "I ordered 2 sets but only one arrived". illuco.com FAQ: "No mirror should be treated as fog-proof" and "The coating can wear over time".').font = BODY
rv.cell(base - 1, 1).alignment = Alignment(wrap_text=True)
rv.merge_cells(start_row=base - 1, start_column=1, end_row=base - 1, end_column=6); rv.row_dimensions[base - 1].height = 45
log_hdr = ['Date', 'ASIN', 'Stars', 'Review title', 'Review text (paste)', 'Complaint category']
for j, h in enumerate(log_hdr, 1):
    c = rv.cell(base + 1, j, h); c.font = HFONT; c.fill = HFILL
rv.cell(base, 1, 'REVIEW LOG - paste every 1-3 star review here (Seller Central > Brand Analytics > Customer Reviews)').font = Font(name=F, bold=True)
ex = ['2026-10-02', 'B0F85B5BDC', 1, '(example) Blurry', '(example row - replace) Image is blurry unless very close to the tooth', 'Magnification/blur']
for j, v in enumerate(ex, 1):
    c = rv.cell(base + 2, j, v); c.font = Font(name=F, size=9, italic=True, color='808080')
cats = '"Fogging,Magnification/blur,Coating/autoclave wear,Handle fit/compatibility,Quantity/what is in box,Price/value,Damaged/defective,Shipping/missing item,Other"'
dv2 = DataValidation(type='list', formula1=cats, allow_blank=True); rv.add_data_validation(dv2); dv2.add(f'F{base+2}:F{base+60}')
for r_ in range(base + 3, base + 61):
    for j in range(1, 7): rv.cell(r_, j).fill = INFILL
srow = base + 1
rv.cell(srow, 8, 'Complaint category').font = HFONT; rv.cell(srow, 8).fill = HFILL
rv.cell(srow, 9, 'Count').font = HFONT; rv.cell(srow, 9).fill = HFILL
for k, ccat in enumerate(cats.strip('"').split(','), 1):
    rv.cell(srow + k, 8, ccat).font = BODY
    rv.cell(srow + k, 9, f'=COUNTIF($F${base+3}:$F${base+60},H{srow+k})').font = BODY
rv.column_dimensions['H'].width = 28; rv.column_dimensions['I'].width = 8

# ---------------- Competitors ----------------
cp = wb.create_sheet('Competitors')
COMPS = [
 ('B0769MYHBB', 'Professional', 6, 'Double-sided #5 cone socket heads; 1 video; minimal bullets; brand trust carries it'),
 ('B0D7QSSQ3F', 'Professional', 12, 'Crystal HD heads; "40% brighter than rhodium"; sold by a dental supply reseller; no A+'),
 ('B0DK453JHV', 'Professional', 6, 'Double-sided EU thread #4'),
 ('B077T1DWDR', 'Professional / value', 5, 'Front surface set of 5 with handles; BSR #21'),
 ('B07NTGBDQW', 'Professional / value', 5, 'Front surface, plasma handle, set of 5'),
 ('B08FHCK6MR', 'Professional / value', None, 'Rhodium front surface'),
 ('B0819456WP', 'Professional', None, 'Double-sided front surface #5 with handle'),
 ('B07DQ69PRR', 'Professional / value', 12, 'Mirror tops, EU threading, front surface'),
 ('B0DYP5QCM5', 'Value heads', 12, '#5 heads, stainless; BSR #26'),
 ('B0D5K6YR1C', 'Value', 12, '#4 front surface with handle'),
 ('B0CQ5GJQ3H', 'Photo mirror', 4, 'Fog-free kit with fan + LED handle; 2 videos; A+; BSR #8. "Customers say": breaks after 3 months, scratches'),
 ('B09T37FZ6X', 'Photo mirror', None, 'Fog-free 2-sided photo reflector'),
 ('B096MLN8B5', 'Photo mirror', 5, 'Budget 5-piece intraoral mirrors; BSR #7'),
 ('B0BFR5V1W5', 'Photo mirror', 5, '2-sided reflector set; 359 ratings'),
 ('B08GSQWY5S', 'Consumer', 1, 'LED anti-fog mouth mirror; #1 Dental Mirrors; 3K+/month'),
 ('B0811SZWV7', 'Consumer', 1, 'Stainless inspection mirror; #2 Dental Mirrors'),
 ('B09JFLLTVX', 'Consumer', 1, 'Stainless mirror with handle; #3 Dental Mirrors'),
]
crow = []
for a, seg, pack, note in COMPS:
    x = comp[a]
    bsr = '; '.join(f"#{b['rank']:,} {b['category']}" for b in (x.get('best_sellers_rank') or []))
    crow.append([a, x.get('brand'), seg, (x.get('title') or '')[:90], x.get('price'), pack, None, x.get('rating'), x.get('review_count'),
                 x.get('bought_in_past_month'), bsr, len(x.get('images') or []), note])
crow += [['ILLUCO 5-Pack', 'ILLUCO', 'Professional (premium)', '5-pack with handles 1X / 2X / 3X', '$95.00', 5, None, 3.4, 5, None, '#54 Dental Mirrors', 7, 'Our listing'],
         ['ILLUCO Heads', 'ILLUCO', 'Professional (premium)', 'Heads 5-pack 1X / 2X / 3X', '$60.00', 5, None, 2.0, 2, None, '#116 Dental Mirrors', 5, 'Our listing'],
         ['ILLUCO Single', 'ILLUCO', 'Professional / student', '1 mirror with handle', '$19.99', 1, None, 3.4, 3, None, '#30 Dental Mirrors (orphan)', 4, 'Our listing'],
         ['ILLUCO Photo', 'ILLUCO', 'Photo mirror (premium)', 'Double-sided photo mirror', '$165.00', 1, None, None, 0, None, '#462 Dental Mirrors', 5, 'Our listing']]
table(cp, ['ASIN', 'Brand', 'Segment', 'Title (truncated)', 'Price', 'Units per pack', 'Price per unit', 'Rating', 'Ratings', 'Bought past month',
           'BSR', 'Gallery images', 'What they do / note'], crow, [12, 14, 16, 45, 9, 8, 9, 7, 8, 10, 30, 8, 55])
for i in range(2, len(crow) + 2):
    c = cp[f'E{i}']
    if isinstance(c.value, str) and c.value.startswith('$'):
        c.value = float(c.value.replace('$', '').replace(',', '')); c.number_format = '$#,##0.00'
    cp[f'G{i}'] = f'=IFERROR(E{i}/F{i},"")'; cp[f'G{i}'].number_format = '$#,##0.00'; cp[f'G{i}'].font = BODY
for i in range(2, len(crow) + 2):
    a = cp[f'A{i}'].value
    if a and a.startswith('B0'): link(cp[f'A{i}'], dp(a))
ILL = {'ILLUCO 5-Pack': 'B0FCZBD1KY', 'ILLUCO Heads': 'B0FBPG5CS9', 'ILLUCO Single': 'B0G2DYRY7T', 'ILLUCO Photo': 'B0FCNG7T9P'}
for i in range(2, len(crow) + 2):
    a = cp[f'A{i}'].value
    if a in ILL: link(cp[f'A{i}'], dp(ILL[a]))
cp.cell(len(crow) + 3, 1, 'Source: amazon.com search results for "dental mirror", "front surface dental mirror", "dental photography mirror", "dental mirror replacement head", captured 2026-11-20. Units per pack read from titles; blank where the title does not say. Bought past month is Amazon\'s on-page badge.').font = Font(name=F, size=8, italic=True)

# ---------------- Keywords ----------------
kw = wb.create_sheet('Keywords')
K = [
 ('dental mirror', 'Amazon autocomplete + top competitor term', 'Broad (mixed consumer/pro)', 'All', 'Title, PPC Phrase (with negatives)'),
 ('dental mirrors', 'Autocomplete', 'Broad', 'All', 'Backend, PPC Phrase'),
 ('mouth mirror', 'Autocomplete + competitor titles', 'Professional', '5-pack, single, heads', 'Bullets, Backend, PPC Exact'),
 ('mouth mirror dental', 'Autocomplete', 'Professional', '5-pack, single', 'PPC Exact'),
 ('mouth mirror heads', 'Autocomplete', 'Professional (replacement)', 'Heads', 'Title-adjacent, PPC Exact'),
 ('dental mirrors #4', 'Autocomplete', 'Professional', '5-pack, heads, single', 'Backend ("number 4"), PPC Exact'),
 ('dental mirrors double sided', 'Autocomplete', 'Professional', 'Double-Sided (new)', 'Title, PPC Exact'),
 ('dental mirror anti fog', 'Autocomplete', 'Mixed', 'All mouth mirrors', 'Backend ("anti fog"), PPC Phrase'),
 ('front surface dental mirror', 'Competitor titles (Hu-Friedy, Artman, SurgiMac)', 'Professional', 'All', 'Highlight, Bullets, PPC Exact'),
 ('front surface mirror dental', 'Autocomplete', 'Professional', 'All', 'PPC Exact'),
 ('cone socket mirror', 'Competitor titles', 'Professional (replacement)', 'Heads, 5-pack', 'Title (heads), PPC Exact'),
 ('dental photography mirrors', 'Autocomplete', 'Photo', 'Photo mirror', 'Title, PPC Exact'),
 ('dental photography mirror anti fog', 'Autocomplete', 'Photo', 'Photo mirror', 'Backend, PPC Phrase'),
 ('dental photography mirrors fog free', 'Autocomplete', 'Photo', 'Photo mirror', 'PPC Exact'),
 ('intraoral mirror', 'Competitor titles', 'Photo', 'Photo mirror', 'Highlight, Backend'),
 ('occlusal mirror', 'Competitor titles', 'Photo', 'Photo mirror (occlusal)', 'Title per variant, PPC Exact'),
 ('dental mirrors for photos', 'Autocomplete', 'Photo', 'Photo mirror', 'PPC Phrase'),
 ('large mouth mirror', 'ILLUCO Grand file', 'Professional', 'Grand (new)', 'Backend, PPC Exact'),
 ('magnifying dental mirror', 'Category gap (no competitor owns it)', 'Professional', '2X/3X variants', 'Bullets, PPC Exact'),
 ('dental mirror with light', 'Autocomplete', 'CONSUMER (LED)', 'None', 'NEGATIVE on pro campaigns'),
 ('dental mirrors for home use', 'Autocomplete', 'CONSUMER', 'Single only', 'NEGATIVE on 5-pack/heads; test on single'),
 ('dental mirror disposable / plastic', 'Autocomplete', 'CONSUMER / bulk disposable', 'None', 'NEGATIVE'),
 ('dental mirror and pick set', 'Autocomplete', 'CONSUMER', 'None', 'NEGATIVE'),
 ('dental mirror for teeth', 'Autocomplete', 'CONSUMER', 'Single only', 'NEGATIVE on 5-pack/heads'),
 ('mouth mirrors classroom', 'Autocomplete', 'Education (kids)', 'None', 'NEGATIVE'),
]
table(kw, ['Keyword', 'Source', 'Intent / segment', 'ILLUCO family', 'Placement'], K, [34, 40, 26, 26, 40])
kw.cell(len(K) + 3, 1, 'Search volume is not available from public data. Add Brand Analytics > Search Query Performance (search volume, click and purchase share) for each keyword in a new column before final bid decisions.').font = Font(name=F, size=8, italic=True)

# ---------------- PPC ----------------
pp = wb.create_sheet('PPC Plan')
pp.cell(1, 1, 'Break-even and bid calculator (inputs in yellow - replace placeholder assumptions with your margin and Ads data)').font = Font(name=F, bold=True, size=11)
calc_hdr = ['Family', 'Avg price ($)', 'Margin before ads (%)', 'Expected CVR (%)', 'Target ACoS (% of margin)', 'Break-even ACoS', 'Target ACoS', 'Max CPC ($)', 'Daily clicks wanted', 'Daily budget ($)', 'Expected market CPC ($)']
calc = [['5-Pack with Handles', 120, 0.55, 0.031, 0.6], ['Replacement Heads', 85, 0.6, 0.109, 0.6], ['Single Mirror', 27, 0.5, 0.124, 0.6],
        ['Photo Mirror', 165, 0.6, 0.05, 0.6], ['Grand + Double-Sided (launch)', 150, 0.55, 0.06, 0.9]]
for j, h in enumerate(calc_hdr, 1):
    c = pp.cell(3, j, h); c.font = HFONT; c.fill = HFILL; c.alignment = Alignment(wrap_text=True)
for i, row in enumerate(calc, 4):
    for j, v in enumerate(row, 1):
        c = pp.cell(i, j, v); c.font = BLUE if j > 1 else BODY; c.border = BOX
        if j > 1: c.fill = INFILL
    pp.cell(i, 2).number_format = '$#,##0'
    for col in 'CDE': pp[f'{col}{i}'].number_format = '0%'
    pp[f'F{i}'] = f'=C{i}'; pp[f'G{i}'] = f'=C{i}*E{i}'; pp[f'H{i}'] = f'=B{i}*D{i}*G{i}'
    pp[f'I{i}'] = [10, 8, 10, 5, 15][i - 4]; pp[f'I{i}'].font = BLUE; pp[f'I{i}'].fill = INFILL
    pp[f'K{i}'] = 1.34; pp[f'K{i}'].font = BLUE; pp[f'K{i}'].fill = INFILL; pp[f'K{i}'].number_format = '$#,##0.00'
    pp[f'J{i}'] = f'=MIN(H{i},K{i})*I{i}'
    for col in 'FG': pp[f'{col}{i}'].number_format = '0.0%'
    for col in 'HJ': pp[f'{col}{i}'].number_format = '$#,##0.00'
    for col in 'FGHJ': pp[f'{col}{i}'].font = BODY
pp['A9'] = 'Total daily budget (ON HOLD by owner 11/20 - reference only)'; pp['A9'].font = Font(name=F, bold=True)
pp['J9'] = '=SUM(J4:J8)'; pp['J9'].number_format = '$#,##0.00'; pp['J9'].font = Font(name=F, bold=True)
pp['A10'] = ('Prices = current Amazon averages; CVR = Business Report 11/20 unit session % per family (launch row assumed); market CPC = $1.34 average from the SP campaign report (Aug 1-Nov 20). Margin and click targets are PLACEHOLDERS - '
             'replace margin with landed cost + FBA + referral fees, CVR with Business Report unit session %, and market CPC with the Ads search-term report. Budget = clicks x the lower of market CPC and Max CPC. Launch row uses 90% of margin as target ACoS to build initial reviews/rank.')
pp['A10'].font = Font(name=F, size=8, italic=True); pp['A10'].alignment = Alignment(wrap_text=True); pp.merge_cells('A10:K10'); pp.row_dimensions[10].height = 40
camp = [
 ['ILL | SP | Kit5 | Exact', 'SP manual', '5-Pack', 'Exact: front surface dental mirror, mouth mirror, dental mirrors #4, magnifying dental mirror', 'Proven converters; bid to Max CPC'],
 ['ILL | SP | Kit5 | Phrase', 'SP manual', '5-Pack', 'Phrase: dental mirror, mouth mirror dental, dental mirror anti fog', 'Discovery; harvest winners to Exact weekly'],
 ['ILL | SP | Heads | Exact', 'SP manual', 'Heads', 'Exact: mouth mirror heads, dental mirror replacement head, cone socket mirror', 'Replacement intent'],
 ['ILL | SP | Single | Phrase', 'SP manual', 'Single', 'Phrase: dental mirror, dental mirror for dental students', 'Entry product; allow some consumer traffic'],
 ['ILL | SP | Photo | Exact', 'SP manual', 'Photo', 'Exact: dental photography mirrors, occlusal mirror, intraoral mirror', 'Low volume, high intent'],
 ['ILL | SP | ALL | Auto', 'SP auto', 'All (ad groups per family)', 'Close + substitutes on; loose + complements low bids', 'Research only; negate consumer terms'],
 ['ILL | SP | PAT | Competitors', 'SP product targeting', '5-Pack, Heads', 'Hu-Friedy B0769MYHBB, Zirc B0D7QSSQ3F, Artman B077T1DWDR / B07NTGBDQW, SurgiMac B08FHCK6MR, Wise B0819456WP', 'Conquest premium buyers; lead with 99% vs 60-70%'],
 ['ILL | SP | PAT | Photo comps', 'SP product targeting', 'Photo', 'Ceonam B0CQ5GJQ3H, faruijie B09T37FZ6X, Dentasop B0BFR5V1W5', 'Ceonam reviews complain of breakage and scratching - our durability angle'],
 ['ILL | SP | Brand defense', 'SP manual', 'All', 'Exact: illuco, illuco dental mirror, illuco mirror', 'Cheap; protects branded traffic from Google/social'],
 ['ILL | SB | Store spotlight', 'Sponsored Brands', 'All', 'Exact: front surface dental mirror, dental mirrors professional', 'Needs the rebuilt store'],
 ['ILL | SBV | Reflectance demo', 'Sponsored Brands Video', '5-Pack', 'Phrase: dental mirror, mouth mirror', 'Needs the 15-30s side-by-side video'],
 ['NEGATIVES (shared list)', 'All pro campaigns', '-', 'with light, led, light up, home use, for kids, classroom, disposable, plastic, pick, plaque, tartar, hand mirror, makeup, telescoping, inspection mirror car, mechanic', 'Apply to 5-pack, heads, photo'],
]
for j, h in enumerate(['Campaign', 'Type', 'Family', 'Targeting', 'Purpose / note'], 1):
    c = pp.cell(12, j, h); c.font = HFONT; c.fill = HFILL
for i, row in enumerate(camp, 13):
    for j, v in enumerate(row, 1):
        c = pp.cell(i, j, v); c.font = BODY; c.alignment = Alignment(wrap_text=True, vertical='top'); c.border = BOX
for col, w in zip('ABCDEFGHIJK', (30, 18, 16, 60, 45, 12, 12, 12, 12, 14, 12)):
    pp.column_dimensions[col].width = w
audit = ['AUDIT CHECKLIST (run on the 60-day bulk sheet + search-term report)',
         '1. Wasted spend: search terms with spend > 1.5x target CPA and 0 orders -> negative exact.',
         '2. Consumer leakage: spend on terms containing light/led/home/kids/plastic/disposable -> negative phrase.',
         '3. Cannibalisation: same keyword in several campaigns -> keep the best ACoS, pause the rest.',
         '4. Converters stuck in Auto/Broad: orders >= 2 -> add as Exact, negate in the source campaign.',
         '5. Placement: compare Top of Search vs Rest of Search ACoS; set TOS modifier where TOS ACoS is lower.',
         '6. Budget caps: campaigns out of budget before 6pm with ACoS under target -> raise (after approval).']
for k, t in enumerate(audit):
    c = pp.cell(27 + k, 1, t); c.font = Font(name=F, size=9, bold=(k == 0))
_camp = list(_csv.DictReader(_io.StringIO(open('data/account/CHECK-_ILLUCO_3.csv', 'rb').read().decode('utf-8-sig'))))
base = 35
pp.cell(base, 1, 'CURRENT SPONSORED PRODUCTS CAMPAIGNS (Aug 1 - Nov 20, 2026; no Sponsored Brands or DSP running)').font = Font(name=F, bold=True, size=10)
cols = ['Campaign Name', 'Status', 'Budget Amount', 'Targeting Type', 'Impressions', 'Clicks', 'Spend', '7 Day Total Orders (#)', '7 Day Total Sales ']
for j, h in enumerate(['Campaign', 'Status', 'Daily budget', 'Targeting', 'Impressions', 'Clicks', 'Spend ($)', 'Orders', 'Sales ($)', 'ACoS', 'Conversion'], 1):
    c = pp.cell(base + 1, j, h); c.font = HFONT; c.fill = HFILL
for i, r in enumerate(_camp, base + 2):
    for j, k in enumerate(cols, 1):
        v = r[k]
        if j >= 5:
            v = _num(v)
        c = pp.cell(i, j, v); c.font = BODY; c.border = BOX
    pp.cell(i, 7).number_format = '$#,##0'; pp.cell(i, 9).number_format = '$#,##0'
    pp.cell(i, 10, f'=IFERROR(G{i}/I{i},"")').number_format = '0.0%'
    pp.cell(i, 11, f'=IFERROR(H{i}/F{i},"")').number_format = '0.0%'
end_ = base + 1 + len(_camp)
tr = end_ + 1
pp.cell(tr, 1, 'Total').font = Font(name=F, bold=True)
for col in 'EFGHI':
    pp[f'{col}{tr}'] = f'=SUM({col}{base+2}:{col}{end_})'; pp[f'{col}{tr}'].font = Font(name=F, bold=True)
pp[f'G{tr}'].number_format = '$#,##0'; pp[f'I{tr}'].number_format = '$#,##0'
pp[f'J{tr}'] = f'=IFERROR(G{tr}/I{tr},"")'; pp[f'J{tr}'].number_format = '0.0%'
pp[f'K{tr}'] = f'=IFERROR(H{tr}/F{tr},"")'; pp[f'K{tr}'].number_format = '0.0%'
pp.cell(tr + 1, 1, 'Source: CHECK-_ILLUCO_3.csv (SP campaign report). Pauses, negatives and harvests: PPC Apply tab.').font = Font(name=F, size=8, italic=True)

# ---------------- Creative plan ----------------
cr = wb.create_sheet('Images A+ Video')
crs = [
 ['All mouth mirrors', 'Image slot 1 (main)', 'Pure white; show exact count in the pack (5 or 1); no text', 'OK on 5-pack; single 3X orphan main shows the head in profile - reshoot'],
 ['All mouth mirrors', 'Image 2', '"What\'s in the box": count callout (x5 heads, x5 handles, care guide / x1 for single)', 'Single listings currently show FIVE mirrors here - replace first'],
 ['All mouth mirrors', 'Image 3', 'Side-by-side real photo: ILLUCO vs standard mirror under the same operatory light (99% vs 60-70%)', 'Missing - strongest proof of the price premium'],
 ['All mouth mirrors', 'Image 4', 'Magnification guide: 1X / 2X / 3X field of view + working distance; who each is for', 'Current "Choose your magnification" uses cartoon gums and no field-of-view guidance'],
 ['All mouth mirrors', 'Image 5', 'Size and fit: Size 4 = 22 mm head, cone socket thread, handle length', 'Missing'],
 ['All mouth mirrors', 'Image 6', 'Water-repellent demo: droplets beading off; honest "resists fog" wording', 'Missing'],
 ['All mouth mirrors', 'Image 7', 'Care card led by the 5-minute autoclave at 273°F (134°C) as a time saver; warning that longer / 20-minute cycles strip the coating; 100+ cycles on the 5-minute setting', 'Today the instructions are tiny; over-autoclaving causes the bad reviews (sales team)'],
 ['All mouth mirrors', 'Image 8 (lifestyle)', 'Clinician with loupes + headlight (ILLUCO cross-sell) in a real operatory', 'Only the orphan 1X listing has a gloved-hand photo'],
 ['Heads', 'Image 2', 'Compatibility chart: cone socket YES / simple stem NO / EU thread NO', 'Missing - likely 1-star driver'],
 ['Photo mirror', 'Image 2', 'Dimension drawing WITH units (mm) for every shape', 'Current drawing has numbers without units'],
 ['Photo mirror', 'Image 3', 'Before/after intraoral photo: ILLUCO vs rhodium reflector (ghosting)', 'Missing'],
 ['A+ (all mirrors)', 'Module 1', 'Brand banner: "Brighter view. Less fatigue." + ILLUCO clinical photo', 'Basic A+ today: 3 images, no comparison chart'],
 ['A+ (all mirrors)', 'Module 2', 'Comparison chart across the line: 5-pack, heads, single, Double-Sided, Grand, photo mirror (size, faces, magnification, handle, pack, best for)', 'Missing; essential once Grand and Double-Sided launch'],
 ['A+ (all mirrors)', 'Module 3', 'Reflectance comparison: standard vs ILLUCO dielectric (only claims you can document)', ''],
 ['A+ (all mirrors)', 'Module 4', 'Magnification and compatibility guide', ''],
 ['A+ (all mirrors)', 'Mobile check', 'Text >= 30 px on a 970 px module; use A+ text fields, not text baked into images', 'Current infographic text is ~11 px at phone size'],
 ['Video', 'V1 (45-60s, listing)', 'Unboxing + reflectance side-by-side + water bead test + magnification demo + autoclave', '5-pack has a video; single, heads and photo have none'],
 ['Video', 'V2 (15-30s, SBV)', 'Hook in 2s: split-screen dull vs bright mirror; end card "99% reflectance"', 'For Sponsored Brands Video'],
 ['Video', 'V3 (30s, photo mirror)', 'Intraoral photo with ILLUCO vs standard reflector, no ghosting', ''],
 ['Video', 'V4 (20s, heads)', 'How to swap a cone socket head; what it fits', 'Pre-empts fit complaints'],
]
table(cr, ['Scope', 'Slot / module', 'Recommended content', 'Current gap found'], crs, [20, 20, 80, 60])

# ---------------- External traffic ----------------
ex = wb.create_sheet('External Traffic')
exr = [
 ['Google Ads - Search', 'Chiru', 'Exact/phrase: front surface dental mirror, dental mirror heads cone socket, dental photography mirror, ILLUCO brand', 'Amazon Attribution tag per ad group; Brand Referral Bonus enrolled', 'Attributed DPV, add-to-cart, purchases; ROAS incl. ~10% referral bonus'],
 ['Google Ads - Shopping', 'Chiru', 'Shopping ads cannot point to Amazon pages (Merchant Center requires your own domain) -> run Shopping to illuco.com', 'Keep separate from Amazon budget', 'illuco.com ROAS'],
 ['Social - IG / FB / TikTok / YouTube', 'Shery', 'Reflectance side-by-side, water-bead test, "mirror under loupes" POV, autoclave durability, dental-student tips', 'One Attribution tag per platform; link in bio to the Amazon store page', 'Clicks, attributed sales, follower growth'],
 ['Creators - RDH, dental students, cosmetic/ortho dentists', 'Annabelle / Shery', 'Seed 15-20 creators with kits; photo mirror to cosmetic/ortho photographers; FTC #ad disclosure', 'Unique Attribution tag per creator; Amazon Creator Connections for commission', 'Attributed sales per creator; content reused in ads'],
 ['Amazon Attribution', 'Cenk', 'Create tags: channel_source_campaign_creative (e.g. google_search_frontsurface_v1)', 'Set up before any external spend', 'Weekly report'],
 ['Promotions', 'Cenk (approval needed)', 'Coupon 10-15% on 5-pack and heads for BFCM (11/27-11/30); Amazon Business quantity pricing for clinics; Subscribe & Save test on heads (illuco.com already offers 10% S&S)', 'Respect price parity with illuco.com', 'Conversion rate during the promo vs the 30 days before'],
 ['Reviews (compliant)', 'Cenk', 'Enroll every parent in Vine (up to 30 units); use "Request a Review" on all orders; no incentives tied to reviews', 'Starts after the listing fixes go live', 'Rating and review count per family'],
]
table(ex, ['Channel', 'Owner', 'What to run', 'Tracking', 'KPI'], exr, [30, 16, 70, 45, 40])

# ---------------- Action plan ----------------
ap = wb.create_sheet('Action Plan')
apr = [
 ['Nov 20', 'Claudia reads the new copy', 'Cenk / sales team', 'Listing Copy tab', 'Not started'],
 ['Nov 20', 'Upload ILLUCO_Amazon_UPLOAD.xlsx (2 families, new copy, new products; Amazon prices unchanged)', 'Cenk', 'Upload Check tab', 'Not started'],
 ['Nov 20', 'Seller Support: merge B0GGDQ15DD into B0G2DYRY7T; re-classify dermatoscopes', 'Cenk', 'What I Need tab', 'Not started'],
 ['Nov 21', 'Images go up with the upload (8 per child); then make the GitHub repo private', 'Cenk', 'Image Kit tab', 'Not started'],
 ['Nov 21', 'Apply negatives and harvests from the PPC audit (no budget change)', 'Cenk', 'PPC Apply tab', 'Not started'],
 ['Nov 21', 'Supplier: top-coat durability and test reports', 'Cenk', '', 'Not started'],
 ['Nov 21', 'Answer NCX flag; Vine for both family parents; Request a Review on all orders', 'Cenk', '', 'Not started'],
 ['Nov 24', 'Check processing report; confirm both families render on amazon.com', 'Cenk', '', 'Not started'],
 ['Dec 1', 'Compare 5-pack conversion before vs after the new copy and images', 'Cenk', 'ASIN Report tab', 'Not started'],
 ['On hold', 'Black Friday coupon and PPC budget increase', 'Manager', 'PPC Plan tab', 'Blocked'],
 ['Later', 'Store rebuild, A+ comparison chart, video, Google / social / creators with Attribution', 'Design, Chiru, Shery, Annabelle', 'External Traffic tab', 'Not started'],
]
table(ap, ['Date', 'Task', 'Owner', 'Reference', 'Status'], apr, [11, 85, 18, 38, 12])
dv3 = DataValidation(type='list', formula1='"Not started,In progress,Done,Blocked"', allow_blank=True); ap.add_data_validation(dv3); dv3.add(f'E2:E{len(apr)+1}')

# ---------------- What I need ----------------
dn = wb.create_sheet('What I Need', 1)
from links import NEEDS
dn.cell(1, 1, 'What I need to finish the audit and apply the updates (click the links; Seller Central and Ads links open after you sign in)').font = Font(name=F, bold=True, size=11)
rows_ = [[i, t, w, where, None, why, by, ''] for i, (t, w, where, url, why, by) in enumerate(NEEDS, 1)]
table(dn, ['#', 'Type', 'What I need', 'Where to find it', 'Link', 'Why', 'Needed by', 'Done? (Y)'], rows_, [4, 9, 60, 42, 16, 36, 11, 9], start=2, input_cols=(8,))
for i, (t, w, where, url, why, by) in enumerate(NEEDS, 3):
    if url: link(dn.cell(i, 5), url, 'Open')
dn.freeze_panes = 'C3'
from links import RECEIVED
rb = len(NEEDS) + 5
dn.cell(rb, 1, 'Already received 11/20 - thank you').font = Font(name=F, bold=True, size=11)
for k, (what, src) in enumerate(RECEIVED, 1):
    dn.cell(rb + k, 2, 'Done').font = Font(name=F, size=9, color='008000', bold=True)
    dn.cell(rb + k, 3, what).font = BODY
    dn.cell(rb + k, 4, src).font = BODY

# ================= consolidated tabs (one report instead of many files) =================
import csv as _c2
from existing_listing_content import ROWS as _ROWS, ATTRIBUTE_FIXES as _FIX
from openpyxl.utils import get_column_letter as _gcl

def _csv(path):
    return list(_c2.DictReader(open(path, encoding='utf-8')))

def _style_block(ws, first_row, last_row, ncols, wrap=True):
    for r_ in range(first_row, last_row + 1):
        for c_ in range(1, ncols + 1):
            cell = ws.cell(r_, c_)
            if cell.font is None or not cell.font.bold:
                cell.font = BODY
            cell.alignment = Alignment(wrap_text=wrap, vertical='top')

# ---- Upload Check ----
uc = wb.create_sheet('Upload Check', 3)
uc.cell(1, 1, 'ILLUCO_Amazon_UPLOAD.xlsx - what it contains and the pre-upload check').font = Font(name=F, bold=True, size=12)
rows_up = _csv('data/build/upload_rows.csv')
# same order as the upload: each parent and its children, one family per pack size (owner, 11/23)
sections = [('5PK', 'IDM-5PACK-FAMILY-PARENT: ILLUCO UHD Dental Mirrors with Handles, 5 Pack, and its children'),
            ('SINGLE', 'IDM-SINGLE-FAMILY-PARENT: ILLUCO UHD Dental Mirror with Handle, 1 Pack, and its children'),
            ('GRAND', 'IDM-GRAND-FAMILY-PARENT: ILLUCO Grand UHD Dental Mirrors with Handles, 2 Pack, and its children'),
            ('HEADS', 'IDM-HEADS-FAMILY-PARENT: ILLUCO UHD Dental Mirror Heads, 5 Pack, and its children'),
            ('-', 'Not in the upload')]
TYPE = {'1 parent': 'PARENT', '2 new child': 'Child (new product): its UPC needs brand ILLUCO in GS1', '3 existing child': 'Child (existing listing)',
        '4 not re-parented': 'Seller Support case'}
uc.cell(2, 1, 'Step 1: upload ILLUCO_Amazon_STEP1_delete_parent.xlsx (1 row): it deletes IDM-HANDLE-FAMILY-PARENT, the 11/21 '
              'family that mixed pack sizes; its listings keep their ASINs, reviews and stock. Step 2: when its processing report is '
              'back, upload ILLUCO_Amazon_UPLOAD.xlsx. It sends no images; yellow main-image cells need a new main (Image List tab).'
              ).font = Font(name=F, size=10, bold=True)
r0 = 3
for key, label in sections:
    items = [x for x in rows_up if x['family'] == key]
    uc.cell(r0, 1, f'{label}: {len(items)} rows').font = Font(name=F, bold=True, size=10)
    r0 += 1
    for j, h in enumerate(['Type', 'SKU', 'ASIN', 'Size value', 'Color', 'Items', 'Action', 'Amazon price now', 'Price in upload', 'Note'], 1):
        c = uc.cell(r0, j, h); c.font = HFONT; c.fill = HFILL
    for x in items:
        r0 += 1
        is_parent = x['section'] == '1 parent'
        vals = [TYPE[x['section']], x['sku'], x['asin'], x['size'], x['color'], x['items'], x['action'], x['price_old'], x['price_new'], x['note']]
        for j, v in enumerate(vals, 1):
            c = uc.cell(r0, j, v); c.font = Font(name=F, size=10, bold=is_parent); c.alignment = Alignment(wrap_text=True, vertical='top'); c.border = BOX
            if is_parent:
                c.fill = PatternFill(fill_type='solid', fgColor='DDEBF7')
        if not is_parent:
            uc.cell(r0, 2).alignment = Alignment(vertical='top', indent=2)
        if x['asin'].startswith('B0'):
            link(uc.cell(r0, 3), dp(x['asin']))
    r0 += 2
chk = _csv('data/build/upload_check.csv')
import os as _os
chk_new = _csv('data/build/upload_check_new_products.csv') if _os.path.exists('data/build/upload_check_new_products.csv') else []
for _x in chk_new:
    _x['sku'] = _x['sku'] + ' (new products file)'
uc.cell(r0, 1, f"Automated check against the template's own rules: {sum(1 for x in chk if x['level']=='ERROR')} errors, "
               f"{sum(1 for x in chk if x['level']=='WARN')} warnings (dropdown values, required fields, parent/child themes, unique "
               "variations, text limits, UPC check digits, prices, image URLs). Amazon's own review rejected the 7 new UPCs on 11/20: "
               "GS1 lists their brand as IDM SERIES, so they pass once Korea changes it to ILLUCO.").font = Font(name=F, bold=True, size=10)
chk = chk + chk_new
chk_s1 = _csv('data/build/upload_check_step1.csv') if _os.path.exists('data/build/upload_check_step1.csv') else []
for _x in chk_s1:
    _x['sku'] = _x['sku'] + ' (step 1 file)'
chk = chk + chk_s1
r0 += 1
for j, h in enumerate(['Level', 'Row', 'SKU', 'Column', 'Issue'], 1):
    c = uc.cell(r0, j, h); c.font = HFONT; c.fill = HFILL
for x in chk:
    r0 += 1
    for j, k in enumerate(['level', 'row', 'sku', 'column', 'issue'], 1):
        c = uc.cell(r0, j, x[k]); c.font = BODY; c.border = BOX; c.alignment = Alignment(wrap_text=True, vertical='top')
r0 += 2
uc.cell(r0, 1, 'Only Amazon can check these (the processing report shows them after upload):').font = Font(name=F, bold=True, size=10)
for k, txt in enumerate(['The live listings use product type PROFESSIONAL_HEALTHCARE (if a row says "product type mismatch", change column B for that row to the type shown on the Edit listing page)',
                         'The 7 new UPCs are registered to ILLUCO in GS1'], 1):
    uc.cell(r0 + k, 1, f'{k}. {txt}').font = BODY
s1_rows = _csv('data/build/step1_mains.csv')
r0 += len(['', '']) + 2
uc.cell(r0, 1, f'Step 1 file, ILLUCO_Amazon_STEP1_delete_parent.xlsx: {1 + len(s1_rows)} rows').font = Font(name=F, bold=True, size=10)
r0 += 1
for j, h in enumerate(['Action', 'SKU', 'ASIN', 'New main image'], 1):
    c = uc.cell(r0, j, h); c.font = HFONT; c.fill = HFILL
r0 += 1
for j, v in enumerate(['Delete', 'IDM-HANDLE-FAMILY-PARENT', '(parent)', 'Its listings join the new families in step 2'], 1):
    c = uc.cell(r0, j, v); c.font = BODY; c.border = BOX
for x in s1_rows:
    r0 += 1
    for j, v in enumerate(['Edit (Partial Update): main image only', x['sku'], x['asin'], x['main_url'].split('/image_kit/')[-1]], 1):
        c = uc.cell(r0, j, v); c.font = BODY; c.border = BOX
    link(uc.cell(r0, 3), dp(x['asin']))
for col, wdt in zip('ABCDEFGHIJ', (22, 30, 13, 28, 11, 6, 30, 12, 12, 60)):
    uc.column_dimensions[col].width = wdt

# ---- Listing Copy ----
lc = wb.create_sheet('Listing Copy', 4)
lhdr = ['ASIN', 'Family', 'Mag', 'Color', 'Current title (live)', 'NEW title', 'Chars', 'NEW Item Highlight', 'Bullet 1', 'Bullet 2',
        'Bullet 3', 'Bullet 4', 'Bullet 5', 'Description', 'Backend keywords', 'Model no.', 'SKU(s)', 'Price', 'New family / size value', 'Note']
lrows = []
LC_FAM = {'5-Pack with Handles': '5 Pack family', 'Single Mirror with Handle': '1 Pack family',
          'Replacement Heads 5-Pack': 'Heads family'}
def _lc_key(rr):   # same order as the upload: 5 Pack family, 1 Pack family, heads family, duplicate last
    if rr['asin'] == 'B0GGDQ15DD':
        return (9, 0, 0, 0)
    sub = 0 if ('5' in rr['family'] and 'Pack' in rr['family'] and rr['new_family'] == 'A') else 1
    return (0 if rr['new_family'] == 'A' else 1, sub, rr['mag'], 0 if rr['color'] == 'Light Blue' else 1)
for rr in sorted(_ROWS, key=_lc_key):
    live = cat.get(rr['asin'], {})
    lrows.append([rr['asin'], rr['family'], f"{rr['mag']}X", rr['color'], live.get('title'), rr['title'], len(rr['title']), rr['highlight'],
                  *rr['bullets'], rr['description'], rr['keywords'], rr['model_suggested'],
                  ', '.join(k + (' (inferred)' if v == 'inferred' else '') for k, v in rr['skus']), 'unchanged',
                  ('Merge into B0G2DYRY7T (Seller Support)' if rr['asin'] == 'B0GGDQ15DD' else
                   f"{LC_FAM[rr['family']]} / {rr['var_size']}"), rr['note']])
table(lc, lhdr, lrows, [12, 18, 5, 10, 40, 40, 6, 40, 50, 50, 50, 50, 50, 60, 40, 15, 22, 8, 26, 40])
for i in range(2, len(lrows) + 2):
    link(lc[f'A{i}'], dp(lc[f'A{i}'].value)); lc[f'R{i}'].number_format = '$#,##0.00'
n_ = len(lrows) + 3
lc.cell(n_, 1, 'Attribute fixes (not in the upload; Seller Support or Edit listing)').font = Font(name=F, bold=True)
for k, x in enumerate(_FIX, 1):
    for j, v in enumerate(x, 1):
        c = lc.cell(n_ + k, j, v); c.font = BODY; c.alignment = Alignment(wrap_text=True, vertical='top')
lc.cell(n_ + len(_FIX) + 2, 1, 'New Grand / Double-Sided / heads copy is in the upload file itself (the rows with Listing Action "Create or Replace").').font = Font(name=F, size=8, italic=True)

# ---- Sales Direction ----
sd = wb.create_sheet('Sales Direction', 5)
sd.cell(1, 1, 'Sales direction (Claudia, Nov 20) and where it is applied - use as the brief for Ashley').font = Font(name=F, bold=True, size=12)
sdr = [
 ['Lead with HIGH DEFINITION; fog resistance is secondary', 'Every Item Highlight starts "Ultra High Definition"; bullet 1 = "Ultra High Definition View"; fog / anti-fog removed from titles and highlights', 'Upload: all rows; image kit slot 3'],
 ['2X and 3X are the premium, new feature; 1X is basic', '2X/3X titles start "ILLUCO UHD 2X Magnifying ..."; bullet 2 = "2X Magnification, a Premium Upgrade: most mouth mirrors are 1X"; parent titles list the magnifications on offer', 'Upload: titles + bullet 2; image kit slot 4'],
 ['5-minute autoclave at 273°F is a time saver and must be prominent', 'Bullet "5-Minute Autoclave Saves Time" on every product; description care paragraph; image kit care card leads with 5 minutes', 'Upload: bullet 3; image kit slot 7'],
 ['Standard 20-minute cycles cook off the coating (cause of the bad reviews)', 'Copy says: do not use the standard 20-minute cycle at 273°F or any setting above 277°F (136°C); 20 min at 250°F (121°C) stays as the alternative', 'Upload: bullet 3 + description'],
 ['"100+ autoclave cycles", not "100"; the mirror still works after the coating life', '"On the 5-minute setting the coating is rated for 100+ cycles, and the mirror stays usable after that"; highlight "100+ Cycles"', 'Upload: bullet 3, highlight, description'],
 ['Instructions are almost hidden', 'Recommended: bigger in-box instruction card; upload the care card PDF as "Instructions for Use" (column IK of the template) so it shows under Product guides and documents; A+ module on the 5-minute autoclave', 'Next step (needs a hosted PDF)'],
 ['Interact with customers', 'Amazon removed contacting customers about critical reviews (Customer Reviews page notice); respond when customers message first, answer on social media, and fix the cause through the instruction card and copy', 'Process'],
]
table(sd, ['What sales said', 'How it is applied', 'Where'], sdr, [48, 90, 34], start=3)

# ---- PPC Apply (pauses, negatives, harvest) ----
pa = wb.create_sheet('PPC Apply')
pa.cell(1, 1, 'Apply in Campaign manager - no budget changes. Tick Done as you go.').font = Font(name=F, bold=True, size=12)
PAUSES = [('BRAND-KW', 'dental', 'Phrase', '$191 spend, 2 orders; 92% went to handpieces, loupes, drills, materials'),
          ('BRAND-KW', 'dental tools home use', 'Broad', '$168 spend, 2 orders; consumer intent'),
          ('BRAND-KW', 'dental hygienist must haves', 'Exact', '$16 spend, 0 orders'),
          ('HEADS-KW', 'dental mirror', 'Broad', '$8.55, 0 orders (the converting PHRASE keyword stays on)'),
          ('DERM', 'dermatoscope otoscopes & ophthalmoscopes', 'Broad', 'Off-target, 0 orders'),
          ('DERM', 'dermatoscope iphone', 'any', 'Phone-attachment search'),
          ('DERM', 'smartphone dermatoscope', 'any', 'Phone-attachment search'),
          ('DERM', 'dermatoscope for smart phone', 'any', 'Phone-attachment search'),
          ('DERM', 'dermatoscope attachment for iphone', 'any', 'Phone-attachment search')]
pa.cell(3, 1, '1. PAUSE these keywords (ad group > Targeting tab > switch off)').font = Font(name=F, bold=True)
for j, h in enumerate(['Done', 'Campaign', 'Keyword', 'Match', 'Why'], 1):
    c = pa.cell(4, j, h); c.font = HFONT; c.fill = HFILL
for i, (cmp, kw_, mt, why) in enumerate(PAUSES, 5):
    for j, v in enumerate(['', cmp, kw_, mt, why], 1):
        c = pa.cell(i, j, v); c.font = BODY; c.border = BOX
    pa.cell(i, 1).fill = INFILL
r_ = 5 + len(PAUSES) + 1
pa.cell(r_, 1, '2. ADD NEGATIVES (ad group > Negative targeting > Add negative keywords / products). Copy a block from column C and paste it.').font = Font(name=F, bold=True)
negs = _csv('analysis/negative_keywords.csv')
SHORT = {'VIC-M-SP-Dental Mirror Branded and Product KW': 'BRAND-KW',
         'VIC-BOF | SP | Dental Mirror HEAD 1x 2x 3x | SP Exact Target + Prod Exp + Brand Exp': 'HEADS-KW',
         'VIC-M- SP | Dental Mirror Category | Dental Mirror | All Single Multipack': 'CATEGORY',
         'VIC-SP-AUTO-DTMR-1PK-ALL': 'AUTO-1PK', 'VIC-SP-AUTO-MRHD-5PK-ALL': 'AUTO-HEADS', 'SP-Dermatoscope-KWs-All': 'DERM'}
from collections import OrderedDict as _OD
grp = _OD()
for x in negs:
    grp.setdefault((SHORT[x['campaign']], x['campaign'], x['ad_group'], x['match_type']), []).append(x)
r_ += 1
for (short, cmp, ag, mt), items in grp.items():
    r_ += 1
    spent = sum(float(x['spend_to_date'] or 0) for x in items)
    c = pa.cell(r_, 1, 'Done?'); c.fill = INFILL; c.font = BODY
    pa.cell(r_, 2, f'{short} | {mt} | {len(items)} terms | ${spent:,.2f} spent, 0 orders').font = Font(name=F, bold=True, size=9)
    pa.cell(r_ + 1, 2, f'Campaign: {cmp}').font = Font(name=F, size=8, color='595959')
    pa.cell(r_ + 2, 2, f'Ad group: {ag}').font = Font(name=F, size=8, color='595959')
    for k, x in enumerate(items):
        pa.cell(r_ + 1 + k, 3, x['keyword']).font = Font(name=F, size=10)
    r_ += max(len(items), 2) + 1
r_ += 1
pa.cell(r_, 1, '3. MOVE PROVEN SEARCHES TO EXACT (harvest)').font = Font(name=F, bold=True)
hv = _csv('analysis/harvest_keywords.csv')
hcols = [k for k in hv[0].keys()] if hv else []
for j, h in enumerate(hcols, 1):
    c = pa.cell(r_ + 1, j, h); c.font = HFONT; c.fill = HFILL
for i, x in enumerate(hv, r_ + 2):
    for j, h in enumerate(hcols, 1):
        c = pa.cell(i, j, x[h]); c.font = BODY; c.alignment = Alignment(wrap_text=True, vertical='top')
for col, wdt in zip('ABCDEFGHI', (8, 60, 34, 10, 50, 12, 12, 26, 40)):
    pa.column_dimensions[col].width = wdt

# ---- Search Query Performance appended to Keywords ----
sq = _csv('analysis/sqp_top_queries.csv')
base_ = kw.max_row + 3
kw.cell(base_, 1, 'Search Query Performance (Brand Analytics) - top queries').font = Font(name=F, bold=True)
qcols = list(sq[0].keys()) if sq else []
for j, h in enumerate(qcols, 1):
    c = kw.cell(base_ + 1, j, h); c.font = HFONT; c.fill = HFILL; c.alignment = Alignment(wrap_text=True)
for i, x in enumerate(sq[:60], base_ + 2):
    for j, h in enumerate(qcols, 1):
        c = kw.cell(i, j, x[h]); c.font = BODY

# ---- Image Kit ----
ik = wb.create_sheet('Image Kit')
man = _csv('image_kit/manifest.csv')
mcols = list(man[0].keys())
table(ik, mcols, [[x[k] for k in mcols] for x in man], [10, 26, 40, 18, 46, 40, 16, 70])

# ---- Shopper Preview: exactly what every listing shows after the upload (owner, 11/21: approve before uploading) ----
sp = wb.create_sheet('Shopper Preview')
sp.cell(1, 1, 'Shopper Preview: what each listing shows after ILLUCO_Amazon_UPLOAD.xlsx is processed. '
              'Read-only check; nothing here changes Amazon.').font = Font(name=F, bold=True, size=12)
sp.cell(2, 1, 'Variations sit together only when they are the same product (one family per product line); anything else stays '
              'separate: photo mirrors, dermatoscopes, headlights and loupes are not touched. Each family holds one pack size '
              '(owner, 11/23), so shoppers pick Color and Size (heads: Size). Model is the product-details line; the IDM code is '
              'the Part Number.'
        ).font = Font(name=F, size=10, italic=True)
_up = openpyxl.load_workbook('ILLUCO_Amazon_UPLOAD.xlsx')['Template']
_plan = {x['sku'].replace(' (INFERRED)', ''): x for x in _csv('data/build/upload_rows.csv')}
_s1 = {x['sku']: x['main_url'] for x in _csv('data/build/step1_mains.csv')}
_miss = {(x['sku'], x['column']): x['meanwhile'] for x in _csv('data/build/missing_images.csv')}
sp_hdr = ['Family / listing', 'ASIN', 'SKU(s)', 'Title', 'Item Highlight', 'Size', 'Color', 'Number of Items', 'Model',
          'Part number', 'Main image', 'Status']
for j, h in enumerate(sp_hdr, 1):
    c = sp.cell(4, j, h); c.font = HFONT; c.fill = HFILL; c.border = BOX
_rows, _seen = [], {}
SP_FAM = {'IDM-5PACK-FAMILY-PARENT': '5 Pack', 'IDM-SINGLE-FAMILY-PARENT': '1 Pack', 'IDM-GRAND-FAMILY-PARENT': 'Grand 2 Pack',
          'IDM-HEADS-FAMILY-PARENT': 'Heads 5 Pack'}
for r in range(8, _up.max_row + 1):
    sku = _up[f'A{r}'].value
    if not sku:
        continue
    asin = (_plan.get(sku) or {}).get('asin', '')
    key = asin if asin.startswith('B0') else sku
    if key in _seen:                       # same ASIN with a second SKU (FBA + merchant): one line, both SKUs
        _rows[_seen[key]][2] += ', ' + sku
        continue
    parent = _up[f'D{r}'].value == 'Parent'
    main = _up[f'T{r}'].value
    main_txt = ('-' if parent else (main.split('/image_kit/')[-1] if main else
                                    ('Step 1: ' + _s1[sku].split('/image_kit/')[-1] if sku in _s1 else
                                     ('NEW MAIN NEEDED (Image List). Now: ' + _miss[(sku, 'T')] if (sku, 'T') in _miss else 'keeps its current main (real photo on white)'))))
    if parent:
        fam_txt = 'PARENT: ' + SP_FAM[sku]
        status = (('Exists; re-sent unchanged' if sku == 'IDM-HEADS-FAMILY-PARENT' else 'Created') +
                  ' (theme: ' + str(_up[f'F{r}'].value) + ')')
    else:
        fam_txt = '    child of ' + SP_FAM[_up[f'E{r}'].value]
        status = ('New: goes live once GS1 shows brand ILLUCO for its UPC' if str(_up[f'C{r}'].value).startswith('Create')
                  else 'Live listing: updated')
    _seen[key] = len(_rows)
    _rows.append([fam_txt, asin if asin.startswith('B0') else (asin or '(new)'), sku, _up[f'G{r}'].value, _up[f'H{r}'].value,
                  _up[f'BB{r}'].value, _up[f'BA{r}'].value, _up[f'AY{r}'].value, _up[f'P{r}'].value, _up[f'BC{r}'].value,
                  main_txt, status])
PFILL_SP = PatternFill(fill_type='solid', fgColor='DDEBF7')
for i, row_ in enumerate(_rows, 5):
    is_p = str(row_[0]).startswith('PARENT')
    for j, v in enumerate(row_, 1):
        c = sp.cell(i, j, v); c.border = BOX
        c.font = Font(name=F, size=10, bold=is_p)
        if is_p:
            c.fill = PFILL_SP
    if str(row_[1]).startswith('B0'):
        link(sp.cell(i, 2), dp(row_[1]))
for col, wdt in zip('ABCDEFGHIJKL', (30, 13, 26, 70, 60, 30, 11, 9, 40, 14, 44, 44)):
    sp.column_dimensions[col].width = wdt
sp.freeze_panes = 'D5'

# ---- Image List: the upload carries no images (owner, 11/23: "I'll work on it with Ashley") ----
mi = wb.create_sheet('Image List')
mi.cell(1, 1, 'Image List: ILLUCO_Amazon_UPLOAD.xlsx sends no images. Live listings keep what they show now; new products '
              'start without images. Yellow main-image cells in the upload = a new main is needed.').font = Font(name=F, bold=True, size=12)
mi.cell(2, 1, 'Main image rule (Amazon): pure white background (RGB 255), the product only, no box, no text, no props, '
              'product fills about 85% of the frame, at least 2000 x 2000 px. Every main live today is on pure white.'
        ).font = Font(name=F, size=10, italic=True)
_ml = [x for x in _csv('data/build/missing_images.csv') if x['column'] == 'T']
_photos = {}
for x in _ml:
    _photos.setdefault(x['photo'], []).append(x)
_order = sorted(_photos.items(), key=lambda kv: (0 if 'suppressed' in kv[1][0]['meanwhile'] else
                                                 1 if 'new product' not in kv[1][0]['meanwhile'] else 2, kv[0]))
mi.cell(4, 1, f'1. Main images to shoot ({len(_order)} photos)').font = Font(name=F, bold=True, size=11)
for j, h in enumerate(['#', 'Main photo to shoot', 'Listings (SKU / ASIN)', 'Main on Amazon now'], 1):
    c = mi.cell(5, j, h); c.font = HFONT; c.fill = HFILL; c.border = BOX
r_ = 5
for i, (photo, xs) in enumerate(_order, 1):
    r_ += 1
    used = ', '.join(sorted({x['sku'] + (f" ({x['asin']})" if x['asin'].startswith('B0') else ' (new)') for x in xs}))
    for j, v in enumerate([i, photo, used, xs[0]['meanwhile']], 1):
        c = mi.cell(r_, j, v); c.border = BOX
        c.font = Font(name=F, size=10, bold='suppressed' in xs[0]['meanwhile'])
r_ += 2
_il = _csv('data/build/image_list.csv')
_pos = {x['sku'].replace(' (INFERRED)', ''): k for k, x in enumerate(_csv('data/build/upload_rows.csv'))}
_il.sort(key=lambda x: _pos.get(x['sku'], 10 ** 6))      # same order as the upload: family by family
mi.cell(r_, 1, f'2. Every listing in the upload ({len(_il)} SKUs)').font = Font(name=F, bold=True, size=11)
r_ += 1
for j, h in enumerate(['Family', 'SKU', 'ASIN', 'Size', 'Color', 'Main now', 'Main', 'Other images now'], 1):
    c = mi.cell(r_, j, h); c.font = HFONT; c.fill = HFILL; c.border = BOX
_fam_name = {'5PK': '5 Pack', 'SINGLE': '1 Pack', 'GRAND': 'Grand 2 Pack', 'HEADS': 'Heads 5 Pack'}
for x in _il:
    r_ += 1
    vals = [_fam_name.get(x['family'], x['family']), x['sku'], x['asin'], x['size'], x['color'], x['main_now'], x['main_action'],
            x['other_images_now']]
    for j, v in enumerate(vals, 1):
        c = mi.cell(r_, j, v); c.font = BODY; c.border = BOX
        if j == 7 and v.startswith('New'):
            c.fill = PatternFill(fill_type='solid', fgColor='FFFF00')
    if x['asin'].startswith('B0'):
        link(mi.cell(r_, 3), dp(x['asin']))
r_ += 2
mi.cell(r_, 1, '3. Live images to replace when Ashley has new ones (not changed by this upload)').font = Font(name=F, bold=True, size=11)
for k, txt in enumerate([
        'Image 2 on the 3 heads listings (B0FBPG5CS9, B0FCHH2SQB, B0FCJY3H9H): a composite of 5 copies of one head, live since '
        '11/21. Delete it in Manage Images or replace it.',
        'Image 2 on the 5-pack listings: the box print says "Anti-Fog technology", which the copy no longer claims.',
        'Image 8 on the Dark Blue 5-pack and Dark Blue single listings: stock photos, the mirrors shown are not ILLUCO\'s.'], 1):
    mi.cell(r_ + k, 1, f'{k}. {txt}').font = BODY
for col, wdt in zip('ABCDEFGH', (12, 60, 52, 30, 11, 52, 16, 44)):
    mi.column_dimensions[col].width = wdt
mi.freeze_panes = 'A6'

order = ['Summary', 'Shopper Preview', 'Image List', 'What I Need', 'ASIN Report', 'Upload Check', 'Listing Copy', 'Sales Direction', 'Review Analysis',
         'Competitors', 'Keywords', 'PPC Plan', 'PPC Apply', 'Images A+ Video', 'Image Kit', 'External Traffic', 'Action Plan']
wb._sheets = [wb[n] for n in order]

from xlsx_thin import thin_rows
thin_rows(wb)   # owner: every row at the default thin height
wb.save(OUT)
print('saved')
