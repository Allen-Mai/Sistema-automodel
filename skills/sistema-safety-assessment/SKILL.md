---
name: sistema-safety-assessment
description: 在本机使用 SISTEMA 3.0.4 查看、核对或新建 ISO 13849-1 机器安全回路评估项目（PL / PFH / Cat. / MTTFd / DCavg / CCF），包括软件窗口结构、五层项目层级、只读检查流程与截图定位的操作要点。
whenToUse: 当任务涉及本机 SISTEMA 软件、`.ssm` 项目文件、安全回路 / 安全功能 / 急停 / 安全门的 PL 评估，或需要读取、核对、复现已有安全评估项目内容时。
---

# SISTEMA 安全回路评估（本机操作指南）

## 1. 环境事实（先确认，别猜）

| 项 | 值 |
|---|---|
| 程序 | `C:\Program Files (x86)\SISTEMA 3.0.4\SISTEMA.exe` |
| 主窗口 | 类名 `TFormMain`，标题 `SISTEMA - Safety Integrity Software Tool for the Evaluation of Machine Applications v3.0.4 Build 5` |
| 项目文件 | `.ssm`；自动备份 `.ssm_backup`；打开时生成 `.<项目名>~ssm` 锁文件 |
| 最近文件 | 注册表 `HKCU\Software\IFA\SISTEMA\3.0.4\RecentFiles`（`1` = 最近打开，可据此定位当前项目路径） |
| 元件库 | `<用户>\Documents\SISTEMA\Libraries\SISTEMA_Lib300_EN.slb`（窗口底部状态栏显示当前库） |
| 导出报告 | `File → Export as PDF…`（快捷键 Strg+E） |

判断"当前打开的是哪一个项目"：优先看 `RecentFiles` 的 `1`，并用项目目录里是否存在 `.~ssm` 锁文件交叉验证（同名副本常见）。

用户的项目工作区约定：`C:\Users\<user>\Desktop\SISTEMA V2 测试建模\`，下按 `00-`…`07-` 编号分项目（如 `06-玻璃盘筛选机`、`07-测试`），每个项目目录内含 `.ssm` / `.ssm_backup` / 导出的 `.pdf` / `Documents\` / `Standards\`。

## 2. 五层项目层级（回答"层级关系"必须用这个）

```
PR 项目        Project          一个 .ssm 文件 = 一台设备
└ SF 安全功能   Safety Function  PLr(要求) vs PL(实际)、PFH
  └ SB 子系统   Subsystem       一条串联链：PL、PFH、Cat.、MTTFd、DCavg、CCF
    └ CH 通道   Channel         Cat 3/4 的双通道，Channel 1 / 2 分开算
      └ BL 块   Block           通道内元件：MTTFd、DC、Use case
        └ EL 元素 Element       块内部元素（Context 面板出现 "EL" 分组）
```

关键规则：

- 一个 **SF** 下的多个 **SB 是串联的**：整条安全回路被拆成"输入 → 逻辑 → 输出"式的子系统链（如 门开关 → G9SX 逻辑 → STO → 气源切断 → 电机切断）。
- **CH 属于 SB**（双通道结构的两个通道），**BL 属于 CH**。树里看起来像同级，展开即可确认（展开 CH 才看到 BL）；不要只凭缩进下结论。
- 汇总方向是自下而上：BL → CH → SB → SF → PR。

各层判据：

| 层级 | 关注量 |
|---|---|
| SF | PLr（来自风险评估的要求值）、PL（实际达到）、PFH [1/h]；必须 **PL ≥ PLr** |
| SB | PL、PFH、Cat.、MTTFd [a]、DCavg [%]、CCF |
| CH | 通道 MTTFd 及其等级（High/Medium/Low） |
| BL | MTTFd、DC [%]、Use case、订货号 |

## 3. 界面与操作

**五个面板，联动逻辑是操作主线**：

| 面板 | 位置 | 作用 |
|---|---|---|
| Projects | 左上 | 项目树（PR/SF/SB/CH/BL/EL），**选中谁，下面两块就显示谁** |
| Blocks | 中上 | 可选块来源：`Library`、`VDMA Library`、`New`、`Edit`、`Delete` |
| 明细表 | 右上 | 当前节点内容（选 CH 就列出通道内 BL 及其 MTTFd / DC / Use case） |
| Context | 左下 | 当前节点及上层的评估结果（PL、PFH、Cat.、MTTFd、DCavg、CCF） |
| Messages | 右下 | 校验与警告（PL 不达标、参数被规则调整等都在这里） |

**菜单**：File（New / Open… / Save / Save As… / Close Project / Close All / Export as PDF… / Print… / 最近文件 / Exit）、Edit、View、Help（含 What's This?）。
**工具栏**：New、Open…、Save、Close Project、Library、VDMA Library、**Report**、Help、What's This?。
注意：菜单里的 `Strg+X` 是**德语 Ctrl** 标注（英文界面 + 德文快捷键标签）。

**树的操作**：点节点前的 `+/−`，或选中节点后按 `→` / `←` 展开收拢。实测 `→` 可靠；`+` 的点击热区很小，容易点空。

## 4. 用自动化操作它（重要，容易白费功夫）

- **无 UI Automation**：SISTEMA 是 Delphi VCL 程序，Windows-MCP 的 `Snapshot` 只能看到标题栏（菜单栏/最小化/关闭），**看不到树和表格**。因此必须"截图 → 看图 → 按像素坐标点击"。
- **坐标要分清物理/逻辑**：本机显示器 2560×1600 @150%（effective DPI 144）。全屏截图用 `CopyFromScreen(0,0,0,0, 2560x1600)` 得到物理像素；`System.Windows.Forms.SystemInformation.VirtualScreen` 返回的是逻辑值（1707×1067），**不可用于截图/点击换算**。把窗口 `GetWindowRect` 结果当作物理坐标，并与截图同源使用。
- **切前台**：PowerShell 的 `SetForegroundWindow` 常被 Windows 前台锁静默拒绝（表现为点击落到了别的窗口上）。改用 Windows-MCP 的 `App(mode="switch", name="...")`；若按进程名匹配失败，先用 EnumWindows 拿到真实窗口标题（`TFormMain` 的完整标题）。
- **验证动作是否真的生效**：点击后重新截图并比对 `sha256`；像素完全没变说明没点中（点偏 10~20 px 就会发生）。
- 只读探索时不要点 `Delete`、不要 `Save`；展开/折叠节点、打开菜单后按 `Esc` 关闭都是安全的。

## 5. 典型评估流程

1. **读输入**：项目目录里的电气图纸 PDF、安全回路描述 docx/xlsx，确认有哪几条安全功能（安全门、急停、STO 等）。
2. **建结构**：`PR` 下建 `SF`（每条安全功能一个）；SF 下按回路串联关系建 `SB`；需要双通道时在 SB 下建 `CH 1/2`。
3. **放元件**：展开 `CH`，从 `Blocks → Library / VDMA Library` 取元件（安全继电器、门开关、接触器…）作为 `BL`，填 MTTFd、DC。
4. **设参数**：给 SB 设 Category、CCF（双通道需满足 CCF 要求）、通道 MTTFd 与 DC。
5. **读结果**：选中 `SF` 看 Context 的 PLr / PL / PFH，确认 **PL ≥ PLr**；选中 `SB` 看 Cat. / MTTFd / DCavg / CCF。
6. **看 Messages**：所有校验提示都在这里，例如通道 MTTFd 被 SISTEMA 的 100 a 上限规则处理。
7. **出报告**：`Report` 或 `File → Export as PDF…`，把 PDF 放在项目目录里归档。

## 6. 校验要点与坑

- **PLr 是要求值、PL 是算出来的实际值**，两者不能混；比较时看同一个 SF 的 Context 面板。
- **MTTFd / DCavg 与 Category 有对应关系**，SISTEMA 会用 Messages 提示不满足的情况（如 DCavg 低于 Cat. 要求、CCF 未满足）。
- **通道 MTTFd 有 100 a 上限**：超过（或触及规则）时会看到 "The channels MTTFd has been cut … For a channel 100 a is the maximum acceptable mean time to a dangerous failure."
- **同名项目副本**很常见（如 `06-`/`07-` 下同名 `.ssm`），改动前先用锁文件 + RecentFiles 确认改的是哪一份，避免改错副本。
- 涉及修改用户项目时：先说明将改什么、征得同意，并在动手前确认项目文件所在路径。

## 7. 项目文件是 XML（可直接解析，不必点界面）

`.ssm` 是 tiOPF 导出的 XML：`<xmldocdata><tables><table table_name=".."><fields/><rows><row 字段="值" .../></rows></table>`。
**所有字段都是 `<row>` 的 XML 属性**（不是子元素），可直接读取：

| 表 | 层级 | 关键字段 |
|---|---|---|
| projectops | PR | name, machinename, author, normversion, document, standardsfolder, documentsfolder |
| sfops | SF | projectopoid, name, plr(plA..plE), plrdet, riskparamf/p/s, plcal, pfhcal |
| componentops | SB | sfopoid, name, functiontypes(fncInput/fncLogic/fncOutput), cat(cat2..cat4), ccfscore, mttfd, dcavg, pfh, equipmentid, manufacturer, deviceid, devicegroup, partno, catstandardfile |
| channelops | CH | componentopoid, channeltype(ch1/ch2/chTest) — **每个 SB 固定三个通道** |
| blocops | BL | parentopoid(→CH), name, equipmentid(位号), manufacturer, deviceid(型号), partno, devicegroup, b10d, nop, mttfd, dc, technology(tecElectromechanic/tecElectronic), cat |
| elementops | EL | parentopoid(→BL)，常见为空占位，可忽略 |

引用链：`projectopoid / sfopoid / componentopoid / parentopoid`。注意 CH1 与 CH2 通常镜像、位号不同；一个 SB 可被多个 SF 复用。
工具：`sistema-tools\ssm_hierarchy.py`（重建整树）、`ssm_inspect.py`（列表/导出）、`ssm_probe.py`（结构调试）。

## 8. 新项目资料收集（Excel 模板）

模板：`桌面\SISTEMA建模资料模板.xlsx`（由 `sistema-tools\build_template.py` 从蓝本 .ssm 生成，含 6 张表）：
说明 / 1-项目信息(PR) / 2-安全功能SF / 3-子系统SB / 4-通道元件CH-BL / 5-元器件BOM / 6-枚举参考。

填写约定：**位号为主键**；双通道各写一遍；chTest 可留空；机电件填 B10d+nop、电子件填 MTTFd；结果类字段（PFH/PL/DCavg）不用填；范围位号写 `1..10`（数量列同步）。
两种建模方式：**单器件**（SB 行直接给 MTTFd/DC，如门开关、安全继电器本体）与 **功能链**（元件放 CH 里，参数由元件汇总到 SB）。

## 9. 在 SISTEMA 界面里建模（UI 操作要点）

用户要求"直接在软件里新建"时按这套走。SISTEMA 无 UI Automation，只能截图 + 坐标点击；Delphi 模态框对合成鼠标事件常不响应，优先用键盘。

| 动作 | 操作 |
|---|---|
| 新建项目 | `File→New`（Ctrl+N）→ 右侧 Project 面板填 Project name |
| 新建子节点 | 树里选中父节点 → **Ctrl+Insert**（= 右键 New，德语 Strg+Einfg） |
| 命名 | 右侧面板第一个输入框 → Ctrl+A → 粘贴（中文用剪贴板，SendKeys 直接送中文不可靠） |
| Function | 面板里 ☐ Input / ☐ Logic / ☐ Output 三个复选框，逐个点 |
| Category | Category 页：**点中单元格后用 ↓/↑ 切换**（End = Cat 4）；**设完类别 SISTEMA 自动生成 CH1/CH2 + 空块**，不用手动建通道 |
| Technology 下拉 | 点箭头不展开，要按 **Alt+↓**，列表里选 electromechanic / electronic / … |
| 元件参数 | 选中 BL → Block 面板填 Name + Device details；**MTTFd 页**选 `Determine MTTFD value from B10D/B10` 填 B10D+nop（或 `Enter MTTFD value directly`）；**DC 页**选 `Enter DC value directly` 填 DC% |
| 保存 | Ctrl+S；新项目弹 Save project 对话框（填完整路径，已存在会问 Overwrite）；保存后同目录出现 `.ssm_backup` 与 `.~ssm` |
| 元件库 | Blocks 页每通道的 `Library` 按钮 —— 本机 `SISTEMA_Lib300_EN.slb` 的 **BL 层是 0 项**，没有可插元件，直接跳过 |

**实测踩坑（都很费时间）**：

- 输入框行距约 **41 px**（按 52 估会整体错位，内容填进相邻字段）
- 点击前必须 `SetProcessDPIAware()`，否则 150% 缩放下坐标被 DPI 虚拟化，点击落空且画面 sha256 不变
- 切前台用 PowerShell `SetForegroundWindow(主窗口 hwnd)`；Windows-MCP 的 `App(mode=switch)` 对 SISTEMA **匹配不到窗口**（要用 EnumWindows 拿 `TFormMain`）
- 模态框（Warning / Error / Confirm / Save）用 `{ENTER}`、`{ESC}`，或 `PostMessage(hwnd, WM_CLOSE, 0, 0)`；**合成鼠标点击经常无效**
- 树节点坐标随展开状态变化，别复用旧坐标；导航用 `{END}` 跳最后一个节点更稳
- 新建 SB 默认 Cat 未设；用 End→↑ 想设 Cat 3 时 ↑ 有时不生效，需重按一次并回读 Context 的 `Cat.` 确认
- 一个块要填 8~10 个字段；重复元件建议**在界面里复制块再改位号**，比逐个新建快得多

## 10. 相关工具

- 截图/点击：Windows-MCP（`mcp__windows__*`）或 PowerShell + `user32`（`SetCursorPos` / `mouse_event`）。
- 图片判读：`read_image`；需要看清细节时用 Python(PIL) 裁剪放大后再读，比全屏缩略图可靠。
- 坐标/窗口枚举：PowerShell + `EnumWindows`、`GetWindowRect`。

## 11. 用 Win32 消息驱动 SISTEMA（首选，比坐标点击可靠得多）

**核心结论：SISTEMA 不暴露 UI Automation，但它的 Delphi 控件本身是标准 Win32 窗口，可以直接发消息。**
实测在本机 SISTEMA 3.0.4 上验证通过。

| 控件类 | 对应界面 | 可行操作（实测） |
|---|---|---|
| `TLabeledEditEx` | 所有单行输入框（Name、Manufacturer、B10D、nop、DC…） | **`WM_SETTEXT` 写入 / `WM_GETTEXT` 读回** ✅ |
| `TIFABitBtn` | 按钮（New、Open、Calculate nop、Switch content of channels…） | `BM_CLICK`（0x00F5） |
| `TAdvOfficeCheckBox` / `TRadioButton` | Function 勾选、MTTFd/DC 方式单选 | `BM_CLICK` / `BM_SETCHECK` |
| `TIFAComboBox` | Category 等选择控件 | `WM_GETTEXT` **可读出当前值与全部选项文本**（实测返回 `'3\|Requirements of B…'`）✅ |
| `TtiVTTreeView` / `TtiVirtualStringTree` | 项目树（自绘） | `WM_GETTEXT` 无效 → 用键盘消息或坐标点击 |
| `TValueListEditor` / `TIFAMarkedStringGrid` | Context 结果表 / Messages 表（自绘） | `WM_GETTEXT` 无效 → 截图判读 |

**定位控件**：`EnumWindows`（顶层，用 `TFormMain`/`TFormComponent` 等类名区分面板）+ `EnumChildWindows` 拿 hwnd、类名、文本、矩形。
面板对应关系：`TFormComponent`=子系统/块属性面板、`TFormContext`=Context、`TFormSSMMessageListUI`=Messages。

**三个必踩的坑**：

1. **`EnumChildWindows` 本身已经递归遍历所有后代**，回调里不要再递归 —— 否则数量指数爆炸（实测跑出 340 万行 / 395 MB）。
2. **消息要发给控件本体，不要找它的子 `Edit`**：`TLabeledEditEx` 的子控件只有 `TWinControlProxy`，`FindWindowEx(..., 'Edit', ...)` 返回 0。Delphi 把自定义类名注册给了编辑框窗口自己，所以 `SendMessageW(editHwnd, WM_SETTEXT/ WM_GETTEXT, ...)` 直接可用。
3. **验证写入必须用 `SendMessage(WM_GETTEXT)`**（同步查询控件真实值）；`GetWindowText` 对跨进程窗口只返回缓存的标题，会得到假阳性。

**窗口位置**：若控件矩形出现极大负值（如 `(-31000,-31000)`），说明窗体被移到屏幕外，
先 `SetWindowPos(hwnd, 0, 0, 0, 1900, 1040, SWP_NOZORDER)` + `SetForegroundWindow` 拉回来，再枚举才有正常坐标。

脚本：`tools/sistema/enum_controls.ps1`（平铺枚举控件树，输出 hwnd/类名/文本/矩形）。
