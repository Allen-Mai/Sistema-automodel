---
name: windows-desktop-automation
description: 在这台 150% 缩放、无 UI Automation 的 Windows 机器上用截图 + 坐标点击操作第三方桌面软件（SISTEMA、E-Mobile、向日葵等自绘/传统 Win32 程序）的可靠做法与全部踩坑记录。
whenToUse: 当需要代替用户在桌面软件里点击、填表、开窗口、传文件，或点击/快捷键"没反应"需要排查时。
---

# Windows 桌面自动化（本机实操要点）

前提事实：显示器 2560×1600 @**150% 缩放**（effective DPI 144）；PowerShell 是主要工具；Windows-MCP（`mcp__windows__*`）可用但对其 UIA 支持差的程序无效。

## 1. 三条必须遵守的铁律

1. **点击前调用 `SetProcessDPIAware()`**（pwsh 新进程每次都要）。否则 150% 缩放下 `SetCursorPos` 的坐标被系统虚拟化，点击落到错误位置，**而且截图画面完全不变**（很容易误判成"控件不响应"）。
2. **点击前把目标窗口置前**。`SetForegroundWindow` 常被 Windows 前台锁静默拒绝 → 点击落到别的窗口上。稳妥做法：先 `EnumWindows` 找到目标 hwnd（按 `TFormMain` 等类名 + 进程 id），`SetWindowPos(hwnd, 0,0,0,W,H, SWP_NOZORDER)` 把它拉回屏幕内，再 `SetForegroundWindow`。这一步失败时，用 Windows-MCP 的 `App(mode="switch", name=...)` 兜底（但对 SISTEMA 匹配不到窗口，只能用 PowerShell）。
3. **每次关键操作后重新截图并比对 `sha256`**。像素完全一致 = 没生效；变了 = 生效。不要"假设点到了"。

## 2. 坐标系统（最容易算错的地方）

- 全屏截图用 `CopyFromScreen(0,0,0,0, 2560,1600)` 得到的是**物理像素**，与 `GetWindowRect` 同源，可以直接相加当点击坐标。
- **`System.Windows.Forms.SystemInformation.VirtualScreen` 返回逻辑值（1707×1067），不可用于截图或点击换算**。
- 窗口被移动过就别复用旧坐标；树/列表展开后行位置会整体下移。
- 电子表格类输入框的行距要**实测**（SISTEMA 的 Block 面板实测 41 px/行；按 52 估算会把内容填进相邻字段）。

## 3. 定位控件的技巧

- 目测坐标常常偏 10~20 px。**把小区域裁剪放大后再看**（PIL：`crop(...).resize((w*2,h*2))`），比全屏缩略图可靠得多。
- 键盘导航优先于鼠标：树/列表用 `{END}` 跳最后一项、`{DOWN}`/`{UP}` 移动，比算坐标稳。
- 下拉框：
  - 标准 Win32/可编辑下拉：**`Alt+↓`** 展开（点箭头有时只聚焦不展开）。
  - 列表型多行控件（SISTEMA 的 Category）：**点中单元格后用 `↓`/`↑` 切换**（`End` = 最后一项）。
- 文本输入统一走**剪贴板**：`Set-Clipboard` + `^a` + `^v`。`SendKeys` 直接送中文不可靠。

## 4. 对话框处理（关键教训）

- **Delphi 自绘模态框（`TAdvSmoothMessageDialogForm` 等）对合成鼠标点击经常完全不响应**：点了按钮、窗口还在，画面 sha256 不变。
- 可靠手段按优先级：
  1. `SetForegroundWindow(对话框 hwnd)` 后发 `{ENTER}`（默认按钮）/ `{ESC}`（取消）
  2. 标准对话框（`#32770`）用 `PostMessage(hwnd, WM_CLOSE, 0, 0)`
  3. 枚举子窗口找按钮（`EnumChildWindows` + 文本匹配）→ `PostMessage(btn, BM_CLICK, 0, 0)`
  4. 都不行时，模态框会在主窗口后续操作超时后自行消失，重新截图确认即可
- **模态框开着时，所有菜单/快捷键操作都会被吞掉**（表现为"Ctrl+L 没反应""文件打不开"）。先清对话框再操作。

## 5. 不同程序的差异

| 程序类型 | 例子 | UIA 支持 | 操作方式 |
|---|---|---|---|
| Flutter 自绘 | 向日葵 AweSun | 差（只有外壳） | 截图 + 坐标点击；控件热区小，先放大裁切定位 |
| Delphi VCL | SISTEMA | 差（Snapshot 只看得到标题栏） | 截图 + 坐标点击；输入框行距要实测 |
| Electron/CEF | E-Mobile(泛微 OA) | 部分 | 菜单可点，文件选择用剪贴板粘贴路径 |
| 标准 Win32 | 文件对话框 | 好 | 键盘为主（`Alt+↓`、`{ENTER}`、路径粘贴） |

## 6. 给"上传/下载文件"类操作的经验

- 文件选择对话框：把**完整路径**粘到文件名框再回车，比在目录树里导航快且稳。
- 对话框默认目录可能不是你要的（E-Mobile 默认在业务图纸目录），别假设。
- 覆盖已有文件会弹 "Overwrite?" 确认，要处理。

## 7. 验证与收尾

- 每个阶段结束**截图存证**（保存到 `%TEMP%`，不要塞满用户桌面），必要时裁剪放大给用户看。
- 代表用户**外发内容前必须确认收件人和内容**（例如把远程码发到 OA 给某个同事）——这类动作不可撤回。
- 生成的临时文件（截图、探针脚本、预览 txt）收尾时清理干净；删除前先打印路径和存在性再删。
