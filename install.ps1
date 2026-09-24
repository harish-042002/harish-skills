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
  Write-Host "  1. Global skill install - use Plat across projects"
  Write-Host "  2. Project-local skill install - install Plat only in this repo"
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
"@
  Write-Host "Added Plat Cursor rule: $Path"
}

function Expected-SkillDir {
  if ($Scope -eq "global") {
    switch ($Agent) {
      "claude-code" {
        if ($env:CLAUDE_CONFIG_DIR) { return (Join-Path $env:CLAUDE_CONFIG_DIR "skills/plat") }
        return (Join-Path $HOME ".claude/skills/plat")
      }
      "codex" {
        if ($env:CODEX_HOME) { return (Join-Path $env:CODEX_HOME "skills/plat") }
        return (Join-Path $HOME ".codex/skills/plat")
      }
      "cursor" { return (Join-Path $HOME ".cursor/skills/plat") }
    }
  }

  if ($Agent -eq "claude-code") {
    return (Join-Path (Get-Location) ".claude/skills/plat")
  }
  return (Join-Path (Get-Location) ".agents/skills/plat")
}

if (-not $Agent) { $Agent = Ask-Agent }
if (-not $Scope) { $Scope = Ask-Scope }

if (-not (Get-Command npx -ErrorAction SilentlyContinue)) { throw "npx is required." }
if (-not (Get-Command python -ErrorAction SilentlyContinue) -and -not (Get-Command python3 -ErrorAction SilentlyContinue)) { throw "Python 3 is required." }

Write-Host ""
Write-Host "PLAT · INSTALL / UPDATE"
Write-Host "Agent: $Agent"
Write-Host "Scope: $Scope"
Write-Host ""

$args = @("-y","skills@latest","add",$Repo,"--skill","plat","-a",$Agent,"--copy","-y")
if ($Scope -eq "global") { $args += "-g" }
& npx @args
if ($LASTEXITCODE -ne 0) { throw "Skills CLI install failed." }

$skillDir = Expected-SkillDir
$skillFile = Join-Path $skillDir "SKILL.md"
if (-not (Test-Path $skillFile)) {
  throw "Plat install verification failed. Expected: $skillFile"
}
Write-Host "Verified Plat skill: $skillFile"

$tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("plat-setup-" + [guid]::NewGuid().ToString() + ".py")
Invoke-WebRequest -Uri "$RawBase/skills/plat/scripts/setup.py" -OutFile $tmp

$py = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { "python3" }
$setupArgs = @($tmp)
if ($Reconfigure) { $setupArgs += "--force" }
& $py @setupArgs
if ($LASTEXITCODE -ne 0) { throw "Plat onboarding failed." }
Remove-Item -Force $tmp -ErrorAction SilentlyContinue

if ($Scope -eq "global") {
  switch ($Agent) {
    "claude-code" {
      $base = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $HOME ".claude" }
      Add-InstructionBlock (Join-Path $base "CLAUDE.md")
    }
    "codex" {
      $base = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
      Add-InstructionBlock (Join-Path $base "AGENTS.md")
    }
    "cursor" { Install-CursorRule (Join-Path $HOME ".cursor/rules/plat.mdc") }
  }
} else {
  switch ($Agent) {
    "claude-code" { Add-InstructionBlock (Join-Path (Get-Location) "CLAUDE.md") }
    default { Add-InstructionBlock (Join-Path (Get-Location) "AGENTS.md") }
  }
}

$updateChecker = Join-Path $skillDir "scripts/update_check.py"
if (Test-Path $updateChecker) {
  if ($Scope -eq "project") {
    & $py $updateChecker --register $skillDir --agent $Agent --scope $Scope --project-root (Get-Location).Path
  } else {
    & $py $updateChecker --register $skillDir --agent $Agent --scope $Scope
  }
  if ($LASTEXITCODE -ne 0) {
    Write-Warning "Plat update checker setup did not complete. Plat itself is still installed."
  }
  & $py $updateChecker --update-all
  if ($LASTEXITCODE -ne 0) {
    Write-Warning "One or more registered Plat installations could not be synchronized."
  }
} else {
  Write-Warning "Plat daily update checker was not found at $updateChecker"
}

Write-Host ""
Write-Host "Plat is ready."
Write-Host "Developer profile: $HOME/.plat/profile.md"
Write-Host "Skill:       $skillDir"
Write-Host ""
Write-Host "Ask normally. Plat decides the smallest useful mode, depth, and specialist team."
Write-Host "Update checks run every 2 hours outside engineering sessions and notify only when a newer release or remaining outdated installation exists."
Write-Host "Re-running this installer for any registered agent also syncs all other registered Plat installations."
