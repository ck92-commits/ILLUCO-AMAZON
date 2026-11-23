"""Step 1 of 2: ILLUCO_Amazon_STEP1_delete_and_mains.xlsx. Upload it first, wait for its processing report, then
upload ILLUCO_Amazon_UPLOAD.xlsx (step 2).

1. Deletes the parent listing IDM-HANDLE-FAMILY-PARENT. That family (11/21) mixed pack sizes under theme
   SIZE/COLOR/NUMBER_OF_ITEMS; the owner wants one pack size per family with Color and Size as the choices (11/23), so
   its listings move to new parents in step 2. A live family's theme cannot be changed in place, and a child can
   belong to only one parent (Amazon 8032), so the old parent goes first. Deleting a parent removes only that parent
   listing: the children keep their ASINs, reviews, stock and offers. IDM-HEADS-FAMILY-PARENT stays.
2. Sets the new product-only main image on the live listings whose main changes (rows written by
   build_merge_upload.py to data/build/step1_mains.csv): image-only "Edit (Partial Update)" rows with SKU, product
   type, action and main image only. Kept apart from the family move in step 2, so an image Amazon refuses cannot
   take a family move with it, and the report shows the image result on its own.
(The first delete file, 11/21, removed the three original parents IDM3C4XXX / B0FDCGG69J, 0Z-AYA6-3N2M / B0GGD9DVP9
and 6B-536I-O2ME / B0FCNL53JN; that is done.)
usage: build_step1.py <template .xlsx> <out .xlsx>   (run build_merge_upload.py first)"""
import sys, copy, csv, openpyxl
sys.path.insert(0, 'scripts')
from xlsx_thin import thin_rows

OLD_PARENTS = [   # (parent SKU, family)
    ('IDM-HANDLE-FAMILY-PARENT', 'mirrors with handles, mixed pack sizes (uploaded 11/21)'),
]
PT = 'PROFESSIONAL_HEALTHCARE'
TPL, OUT = sys.argv[1:3]
mains = list(csv.DictReader(open('data/build/step1_mains.csv', encoding='utf-8')))
assert mains, 'run build_merge_upload.py first'
wb = openpyxl.load_workbook(TPL)
t = wb['Template']
blank = copy.copy(t.cell(900, 1)._style)
for r in range(8, t.max_row + 1):          # clear every data row of the template
    for c in range(1, t.max_column + 1):
        cell = t.cell(r, c)
        if cell.value is not None or cell.comment:
            cell.value = None; cell.comment = None
        cell._style = copy.copy(blank)
r = 8
for sku, _ in OLD_PARENTS:
    t[f'A{r}'], t[f'B{r}'], t[f'C{r}'] = sku, PT, 'Delete'
    r += 1
for m in mains:
    t[f'A{r}'], t[f'B{r}'], t[f'C{r}'], t[f'T{r}'] = m['sku'], PT, 'Edit (Partial Update)', m['main_url']
    r += 1
thin_rows(wb)
wb.save(OUT)
print('rows', r - 8, '| delete:', [s for s, _ in OLD_PARENTS], '| main images:', len(mains))
