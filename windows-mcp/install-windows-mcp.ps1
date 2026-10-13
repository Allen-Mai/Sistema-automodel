<#
  install-windows-mcp.ps1
  在新设备上把 Windows-MCP 接入 DeepSeek Harness（DSH）。

  用法（管理员不需要，普通 PowerShell 即可）：
    powershell -ExecutionPolicy Bypass -File .\install-windows-mcp.ps1
    powershell -ExecutionPolicy Bypass -File .\install-windows-mcp.ps1 -DshCli "C:\...\resources\runtime\cli\bin\dsh.cmd" -McpClientVersion 0.2.0-rc.2

  说明：本脚本负责 1~4 步；第 5 步（改 patch）会打印出需要手动粘贴的片段，第 6 步需要你重启 DSH。
#>
param(
  [string]$PythonVersion = '3.13',
  [string]$DshCli = '',
  [string]$ProfileName = 'desktop',
  [string]$McpClientVersion = '0.2.0-rc.2'
)

$ErrorActionPreference = 'Stop'
function Info($m) { Write-Host "[*] $m" -ForegroundColor Cyan }
function Ok($m)   { Write-Host "[+] $m" -ForegroundColor Green }
function Warn($m) { Write-Host "[!] $m" -ForegroundColor Yellow }

# ---------- 1) uv ----------
$uv = Join-Path $env:USERPROFILE '.local\bin\uv.exe'
if (-not (Test-Path $uv)) {
  Info 'uv 未安装，开始安装（astral.sh 官方脚本）'
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
  Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
  if (-not (Test-Path $uv)) { throw "uv 安装后仍未找到：$uv" }
}
Ok "uv: $(& $uv --version)"

# ---------- 2) windows-mcp ----------
# 关键：必须指定 Python 版本。uv 默认挑最新（如 3.15），而 pyyaml 没有对应 wheel，
# 会尝试本地编译并因缺少 MSVC 失败。
Info "安装 windows-mcp（--python $PythonVersion）"
& $uv tool install --python $PythonVersion --force windows-mcp
$mcpExe = Join-Path $env:USERPROFILE '.local\bin\windows-mcp.exe'
if (-not (Test-Path $mcpExe)) { throw "windows-mcp.exe 未生成：$mcpExe" }
Ok "windows-mcp: $mcpExe"
& $mcpExe --help | Select-Object -First 3 | ForEach-Object { Write-Host "    $_" }

# ---------- 3) 定位 DSH CLI ----------
if (-not $DshCli) {
  $candidates = @(
    "$env:LOCALAPPDATA\Programs\DeepSeek Harness\resources\runtime\cli\bin\dsh.cmd",
    "$env:PROGRAMFILES\DeepSeek Harness\resources\runtime\cli\bin\dsh.cmd"
  )
  $DshCli = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
}
if (-not $DshCli) {
  Warn '未找到 dsh.cmd，请用 -DshCli 指定；跳过第 3~4 步'
} else {
  Ok "DSH CLI: $DshCli"
  $runtimeBin = Split-Path $DshCli -Parent | Split-Path -Parent | Split-Path -Parent
  $runtimeBin = Join-Path $runtimeBin 'bin'
  $env:Path = "$runtimeBin;$env:Path"

  # ---------- 4) 桥接插件（普通插件，不能用 install_bundle） ----------
  Info "安装桥接插件 @deepseek-ai/dsh-mcp-client@$McpClientVersion 到 profile '$ProfileName'"
  & $DshCli plugin --profile $ProfileName add "@deepseek-ai/dsh-mcp-client@$McpClientVersion"
  Ok '桥接插件已作为普通依赖写入 profile/package.json'
}

# ---------- 5) 打印需要手动追加的 patch ----------
$patchPath = Join-Path $env:USERPROFILE ".dsh\profiles\$ProfileName\cordis.patch.yml"
$snippet = @"
- insert:
    - id: mcp-windows
      name: "@deepseek-ai/dsh-mcp-client"
      config:
        serverName: windows
        transport: stdio
        command: "$($mcpExe -replace '\\','\\')"
        args: ["serve"]
        env:
          ANONYMIZED_TELEMETRY: "false"
        toolCallTimeoutMs: 120000
"@
Write-Host ''
Warn "把下面片段追加到：$patchPath"
Write-Host '--------------------------------------------------------------'
Write-Host $snippet
Write-Host '--------------------------------------------------------------'
Warn '追加后【重启 DSH 应用】才会生效（新增条目不能热加载）'
Info '验证：工具列表里应出现 mcp__windows__*（20 个），或直接向 windows-mcp.exe serve 发 initialize 测试'
