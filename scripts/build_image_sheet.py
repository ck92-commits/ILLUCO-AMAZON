"""ILLUCO_SKU_Images.xlsx: one row per listing, one thumbnail per image slot, showing what each listing shows AFTER
ILLUCO_Amazon_UPLOAD.xlsx is processed (owner, 11/24: "I'm confused with the images - a separate file for SKUs and
images"). Reference only, not an Amazon upload.

Live state = what the 11/21-11/23 uploads put on each listing (the 11/23 file, commit 0ad78e0, images at a648d7a;
B0G2DYRY7T kept its own 4 photos; the Dark Blue 2X/3X main was refused). After = live state with this upload's
non-blank image cells on top.
usage: build_image_sheet.py <out .xlsx>"""
import csv, io, json, re, subprocess, sys
import openpyxl
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from PIL import Image

sys.path.insert(0, 'scripts')
from xlsx_thin import thin_rows  # noqa: F401  (rows here need real height for the thumbnails)

OUT = sys.argv[1]
SLOTS = ['T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'AA', 'AB']
SLOT_NAME = ['Main', 'Image 2', 'Image 3', 'Image 4', 'Image 5', 'Image 6', 'Image 7', 'Image 8', 'Image 9']
F = 'Arial'
GREEN, YELLOW, ORANGE, RED, GREY = 'E5F4E4', 'FFF2A8', 'F9D9C4', 'F4C7C3', 'F0EFEC'
THIN = Side(style='thin', color='BFBFBF')
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def load(path_or_rev):
    """Open an image from the working tree, or 'rev:path' from git."""
    if ':' in path_or_rev and not path_or_rev.startswith('/'):
        blob = subprocess.run(['git', 'show', path_or_rev], capture_output=True, check=True).stdout
        return Image.open(io.BytesIO(blob))
    return Image.open(path_or_rev)


idx = {x['url']: x['path'] for x in json.load(open('image_kit/_sources/sources_index.json')) if x.get('path')}


def locate(url):
    m = re.search(r'raw\.githubusercontent\.com/[^/]+/[^/]+/([0-9a-f]{40})/(.+)$', url)
    if m:
        return f'{m.group(1)}:{m.group(2)}'
    u = url.replace('%2B', '+')
    if u in idx:
        return idx[u]
    m = re.search(r'/images/I/([^/]+)$', u)
    if m:
        return 'image_kit/_sources/amazon/' + m.group(1).replace('+', 'PLUS')
    raise KeyError(url)


def short(url):
    name = url.split('/')[-1].replace('%2B', '+')
    return name


def rows_of(path):
    t = openpyxl.load_workbook(path)['Template']
    return {t[f'A{r}'].value: {c: t[f'{c}{r}'].value for c in SLOTS + ['C', 'D', 'E', 'BA', 'BB']}
            for r in range(8, t.max_row + 1) if t[f'A{r}'].value}


prev_blob = subprocess.run(['git', 'show', '0ad78e0:ILLUCO_Amazon_UPLOAD.xlsx'], capture_output=True, check=True).stdout
prev_path = '/tmp/claude-0/-home-user-ILLUCO-AMAZON/708abc4c-dc51-5eee-9ea1-f0a7d8d91b8a/scratchpad/upload_1123.xlsx'
open(prev_path, 'wb').write(prev_blob)
prev = rows_of(prev_path)
cur_wb = openpyxl.load_workbook('ILLUCO_Amazon_UPLOAD.xlsx')
cur_t = cur_wb['Template']
cur = rows_of('ILLUCO_Amazon_UPLOAD.xlsx')
order = [cur_t[f'A{r}'].value for r in range(8, cur_t.max_row + 1) if cur_t[f'A{r}'].value]
plan = {x['sku'].replace(' (INFERRED)', ''): x for x in csv.DictReader(open('data/build/upload_rows.csv', encoding='utf-8'))}
notes = {x['sku']: x for x in csv.DictReader(open('data/build/image_list.csv', encoding='utf-8'))}
FAM = {'IDM-5PACK-FAMILY-PARENT': '5 Pack', 'IDM-SINGLE-FAMILY-PARENT': '1 Pack', 'IDM-GRAND-FAMILY-PARENT': 'Grand 2 Pack',
       'IDM-HEADS-FAMILY-PARENT': 'Heads 5 Pack'}
OWN_B0G2 = ['41DY+Bjl5lL', '51b9bFn2fiL', '61noMl85BeL', '41eq8ArY68L']   # B0G2DYRY7T's own photos, slots 1-4

# group SKUs by ASIN (two SKUs of one ASIN show the same images)
groups = []
seen = {}
for sku in order:
    v = cur[sku]
    if v['D'] != 'Child':
        continue
    asin = plan[sku]['asin']
    key = asin if asin.startswith('B0') else sku
    if key in seen:
        groups[seen[key]]['skus'].append(sku)
        continue
    seen[key] = len(groups)
    groups.append(dict(key=key, asin=asin, skus=[sku], fam=FAM[v['E']], size=v['BB'], color=v['BA'] or '',
                       new=str(v['C']).startswith('Create')))

ISSUE = {   # live images with a known problem (from the image kit manifest)
    'kit_5pack_light_blue/02_whats_in_the_box': 'box print says "Anti-Fog"',
    'kit_5pack_dark_blue/02_whats_in_the_box': 'box print says "Anti-Fog"',
    'kit_5pack_dark_blue/08_applications': 'stock photos, not ILLUCO mirrors',
    'single_1pack_dark_blue/08_applications': 'stock photos, not ILLUCO mirrors',
    'dsdm-03.jpg': 'box print mentions fog resistance', 'dsdm-03_db.jpg': 'box print mentions fog resistance',
    'dsdm-04.jpg': 'stock photos, not ILLUCO mirrors', 'grand-04.jpg': 'stock photos, not ILLUCO mirrors',
}

wb = openpyxl.Workbook()
ws = wb.active
ws.title = 'SKUs and Images'
ws['A1'] = 'ILLUCO SKUs and images: what each listing shows AFTER ILLUCO_Amazon_UPLOAD.xlsx is processed'
ws['A1'].font = Font(name=F, bold=True, size=13)
ws['A2'] = ('Green = real photo.  Orange = live image with a known issue, for later (nothing requested now).  '
            '"NEW" = this upload sets it; everything else is already live and stays.')
ws['A2'].font = Font(name=F, size=10, italic=True)
hdr = ['Family', 'Listing', 'ASIN', 'SKU(s)', 'This upload sets'] + SLOT_NAME + ['Note']
for j, h in enumerate(hdr, 1):
    c = ws.cell(4, j, h)
    c.font = Font(name=F, bold=True, size=10, color='FFFFFF')
    c.fill = PatternFill('solid', fgColor='1F3864')
    c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    c.border = BOX
TH = 96   # thumbnail px
r = 5
tmp_imgs = []
for g in groups:
    sku0 = g['skus'][0]
    live = {s: prev.get(sku0, {}).get(s) for s in SLOTS}
    if g['asin'] == 'B0G2DYRY7T':
        for k, pid in enumerate(OWN_B0G2):
            live[SLOTS[k]] = 'https://m.media-amazon.com/images/I/' + pid + '.jpg'
    if g['asin'] in ('B0F84TKGLS', 'B0F85B5BDC'):
        live['T'] = None            # refused by Amazon (100560): no main live
    if g['new']:
        live = {s: None for s in SLOTS}
    sets = {s: cur[sku0][s] for s in SLOTS if cur[sku0][s]}
    after = {s: sets.get(s) or live.get(s) for s in SLOTS}
    note = notes.get(sku0, {}).get('note', '')
    vals = [g['fam'], f"{g['size']}, {g['color']}".strip(', '), g['asin'] if g['asin'].startswith('B0') else 'new',
            '\n'.join(g['skus']),
            ('\n'.join(f'{SLOT_NAME[SLOTS.index(s)]}: {short(u)}' for s, u in sets.items()) or 'nothing (live images stay)')]
    for j, v in enumerate(vals, 1):
        c = ws.cell(r, j, v)
        c.font = Font(name=F, size=9, bold=(j == 2))
        c.alignment = Alignment(vertical='center', wrap_text=True)
        c.border = BOX
    for k, s in enumerate(SLOTS):
        col = 6 + k
        c = ws.cell(r, col)
        c.border = BOX
        c.alignment = Alignment(horizontal='center', vertical='bottom', wrap_text=True)
        url = after[s]
        if not url:
            if s == 'T':
                c.fill = PatternFill('solid', fgColor=RED)
                c.value = 'NO MAIN'
                c.font = Font(name=F, size=9, bold=True)
            continue
        kit = re.search(r'image_kit/[AB]_\w+/(\w+/\w+)\.jpg$', url)
        tag = kit.group(1) if kit else short(url)
        if tag in ISSUE:
            fill = ORANGE
        else:
            fill = GREEN
        c.fill = PatternFill('solid', fgColor=fill)
        label = ('NEW ' if s in sets else '') + (ISSUE.get(tag, '') if fill == ORANGE else '')
        c.value = label.strip() or None
        c.font = Font(name=F, size=8, bold=s in sets)
        im = load(locate(url)).convert('RGB')
        im.thumbnail((TH, TH))
        bio = io.BytesIO()
        im.save(bio, 'JPEG', quality=80)
        bio.seek(0)
        xi = XLImage(bio)
        xi.width, xi.height = im.size
        ws.add_image(xi, f'{openpyxl.utils.get_column_letter(col)}{r}')
        tmp_imgs.append(bio)
    c = ws.cell(r, 6 + len(SLOTS), note or ('' if not g['new'] else ''))
    c.font = Font(name=F, size=9)
    c.alignment = Alignment(vertical='center', wrap_text=True)
    c.border = BOX
    ws.row_dimensions[r].height = 112
    r += 1
for col, wdt in zip('ABCDE', (11, 22, 12, 17, 26)):
    ws.column_dimensions[col].width = wdt
for k in range(len(SLOTS)):
    ws.column_dimensions[openpyxl.utils.get_column_letter(6 + k)].width = 15.5
ws.column_dimensions[openpyxl.utils.get_column_letter(6 + len(SLOTS))].width = 48
ws.freeze_panes = 'F5'
ws.page_setup.orientation = 'landscape'
ws.page_setup.fitToWidth = 1
ws.page_setup.fitToHeight = 0
ws.sheet_properties.pageSetUpPr.fitToPage = True
ws.print_title_rows = '4:4'

wb.save(OUT)
print('listings', len(groups), 'thumbnails', len(tmp_imgs))
