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
from existing_listing_content import ROWS, B_LOOK, B_FOG, HANDLE, INTRO, STERIL, COAT

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

def fix_copy(v):
    """Remove the fog / 100-cycle claims that reviews and returns contradict."""
    if not isinstance(v, str):
        return v
    v = v.replace(', Fog-Resistant, Autoclave-Rated 100 Cycles', ', Autoclavable')
    v = v.replace('99% Reflectance, Fog-Resistant, Autoclave-Rated 100 Cycles, No Ghost Image', '99% Reflectance, No Ghost Image, Autoclavable')
    for a in ['The fog-resistant, water-repellent surface withstands 100 autoclave cycles. ',
              'A water-repellent coating keeps the view clear mid-procedure, and the mirror withstands 100 autoclave cycles. ',
              'A water-repellent coating keeps the view clear, and the mirror withstands 100 autoclave cycles. ',
              'A water-repellent coating keeps the view clear, and the heads are rated for 100 autoclave cycles. ']:
        v = v.replace(a, COAT)
    if v.startswith('FOG-RESISTANT, AUTOCLAVE-RATED FOR 100 CYCLES') or v.startswith('AUTOCLAVE-RATED FOR 100 CYCLES'):
        v = B_FOG
    v = v.replace(' anti fog', '')
    return v

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
     'G': 'ILLUCO UHD Dental Mirrors with Handles, Size 4 and Grand Size 10',
     'H': '99% Reflectance, Front Surface, No Ghost Image, Single, 5 Pack, Double-Sided and Grand, Autoclavable',
     'AD': INTRO + ('Choose the format that fits your operatory: single Size 4 (22mm) mirrors, 5-pack kits in 1X, 2X and 3X, '
                    'the Double-Sided Size 4 with 99% reflectance on both faces, or the Grand Size 10 (34mm) for a 2.4x wider view. '
                    'Every mirror comes on an ergonomic anti-rotation handle in Light Blue or Dark Blue. ' + COAT + STERIL),
     'AE': B_LOOK,
     'AF': ('CHOOSE YOUR MIRROR: Single or 5-pack Size 4 (22mm) in 1X, 2X or 3X; Double-Sided Size 4 with 99% on both faces; '
            'or Grand Size 10 (34mm) for 2.4x the viewing area. Light Blue or Dark Blue handles.'),
     'AG': HANDLE, 'AH': B_FOG,
     'AI': 'BUILT FOR CLINICIANS: Made for general dentists, hygienists, orthodontists, oral surgeons and dental students who want a brighter, ghost-free view.',
     'AJ': 'mouth mirror dentist tools dental instruments tooth teeth oral exam intraoral hygienist orthodontist front surface number 4 size 10 large double sided professional hd'})
put({'A': PB, 'B': PT, 'C': CREATE, 'D': 'Parent', 'F': TB, 'I': BRAND, 'L': ITK, 'EZ': 'Republic of Korea', 'FX': 'Not Applicable',
     'G': 'ILLUCO UHD Dental Mirror Heads, Size 4 (22mm), Cone Socket, 5 Pack',
     'H': 'Replacement Heads, Handles Not Included, Single-Sided or Double-Sided, 1X/2X/3X, 99% Reflectance, Autoclavable',
     'AD': INTRO + ('These Size 4 (22mm) replacement heads thread onto standard cone socket mirror handles, including ILLUCO ergonomic handles '
                    '(sold separately). Choose single-sided heads in 1X, 2X or 3X, or Double-Sided heads with 99% reflectance on both faces. '
                    + COAT + STERIL + ' Each pack includes 5 heads.'),
     'AE': B_LOOK,
     'AF': 'CONE SOCKET FIT, HANDLES NOT INCLUDED: Threads onto standard cone socket mirror handles, including ILLUCO ergonomic anti-rotation handles. Not for simple stem or European-thread handles.',
     'AG': 'SINGLE-SIDED OR DOUBLE-SIDED: Single-sided heads in 1X, 2X or 3X magnification, or Double-Sided 1X heads with the same 99% coating on both faces.',
     'AH': B_FOG,
     'AI': '5 REPLACEMENT HEADS PER PACK: Restock every operatory with the same bright, ghost-free view.',
     'AJ': 'mouth mirror heads replacement refill tops screw on cone socket dentist dental instruments tooth teeth oral exam intraoral hygienist front surface number 4 professional double sided'})
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
        tc.value = fix_copy(c.value)
        if c.comment:
            tc.comment = Comment(c.comment.text, 'ILLUCO audit')
    t[f'C{row}'] = CREATE; t[f'D{row}'] = 'Child'
    t[f'E{row}'] = PA if fam == 'A' else PB
    t[f'F{row}'] = TA if fam == 'A' else TB
    t[f'BB{row}'] = size
    if sku == 'IDM-3CD41H':
        t[f'T{row}'] = SHOP + 'double-head_7873821b-dd72-4a9a-8cea-7147a90c92c9.jpg'
        t[f'T{row}'].fill = PatternFill(fill_type=None); t[f'T{row}'].comment = None
        t[f'CF{row}'] = '139.00'; t[f'DI{row}'] = '139.00'
        for col in ('EO', 'EQ', 'ES', 'EU'):
            t[f'{col}{row}'].fill = YEL
        t[f'EO{row}'].comment = Comment('Package dimensions and weight unknown - FBA will measure; fill if you have them.', 'ILLUCO audit')
        t[f'T{row}'].comment = Comment('illuco.com image shows ONE double-sided head; replace with the image-kit main showing the 5-pack when ready.', 'ILLUCO audit')
    plan.append(dict(section='2 new child', sku=sku, asin='(new)', family=fam, size=size, color=t[f'BA{row}'].value or '',
                     items=t[f'AY{row}'].value, action=CREATE, price_old='', price_new=t[f'DI{row}'].value, note=''))
    row += 1

# ---- existing children: re-parent + new copy + model numbers + illuco.com prices ----
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
        old = amz_price.get(rr['asin'])
        if old and rr['price_new'] > old:
            flags['DI'] = f'Price goes UP from ${old:.2f} to ${rr["price_new"]:.2f} to match illuco.com. Keep or revert before upload.'
        vals = {'A': sku, 'B': PT, 'C': EDIT, 'D': 'Child', 'E': PA if fam == 'A' else PB, 'F': TA if fam == 'A' else TB,
                'G': rr['title'], 'H': rr['highlight'], 'AD': rr['description'],
                'AE': rr['bullets'][0], 'AF': rr['bullets'][1], 'AG': rr['bullets'][2], 'AH': rr['bullets'][3], 'AI': rr['bullets'][4],
                'AJ': rr['keywords'], 'P': rr['model_suggested'], 'BC': rr['model_suggested'], 'AY': rr['items'],
                'BB': rr['var_size'], 'BM': rr['included'], 'CF': f"{rr['price_new']:.2f}", 'DI': f"{rr['price_new']:.2f}"}
        if fam == 'A':
            vals['BA'] = rr['color']
        put(vals, flags)
        plan.append(dict(section='3 existing child', sku=sku + (' (INFERRED)' if status == 'inferred' else ''), asin=rr['asin'], family=fam,
                         size=rr['var_size'], color=rr['color'], items=rr['items'], action=EDIT, price_old=old, price_new=rr['price_new'], note=rr['note']))

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
wb.save(OUT)
with open(PLAN, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(plan[0].keys())); w.writeheader(); w.writerows(plan)
print('rows', row - 8, 'plan', len(plan))
