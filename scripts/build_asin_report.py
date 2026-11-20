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
 ('Key findings', True),
 ('1. Reviews are thin and split: about 12 ratings across all dental-mirror ASINs, and nearly every negative rating is 1-star. Two orphan single-mirror listings sit outside their variation family, so ratings do not pool.', False),
 ('2. Two of the 1-star ratings are on 3X Dark Blue variants (5-pack B0F85B5BDC and orphan B0GGDGRHRR). Magnified mirrors show a smaller area and blur at distance, yet every title promises "No Distortion".', False),
 ('3. "Autoclavable 100X" sits next to 1X/2X/3X in every title and reads like a magnification. Titles also lead with "Fog-Resistant" while illuco.com says no mirror is fog-proof.', False),
 ('4. Single-mirror (1-pack) listings reuse the 5-pack infographic showing five mirrors, which invites quantity complaints. Replacement-head listings never state they need a cone-socket handle.', False),
 ('5. Data quality: model numbers hold variant names or the placeholder "IDMXXX"; dermatoscopes are classified under Home & Kitchen and Automotive; the 5-pack weight shows 2 lb.', False),
 ('6. Price position: ILLUCO is $19-28 per mirror against $1-9 for Hu-Friedy, Zirc, Artman and JMU, while "dental mirror" search is dominated by $4-10 consumer mirrors. The listing must sell professionals on the 99% reflectance difference.', False),
 ('7. Amazon prices sit above illuco.com: 5-pack $95-140 vs $85, photo mirror $165 vs $155.', False),
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
                                 ('Listing update sheet (GitHub)', GH + 'listings/Existing_Listings_Update_Sheet.xlsx'),
                                 ('Grand / Double-Sided upload file (GitHub)', GH + 'listings/ILLUCO_Grand_DoubleSided_Mirrors_Amazon_Upload_READY.xlsx'),
                                 ('Drive image folder', 'https://drive.google.com/drive/folders/112-y6c3etIb17RGpJH-nvIgKgCBrRnYQ')], 1):
    link(s.cell(base_ + k, 1), url, txt, size=10)

# ---------------- ASIN Report ----------------
FAM = {
 'B0FDCGG69J': ('5-Pack with Handles', 'P1'), 'B0FCNL53JN': ('Replacement Heads 5-Pack', 'P1'),
 'B0GGD9DVP9': ('Single Mirror with Handle', 'P1'), 'B0FCPD1KKN': ('Dental Photo Mirror', 'P2'),
}
COMPLAINTS = {
 '5-Pack with Handles': ('3.4 stars; about 35% of ratings are 1-star. Likely causes: fog expectation ("Fog-Resistant" in the title), '
                         '3X blur or narrow view sold as "No Distortion", price versus value.',
                         'New title and highlight; magnification guidance; drop "100X"; video; Vine; per-mirror savings versus the 1-pack.'),
 'Replacement Heads 5-Pack': ('2.0 stars; 67% 1-star. Likely cause: heads do not fit the buyer\'s handle (cone socket never stated); heads-only pack confused with a kit.',
                              'Title and bullet 2 now say "Cone Socket, Handles Not Included"; add a compatibility image; Vine.'),
 'Single Mirror with Handle': ('5.0 on 1 rating in the family; orphan listings carry 3.4 (3) and 1.0 (1). Likely causes: image 2 shows five mirrors for a 1-pack; 3X Dark Blue blur.',
                               'Merge orphans into the family; replace image 2 with a 1-mirror "what\'s in the box"; new copy; Vine.'),
 'Dental Photo Mirror': ('No ratings; BSR #462. Priced $165 against $8-40 competitors with little proof of the difference.',
                         'Model number placeholder "IDMXXX"; per-shape copy and dimensions; photo-result comparison images; Vine; consider price test.'),
}
hdr = ['ASIN', 'Parent ASIN', 'Family', 'Variant', 'Price (live)', 'Rating', 'Ratings count', 'BSR (Dental Mirrors / category)',
       'Est. monthly units (3rd-party est.)', 'Fulfillment', 'Gallery images',
       'Sessions 30d', 'Units 30d', 'Sales 30d ($)', 'Conversion rate', 'Ad spend 30d ($)', 'Ad sales 30d ($)', 'ACoS', 'TACoS',
       'Main customer complaints (evidence / hypothesis)', 'Recommended improvements', 'Priority', 'Owner', 'Status']
gal = {'B0FCZBD1KY': 7, 'B0FBPG5CS9': 5, 'B0GGDQ15DD': 6, 'B0G2DYRY7T': 4, 'B0GGDGRHRR': 6, 'B0FCNG7T9P': 5}
order = ['B0FCZBD1KY','B0F84VWGG5','B0F84TKGLS','B0FCMVZH31','B0F85B5BDC','B0F857HKBG',
         'B0FBPG5CS9','B0FCHH2SQB','B0FCJY3H9H',
         'B0GGDQ15DD','B0GGF37FSB','B0GGDV4J6B','B0GGD95T8Z','B0GGDS9MVF','B0GGDGRHRR','B0G2DYRY7T',
         'B0FCNG7T9P','B0F86CJ7R6','B0F86DNNSV','B0FCNRP7NF','B0FCN9V5G4',
         'B0F7YPNMWK','B0F81HQMD2','B0F7Z2TP29','B0FSM14R8P','B0F8CVN4W3']
rows = []
for a in order:
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
    if a == 'B0GGDGRHRR': comp_txt = 'ORPHAN (outside family). 1.0 star on 1 rating, 3X Dark Blue. ' + comp_txt
    if a == 'B0G2DYRY7T': comp_txt = 'ORPHAN duplicate of the 1X single mirror; best BSR in the line. 3.4 on 3 ratings (39% 1-star). A+ uses photo-mirror copy. ' + comp_txt
    if a == 'B0F85B5BDC': comp_txt = 'This 3X Dark Blue variant carries a 1-star. ' + comp_txt
    rows.append([a, par, fam, variant, (float(x['price'].replace('$','').replace(',','')) if x.get('price') else None), x.get('rating'), x.get('review_count'), bsr,
                 x.get('estimated_monthly_sales'), 'FBA' if x.get('is_fba') else 'FBM / SFP', gal.get(a, len(x.get('images') or [])),
                 None, None, None, None, None, None, None, None, comp_txt, fix_txt, pri, 'Cenk', 'Not started'])
r_ws = wb.create_sheet('ASIN Report')
table(r_ws, hdr, rows, [12, 12, 20, 22, 9, 7, 8, 26, 10, 9, 8, 9, 8, 10, 9, 10, 10, 8, 8, 55, 50, 7, 9, 11], input_cols=(12, 13, 14, 16, 17))
for i in range(2, len(rows) + 2):
    r_ws[f'O{i}'] = f'=IFERROR(M{i}/L{i},"")'; r_ws[f'O{i}'].number_format = '0.0%'
    r_ws[f'R{i}'] = f'=IFERROR(P{i}/Q{i},"")'; r_ws[f'R{i}'].number_format = '0.0%'
    r_ws[f'S{i}'] = f'=IFERROR(P{i}/N{i},"")'; r_ws[f'S{i}'].number_format = '0.0%'
    for col in 'NPQ': r_ws[f'{col}{i}'].number_format = '$#,##0'
    r_ws[f'E{i}'].number_format = '$#,##0.00'
    for col in 'OST': r_ws[f'{col}{i}'].font = BODY
# example row comment
r_ws.cell(1, 25, 'Critical reviews (opens signed-in)').font = HFONT; r_ws.cell(1, 25).fill = HFILL
r_ws.cell(1, 25).alignment = Alignment(wrap_text=True); r_ws.column_dimensions['Y'].width = 16
for i in range(2, len(rows) + 2):
    a = r_ws[f'A{i}'].value; par = r_ws[f'B{i}'].value
    link(r_ws[f'A{i}'], dp(a))
    if par: link(r_ws[f'B{i}'], dp(par))
    link(r_ws.cell(i, 25), reviews(a), '1-3 star reviews')
r_ws['L2'].comment = Comment('Input: Business Reports > Detail Page Sales and Traffic by Child Item, last 30 days, Sessions - Total. Example format: 412', 'audit')
dv = DataValidation(type='list', formula1='"Not started,In progress,Done,Blocked"', allow_blank=True)
r_ws.add_data_validation(dv); dv.add(f'X2:X{len(rows)+1}')
n = len(rows) + 3
r_ws.cell(n, 1, 'Pending new listings (upload file ready)').font = Font(name=F, bold=True)
for k, (sku, desc) in enumerate([('IDM-2C101LB/DB', 'Grand Size 10, 1X, 2-pack ($124)'), ('IDM-2C102LB/DB', 'Grand Size 10, 2X, 2-pack ($129)'),
                                 ('IDM-2CD41LB/DB', 'Double-Sided Size 4, 5-pack ($179)'), ('IDM-3CD41H', 'Double-Sided heads (price, images TBD)')], 1):
    r_ws.cell(n + k, 1, sku).font = BODY; r_ws.cell(n + k, 3, desc).font = BODY

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
calc = [['5-Pack with Handles', 118, 0.55, 0.08, 0.6], ['Replacement Heads', 85, 0.6, 0.08, 0.6], ['Single Mirror', 26, 0.5, 0.1, 0.6],
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
    pp[f'K{i}'] = 1.2; pp[f'K{i}'].font = BLUE; pp[f'K{i}'].fill = INFILL; pp[f'K{i}'].number_format = '$#,##0.00'
    pp[f'J{i}'] = f'=MIN(H{i},K{i})*I{i}'
    for col in 'FG': pp[f'{col}{i}'].number_format = '0.0%'
    for col in 'HJ': pp[f'{col}{i}'].number_format = '$#,##0.00'
    for col in 'FGHJ': pp[f'{col}{i}'].font = BODY
pp['A9'] = 'Total daily budget (proposal - do not raise spend until approved)'; pp['A9'].font = Font(name=F, bold=True)
pp['J9'] = '=SUM(J4:J8)'; pp['J9'].number_format = '$#,##0.00'; pp['J9'].font = Font(name=F, bold=True)
pp['A10'] = ('Assumptions: prices are live Amazon averages per family (2026-11-20). Margin, CVR and click targets are PLACEHOLDERS, not ILLUCO data - '
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

# ---------------- Creative plan ----------------
cr = wb.create_sheet('Images A+ Video')
crs = [
 ['All mouth mirrors', 'Image slot 1 (main)', 'Pure white; show exact count in the pack (5 or 1); no text', 'OK on 5-pack; single 3X orphan main shows the head in profile - reshoot'],
 ['All mouth mirrors', 'Image 2', '"What\'s in the box": count callout (x5 heads, x5 handles, care guide / x1 for single)', 'Single listings currently show FIVE mirrors here - replace first'],
 ['All mouth mirrors', 'Image 3', 'Side-by-side real photo: ILLUCO vs standard mirror under the same operatory light (99% vs 60-70%)', 'Missing - strongest proof of the price premium'],
 ['All mouth mirrors', 'Image 4', 'Magnification guide: 1X / 2X / 3X field of view + working distance; who each is for', 'Current "Choose your magnification" uses cartoon gums and no field-of-view guidance'],
 ['All mouth mirrors', 'Image 5', 'Size and fit: Size 4 = 22 mm head, cone socket thread, handle length', 'Missing'],
 ['All mouth mirrors', 'Image 6', 'Water-repellent demo: droplets beading off; honest "resists fog" wording', 'Missing'],
 ['All mouth mirrors', 'Image 7', 'Care and autoclave: 134°C/5 min or 121°C/20 min, rated 100 cycles, avoid abrasives', 'Text-only infographic today; text too small at mobile size'],
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
 ['Thu 11/20', 'Apply rewritten titles, highlights, bullets, backend keywords to all 21 dental-mirror ASINs', 'Cenk', 'Existing_Listings_Update_Sheet.xlsx', 'Not started'],
 ['Thu 11/20', 'Upload Grand + Double-Sided file (6 children + parent); head row after price/images confirmed', 'Cenk', 'ILLUCO_Grand_DoubleSided_..._READY.xlsx', 'Not started'],
 ['Thu 11/20', 'Open Seller Support cases: merge orphans B0GGDGRHRR / B0G2DYRY7T; re-classify dermatoscopes', 'Cenk', 'Attribute Fixes tab', 'Not started'],
 ['Thu 11/20', 'Pull Seller Central exports (business, ads, reviews, returns, Brand Analytics)', 'Cenk', 'What I Need tab', 'Not started'],
 ['Thu 11/20', 'Remove the 5-mirror image from the single-mirror galleries', 'Design', 'Images A+ Video tab', 'Not started'],
 ['Fri 11/21', 'PPC audit on 60-day data; negative-keyword sweep; no budget increases', 'Cenk', 'PPC Plan tab', 'Not started'],
 ['Fri 11/21', 'Enroll all parents in Vine; turn on Request a Review', 'Cenk', '', 'Not started'],
 ['Mon 11/24', 'Decide BFCM coupon and price parity (approval)', 'Manager', 'External Traffic tab', 'Not started'],
 ['Tue 11/25', 'Image brief to design (8 slots per family) + A+ comparison chart', 'Cenk / Design', 'Images A+ Video tab', 'Not started'],
 ['Wed 11/26', 'Attribution tags created; Google Search to Amazon brief to Chiru', 'Cenk / Chiru', 'External Traffic tab', 'Not started'],
 ['Mon 12/1', 'New PPC structure live (after approval)', 'Cenk', 'PPC Plan tab', 'Not started'],
 ['Fri 12/5', 'Video shoot (V1-V4); creator seeding list to Annabelle / Shery', 'Shery / Annabelle', '', 'Not started'],
 ['Fri 12/12', 'New images + A+ live; store rebuild live; SB / SBV launched', 'Design / Cenk', '', 'Not started'],
 ['Fri 12/19', '30-day review: rating, CVR, ACoS, TACoS vs this baseline', 'Cenk', 'ASIN Report tab', 'Not started'],
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

wb.save(OUT)
print('saved')
