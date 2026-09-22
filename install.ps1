param(
  [ValidateSet("claude-code","codex","cursor")]
  [string]$Agent,
  [ValidateSet("global","project")]
  [string]$Scope,
  [switch]$Reconfigure
)

$ErrorActionPreference = "Stop"
$Repo = "harish-042002/harish-skills"
$RawBase = "https://raw.githubusercontent.com/$Repo/main"

function Ask-Agent {
  Write-Host ""
  Write-Host "Choose your coding agent:"
  Write-Host "  1. Claude Code"
  Write-Host "  2. Codex"
  Write-Host "  3. Cursor"
  $choice = Read-Host ">"
  switch ($choice) {
    "2" { return "codex" }
    "3" { return "cursor" }
    default { return "claude-code" }
  }
}

function Ask-Scope {
  Write-Host ""
  Write-Host "Install scope:"
  Write-Host "  1. Global - use Plat across projects"
  Write-Host "  2. Project - use Plat only in this project"
  $choice = Read-Host ">"
  if ($choice -eq "2") { return "project" }
  return "global"
}

function Add-InstructionBlock([string]$Path) {
  $dir = Split-Path -Parent $Path
  if ($dir) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
  if (-not (Test-Path $Path)) { New-Item -ItemType File -Force -Path $Path | Out-Null }

  $content = Get-Content -Raw -Path $Path
  if ($content -match "<!-- plat:start -->") {
    Write-Host "Plat instruction already present: $Path"
    return
  }

  Add-Content -Path $Path -Value @"

<!-- plat:start -->
For software engineering requests, use the installed Plat skill.
If the Plat developer profile is missing in an interactive session, complete Plat onboarding before substantive engineering work.
<!-- plat:end -->
"@
  Write-Host "Added Plat instruction: $Path"
}

function Install-CursorRule([string]$Path) {
  $dir = Split-Path -Parent $Path
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  Set-Content -Path $Path -Value @"
---
description: Use installed Plat for software engineering requests
alwaysApply: true
---

For software engineering requests, use the installed Plat skill.
If the Plat developer profile is missing in an interactive session, complete Plat onboarding before substantive engineering work.
"@
  Write-Host "Added Plat Cursor rule: $Path"
}

if (-not $Agent) { $Agent = Ask-Agent }
if (-not $Scope) { $Scope = Ask-Scope }

if (-not (Get-Command npx -ErrorAction SilentlyContinue)) { throw "npx is required." }
if (-not (Get-Command python -ErrorAction SilentlyContinue) -and -not (Get-Command python3 -ErrorAction SilentlyContinue)) { throw "Python 3 is required." }

Write-Host ""
Write-Host "PLAT · INSTALL"
Write-Host "Agent: $Agent"
Write-Host "Scope: $Scope"
Write-Host ""

$args = @("skills","add",$Repo,"--skill","plat","-a",$Agent,"-y")
if ($Scope -eq "global") { $args += "-g" }
& npx @args

$tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("plat-setup-" + [guid]::NewGuid().ToString() + ".py")
Invoke-WebRequest -Uri "$RawBase/skills/plat/scripts/setup.py" -OutFile $tmp

$py = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { "python3" }
$setupArgs = @($tmp)
if ($Reconfigure) { $setupArgs += "--force" }
& $py @setupArgs
Remove-Item -Force $tmp -ErrorAction SilentlyContinue

if ($Scope -eq "global") {
  switch ($Agent) {
    "claude-code" { Add-InstructionBlock (Join-Path $HOME ".claude/CLAUDE.md") }
    "codex" { Add-InstructionBlock (Join-Path $HOME ".codex/AGENTS.md") }
    "cursor" { Install-CursorRule (Join-Path $HOME ".cursor/rules/plat.mdc") }
  }
} else {
  switch ($Agent) {
    "claude-code" { Add-InstructionBlock (Join-Path (Get-Location) "CLAUDE.md") }
    default { Add-InstructionBlock (Join-Path (Get-Location) "AGENTS.md") }
  }
}

Write-Host ""
Write-Host "Plat is ready."
Write-Host "Update check: npx skills check"
if ($Scope -eq "global") {
  Write-Host "Update:       npx skills update plat -g"
} else {
  Write-Host "Update:       npx skills update plat -p"
}
