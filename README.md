# Sistema-automodel

**SISTEMA 自动化建模** —— 用结构化描述直接生成能被 SISTEMA 3.0.4（ISO 13849-1:2023）正常打开的安全回路评估项目。
仓库沉淀了从**标准条款 → 软件界面操作 → `.ssm` 文件格式**的完整实践，另附几项 DSH（DeepSeek Harness）
周边能力（Windows 桌面自动化、插件与 skill 运维）。

> 📘 **[SISTEMA 建模规范](SISTEMA建模规范.md)** —— 项目结构、命名、参数取值与交付校验的作业基准。
> 无论是人工建模还是脚本生成，都按这份规范执行；新手先读它。

## 目录

| 路径 | 内容 |
|---|---|
| **[SISTEMA建模规范.md](SISTEMA建模规范.md)** | **建模规范**：六层层级、命名规则、子系统形态选择、参数规范与数据来源、元件细分、建模流程、交付校验清单、错误速查 |
| `skills/sistema-safety-assessment/` | SISTEMA 安全评估 skill（规范的**操作细则版**）：界面结构、Win32 消息自动化、`.ssm` XML 结构、ISO 13849-1:2023 条款、IFA 官方资源、急停建模参照模板、键盘快捷键 |
| `tools/sistema/sistema_auto.py` | **建模生成器**：结构化描述 → 合法 `.ssm`（模板继承式，内置生成前校验） |
| `tools/sistema/ssm-schema.md` | `.ssm` 九张表的完整字段清单、枚举取值、oid 层级关联、7 条实测失败案例 |
| `tools/sistema/` 其它脚本 | `.ssm` 解析 / 层级重建 / 批量摘要 / PDF 文本提取 / Excel 资料模板生成 |
| `skills/windows-desktop-automation/` | Windows 桌面自动化 skill：DPI 缩放、前台锁、模态框、坐标换算、点击验证 |
| `skills/dsh-plugin-and-skill-ops/` | DSH 插件与 skill 运维 skill：装插件、接外部 MCP、写本地 skill 的全部踩坑 |
| `tools/`（asar-*.js） | 从 DSH 的 `app.asar` 提取插件实现，用于诊断"插件装了但没生效" |
| `windows-mcp/` | Windows-MCP 接入方案：一键安装脚本 + DSH 配置片段 + 版本记录 + 7 条踩坑 |

## 快速开始

### 1. 生成一个 SISTEMA 项目

```powershell
$py = "$env:USERPROFILE\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"

& $py .\tools\sistema\sistema_auto.py demo  D:\sistema\移印机_auto.ssm   # 内置移印机急停示例
& $py .\tools\sistema\sistema_auto.py build spec.json out.ssm             # 吃结构化描述
& $py .\tools\sistema\sistema_auto.py show  D:\sistema\移印机_auto.ssm    # 查看已有项目结构
```

生成的文件可直接被 SISTEMA 3.0.4 打开（**实测**：层级正确、封装子系统识别为绿色、Messages 可评估）。
打开后需**在界面里改一次参数**触发重算再 `Ctrl+S` —— 原因见
[建模规范 §9.2](SISTEMA建模规范.md#92-生成后的必做动作)（`plcal`/`pfhcal` 是软件回写字段）。

### 2. 查看 / 分析已有项目

```powershell
& $py .\tools\sistema\ssm_hierarchy.py    <项目.ssm> tree.txt   # 重建层级树（输出到文件，避免控制台中文乱码）
& $py .\tools\sistema\ssm_inspect.py      <项目.ssm> tables     # 列出所有表与字段
& $py .\tools\sistema\extract_examples.py <示例目录> out.txt    # 批量摘要一批 .ssm
& $py .\tools\sistema\extract_pdf.py      <PDF> out.txt         # 提取 IFA Cookbook 等 PDF 正文
```

### 3. 部署 skill / 接入 Windows-MCP

```powershell
Copy-Item .\skills\* "$env:USERPROFILE\.dsh\skills\" -Recurse -Force
.\windows-mcp\install-windows-mcp.ps1
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

## 已验证的关键事实

| 事实 | 说明 |
|---|---|
| **可直接生成合法 `.ssm`** | 拿本机 SISTEMA 保存的项目当模板，继承字段声明 / 表集合 / 每列默认值 / 数字格式，只重建数据行 |
| 必须写**全部**声明列 | 空值写 `""`；漏列会报 `Error reading field <Document>`，文件**打不开** |
| 只能写**声明过**的列 | 否则错误码 1866 —— 例：2.0.8 的 `pldirectcal` 在 3.0.4 叫 `pldirectbindcal` |
| 数字格式随版本 | 3.0.4 用**点号** `0.65`；2.0.8 官方示例用**逗号** `0,65` |
| 设 Category 后自动生成通道 | 不需要手工建 CH1 / CH2 / chTest |
| 认证安全继电器属**封装子系统** | PNOZ / G9SX 应填厂家 PL/PFH，不要建成 Cat 4 刚性结构 |
| 带 B10d 的元件要拆到**元素级** | 官方 35 个示例：256 个块配 244 个元素 |
| Cat 4 通道 MTTFd 上限 **2500 a** | 其余情况 100 a（2023 版相对旧版的实质变化） |
| SISTEMA 可被 **Win32 消息驱动** | 无 UI Automation 也能自动化：输入框 `WM_SETTEXT`、下拉 `WM_GETTEXT`、按钮 `BM_CLICK` |
| 六层层级 | PR → SF → SB → CH/TE → BL → EL，且插入顺序受强制约束 |

## 这些内容是怎么来的

来自一次真实任务：给**移印机**做急停安全回路评估建模
（6 个 XB4BS84441 急停按钮串联 → PNOZ c1 安全继电器 → G7SA-4A2B 强导型继电器 → 8 台汇川 SV630 的 STO）。

过程中把**标准、软件、文件格式**三层都趟了一遍，踩的坑全部记录在对应文档里（而不是只留结论）：

- SISTEMA 虽无 UI Automation，但 Delphi 控件本身是标准 Win32 窗口 → 可发消息驱动；
  `TLabeledEditEx` **没有**内部 `Edit` 子窗口，消息要发给控件本体；`GetWindowText` 跨进程只读缓存
- 150% 缩放下不调 `SetProcessDPIAware()`，点击坐标被虚拟化**且画面毫无变化**（极易误判成"控件不响应"）
- Delphi 自绘模态框对合成鼠标事件不响应，只能靠键盘 / `WM_CLOSE` / 子窗口 `BM_CLICK`
- `System.Windows.Forms.SystemInformation.VirtualScreen` 返回逻辑值，**不能**用于坐标换算
- DSH：profile patch 新增条目必须写在 `insert:` 里否则静默跳过；`install_bundle` 只能装 bundle；
  uv 默认挑最新 Python 导致 `pyyaml` 编译失败（须 `--python 3.13`）
- Git：本机 github 直连不可达，且 **git 不读 Windows 系统代理**，推送需 `-c http.proxy=…`

## 许可

自用为主，随取随用。
