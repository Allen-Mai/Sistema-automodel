# A

从实机操作中沉淀的 **DSH（DeepSeek Harness）技能与工具集** —— 可直接复制到新设备的
`%USERPROFILE%\.dsh\skills\` 使用，也可用附带的脚本批量部署。

## 目录

| 路径 | 内容 | 用途 |
|---|---|---|
| `skills/sistema-safety-assessment/` | SISTEMA 安全评估（skill） | 读写 `.ssm` 项目：XML 数据结构、五层层级（PR→SF→SB→CH→BL→EL）、界面建模流程、校验规则 |
| `skills/windows-desktop-automation/` | Windows 桌面自动化（skill） | 截图 + 坐标点击操作第三方软件：DPI 缩放、前台锁、模态框、坐标换算、点击验证 |
| `skills/dsh-plugin-and-skill-ops/` | DSH 插件与 skill 运维（skill） | 装插件、接外部 MCP 服务器、写本地 skill 的全部踩坑与诊断入口 |
| `tools/` | asar 读取脚本（Node） | 从 DSH 的 `app.asar` 里提取插件实现，用于诊断"插件装了但没生效" |
| `tools/sistema/` | SISTEMA 工具链（Python） | `.ssm` 解析 / 层级重建 / 项目生成 / 一致性校验 + Excel 资料模板生成 |
| `windows-mcp/` | Windows-MCP 接入方案 | 一键安装 uv + windows-mcp + DSH 桥接插件，含配置片段、版本记录与 7 条踩坑 |

## 快速使用

### 1. 部署 skill

```powershell
Copy-Item .\skills\* "$env:USERPROFILE\.dsh\skills\" -Recurse -Force
```

> ⚠️ DSH 桌面版里 `@deepseek-ai/dsh-skill-filesystem` **默认是 inactive**，磁盘上放再多 skill
> 也不会被发现，而且不报错。需要在 profile patch 里显式激活：
> ```yaml
> - id: skill-filesystem
>   name: "@deepseek-ai/dsh-skill-filesystem"
>   disabled: false
>   config: { includeDefaultRoots: true, watch: true }
> ```
> 详见 `skills/dsh-plugin-and-skill-ops/SKILL.md`。

### 2. 接入 Windows-MCP（Windows 桌面自动化）

```powershell
.\windows-mcp\install-windows-mcp.ps1
```

脚本负责：装 uv → `uv tool install --python 3.13 windows-mcp` → 给 DSH 装桥接插件
`@deepseek-ai/dsh-mcp-client`，并打印需要追加到 `cordis.patch.yml` 的配置片段。追加后**重启 DSH** 生效。

### 3. SISTEMA 工具链

```powershell
$py = "$env:USERPROFILE\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"

# 重建项目层级树（读 .ssm 的 XML，输出到文件，避免控制台中文乱码）
& $py .\tools\sistema\ssm_hierarchy.py <项目.ssm> tree.txt

# 列出所有表与字段
& $py .\tools\sistema\ssm_inspect.py <项目.ssm> tables

# 从蓝本 .ssm 生成 Excel 资料收集模板（先改脚本内的 SSM/OUT 路径）
& $py .\tools\sistema\build_workbook.py
```

`tools/sistema/build_project.py` 是"按描述直接生成 `.ssm`"的尝试版本，**结论是不推荐**：
SISTEMA 有严格的 XML 校验（`mttfd` 必须 >3、`b10d` 必须 ≥0、字段名必须存在于 schema，
多写一个不存在的属性会报 `The attribute 'pl' is not allowed`），生成的缓存值也会让 PL 计算失真。
建议**在 SISTEMA 界面里建模**，流程见 `skills/sistema-safety-assessment/SKILL.md` 第 9 节。

## 这些内容是怎么来的

来自一次真实的设备自动化任务：给移印机做 SISTEMA 急停安全回路评估建模。

过程中踩的坑全部记录在对应 SKILL.md 里（而不是只留结论），例如：

- uv 默认挑最新 Python（3.15），`pyyaml` 没有对应 wheel → 必须 `--python 3.13`
- DSH profile patch **新增条目必须写在 `insert:` 列表里**，否则静默跳过；新增要重启，改已有条目能热加载
- `install_bundle` 只能装 bundle，普通插件要用 `dsh plugin ... add`
- skill provider 默认 inactive → 磁盘上放 skill 也不生效且无日志
- 150% 缩放下不调用 `SetProcessDPIAware()`，点击坐标被虚拟化且画面毫无变化
- Delphi 自绘模态框对合成鼠标事件不响应，只能靠键盘 / `WM_CLOSE`
- `System.Windows.Forms.SystemInformation.VirtualScreen` 返回逻辑值，不能用于坐标换算

## 许可

自用为主，随取随用。
