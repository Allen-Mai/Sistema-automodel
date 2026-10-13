# 08 - Windows MCP（DSH 接入 Windows 桌面自动化）

给 DeepSeek Harness 接上 [Windows-MCP](https://github.com/CursorTouch/Windows-MCP)：一个用 Python 写的 MCP 服务器，
把 Windows 桌面操作能力（截图、点击、输入、开程序、PowerShell、注册表、文件系统…）暴露给 AI Agent。

- 上游：`CursorTouch/Windows-MCP`（MIT，默认分支 `main`）
- PyPI 包：`windows-mcp`（本机安装版本 **0.8.5**，uv tool 安装）
- DSH 侧桥接插件：`@deepseek-ai/dsh-mcp-client`（版本必须与 DSH 运行时一致，本机为 **0.2.0-rc.2**）

## 为什么需要桥接插件

DSH 的插件体系（`dsh.bundle`）只吃 npm 插件包，**自己不实现 MCP 客户端**。要让 DSH 用上外部 MCP 服务器，
必须装官方桥接包 `@deepseek-ai/dsh-mcp-client`，由它把 MCP 工具注册进 `ctx.tools`，工具名形如
`mcp__<serverName>__<Tool>`（本机为 `mcp__windows__Click`、`mcp__windows__Snapshot` …）。

## 目录内容

| 文件 | 说明 |
|---|---|
| `install-windows-mcp.ps1` | 新设备一键安装（uv → windows-mcp → DSH 插件 → 配置提示） |
| `dsh-config/cordis.patch.snippet.yml` | DSH 侧要写入 profile patch 的配置片段 |
| `VERSION.txt` | 本机已验证的版本组合 |
| `github-src/`（可选） | 上游源码浅克隆，需要时用 `git clone --depth 1` 拉 |

## 安装步骤（新设备）

```powershell
# 1) 装 uv（PowerShell 执行策略会拦，先放行当前进程）
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression

# 2) 装 Windows-MCP —— 必须显式指定 Python 3.13！
& "$env:USERPROFILE\.local\bin\uv.exe" tool install --python 3.13 windows-mcp

# 3) DSH 侧装桥接插件（版本对齐运行时；desktop profile 被 Electron 独占，只能用 CLI 的 pnpm 转发）
#    把 resources\runtime\bin 加进 PATH 后：
dsh plugin --profile desktop add "@deepseek-ai/dsh-mcp-client@0.2.0-rc.2"
```

4) 把 `dsh-config/cordis.patch.snippet.yml` 里的 `insert:` 条目追加到
`%USERPROFILE%\.dsh\profiles\desktop\cordis.patch.yml`，并把 `command` 的路径换成目标机器的实际路径。

5) **重启 DSH 应用**（新增条目不能热加载；覆盖已有条目的 config 才能热生效）。

6) 验证：问一句需要桌面的任务，或直接看工具列表里是否出现 `mcp__windows__*`；
也可以脱离 DSH 单独验证服务器：向 `windows-mcp.exe serve` 的 stdin 发一个 `initialize` + `tools/list`（换行分隔 JSON-RPC），应返回 20 个工具。

## 踩坑记录（都实际踩过）

1. **uv 默认挑最新 Python（3.15）→ 安装失败**：`pyyaml` 没有 cp315 预编译轮子，需要 MSVC 现场编译，报
   `Microsoft Visual C++ 14.0 or greater is required`。**必须 `--python 3.13`**（Windows-MCP 要求 ≥3.13，3.13 有现成 wheel）。
2. **不能用 `plugin_manager install_bundle` 装桥接插件**：`@deepseek-ai/dsh-mcp-client` 的 package.json 里没有
   `dsh.bundle`，属于"普通插件"，`install_bundle` 会返回 `{"code":"not-bundle"}`（包被 pnpm add 了但不算 bundle）。
   正确做法是 `dsh plugin --profile desktop add <spec>`，它会提示
   `declares no dsh.bundle — installed as a plain dependency`。
3. **profile patch 新增条目必须写在 `insert:` 列表里**。直接写
   `- id: mcp-windows` / `name: ...` 会被判 `patch: entry "mcp-windows" not found` 并**静默跳过**
   （只有 `--dump-config` 才能看到警告）。改已有条目（如 `skill-filesystem`）则不需要 insert。
4. **新增条目要重启应用**：`app-boot/config-reload` 只做"已有条目的和解"，语义上不引入新的 inactive 条目。
   改完 patch 后如果工具不出现，先重启再排查。
5. **版本要对齐**：桥接插件的 peerDependencies 绑定 DSH 运行时版本，装错版本会被 peer 检查拦下或激活失败。
   查运行时版本：`plugin_manager(list_bundles)` 里 bundle 的 `version` 字段。
6. **stdio 子进程环境会被清洗**：桥接插件删除匹配 `/KEY|PASSWORD|SECRET|TOKEN/i` 以及所有 `DSH_*` 的环境变量，
   但配置里的 `env` 是显式覆盖、仍然生效（所以 `ANONYMIZED_TELEMETRY: "false"` 能关掉上游遥测）。
7. **安全提醒**：Windows-MCP 自带 `PowerShell` / `Registry` / `FileSystem` / `App` 等完全系统访问能力，
   且 `Snapshot`/`Screenshot` 会把整屏内容送进模型上下文。只做 UI 自动化时建议在 `args` 里加
   `--exclude-tools "PowerShell,Registry"` 收窄权限。

## 本机实际状态（供对照）

- `uv.exe` / `uvx.exe` / `windows-mcp.exe` → `%USERPROFILE%\.local\bin\`
- Python 包（uv tool 环境）→ `%APPDATA%\uv\tools\windows-mcp\`（`windows_mcp-0.8.5.dist-info`）
- 服务器信息：`serverInfo.name = windows-mcp`，返回 20 个工具
  （App / DisplayInventory / PowerShell / FileSystem / Snapshot / Screenshot / Click / Type / Scroll / Move /
  Shortcut / Wait / WaitFor / Scrape / MultiSelect / MultiEdit / Clipboard / Process / Notification / Registry）
- 首次调用会有 1~3 秒启动延迟（stdio 子进程冷启动），之后单次调用通常 0.2~0.5 秒
