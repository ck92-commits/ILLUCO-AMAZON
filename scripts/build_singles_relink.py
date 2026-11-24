"""Relationship-only file for the 6 single mirrors (9 SKUs). The 11/24 upload created IDM-SINGLE-FAMILY-PARENT
(ASIN B0HSQBPPDM) but no single joined it, with no error in the report; the 5-pack and heads families did join.
This re-sends only the link: SKU, product type, Edit (Partial Update), Child, parent SKU, theme, color and size.
If Amazon refuses a row, its processing report names the reason (e.g. a different product type).
usage: build_singles_relink.py <template .xlsx> <out .xlsx>"""
import copy, sys
import openpyxl

sys.path.insert(0, 'scripts')
from xlsx_thin import thin_rows

TPL, OUT = sys.argv[1:3]
full = openpyxl.load_workbook('data/build/upload_full.xlsx')['Template']
rows = [{c: full[f'{c}{r}'].value for c in ('A', 'B', 'BA', 'BB', 'E', 'F')}
        for r in range(8, full.max_row + 1)
        if full[f'A{r}'].value and full[f'E{r}'].value == 'IDM-SINGLE-FAMILY-PARENT']
assert len(rows) == 9, len(rows)
wb = openpyxl.load_workbook(TPL)
t = wb['Template']
blank = copy.copy(t.cell(900, 1)._style)
for r in range(8, t.max_row + 1):
    for c in range(1, t.max_column + 1):
        cell = t.cell(r, c)
        if cell.value is not None or cell.comment:
            cell.value = None; cell.comment = None
        cell._style = copy.copy(blank)
for i, x in enumerate(rows):
    r = 8 + i
    t[f'A{r}'], t[f'B{r}'], t[f'C{r}'], t[f'D{r}'] = x['A'], x['B'], 'Edit (Partial Update)', 'Child'
    t[f'E{r}'], t[f'F{r}'], t[f'BA{r}'], t[f'BB{r}'] = x['E'], x['F'], x['BA'], x['BB']
thin_rows(wb)
wb.save(OUT)
for x in rows:
    print(x['A'], '|', x['E'], x['F'], '|', x['BA'], '|', x['BB'])
