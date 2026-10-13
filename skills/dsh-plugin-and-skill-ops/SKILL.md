---
name: dsh-plugin-and-skill-ops
description: 在 DeepSeek Harness(DSH) 桌面版里安装插件/接入外部 MCP 服务器/编写本地 skill 的完整踩坑记录，含 uv 安装、profile patch 语法、热重载边界、skill 发现机制。
whenToUse: 当需要给 DSH 装插件、接 MCP 服务器、加本地 skill，或"装了但没生效/没报错也没反应"时。
---

# DSH 插件与 Skill 运维（本机踩坑全集）

DSH 桌面版：`%LOCALAPPDATA%\Programs\DeepSeek Harness`（`resources/app.asar` 是归档，`resources/app.asar.unpacked/dsh` 是解包部分）；`DSH_HOME=C:\Users\<user>\.dsh`；profile = `C:\Users\<user>\.dsh\profiles\desktop`。
CLI：`resources\runtime\cli\bin\dsh.cmd`（需把 `resources\runtime\bin` 加进 PATH）。**desktop profile 被 Electron 独占，CLI 不能 boot/dump 它**（报 "managed exclusively by the Electron application"），但 `dsh plugin --profile desktop add ...` 这类 pnpm 转发是可用的。

## 1. 插件分两类，装法完全不同

| 类型 | 判据 | 装法 |
|---|---|---|
| **bundle** | package.json 里有 `dsh.bundle` | `plugin_manager install_bundle <spec>` |
| **普通插件** | 没有 `dsh.bundle`（如 `@deepseek-ai/dsh-mcp-client`） | `dsh plugin --profile desktop add <spec>`，会警告 "declares no dsh.bundle — installed as a plain dependency" |

用 `install_bundle` 装普通插件会得到 `error: {"code":"not-bundle"}`（包已 pnpm add 但不算 bundle）。

## 2. profile patch 语法（写错就静默跳过）

- 文件：`~/.dsh/profiles/desktop/cordis.patch.yml`，**顶层 YAML 数组**。
- **改已有条目**：`- id: <patchId>` + `name:` + `config:`（config **整体替换**，不是深合并）→ 保存后可**热重载**。
- **新增条目**：必须包在 `insert:` 列表里：
  ```yaml
  - insert:
      - id: mcp-windows
        name: "@deepseek-ai/dsh-mcp-client"
        config: { ... }
  ```
  直接写 `- id: mcp-windows / name: ...` 会被判 `patch: entry "mcp-windows" not found` 并**静默跳过**（只有 dump-config 才看得到警告）。
- **禁用/启用**：`disabled: false` 可强制激活一个默认 inactive 的条目。
- `app-boot/config-reload` 事件的语义是"不引入新的 inactive 条目"——**新增条目要重启应用**；覆盖已有条目的 config 能热生效。

## 3. 接入外部 MCP 服务器（以 Windows-MCP 为例）

1. 装 uv：`Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression`，会因执行策略报错 → 先 `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force`。
2. `uv tool install windows-mcp` —— **uv 默认挑最新 Python（3.15），pyyaml 无 cp315 wheel 会编译失败**（要 MSVC）。必须 `uv tool install --python 3.13 windows-mcp`。
3. DSH 侧：`dsh plugin --profile desktop add @deepseek-ai/dsh-mcp-client@0.2.0-rc.2`（**版本要与运行时 0.2.0-rc.2 对齐**，否则 peer 依赖冲突阻止安装）。
4. patch 里用 `insert:` 加服务器条目（`serverName/transport/stdio/command/args/env`）；stdio 子进程环境会被清洗（删掉匹配 `KEY|PASSWORD|SECRET|TOKEN` 与 `DSH_*` 的变量，但 config 里的 `env` 显式覆盖仍然生效）。
5. 工具名形如 `mcp__<serverName>__<Tool>`；stdout 必须是干净 JSON-RPC（用 node 脚本发 `initialize`+`tools/list` 可离线验证服务器）。

## 4. Skill 机制（最大的坑在这里）

- 位置：`<root>/<name>/SKILL.md` 或 `<root>/<name>.md`，**只扫一层**。根优先级：项目 `.dsh/skills`(100) → 项目 `.agents/skills`(200) → `customSkillDirs`(300) → **`~/.dsh/skills`(400)** → `~/.agents/skills`(500) → bundled(600)。
- frontmatter：`name`（kebab-case）+ `description` **必填**，可选 `whenToUse` / `metadata` / `disable-model-invocation` / `user-invocable`。写错会被**静默丢弃**（目录里不报错）。
- **致命坑**：desktop profile 里 `@deepseek-ai/dsh-skill-filesystem` 默认是 **inactive**，磁盘上放再多 skill 也不会被发现，`skill` 工具只回 "unknown or no longer available"，**没有任何日志**。
  修复（可热生效）：patch 里加
  ```yaml
  - id: skill-filesystem
    name: "@deepseek-ai/dsh-skill-filesystem"
    disabled: false
    config: { includeDefaultRoots: true, watch: true }
  ```
  改完用 `cordis_inspect_query(Config/listConfigs, name=...)` 看状态是否从 `inactive` 变 `schema`。
- 排查顺序：`skill` 工具是**实时**查 `ctx.skills.list()`（无缓存）→ 看不到就说明 provider 没在工作，而不是文件写错。
- 诊断插件状态：`cordis_inspect_list` / `Config.listConfigs`（看 status、packageDir）；asar 内的实现可用自写脚本提取：`node asar-read.js get <app.asar> /dsh/node_modules/<pkg>/lib/index.js <out>`（脚本见 `default-workspace/asar-read.js`，注意它提取的文件含非 UTF-8 字节时 ripgrep 会当二进制跳过，用 Python 读）。

## 5. 常用只读诊断入口

- `plugin_manager(list_plugins)`：条目 enabled / fiberPhase（`active` / `null`）/ patchId。
- `plugin_manager(list_bundles)`：bundle 的 rows 与 overrides。
- `cordis_inspect_query(Config, listConfigs, {name|entry})`：条目的 Config 投影状态。
- `cordis_inspect_query(Tool, listTools)`：确认新工具（含 `mcp__*`）是否已注册。
- dump patch 语法真源：`dsh <新profile> --dump-config-schema`（别用 desktop，被独占）；验证 patch 是否被接受：`dsh <新profile> --dump-config`。

## 6. 权限与流程注意

- 会话审批策略为 `never` 时，任何需要审批的动作（`sandbox_permissions` 提权、plugin_manager 写操作）会被**自动拒绝**，不要反复尝试。
- 装第三方插件/运行外部 MCP 服务器会把外部代码引入本机并常带完全系统访问能力（Windows-MCP 自带 PowerShell/Registry/FileSystem 工具），装前要提醒用户；遥测类变量（如 `ANONYMIZED_TELEMETRY=false`）可在 `env` 里关掉。

## 7. 网络与代理（本机必读）

- 本机 **github.com 直连不稳定/不可达**（`Test-NetConnection github.com -Port 443` 为 False），但 **Clash Verge 常驻**
  （`clash-verge` + `verge-mihomo` 进程，系统代理 `HKCU:\...\Internet Settings` 指向 `127.0.0.1:7897`）。
- **git 不读 Windows 系统代理**，直连 clone/push 会失败：
  `fatal: unable to access 'https://github.com/...': Failed to connect to github.com:443 after 21xxx ms`。
  解决（只在本次命令生效，不改用户全局配置）：
  ```powershell
  git -c http.proxy=http://127.0.0.1:7897 -c https.proxy=http://127.0.0.1:7897 push origin main
  ```
  需要持久化时再写 `git config --global http.https://github.com.proxy http://127.0.0.1:7897`。
- 先用 `Invoke-WebRequest -Proxy http://127.0.0.1:7897 https://api.github.com/rate_limit` 验证代理是否通（HTTP 200 即可）。
- PowerShell 调用 git 时，正常进度也会走 stderr，看起来像报错；**判断成败看 `$LASTEXITCODE` 和 `git ls-remote`**，不要被红字误导。
- 本机 git 是 winget 装的（`winget install --id Git.Git -e --scope user`，2.55.x），装完新进程才有 PATH。
- 该机器的 GitHub 凭据已存在（clone/push 无需输入 PAT）；私有仓库用 API 查会返回 404，属正常现象，用 `git ls-remote` 判断存在性更可靠。
