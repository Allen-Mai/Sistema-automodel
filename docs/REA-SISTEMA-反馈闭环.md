# SISTEMA 无截图自动化：REA 提供地图，软件自己提供反馈

> 目标：把"操作 SISTEMA"从**截图 + 肉眼看 + 按坐标点**改成**按名字操作 + 读软件自己的输出**。
> 本文说明为什么能这么做、怎么用、边界在哪。

## 1. 三条反馈通道（都不看像素）

| 通道 | 读什么 | 谁产生的 | 延迟 | 用途 |
|---|---|---|---|---|
| **A 控件回读** | `WM_GETTEXT` / `BM_GETCHECK` / `CB_GETTEXT` | 控件自己 | 即时 | 每次写入后的当场确认；枚举某窗体所有字段当前值 |
| **B `.ssm` 复解析** | 保存后的 XML（`*cal` 字段就是 SISTEMA 的计算结果） | SISTEMA 计算并回写 | `Ctrl+S` 后 | 结构、参数、PL/PFHd/MTTFd/DCavg/CCF 的权威值 |
| **C 报告 PDF** | `Ctrl+E` 导出的 PDF | SISTEMA 渲染 | 数秒 | 人看的最终产物；`extract_pdf.py` + `audit_report.py` 已有 |

> 关键的坑：`WM_SETTEXT` 只改了控件里的文字，SISTEMA 在 `OnExit` 才把它写进对象模型。
> 所以 `set_text()` 写完后会 `set_focus` + `TAB` 把焦点移走。
> 没有这一步，面板上显示 `SB1 e-stop input`，存盘后的 `.ssm` 里 `name=""` —— 实测踩到过。

Context 面板（PL / PFH / Cat. / MTTFd / DCavg / CCF 那一栏）在 DFM 里是**空窗体**：
4 个 `TValueListEditor` 全是运行期动态创建的，没有静态结构可依。所以它不单独读 ——
它的数据就是通道 B 的 `plsubitemscal` / `plcal` / `pfhcal` / `dcavg` / `ccfscore`。

## 2. 靠名字定位控件（REA 的产出）

`tools/sistema/rea_ui_map.py` 从 `RT_RCDATA` 里把 93 个 Delphi DFM 解析出来，得到：
DFM 名称、父容器、`Left/Top`、`LabelCaption`、下拉选项。

运行期只有 `hwnd + 类名 + 矩形`，`driver/uimap.py` 负责把两者对齐：

1. **按行匹配**：`Top` 决定归属（容差 5 px），`Left` 只做同分裁决（`TLabeledEditEx`
   会把标签画在自己左边，运行期 x 会偏 20~30 px）；
2. **容器按内容匹配**：`TAdvTabSheet` 全在 (0,0) 且 Z 序随激活页轮转，改用
   "子树类名多重集"的 Jaccard 相似度配对；
3. **序数兜底**：仍分不开时按创建序配对（`EnumChildWindows` 是 Z 序，等于**倒序**创建序）。

于是可以写 `panel.set_text("LEExName", ...)`、`session.select_combo("CBCat", "3")`，
不需要任何坐标。

## 3. 分页控件：`Ctrl+Tab` + 有界探测

SISTEMA 的页签是**懒创建**的：某页没被显示过，页里的控件就还没有 HWND。
`session.ensure_field(name)` 的做法是：

```
while not panel.has(name) and 次数 < 10:
    焦点给 TAdvPageControl -> Ctrl+Tab -> 重新绑定
```

判据是"目标控件是否已实体化"，不是"看起来像哪一页" —— 闭环、可重试、失败会报出
`(saw tabs: [...])` 便于定位。实测 `TFormComponent` 的 6 个页签
（PL / Documentation / MTTFd / DCavg / Category / CCF）都能这样走到。

## 4. 结构操作：只用 Ctrl+Insert，顺着"自动选中"往下走

`Ctrl+N` 建项目 → 项目节点自动选中；`Ctrl+Ins` 建子对象 → 新对象自动选中。
所以**不需要在树里导航**（那才是唯一必须坐标/截图的地方）。
每步的验证是"当前面板类 + 它的 `LEExName`"：面板从 `TFormProject` 变成 `TFormSF` 就是
"SF 建出来了"，再从 `TFormSF` 变成 `TFormComponent` 就是"子系统建出来了"。

## 5. 实测通过的完整链路

`tools/sistema/e2e_ui.py`（本机实际输出）：

```
attached 15316
panel: TFORMCOMPONENT tabs: ['PL', 'Documentation', 'DCavg', 'MTTFD', 'Category', 'CCF']
rename SB -> 'SB1 e-stop input'
categories: ['-', 'B', '1', '2', '3', '4']
CBCat read-back: '3|Requirements of B ...'
save as -> ...\_setup\e2e\DSH_AUTO.ssm
file exists: True size: 36237
  componentops: {'name': 'SB1 e-stop input', 'cat': 'cat3', 'mttfd': '10', 'dcavg': '0',
                 'ccfscore': '0', 'plsubitemscal': 'plN'}
  channelops:  3 rows (ch1/ch2/chTest)
  blocops:     3 rows
```

即：**纯 GUI 操作建出的项目，其结构与参数都在 SISTEMA 自己的存盘结果里对上了**。

## 6. 能力边界（诚实清单）

| 能做 | 不能做（还没有） |
|---|---|
| 新建/保存/另存/导出 PDF、开项目 | 树节点的**任意**跳转（只能顺着自动选中走） |
| 新建 SF / SB / CH / BL（`Ctrl+Ins` 按层级） | 从 `Context` 面板直接读结果（改读 `.ssm`） |
| 改任意已实体化字段（按 DFM 名） | `Messages` 面板逐条读（改读导出的 PDF） |
| 下拉选项按值选择（`CBCat` 等） | 拖拽、库文件导入的坐标交互 |
| 复选框 / 单选按钮 / 按钮 | 任意自定义绘制的列表控件 |

`Messages` 面板本身有 `aSaveMessages`（"Speichern unter…"）动作，但只有右键菜单入口、
没有快捷键，且菜单是自绘窗口，所以本轮没有走这条；PDF 通道已经覆盖同样的信息。

## 7. 命令一览

```powershell
$py = "$env:USERPROFILE\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"

& $py .\tools\sistema\rea_ui_map.py                  # 生成/刷新静态 UI 地图（走 REA）
& $py .\tools\sistema\ui_fields.py TFormComponent     # 列出某窗体的字段与标签
& $py .\tools\sistema\driver\cli.py attach            # 附着到运行中的 SISTEMA
& $py .\tools\sistema\driver\cli.py current           # 当前选中对象 + 全部字段值
& $py .\tools\sistema\driver\cli.py tabs              # 当前面板的页签
& $py .\tools\sistema\driver\cli.py fields            # 同 current
& $py .\tools\sistema\driver\cli.py set LEExName "SB1"  # 按 DFM 名写字段并回读
& $py .\tools\sistema\driver\cli.py new-project "移印机"
& $py .\tools\sistema\driver\cli.py new-child         # Ctrl+Ins
& $py .\tools\sistema\driver\cli.py save-as D:\x\y.ssm
& $py .\tools\sistema\driver\cli.py export-pdf D:\x\y.pdf
& $py .\tools\sistema\e2e_ui.py                       # 端到端自检
```
