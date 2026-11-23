"""Check ILLUCO_Amazon_UPLOAD.xlsx against the template's own rules before it goes to Amazon.
Writes data/build/upload_check.csv (level, row, sku, column, issue), or the CSV path given as the 2nd argument."""
import sys, re, csv, json, urllib.request, openpyxl
from openpyxl.utils import range_boundaries, get_column_letter
sys.path.insert(0, 'scripts')
from existing_listing_content import ROWS
F = sys.argv[1] if len(sys.argv) > 1 else 'ILLUCO_Amazon_UPLOAD.xlsx'
DELETED_PARENTS = {'IDM-HANDLE-FAMILY-PARENT'}   # ILLUCO_Amazon_DELETE_old_parents.xlsx removes it first (11/23)
wb = openpyxl.load_workbook(F)
t = wb['Template']
hdr = {c.column_letter: c.value for c in t[4] if c.value}
issues = []
def add(level, r, col, msg):
    issues.append((level, r, t[f'A{r}'].value, f'{col} {hdr.get(col, "")}'.strip(), msg))
rows = [r for r in range(8, t.max_row + 1) if t[f'A{r}'].value]

# 1. dropdown values, resolved from the template's own data validations
def resolve(f1, row=None):
    f1 = f1.strip()
    m = re.match(r'^INDIRECT\(.*&"([^"]+)"\)$', f1)
    if m and row is not None:            # Amazon's per-product-type lists: <PRODUCT_TYPE><attribute suffix>
        pt = str(t[f'B{row}'].value or '')
        name = ('_' if pt[:1].isdigit() else '') + pt.replace('-', '_').replace(' ', '') + m.group(1)
        if name in wb.defined_names:
            f1 = name
        else:
            return []                    # no list for this product type -> any value is invalid

    if f1.startswith('"'):
        return [x.strip() for x in f1.strip('"').split(',')]
    ref = f1
    if ref in wb.defined_names:
        ref = wb.defined_names[ref].attr_text
    m = re.match(r"^'?([^'!]+)'?!\$?([A-Z]+)\$?(\d+)(?::\$?([A-Z]+)\$?(\d+))?$", ref)
    if not m:
        return None
    ws = wb[m.group(1)]
    end = f'{m.group(4)}{m.group(5)}' if m.group(4) else f'{m.group(2)}{m.group(3)}'
    c1, r1, c2, r2 = range_boundaries(f'{m.group(2)}{m.group(3)}:{end}')
    return [str(ws.cell(r, c).value) for r in range(r1, r2 + 1) for c in range(c1, c2 + 1) if ws.cell(r, c).value is not None]
checked = unchecked = 0
for dv in t.data_validations.dataValidation:
    if dv.type != 'list' or not dv.formula1:
        continue
    for rng in str(dv.sqref).split():
        c1, r1, c2, r2 = range_boundaries(rng)
        for r in rows:
            if not (r1 <= r <= (r2 or r)):
                continue
            for c in range(c1, (c2 or c1) + 1):
                v = t.cell(r, c).value
                if v in (None, ''):
                    continue
                col = get_column_letter(c)
                allowed = resolve(dv.formula1, r)
                if allowed is None:
                    unchecked += 1
                    continue
                checked += 1
                sv = str(v)
                if 'Price' in str(hdr.get(col, '')) and re.fullmatch(r'\d+(\.\d+)?', sv):
                    continue                     # price lists only offer the "Delete Offer" keyword; numbers are valid
                if sv not in allowed and not (isinstance(v, (int, float)) and str(int(v)) in allowed):
                    add('ERROR', r, col, f'"{sv}" is not in the template dropdown')
# 2. required fields, parentage and variation attributes
parents = {t[f'A{r}'].value: t[f'F{r}'].value for r in rows if t[f'D{r}'].value == 'Parent'}
need = {'SIZE': ['BB'], 'COLOR': ['BA'], 'NUMBER_OF_ITEMS': ['AY']}
skus = [t[f'A{r}'].value for r in rows]
for s in set(skus):
    if skus.count(s) > 1:
        add('ERROR', rows[skus.index(s)], 'A', f'SKU {s} appears {skus.count(s)} times')
for r in rows:
    act, lvl = t[f'C{r}'].value, t[f'D{r}'].value
    for col in ('A', 'B', 'C'):
        if not t[f'{col}{r}'].value:
            add('ERROR', r, col, 'required value missing')
    if act.startswith('Create'):
        req = ['G', 'I', 'AD', 'AE', 'EZ', 'FX'] + ([] if lvl == 'Parent' else ['J', 'K'])
        for col in req:
            if not t[f'{col}{r}'].value:
                add('ERROR', r, col, 'required for Create rows')
    if 'NUMBER_OF_ITEMS' in str(t[f'F{r}'].value or ''):
        add('ERROR', r, 'F', 'one pack size per family (owner, 11/23): the theme must not vary Number of Items')
    if lvl == 'Child':
        p = t[f'E{r}'].value
        known = {'IDM-5PACK-FAMILY-PARENT': 'COLOR/SIZE', 'IDM-SINGLE-FAMILY-PARENT': 'COLOR/SIZE',
                 'IDM-GRAND-FAMILY-PARENT': 'COLOR/SIZE', 'IDM-HEADS-FAMILY-PARENT': 'SIZE'}
        if p in DELETED_PARENTS:
            add('ERROR', r, 'E', f'parent {p} is deleted by the delete file before this upload')
        elif p not in parents and p in known:
            if t[f'F{r}'].value != known[p]:   # parent comes from ILLUCO_Amazon_UPLOAD.xlsx, uploaded first
                add('ERROR', r, 'F', 'variation theme differs from the parent')
        elif p not in parents:
            add('ERROR', r, 'E', f'parent SKU {p} is not created in this file')
        elif t[f'F{r}'].value != parents[p]:
            add('ERROR', r, 'F', 'variation theme differs from the parent')
        for part in (t[f'F{r}'].value or '').split('/'):
            for col in need.get(part, []):
                if t[f'{col}{r}'].value in (None, ''):
                    add('ERROR', r, col, f'theme {t[f"F{r}"].value} needs this value')
# 3. one ASIN per variation combination of the family's theme (several SKUs of one ASIN may share it), and one pack
# size per family (owner, 11/23: "separate the quantities")
asin_of = {sku: rr['asin'] for rr in ROWS for sku, _ in rr['skus']}
theme_col = {'SIZE': 'BB', 'COLOR': 'BA', 'NUMBER_OF_ITEMS': 'AY'}
combo, packs = {}, {}
for r in rows:
    if t[f'D{r}'].value != 'Child':
        continue
    key = (t[f'E{r}'].value,) + tuple(t[f'{theme_col.get(p, "BB")}{r}'].value for p in str(t[f'F{r}'].value or '').split('/'))
    combo.setdefault(key, set()).add(asin_of.get(t[f'A{r}'].value, 'new:' + t[f'A{r}'].value))
    packs.setdefault(t[f'E{r}'].value, {}).setdefault(t[f'AY{r}'].value, []).append(r)
for key, asins in combo.items():
    if len(asins) > 1:
        add('ERROR', rows[0], 'BB', f'two different products share {key}: {sorted(asins)}')
for p, by_n in packs.items():
    if len(by_n) > 1:
        for n, rs in by_n.items():
            for r in rs:
                add('ERROR', r, 'AY', f'family {p} mixes pack sizes {sorted(map(str, by_n))}: keep one per family')
# 4. text limits and style rules
caps = re.compile(r'\b[A-Z]{4,}\b')
for r in rows:
    g = t[f'G{r}'].value or ''
    if len(g) > 200:
        add('ERROR', r, 'G', f'title {len(g)} > 200 characters')
    if len(g) >= 75 and t[f'D{r}'].value == 'Child':
        add('WARN', r, 'G', f'title {len(g)} characters: Item Highlight will not show (needs < 75)')
    for col in ('AE', 'AF', 'AG', 'AH', 'AI'):
        b = t[f'{col}{r}'].value or ''
        if len(b) > 500:
            add('ERROR', r, col, f'bullet {len(b)} > 500 characters')
        bad = [w for w in caps.findall(b) if w not in ('ILLUCO', 'UHD')]
        if bad:
            add('WARN', r, col, f'all-caps words: {bad[:4]}')
    if t[f'D{r}'].value == 'Child':            # harmony: names follow one pattern (owner, 11/21)
        pm = str(t[f'P{r}'].value or '')
        if not pm or pm.upper().startswith('IDM') or len(pm) > 40:
            add('ERROR', r, 'P', f'Model Number must read as a product name (max 40), not a code: {pm!r}')
        n = int(float(t[f'AY{r}'].value or 0)); col = str(t[f'BA{r}'].value or '')
        if f'{n} Pack' not in g:
            add('ERROR', r, 'G', f'title does not say "{n} Pack" (Number of Items is {n})')
        if col and not g.endswith(col):
            add('ERROR', r, 'G', f'title does not end with the color {col}')
        if 'Heads' not in g and ((n > 1) != ('Dental Mirrors' in g)):
            add('ERROR', r, 'G', 'use "Dental Mirrors" for packs and "Dental Mirror" for a single')
    h = t[f'H{r}'].value or ''
    if h and t[f'D{r}'].value == 'Parent':
        add('ERROR', r, 'H', 'leave Item Highlight empty on parent rows (Amazon flags it there)')
    if len(h) > 125:
        add('ERROR', r, 'H', f'Item Highlight {len(h)} > 125 characters (Amazon rejects it)')
    bm = t[f'BM{r}'].value or ''
    if len(bm) > 50:
        add('ERROR', r, 'BM', f'Included Components {len(bm)} characters: Amazon rejected 87+; keep it short')
    if str(t[f'C{r}'].value).startswith('Create'):
        if not t[f'BV{r}'].value or not t[f'BX{r}'].value:
            add('ERROR', r, 'BV', 'item thickness and its unit are required on new listings')
        if not t[f'FA{r}'].value:
            add('ERROR', r, 'FA', 'Are batteries required? is required on new listings')
        if t[f'D{r}'].value == 'Child':
            if not t[f'EW{r}'].value:
                add('ERROR', r, 'EW', 'Number of Boxes is required on new products')
            for col in ('EO', 'EP', 'EQ', 'ER', 'ES', 'ET', 'EU', 'EV'):
                if not t[f'{col}{r}'].value:
                    add('ERROR', r, col, 'package size and weight (with units) are required on new listings')
    kw = t[f'AJ{r}'].value or ''
    if len(kw.encode()) > 249:
        add('ERROR', r, 'AJ', f'keywords {len(kw.encode())} bytes > 249')
    if len(t[f'AD{r}'].value or '') > 2000:
        add('ERROR', r, 'AD', 'description > 2000 characters')
    txt = ' '.join(str(c.value) for c in t[r] if isinstance(c.value, str))
    for claim in ['Fog-Resistant', 'anti fog', 'Anti-Fog', 'Autoclavable 100X', '100 autoclave cycles']:
        if claim.lower() in txt.lower() and '100+ autoclave' not in claim:
            add('WARN', r, '-', f'contains "{claim}"')
# 5. product IDs, prices, image URLs
for r in rows:
    k = t[f'K{r}'].value
    if k:
        d = [int(x) for x in str(k)]
        ok = len(d) == 12 and (10 - sum(d[i] * (3 if i % 2 == 0 else 1) for i in range(11)) % 10) % 10 == d[11]
        if not ok:
            add('ERROR', r, 'K', f'UPC {k} fails the check digit')
    for col in ('CF', 'DI'):
        v = t[f'{col}{r}'].value
        if v not in (None, ''):
            try:
                if float(v) <= 0:
                    add('ERROR', r, col, 'price must be > 0')
            except ValueError:
                add('ERROR', r, col, f'price "{v}" is not a number')
    if t[f'CF{r}'].value and t[f'DI{r}'].value and float(t[f'CF{r}'].value) < float(t[f'DI{r}'].value):
        add('ERROR', r, 'CF', 'list price below your price')
urls = {}
for r in rows:
    for col in ('T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'AA', 'AB'):
        u = t[f'{col}{r}'].value
        if u:
            urls.setdefault(u, []).append((r, col))
for u, places in urls.items():
    try:
        req = urllib.request.Request(u, method='HEAD')
        code = urllib.request.urlopen(req, timeout=20).status
    except Exception as e:
        code = str(e)[:60]
    if code != 200:
        for r, col in places:
            add('ERROR', r, col, f'image URL not reachable ({code})')
for r in rows:
    if t[f'D{r}'].value == 'Child' and t[f'C{r}'].value.startswith('Create') and not t[f'T{r}'].value:
        add('WARN', r, 'T', 'new product has no main image URL yet (upload works; listing is not buyable until an image is added)')
with open(sys.argv[2] if len(sys.argv) > 2 else 'data/build/upload_check.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['level', 'row', 'sku', 'column', 'issue']); w.writerows(issues)
print(f'rows {len(rows)}, dropdown cells checked {checked}, not resolvable {unchecked}, image URLs {len(urls)}')
print('ERRORS', sum(1 for i in issues if i[0] == 'ERROR'), 'WARNINGS', sum(1 for i in issues if i[0] == 'WARN'))
for i in issues:
    print(i)
