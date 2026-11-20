"""Fill UPCs, add the Double-Sided head row and apply copy fixes to the
Grand / Double-Sided Amazon upload template. Writes a new file; the original is untouched."""
import sys, copy, csv, openpyxl
SRC, DST, LOG = sys.argv[1], sys.argv[2], sys.argv[3]
wb = openpyxl.load_workbook(SRC)
ws = wb['Template']
changes = []

def setv(cell, new, why):
    old = ws[cell].value
    if old != new:
        ws[cell].value = new
        changes.append((cell, ws['A' + ''.join(ch for ch in cell if ch.isdigit())].value, why, old, new))

UPC = {'IDM-2C101DB': '810194860836', 'IDM-2C101LB': '810194860843',
       'IDM-2C102DB': '810194860850', 'IDM-2C102LB': '810194860867',
       'IDM-2CD41DB': '810194860874', 'IDM-2CD41LB': '810194860881'}
rows = {ws[f'A{r}'].value: r for r in range(8, 15)}

# 1) UPCs
for sku, upc in UPC.items():
    setv(f'K{rows[sku]}', upc, 'UPC supplied by ILLUCO (check digit verified)')

# 2) Titles kept as supplied: they are under 75 characters on purpose so Amazon shows the
#    Item Highlight (title_differentiation) in search, per the template's Data Definitions.

# 3) "Autoclavable 100X" reads like a magnification next to 1X/2X -> say "rated 100 cycles"
for r in range(8, 15):
    h = ws[f'H{r}'].value
    if h and 'Autoclavable 100X' in h:
        setv(f'H{r}', h.replace('Autoclavable 100X', 'Autoclave-Rated 100 Cycles'), '"100X" confused with magnification')
    ah = ws[f'AH{r}'].value
    if ah:
        new = ah.replace('FOG-RESISTANT AND AUTOCLAVABLE 100X:', 'FOG-RESISTANT, AUTOCLAVE-RATED FOR 100 CYCLES:') \
                .replace('AUTOCLAVABLE 100X:', 'AUTOCLAVE-RATED FOR 100 CYCLES:')
        setv(f'AH{r}', new, '"100X" confused with magnification')

# 4) Unsourced competitor reflectance figure
for sku in ('IDM-2CD41LB', 'IDM-2CD41DB'):
    r = rows[sku]
    ae = ws[f'AE{r}'].value
    setv(f'AE{r}', ae.replace('60-70% of light, rhodium 80-85%.', '60-70% of light.'),
         'Removed unsourced competitor claim (rhodium 80-85%) - restore only with a test report')

# 5) 2X rows: a magnifying (concave) mirror is not "distortion-free" for quadrant photos
for sku in ('IDM-2C102LB', 'IDM-2C102DB'):
    r = rows[sku]
    ad = ws[f'AD{r}'].value
    setv(f'AD{r}', ad.replace('The surface is large and distortion-free enough for clean quadrant photos.',
                              'The 2X magnified view enlarges margins and fine detail; choose the 1X version for life-size quadrant photography.'),
         '2X mirror described as distortion-free')

# 6) New row: Double-Sided Dental Mirror Head (IDM-3CD41H), standalone listing (heads have no handles, so they must not sit in the "with Handles" family)
src, dst = 14, 15
for c in ws[src]:
    t = ws.cell(dst, c.column)
    if c.has_style:
        t._style = copy.copy(c._style)
COPY_COLS = ['B','C','I','J','L','M','Q','AO','AZ','BD','BE','BF','BG','BK','CD','DD','EZ','FA','FX','GH','GU','GV','GW','GX','GY','GZ']
for col in COPY_COLS:
    ws[f'{col}{dst}'].value = ws[f'{col}{src}'].value
head = {
 'A': 'IDM-3CD41H', 'K': '810194860898', 'P': 'IDM-3CD41H', 'BC': 'IDM-3CD41H',
 'G': 'ILLUCO Double-Sided UHD Dental Mirror Heads, Size 4 (22mm), 5 Pack',
 'H': 'Replacement Heads, Handles Not Included, Cone Socket, 1X, 99% Reflectance Both Sides, Fog-Resistant, Autoclave-Rated 100 Cycles',
 'AD': ("The first thing dental professionals notice about an ILLUCO mirror is the view. Most dental mirrors reflect only 60-70% of available light. "
        "ILLUCO's UHD front surface dielectric coating on German optical glass reflects 99%, so the image is over 40% brighter, sharp, true to color and free of the ghost images that cause visual fatigue. "
        "These replacement heads carry that coating on both faces, so you can retract tissue with one side and view with the other without flipping the mirror mid-procedure. "
        "Size 4 (22mm) with a true 1X view for routine exams, restorative checks and indirect vision. The cone socket thread fits standard cone socket mirror handles, including ILLUCO ergonomic handles (sold separately). "
        "A water-repellent coating keeps the view clear, and the heads are rated for 100 autoclave cycles. Sterilize at 273°F (134°C) for 5 minutes or 250°F (121°C) for 20 minutes; do not exceed 277°F (136°C). "
        "Each pack includes 5 double-sided Size 4 mirror heads. Handles are not included."),
 'AE': ws[f'AE{src}'].value,
 'AF': 'TWO MIRROR FACES, NO FLIPPING: Retract tissue with one face and view with the other without turning the mirror mid-procedure. Both sides carry the same 99% UHD coating, so there is no weaker side.',
 'AG': 'CONE SOCKET FIT, HANDLES NOT INCLUDED: Threads onto standard cone socket mirror handles, including ILLUCO ergonomic anti-rotation handles. Not for simple stem or European-thread handles. Check your handle before ordering.',
 'AH': ws[f'AH{src}'].value,
 'AI': '5 REPLACEMENT HEADS: 5 double-sided Size 4 (22mm) mirror heads with a true 1X, life-size view. Restock your operatory with the same bright view on both faces. Built for general dentists, hygienists, orthodontists and dental students.',
 'AJ': 'mouth mirror heads replacement refill tops screw on two sided dual dentist dental instruments tooth teeth oral exam intraoral hygienist anti fog number 4 professional dentist mirror for inside mouth hd high definition',
 'AY': 5, 'BB': 'Size 4 (22mm)', 'BM': '5 Double-Sided Size 4 Mirror Heads',
}
for col, v in head.items():
    ws[f'{col}{dst}'].value = v
assert len(head['G']) < 75 and len(head['AJ'].encode()) <= 249
changes.append(('row 15', 'IDM-3CD41H', 'NEW standalone listing: Double-Sided head (UPC 810194860898). Price, images and package dims left blank - must be supplied', '', head['G']))

for r in list(range(8, 16)):
    kw = ws[f'AJ{r}'].value
    if kw: assert len(kw.encode()) <= 249, (r, len(kw.encode()))

wb.save(DST)
with open(LOG, 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['cell', 'sku', 'reason', 'old', 'new']); w.writerows(changes)
print(len(changes), 'changes')
