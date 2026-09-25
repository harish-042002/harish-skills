param(
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
  Write-Host "Choose where to install Plat:"
  Write-Host "  1. Claude Code"
  Write-Host "  2. Codex"
  Write-Host "  3. Cursor"
  Write-Host "  4. All coding agents supported by skills@latest"
  Write-Host "  5. Another supported agent ID"
  $choice = Read-Host ">"
  switch ($choice) {
    "1" { return "claude-code" }
    "2" { return "codex" }
    "3" { return "cursor" }
    "5" {
      $custom = Read-Host "Skills CLI agent ID (example: kiro-cli, antigravity, cline, opencode)"
      if (-not $custom) { throw "Agent ID cannot be empty." }
      return $custom
    }
    default { return "*" }
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
  $content = if (Test-Path $Path) { [IO.File]::ReadAllText($Path) } else { "" }
  $start = "<!-- plat:start -->"
  $end = "<!-- plat:end -->"
  $starts = [regex]::Matches($content, [regex]::Escape($start)).Count
  $ends = [regex]::Matches($content, [regex]::Escape($end)).Count
  if ($starts -ne $ends -or $starts -gt 1) { throw "Ambiguous Plat markers; instruction file left unchanged: $Path" }
  $block = $start + "`n" + "For obvious, local, reversible edits, work directly and verify the result without loading Plat unless explicitly requested. Use the installed Plat skill for non-trivial engineering work, unresolved risk, or multi-step changes." + "`n" + $end
  if ($starts -eq 1) {
    if ($content.IndexOf($end) -lt $content.IndexOf($start)) { throw "Reversed Plat markers; instruction file left unchanged" }
    $pattern = "(?s)" + [regex]::Escape($start) + ".*?" + [regex]::Escape($end)
    $updated = [regex]::Replace($content, $pattern, [System.Text.RegularExpressions.MatchEvaluator]{ param($m) $block })
  } else {
    $separator = if ($content -and -not $content.EndsWith("`n")) { "`n`n" } else { "`n" }
    $updated = $content + $separator + $block + "`n"
  }
  if ($dir) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
  if ($updated -ne $content) { [IO.File]::WriteAllText($Path, $updated, [System.Text.UTF8Encoding]::new($false)) }
  Write-Host "Plat activation rule current: $Path"
}

function Install-CursorRule([string]$Path) {
  $dir = Split-Path -Parent $Path
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  Set-Content -Path $Path -Value @"
---
description: Route non-trivial engineering work to Plat; keep tiny edits direct
alwaysApply: true
---

For obvious, local, reversible edits, work directly and verify the result without loading Plat unless explicitly requested. Use the installed Plat skill for non-trivial engineering work, unresolved risk, or multi-step changes.
"@
  Write-Host "Added Plat Cursor rule: $Path"
}

function Wire-KnownAgents {
  if ($Agent -eq "claude-code") {
    if ($Scope -eq "global") {
      $base = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $HOME ".claude" }
      Add-InstructionBlock (Join-Path $base "CLAUDE.md")
    } else {
      Add-InstructionBlock (Join-Path (Get-Location) "CLAUDE.md")
    }
    return
  }

  if ($Agent -eq "codex") {
    if ($Scope -eq "global") {
      $base = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
      Add-InstructionBlock (Join-Path $base "AGENTS.md")
    } else {
      Add-InstructionBlock (Join-Path (Get-Location) "AGENTS.md")
    }
    return
  }

  if ($Agent -eq "cursor") {
    if ($Scope -eq "global") {
      Install-CursorRule (Join-Path $HOME ".cursor/rules/plat.mdc")
    } else {
      Add-InstructionBlock (Join-Path (Get-Location) "AGENTS.md")
    }
    return
  }

  if ($Agent -eq "*" -and $Scope -eq "global") {
    $claudeBase = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $HOME ".claude" }
    $codexBase = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
    if (Test-Path $claudeBase) { Add-InstructionBlock (Join-Path $claudeBase "CLAUDE.md") }
    if (Test-Path $codexBase) { Add-InstructionBlock (Join-Path $codexBase "AGENTS.md") }
    if (Test-Path (Join-Path $HOME ".cursor")) { Install-CursorRule (Join-Path $HOME ".cursor/rules/plat.mdc") }
  }
}

if (-not $Agent) { $Agent = Ask-Agent }
if ($Agent -eq "all") { $Agent = "*" }
if (-not $Scope) { $Scope = Ask-Scope }

if (-not (Get-Command npx -ErrorAction SilentlyContinue)) { throw "npx is required." }
if (-not (Get-Command python -ErrorAction SilentlyContinue) -and -not (Get-Command python3 -ErrorAction SilentlyContinue)) { throw "Python 3 is required." }

Write-Host ""
Write-Host "PLAT · INSTALL / UPDATE"
if ($Agent -eq "*") {
  Write-Host "Agent: all agents supported by skills@latest"
} else {
  Write-Host "Agent: $Agent"
}
Write-Host "Scope: $Scope"
Write-Host ""

$args = @("-y","skills@latest","add",$Repo,"--skill","plat","-a",$Agent,"--copy","-y")
if ($Scope -eq "global") { $args += "-g" }
& npx @args
if ($LASTEXITCODE -ne 0) { throw "Skills CLI install failed. Check the agent ID printed by skills@latest." }

$py = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { "python3" }
$tmpSetup = Join-Path ([System.IO.Path]::GetTempPath()) ("plat-setup-" + [guid]::NewGuid().ToString() + ".py")
$tmpUpdate = Join-Path ([System.IO.Path]::GetTempPath()) ("plat-update-" + [guid]::NewGuid().ToString() + ".py")
Invoke-WebRequest -Uri "$RawBase/skills/plat/scripts/setup.py" -OutFile $tmpSetup
Invoke-WebRequest -Uri "$RawBase/skills/plat/scripts/update_check.py" -OutFile $tmpUpdate

$setupArgs = @($tmpSetup)
if ($Reconfigure) { $setupArgs += "--force" }
& $py @setupArgs
if ($LASTEXITCODE -ne 0) { throw "Plat onboarding failed." }

Wire-KnownAgents

$registerArgs = @($tmpUpdate, "--register-scope", "--agent-selector", $Agent, "--scope", $Scope)
if ($Scope -eq "project") {
  $registerArgs += @("--project-root", (Get-Location).Path)
}
& $py @registerArgs
if ($LASTEXITCODE -ne 0) { throw "Plat install verification/registration failed." }

$persistedUpdater = Join-Path $HOME ".plat/bin/update_check.py"
& $py $persistedUpdater --update-all
if ($LASTEXITCODE -ne 0) {
  Write-Warning "One or more older registered Plat installation groups could not be synchronized."
}

Remove-Item -Force $tmpSetup,$tmpUpdate -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "Plat is ready."
Write-Host "Developer profile: $HOME/.plat/profile.md"
Write-Host "Registered installs: $HOME/.plat/installations.json"
Write-Host ""
Write-Host "The upstream Skills CLI owns the coding-agent catalog and install paths."
Write-Host "Update checks run every 2 hours outside engineering sessions."
Write-Host "Re-running this installer from any supported agent can synchronize all registered Plat groups."
