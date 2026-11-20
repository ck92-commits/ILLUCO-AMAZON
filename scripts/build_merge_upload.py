"""Build ONE upload file that merges all ILLUCO dental mirrors (except photo mirrors) into two families:
  A  IDM-HANDLE-FAMILY-PARENT  theme SIZE/COLOR/NUMBER_OF_ITEMS  (singles, 5-pack kits, Double-Sided, Grand)
  B  IDM-HEADS-FAMILY-PARENT   theme SIZE                        (replacement heads incl. Double-Sided heads)
Existing ASINs are re-parented with "Edit (Partial Update)" (their ASINs, sales history and reviews stay);
new Grand / Double-Sided / head SKUs are created with "Create or Replace (Full Update)".
usage: build_merge_upload.py <ILLUCO template .xlsx> <Grand/DS READY .xlsx> <out .xlsx> <plan .csv>"""
import sys, copy, csv, openpyxl
from openpyxl.styles import PatternFill
from openpyxl.comments import Comment
sys.path.insert(0, 'scripts')
from existing_listing_content import ROWS, B_HD, B_AUTO, HANDLE, INTRO, CARE, KW_CORE, lead_case

TPL, READY, OUT, PLAN = sys.argv[1:5]
PT, BRAND = 'PROFESSIONAL_HEALTHCARE', 'ILLUCO'
ITK = 'Industrial & Scientific > Professional Dental Supplies > Handpieces & Instruments > Mirrors (professional-dental-laryngeal-mirrors)'
PA, PB = 'IDM-HANDLE-FAMILY-PARENT', 'IDM-HEADS-FAMILY-PARENT'
TA, TB = 'SIZE/COLOR/NUMBER_OF_ITEMS', 'SIZE'
CREATE, EDIT = 'Create or Replace (Full Update)', 'Edit (Partial Update)'
YEL = PatternFill('solid', fgColor='FFFF00')
SHOP = 'https://cdn.shopify.com/s/files/1/0795/1348/5611/files/'

wb = openpyxl.load_workbook(TPL)
t = wb['Template']
for r in range(8, t.max_row + 1):
    for c in t[r]:
        c.value = None
rd = openpyxl.load_workbook(READY)['Template']
style_row = 14
plan = []

GRAND_MID = ("The ILLUCO Grand Dental Mirror puts that clarity on a Size 10 (34mm) head, giving a 2.4x wider field "
             "of view than a standard Size 4 (22mm) mirror. View an entire quadrant, multi-unit restorations or "
             "full-arch alignment in a single glance and spend less time repositioning. The wide 34mm surface also "
             "distributes pressure evenly for comfortable cheek and tongue retraction and bounces more overhead light "
             "into deep posterior regions. ")
DS_MID = ("The ILLUCO Double-Sided Dental Mirror carries that clarity on both faces, so you can retract tissue with one "
          "side and view with the other without flipping the mirror mid-procedure. At Size 4 (22mm) with a true 1X "
          "view, it suits routine exams, restorative checks, indirect vision and intraoral photography. ")
HEAD_MID = ("These replacement heads carry that coating on both faces, so you can retract tissue with one side and view "
            "with the other without flipping the mirror mid-procedure. Size 4 (22mm), true 1X view; the cone socket "
            "thread fits standard cone socket mirror handles, including ILLUCO ergonomic handles (sold separately). ")


def new_row_copy(sku, color):
    """Title / highlight / bullet 1 / autoclave bullet / description / keywords for the 7 new SKUs."""
    if sku.startswith('IDM-2C10'):
        mag = 2 if sku.startswith('IDM-2C102') else 1
        title = (f"ILLUCO Grand UHD Dental Mirror, Size 10 (34mm), 1X, 2 Pack, {color}" if mag == 1 else
                 f"ILLUCO Grand UHD 2X Magnifying Dental Mirror, Size 10, 2 Pack, {color}")
        hl = ("Ultra High Definition, With Handles, 2.4X Wider View, 99% Reflectance, 5-Minute Autoclave, 100+ Cycles"
              if mag == 1 else
              "Ultra High Definition, 34mm Head, With Handles, 2.4X Wider View, 99% Reflectance, 5-Minute Autoclave, 100+ Cycles")
        magline = ("This is the 1X version for a life-size view and clean quadrant photos. " if mag == 1 else
                   "This is the 2X magnifying version for fine detail; most mouth mirrors stop at 1X. ")
        desc = (INTRO + GRAND_MID + magline + CARE + "Each kit includes 2 Grand Size 10 mirror heads, 2 ergonomic "
                f"anti-rotation handles ({color}) and an autoclave sterilization and care guide.")
        kw = ("large mouth mirror oversize jumbo wide view dentist orthodontist oral surgery retractor intraoral "
              "photography quadrant tooth teeth oral exam hygienist uhd " + KW_CORE.replace(' 2x 3x', ' 2x'))
        return title, hl, B_HD, desc, kw
    if sku.startswith('IDM-2CD41'):
        title = f"ILLUCO Double-Sided UHD Dental Mirror, Size 4 (22mm), 5 Pack, {color}"
        hl = "Ultra High Definition on Both Sides, With Handles, 1X, 99% Reflectance, 5-Minute Autoclave, 100+ Cycles"
        b1 = ("ULTRA HIGH DEFINITION ON BOTH FACES: ILLUCO's front-surface dielectric coating on German optical glass "
              "reflects 99% of light on both sides, versus 60-70% for standard dental mirrors. The image is over 40% "
              "brighter, sharp and true to color, with no ghost image.")
        desc = (INTRO + DS_MID + CARE + "Each pack includes 5 double-sided Size 4 mirror heads, 5 ergonomic "
                f"anti-rotation handles ({color}) and an autoclave sterilization and care guide.")
        kw = ("two sided mouth mirror dual dentist tools dental instruments tooth teeth oral exam intraoral photography "
              "hygienist cone socket number 4 professional dentist mirror hd high definition uhd quick autoclave")
        return title, hl, b1, desc, kw
    # IDM-3CD41H double-sided heads
    title = "ILLUCO Double-Sided UHD Dental Mirror Heads, Size 4 (22mm), 5 Pack"
    hl = "Ultra High Definition on Both Sides, Replacement Heads, Handles Not Included, Cone Socket, 1X, 5-Minute Autoclave, 100+ Cycles"
    b1 = ("ULTRA HIGH DEFINITION ON BOTH FACES: ILLUCO's front-surface dielectric coating on German optical glass "
          "reflects 99% of light on both sides, versus 60-70% for standard dental mirrors. The image is over 40% "
          "brighter, sharp and true to color, with no ghost image.")
    desc = INTRO + HEAD_MID + CARE + "Each pack includes 5 double-sided Size 4 mirror heads. Handles are not included."
    kw = ("mouth mirror heads replacement refill tops screw on two sided dual dentist dental instruments tooth teeth oral "
          "exam hygienist number 4 professional hd high definition uhd quick autoclave")
    return title, hl, b1, desc, kw

row = 8
def put(vals, flags=None, note=None):
    global row
    for c in t[style_row]:
        if c.has_style:
            t.cell(row, c.column)._style = copy.copy(c._style)
    for col, v in vals.items():
        t[f'{col}{row}'] = v
    for col, msg in (flags or {}).items():
        t[f'{col}{row}'].fill = YEL
        t[f'{col}{row}'].comment = Comment(msg, 'ILLUCO audit')
    row += 1

# ---- parents ----
put({'A': PA, 'B': PT, 'C': CREATE, 'D': 'Parent', 'F': TA, 'I': BRAND, 'L': ITK, 'EZ': 'Republic of Korea', 'FX': 'Not Applicable',
     'G': 'ILLUCO UHD Dental Mirrors with Handles, 1X, 2X and 3X Magnifying, Size 4 and Grand Size 10',
     'H': 'Ultra High Definition, 99% Reflectance, No Ghost Image, 5-Minute Autoclave, 100+ Cycles, Single, 5 Pack, Double-Sided and Grand',
     'AD': INTRO + ('Choose the format that fits your operatory: single Size 4 (22mm) mirrors or 5-pack kits in 1X, or 2X and 3X '
                    'magnifying for fine detail (most mouth mirrors stop at 1X); the Double-Sided Size 4 with 99% reflectance on both '
                    'faces; or the Grand Size 10 (34mm) for a 2.4x wider view. Every mirror comes on an ergonomic anti-rotation '
                    'handle in Light Blue or Dark Blue. ' + CARE),
     'AE': B_HD,
     'AF': ('2X AND 3X MAGNIFICATION, OR TRUE 1X: Most mouth mirrors are 1X. Choose ILLUCO 2X or 3X to see margins, caries and '
            'calculus larger, or 1X for a life-size view. Also Double-Sided Size 4 and Grand Size 10 (34mm). Light Blue or Dark Blue handles.'),
     'AG': B_AUTO, 'AH': HANDLE,
     'AI': 'BUILT FOR CLINICIANS: Made for general dentists, hygienists, orthodontists, oral surgeons and dental students who want a brighter, ghost-free view.',
     'AJ': 'mouth mirror dentist tools dental instruments tooth teeth oral exam intraoral hygienist orthodontist front surface number 4 size 10 large double sided professional ' + KW_CORE})
put({'A': PB, 'B': PT, 'C': CREATE, 'D': 'Parent', 'F': TB, 'I': BRAND, 'L': ITK, 'EZ': 'Republic of Korea', 'FX': 'Not Applicable',
     'G': 'ILLUCO UHD Dental Mirror Heads, 1X, 2X and 3X Magnifying, Size 4 (22mm), Cone Socket, 5 Pack',
     'H': 'Ultra High Definition, Replacement Heads, Handles Not Included, Single-Sided or Double-Sided, 5-Minute Autoclave, 100+ Cycles',
     'AD': INTRO + ('These Size 4 (22mm) replacement heads thread onto standard cone socket mirror handles, including ILLUCO ergonomic handles '
                    '(sold separately). Choose single-sided heads in 1X, or 2X and 3X magnifying for fine detail, or Double-Sided heads with '
                    '99% reflectance on both faces. ' + CARE + 'Each pack includes 5 heads.'),
     'AE': B_HD,
     'AF': 'CONE SOCKET FIT, HANDLES NOT INCLUDED: Threads onto standard cone socket mirror handles, including ILLUCO ergonomic anti-rotation handles. Not for simple stem or European-thread handles.',
     'AG': 'SINGLE-SIDED IN 1X, 2X OR 3X, OR DOUBLE-SIDED: Most mouth mirrors are 1X; ILLUCO 2X and 3X show fine detail larger. Double-Sided 1X heads carry the same 99% coating on both faces.',
     'AH': B_AUTO,
     'AI': '5 REPLACEMENT HEADS PER PACK: Restock every operatory with the same bright, ghost-free view.',
     'AJ': 'mouth mirror heads replacement refill tops screw on cone socket dentist dental instruments tooth teeth oral exam hygienist number 4 professional double sided ' + KW_CORE})
plan += [dict(section='1 new parent', sku=PA, asin='(new)', family='A', size='', color='', items='', action=CREATE, price_old='', price_new='', note='Family A parent'),
         dict(section='1 new parent', sku=PB, asin='(new)', family='B', size='', color='', items='', action=CREATE, price_old='', price_new='', note='Family B parent')]

# ---- new children from the Grand / Double-Sided file ----
NEW = {'IDM-2C101LB': ('A', 'Size 10 (34mm) Grand 1X'), 'IDM-2C101DB': ('A', 'Size 10 (34mm) Grand 1X'),
       'IDM-2C102LB': ('A', 'Size 10 (34mm) Grand 2X'), 'IDM-2C102DB': ('A', 'Size 10 (34mm) Grand 2X'),
       'IDM-2CD41LB': ('A', 'Size 4 (22mm) Double-Sided 1X'), 'IDM-2CD41DB': ('A', 'Size 4 (22mm) Double-Sided 1X'),
       'IDM-3CD41H': ('B', 'Size 4 (22mm) Double-Sided 1X')}
for r in range(9, 16):
    sku = rd[f'A{r}'].value
    fam, size = NEW[sku]
    for c in rd[r]:
        tc = t.cell(row, c.column)
        if c.has_style:
            tc._style = copy.copy(c._style)
        tc.value = c.value
        if c.comment:
            tc.comment = Comment(c.comment.text, 'ILLUCO audit')
    t[f'C{row}'] = CREATE; t[f'D{row}'] = 'Child'
    t[f'E{row}'] = PA if fam == 'A' else PB
    t[f'F{row}'] = TA if fam == 'A' else TB
    t[f'BB{row}'] = size
    title, hl, b1, desc, kw = new_row_copy(sku, t[f'BA{row}'].value)
    t[f'G{row}'] = title; t[f'H{row}'] = hl; t[f'AE{row}'] = b1; t[f'AH{row}'] = B_AUTO; t[f'AD{row}'] = desc; t[f'AJ{row}'] = kw
    if sku == 'IDM-3CD41H':
        t[f'T{row}'] = SHOP + 'double-head_7873821b-dd72-4a9a-8cea-7147a90c92c9.jpg'
        t[f'T{row}'].fill = PatternFill(fill_type=None); t[f'T{row}'].comment = None
        t[f'CF{row}'] = '139.00'; t[f'DI{row}'] = '139.00'
        for col in ('CF', 'DI'):
            t[f'{col}{row}'].fill = YEL
        t[f'DI{row}'].comment = Comment('Placeholder: $139 is the illuco.com price. The heads are new on Amazon, so set the Amazon '
                                        'price here and in CF (List Price) before upload.', 'ILLUCO audit')
        for col in ('EO', 'EQ', 'ES', 'EU'):
            t[f'{col}{row}'].fill = YEL
        t[f'EO{row}'].comment = Comment('Package dimensions and weight unknown - FBA will measure; fill if you have them.', 'ILLUCO audit')
        t[f'T{row}'].comment = Comment('illuco.com image shows ONE double-sided head; replace with the image-kit main showing the 5-pack when ready.', 'ILLUCO audit')
    plan.append(dict(section='2 new child', sku=sku, asin='(new)', family=fam, size=size, color=t[f'BA{row}'].value or '',
                     items=t[f'AY{row}'].value, action=CREATE, price_old='', price_new=t[f'DI{row}'].value, note=''))
    row += 1

# ---- existing children: re-parent + new copy + model numbers (Amazon prices left unchanged, owner 11/20) ----
amz_price = {}
import json
for x in json.load(open('data/raw/illuco_catalog.json')):
    if x.get('price'):
        amz_price.setdefault(x['asin'], float(x['price'].replace('$', '').replace(',', '')))
for rr in ROWS:
    if rr['asin'] == 'B0GGDQ15DD':
        plan.append(dict(section='4 not re-parented', sku='IDM2C41LB-1X-FBA / IDM-2C41LB-1X', asin=rr['asin'], family='-', size='', color='',
                         items='', action='Seller Support: merge duplicate ASIN into B0G2DYRY7T', price_old=amz_price.get(rr['asin']), price_new='', note=rr['note']))
        continue
    fam = rr['new_family']
    for sku, status in rr['skus']:
        flags = {}
        if status == 'inferred':
            flags['A'] = f"SKU inferred from the IDM pattern for {rr['asin']} - confirm in Manage All Inventory before upload."
        old = amz_price.get(rr['asin'])   # live Amazon price; the upload leaves it as is
        vals = {'A': sku, 'B': PT, 'C': EDIT, 'D': 'Child', 'E': PA if fam == 'A' else PB, 'F': TA if fam == 'A' else TB,
                'G': rr['title'], 'H': rr['highlight'], 'AD': rr['description'],
                'AE': rr['bullets'][0], 'AF': rr['bullets'][1], 'AG': rr['bullets'][2], 'AH': rr['bullets'][3], 'AI': rr['bullets'][4],
                'AJ': rr['keywords'], 'P': rr['model_suggested'], 'BC': rr['model_suggested'], 'AY': rr['items'],
                'BB': rr['var_size'], 'BM': rr['included']}
        if fam == 'A':
            vals['BA'] = rr['color']
        put(vals, flags)
        plan.append(dict(section='3 existing child', sku=sku + (' (INFERRED)' if status == 'inferred' else ''), asin=rr['asin'], family=fam,
                         size=rr['var_size'], color=rr['color'], items=rr['items'], action=EDIT, price_old=old, price_new='unchanged', note=rr['note']))

# sanity: unique variation combos per family, valid theme values, title length
combos = {}
for r in range(8, row):
    if t[f'D{r}'].value != 'Child':
        continue
    key = (t[f'E{r}'].value, t[f'BB{r}'].value, t[f'BA{r}'].value, t[f'AY{r}'].value)
    asin_key = t[f'A{r}'].value
    combos.setdefault(key, set()).add(asin_key)
dups = {k: v for k, v in combos.items() if len(v) > 1}
for k, v in dups.items():
    # several SKUs of ONE ASIN share a combo legitimately (FBA + FBM offers)
    print('shared combo', k, v)
assert all(len(str(t[f'G{r}'].value or '')) < 200 for r in range(8, row))
for r in range(8, row):
    for col in ('AE', 'AF', 'AG', 'AH', 'AI'):
        if t[f'{col}{r}'].value:
            t[f'{col}{r}'] = lead_case(t[f'{col}{r}'].value)
wb.save(OUT)
with open(PLAN, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(plan[0].keys())); w.writeheader(); w.writerows(plan)
print('rows', row - 8, 'plan', len(plan))
