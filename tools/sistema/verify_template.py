"""Read back the generated workbook: sheet sizes, first rows, and every data validation."""
import sys
from openpyxl import load_workbook

path, out = sys.argv[1], sys.argv[2]
wb = load_workbook(path)
lines = []
for ws in wb.worksheets:
    lines.append('=' * 92)
    lines.append('SHEET %s   (%d rows x %d cols)' % (ws.title, ws.max_row, ws.max_column))
    for dv in ws.data_validations.dataValidation:
        lines.append('   下拉 %-10s : %s' % (dv.sqref, dv.formula1))
    for row in ws.iter_rows(min_row=1, max_row=min(ws.max_row, 7), values_only=True):
        cells = ['' if c is None else str(c) for c in row]
        lines.append('   | ' + ' | '.join(cells))
    if ws.max_row > 7:
        lines.append('   ... (%d more rows)' % (ws.max_row - 7))
    lines.append('')
with open(out, 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(lines))
print('wrote', out, len(lines), 'lines')
