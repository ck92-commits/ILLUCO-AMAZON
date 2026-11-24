"""Build ONE upload file with ILLUCO's dental mirrors (except photo mirrors) in four variation families. Each family
holds one pack size and its children vary by Color and Size only (owner, 11/23: "separate the quantities"):
  IDM-5PACK-FAMILY-PARENT   COLOR/SIZE  5 mirrors + 5 handles: Size 4 1X / 2X / 3X kits and the Double-Sided 5-pack
  IDM-SINGLE-FAMILY-PARENT  COLOR/SIZE  1 mirror + 1 handle: Size 4 1X / 2X / 3X
  IDM-GRAND-FAMILY-PARENT   COLOR/SIZE  2 mirrors + 2 handles: Grand Size 10 1X / 2X
  IDM-HEADS-FAMILY-PARENT   SIZE        5 replacement heads: single-sided 1X / 2X / 3X and Double-Sided
The family uploaded on 11/21 (IDM-HANDLE-FAMILY-PARENT, theme SIZE/COLOR/NUMBER_OF_ITEMS) is deleted first by
ILLUCO_Amazon_STEP1_delete_parent.xlsx (build_step1.py): a live family's theme cannot be changed in place, and a
child can belong to only one parent (Amazon 8032).
Existing ASINs are re-parented with "Edit (Partial Update)" (their ASINs, sales history and reviews stay);
new Grand / Double-Sided / head SKUs are created with "Create or Replace (Full Update)".
usage: build_merge_upload.py <ILLUCO template .xlsx> <Grand/DS READY .xlsx> <out .xlsx> <plan .csv>"""
import sys, copy, csv, openpyxl
from openpyxl.styles import PatternFill
from openpyxl.comments import Comment
sys.path.insert(0, 'scripts')
from existing_listing_content import ROWS, B_HD, B_AUTO, HANDLE, INTRO, CARE, KW_CORE, lead_case, size_name

TPL, READY, OUT, PLAN = sys.argv[1:5]
PT, BRAND = 'PROFESSIONAL_HEALTHCARE', 'ILLUCO'
ITK = 'Industrial & Scientific > Professional Dental Supplies > Handpieces & Instruments > Mirrors (professional-dental-laryngeal-mirrors)'
FAM = {   # family -> (parent SKU, variation theme); one pack size per family
    '5PK': ('IDM-5PACK-FAMILY-PARENT', 'COLOR/SIZE'),
    'SINGLE': ('IDM-SINGLE-FAMILY-PARENT', 'COLOR/SIZE'),
    'GRAND': ('IDM-GRAND-FAMILY-PARENT', 'COLOR/SIZE'),
    'HEADS': ('IDM-HEADS-FAMILY-PARENT', 'SIZE'),
}
FAM_ORDER = list(FAM)
FAM_OF_PARENT = {p: f for f, (p, _) in FAM.items()}
DELETED_PARENT = 'IDM-HANDLE-FAMILY-PARENT'   # removed by the delete file before this upload


def family_of(kind, size, items):
    """kind 'A' = mirror with handle, 'B' = replacement heads (existing_listing_content's new_family)."""
    if kind == 'B':
        return 'HEADS'
    if 'Grand' in str(size):
        return 'GRAND'
    return {5: '5PK', 1: 'SINGLE'}[int(float(items))]


def kind_of(fam):
    return 'B' if fam == 'HEADS' else 'A'


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
        title = (f"ILLUCO Grand UHD Dental Mirrors, Size 10, 1X, 2 Pack, {color}" if mag == 1 else
                 f"ILLUCO Grand UHD 2X Magnifying Dental Mirrors, Size 10, 2 Pack, {color}")
        hl = "Ultra High Definition, 34mm Head, With 2 Handles, 2.4X Wider View, 99% Reflectance, 5-Minute Autoclave, 100+ Cycles"
        magline = ("This is the 1X version for a life-size view and clean quadrant photos. " if mag == 1 else
                   "This is the 2X magnifying version for fine detail; most mouth mirrors stop at 1X. ")
        desc = (INTRO + GRAND_MID + magline + CARE + "Each kit includes 2 Grand Size 10 mirror heads, 2 ergonomic "
                f"anti-rotation handles ({color}) and an autoclave sterilization and care guide.")
        kw = ("large mouth mirror oversize jumbo wide view dentist orthodontist oral surgery retractor intraoral "
              "photography quadrant tooth teeth oral exam hygienist uhd " + KW_CORE.replace(' 2x 3x', ' 2x'))
        return title, hl, B_HD, desc, kw
    if sku.startswith('IDM-2CD41'):
        title = f"ILLUCO Double-Sided UHD Dental Mirrors, Size 4 (22mm), 5 Pack, {color}"
        hl = "Ultra High Definition on Both Sides, With 5 Handles, 1X, 99% Reflectance, 5-Minute Autoclave, 100+ Cycles"
        b1 = ("ULTRA HIGH DEFINITION ON BOTH FACES: ILLUCO's front-surface dielectric coating on German optical glass "
              "reflects 99% of light on both sides, versus 60-70% for standard dental mirrors. The image is over 40% "
              "brighter, sharp and true to color, with no ghost image.")
        desc = (INTRO + DS_MID + CARE + "Each pack includes 5 double-sided Size 4 mirror heads, 5 ergonomic "
                f"anti-rotation handles ({color}) and an autoclave sterilization and care guide.")
        kw = ("two sided mouth mirror dual dentist tools dental instruments tooth teeth oral exam intraoral photography "
              "hygienist cone socket number 4 professional dentist mirror hd high definition uhd quick autoclave")
        return title, hl, b1, desc, kw
    # IDM-3CD41H double-sided heads
    title = "ILLUCO Double-Sided UHD Dental Mirror Heads, Size 4 (22mm), 1X, 5 Pack"
    hl = "Ultra High Definition on Both Sides, Cone Socket, Handles Not Included, 1X, 5-Minute Autoclave, 100+ Cycles"
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

# ---- parents: one per pack size (owner, 11/23) ----
PARENT_BASE = {'B': PT, 'C': CREATE, 'D': 'Parent', 'I': BRAND, 'L': ITK, 'EZ': 'Republic of Korea', 'FX': 'Not Applicable'}
CLINICIANS = ('BUILT FOR CLINICIANS: Made for general dentists, hygienists, orthodontists, oral surgeons and dental students '
              'who want a brighter, ghost-free view.')
put({**PARENT_BASE, 'A': FAM['5PK'][0], 'F': FAM['5PK'][1],
     'G': 'ILLUCO UHD Dental Mirrors with Handles, 5 Pack, Size 4 (22mm), 1X, 2X, 3X or Double-Sided',
     'AD': INTRO + ('Each pack holds 5 Size 4 (22mm) mirrors on 5 ergonomic anti-rotation handles, in Light Blue or Dark Blue. '
                    'Choose 1X for a life-size view, 2X or 3X magnifying for fine detail (most mouth mirrors stop at 1X), or the '
                    'Double-Sided 1X with 99% reflectance on both faces. ' + CARE + 'Each pack includes 5 mirrors, 5 handles '
                    'and an autoclave sterilization and care guide.'),
     'AE': B_HD,
     'AF': ('1X, 2X OR 3X, OR DOUBLE-SIDED: Most mouth mirrors are 1X. Choose ILLUCO 2X or 3X to see margins, caries and calculus '
            'larger, 1X for a life-size view, or Double-Sided 1X to retract with one face and view with the other.'),
     'AG': B_AUTO, 'AH': HANDLE,
     'AI': ('5 MIRRORS AND 5 HANDLES PER PACK: Equip a whole operatory at once, in Light Blue or Dark Blue. Built for general '
            'dentists, hygienists, orthodontists and dental students.'),
     'AJ': 'mouth mirror dentist tools dental instruments tooth teeth oral exam intraoral hygienist orthodontist front surface number 4 set kit double sided ' + KW_CORE})
put({**PARENT_BASE, 'A': FAM['SINGLE'][0], 'F': FAM['SINGLE'][1],
     'G': 'ILLUCO UHD Dental Mirror with Handle, 1 Pack, Size 4 (22mm), 1X, 2X or 3X Magnifying',
     'AD': INTRO + ('One Size 4 (22mm) mirror on an ergonomic anti-rotation handle, in Light Blue or Dark Blue. Choose 1X for a '
                    'life-size view, or 2X or 3X magnifying for fine detail (most mouth mirrors stop at 1X). ' + CARE +
                    'Includes 1 mirror and 1 handle. Also available in 5 packs and as replacement heads.'),
     'AE': B_HD,
     'AF': ('2X AND 3X MAGNIFICATION, OR TRUE 1X: Most mouth mirrors are 1X. Choose ILLUCO 2X or 3X to see margins, caries and '
            'calculus larger, or 1X for a life-size view. Light Blue or Dark Blue handle.'),
     'AG': B_AUTO, 'AH': HANDLE, 'AI': CLINICIANS,
     'AJ': 'mouth mirror dentist tools dental instruments tooth teeth oral exam intraoral hygienist student front surface number 4 professional single ' + KW_CORE})
put({**PARENT_BASE, 'A': FAM['GRAND'][0], 'F': FAM['GRAND'][1],
     'G': 'ILLUCO Grand UHD Dental Mirrors with Handles, 2 Pack, Size 10 (34mm), 1X or 2X Magnifying',
     'AD': INTRO + GRAND_MID + ('Choose 1X for a life-size view or 2X magnifying for fine detail. ' + CARE + 'Each kit includes '
                                '2 Grand Size 10 mirror heads, 2 ergonomic anti-rotation handles in Light Blue or Dark Blue and an '
                                'autoclave sterilization and care guide.'),
     'AE': B_HD,
     'AF': ('GRAND SIZE 10 (34MM), 2.4X WIDER VIEW: See a whole quadrant, multi-unit restorations or full-arch alignment in one '
            'glance and spend less time repositioning. Choose 1X or 2X magnifying.'),
     'AG': B_AUTO, 'AH': HANDLE, 'AI': CLINICIANS,
     'AJ': ('large mouth mirror oversize jumbo wide view dentist orthodontist oral surgery retractor intraoral photography quadrant '
            'tooth teeth oral exam hygienist uhd ' + KW_CORE.replace(' 2x 3x', ' 2x'))})
put({**PARENT_BASE, 'A': FAM['HEADS'][0], 'F': FAM['HEADS'][1],
     'G': 'ILLUCO UHD Dental Mirror Heads, 5 Pack, Size 4 (22mm), Cone Socket, 1X, 2X, 3X or Double-Sided',
     'AD': INTRO + ('These Size 4 (22mm) replacement heads thread onto standard cone socket mirror handles, including ILLUCO ergonomic handles '
                    '(sold separately). Choose single-sided heads in 1X, or 2X and 3X magnifying for fine detail, or Double-Sided heads with '
                    '99% reflectance on both faces. ' + CARE + 'Each pack includes 5 heads.'),
     'AE': B_HD,
     'AF': 'CONE SOCKET FIT, HANDLES NOT INCLUDED: Threads onto standard cone socket mirror handles, including ILLUCO ergonomic anti-rotation handles. Not for simple stem or European-thread handles.',
     'AG': 'SINGLE-SIDED IN 1X, 2X OR 3X, OR DOUBLE-SIDED: Most mouth mirrors are 1X; ILLUCO 2X and 3X show fine detail larger. Double-Sided 1X heads carry the same 99% coating on both faces.',
     'AH': B_AUTO,
     'AI': '5 REPLACEMENT HEADS PER PACK: Restock every operatory with the same bright, ghost-free view.',
     'AJ': 'mouth mirror heads replacement refill tops screw on cone socket dentist dental instruments tooth teeth oral exam hygienist number 4 professional double sided ' + KW_CORE})
PARENT_NOTE = {'5PK': 'New parent: 5 mirrors + 5 handles (Size 4 1X / 2X / 3X and Double-Sided)',
               'SINGLE': 'New parent: 1 mirror + 1 handle (Size 4 1X / 2X / 3X)',
               'GRAND': 'New parent: 2 mirrors + 2 handles (Grand Size 10 1X / 2X)',
               'HEADS': 'Exists since 11/21 (unchanged): 5 replacement heads'}
plan += [dict(section='1 parent', sku=FAM[f][0], asin='(new)' if f != 'HEADS' else '(exists)', family=f, size='', color='',
              items='', action=CREATE, price_old='', price_new='', note=PARENT_NOTE[f]) for f in FAM_ORDER]

# ---- new children from the Grand / Double-Sided file ----
NEW = {'IDM-2C101LB': ('A', 'Size 10 (34mm) Grand 1X'), 'IDM-2C101DB': ('A', 'Size 10 (34mm) Grand 1X'),
       'IDM-2C102LB': ('A', 'Size 10 (34mm) Grand 2X'), 'IDM-2C102DB': ('A', 'Size 10 (34mm) Grand 2X'),
       'IDM-2CD41LB': ('A', 'Size 4 (22mm) Double-Sided 1X'), 'IDM-2CD41DB': ('A', 'Size 4 (22mm) Double-Sided 1X'),
       'IDM-3CD41H': ('B', 'Size 4 (22mm) Double-Sided 1X')}
for r in range(9, 16):
    sku = rd[f'A{r}'].value
    kind, size = NEW[sku]
    for c in rd[r]:
        tc = t.cell(row, c.column)
        if c.has_style:
            tc._style = copy.copy(c._style)
        tc.value = c.value
        if c.comment:
            tc.comment = Comment(c.comment.text, 'ILLUCO audit')
    fam = family_of(kind, size, t[f'AY{row}'].value)
    t[f'C{row}'] = CREATE; t[f'D{row}'] = 'Child'
    t[f'E{row}'], t[f'F{row}'] = FAM[fam]
    t[f'BB{row}'] = size
    title, hl, b1, desc, kw = new_row_copy(sku, t[f'BA{row}'].value)
    t[f'G{row}'] = title; t[f'H{row}'] = hl; t[f'AE{row}'] = b1; t[f'AH{row}'] = B_AUTO; t[f'AD{row}'] = desc; t[f'AJ{row}'] = kw
    if sku == 'IDM-3CD41H':
        t[f'T{row}'] = SHOP + 'double-head_7873821b-dd72-4a9a-8cea-7147a90c92c9.jpg'
        t[f'T{row}'].fill = PatternFill(fill_type=None); t[f'T{row}'].comment = None
        t[f'CF{row}'] = '139.00'; t[f'DI{row}'] = '139.00'
        t[f'DI{row}'].comment = Comment('$139 = the illuco.com price, used for now (owner, Nov 20). The heads are new on Amazon.',
                                        'ILLUCO audit')
        for col in ('EO', 'EQ', 'ES', 'EU'):
            t[f'{col}{row}'].fill = YEL
        t[f'EO{row}'].comment = Comment('Package dimensions and weight unknown - FBA will measure; fill if you have them.', 'ILLUCO audit')
        t[f'T{row}'].comment = Comment('illuco.com image shows ONE double-sided head; replace with the image-kit main showing the 5-pack when ready.', 'ILLUCO audit')
    plan.append(dict(section='2 new child', sku=sku, asin='(new)', family=fam, size=size, color=t[f'BA{row}'].value or '',
                     items=t[f'AY{row}'].value, action=CREATE, price_old='', price_new=t[f'DI{row}'].value, note=''))
    row += 1

# ---- existing children: re-parent + new copy + model numbers (Amazon prices left unchanged, owner 11/20) ----
# The OLD 5-pack and heads families use the model number as their only selector ("Model: ..."), so it must read
# as a product name, never a code (owner, 11/21). The IDM code goes in Part Number.
def harmonized_model(size, n, color, fam):
    """Model Number = a short product name in the same words as the variation choices and titles (owner, 11/21:
    names must be in harmony; the old families show Model as their selector). Never a code; max 40 characters."""
    m = str(size).split()[-1]          # 1X / 2X / 3X
    n = int(float(n))
    if 'Grand' in str(size):
        s = f'Size 10 Grand, {m}, {n} Pack, {color}'
    elif 'Double-Sided' in str(size):
        s = f'Size 4 Double-Sided, {n} Pack, {color}' if fam == 'A' else f'Size 4 Double-Sided Heads, {m}, {n} Pack'
    elif fam == 'B':
        s = f'Size 4 Single-Sided Heads, {m}, {n} Pack'
    else:
        s = f'Size 4, {m}, {n} Pack, {color}'
    assert len(s) <= 40, s
    return s


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
    fam = family_of(rr['new_family'], rr['var_size'], rr['items'])
    for sku, status in rr['skus']:
        flags = {}
        if status == 'inferred':
            flags['A'] = f"SKU inferred from the IDM pattern for {rr['asin']} - confirm in Manage All Inventory before upload."
        old = amz_price.get(rr['asin'])   # live Amazon price; the upload leaves it as is
        vals = {'A': sku, 'B': PT, 'C': EDIT, 'D': 'Child', 'E': FAM[fam][0], 'F': FAM[fam][1],
                'G': rr['title'], 'H': rr['highlight'], 'AD': rr['description'],
                'AE': rr['bullets'][0], 'AF': rr['bullets'][1], 'AG': rr['bullets'][2], 'AH': rr['bullets'][3], 'AI': rr['bullets'][4],
                'AJ': rr['keywords'], 'P': harmonized_model(rr['var_size'], rr['items'], rr['color'], rr['new_family']), 'BC': rr['model_suggested'], 'AY': rr['items'],
                'BB': rr['var_size'], 'BM': rr['included']}
        if kind_of(fam) == 'A':
            vals['BA'] = rr['color']
        put(vals, flags)
        plan.append(dict(section='3 existing child', sku=sku + (' (INFERRED)' if status == 'inferred' else ''), asin=rr['asin'], family=fam,
                         size=rr['var_size'], color=rr['color'], items=rr['items'], action=EDIT, price_old=old, price_new='unchanged', note=rr['note']))

# sanity: one product per variation combination (several SKUs of ONE ASIN may share it: FBA + FBM offers),
# one pack size per family (owner, 11/23), title length
THEME_COL = {'SIZE': 'BB', 'COLOR': 'BA', 'NUMBER_OF_ITEMS': 'AY'}
asin_by_sku = {p['sku'].replace(' (INFERRED)', ''): p['asin'] for p in plan}
combos, counts = {}, {}
for r in range(8, row):
    if t[f'D{r}'].value != 'Child':
        continue
    sku, par = t[f'A{r}'].value, t[f'E{r}'].value
    key = (par,) + tuple(t[f'{THEME_COL[p]}{r}'].value for p in t[f'F{r}'].value.split('/'))
    assert all(key[1:]), (sku, key)
    a = asin_by_sku.get(sku)
    combos.setdefault(key, set()).add(a if a and a != '(new)' else 'new:' + sku)
    counts.setdefault(par, set()).add(int(float(t[f'AY{r}'].value)))
    assert par in FAM_OF_PARENT and t[f'F{r}'].value == FAM[FAM_OF_PARENT[par]][1], (sku, par)
dups = {k: v for k, v in combos.items() if len(v) > 1}
assert not dups, dups
assert all(len(v) == 1 for v in counts.values()), counts
print('pack size per family:', {FAM_OF_PARENT[p]: sorted(v)[0] for p, v in counts.items()})
assert all(len(str(t[f'G{r}'].value or '')) < 200 for r in range(8, row))
for r in range(8, row):
    for col in ('AE', 'AF', 'AG', 'AH', 'AI'):
        if t[f'{col}{r}'].value:
            t[f'{col}{r}'] = lead_case(t[f'{col}{r}'].value)
# ---- images: every child gets its 8 image-kit images, linked from the GitHub repo at a fixed commit ----
# (the repo is public, so Amazon can download them while it processes the upload; it keeps its own copies after that)
import subprocess
from pathlib import Path
IMG_DIRS = {  # ASIN (existing) or SKU (new) -> image_kit folder
    'B0FCZBD1KY': 'A_handle/kit_5pack_dark_blue', 'B0F84TKGLS': 'A_handle/kit_5pack_dark_blue', 'B0F85B5BDC': 'A_handle/kit_5pack_dark_blue',
    'B0F84VWGG5': 'A_handle/kit_5pack_light_blue', 'B0FCMVZH31': 'A_handle/kit_5pack_light_blue', 'B0F857HKBG': 'A_handle/kit_5pack_light_blue',
    'B0G2DYRY7T': 'A_handle/single_1pack_light_blue', 'B0GGDV4J6B': 'A_handle/single_1pack_light_blue', 'B0GGDS9MVF': 'A_handle/single_1pack_light_blue',
    'B0GGF37FSB': 'A_handle/single_1pack_dark_blue', 'B0GGD95T8Z': 'A_handle/single_1pack_dark_blue', 'B0GGDGRHRR': 'A_handle/single_1pack_dark_blue',
    'B0FBPG5CS9': 'B_heads/single_sided_heads_5pack', 'B0FCHH2SQB': 'B_heads/single_sided_heads_5pack', 'B0FCJY3H9H': 'B_heads/single_sided_heads_5pack',
    'IDM-2C101LB': 'A_handle/grand_2pack_light_blue', 'IDM-2C102LB': 'A_handle/grand_2pack_light_blue',
    'IDM-2C101DB': 'A_handle/grand_2pack_dark_blue', 'IDM-2C102DB': 'A_handle/grand_2pack_dark_blue',
    'IDM-2CD41LB': 'A_handle/double_sided_5pack_light_blue', 'IDM-2CD41DB': 'A_handle/double_sided_5pack_dark_blue',
    'IDM-3CD41H': 'B_heads/double_sided_heads_5pack',
}
if subprocess.run(['git', 'status', '--porcelain', 'image_kit'], capture_output=True, text=True).stdout.strip():
    sys.exit('image_kit has uncommitted changes: commit and push them first (the upload links to a commit)')
IMG_SHA = subprocess.run(['git', 'log', '-1', '--format=%H', '--', 'image_kit'], capture_output=True, text=True, check=True).stdout.strip()
IMG_BASE = f'https://raw.githubusercontent.com/ck92-commits/ILLUCO-AMAZON/{IMG_SHA}/image_kit/'
IMG_COLS = ['T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'AA']   # main image + other images 1-7
# B0G2DYRY7T ships the black-shank version (owner, 11/20): its 4 current photos stay (main + other 1-3, left blank so
# the partial update does not touch them) and 5 related kit images fill its empty slots (other 4-8).
KEEP_CURRENT = {'B0G2DYRY7T': ['03_key_benefit', '07_care', '04_magnification', '05_comparison', '06_handle']}
# Amazon refused the 1X Dark Blue 5-pack photo (the live main of B0FCZBD1KY) as the main of the 2X and 3X Dark Blue
# 5-packs: error 100560 "does not accurately represent the product", then 18320 "main image missing" (both listings
# suppressed, 11/21 and 11/23). They get their own main: a new image, as the Light Blue 5-packs got (accepted).
MAIN_OVERRIDE = {'B0F84TKGLS': 'main_alt_2x3x.jpg', 'B0F85B5BDC': 'main_alt_2x3x.jpg'}
# Live listings whose MAIN changes (new product-only mains, owner 11/23). Their main goes in the step-1 file as an
# image-only row, not in this file: an image Amazon refuses must not take the family move in the same row with it
# (independent review, 11/23). Every other live main in this file is pixel-identical to the one accepted on 11/23.
MAIN_IN_STEP1 = {'B0F84VWGG5', 'B0FCMVZH31', 'B0F857HKBG',        # Light Blue 5-packs: box shot -> product only
                 'B0F84TKGLS', 'B0F85B5BDC',                      # Dark Blue 2X / 3X 5-packs: suppressed, no main
                 'B0FBPG5CS9', 'B0FCHH2SQB', 'B0FCJY3H9H'}        # single-sided heads: box + heads -> heads only
step1_mains = []
# Owner, 11/23: "do not generate images - leave it blank and mark". These kit images are composites (copies or grafts of
# one photo), so their cells stay blank and yellow (the final image pass below clears these cells and sets real photos only); everything else is ILLUCO's own photos
# or slides built on them.
PHOTO_NEEDED = {
    ('A_handle/kit_5pack_light_blue', '01_main'): 'Light Blue 5-pack: 5 mirrors + 5 handles on white, true colour, no box',
    ('A_handle/kit_5pack_dark_blue', 'main_alt_2x3x'): 'Dark Blue 5-pack: 5 mirrors + 5 handles on white, a new photo (not the 1X listing photo)',
    ('A_handle/double_sided_5pack_light_blue', '01_main'): 'Double-Sided 5-pack, Light Blue: 5 assembled mirrors, full length, on white',
    ('A_handle/double_sided_5pack_dark_blue', '01_main'): 'Double-Sided 5-pack, Dark Blue: 5 assembled mirrors, full length, on white',
    ('A_handle/grand_2pack_light_blue', '01_main'): 'Grand 2-pack, Light Blue: 2 complete mirrors on white',
    ('A_handle/grand_2pack_light_blue', '02_whats_in_the_box'): 'Grand kit, Light Blue: box with 2 mirrors and 2 Light Blue handles',
    ('A_handle/grand_2pack_dark_blue', '01_main'): 'Grand 2-pack, Dark Blue: 2 complete mirrors on white',
    ('A_handle/grand_2pack_dark_blue', '02_whats_in_the_box'): 'Grand kit, Dark Blue: box with 2 mirrors and 2 Dark Blue handles',
    ('B_heads/single_sided_heads_5pack', '01_main'): 'Single-sided heads: 5 heads face-on on white, no box',
    ('B_heads/single_sided_heads_5pack', '02_whats_in_the_box'): 'Single-sided heads: what is in the box (5 heads, no handles)',
    ('B_heads/double_sided_heads_5pack', '01_main'): 'Double-Sided heads: 5 heads face-on on white',
    ('B_heads/double_sided_heads_5pack', '02_whats_in_the_box'): 'Double-Sided heads: what is in the box (5 heads, no handles)',
}
NOW_LIVE = {   # what the live listing shows in that slot while the cell stays blank
    ('A_handle/kit_5pack_light_blue', '01_main'): "keeps its live main, ILLUCO's Light Blue box photo",
    ('A_handle/kit_5pack_dark_blue', 'main_alt_2x3x'): 'no main: the listing stays suppressed until this photo is uploaded',
    ('B_heads/single_sided_heads_5pack', '01_main'): "keeps its live main, ILLUCO's box + heads photo",
    ('B_heads/single_sided_heads_5pack', '02_whats_in_the_box'): ('image 2 live since 11/21 is a composite (5 copies of one head): '
                                                                  'delete it in Manage Images or replace it with the new photo'),
}
missing = []
sku_asin = {p['sku']: p['asin'] for p in plan}
for r in range(8, row):
    if t[f'D{r}'].value != 'Child':
        continue
    sku = t[f'A{r}'].value
    key = sku if sku in IMG_DIRS else sku_asin[sku]
    folder = IMG_DIRS[key]
    files = sorted(f.name for f in Path('image_kit', folder).glob('0[1-8]_*.jpg'))
    assert len(files) == 8, (folder, files)
    if key in KEEP_CURRENT:
        pick = [next(f for f in files if f.startswith(p)) for p in KEEP_CURRENT[key]]
        for col in IMG_COLS[:4]:
            c = t[f'{col}{r}']; c.value = None; c.fill = PatternFill(fill_type=None); c.comment = None
        for col, name in zip(['X', 'Y', 'Z', 'AA', 'AB'], pick):
            c = t[f'{col}{r}']; c.value = IMG_BASE + folder + '/' + name; c.fill = PatternFill(fill_type=None); c.comment = None
        continue
    for col, name in zip(IMG_COLS, files):
        c = t[f'{col}{r}']
        if col == 'T' and key in MAIN_OVERRIDE:
            name = MAIN_OVERRIDE[key]
            assert Path('image_kit', folder, name).is_file(), name
        c.fill = PatternFill(fill_type=None)
        c.comment = None
        stem = name.rsplit('.', 1)[0]
        if (folder, stem) in PHOTO_NEEDED:
            new = str(t[f'C{r}'].value).startswith('Create')
            live = 'new product, not live yet' if new else NOW_LIVE.get((folder, stem), 'keeps its live image')
            c.value = None
            c.fill = YEL
            c.comment = Comment(f'MISSING, real photo requested from Ashley: {PHOTO_NEEDED[(folder, stem)]}. '
                                f'No generated image (owner, 11/23). Meanwhile: {live}.', 'ILLUCO audit')
            missing.append(dict(sku=sku, asin='(new)' if new else key, column=col,
                                slot='Main image' if col == 'T' else f'Image {IMG_COLS.index(col) + 1}',
                                photo=PHOTO_NEEDED[(folder, stem)], meanwhile=live))
            continue
        c.value = IMG_BASE + folder + '/' + name
        if col == 'T' and key in MAIN_IN_STEP1:
            step1_mains.append(dict(sku=sku, asin=key, main_url=c.value))
            c.value = None
    c = t[f'AB{r}']; c.value = None; c.fill = PatternFill(fill_type=None); c.comment = None
print('images linked at', IMG_SHA[:7])
assert {m['asin'] for m in step1_mains} <= MAIN_IN_STEP1

# Owner, 11/24: use every real photo we have (ILLUCO's own photos come from Ashley too) and request nothing new for now.
# Live listings need no images in a partial update (a blank cell keeps what they show), except where the 11/21-11/23
# uploads left something wrong: the Dark Blue 2X/3X and the Light Blue 5-packs get back their own mains from before
# 11/21, and the heads get ILLUCO's single-head photo as image 2 in place of a composite. New products get ILLUCO's own
# photos (illuco.com, or the Drive originals in image_kit/illuco_originals, unchanged). Every main is on white.
AMZ_I = 'https://m.media-amazon.com/images/I/'
ORIG_SHA = subprocess.run(['git', 'log', '-1', '--format=%H', '--', 'image_kit/illuco_originals'], capture_output=True,
                          text=True, check=True).stdout.strip()
ORIG = f'https://raw.githubusercontent.com/ck92-commits/ILLUCO-AMAZON/{ORIG_SHA}/image_kit/illuco_originals/'
N_LB = "Restored: this listing's own main from before 11/21 (500 px)."
N_DB = ("Restored: this listing's own main from before 11/21 (500 px). Lifts the suppression if Amazon accepts it; it "
        "refused a 2000 px copy of this photo on 11/21 (100560).")
REAL = {   # ASIN (live) or SKU (new) -> {column: (url, note on the stand-in or None)}
    **{a: {'T': (AMZ_I + '41Uw02dXsML.jpg', N_LB)} for a in ('B0F84VWGG5', 'B0FCMVZH31', 'B0F857HKBG')},
    **{a: {'T': (AMZ_I + '41%2BEMJIHFJL.jpg', N_DB)} for a in ('B0F84TKGLS', 'B0F85B5BDC')},
    **{a: {'U': (SHOP + 'single-head.jpg', None)} for a in ('B0FBPG5CS9', 'B0FCHH2SQB', 'B0FCJY3H9H')},
    **{k: {'T': (SHOP + 'main_1b36fb35-6c34-4a82-81aa-68ef89447d58.jpg', None), 'U': (SHOP + 'grand-01.jpg', None),
           'V': (SHOP + 'grand-02.jpg', None), 'W': (ORIG + 'grand-04.jpg', None)} for k in ('IDM-2C101LB', 'IDM-2C102LB')},
    **{k: {'T': (SHOP + 'main_db.jpg', None), 'U': (ORIG + 'grand-01_db.jpg', None), 'V': (SHOP + 'grand-02.jpg', None),
           'W': (ORIG + 'grand-04.jpg', None)} for k in ('IDM-2C101DB', 'IDM-2C102DB')},
    'IDM-2CD41LB': {'T': (SHOP + 'main.jpg', None), 'U': (SHOP + 'dsdm-01.jpg', None), 'V': (SHOP + 'dsdm-02.jpg', None),
                    'W': (SHOP + 'dsdm-03.jpg', None), 'X': (SHOP + 'dsdm-04.jpg', None)},
    'IDM-2CD41DB': {'T': (ORIG + 'ds_main_db.jpg', None), 'U': (ORIG + 'dsdm-01_db.jpg', None),
                    'V': (ORIG + 'dsdm-02_db.jpg', None), 'W': (ORIG + 'dsdm-03_db.jpg', None), 'X': (SHOP + 'dsdm-04.jpg', None)},
    'IDM-3CD41H': {'T': (SHOP + 'double-head_7873821b-dd72-4a9a-8cea-7147a90c92c9.jpg', None)},
}
image_list = []
for r in range(8, row):
    if t[f'D{r}'].value != 'Child':
        continue
    sku = t[f'A{r}'].value
    new = str(t[f'C{r}'].value).startswith('Create')
    asin = '(new)' if new else sku_asin.get(sku, '')
    for col in IMG_COLS + ['AB']:
        c = t[f'{col}{r}']
        c.value = None; c.fill = PatternFill(fill_type=None); c.comment = None
    plan_ = REAL.get(sku if new else asin, {})
    for col, (url, note) in plan_.items():
        c = t[f'{col}{r}']
        c.value = url
    main_url, main_note = plan_.get('T', (None, None))
    if main_url:
        main_after = 'restored own main from before 11/21' if main_note else "ILLUCO's own photo"
    else:
        main_after = 'its live main stays'
    sent = [col for col in IMG_COLS if t[f'{col}{r}'].value]
    image_list.append(dict(sku=sku, asin=asin, family=FAM_OF_PARENT[t[f'E{r}'].value], size=t[f'BB{r}'].value or '',
                           color=t[f'BA{r}'].value or '', main_after=main_after,
                           note=main_note or '', images_in_upload=', '.join(sent) or 'none'))
with open('data/build/image_list.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(image_list[0].keys())); w.writeheader(); w.writerows(image_list)
print('image cells filled with real images:', sum(1 for x in image_list for _ in x['images_in_upload'].split(', ') if x['images_in_upload'] != 'none'))
with open('data/build/step1_mains.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['sku', 'asin', 'main_url']); w.writeheader(); w.writerows(step1_mains)
print('mains moved to step 1:', len(step1_mains))

# ---- order the rows parent -> its children (owner: "Parent, its children, next parent, its children") ----
# Families: 5-pack, single, Grand, heads. Within a family: single-sided before Double-Sided, then 1X/2X/3X, Light Blue
# before Dark Blue. Parent rows are bold on a light fill and child SKUs are indented (formatting only).
import re as _re
from openpyxl.styles import Font, Alignment
COLOR_ORDER = {'Light Blue': 0, 'Dark Blue': 1}
def row_key(r):
    sku = t[f'A{r}'].value
    if t[f'D{r}'].value == 'Parent':
        return (FAM_ORDER.index(FAM_OF_PARENT[sku]), 0, 0, '', 0, '')
    size = str(t[f'BB{r}'].value or '')
    m = _re.search(r'(\d)X$', size)
    return (FAM_ORDER.index(FAM_OF_PARENT[t[f'E{r}'].value]), 1, 1 if 'Double-Sided' in size else 0,
            m.group(1) if m else '9', COLOR_ORDER.get(t[f'BA{r}'].value, 2), sku)
order = sorted(range(8, row), key=row_key)
maxc = t.max_column
snap = [[(t.cell(r, c_).value, copy.copy(t.cell(r, c_)._style), copy.copy(t.cell(r, c_).comment) if t.cell(r, c_).comment else None)
         for c_ in range(1, maxc + 1)] for r in order]
for r in range(8, row):
    for c_ in range(1, maxc + 1):
        t.cell(r, c_).comment = None
for i, cells in enumerate(snap):
    r = 8 + i
    for c_, (v, st, cm) in enumerate(cells, 1):
        cell = t.cell(r, c_)
        cell.value = v; cell._style = st; cell.comment = cm
PARENT_FILL = PatternFill(fill_type='solid', fgColor='DDEBF7')
for r in range(8, row):
    if t[f'D{r}'].value == 'Parent':
        for c_ in range(1, maxc + 1):
            cell = t.cell(r, c_)
            if not (cell.fill and cell.fill.fill_type and str(cell.fill.fgColor.rgb).endswith('FFFF00')):
                cell.fill = PARENT_FILL
            f_ = copy.copy(cell.font); f_.bold = True; cell.font = f_
    else:
        a_ = t[f'A{r}'].alignment
        t[f'A{r}'].alignment = Alignment(horizontal='left', vertical=a_.vertical, indent=2)
pos = {t[f'A{r}'].value: r for r in range(8, row)}
plan.sort(key=lambda p: pos.get(p['sku'].replace(' (INFERRED)', ''), 10 ** 6))
print('row order:', ' | '.join(f"{t[f'A{r}'].value}" for r in range(8, row)))

# ---- fixes for Amazon's upload review (owner screenshot, 11/20) ----
# Item Highlight max 125 characters; Included Components short (the long lists were rejected); item thickness is
# required on new listings (parents too); the new Double-Sided heads need package size and weight.
YEL_NOTE = 'ILLUCO audit'
def components(r):
    size = str(t[f'BB{r}'].value or ''); n = int(float(t[f'AY{r}'].value or 0)); fam = kind_of(FAM_OF_PARENT[t[f'E{r}'].value])
    if 'Grand' in size:
        return f'{n} Grand Mirrors and {n} Handles'
    if 'Double-Sided' in size:
        return f'{n} Double-Sided Mirrors and {n} Handles' if fam == 'A' else f'{n} Double-Sided Mirror Heads'
    if fam == 'B':
        return f'{n} Mirror Heads'
    return '1 Mirror Head and 1 Handle' if n == 1 else f'{n} Mirror Heads and {n} Handles'
THICK = {'A': ('0.4', 'Estimate: the handle is about 10 mm (0.4 in) at its thickest, judged from product photos. '
                      'Measure one and correct if different.'),
         'B': ('0.15', 'Estimate: a mirror head is about 4 mm (0.15 in) thick. Measure one and correct if different.')}
for r in range(8, row):
    is_parent = t[f'D{r}'].value == 'Parent'
    fam = kind_of(FAM_OF_PARENT[t[f'A{r}'].value if is_parent else t[f'E{r}'].value])
    if not is_parent:
        t[f'BM{r}'] = components(r)
        t[f'P{r}'] = harmonized_model(t[f'BB{r}'].value, t[f'AY{r}'].value, t[f'BA{r}'].value or '', fam)
        assert len(t[f'BM{r}'].value) <= 40, t[f'BM{r}'].value
    assert len(t[f'H{r}'].value or '') <= 125, (t[f'A{r}'].value, len(t[f'H{r}'].value))
    if str(t[f'C{r}'].value).startswith('Create'):
        val, note = THICK[fam]
        t[f'BV{r}'] = val; t[f'BW{r}'] = val; t[f'BX{r}'] = 'Inches'
        t[f'BV{r}'].fill = YEL; t[f'BV{r}'].comment = Comment(note, YEL_NOTE)
        if is_parent:
            t[f'FA{r}'] = 'No'          # Are batteries required? (Amazon review flagged it on the parents)
        else:
            t[f'EW{r}'] = 1             # Number of Boxes: each product ships in one box (flagged on the 7 new children)
    if t[f'A{r}'].value == 'IDM-3CD41H':
        for col, v in (('EO', '8.27'), ('EP', 'Inches'), ('EQ', '3.94'), ('ER', 'Inches'), ('ES', '1.38'), ('ET', 'Inches'),
                       ('EU', '0.3'), ('EV', 'Pounds')):
            t[f'{col}{r}'] = v
        t[f'EO{r}'].comment = Comment('Estimate: same box size as the Double-Sided 5-pack kit (8.27 x 3.94 x 1.38 in) and about '
                                      '0.3 lb (the single-sided heads list 3.2 oz). Measure the heads box and correct; FBA '
                                      're-measures at check-in.', YEL_NOTE)

# Size values as shoppers see them: magnification first (owner, 11/24). All logic above used the internal keys.
for r in range(8, row):
    if t[f'D{r}'].value == 'Child' and t[f'BB{r}'].value:
        t[f'BB{r}'] = size_name(t[f'BB{r}'].value)
for p in plan:
    if p.get('size'):
        p['size'] = size_name(p['size'])
_seen = {}
for r in range(8, row):
    if t[f'D{r}'].value == 'Child':
        k = (t[f'E{r}'].value, t[f'BB{r}'].value, t[f'BA{r}'].value)
        _seen.setdefault(k, set()).add(asin_by_sku.get(t[f'A{r}'].value) or t[f'A{r}'].value)
assert all(len(v) == 1 for v in _seen.values()), {k: v for k, v in _seen.items() if len(v) > 1}

from xlsx_thin import thin_rows
thin_rows(wb)   # owner: every row at the default thin height

wb.save(OUT)   # one file (owner, 11/20): parents, existing listings and the 7 new products together
with open(PLAN, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(plan[0].keys())); w.writeheader(); w.writerows(plan)
print('rows', row - 8, 'plan', len(plan))
