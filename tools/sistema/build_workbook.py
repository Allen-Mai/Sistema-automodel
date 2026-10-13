"""Build a SISTEMA modeling workbook: one sheet per subsystem, Chinese dropdowns, minimal input.

Structure:
  说明 / 1-项目信息 / 2-安全功能SF / SB空白模板 / SB01..SBnn (one per subsystem) / 元器件型号参考 / 枚举参考
Users only fill: SF name + PLr, and in each subsystem sheet the element 位号 + 型号.
Everything else (brand, B10d, nop, MTTFd, DC, technology, role, category, CCF) is optional and gets completed later.
"""
import re
import xml.etree.ElementTree as ET
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter

SSM = r'C:\Users\sf-bc04.SF\Desktop\SISTEMA V2 测试建模\07-测试\Safety Circuit for Glass Disc Sorting Equipment.ssm'
OUT = r'C:\Users\sf-bc04.SF\Desktop\SISTEMA建模资料模板.xlsx'

HEAD_FILL = PatternFill('solid', fgColor='DDEBF7')
KEY_FILL = PatternFill('solid', fgColor='EDF3FA')
HEAD_FONT = Font(bold=True, size=10)
TITLE_FONT = Font(bold=True, size=12)

PLR = {'plA': 'PL a', 'plB': 'PL b', 'plC': 'PL c', 'plD': 'PL d', 'plE': 'PL e'}
ROLE = {'fncInput': '输入', 'fncLogic': '逻辑', 'fncOutput': '输出'}
CAT = {'catB': 'Cat. B', 'cat1': 'Cat. 1', 'cat2': 'Cat. 2', 'cat3': 'Cat. 3', 'cat4': 'Cat. 4'}
CAT_BLK = {'catN': '未指定', **CAT}
CHAN = {'ch1': '通道1', 'ch2': '通道2', 'chTest': '测试通道'}
TECH = {'tecElectromechanic': '机电', 'tecElectronic': '电子'}
CCF = {'0': '未评估（0）', '60': '部分满足（60）', '65': '满足措施（65）', '90': '较高（90）', '99': '很高（99）'}

ELEMENT_HEAD = ['通道', '序号', '位号', '型号', '品牌', 'B10d', 'nop（每年动作次数）',
                'MTTFd（电子件）', 'DC', '技术类型', '说明']
ELEMENT_WIDTHS = [12, 6, 16, 26, 18, 12, 13, 14, 7, 10, 34]
HEAD_ROW = 10


def zh_role(raw):
    if not raw:
        return ''
    return '+'.join(ROLE.get(p.strip(), p.strip()) for p in raw.split(',') if p.strip())


def zh(mapping, raw, default=''):
    return mapping.get(raw, raw if raw else default)


def load(path):
    root = ET.parse(path).getroot()
    return {tbl.get('table_name'): [r.attrib for r in tbl.findall('./rows/row')] for tbl in root.iter('table')}


def v(row, key, default=''):
    val = row.get(key)
    return default if val in (None, '') else val


def clean(text):
    if not text:
        return ''
    return re.sub(r'\s+', ' ', text.strip().strip('|')).strip()


def sheet_name(idx, name):
    s = re.sub(r'[\[\]:*?/\\]', ' ', name or '子系统')
    s = re.sub(r'\s+', ' ', s).strip()[:20].strip()
    return ('SB%02d-%s' % (idx, s))[:31]


def style_header_row(ws, row, ncols, widths=None):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill = HEAD_FILL
        cell.font = HEAD_FONT
        cell.alignment = Alignment(vertical='center', horizontal='center', wrap_text=True)
    if widths:
        for i, w in enumerate(widths, start=1):
            if i <= ncols:
                ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[row].height = 26


def add_dv(ws, values, cell_range):
    dvv = DataValidation(type='list', formula1='"%s"' % ','.join(values), allow_blank=True, showDropDown=False)
    ws.add_data_validation(dvv)
    dvv.add(cell_range)


def fill_subsystem_sheet(ws, data):
    """Upper block = subsystem attributes (key/value); lower block = element list."""
    ws.column_dimensions['A'].width = 18
    ws.column_dimensions['B'].width = 46
    ws.cell(row=1, column=1, value='子系统属性（可留空，我会补全）').font = TITLE_FONT
    for i, (k, val) in enumerate([
        ('子系统名称', data.get('name', '')),
        ('所属安全功能', data.get('sf', 'SF1')),
        ('功能角色', data.get('role', '')),
        ('类别（Cat.）', data.get('cat', '')),
        ('CCF', data.get('ccf', '')),
        ('技术文档', data.get('doc', '')),
        ('备注', data.get('note', '')),
    ], start=2):
        key = ws.cell(row=i, column=1, value=k)
        key.fill = KEY_FILL
        key.font = HEAD_FONT
        ws.cell(row=i, column=2, value=val)
    ws.cell(row=9, column=1, value='元件清单（必填：位号 + 型号）').font = TITLE_FONT
    for c, name in enumerate(ELEMENT_HEAD, start=1):
        ws.cell(row=HEAD_ROW, column=c, value=name)
    style_header_row(ws, HEAD_ROW, len(ELEMENT_HEAD), ELEMENT_WIDTHS)
    r = HEAD_ROW + 1
    for el in data.get('elements', []):
        for c, key in enumerate(['channel', 'seq', 'equip', 'model', 'brand', 'b10d',
                                 'nop', 'mttfd', 'dc', 'tech', 'note'], start=1):
            ws.cell(row=r, column=c, value=el.get(key, ''))
        r += 1
    last = max(r + 10, HEAD_ROW + 16)
    add_dv(ws, list(ROLE.values()) + ['输入+逻辑', '逻辑+输出', '输入+输出', '输入+逻辑+输出'], 'B3')
    add_dv(ws, list(CAT.values()), 'B5')
    add_dv(ws, list(CCF.values()), 'B6')
    add_dv(ws, ['通道1', '通道2', '测试通道'], 'A%d:A%d' % (HEAD_ROW + 1, last))
    add_dv(ws, list(TECH.values()), 'J%d:J%d' % (HEAD_ROW + 1, last))
    ws.freeze_panes = 'A%d' % (HEAD_ROW + 1)


def main():
    t = load(SSM)
    pr = t['projectops'][0]
    sfs, sbs, chs, bls = t['sfops'], t['componentops'], t['channelops'], t['blocops']

    def sb_list(sf):
        return [s for s in sbs if s.get('sfopoid') == sf.get('oid')]

    def ch_list(sb):
        return [c for c in chs if c.get('componentopoid') == sb.get('oid')]

    def bl_list(ch):
        return [b for b in bls if b.get('parentopoid') == ch.get('oid')]

    wb = Workbook()

    # ================= 说明 =================
    ws = wb.active
    ws.title = '说明'
    ws.column_dimensions['A'].width = 26
    ws.column_dimensions['B'].width = 106
    for i, (a, b) in enumerate([
        ('SISTEMA 建模资料模板', ''),
        ('怎么用', '每个子系统一张表（SB01、SB02…），在表里填这个回路的元件就行；其余内容我会补全。'),
        ('最少要填', '① 2-安全功能SF：安全功能名称 + PLr要求  ② 每张子系统表：元件清单的「位号 + 型号」。'),
        ('可留空', '品牌、B10d、nop、MTTFd、DC、技术类型、功能角色、类别、CCF、技术文档 —— 我按型号从元件库/手册补。'),
        ('下拉说明', '所有下拉均为中文；中文写法对应的 SISTEMA 内部代号见「枚举参考」。'),
        ('', ''),
        ('【表 ↔ SISTEMA 层级】', ''),
        ('1-项目信息', '对应 PR（项目）—— 一台设备一个项目，生成一个 .ssm 文件。'),
        ('2-安全功能SF', '对应 SF（安全功能）—— 每条安全功能一行。'),
        ('SBxx-…', '对应 SB（子系统）—— 一张表 = 一个子系统；上半部是子系统属性，下半部是元件清单（= 通道 CH 与元件 BL）。'),
        ('SB空白模板', '新建子系统时复制这张表：右键表标签 → 移动或复制 → 勾选「建立副本」。'),
        ('元器件型号参考', '常见型号参数速查（来自蓝本项目），填参数时可复制。'),
        ('枚举参考', '中文写法 ↔ SISTEMA 内部代号，不用改。'),
        ('', ''),
        ('【子系统表怎么填】', ''),
        ('单器件子系统', '整个回路就是一个器件时（安全门开关、安全逻辑单元），元件清单写一行、通道列留空。'),
        ('功能链子系统', '多个元件串联时（急停→继电器→接触器），按通道分别列：通道1、通道2 各写一遍（结构对称、位号不同）。'),
        ('测试通道', '没有测试元件就不写；需要时通道列选「测试通道」。'),
        ('双通道', '两个通道元件顺序要一致；位号不同（通道1=KA21，通道2=KA22）。'),
        ('位号范围', '如 Safety Door 1..10 就写「1..10」，我展开成 10 个实例。'),
        ('序号', '可留空，我按自上而下顺序处理。'),
        ('', ''),
        ('【我拿到表之后】', ''),
        ('生成', '按各表层级生成 .ssm，再用 SISTEMA 打开并截图给你核对。'),
        ('校验', '位号与型号是否齐全、双通道是否对称、类别/CCF 与元件 DC 是否自洽、SF 的 PL 是否满足 PLr。'),
    ], start=1):
        ca = ws.cell(row=i, column=1, value=a)
        ca.font = TITLE_FONT if (a.endswith('】') or i == 1) else HEAD_FONT
        ws.cell(row=i, column=2, value=b).alignment = Alignment(wrap_text=True, vertical='top')

    # ================= 1-项目信息 =================
    ws = wb.create_sheet('1-项目信息')
    ws.append(['字段', '值（示例 = 蓝本项目）', '说明'])
    for r in [
        ('项目名称', clean(v(pr, 'name')), '必填：SISTEMA 里的项目名称'),
        ('机器/设备名称', v(pr, 'machinename'), '可留空'),
        ('负责人/作者', v(pr, 'author'), '可留空'),
        ('执行标准', v(pr, 'normversion'), '一般不用改'),
        ('整体图纸引用', v(pr, 'document'), '图纸文件名，可留空'),
        ('文档文件夹', v(pr, 'documentsfolder', 'Documents'), ''),
        ('标准文件夹', v(pr, 'standardsfolder', 'Standards'), ''),
        ('备注', '', ''),
    ]:
        ws.append(list(r))
    style_header_row(ws, 1, 3, [18, 52, 34])
    ws.freeze_panes = 'A2'

    # ================= 2-安全功能SF =================
    ws = wb.create_sheet('2-安全功能SF')
    ws.append(['SF编号', '安全功能名称', 'PLr要求', '备注'])
    for i, sf in enumerate(sfs, start=1):
        ws.append(['SF%d' % i, clean(v(sf, 'name')), zh(PLR, v(sf, 'plr')), ''])
    style_header_row(ws, 1, 4, [10, 52, 12, 40])
    ws.freeze_panes = 'A2'
    add_dv(ws, list(PLR.values()), 'C2:C60')

    # ================= SB空白模板 =================
    fill_subsystem_sheet(wb.create_sheet('SB空白模板'),
                         {'name': '', 'sf': 'SF1', 'role': '', 'cat': '', 'ccf': '', 'doc': '', 'note': '',
                          'elements': []})

    # ================= 每个子系统一张表 =================
    idx = 0
    for i, sf in enumerate(sfs, start=1):
        for sb in sb_list(sf):
            idx += 1
            elements = []
            for ch in ch_list(sb):
                seq_in_ch = 0
                for b in bl_list(ch):
                    equip = clean(v(b, 'equipmentid'))
                    if not equip:
                        continue
                    seq_in_ch += 1
                    is_elec = v(b, 'technology') == 'tecElectronic'
                    elements.append({
                        'channel': zh(CHAN, v(ch, 'channeltype')), 'seq': seq_in_ch,
                        'equip': equip, 'model': clean(v(b, 'deviceid')) or clean(v(b, 'name')),
                        'brand': clean(v(b, 'manufacturer')),
                        'b10d': '' if is_elec else (v(b, 'b10d') or ''),
                        'nop': '' if is_elec else (v(b, 'nop') or ''),
                        'mttfd': v(b, 'mttfd') if is_elec else '',
                        'dc': v(b, 'dc') or '', 'tech': zh(TECH, v(b, 'technology')),
                        'note': clean(v(b, 'usecase')),
                    })
            if not elements:  # device-level subsystem: parameters sit on the SB itself
                elements = [{
                    'channel': '', 'seq': '', 'equip': clean(v(sb, 'equipmentid')),
                    'model': clean(v(sb, 'deviceid') or v(sb, 'devicegroup')),
                    'brand': clean(v(sb, 'manufacturer')), 'b10d': '', 'nop': '',
                    'mttfd': v(sb, 'mttfd') or '', 'dc': v(sb, 'dcavg') or '',
                    'tech': '', 'note': '单器件：参数挂在本子系统上',
                }]
            fill_subsystem_sheet(wb.create_sheet(sheet_name(idx, clean(v(sb, 'name')))), {
                'name': clean(v(sb, 'name')), 'sf': 'SF%d' % i, 'role': zh_role(v(sb, 'functiontypes')),
                'cat': zh(CAT, v(sb, 'cat')), 'ccf': zh(CCF, v(sb, 'ccfscore')),
                'doc': v(sb, 'catstandardfile'), 'note': '', 'elements': elements,
            })

    # ================= 元器件型号参考 =================
    ws = wb.create_sheet('元器件型号参考')
    ws.append(['型号', '品牌', '器件组', 'B10d', 'nop（每年动作次数）', 'MTTFd（电子件）',
               'DC', '技术类型', '元件类别', '用到的位号', '引用文档'])
    groups = {}
    for b in bls:
        equip = clean(v(b, 'equipmentid'))
        model = clean(v(b, 'deviceid'))
        if not equip or not model:
            continue
        g = groups.setdefault(model, {'brand': clean(v(b, 'manufacturer')), 'group': clean(v(b, 'devicegroup')),
                                      'b10d': v(b, 'b10d'), 'nop': v(b, 'nop'), 'mttfd': v(b, 'mttfd'),
                                      'dc': v(b, 'dc'), 'tech': zh(TECH, v(b, 'technology')),
                                      'cat': zh(CAT_BLK, v(b, 'cat')), 'equips': [], 'doc': v(b, 'document')})
        if equip not in g['equips']:
            g['equips'].append(equip)
    for model, g in groups.items():
        is_elec = g['tech'] == '电子'
        ws.append([model, g['brand'], g['group'],
                   '' if is_elec else g['b10d'], '' if is_elec else g['nop'],
                   g['mttfd'], g['dc'], g['tech'], g['cat'], '、'.join(g['equips']), g['doc']])
    style_header_row(ws, 1, 11, [26, 18, 22, 12, 13, 14, 7, 10, 10, 22, 40])
    ws.freeze_panes = 'A2'

    # ================= 枚举参考 =================
    ws = wb.create_sheet('枚举参考')
    ws.append(['字段（所在表）', '中文写法（下拉可选）', '对应 SISTEMA 内部代号 / 含义'])
    for r in [
        ('PLr要求（2-安全功能SF）', 'PL a / PL b / PL c / PL d / PL e', 'plA…plE —— 要求的性能等级'),
        ('功能角色（子系统表）', '输入 / 逻辑 / 输出，组合写「输出+逻辑」', 'fncInput / fncLogic / fncOutput'),
        ('类别（子系统表）', 'Cat. B / Cat. 1 / Cat. 2 / Cat. 3 / Cat. 4', 'catB / cat1 / cat2 / cat3 / cat4'),
        ('CCF（子系统表）', '未评估（0） / 部分满足（60） / 满足措施（65） / 较高（90） / 很高（99）', 'ccfscore 数值 0～100'),
        ('通道（元件清单）', '通道1 / 通道2 / 测试通道（留空 = 单器件）', 'ch1 / ch2 / chTest'),
        ('技术类型（元件清单）', '机电 / 电子', 'tecElectromechanic / tecElectronic —— 机电件给 B10d+nop，电子件给 MTTFd'),
        ('元件类别（型号参考）', '未指定 / Cat. B / Cat. 1～Cat. 4', 'catN / catB / cat1…cat4'),
        ('DC', '直接填数字：0.65 / 0.8 / 0.9 / 0.99', '诊断覆盖率：低 / 中 / 高 / 很高'),
        ('B10d、nop', '填数字：B10d 如 20000000，nop 如 2000', '机电件原始参数，SISTEMA 据此推算 MTTFd'),
    ]:
        ws.append(list(r))
    style_header_row(ws, 1, 3, [30, 54, 60])
    ws.freeze_panes = 'A2'

    wb.save(OUT)
    print('saved:', OUT, '| sheets:', len(wb.sheetnames), '| subsystems:', idx)


if __name__ == '__main__':
    main()
