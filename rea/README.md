# REA 接入（morluto/rea）与它在 SISTEMA 自动化里的位置

[REA](https://github.com/morluto/rea) 是本地逆向工程 MCP（MIT，npm 包 `rea-agents`，本机 6.7.0）。
本仓库用它做两件事，**都不是"让 AI 看截图"**：

1. **把 SISTEMA 的界面结构静态导出**（`tools/sistema/rea_ui_map.py`）
   `rea inspect-pe-resources SISTEMA.exe` 返回完整 PE 资源清单（1152 项，含偏移与 SHA-256）。
   SISTEMA 是 Delphi 程序，每个窗体的定义（TPF0/DFM）就躺在 `RT_RCDATA` 里 ——
   共 **93 个窗体**可解析（另 3 项是 madExcept / TMS 编辑器窗体的私有流，跳过）。
   DFM 里每个控件都有 **DFM 名称 + 父容器 + Left/Top + `LabelCaption`**，
   这正是"哪个输入框是 B10D"的权威答案，取代了按坐标猜。
2. **诊断运行期能力**：`rea doctor`、`rea list-frida-processes` 等命令用来确认某个深度分析通道
   在本机是否可用，而不是靠猜。

> REA **不参与**搬运键鼠：键鼠由 `tools/sistema/driver/` 直接走 Win32 消息与 `SendInput`。
> REA 提供的是"软件长什么样"的地图，"软件做了什么"的回答仍然来自 SISTEMA 自己。

## 安装（本机已执行）

```powershell
.\rea\install-rea.ps1            # 幂等；已装则跳过
```

脚本做的事：

| 步骤 | 说明 |
|---|---|
| Node 24.22.1 | REA 要求 `^22.23.4 || ^24.22.1 || >=26.12.1`；本机原有 24.21.0 **不满足**，装到 `%LOCALAPPDATA%\Programs\node24` |
| `npm install -g rea-agents` | 用上面这个 node 的 npm；npm cache 换成 `node24\npm-cache`（默认 cache 目录曾报 `EPERM`） |
| `rea setup --client dsh` | 注册 MCP（写 `~/.dsh/cordis.patch.yml`，工具名 `mcp__rea__*`），并装 skill 到 `~/.agents/skills/reverse-engineer-anything` |
| `rea doctor --client dsh` | 验证 |

**本机 `rea setup` 会失败并报 `clients.dsh.status: failed / reason: write`**：
REA 的事务式写入依赖它的 Windows 原生控件，而本机那条路径报
`Create private object relative to its admitted parent failed (Win32 5): 拒绝访问`
（`rea doctor` 的 jadx 自检也是同一句）。所以脚本在检测到该症状时**改为手工落地**：
按官方文档的条目写 `~/.dsh/cordis.patch.yml`，并把 bundled skill 复制到 `~/.agents/skills/`。
条目内容（绝对路径按本机实际值）：

```yaml
- insert:
    - id: rea-mcp
      name: "@deepseek-ai/dsh-mcp-client"
      config:
        serverName: rea
        transport: stdio
        command: C:\Users\admin\AppData\Local\Programs\node24\node.exe
        args: ["C:\\Users\\admin\\AppData\\Local\\Programs\\node24\\node_modules\\rea-agents\\scripts\\rea.mjs", "mcp"]
```

改完 **必须重启 DSH** 才会出现 `mcp__rea__*` 工具（新增 patch 条目不能热加载）。

## 已知不可用：Frida 通道

`rea instrument-with-frida` / `list-frida-processes` 需要可选依赖 `frida`。
本机两次安装都以 `prebuild-install warn install aborted` + `Visual Studio is not installed` 结束
（Node 24.22.1 的 ABI 没有预编译产物，回落到源码编译又缺 VS）。
**因此本仓库的所有自动化都不依赖 Frida**；
`driver/` 用的是纯 Win32 消息 + `SendInput`，反馈来自控件回读、`.ssm` 与导出的 PDF。

## 不需要 Ghidra / Hopper / IDA

`inspect-pe-resources`、`inspect-artifact` 都是 REA 内置的安全静态分析，无需反编译器。
本机未装任何 native provider，`rea doctor` 的 provider 段是红的，不影响上面这些用法。

## 对 `SISTEMA.exe` 的实际产出（可复现）

```powershell
$py = "$env:USERPROFILE\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
& $py .\tools\sistema\rea_ui_map.py          # -> sistema_ui_map.json / .md
& $py .\tools\sistema\ui_fields.py TFormComponent   # 看某个窗体的可寻址字段
```

`SISTEMA.exe` SHA-256：`809c99903d39814ed6ebecca4257e69067acdc948f0d1e66a1894c7436599f9c`（3.0.4 Build 5）。
窗体清单落在 `sistema_ui_map.md`，包含每个字段的 DFM 名称与德文原始标签
（例：`LEExName` = `Name des Subsystems:`、`LEExPFHDirect` = `PFH [1/h]:`、`CBCat` = 类别下拉）。
