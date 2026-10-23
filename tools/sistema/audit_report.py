"""Audit a SISTEMA PDF-export text dump against ISO 13849-1 modelling rules.

Input is the plain-text dump produced by ``extract_pdf.py`` (SISTEMA "Print
report" -> PDF -> extract text).  The script re-derives every number SISTEMA
computed and cross-checks it against the printed tables *and* the free-text
Justification / Documentation fields, so the classic audit findings (text says
99 %, table says 65 %, B10 vs B10d mixed up, truncated justification, mojibake,
dead documentation links) surface mechanically instead of by eyeballing 100+
pages.

Usage
-----
    python audit_report.py report.txt                 # human readable
    python audit_report.py report.txt --md out.md     # markdown table
    python audit_report.py report.txt --json out.json # machine readable

Exit code 1 when at least one FATAL finding was raised, 0 otherwise.

Rules
-----
F1  B10d = B10 / RDF                      (SISTEMA derives B10d from B10 + RDF)
F2  MTTFd = B10d / (0.1 * nop)            (B10d method, EN ISO 13849-1 C.4.2)
F3  DCavg grade matches its value         (<60 none / 60-90 low / 90-99 medium / >=99 high)
F4  MTTFd capped at 100 a (Cat 2/3) or 2500 a (Cat 4)
F5  DC% / Category stated in the text == the table value
F6  Reached PL consistent with PFHd (table 3)
F7  no mojibake (GBK text rendered as Latin-1 in the PDF)
F8  justification text not cut off by the field-length limit
F9  documentation links usable (no ``..\\`` escape, no mojibake in the name)
F10 SF definition fields (trigger / reaction / safe state / demand rate) filled
F11 CCF measures do not exceed the Annex F per-measure cap
F12 B10 / B10d quoted in the text matches the table
F13 "RDF = x %" claimed in the text but no RDF entered for that block
F14 B10d larger than B10 (dangerous-failure ratio used backwards)
F15 text cites a datasheet but the Documentation link is empty
F16 block technology / category left unset inside a category 3/4 subsystem
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field

# --------------------------------------------------------------------------
# ISO 13849-1 tables
# --------------------------------------------------------------------------

#: PL bands, PFHd per hour (EN ISO 13849-1 table 3)
PL_ORDER = ['a', 'b', 'c', 'd', 'e']
PL_BANDS = [
    ('e', 1e-8, 1e-7),
    ('d', 1e-7, 1e-6),
    ('c', 1e-6, 3e-6),
    ('b', 3e-6, 1e-5),
    ('a', 1e-5, 1e-4),
]

#: DCavg grading, EN ISO 13849-1 table 6 / annex K
DC_BANDS = [(99.0, 'High'), (90.0, 'Medium'), (60.0, 'Low'), (0.0, 'None')]

MTTFD_CAP_CAT4 = 2500.0
MTTFD_CAP_OTHER = 100.0

#: Annex F, table F.1 per-measure maximum score
CCF_CAPS = {
    'SEP': 15, 'DIV': 20, 'DES': 20, 'DEX': 20, 'APP': 20,
    'ANA': 5, 'COM': 5, 'ENV': 25, 'EMC': 10, 'E/M': 10, 'EM': 10,
}
CCF_MIN = 65

FATAL, WARN, INFO = 'FATAL', 'WARN', 'INFO'


@dataclass
class Finding:
    rule: str
    severity: str
    page: str
    where: str
    detail: str

    def as_dict(self) -> dict:
        return dict(rule=self.rule, severity=self.severity, page=self.page,
                    where=self.where, detail=self.detail)


@dataclass
class Node:
    kind: str                    # SF | SB | CH | BL
    page: int
    name: str = ''
    sf: str = ''
    cat: str = ''
    tech: str = ''
    dc: str = ''
    mttfd: str = ''
    b10: str = ''
    b10d: str = ''
    rdf: str = ''
    nop: str = ''
    ccf: str = ''
    plr: str = ''
    pl: str = ''
    pfh: float | None = None
    status: str = ''
    text: list[str] = field(default_factory=list)   # justification free text
    messages: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)


PAGE_RE = re.compile(r'^===== PAGE (\d+) =====$', re.M)
SECTION_RE = re.compile(
    r'^(Subsystems|Channels /  Test channels|Channels / Test channels|Blocks) '
    r'\((\d+)\s*/\s*(\d+)\)$')
NAME_RE = re.compile(r'^Name:\s*(.+?)\s*$')
REACHED_RE = re.compile(r'^\s*([a-e])\s*PFH \[1/h\]:\s*([0-9.]+E[-+][0-9]+)')

#: structural label lines that must not be mistaken for free text
STRUCT = (
    'Status / Messages', 'Device details', 'Documentation ', 'Document ',
    'Performance Level', 'Required Performance Level', 'Qualitative aspects',
    'Electromagnetic immunity', 'Category Safety function', 'Category Subsystem',
    'Category Block', 'MTTFD and Mission time', 'Diagnostic coverage',
    'Common cause failure', 'Requirements for', 'Category requirements',
    'Message [Status', 'The PL shall', 'Route for fulfilment',
    'Identifier of the Safety function', 'Safety function type', 'Triggering event',
    'Reaction and', 'Safe state', 'Operation mode', 'Interfaces', 'Demand rate',
    'Running-on time', 'Priority', 'Source (e.g. standard)', 'File ',
    'List of devices', 'Device list', 'Reference designator', 'Inventory number',
    'Device Manufacturer', 'Device Identifier', 'Device group', 'Part number',
    'Revision', 'Function ', 'Technology', 'Use case', 'Description of the use case',
    'Print options', 'Contained safety functions', 'PL determination', 'PL:',
    'MTTFD [a]', 'Mission time', 'Shortest', 'CCF Points', 'DCavg [%]', 'DC [%]',
    'B10', 'B10D', 'nop ', 'RDF ', 'S t a t u s', 'PLr (by direct', 'D o c u m e n t',
)
#: short checkbox / enum tokens printed one per line
TOKENS = {'Input', 'Logic', 'Output', 'unknown', 'green', 'red', 'yellow', 'n/a'}


def norm(line: str) -> str:
    return re.sub(r'\s+', ' ', line).strip()


def to_num(s: str) -> float | None:
    if not s:
        return None
    s = s.strip().replace('\u00a0', '')
    s = re.sub(r'\s+', '', s)
    if re.fullmatch(r'\d{1,3}(,\d{3})+', s):
        s = s.replace(',', '')
    else:
        s = s.replace(',', '.')
    try:
        return float(s)
    except ValueError:
        return None


def pl_from_pfh(pfh: float | None) -> str | None:
    if pfh is None:
        return None
    for name, lo, hi in PL_BANDS:
        if lo <= pfh < hi:
            return name
    return 'e' if pfh < 1e-8 else None


def grade_of(dc: float) -> str:
    for lo, name in DC_BANDS:
        if dc >= lo:
            return name
    return 'None'


def is_struct(line: str) -> bool:
    if line in TOKENS:
        return True
    if line.startswith('- '):
        return False          # bullet => free text
    return any(line.startswith(p) for p in STRUCT)


def parse(text: str) -> tuple[list[Node], dict]:
    pages = PAGE_RE.split(text)
    nodes: list[Node] = []
    meta: dict = {'pages': 0, 'sf_fields': {}}
    cur: Node | None = None
    sf_name = ''

    def close() -> None:
        nonlocal cur
        if cur is not None:
            nodes.append(cur)
            cur = None

    for i in range(1, len(pages), 2):
        page_no = int(pages[i])
        meta['pages'] = max(meta['pages'], page_no)
        # SISTEMA wraps long file names, so "....p" / "df" may arrive on two
        # lines.  Join them before parsing, otherwise the Documentation link
        # looks empty.
        raw_lines = pages[i + 1].splitlines()
        merged: list[str] = []
        k = 0
        while k < len(raw_lines):
            ln = raw_lines[k]
            if re.search(r'\.(p|d|do|doc|docx)$', ln.strip()) and k + 1 < len(raw_lines) \
                    and re.fullmatch(r'(df|cx|oc|ocx)?', raw_lines[k + 1].strip()):
                ln = ln.rstrip() + raw_lines[k + 1].strip()
                k += 1
            merged.append(ln)
            k += 1
        for raw in merged:
            line = norm(raw)
            if not line:
                continue
            if (line.startswith('SISTEMA -') or line.startswith('Project name:')
                    or line.startswith('File date:') or line.startswith('Page ')):
                continue
            if line.startswith('Safety function:'):
                new = re.sub(r'\s+', ' ', line.split(':', 1)[1]).strip()
                if new != sf_name:
                    close()
                    sf_name = new
                    cur = Node(kind='SF', page=page_no, name=new, sf=new)
                continue

            m = SECTION_RE.match(line)
            if m:
                kind = 'BL' if m.group(1).startswith('Block') else (
                    'SB' if m.group(1).startswith('Subsystem') else 'CH')
                close()
                cur = Node(kind=kind, page=page_no, sf=sf_name)
                continue

            if cur is None:
                continue

            # SF-level definition fields: remember which ones are empty
            for fld_name in ('Triggering event', 'Safe state', 'Demand rate',
                             'Operation mode', 'Safety function type'):
                if line.startswith(fld_name):
                    value = line.split(':', 1)[1].strip() if ':' in line else ''
                    meta['sf_fields'].setdefault((cur.page, fld_name), value)
                    break

            m = NAME_RE.match(line)
            if m and not cur.name and cur.kind in ('SF', 'SB', 'CH', 'BL') \
                    and '[' not in m.group(1):
                cur.name = m.group(1)
                continue

            # ---- parameter fields -----------------------------------------
            if re.search(r'C.?a t \. :', line) or re.search(r'C a t ?e ?g ?o ?r ?y :', line):
                cur.cat = line.split(':', 1)[1].strip()
                continue
            if line.startswith('DCavg [%]:') or line.startswith('DC [%]:'):
                cur.dc = line.split(':', 1)[-1].strip()
                continue
            if line.startswith('MTTFD [a]'):
                cur.mttfd = line.split(':', 1)[-1].strip()
                continue
            if line.startswith('CCF Points:'):
                cur.ccf = line.split(':', 1)[-1].strip()
                continue
            if line.startswith('PLr (by direct input):'):
                cur.plr = line.split(':', 1)[-1].strip()
                continue
            if line.startswith('Reached PL:'):
                m2 = REACHED_RE.match(line.split(':', 1)[-1])
                if m2:
                    cur.pl = m2.group(1)
                    cur.pfh = float(m2.group(2))
                continue
            if re.search(r'S.?a t u s :', line):
                cur.status = line.split(':', 1)[-1].strip()
                continue
            if 'B10' in line and ('[cycles]' in line or '[%]' in line):
                m2 = re.search(r'\bB10D \[cycles\]:\s*([0-9,]+)', line)
                if m2:
                    cur.b10d = m2.group(1)
                m2 = re.search(r'\bB10 \[cycles\]:\s*([0-9,]+)', line)
                if m2:
                    cur.b10 = m2.group(1)
                m2 = re.search(r'RDF \[%\]:\s*([0-9.,]+)', line)
                if m2:
                    cur.rdf = m2.group(1)
                m2 = re.search(r'nop \[cycles/a\]:\s*([0-9.,]+)', line)
                if m2:
                    cur.nop = m2.group(1)
                continue
            if re.search(r'\.(pdf|doc|docx)\s*$', line) or line.startswith('http'):
                cur.links.append(line)
                continue
            if line.startswith('Technology :') or re.search(r'T.?e c h n o l o g y :', line):
                cur.tech = line.split(':', 1)[-1].strip()
                continue
            if line.startswith('- '):
                # SISTEMA prints status messages as bullets; keep them apart so
                # they cannot be mistaken for the tail of a justification text
                cur.messages.append(line)
                continue
            if is_struct(line):
                continue
            cur.text.append(line)

    close()
    return nodes, meta


# --------------------------------------------------------------------------
# rules
# --------------------------------------------------------------------------

def audit(nodes: list[Node], meta: dict, text: str) -> list[Finding]:
    out: list[Finding] = []

    def add(rule, sev, page, where, detail):
        out.append(Finding(rule, sev, str(page), where, detail))

    # ---- F7: mojibake, reported once with the affected page list ----------
    bad = []
    for i in range(1, len(PAGE_RE.split(text)), 2):
        page = int(PAGE_RE.split(text)[i])
        body = PAGE_RE.split(text)[i + 1]
        cnt = sum(1 for ch in body if 0x80 <= ord(ch) <= 0xFF)
        if cnt > 3:
            bad.append((page, cnt))
    if bad:
        pages_txt = ', '.join(f'P{p}({c})' for p, c in bad)
        add('F7', FATAL, bad[0][0], f'{len(bad)} pages',
            f'中文自由文本字段在 PDF 中为乱码（{len(bad)} 页 / 共 {sum(c for _, c in bad)} 个'
            f'非 ANSI 字节）：{pages_txt[:600]}')

    # ---- F17: EMI requirement circular / unanswered ---------------------
    if re.search(r'EMI measures:\s*n/a', text) and \
            'documented in the associated safety function' in text:
        first = re.search(r'EMI measures:\s*n/a', text)
        page = text[:first.start()].count('===== PAGE ') if first else 1
        add('F17', FATAL, page, 'EMI (Annex L)',
            '安全功能级 EMI 措施写 n/a，而每个子系统的 EMI 栏写'
            '"was documented in the associated safety function" —— 指向空字段，'
            'Annex L 的电磁免疫实际无人负责')

    cat_of_sf: dict[int, str] = {}
    for n in nodes:
        where = f'{n.kind} {n.name}'.strip()
        joined = ' '.join(n.text)

        if n.kind == 'SF':
            if n.pfh is not None and n.pl:
                band = pl_from_pfh(n.pfh)
                # a lower Reached PL than the PFHd band allows is conservative
                # (e.g. the subsystem is only suitable up to "d" by qualitative
                # aspects), so only flag the optimistic direction.
                if band and PL_ORDER.index(band) < PL_ORDER.index(n.pl):
                    add('F6', FATAL, n.page, where,
                        f'Reached PL {n.pl} 优于 PFHd={n.pfh:.2e}/h 所能支撑的 PL {band}'
                        '（方向乐观，审核会当场推翻）')
            continue

        if n.cat and re.fullmatch(r'[B1-4]', n.cat.strip()):
            cat_of_sf[n.page] = n.cat.strip()

        # ---- F3: DC grade -------------------------------------------------
        dc_val = None
        m = re.match(r'([0-9.]+)\s*\((High|Medium|Low|None)\)', n.dc or '')
        if m:
            dc_val = float(m.group(1))
            expect = grade_of(dc_val)
            if expect != m.group(2):
                add('F3', WARN, n.page, where,
                    f'DC {dc_val:g}% 标为 {m.group(2)}，按分级应为 {expect}'
                    f'（<60 无 / 60–90 低 / 90–99 中 / >=99 高）')

        # ---- F5: DC% and Category claimed in the text ---------------------
        mt = re.search(r'DC of ([0-9.]+)\s*%', joined)
        if mt and dc_val is not None and abs(float(mt.group(1)) - dc_val) > 0.51:
            add('F5', FATAL, n.page, where,
                f'说明文字写 DC={mt.group(1)}%，表格填 {dc_val:g}%')
        mt = re.search(r'Categor(?:y|ies)\s*[:=]?\s*([B1-4])\b(?!\s+and)', joined)
        if mt and n.cat and re.fullmatch(r'[B1-4]', n.cat.strip()) and mt.group(1) != n.cat.strip():
            add('F5', FATAL, n.page, where,
                f'说明文字写 Category {mt.group(1)}，表格选 {n.cat.strip()}')

        # ---- F1 / F14: B10, RDF, B10d ------------------------------------
        b10, rdf, b10d = to_num(n.b10), to_num(n.rdf), to_num(n.b10d)
        if b10 and b10d and rdf:
            expect = b10 / (rdf / 100.0)
            if abs(expect - b10d) / b10d > 0.02:
                add('F1', FATAL, n.page, where,
                    f'B10={b10:g} ÷ RDF={rdf:g}% 应得 B10d={expect:,.0f}，表格印 {b10d:,.0f}')
        if b10 and b10d and b10d > b10 * 1.5:
            add('F14', INFO, n.page, where,
                f'B10d={b10d:,.0f} 是 B10={b10:g} 的 {b10d / b10:.1f} 倍'
                f'（RDF={rdf or "?"}%）：SISTEMA 的语义是 B10d=B10/RDF，'
                '务必确认厂家原始数据给的是 B10 而不是 B10d，否则 MTTFd 会被抬高 1/RDF 倍')
        if b10 and b10d and not rdf:
            add('F13', WARN, n.page, where,
                f'B10={b10:g} 与 B10d={b10d:,.0f} 同时印出但无 RDF 字段，'
                f'两者比例 {b10d / b10:.2f} 无法在表格内自证')

        # ---- F12 / F13: numbers quoted in the text ------------------------
        for mt in re.finditer(r'B10d\s*(?:value|=|:)?\s*([0-9][0-9,\.]{4,})\s*(?:cycles)?', joined):
            v = to_num(mt.group(1))
            if v and b10d and abs(v - b10d) / b10d > 0.02:
                add('F12', FATAL, n.page, where,
                    f'文字写 B10d={v:,.0f}，表格 B10D={b10d:,.0f}')
                break
        for mt in re.finditer(r'B10\s*(?:value|=|:)?\s*([0-9][0-9,\.]{4,})\s*(?:cycles)?', joined):
            v = to_num(mt.group(1))
            if v and b10 and abs(v - b10) / b10 > 0.02:
                add('F12', FATAL, n.page, where, f'文字写 B10={v:,.0f}，表格 B10={b10:,.0f}')
                break
        mt = re.search(r'(?:[Dd]angerous [Ff]ailures?(?: fraction)?|RDF)\s*[:=]?\s*([0-9.]+)\s*%', joined)
        if mt and rdf is None and b10d:
            add('F13', FATAL, n.page, where,
                f'文字声称填了危险失效比例 {mt.group(1)}%，但表格没有 RDF 字段'
                f'（只印 B10D={b10d:,.0f}）—— 说明与录入方式不符')

        # ---- F2: MTTFd = B10d / (0.1 nop) --------------------------------
        nop = to_num(n.nop)
        mttfd = to_num((n.mttfd or '').split('(')[0])
        if b10d and nop and mttfd:
            expect = b10d / (0.1 * nop)
            if abs(expect - mttfd) / max(mttfd, 1e-9) > 0.01:
                add('F2', FATAL, n.page, where,
                    f'MTTFd={mttfd:g} a ≠ B10d/(0.1×nop)={expect:,.1f} a')

        # ---- F4: MTTFd cap (enforced at channel / subsystem level) --------
        if mttfd and n.kind in ('CH', 'SB') and n.cat and re.fullmatch(r'[1-4]', n.cat.strip()):
            cap = MTTFD_CAP_CAT4 if n.cat.strip() == '4' else MTTFD_CAP_OTHER
            if mttfd > cap + 1:
                add('F4', WARN, n.page, where,
                    f'MTTFd={mttfd:g} a 未按 Cat {n.cat.strip()} 截断到 {cap:g} a')

        # ---- F16: block metadata left unset ------------------------------
        if n.kind == 'BL' and (n.tech in ('unknown', '') or n.cat in ('-', '')):
            add('F16', WARN, n.page, where,
                f'块的 Technology={n.tech or "空"} / Category={n.cat or "空"} 未设置，'
                '在 Cat 3/4 子系统内会成为审核问询点')

        # ---- F15: cites a document but no link ---------------------------
        if not n.links and re.search(r'(datasheet|manual|guide|OTIRON|Datasheet|Manual)\b', joined):
            add('F15', WARN, n.page, where,
                '正文引用了厂家手册/数据表，但 Documentation 栏未挂任何文件链接')

        # ---- F9: documentation links ------------------------------------
        for link in n.links:
            if link.startswith('..\\') or link.startswith('../'):
                add('F9', WARN, n.page, where,
                    f'文档链接为上级目录相对路径 {link[:70]}（报告外发后失效）')
            elif re.search(r'[\u0080-\u00ff]{3,}', link):
                add('F9', FATAL, n.page, where,
                    f'文档链接文件名乱码：{link[:70]}')

        # ---- F8: truncated justification ---------------------------------
        # only the last line of the free-text block can prove a truncation;
        # mid-paragraph lines are ordinary PDF word wrap
        if n.text:
            tail = n.text[-1].strip()
            if len(tail) > 20 and not re.search(r'[.:;)\]"”]$', tail):
                add('F8', FATAL, n.page, where,
                    f'说明字段被字段长度截断，末行：…{tail[-70:]}')

        # ---- F18: CCF score without any justification -------------------
        if n.ccf and 'CCF' not in joined and 'Common cause' not in joined:
            add('F18', WARN, n.page, where,
                f'CCF Points={n.ccf.split("(")[0].strip()} 但该节点没有任何 CCF 措施依据文字')

        # ---- F11: CCF measure caps --------------------------------------
        for key, cap in CCF_CAPS.items():
            for m2 in re.finditer(rf'\b{re.escape(key)}\)?\s*[-—:]\s*(\d+)\s*points?', joined):
                val = int(m2.group(1))
                if val > cap:
                    add('F11', FATAL, n.page, where,
                        f'CCF 措施 {key} 给 {val} 分，超过附录 F 表 F.1 上限 {cap} 分')
        # ---- F18b: measures that add up to the claimed score -------------
        scores = {}
        for key in CCF_CAPS:
            m2 = re.search(rf'\b{re.escape(key)}\)?\s*[-—:]\s*(\d+)\s*points?', joined)
            if m2:
                scores[key] = min(int(m2.group(1)), CCF_CAPS[key])
        if scores and n.ccf:
            capped = sum(scores.values())
            raw = sum(int(m.group(1)) for m in
                      re.finditer(r'\b[A-Z/]{2,3}\)?\s*[-—:]\s*(\d+)\s*points?', joined))
            claimed = to_num(n.ccf.split('(')[0].strip())
            if claimed and capped < claimed <= raw:
                add('F11', FATAL, n.page, where,
                    f'CCF 明细各项相加 {raw} 分，但按附录 F 表 F.1 上限折算只有 {capped} 分，'
                    f'低于 Cat 3 要求的 {CCF_MIN} 分（表格仍显示 {claimed:g} fulfilled）')

    # ---- F10: SF definition fields --------------------------------------
    seen_sf = set()
    for n in nodes:
        if n.kind != 'SF' or n.page in seen_sf:
            continue
        seen_sf.add(n.page)
        empty = [f for f in ('Triggering event', 'Safe state', 'Demand rate', 'Operation mode')
                 if not meta['sf_fields'].get((n.page, f))]
        if empty:
            add('F10', WARN, n.page, f'SF {n.name}',
                '安全功能定义字段为空：' + '、'.join(empty))

    # de-duplicate identical findings
    uniq, keys = [], set()
    for f in out:
        k = (f.rule, f.severity, f.page, f.where, f.detail)
        if k not in keys:
            keys.add(k)
            uniq.append(f)
    return uniq


# --------------------------------------------------------------------------
# output
# --------------------------------------------------------------------------

def render_md(findings: list[Finding]) -> str:
    order = {FATAL: 0, WARN: 1, INFO: 2}
    rows = ['| 规则 | 级别 | 位置 | 发现 |', '|---|---|---|---|']
    for f in sorted(findings, key=lambda x: (order[x.severity], x.rule, int(x.page))):
        rows.append(f'| {f.rule} | {f.severity} | P{f.page} {f.where} | '
                    f'{f.detail.replace("|", "／")} |')
    return '\n'.join(rows)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('textfile')
    ap.add_argument('--json')
    ap.add_argument('--md')
    ap.add_argument('--quiet', action='store_true')
    args = ap.parse_args()

    text = open(args.textfile, encoding='utf-8', errors='replace').read()
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    nodes, meta = parse(text)
    findings = audit(nodes, meta, text)

    fatal = [f for f in findings if f.severity == FATAL]
    warn = [f for f in findings if f.severity == WARN]

    print(f'# {args.textfile}  ({meta["pages"]} pages, {len(nodes)} sections)')
    print(f'# FATAL {len(fatal)} / WARN {len(warn)}\n')
    if not args.quiet:
        cur = None
        for f in sorted(findings, key=lambda x: (x.severity != FATAL, int(x.page), x.rule)):
            if f.page != cur:
                print(f'--- page {f.page} ---')
                cur = f.page
            print(f'[{f.severity:5}] {f.rule:3} {f.where}: {f.detail}')
    if args.json:
        json.dump([f.as_dict() for f in findings], open(args.json, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        print(f'\njson -> {args.json}')
    if args.md:
        open(args.md, 'w', encoding='utf-8').write(render_md(findings) + '\n')
        print(f'md   -> {args.md}')
    return 1 if fatal else 0


if __name__ == '__main__':
    sys.exit(main())
