"""Field-level diff between the blueprint project and the generated one.

Compares same-kind nodes so we can see which field prevents SISTEMA from computing PL/PFH.
"""
import sys
import xml.etree.ElementTree as ET

BP = r'C:\Users\sf-bc04.SF\Desktop\SISTEMA V2 测试建模\07-测试\Safety Circuit for Glass Disc Sorting Equipment.ssm'
NEW = r'C:\Users\sf-bc04.SF\Desktop\SISTEMA V2 测试建模\10-移印机\移印机.ssm'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'diff.txt'


def load(p):
    root = ET.parse(p).getroot()
    return {t.get('table_name'): [r.attrib for r in t.findall('./rows/row')] for t in root.iter('table')}


def diff(tag, a, b):
    lines = ['=== %s ===' % tag, '  A(id)=%s' % (a.get('oid') or a.get('name')), '  B(id)=%s' % (b.get('oid') or b.get('name'))]
    keys = list(a.keys()) + [k for k in b.keys() if k not in a]
    for k in keys:
        av, bv = a.get(k, '<missing>'), b.get(k, '<missing>')
        if av != bv:
            lines.append('  %-26s A=%-34s B=%s' % (k, repr(av)[:34], repr(bv)[:44]))
    return lines


def main():
    bp, new = load(BP), load(NEW)
    out = []

    # 1) single-device subsystem: blueprint 门开关 (works) vs new PNOZ c1 (flagged)
    a = next(x for x in bp['componentops'] if 'Safety Door' in x.get('name', ''))
    b = next(x for x in new['componentops'] if 'PNOZ' in x.get('name', ''))
    out += diff('componentops: 单器件 (蓝本门开关 A vs 新PNOZ c1 B)', a, b)

    # 2) chain subsystem: blueprint STO (works) vs new 急停按钮串联 (flagged)
    a2 = next(x for x in bp['componentops'] if 'STO Safe Torque' in x.get('name', ''))
    b2 = next(x for x in new['componentops'] if '急停按钮串联' in x.get('name', ''))
    out += [''] + diff('componentops: 功能链 (蓝本STO A vs 新急停按钮 B)', a2, b2)

    # 3) mechanical block: blueprint XB2BS544C vs new XB4BS84441
    a3 = next(x for x in bp['blocops'] if x.get('deviceid') == 'XB2BS544C')
    b3 = next(x for x in new['blocops'] if x.get('deviceid') == 'XB4BS84441')
    out += [''] + diff('blocops: 机电块 (蓝本XB2BS544C A vs 新XB4BS84441 B)', a3, b3)

    # 4) electronic block: blueprint STO vs new SV630 STO
    a4 = next(x for x in bp['blocops'] if x.get('deviceid', '').startswith('V90 STO'))
    b4 = next(x for x in new['blocops'] if x.get('deviceid') == 'SV630 STO')
    out += [''] + diff('blocops: 电子块 (蓝本V90 STO A vs 新SV630 STO B)', a4, b4)

    # 5) sf level
    a5, b5 = bp['sfops'][0], new['sfops'][0]
    out += [''] + diff('sfops (蓝本SF1 A vs 新SF B)', a5, b5)

    with open(OUT, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(out))
    print('wrote', OUT, len(out), 'lines')


if __name__ == '__main__':
    main()
