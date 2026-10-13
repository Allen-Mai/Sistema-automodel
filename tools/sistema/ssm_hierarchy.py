"""Rebuild SISTEMA project hierarchy from .ssm XML (fields are XML attributes on <row>).

PR projectops -> SF sfops -> SB componentops -> CH channelops -> BL blocops -> EL elementops
Writes UTF-8 output to a file (console mangles CJK).
"""
import sys
import xml.etree.ElementTree as ET


def load(path):
    root = ET.parse(path).getroot()
    tables = {}
    for tbl in root.iter('table'):
        tables[tbl.get('table_name')] = [r.attrib for r in tbl.findall('./rows/row')]
    return tables


def v(row, key, default='-'):
    val = row.get(key)
    return default if val in (None, '') else val


def main():
    path, out_path = sys.argv[1], sys.argv[2]
    t = load(path)
    out = []
    w = out.append

    prs = t.get('projectops', [])
    sfs = t.get('sfops', [])
    sbs = t.get('componentops', [])
    chs = t.get('channelops', [])
    bls = t.get('blocops', [])
    els = t.get('elementops', [])

    w('=== 行数 ===')
    for name, rows in t.items():
        w('  %-20s %d' % (name, len(rows)))

    # reference integrity check
    ch_oids = {c.get('oid') for c in chs}
    sb_oids = {s.get('oid') for s in sbs}
    bl_oids = {b.get('oid') for b in bls}
    par = [b.get('parentopoid') for b in bls]
    w('')
    w('=== 引用完整性 ===')
    w('  blocops.parentopoid -> channelops: %d/%d' % (sum(1 for p in par if p in ch_oids), len(par)))
    w('  blocops.parentopoid -> componentops: %d/%d' % (sum(1 for p in par if p in sb_oids), len(par)))
    epar = [e.get('parentopoid') for e in els]
    w('  elementops.parentopoid -> blocops: %d/%d' % (sum(1 for p in epar if p in bl_oids), len(epar)))

    for pr in prs:
        w('')
        w('=' * 100)
        w('PR  %s' % v(pr, 'name'))
        w('    norm=%s  author=%s  machine=%s' % (v(pr, 'normversion'), v(pr, 'author'), v(pr, 'machinename')))
        w('    document=%s   standards=%s documents=%s' % (v(pr, 'document'), v(pr, 'standardsfolder'), v(pr, 'documentsfolder')))
        w('    project file recorded in ssm: %s' % v(pr, 'filename'))

        for sf in [s for s in sfs if s.get('projectopoid') == pr.get('oid')]:
            w('')
            w('  SF  %s' % v(sf, 'name'))
            w('      PLr=%s (det=%s)  PL_calc=%s  PFH_calc=%s' % (v(sf, 'plr'), v(sf, 'plrdet'), v(sf, 'plcal'), v(sf, 'pfhcal')))
            w('      risk: F=%s P=%s S=%s  W=%s   emi=%s score=%s' % (
                v(sf, 'riskparamf'), v(sf, 'riskparamp'), v(sf, 'riskparams'), v(sf, 'wparameter'), v(sf, 'emiroute'), v(sf, 'emiscore')))
            w('      sftype=%s triggerevent=%s safestate=%s opmode=%s' % (
                v(sf, 'sftype'), v(sf, 'triggerevent'), v(sf, 'safestate'), v(sf, 'opmode')))
            w('      reaction=%s reqfreq=%s resp=%s priority=%s' % (
                v(sf, 'reaction'), v(sf, 'requestfrequency'), v(sf, 'responsetime'), v(sf, 'priority')))
            w('      document=%s  plrdocumentation=%s' % (v(sf, 'document'), v(sf, 'plrdocumentation')))

            for sb in [s for s in sbs if s.get('sfopoid') == sf.get('oid')]:
                w('')
                w('    SB  %s' % v(sb, 'name'))
                w('        func=%s  cat=%s  CCF=%s  DCavg=%s  MTTFd=%s  PL=%s  PFH=%s  missiontime=%s' % (
                    v(sb, 'functiontypes'), v(sb, 'cat'), v(sb, 'ccfscore'), v(sb, 'dcavg'),
                    v(sb, 'mttfd'), v(sb, 'pl'), v(sb, 'pfh'), v(sb, 'missiontime')))
                w('        det: pl=%s mttfd=%s dcavg=%s ccf=%s  qualitativePL=%s  plconditions=%s' % (
                    v(sb, 'pldet'), v(sb, 'mttfddet'), v(sb, 'dcavgdet'), v(sb, 'ccfscoredet'),
                    v(sb, 'qualitativeaspects_pl'), v(sb, 'plconditions')))
                w('        mfr=%s device=%s group=%s equip=%s partno=%s rev=%s' % (
                    v(sb, 'manufacturer'), v(sb, 'deviceid'), v(sb, 'devicegroup'),
                    v(sb, 'equipmentid'), v(sb, 'partno'), v(sb, 'revision')))
                w('        standards=%s | file=%s' % (v(sb, 'catstandard'), v(sb, 'catstandardfile')))
                w('        usecase=%s document=%s' % (v(sb, 'usecase'), v(sb, 'document')))

                for ch in [c for c in chs if c.get('componentopoid') == sb.get('oid')]:
                    w('      CH  %s   type=%s' % (v(ch, 'name', '(unnamed)'), v(ch, 'channeltype')))
                    for bl in [b for b in bls if b.get('parentopoid') == ch.get('oid')]:
                        w('        BL  %s' % v(bl, 'name'))
                        w('            MTTFd=%s DC=%s B10d=%s nop=%s B10=%s lambda=%s MTTF=%s MTBF=%s tech=%s' % (
                            v(bl, 'mttfd'), v(bl, 'dc'), v(bl, 'b10d'), v(bl, 'nop'), v(bl, 'b10'),
                            v(bl, 'lambda'), v(bl, 'mttf'), v(bl, 'mtbf'), v(bl, 'technology')))
                        w('            mfr=%s device=%s group=%s partno=%s equip=%s usecase=%s cat=%s' % (
                            v(bl, 'manufacturer'), v(bl, 'deviceid'), v(bl, 'devicegroup'),
                            v(bl, 'partno'), v(bl, 'equipmentid'), v(bl, 'usecase'), v(bl, 'cat')))
                        w('            dcmeasure=%s missiontime=%s document=%s' % (
                            v(bl, 'dcmeasure'), v(bl, 'missiontime'), v(bl, 'document')))
                        for el in [e for e in els if e.get('parentopoid') == bl.get('oid')]:
                            w('          EL  %s | MTTFd=%s DC=%s B10d=%s nop=%s tech=%s' % (
                                v(el, 'name'), v(el, 'mttfd'), v(el, 'dc'), v(el, 'b10d'), v(el, 'nop'), v(el, 'technology')))

    # document references
    w('')
    w('=== 文档引用 ===')
    seen = set()
    for tname, rows in t.items():
        for row in rows:
            for key in ('document', 'documentation', 'catstandardfile', 'libfilename', 'plrdocument', 'plrstandardfile'):
                val = row.get(key)
                if val:
                    sig = (tname, key, val)
                    if sig not in seen:
                        seen.add(sig)
                        w('  %-14s %-16s %s' % (tname, key, val))

    with open(out_path, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(out))
    print('wrote %s (%d lines)' % (out_path, len(out)))


if __name__ == '__main__':
    main()
