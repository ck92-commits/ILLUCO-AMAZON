"""Keep every row at Excel's default (thin) height: no wrapped text, no custom row heights.

Owner request 2026-11-20: expanded rows are hard to read. Applied to every visible sheet of the upload
and the report before they are saved. Usage as a module: thin_rows(wb). Hidden sheets are left alone.
"""
from openpyxl.styles import Alignment


def thin_rows(wb):
    for ws in wb.worksheets:
        if ws.sheet_state != 'visible':
            continue
        for row in ws.iter_rows():
            for c in row:
                a = c.alignment
                if a is not None and a.wrap_text:
                    c.alignment = Alignment(horizontal=a.horizontal, vertical=a.vertical, text_rotation=a.text_rotation,
                                            wrap_text=False, shrink_to_fit=a.shrink_to_fit, indent=a.indent)
        for dim in ws.row_dimensions.values():
            dim.height = None
