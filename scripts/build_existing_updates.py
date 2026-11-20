"""Build (a) an ASIN-keyed update sheet for manual Seller Central edits and
(b) an Amazon partial-update template (SKU column to be pasted from the All Listings Report)."""
import sys, json, copy, openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment
sys.path.insert(0, 'scripts')
from existing_listing_content import ROWS, ATTRIBUTE_FIXES, CONFIRM
from links import dp, link

TEMPLATE_SRC, SHEET_OUT, TPL_OUT = sys.argv[1:4]
cat = {x['asin']: x for x in json.load(open('data/raw/illuco_catalog.json'))}

for r in ROWS:
    assert len(r['title']) < 75, (r['asin'], len(r['title']), r['title'])
    assert len(r['keywords'].encode()) <= 249, (r['asin'], len(r['keywords'].encode()))
    for b in r['bullets']:
        assert len(b) <= 500, (r['asin'], len(b))

# (a) human-readable update sheet
wb = openpyxl.Workbook()
ws = wb.active; ws.title = 'Listing Updates'
hdr = ['ASIN', 'Parent ASIN', 'Family', 'Magnification', 'Color', 'Current price', 'Current rating',
       'Current title (live)', 'NEW title (<75 chars)', 'Title length', 'NEW Item Highlight',
       'NEW Bullet 1', 'NEW Bullet 2', 'NEW Bullet 3', 'NEW Bullet 4', 'NEW Bullet 5',
       'NEW Description', 'NEW Generic Keywords (backend)', 'Keyword bytes', 'Size', 'Number of Items',
       'Included Components', 'Suggested Model/Part No. (confirm)', 'Action notes']
ws.append(hdr)
for r in ROWS:
    live = cat.get(r['asin'], {})
    ws.append([r['asin'], r['parent'], r['family'], f"{r['mag']}X", r['color'], live.get('price'),
               r['rating'], live.get('title'), r['title'], None, r['highlight'], *r['bullets'],
               r['description'], r['keywords'], len(r['keywords'].encode()), r['size'], r['items'],
               r['included'], r['model_suggested'], r['note']])
    ws.cell(ws.max_row, 10).value = f'=LEN(I{ws.max_row})'
head_font = Font(name='Arial', bold=True, color='FFFFFF'); fill = PatternFill('solid', fgColor='1F3864')
thin = Side(style='thin', color='BFBFBF')
for c in ws[1]:
    c.font = head_font; c.fill = fill; c.alignment = Alignment(wrap_text=True, vertical='center')
widths = [13, 13, 22, 8, 11, 10, 22, 45, 45, 8, 40] + [55]*5 + [70, 45, 8, 14, 8, 30, 18, 50]
for i, w in enumerate(widths, 1):
    ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
for row in ws.iter_rows(min_row=2):
    for c in row:
        c.font = Font(name='Arial', size=9); c.alignment = Alignment(wrap_text=True, vertical='top')
        c.border = Border(top=thin, bottom=thin, left=thin, right=thin)
for i in range(2, ws.max_row + 1):
    link(ws[f'A{i}'], dp(ws[f'A{i}'].value)); link(ws[f'B{i}'], dp(ws[f'B{i}'].value))
ws.freeze_panes = 'C2'; ws.auto_filter.ref = ws.dimensions

ws2 = wb.create_sheet('Attribute Fixes')
ws2.append(['ASIN / Family', 'Product', 'Problem found on the live listing', 'Fix'])
for x in ATTRIBUTE_FIXES:
    ws2.append(list(x))
    a = x[0].split()[0]
    if a.startswith('B0'): link(ws2.cell(ws2.max_row, 1), dp(a), x[0], size=10)
ws3 = wb.create_sheet('Confirm Before Upload')
ws3.append(['#', 'Item to confirm', 'Owner', 'Confirmed? (Y/N)'])
for i, x in enumerate(CONFIRM, 1): ws3.append([i, x, '', ''])
for w in (ws2, ws3):
    for c in w[1]: c.font = head_font; c.fill = fill
    for row in w.iter_rows(min_row=2):
        for c in row: c.font = Font(name='Arial', size=10); c.alignment = Alignment(wrap_text=True, vertical='top')
    for col, wd in zip('ABCD', (20, 70 if w is ws3 else 28, 60 if w is ws2 else 18, 60 if w is ws2 else 16)):
        w.column_dimensions[col].width = wd
ws4 = wb.create_sheet('How To Apply')
for line in [
    'HOW TO APPLY THESE UPDATES (today)',
    'Option A - manual (no SKUs needed): Seller Central > Catalog > Manage All Inventory > search the ASIN > Edit.',
    '   Paste NEW title, Item Highlight (if the field is shown), bullets, description and generic keywords from the Listing Updates tab.',
    'Option B - bulk: open Existing_Listings_PartialUpdate_Template.xlsx, paste each SKU into column A (the cell comment shows the ASIN),',
    '   then Catalog > Add Products via Upload > Upload your spreadsheet. Listing Action is already "Edit (Partial Update)", so only the filled attributes change.',
    'Do NOT change brand name, price or variation structure in this upload. Variation merges (orphans) go through a separate request.',
    'After upload: check the Processing Report for errors, then re-check each ASIN on amazon.com within 24h.',
]:
    ws4.append([line])
ws4.column_dimensions['A'].width = 150
for row in ws4.iter_rows():
    for c in row: c.font = Font(name='Arial', size=10, bold=(c.row == 1))
wb.save(SHEET_OUT)

# (b) partial-update template built from ILLUCO's own PROFESSIONAL_HEALTHCARE template
tw = openpyxl.load_workbook(TEMPLATE_SRC)
t = tw['Template']
for r in range(8, t.max_row + 1):
    for c in t[r]:
        c.value = None
yellow = PatternFill('solid', fgColor='FFFF00')
start = 8
for i, r in enumerate(ROWS):
    row = start + i
    for c in t[14]:
        if c.has_style:
            t.cell(row, c.column)._style = copy.copy(c._style)
    vals = {'B': 'PROFESSIONAL_HEALTHCARE', 'C': 'Edit (Partial Update)', 'G': r['title'], 'H': r['highlight'],
            'AD': r['description'], 'AE': r['bullets'][0], 'AF': r['bullets'][1], 'AG': r['bullets'][2],
            'AH': r['bullets'][3], 'AI': r['bullets'][4], 'AJ': r['keywords'], 'AY': r['items'],
            'BB': r['size'], 'BM': r['included']}
    if r['color']:
        vals['BA'] = r['color']
    for col, v in vals.items():
        t[f'{col}{row}'] = v
    t[f'A{row}'].fill = yellow
    t[f'A{row}'].comment = Comment(f"Paste the SKU for ASIN {r['asin']} ({r['family']} {r['mag']}X {r['color']}).", 'ILLUCO audit')
tw.save(TPL_OUT)
print('rows', len(ROWS))
