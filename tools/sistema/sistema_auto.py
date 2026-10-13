"""SISTEMA automatic modelling: structured description -> valid .ssm project.

Design note
-----------
A .ssm file is tiOPF XML and every table carries a <fields> block describing each
column (name, kind, size).  Rather than hard-coding those declarations (which change
between SISTEMA releases), this tool **copies the field declarations from a template
project** - any .ssm saved by the locally installed SISTEMA - and rebuilds only the
<rows>.  That keeps the output bit-compatible with whatever version wrote the template.

Usage
-----
    python sistema_auto.py schema <template.ssm>              # dump column definitions
    python sistema_auto.py demo   <out.ssm> [--template T]    # built-in pad-printing e-stop
    python sistema_auto.py build  <spec.json> <out.ssm> [--template T]
    python sistema_auto.py check  <out.ssm>                   # validate a generated file
    python sistema_auto.py show   <out.ssm>                   # summarise an existing project

Conventions recovered from 35 official IFA example projects (see ssm-schema.md):
  * numbers use a COMMA decimal separator (German locale): 4,23E-6
  * -2 means "not set"; b10d=0 means "B10d not used"
  * componentops has NO 'pl' column - PL lives in plsubitemscal / pldirectcal
  * every subsystem owns exactly three channels: ch1, ch2, chTest
"""
from __future__ import annotations

import json
import os
import re
import sys
import uuid
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Any

SSMVERSION = '3.0.4'
NORMVERSION = 'ISO 13849-1:2023, ISO 13849-2:2012'
DEFAULT_TEMPLATE = os.path.join(
    os.path.expanduser('~'), 'Desktop', 'SISTEMA V2 测试建模', '10-移印机', '移印机.ssm')

# ---------------------------------------------------------------- enum mappings
PL = {'n': 'plN', 'a': 'plA', 'b': 'plB', 'c': 'plC', 'd': 'plD', 'e': 'plE'}
CAT = {'b': 'catB', '1': 'cat1', '2': 'cat2', '3': 'cat3', '4': 'cat4'}
TECH = {
    'electronic': 'tecElectronic', 'electromechanic': 'tecElectromechanic',
    'pneumatic': 'tecPneumatic', 'hydraulic': 'tecHydraulic',
    'mechanic': 'tecMechanic', 'other': 'tecOther', 'unknown': 'tecUnknown',
}
FNC = {'input': 'fncInput', 'logic': 'fncLogic', 'output': 'fncOutput',
       'unknown': 'fncUnknown'}
CHANNELS = ('ch1', 'ch2', 'chTest')


def pl(v: Any) -> str:
    return PL.get(str(v).strip().lower(), 'plN')


def cat(v: Any) -> str:
    return CAT.get(str(v).strip().lower(), 'catB')


def tech(v: Any) -> str:
    return TECH.get(str(v).strip().lower(), 'tecUnknown')


def fnc(v: Any) -> str:
    return FNC.get(str(v).strip().lower(), 'fncUnknown')


def num(v: Any, not_set: str = '-2') -> str:
    """Format a number for the .ssm file.

    SISTEMA 3.0.4 writes plain decimal points (``dc="0.65"``, ``lambda="1.14155E-5"``),
    whereas the 2.0.8-era official IFA examples used German commas (``4,23E-6``).
    Both spellings are normalised to a dot here, matching the 3.0.4 template.
    """
    if v is None or v == '':
        return not_set
    if isinstance(v, str):
        v = v.strip().replace(',', '.')
        return v if v else not_set
    if isinstance(v, bool):
        return '1' if v else '0'
    if isinstance(v, int):
        return str(v)
    return repr(float(v)) if float(v) != int(v) else str(int(v))


def oid() -> str:
    return str(uuid.uuid4()).upper()


def esc(s: Any) -> str:
    return (str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            .replace('"', '&quot;'))


# ---------------------------------------------------------------- data model
@dataclass
class Element:
    """EL - leaf component. Anything with a B10d belongs at this level."""
    name: str = ''
    mttfd: Any = 10
    dc: Any = 0
    b10d: Any = 0
    nop: Any = None          # None -> -2 (not set)
    technology: str = 'unknown'
    function: str = 'unknown'

    def columns(self) -> dict[str, Any]:
        return {
            'name': self.name, 'mttfd': num(self.mttfd), 'dc': num(self.dc, '0'),
            'b10d': num(self.b10d, '0'), 'nop': num(self.nop),
            'technology': tech(self.technology), 'functiontypes': fnc(self.function),
            'calcmttfddet': 'calcMTTFdMTTF', 'mttfddet': 'detDirect',
            'dcdet': 'detDirect',
        }


@dataclass
class Block:
    """BL - functional unit inside a channel."""
    name: str = ''
    mttfd: Any = 10
    dc: Any = 0
    b10d: Any = 0
    nop: Any = None
    technology: str = 'unknown'
    function: str = 'unknown'
    manufacturer: str = ''
    deviceid: str = ''
    partno: str = ''
    elements: list[Element] = field(default_factory=list)

    def columns(self) -> dict[str, Any]:
        cols: dict[str, Any] = {
            'name': self.name, 'mttfd': num(self.mttfd), 'dc': num(self.dc, '0'),
            'b10d': num(self.b10d, '0'), 'nop': num(self.nop),
            'technology': tech(self.technology), 'functiontypes': fnc(self.function),
            'calcmttfddet': 'calcMTTFdMTTF', 'mttfddet': 'detDirect',
            'dcdet': 'detDirect',
        }
        if self.manufacturer:
            cols['manufacturer'] = self.manufacturer
        if self.deviceid:
            cols['deviceid'] = self.deviceid
        if self.partno:
            cols['partno'] = self.partno
        return cols


@dataclass
class Subsystem:
    """SB - the 2023-edition 'subsystem', either rigid-structure or encapsulated."""
    name: str = ''
    category: str = 'B'
    function: str = 'unknown'
    ccf: Any = 0
    mttfd: Any = 10
    dcavg: Any = 0
    pfh: str = '3.8E-5'          # template default; recalculated on open (3.0.4 uses a dot)
    encapsulated: bool = False   # True -> manufacturer states PL/PFH, channels stay empty
    pl_value: str = ''           # for encapsulated subsystems (e.g. 'd')
    channels: dict[str, list[Block]] = field(default_factory=dict)

    def channel_blocks(self, ch: str) -> list[Block]:
        return self.channels.get(ch, []) or []


@dataclass
class SafetyFunction:
    name: str = ''
    plr: str = 'c'
    sftype: str = 'Safety-related stop function initiated by safeguard'
    reaction: str = 'Stopping dangerous movement, STO (safe torque off)'
    triggerevent: str = ''
    safestate: str = ''
    opmode: str = ''
    requestfrequency: str = ''
    responsetime: str = ''
    subsystems: list[Subsystem] = field(default_factory=list)


@dataclass
class Project:
    name: str = 'SISTEMA Project'
    machine: str = ''
    author: str = ''
    safety_functions: list[SafetyFunction] = field(default_factory=list)


# ---------------------------------------------------------------- template access
def load_field_defs(template: str) -> dict[str, list[str]]:
    """Return {table_name: ["<field .../>", ...]} copied verbatim from the template."""
    root = ET.parse(template).getroot()
    out: dict[str, list[str]] = {}
    for tbl in root.iter('table'):
        name = tbl.get('table_name')
        if not name:
            continue
        defs = []
        for f in tbl.findall('./fields/field'):
            kind = f.get('field_kind', 'string')
            size = f.get('field_Size', '0')
            defs.append(f'<field field_name="{esc(f.get("field_name"))}" '
                        f'field_kind="{kind}" field_Size="{size}"/>')
        out[name] = defs
    return out


def table_xml(name: str, defs: list[str], rows: list[dict[str, Any]],
              order: list[str] | None = None,
              defaults: dict[str, str] | None = None) -> str:
    """Build one <table> element.

    Two rules learned the hard way from SISTEMA 3.0.4:

    * **Every declared column must be written**, empty ones as ``""``.  Omitting a
      column makes the tiOPF reader fail with ``Error reading field <Document>``.
    * **Only declared columns may be written.**  An unknown attribute is rejected
      with error code 1866 -- that is how the 2.0.8-era ``pldirectcal`` fails on
      3.0.4, where the column was renamed to ``pldirectbindcal``.

    Missing values are taken from the template's own first data row (``defaults``),
    which also reproduces the exact type/empty conventions of that SISTEMA version.
    """
    cols: list[str] = []
    for d in defs:
        m = re.search(r'field_name="([^"]+)"', d)
        if m:
            cols.append(m.group(1))
    allowed = set(cols)
    defaults = defaults or {}
    dropped: set[str] = set()
    parts = [f'<table table_name="{name}"><fields>', ''.join(defs), '</fields><rows>']
    for row in rows:
        dropped |= {k for k in row if k not in allowed}
        full = {}
        for col in cols:                       # write every declared column, in order
            if col in row:
                full[col] = row[col]
            elif col in defaults:
                full[col] = defaults[col]
            else:
                full[col] = ''
        for k in (order or []):                # keep key columns up front
            if k in full:
                full[k] = full.pop(k)
        attrs = ''.join(f' {k}="{esc(v)}"' for k, v in full.items())
        parts.append(f'<row{attrs}/>')
    parts.append('</rows></table>')
    if dropped:
        print(f'  [已丢弃模板未声明的列] {name}: {", ".join(sorted(dropped))}')
    return ''.join(parts)


def template_defaults(template: str) -> dict[str, dict[str, str]]:
    """{table: {column: value}} taken from the template's first row of each table."""
    root = ET.parse(template).getroot()
    out: dict[str, dict[str, str]] = {}
    for tbl in root.iter('table'):
        name = tbl.get('table_name')
        if not name:
            continue
        rows = tbl.findall('./rows/row')
        out[name] = dict(rows[0].attrib) if rows else {}
    return out


# ---------------------------------------------------------------- generation
def build_project(project: Project, template: str) -> str:
    defs = load_field_defs(template)
    base = {'ssmversion': SSMVERSION, 'normversion': NORMVERSION, 'isprotected': '0'}

    pr_oid = oid()
    pr_rows = [dict(base, oid=pr_oid, name=project.name,
                    machinename=project.machine or project.name,
                    author=project.author or '')]

    sf_rows, sb_rows, ch_rows, bl_rows, el_rows = [], [], [], [], []

    for sf in project.safety_functions:
        sf_oid = oid()
        sf_rows.append(dict(
            base, oid=sf_oid, projectopoid=pr_oid, name=sf.name,
            plr=pl(sf.plr), plrdet='detDirect',
            sftype=sf.sftype, reaction=sf.reaction,
            triggerevent=sf.triggerevent, safestate=sf.safestate,
            opmode=sf.opmode, requestfrequency=sf.requestfrequency,
            responsetime=sf.responsetime,
            plcal='plN', pfhcal='-1'))

        for sb in sf.subsystems:
            sb_oid = oid()
            if sb.encapsulated:
                # Manufacturer states PL / PFH -> detDirect everywhere, PL from pldirectcal
                sb_cols = dict(
                    base, oid=sb_oid, sfopoid=sf_oid, name=sb.name,
                    cat=cat(sb.category), functiontypes=fnc(sb.function),
                    ccfscore=num(sb.ccf, '0'), ccfscoredet='detDirect',
                    mttfd=num(sb.mttfd), mttfddet='detDirect',
                    dcavg=num(sb.dcavg, '0'), dcavgdet='detDirect',
                    pfh=sb.pfh, pldet='detDirect',
                    plsubitemscal='plN',
                    # 3.0.4 把 2.0.8 的 pldirectcal 改名为 pldirectbindcal
                    pldirectbindcal=pl(sb.pl_value) if sb.pl_value else '-')
            else:
                blocks_any = any(sb.channel_blocks(c) for c in CHANNELS)
                sb_cols = dict(
                    base, oid=sb_oid, sfopoid=sf_oid, name=sb.name,
                    cat=cat(sb.category), functiontypes=fnc(sb.function),
                    ccfscore=num(sb.ccf, '0'), ccfscoredet='detDirect',
                    mttfd=num(sb.mttfd), mttfddet='detDirect' if not blocks_any else 'detSubItems',
                    dcavg=num(sb.dcavg, '0'), dcavgdet='detDirect' if not blocks_any else 'detSubItems',
                    pfh=sb.pfh,
                    pldet='detSubItems' if blocks_any else 'detDirect',
                    plsubitemssimplecal='plN')
            sb_rows.append(sb_cols)

            for ch_type in CHANNELS:
                ch_oid = oid()
                ch_rows.append(dict(base, oid=ch_oid, componentopoid=sb_oid,
                                    channeltype=ch_type, name=''))
                for blk in sb.channel_blocks(ch_type):
                    bl_oid = oid()
                    bl_rows.append(dict(base, oid=bl_oid, parentopoid=ch_oid,
                                        **blk.columns()))
                    for el in blk.elements:
                        el_rows.append(dict(base, oid=oid(), parentopoid=bl_oid,
                                            **el.columns()))

    # 表集合、表顺序与字段声明完全由模板决定：模板有哪张表就输出哪张（包括
    # messagehelperops 这类辅助表），只把行数据换成我们的。这样既不会漏表，
    # 也不会凭空造出模板里没有的表（例如未使用措施清单时就没有 dcmeasureops）。
    rows_by_table = {
        'projectops': pr_rows, 'sfops': sf_rows, 'componentops': sb_rows,
        'channelops': ch_rows, 'blocops': bl_rows, 'elementops': el_rows,
    }
    order = {
        'projectops': ['oid', 'ssmversion', 'normversion', 'isprotected', 'name'],
        'sfops': ['oid', 'ssmversion', 'normversion', 'isprotected', 'projectopoid', 'name'],
        'componentops': ['oid', 'ssmversion', 'normversion', 'isprotected', 'sfopoid', 'name'],
        'channelops': ['oid', 'ssmversion', 'normversion', 'isprotected', 'channeltype',
                       'componentopoid', 'name'],
        'blocops': ['oid', 'ssmversion', 'normversion', 'isprotected', 'parentopoid', 'name'],
        'elementops': ['oid', 'ssmversion', 'normversion', 'isprotected', 'parentopoid', 'name'],
    }
    defaults_map = template_defaults(template)
    tables = []
    for tbl in ET.parse(template).getroot().iter('table'):
        name = tbl.get('table_name')
        defs = [f'<field field_name="{esc(f.get("field_name"))}" '
                f'field_kind="{f.get("field_kind", "string")}" '
                f'field_Size="{f.get("field_Size", "0")}"/>'
                for f in tbl.findall('./fields/field')]
        tables.append(table_xml(name, defs, rows_by_table.get(name, []),
                                order.get(name), defaults_map.get(name, {})))
    return ('<?xml version="1.0"?>\n<xmldocdata><tiopf version="2.1"/><tables>'
            + ''.join(tables) + '</tables></xmldocdata>')


# ---------------------------------------------------------------- validation
def check_project(project: Project) -> list[str]:
    """Catch the mistakes that make SISTEMA refuse a file, before it is written."""
    problems: list[str] = []
    if not project.safety_functions:
        problems.append('没有安全功能（SF）')
    for sf in project.safety_functions:
        tag = f'SF "{sf.name}"'
        if not sf.name:
            problems.append(f'{tag}: 名称为空')
        if not sf.subsystems:
            problems.append(f'{tag}: 没有子系统（SB）')
        for sb in sf.subsystems:
            stag = f'  SB "{sb.name}"'
            c = str(sb.category).upper()
            if sb.encapsulated:
                if not sb.pfh or sb.pfh.replace(',', '.') == '3.8E-5':
                    problems.append(f'{stag}: 封装子系统应填厂家 PFH（当前是模板默认值）')
                if any(sb.channel_blocks(ch) for ch in CHANNELS):
                    problems.append(f'{stag}: 封装子系统不应包含块（内部结构不拆解）')
                continue
            # rigid structure rules
            if c in ('2', '3', '4') and float(str(sb.ccf or 0)) < 65:
                problems.append(f'{stag}: Cat {c} 要求 CCF ≥ 65（当前 {sb.ccf}）')
            d = float(str(sb.dcavg or 0))
            if c == '4' and d < 90:
                problems.append(f'{stag}: Cat 4 要求 DCavg 高（≥90%），当前 {sb.dcavg}')
            if c == '3' and d >= 99:
                problems.append(f'{stag}: DCavg ≥99% 时应考虑 Cat 4')
            if c in ('3', '4') and not any(sb.channel_blocks(x) for x in ('ch1', 'ch2')):
                problems.append(f'{stag}: Cat {c} 需要两个通道都有块')
            for ch in CHANNELS:
                for blk in sb.channel_blocks(ch):
                    btag = f'{stag} → {ch} → BL "{blk.name}"'
                    try:
                        if float(str(blk.mttfd)) <= 3 and str(blk.b10d) in ('0', '', 'None'):
                            problems.append(f'{btag}: MTTFd 必须 > 3（或给出 B10d 让软件计算）')
                    except ValueError:
                        pass
                    if blk.b10d not in (0, '0', '', None) and not blk.elements:
                        problems.append(f'{btag}: 带 B10d 的元件应细分到元素级（官方流程）')
                    for el in blk.elements:
                        try:
                            if float(str(el.mttfd)) <= 3 and str(el.b10d) in ('0', '', 'None'):
                                problems.append(f'{btag} → EL: MTTFd 必须 > 3')
                        except ValueError:
                            pass
    return problems


# ---------------------------------------------------------------- demo spec
def demo_project() -> Project:
    """The pad-printing machine e-stop circuit, mirroring IFA example 10."""
    return Project(
        name='移印机', machine='Pad printing machine', author='',
        safety_functions=[SafetyFunction(
            name='Actuation of the emergency stop devices leads to STO of all pad-printing axes',
            plr='c',
            sftype='Safety-related stop function initiated by safeguard',
            reaction='Stopping dangerous movement, STO (safe torque off)',
            triggerevent='Actuation of one of the 6 emergency stop pushbuttons',
            safestate='Safe torque off of the 8 Inovance SV630 drives',
            opmode='Automatic mode',
            subsystems=[
                Subsystem(
                    name='Emergency stop devices (6 x XB4BS84441)', category='3',
                    function='input', ccf=65, mttfd=10, dcavg=0,
                    channels={
                        'ch1': [Block(name='S1..S6.1', mttfd=10, dc=0.6, b10d=100000,
                                      nop=1, technology='electromechanic', function='input',
                                      manufacturer='Schneider Electric',
                                      deviceid='XB4BS84441',
                                      elements=[Element(name='XB4BS84441', mttfd=10, dc=0.6,
                                                        b10d=100000, nop=1,
                                                        technology='electromechanic',
                                                        function='input')])],
                        'ch2': [Block(name='S1..S6.2', mttfd=10, dc=0.6, b10d=100000,
                                      nop=1, technology='electromechanic', function='input',
                                      manufacturer='Schneider Electric',
                                      deviceid='XB4BS84441',
                                      elements=[Element(name='XB4BS84441', mttfd=10, dc=0.6,
                                                        b10d=100000, nop=1,
                                                        technology='electromechanic',
                                                        function='input')])],
                    }),
                Subsystem(
                    name='PNOZ c1 safety relay', category='3', function='logic',
                    encapsulated=True, pfh='3E-7', pl_value='d'),
                Subsystem(
                    name='G7SA-4A2B force-guided relays', category='3',
                    function='output', ccf=65, mttfd=10, dcavg=0,
                    channels={
                        'ch1': [Block(name='KA1', mttfd=10, dc=0.99, b10d=20000000,
                                      nop=2000, technology='electromechanic',
                                      function='output', manufacturer='OMRON',
                                      deviceid='G7SA-4A2B',
                                      elements=[Element(name='G7SA-4A2B', mttfd=10, dc=0.99,
                                                        b10d=20000000, nop=2000,
                                                        technology='electromechanic',
                                                        function='output')])],
                        'ch2': [Block(name='KA2', mttfd=10, dc=0.99, b10d=20000000,
                                      nop=2000, technology='electromechanic',
                                      function='output', manufacturer='OMRON',
                                      deviceid='G7SA-4A2B',
                                      elements=[Element(name='G7SA-4A2B', mttfd=10, dc=0.99,
                                                        b10d=20000000, nop=2000,
                                                        technology='electromechanic',
                                                        function='output')])],
                    }),
                Subsystem(
                    name='SV630 STO inputs (8 axes)', category='3', function='output',
                    ccf=65, mttfd=10, dcavg=0,
                    channels={
                        'ch1': [Block(name='SV1..SV8 STO-A', mttfd=2283, dc=0.99, b10d=0,
                                      technology='electronic', function='output',
                                      manufacturer='Inovance', deviceid='SV630',
                                      elements=[Element(name='SV630 STO', mttfd=2283, dc=0.99,
                                                        b10d=0, technology='electronic',
                                                        function='output')])],
                        'ch2': [Block(name='SV1..SV8 STO-B', mttfd=2283, dc=0.99, b10d=0,
                                      technology='electronic', function='output',
                                      manufacturer='Inovance', deviceid='SV630',
                                      elements=[Element(name='SV630 STO', mttfd=2283, dc=0.99,
                                                        b10d=0, technology='electronic',
                                                        function='output')])],
                    }),
            ])])


def project_from_spec(spec: dict[str, Any]) -> Project:
    pr = spec.get('project', {})
    project = Project(name=pr.get('name', 'SISTEMA Project'),
                      machine=pr.get('machine', ''), author=pr.get('author', ''))
    for sf_spec in spec.get('safety_functions', []):
        sf = SafetyFunction(
            name=sf_spec.get('name', ''), plr=sf_spec.get('plr', 'c'),
            sftype=sf_spec.get('sftype', ''),
            reaction=sf_spec.get('reaction', ''),
            triggerevent=sf_spec.get('triggerevent', ''),
            safestate=sf_spec.get('safestate', ''),
            opmode=sf_spec.get('opmode', ''),
            requestfrequency=sf_spec.get('requestfrequency', ''),
            responsetime=sf_spec.get('responsetime', ''))
        for sb_spec in sf_spec.get('subsystems', []):
            sb = Subsystem(
                name=sb_spec.get('name', ''), category=sb_spec.get('category', 'B'),
                function=sb_spec.get('function', 'unknown'),
                ccf=sb_spec.get('ccf', 0), mttfd=sb_spec.get('mttfd', 10),
                dcavg=sb_spec.get('dcavg', 0), pfh=sb_spec.get('pfh', '3.8E-5'),
                encapsulated=bool(sb_spec.get('encapsulated', False)),
                pl_value=sb_spec.get('pl', ''))
            for ch_name, blocks in (sb_spec.get('channels') or {}).items():
                sb.channels[ch_name] = [
                    Block(
                        name=b.get('name', ''), mttfd=b.get('mttfd', 10),
                        dc=b.get('dc', 0), b10d=b.get('b10d', 0), nop=b.get('nop'),
                        technology=b.get('technology', 'unknown'),
                        function=b.get('function', 'unknown'),
                        manufacturer=b.get('manufacturer', ''),
                        deviceid=b.get('deviceid', ''),
                        partno=b.get('partno', ''),
                        elements=[Element(**e) for e in b.get('elements', [])])
                    for b in blocks]
            sf.subsystems.append(sb)
        project.safety_functions.append(sf)
    return project


# ---------------------------------------------------------------- inspection
def summarise(path: str) -> str:
    root = ET.parse(path).getroot()
    def rows(t: str) -> list[dict]:
        for tbl in root.iter('table'):
            if tbl.get('table_name') == t:
                return [r.attrib for r in tbl.findall('./rows/row')]
        return []
    out = []
    pr = rows('projectops')
    if pr:
        p = pr[0]
        out.append(f"PR: {p.get('name')} | ssmversion={p.get('ssmversion')} | norm={p.get('normversion')}")
    sfs, sbs, chs = rows('sfops'), rows('componentops'), rows('channelops')
    bls, els = rows('blocops'), rows('elementops')
    out.append(f"表行数: SF={len(sfs)} SB={len(sbs)} CH={len(chs)} BL={len(bls)} EL={len(els)}")
    for s in sfs:
        out.append(f"  SF: {s.get('name')} | PLr={s.get('plr')} PL={s.get('plcal')} PFH={s.get('pfhcal')}")
    for b in sbs:
        out.append(f"    SB: {b.get('name')} | cat={b.get('cat')} mttfd={b.get('mttfd')} "
                   f"dcavg={b.get('dcavg')} ccf={b.get('ccfscore')} pfh={b.get('pfh')} "
                   f"pldet={b.get('pldet')} fn={b.get('functiontypes')}")
        for c in [x for x in chs if x.get('componentopoid') == b.get('oid')]:
            n = len([x for x in bls if x.get('parentopoid') == c.get('oid')])
            if n:
                out.append(f"      CH {c.get('channeltype')}: {n} 块")
    return '\n'.join(out)


def write_utf8(path: str, text: str) -> None:
    with open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(text)


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 1
    cmd = argv[1]
    template = DEFAULT_TEMPLATE
    if '--template' in argv:
        template = argv[argv.index('--template') + 1]

    if cmd == 'schema':
        defs = load_field_defs(argv[2])
        for name, fields in defs.items():
            print(f'--- {name}: {len(fields)} 列')
            for f in fields[:6]:
                print('   ', f)
        return 0

    if cmd == 'demo':
        out = argv[2]
        project = demo_project()
    elif cmd == 'build':
        with open(argv[2], encoding='utf-8') as fh:
            project = project_from_spec(json.load(fh))
        out = argv[3]
    elif cmd == 'check':
        print(summarise(argv[2]))
        return 0
    elif cmd == 'show':
        print(summarise(argv[2]))
        return 0
    else:
        print(__doc__)
        return 1

    problems = check_project(project)
    if problems:
        print(f'校验发现 {len(problems)} 个问题（仍会生成文件，但 SISTEMA 可能报错）：')
        for p in problems:
            print('  !', p)
    if not os.path.exists(template):
        print(f'模板项目不存在: {template}')
        return 2
    xml = build_project(project, template)
    write_utf8(out, xml)
    print(f'已生成 {out} ({len(xml):,} 字节, {len(xml.encode("utf-8")):,} bytes UTF-8)')
    print(f'模板: {template}')
    print(summarise(out))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
