"""Generate a SISTEMA .ssm project for 移印机 (pad printing machine) emergency-stop circuit.

Approach: read the blueprint .ssm as a *structural template* (fields/rows are XML attributes),
then emit brand-new rows with fresh GUIDs, keeping every template field so the file stays
byte-compatible with what SISTEMA itself writes. Computed fields are copied from the template
(SISTEMA recalculates them on open/refresh).
"""
import os
import re
import uuid
import datetime
import xml.etree.ElementTree as ET

BLUEPRINT = r'C:\Users\sf-bc04.SF\Desktop\SISTEMA V2 测试建模\07-测试\Safety Circuit for Glass Disc Sorting Equipment.ssm'
OUT_DIR = r'C:\Users\sf-bc04.SF\Desktop\SISTEMA V2 测试建模\10-移印机'
OUT = os.path.join(OUT_DIR, '移印机.ssm')

STD = 'ISO 13849-1:2023, ISO 13849-2:2012'
SSM_VERSION = '3.0.4'


def new_oid():
    return str(uuid.uuid4()).upper()


def load(path):
    root = ET.parse(path).getroot()
    return root, {tbl.get('table_name'): [r.attrib for r in tbl.findall('./rows/row')] for tbl in root.iter('table')}


def has_blocks(sb, chs, bls):
    for c in chs:
        if c.get('componentopoid') == sb.get('oid'):
            for b in bls:
                if b.get('parentopoid') == c.get('oid') and b.get('equipmentid'):
                    return True
    return False


# ---------------------------------------------------------------- project definition
PROJECT = {'name': '移印机', 'machinename': '移印机', 'document': '', 'author': '', 'number': '', 'version': ''}
SFS = [{'name': '急停安全回路', 'plr': 'plD', 'plrdet': 'detMeasures'}]

# element tuple keys:
#  channel | equip | model | mfr | group | partno | b10d | nop | mttfd | dc | tech | cat | note
EL = ['channel', 'equip', 'model', 'mfr', 'group', 'partno', 'b10d', 'nop', 'mttfd', 'dc', 'tech', 'cat', 'note']


def e(**kw):
    row = {k: '' for k in EL}
    row.update(kw)
    return row


# SISTEMA refuses to open a project when a block's MTTFd field is empty/invalid
# ("Invalid MTTFD value: -1 / lower than or equal to 3 is not accepted").
# Values below mirror the blueprint's own numbers for the same components.
MTTFD_BY_MODEL = {'G7SA-4A2B': '10', 'SV630 STO': '2283', 'V90 STO Safe Torque Off': '2283'}


def mttfd_for(el):
    if el['tech'] == 'tecElectronic':
        return el['mttfd'] or '100'
    return MTTFD_BY_MODEL.get(el['model'], '100')


ESTOP_NOTE = 'B10d/DC 待按施耐德安全数据表核对'
STO_NOTE = 'STO 参数待按汇川 SV630 安全手册核对'
PNOZ_NOTE = 'MTTFd/DC 待按 Pilz PNOZ c1 手册核对'

# 6 个急停按钮，双通道（每个按钮两个 NC 触点）
estop_elements = []
for ch in ('ch1', 'ch2'):
    for i in range(1, 7):
        estop_elements.append(e(channel=ch, equip='SB%d' % i, model='XB4BS84441', mfr='Schneider Electric',
                                group='E-Stop_Function', partno='XB4BS84441', b10d='1500000', nop='700',
                                dc='0.65', tech='tecElectromechanic', cat='catN', note=ESTOP_NOTE))

# 2 个强制导向继电器，每个通道一个
relay_elements = [
    e(channel='ch1', equip='KA1', model='G7SA-4A2B', mfr='OMRON', group='Safety Relay',
      partno='G7SA-4A2B-DC24', b10d='20000000', nop='2000', dc='0.65', tech='tecElectromechanic', cat='catN'),
    e(channel='ch2', equip='KA2', model='G7SA-4A2B', mfr='OMRON', group='Safety Relay',
      partno='G7SA-4A2B-DC24', b10d='20000000', nop='2000', dc='0.65', tech='tecElectromechanic', cat='catN'),
]

# 8 台汇川 SV630 的 STO，双通道
sto_elements = []
for ch in ('ch1', 'ch2'):
    for i in range(1, 9):
        sto_elements.append(e(channel=ch, equip='SV%d' % i, model='SV630 STO', mfr='Inovance',
                              group='Safe drive / STO', mttfd='2283', dc='0.65', tech='tecElectronic',
                              cat='cat3', note=STO_NOTE))

SUBSYSTEMS = [
    {'name': '急停按钮串联（6个）', 'func': 'fncInput', 'cat': 'cat3', 'ccf': '65', 'elements': estop_elements},
    {'name': 'PNOZ c1 安全继电器', 'func': 'fncLogic', 'cat': 'cat4', 'ccf': '0', 'elements': [
        e(equip='K1', model='PNOZ c1', mfr='Pilz', group='Safety Relay', mttfd='100', dc='0.99',
          tech='tecElectronic', cat='cat4', note=PNOZ_NOTE)]},
    {'name': 'G7SA-4A2B 强导继电器', 'func': 'fncOutput', 'cat': 'cat3', 'ccf': '65', 'elements': relay_elements},
    {'name': 'SV630 STO 输出（8轴）', 'func': 'fncOutput', 'cat': 'cat3', 'ccf': '65', 'elements': sto_elements},
]


def main():
    root, t = load(BLUEPRINT)
    pr_tpl = t['projectops'][0]
    sf_tpl = t['sfops'][0]
    chs, bls, els = t['channelops'], t['blocops'], t['elementops']
    sb_tpl = next(sb for sb in t['componentops'] if has_blocks(sb, chs, bls))
    ch_tpl = chs[0]
    bl_tpl = next(b for b in bls if b.get('equipmentid'))
    empty_tpl = next(b for b in bls if not b.get('equipmentid'))
    el_tpl = els[0]

    def mk(tpl, oid, **kw):
        d = dict(tpl)
        d['oid'] = oid
        d['ssmversion'] = SSM_VERSION
        d['normversion'] = STD
        d['isprotected'] = '0'
        d.update({k: v for k, v in kw.items()})
        return d

    rows = {name: [] for name in t}
    now = datetime.datetime.now()
    created = now.strftime('%d/%m/%Y %H:%M:%S:') + '%03d' % (now.microsecond // 1000)

    pr_oid = new_oid()
    rows['projectops'].append(mk(pr_tpl, pr_oid, name=PROJECT['name'], machinename=PROJECT['machinename'],
                                 author=PROJECT['author'], document=PROJECT['document'],
                                 filename=OUT, createdate=created, documentation='',
                                 tester='', manager='', status='', number=PROJECT['number'],
                                 version=PROJECT['version']))

    for sf in SFS:
        sf_oid = new_oid()
        rows['sfops'].append(mk(sf_tpl, sf_oid, projectopoid=pr_oid, name=sf['name'],
                                plr=sf['plr'], plrdet=sf['plrdet'], document='', documentation='',
                                plrdocumentation='', plrdocument='', plrstandard='', plrstandardfile='',
                                reaction='', requestfrequency='', responsetime='', priority='',
                                safestate='', sftype='', triggerevent='', opmode='',
                                emiroute='emiU', emidocumentation='', emidocument='', emimeasures=''))

        for sb in SUBSYSTEMS:
            sb_oid = new_oid()
            chain_mode = any(el['channel'] for el in sb['elements'])
            single = sb['elements'][0] if not chain_mode else None

            overrides = dict(sfopoid=sf_oid, name=sb['name'], functiontypes=sb['func'],
                             cat=sb['cat'], ccfscore=sb['ccf'], document='', usecase='',
                             catdocumentation='', catstandard='', catstandardfile='',
                             ccfdocument='', ccfdocumentation='', dcavgdocument='', dcavgdocumentation='',
                             mttfddocumentation='', mttfddocument='', libname='', libid='', libfilename='',
                             partno='', revision='', equipmentid='', manufacturer='', deviceid='',
                             devicegroup='', description='', missiontime='20', pfh='0')
            if single:
                # device-level parameters sit on the subsystem itself -> PL is given directly
                overrides.update(mttfd=single['mttfd'], dcavg=single['dc'], mttfddet='detDirect',
                                 dcavgdet='detDirect', pldet='detDirect', ccfscoredet='detMeasures',
                                 catconditionsrelevant='0', catconditions='',
                                 manufacturer=single['mfr'], deviceid=single['model'],
                                 devicegroup=single['group'], equipmentid=single['equip'])
            else:
                overrides.update(mttfddet='detSubItems', dcavgdet='detSubItems')
            rows['componentops'].append(mk(sb_tpl, sb_oid, **overrides))

            ch_oids = {}
            for ctype in ('ch1', 'ch2', 'chTest'):
                ch_oid = new_oid()
                ch_oids[ctype] = ch_oid
                rows['channelops'].append(mk(ch_tpl, ch_oid, componentopoid=sb_oid,
                                             channeltype=ctype, name=''))

            for ctype in ('ch1', 'ch2', 'chTest'):
                assigned = [x for x in sb['elements'] if x['channel'] == ctype]
                if not assigned:
                    # SISTEMA keeps one (empty) block in every channel
                    bl_oid = new_oid()
                    rows['blocops'].append(mk(empty_tpl, bl_oid, parentopoid=ch_oids[ctype]))
                    rows['elementops'].append(mk(el_tpl, new_oid(), parentopoid=bl_oid, name=''))
                    continue
                for el in assigned:
                    bl_oid = new_oid()
                    is_elec = el['tech'] == 'tecElectronic'
                    rows['blocops'].append(mk(
                        bl_tpl, bl_oid, parentopoid=ch_oids[ctype],
                        name=el['model'], equipmentid=el['equip'], deviceid=el['model'],
                        manufacturer=el['mfr'], devicegroup=el['group'], partno=el['partno'],
                        b10d=el['b10d'] or '0', nop=el['nop'] if not is_elec else 'FE',
                        mttfd=mttfd_for(el), mttfddet='detDirect' if is_elec else 'detB10D',
                        dc=el['dc'], technology=el['tech'], cat=el['cat'],
                        functiontypes=sb['func'].split(',')[0],
                        missiontime='20', description='', usecase=el['note'],
                        usecasedocumentation='', document='',
                        dcdocumentation='', dcdocument='', mttfddocumentation='', mttfddocument='',
                        dcmeasure='', dcmeasuredc='0', dcmeasuredocumentation='', dcmeasuredocument=''))
                    rows['elementops'].append(mk(el_tpl, new_oid(), parentopoid=bl_oid, name=''))

    # write tables back
    for tbl in root.iter('table'):
        name = tbl.get('table_name')
        rows_el = tbl.find('./rows')
        for r in list(rows_el):
            rows_el.remove(r)
        for attrib in rows.get(name, []):
            ET.SubElement(rows_el, 'row', {k: str(v) for k, v in attrib.items()})

    # local sanity check: SISTEMA rejects b10d < 0 and mttfd <= 3 on any block
    problems = []
    for b in rows['blocops']:
        equip = b.get('equipmentid') or '(empty block)'
        try:
            if float(b.get('b10d') or 0) < 0:
                problems.append(('b10d', equip, b.get('b10d')))
        except ValueError:
            problems.append(('b10d', equip, b.get('b10d')))
        try:
            if float(b.get('mttfd') or -1) <= 3:
                problems.append(('mttfd', equip, b.get('mttfd')))
        except ValueError:
            problems.append(('mttfd', equip, b.get('mttfd')))
        try:
            dc = float(b.get('dc') or 0)
            if dc < 0 or dc > 1:
                problems.append(('dc', equip, b.get('dc')))
        except ValueError:
            problems.append(('dc', equip, b.get('dc')))
    print('  sanity check:', 'OK' if not problems else problems[:8])

    os.makedirs(OUT_DIR, exist_ok=True)
    body = ET.tostring(root, encoding='unicode')
    with open(OUT, 'w', encoding='utf-8', newline='') as fh:
        fh.write('<?xml version="1.0"?>\r\n' + body + '\r\n')

    print('wrote:', OUT)
    for name, r in rows.items():
        if r:
            print('  %-18s %d rows' % (name, len(r)))


if __name__ == '__main__':
    main()
