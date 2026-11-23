"""One-time file that deletes the parent listing IDM-HANDLE-FAMILY-PARENT before the upload.

That family (uploaded 11/21) mixed pack sizes under theme SIZE/COLOR/NUMBER_OF_ITEMS. The owner wants one pack size
per family with Color and Size as the choices (11/23), so its children move to new parents: IDM-5PACK-FAMILY-PARENT,
IDM-SINGLE-FAMILY-PARENT and IDM-GRAND-FAMILY-PARENT. A live family's theme cannot be changed in place, and a child
can belong to only one parent (Amazon 8032), so the old parent goes first. Deleting a parent removes only that
parent listing; the children keep their ASINs, reviews, stock and offers. IDM-HEADS-FAMILY-PARENT stays.
Upload this first, wait for its processing report, then upload ILLUCO_Amazon_UPLOAD.xlsx.
(The first version of this file, 11/21, deleted the three original parents IDM3C4XXX / B0FDCGG69J,
0Z-AYA6-3N2M / B0GGD9DVP9 and 6B-536I-O2ME / B0FCNL53JN; that is done.)
usage: build_delete_old_parents.py <template .xlsx> <out .xlsx>"""
import sys, copy, openpyxl
sys.path.insert(0, 'scripts')
from xlsx_thin import thin_rows

OLD_PARENTS = [   # (parent SKU, parent ASIN, family)
    ('IDM-HANDLE-FAMILY-PARENT', '', 'mirrors with handles, mixed pack sizes (uploaded 11/21)'),
]
TPL, OUT = sys.argv[1:3]
wb = openpyxl.load_workbook(TPL)
t = wb['Template']
blank = copy.copy(t.cell(900, 1)._style)
for r in range(8, t.max_row + 1):          # clear every data row of the template
    for c in range(1, t.max_column + 1):
        cell = t.cell(r, c)
        if cell.value is not None or cell.comment:
            cell.value = None; cell.comment = None
        cell._style = copy.copy(blank)
for i, (sku, asin, fam) in enumerate(OLD_PARENTS):
    t[f'A{8 + i}'] = sku
    t[f'B{8 + i}'] = 'PROFESSIONAL_HEALTHCARE'
    t[f'C{8 + i}'] = 'Delete'
thin_rows(wb)
wb.save(OUT)
print('rows', len(OLD_PARENTS), [s for s, _, _ in OLD_PARENTS])
