"""SISTEMA .ssm inspector (the file is tiOPF XML: <xmldocdata><table table_name=...>...).

Usage:
  python ssm_inspect.py <file.ssm> tables
  python ssm_inspect.py <file.ssm> dump <table_name> [max_rows]
  python ssm_inspect.py <file.ssm> tree
"""
import sys
import xml.etree.ElementTree as ET


def load(path):
    return ET.parse(path).getroot()


def tables(root):
    out = []
    for tbl in root.iter('table'):
        name = tbl.get('table_name')
        fields = [fl.get('field_name') for fl in tbl.findall('./fields/field')]
        rows = tbl.findall('./rows/row')
        out.append((name, fields, rows))
    return out


def row_values(row):
    values = {}
    for obj in row:
        oid = obj.get('oid')
        payload = {}
        for field in obj.findall('./field'):
            value = field.find('./value')
            children = value.findall('./*') if value is not None else []
            if children:
                payload[field.get('field_name')] = [c.get('oid') for c in children]
            else:
                payload[field.get('field_name')] = (value.text if value is not None else None)
        values[oid] = payload
    return values


def main():
    path, mode = sys.argv[1], sys.argv[2]
    root = load(path)
    if mode == 'tables':
        for name, fields, rows in tables(root):
            print('%-26s rows=%-5d fields=%s' % (name, len(rows), ','.join(fields)))
    elif mode == 'dump':
        target = sys.argv[3]
        limit = int(sys.argv[4]) if len(sys.argv) > 4 else 10 ** 9
        for tbl in root.iter('table'):
            if tbl.get('table_name') != target:
                continue
            rows = tbl.findall('./rows/row')
            print('# table %s: %d rows' % (target, len(rows)))
            for i, row in enumerate(rows[:limit]):
                print('--- row %d ---' % i)
                for oid, payload in row_values(row).items():
                    print('  oid=%s' % oid)
                    for k, v in payload.items():
                        print('     %-22s %s' % (k, v))
    elif mode == 'tree':
        # generic: show every table's oid -> key fields compactly
        for name, fields, rows in tables(root):
            if not rows:
                continue
            print('=== %s (%d rows) ===' % (name, len(rows)))
            for row in rows:
                for oid, payload in row_values(row).items():
                    brief = {k: v for k, v in payload.items() if v not in (None, '', [])}
                    print('  %s  %s' % (oid, brief))
    else:
        print('unknown mode', mode)


if __name__ == '__main__':
    main()
