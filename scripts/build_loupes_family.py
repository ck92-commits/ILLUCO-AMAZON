"""ILLUCO_Amazon_LOUPES_family.xlsx: one variation family for the 9 ILLUCO 3.3X flip-up loupes that stand alone today
(owner, 11/24). Parent IDM-LOUPE-FAMILY-PARENT, theme COLOR/SIZE: Color = frame (Matte Black, Coffee, Sports),
Size = working distance (37, 42 or 47 cm). The 9 children are live ASINs (inactive, 0 stock) and only get the link:
Edit (Partial Update) with parentage, parent SKU, theme, color and size. SKUs and ASINs from the All Listings Report of
11/24. Assumes the loupes' product type is PROFESSIONAL_HEALTHCARE: check it on a loupe's Edit page before uploading.
usage: build_loupes_family.py <template .xlsx> <out .xlsx>"""
import copy, sys
import openpyxl
from openpyxl.comments import Comment
from openpyxl.styles import PatternFill

sys.path.insert(0, 'scripts')
from xlsx_thin import thin_rows

PT, PARENT = 'PROFESSIONAL_HEALTHCARE', 'IDM-LOUPE-FAMILY-PARENT'
YEL = PatternFill('solid', fgColor='FFFF00')
WD = {'37': '37 cm (14.5 in)', '42': '42 cm (16.5 in)', '47': '47 cm (18.5 in)'}
CHILDREN = [   # (SKU, ASIN, frame color, working distance cm)
    ('IFL-1033G-37-Classic', 'B0F7YT6N5Q', 'Matte Black', '37'),
    ('96-GOTG-T12P', 'B0F7ZYNX44', 'Coffee', '37'),
    ('IFL-1033G-37-Sports', 'B0F7ZQ115H', 'Sports', '37'),
    ('IFL-1033G-42-Classic', 'B0F7YX71L1', 'Matte Black', '42'),
    ('IFL-1033G-42-Coffee', 'B0F7ZPJ7ZS', 'Coffee', '42'),
    ('IFL-1033G-42-Sports', 'B0F817H83P', 'Sports', '42'),
    ('IFL-1033G-47-Classic', 'B0F7ZJYFKX', 'Matte Black', '47'),
    ('IFL-1033G-47-Coffee', 'B0F8154YTQ', 'Coffee', '47'),
    ('IFL-1033G-47-Sports', 'B0F7ZRZRW9', 'Sports', '47'),
]
DESC = ("ILLUCO flip-up dental loupes with 3.3X magnification and a 10.5 cm field of view. Choose the working distance "
        "that fits your posture: 37 cm, 42 cm or 47 cm. The flip-up design lets you lift the optics out of your line of "
        "sight between tasks, and the adjustable pupil distance gives a personalized, comfortable fit. Made for "
        "dentists, hygienists and other professionals who need a clear, magnified view. Each set includes a case, "
        "cleaning cloth, cleaning solution, 2 head straps, an extra nose pad and extra screws.")
TPL, OUT = sys.argv[1:3]
wb = openpyxl.load_workbook(TPL)
t = wb['Template']
blank = copy.copy(t.cell(900, 1)._style)
for r in range(8, t.max_row + 1):
    for c in range(1, t.max_column + 1):
        cell = t.cell(r, c)
        if cell.value is not None or cell.comment:
            cell.value = None; cell.comment = None
        cell._style = copy.copy(blank)
parent = {'A': PARENT, 'B': PT, 'C': 'Create or Replace (Full Update)', 'D': 'Parent', 'F': 'COLOR/SIZE', 'I': 'ILLUCO',
          'G': 'ILLUCO Flip-Up Dental Loupes, 3.3X Magnification, 37, 42 or 47 cm Working Distance',
          'AD': DESC,
          'L': 'Industrial & Scientific > Professional Dental Supplies > Infection Control > Eyewear (professional-dental-eyewear)',
          'AE': ('3.3X Magnification, Flip-Up Design: A clear, magnified view with a 10.5 cm field of view; flip the optics '
                 'up between tasks without taking the loupes off.'),
          'AF': ('Choose Your Working Distance: 37 cm, 42 cm or 47 cm, to match your working posture. Adjustable pupil '
                 'distance for a personalized fit.'),
          'AG': ('Three Frames: Matte Black, Coffee or Sports. Each set includes a case, cleaning cloth, cleaning solution, '
                 '2 head straps, an extra nose pad and extra screws.'),
          'AJ': 'dental loupes flip up magnifying glasses dentist hygienist surgical loupe 3.3x magnification working distance',
          'EZ': 'Republic of Korea', 'FX': 'Not Applicable', 'FA': 'No',
          'BV': '1.6', 'BW': '1.6', 'BX': 'Inches'}
for col, v in parent.items():
    t[f'{col}8'] = v
for col, note in (('EZ', 'Country of origin of the loupes: Republic of Korea assumed (as the mirrors). Correct it if '
                         'they are made elsewhere.'),
                  ('BV', 'Estimate: about 1.6 in (4 cm) deep for a loupe frame. Amazon requires it on new listings; '
                         'correct it if you have the measurement.'),
                  ('L', 'The Professional Healthcare template has no loupe category; Eyewear is the closest. Only the '
                        'parent gets it; the 9 loupes keep their own category.')):
    t[f'{col}8'].fill = YEL
    t[f'{col}8'].comment = Comment(note, 'ILLUCO audit')
for i, (sku, asin, color, wd) in enumerate(CHILDREN):
    r = 9 + i
    t[f'A{r}'], t[f'B{r}'], t[f'C{r}'], t[f'D{r}'] = sku, PT, 'Edit (Partial Update)', 'Child'
    t[f'E{r}'], t[f'F{r}'], t[f'BA{r}'], t[f'BB{r}'] = PARENT, 'COLOR/SIZE', color, WD[wd]
combos = {(c, w) for _, _, c, w in CHILDREN}
assert len(combos) == len(CHILDREN) == 9
thin_rows(wb)
wb.save(OUT)
print('parent', PARENT, '| children', len(CHILDREN))
for sku, asin, c, w in CHILDREN:
    print(f'  {sku:<22} {asin}  Color={c:<12} Size={WD[w]}')
