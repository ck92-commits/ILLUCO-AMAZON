"""One-time file that deletes the 3 OLD parent listings, so their children can join the new families.

Amazon warning 8032 (11/21): a child can belong to only one parent. Deleting a parent removes only that
parent listing; the children keep their ASINs, reviews, stock and offers. Parent SKUs as shown in
Manage All Inventory on 11/21 (owner screenshots). Upload this first, wait for it to finish, then upload
ILLUCO_Amazon_UPLOAD.xlsx again.
usage: build_delete_old_parents.py <template .xlsx> <out .xlsx>"""
import sys, copy, openpyxl
sys.path.insert(0, 'scripts')
from xlsx_thin import thin_rows

OLD_PARENTS = [   # (parent SKU, parent ASIN, family)
    ('IDM3C4XXX', 'B0FDCGG69J', '5-pack with handles'),
    ('0Z-AYA6-3N2M', 'B0GGD9DVP9', 'single mirror with handle'),
    ('6B-536I-O2ME', 'B0FCNL53JN', 'replacement heads'),
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
