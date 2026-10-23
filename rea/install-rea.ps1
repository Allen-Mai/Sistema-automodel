<#
.SYNOPSIS
    Install REA (rea-agents) for DeepSeek Harness, idempotently.

.DESCRIPTION
    1. Node 24.22.1 into %LOCALAPPDATA%\Programs\node24 when the machine Node is
       outside REA's supported range (^22.23.4 || ^24.22.1 || >=26.12.1).
    2. npm i -g rea-agents using that npm, with a private cache directory.
    3. rea setup --client dsh, falling back to a manual Cordis patch when REA's
       transactional write fails with "reason: write" on this host.
    4. rea doctor --client dsh to verify.

.NOTES
    Restart DeepSeek Harness afterwards: new Cordis patch entries are not hot
    loaded, so mcp__rea__* tools only appear on the next start.
#>
[CmdletBinding()]
param(
    [string]$NodeRoot = "$env:LOCALAPPDATA\Programs\node24",
    [string]$NodeVersion = "24.22.1",
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

function Write-Step($message) { Write-Host "==> $message" -ForegroundColor Cyan }

function Get-NodeVersion($exe) {
    if (-not (Test-Path $exe)) { return "" }
    try { return (& $exe -p "process.version").Trim() } catch { return "" }
}

function Test-ReaNode($version) {
    # REA: ^22.23.4 || ^24.22.1 || >=26.12.1
    if ($version -match '^v(\d+)\.(\d+)\.(\d+)') {
        $major = [int]$Matches[1]; $minor = [int]$Matches[2]; $patch = [int]$Matches[3]
        if ($major -eq 22) { return ($minor -gt 23) -or ($minor -eq 23 -and $patch -ge 4) }
        if ($major -eq 24) { return ($minor -gt 22) -or ($minor -eq 22 -and $patch -ge 1) }
        if ($major -gt 26) { return $true }
        if ($major -eq 26) { return ($minor -gt 12) -or ($minor -eq 12 -and $patch -ge 1) }
    }
    return $false
}

# --- 1. Node runtime -------------------------------------------------------
$nodeExe = Join-Path $NodeRoot "node.exe"
$current = Get-NodeVersion $nodeExe
if (-not (Test-ReaNode $current)) {
    Write-Step "installing Node $NodeVersion into $NodeRoot"
    $zip = Join-Path $env:TEMP "node-v$NodeVersion-win-x64.zip"
    $url = "https://nodejs.org/dist/v$NodeVersion/node-v$NodeVersion-win-x64.zip"
    Invoke-WebRequest -Uri $url -OutFile $zip -UseBasicParsing
    $extract = Join-Path $env:TEMP "node-v$NodeVersion-extract"
    if (Test-Path $extract) { Remove-Item $extract -Recurse -Force }
    Expand-Archive -Path $zip -DestinationPath $extract -Force
    if (Test-Path $NodeRoot) { Remove-Item $NodeRoot -Recurse -Force }
    Move-Item (Join-Path $extract "node-v$NodeVersion-win-x64") $NodeRoot
    Remove-Item $zip -Force; Remove-Item $extract -Recurse -Force
    $current = Get-NodeVersion $nodeExe
}
Write-Step "node $current at $nodeExe"
if (-not (Test-ReaNode $current)) { throw "Node $current is outside REA's supported range" }

# --- 2. rea-agents ---------------------------------------------------------
$reaScript = Join-Path $NodeRoot "node_modules\rea-agents\scripts\rea.mjs"
if ($Force -or -not (Test-Path $reaScript)) {
    Write-Step "npm install -g rea-agents"
    $env:npm_config_cache = Join-Path $NodeRoot "npm-cache"
    Push-Location $NodeRoot
    try { & (Join-Path $NodeRoot "npm.cmd") install -g rea-agents --loglevel=warn }
    finally { Pop-Location }
}
& $nodeExe $reaScript --version

# --- 3. register with DeepSeek Harness ------------------------------------
$dshHome = if ($env:DSH_HOME) { $env:DSH_HOME } else { Join-Path $env:USERPROFILE ".dsh" }
$patchPath = Join-Path $dshHome "cordis.patch.yml"
Write-Step "rea setup --client dsh"
$json = & $nodeExe $reaScript setup --client dsh --yes --json 2>$null
$setupFailed = $LASTEXITCODE -ne 0
if ($setupFailed) {
    Write-Warning "REA setup failed (reason: write on this host); applying the documented entry manually"
    $entry = @(
        "- insert:",
        "    - id: rea-mcp",
        "      name: ""@deepseek-ai/dsh-mcp-client""",
        "      config:",
        "        serverName: rea",
        "        transport: stdio",
        "        command: $nodeExe",
        "        args: [""$($reaScript -replace '\\','\\\\')"", ""mcp""]"
    ) -join "`r`n"
    $existing = if (Test-Path $patchPath) { Get-Content $patchPath -Raw } else { "" }
    if ($existing -notmatch "rea-mcp") {
        if (Test-Path $patchPath) { Copy-Item $patchPath "$patchPath.rea.backup" -Force }
        Set-Content -Path $patchPath -Value (($existing.TrimEnd() + "`r`n" + $entry).TrimStart()) -Encoding utf8
        Write-Step "wrote $patchPath"
    } else {
        Write-Step "rea-mcp entry already present in $patchPath"
    }
    $skillSource = Join-Path $NodeRoot "node_modules\rea-agents\skills\reverse-engineer-anything"
    $skillRoot = Join-Path $env:USERPROFILE ".agents\skills"
    if (Test-Path $skillSource) {
        New-Item -ItemType Directory -Force -Path $skillRoot | Out-Null
        Copy-Item $skillSource (Join-Path $skillRoot "reverse-engineer-anything") -Recurse -Force
        Write-Step "installed skill into $skillRoot"
    }
}

# --- 4. verify -------------------------------------------------------------
Write-Step "rea doctor --client dsh"
& $nodeExe $reaScript doctor --client dsh --json | Out-Null
Write-Host ""
Write-Host "Done. Restart DeepSeek Harness, then REA tools appear as mcp__rea__*." -ForegroundColor Green
