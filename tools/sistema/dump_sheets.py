"""Dump selected sheets (by index) fully, for checking element lists."""
import sys
from openpyxl import load_workbook

path, out = sys.argv[1], sys.argv[2]
idxs = [int(x) for x in sys.argv[3:]]
wb = load_workbook(path)
lines = []
names = wb.sheetnames
for i in idxs:
    ws = wb[names[i]]
    lines.append('=== [%d] %s ===' % (i, names[i]))
    for row in ws.iter_rows(values_only=True):
        cells = ['' if c is None else str(c) for c in row]
        if any(cells):
            lines.append('  ' + ' | '.join(cells))
    lines.append('')
with open(out, 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(lines))
print('wrote', out)
