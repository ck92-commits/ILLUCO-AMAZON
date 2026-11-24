"""ILLUCO_Amazon_SKINSOFT_family.xlsx: rebuilds the Skinsoft facial mask brush family that the 11/24 delete file broke by
deleting its parent HD-FBGB (B0GXC5GWBL). Recreates parent HD-FBGB and links the 2, 3 and 5 packs to it as link-only
Edit rows. Product type COSMETIC_BRUSH and brand Hansderma (owner's screenshot of the 2-pack Edit page, 11/24). Theme
NUMBER_OF_ITEMS (2, 3, 5). The parent gets the required fields: description (the listings' own text), bullets drawn from
it, country of origin (Republic of Korea, owner 11/24). No item type keyword: the children's face-brushes is not
among this template's 6 values, and the field is optional. Needs a COSMETIC_BRUSH template: a template carries its product types (settings 'ptds'), and
the Professional Healthcare one would refuse these rows. Columns are found by attribute key (row 5), not by letter.
validate_upload.py reads Healthcare column letters, so it does not apply here; checked against the template's
Valid Values instead (20 dropdown cells, 0 invalid). The template itself is not committed (account settings row).
usage: build_skinsoft_family.py <COSMETIC_BRUSH template .xlsx> <out .xlsx>"""
import base64, copy, re, sys, urllib.parse
import openpyxl

sys.path.insert(0, 'scripts')
from xlsx_thin import thin_rows

PT, PARENT = 'COSMETIC_BRUSH', 'HD-FBGB'
CHILDREN = [('HD-GB-2pk', 'B0GXC678JG', 2), ('HD-GB-3pk', 'B0GXCB1S1Z', 3), ('HD-GB-5pk', 'B0GXC882P2', 5)]
DESC = ("Smooth, soft and full, give extraordinary coverage for the face with this facial mask brush. Easier to use "
        "around those hard to reach and smaller sections of your face, such as your eyes and nose area. Won't hurt your "
        "skin, good item for make-up and useful. For applying facial masks, smoothing masks.")
BULLETS = ["Soft, Full Bristles: Smooth, even coverage when applying facial masks, and gentle on your skin.",
           "Reaches Small Areas: Easy to use around the eyes, nose and other hard-to-reach parts of the face.",
           "For Masks and Make-Up: Apply and smooth facial masks, or use it for make-up.",
           "Choose Your Pack: 2, 3 or 5 brushes per pack."]
COUNTRY = 'Republic of Korea'   # owner, 11/24
# pack-count themes in order of preference; the first one the template offers is used
THEMES = [('NUMBER_OF_ITEMS', 'number_of_items'), ('ITEM_PACKAGE_QUANTITY', 'item_package_quantity'), ('SIZE', 'size')]

TPL, OUT = sys.argv[1:3]
wb = openpyxl.load_workbook(TPL)
t = wb['Template']
settings = urllib.parse.unquote(t['A1'].value or '')
m = re.search(r'ptds=([A-Za-z0-9+/=]+)', settings)
ptds = base64.b64decode(m.group(1)).decode() if m else ''
assert PT in ptds.split(','), f'template product types {ptds!r} do not include {PT}'
keys = {str(t.cell(5, c).value): c for c in range(1, t.max_column + 1) if t.cell(5, c).value}


def col(prefix):
    hits = [c for k, c in keys.items() if k.startswith(prefix)]
    assert hits, f'no column for {prefix}'
    return hits[0]


offered = set()
for ws in wb.worksheets:
    if ws.title in ('Valid Values', 'Dropdown Lists'):
        for row in ws.iter_rows(values_only=True):
            offered.update(str(v).strip() for v in row if isinstance(v, str))
theme, attr = next((th, a) for th, a in THEMES if th in offered)
blank = copy.copy(t.cell(900, 1)._style)
for r in range(8, t.max_row + 1):
    for c in range(1, t.max_column + 1):
        cell = t.cell(r, c)
        if cell.value is not None or cell.comment:
            cell.value = None; cell.comment = None
        cell._style = copy.copy(blank)


def put(r, prefix, v):
    t.cell(r, col(prefix), v)


put(8, 'contribution_sku#1', PARENT); put(8, 'product_type#1', PT)
put(8, '::record_action', 'Create or Replace (Full Update)')
put(8, 'parentage_level[', 'Parent'); put(8, 'variation_theme#1', theme)
put(8, 'item_name[', 'Skinsoft Facial Mask Brush, Golden Brush'); put(8, 'brand[', 'Hansderma')
put(8, 'product_description[', DESC)
for b, text in zip([c for k, c in sorted(keys.items(), key=lambda kv: kv[1]) if k.startswith('bullet_point[')], BULLETS):
    t.cell(8, b, text)
put(8, 'generic_keyword[', 'facial mask brush face mask applicator brush skincare mask brush soft brush')
put(8, 'country_of_origin[', COUNTRY)
put(8, 'batteries_required[', 'No')
put(8, 'supplier_declared_dg_hz_regulation[', 'Not Applicable')
for i, (sku, asin, n) in enumerate(CHILDREN):
    r = 9 + i
    put(r, 'contribution_sku#1', sku); put(r, 'product_type#1', PT)
    put(r, '::record_action', 'Edit (Partial Update)'); put(r, 'parentage_level[', 'Child')
    put(r, 'child_parent_sku_relationship[', PARENT); put(r, 'variation_theme#1', theme)
    put(r, f'{attr}[', n if attr != 'size' else f'{n} Pack')
thin_rows(wb)
wb.save(OUT)
print('template product types:', ptds, '| theme:', theme)
for sku, asin, n in CHILDREN:
    print(f'  {sku:<10} {asin}  {attr}={n}')
