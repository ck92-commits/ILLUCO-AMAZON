"""Split the built upload in two (owner, 11/24: Amazon's preview flags the 7 new UPCs, still brand IDM SERIES in GS1):
  ILLUCO_Amazon_UPLOAD.xlsx          now: the live listings' changes (3 parents with live children + 19 edit rows)
  ILLUCO_Amazon_NEW_PRODUCTS.xlsx    later, once Verified by GS1 shows brand ILLUCO: the 7 new products + the Grand parent
The combined file is kept as data/build/upload_full.xlsx for the report and the image sheet.
usage: split_new_products.py   (run after build_merge_upload.py)"""
import copy, shutil, sys
import openpyxl

sys.path.insert(0, 'scripts')
from xlsx_thin import thin_rows

SRC, FULL = 'ILLUCO_Amazon_UPLOAD.xlsx', 'data/build/upload_full.xlsx'
NEW_PARENTS = {'IDM-GRAND-FAMILY-PARENT'}   # only has new children


def is_new(t, r):
    a, c, d = t[f'A{r}'].value, str(t[f'C{r}'].value), t[f'D{r}'].value
    return (d == 'Child' and c.startswith('Create')) or a in NEW_PARENTS


def write(keep_new, out):
    wb = openpyxl.load_workbook(FULL)
    t = wb['Template']
    last = max(r for r in range(8, t.max_row + 1) if t[f'A{r}'].value)
    maxc = t.max_column
    rows = [r for r in range(8, last + 1) if t[f'A{r}'].value and is_new(t, r) == keep_new]
    snap = [[(t.cell(r, c).value, copy.copy(t.cell(r, c)._style), copy.copy(t.cell(r, c).comment) if t.cell(r, c).comment
              else None) for c in range(1, maxc + 1)] for r in rows]
    blank = copy.copy(t.cell(900, 1)._style)
    for r in range(8, last + 1):
        for c in range(1, maxc + 1):
            cell = t.cell(r, c)
            cell.value = None; cell.comment = None; cell._style = copy.copy(blank)
    for i, cells in enumerate(snap):
        for c, (v, st, cm) in enumerate(cells, 1):
            cell = t.cell(8 + i, c)
            cell.value = v; cell._style = st; cell.comment = cm
    thin_rows(wb)
    wb.save(out)
    return [s[0][0] for s in snap]


shutil.copyfile(SRC, FULL)
now = write(False, 'ILLUCO_Amazon_UPLOAD.xlsx')
later = write(True, 'ILLUCO_Amazon_NEW_PRODUCTS.xlsx')
print('UPLOAD (now):', len(now), 'rows |', 'NEW_PRODUCTS (after GS1):', len(later), 'rows:', later)
