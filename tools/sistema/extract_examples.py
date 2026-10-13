"""Batch-extract structure and key parameters from SISTEMA .ssm example projects.

The .ssm file is tiOPF XML:
  <xmldocdata><table table_name="..."><fields>...</fields><rows><row .../></rows></table>...
Every column is an XML *attribute* on <row>, so each table is simply a list of dicts.

Usage:
  python extract_examples.py <dir-with-ssm> [out.txt]
"""
import glob
import os
import sys
import xml.etree.ElementTree as ET


def table_rows(root, table_name):
    for tbl in root.iter('table'):
        if tbl.get('table_name') == table_name:
            return [r.attrib for r in tbl.findall('./rows/row')]
    return []


def g(row, key, dash='-'):
    v = row.get(key)
    return v if v not in (None, '') else dash


def summarize(path, out):
    root = ET.parse(path).getroot()
    prs = table_rows(root, 'projectops')
    sfs = table_rows(root, 'sfops')
    sbs = table_rows(root, 'componentops')
    chs = table_rows(root, 'channelops')
    bls = table_rows(root, 'blocops')
    els = table_rows(root, 'elementops')
    dcs = table_rows(root, 'dcmeasureops')
    ccf = table_rows(root, 'ccfmeasureops')

    out.append(f"### {os.path.basename(path)}")
    for p in prs:
        out.append(f"  PR: {g(p,'name')} | norm={g(p,'normversion')} | ssmversion={g(p,'ssmversion')}")

    # 按 componentopoid 归组通道/块，便于看清层次
    for s in sfs:
        out.append(f"  SF: {g(s,'name')} | PLr={g(s,'plr')} plrdet={g(s,'plrdet')} "
                   f"| PLcal={g(s,'plcal')} PFHcal={g(s,'pfhcal')} "
                   f"| sftype={g(s,'sftype')} reaction={g(s,'reaction')} opmode={g(s,'opmode')}")

    for b in sbs:
        out.append(f"    SB: {g(b,'name')} | cat={g(b,'cat')} mttfd={g(b,'mttfd')} dcavg={g(b,'dcavg')} "
                   f"ccf={g(b,'ccfscore')} pfh={g(b,'pfh')} "
                   f"| pldet={g(b,'pldet')} plsubitemssimplecal={g(b,'plsubitemssimplecal')} "
                   f"plsubitemscal={g(b,'plsubitemscal')} pldirectcal={g(b,'pldirectcal')} "
                   f"pfhsubitemssimplecal={g(b,'pfhsubitemssimplecal')} "
                   f"| mttfddet={g(b,'mttfddet')} dcavgdet={g(b,'dcavgdet')} ccfscoredet={g(b,'ccfscoredet')} "
                   f"| fn={g(b,'functiontypes')} mfr={g(b,'manufacturer')} dev={g(b,'deviceid')}")
        oid = b.get('oid')
        for c in [x for x in chs if x.get('componentopoid') == oid]:
            out.append(f"      CH: {g(c,'name')} type={g(c,'channeltype')}")
            coid = c.get('oid')
            for bl in [x for x in bls if x.get('parentopoid') == coid]:
                out.append(f"        BL: {g(bl,'name')} mttfd={g(bl,'mttfd')} dc={g(bl,'dc')} b10d={g(bl,'b10d')} "
                           f"nop={g(bl,'nop')} tech={g(bl,'technology')} fn={g(bl,'functiontypes')} "
                           f"calcmttfddet={g(bl,'calcmttfddet')} libname={g(bl,'libname')}")
                boid = bl.get('oid')
                for el in [x for x in els if x.get('parentopoid') == boid]:
                    out.append(f"          EL: {g(el,'name')} mttfd={g(el,'mttfd')} dc={g(el,'dc')} "
                               f"b10d={g(el,'b10d')} nop={g(el,'nop')} tech={g(el,'technology')}")

    if dcs:
        out.append(f"  [dcmeasureops] {len(dcs)} 条: " +
                   "; ".join(f"{g(d,'heading')}(dcmin={g(d,'dcmin')},dcmax={g(d,'dcmax')},dc={g(d,'dc')})" for d in dcs[:6]))
    if ccf:
        out.append(f"  [ccfmeasureops] {len(ccf)} 条, 总分示例={g(ccf[0],'score')}")
    out.append("")


def main():
    src = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else None
    out = []
    files = sorted(glob.glob(os.path.join(src, '*.ssm')))
    out.append(f"共 {len(files)} 个 .ssm 项目")
    out.append("")
    for f in files:
        try:
            summarize(f, out)
        except Exception as exc:  # noqa: BLE001
            out.append(f"### {os.path.basename(f)}\n  !! 解析失败: {exc}\n")
    text = "\n".join(out)
    if out_path:
        with open(out_path, 'w', encoding='utf-8') as fh:
            fh.write(text)
        print(f"wrote {out_path} ({len(out)} lines)")
    else:
        print(text)


if __name__ == '__main__':
    main()
