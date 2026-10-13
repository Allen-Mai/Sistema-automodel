"""Dump raw XML node structure of a .ssm file to a UTF-8 text file (avoids console encoding issues)."""
import sys
import xml.etree.ElementTree as ET

path = sys.argv[1]
out = sys.argv[2]
root = ET.parse(path).getroot()

lines = []
lines.append('root tag=%s attrib=%s' % (root.tag, root.attrib))
lines.append('root children: %s' % [c.tag for c in root][:20])

for tbl in list(root.iter('table'))[:4]:
    lines.append('')
    lines.append('TABLE %s' % tbl.get('table_name'))
    lines.append('  children of table: %s' % [c.tag for c in tbl][:10])
    flds = tbl.find('./fields')
    if flds is not None:
        lines.append('  fields children: %d, first: %s' % (len(list(flds)), [c.attrib for c in list(flds)[:3]]))
    rows = tbl.find('./rows')
    lines.append('  rows node: %s  children=%d' % (rows.tag if rows is not None else None, len(list(rows)) if rows is not None else 0))
    if rows is not None and len(list(rows)):
        r0 = list(rows)[0]
        lines.append('  row0 tag=%s attrib=%s children=%d' % (r0.tag, r0.attrib, len(list(r0))))
        for c in list(r0)[:2]:
            lines.append('    child tag=%s attrib=%s children=%d' % (c.tag, c.attrib, len(list(c))))
            for gc in list(c)[:4]:
                lines.append('      gchild tag=%s attrib=%s text=%r children=%d' % (
                    gc.tag, gc.attrib, (gc.text or '')[:60], len(list(gc))))
                for ggc in list(gc)[:3]:
                    lines.append('        ggchild tag=%s attrib=%s text=%r' % (ggc.tag, ggc.attrib, (ggc.text or '')[:60]))

with open(out, 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(lines))
print('wrote', out, len(lines), 'lines')
