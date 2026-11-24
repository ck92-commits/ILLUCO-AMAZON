"""ILLUCO_Amazon_DELETE_unused_SKUs.xlsx: Delete rows for SKUs with no reason to stay (owner, 11/24: "a clear inventory
page, only the SKUs that have sales"). Chosen from the All Listings Report of 11/24 and the 11/20 order and sales data:
extra SKUs on a listing whose other SKU sells, the retired duplicate B0GGDQ15DD, an inactive copy, a dead listing and an
unfinished draft. Real products with no sales yet are NOT here (owner decides): photo mirrors, IDS-3100, Skinsoft 3/5 pk.
Deleting a SKU removes only that offer; reviews stay with the ASIN.
usage: build_delete_unused.py <template .xlsx> <out .xlsx>"""
import copy, sys
import openpyxl

sys.path.insert(0, 'scripts')
from xlsx_thin import thin_rows

DELETE = [   # (SKU, ASIN, why)
    ('8S-2CRX-WR6S', 'B0G2DYRY7T', 'extra SKU, no orders; A2-3YBP-WRV7 sells this listing'),
    ('V9-7J5N-U4E1', 'B0G2DYRY7T', 'extra SKU, no orders; A2-3YBP-WRV7 sells this listing'),
    ('IDM-2C41DB-1X-FBA', 'B0GGF37FSB', 'extra SKU, no orders; IDM-2C41DB-1X sells this listing'),
    ('IDM-2C41LB-1X', 'B0GGDQ15DD', 'duplicate of B0G2DYRY7T, retired (owner, 11/24)'),
    ('IDM2C41LB-1X-FBA', 'B0GGDQ15DD', 'duplicate of B0G2DYRY7T, retired (owner, 11/24)'),
    ('68-X5JM-ENOE', 'B0F7YPNMWK', 'inactive FBA copy of IDS-1100; the merchant SKU 68-X5JM-ENOE-FBM sells it'),
    ('HD-GB-1pk', 'B00K2RFAX8', 'inactive, 0 stock, no sales (Skinsoft brush 1 pack)'),
    ('HD-FBGB', 'B0GXC5GWBL', 'unfinished draft (Skinsoft brush)'),
]
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
for i, (sku, asin, why) in enumerate(DELETE):
    r = 8 + i
    t[f'A{r}'], t[f'B{r}'], t[f'C{r}'] = sku, 'PROFESSIONAL_HEALTHCARE', 'Delete'
thin_rows(wb)
wb.save(OUT)
for sku, asin, why in DELETE:
    print(f'{sku:<20} {asin}  {why}')
