#!/usr/bin/env bash
set -euo pipefail

REPO="harish-042002/harish-skills"
RAW_BASE="https://raw.githubusercontent.com/${REPO}/main"
AGENT=""
SCOPE=""
RECONFIGURE=0

usage() {
  cat <<'EOF'
Plat installer

Usage:
  bash install.sh [--agent all|<skills-cli-agent-id>] [--scope global|project] [--reconfigure]

Examples:
  bash install.sh --agent all --scope global
  bash install.sh --agent codex --scope global
  bash install.sh --agent kiro-cli --scope global
  bash install.sh --agent antigravity --scope project

Agent IDs are validated by the current skills@latest catalog. Plat does not keep
its own fixed coding-agent whitelist.

The installer:
  1. installs Plat using the current Skills CLI agent catalog,
  2. verifies the installed Plat scope using skills list --json,
  3. runs one-time developer preference onboarding,
  4. adds extra persistent instruction wiring only for known hosts where useful,
  5. registers the 2-hour release checker and cross-agent updater.

Re-running this installer updates/synchronizes registered Plat installations
while preserving the developer profile.
EOF
}

ask_agent() {
  local choice raw_choice custom
  while true; do
    echo
    echo "Choose where to install Plat:"
    echo "  1. Claude Code"
    echo "  2. Codex"
    echo "  3. Cursor"
    echo "  4. All coding agents supported by skills@latest"
    echo "  5. Another supported agent ID"
    read -r -p "> " raw_choice || exit 1

    if [[ -z "$raw_choice" ]]; then
      choice="4"
    else
      choice="${raw_choice##*[!0-9]}"
    fi

    case "$choice" in
      1) AGENT="claude-code"; return 0 ;;
      2) AGENT="codex"; return 0 ;;
      3) AGENT="cursor"; return 0 ;;
      4) AGENT="*"; return 0 ;;
      5)
        read -r -p "Skills CLI agent ID (example: kiro-cli, antigravity, cline, opencode): " custom || exit 1
        if [[ -n "$custom" ]]; then
          AGENT="$custom"
          return 0
        fi
        echo "Agent ID cannot be empty." >&2
        ;;
      *) echo "Please enter 1, 2, 3, 4, or 5." >&2 ;;
    esac
  done
}

ask_scope() {
  local choice raw_choice
  while true; do
    echo
    echo "Install scope:"
    echo "  1. Global skill install — use Plat across projects"
    echo "  2. Project-local skill install — install Plat only in this repo"
    read -r -p "> " raw_choice || exit 1

    if [[ -z "$raw_choice" ]]; then
      choice="1"
    else
      choice="${raw_choice##*[!0-9]}"
    fi

    case "$choice" in
      1) SCOPE="global"; return 0 ;;
      2) SCOPE="project"; return 0 ;;
      *) echo "Please enter 1 or 2." >&2 ;;
    esac
  done
}

append_block() {
  local file="$1"
  mkdir -p "$(dirname "$file")"
  touch "$file"

  if grep -q "<!-- plat:start -->" "$file" 2>/dev/null; then
    echo "✓ Plat instruction already present: $file"
    return 0
  fi

  cat >> "$file" <<'EOF'

<!-- plat:start -->
For software engineering requests, use the installed Plat skill.
<!-- plat:end -->
EOF
  echo "✓ Added Plat instruction: $file"
}

install_cursor_rule() {
  local file="$1"
  mkdir -p "$(dirname "$file")"
  cat > "$file" <<'EOF'
---
description: Use installed Plat for software engineering requests
alwaysApply: true
---

For software engineering requests, use the installed Plat skill.
EOF
  echo "✓ Added Plat Cursor rule: $file"
}

wire_known_agents() {
  if [[ "$AGENT" == "claude-code" ]]; then
    if [[ "$SCOPE" == "global" ]]; then
      append_block "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/CLAUDE.md"
    else
      append_block "$(pwd)/CLAUDE.md"
    fi
    return 0
  fi

  if [[ "$AGENT" == "codex" ]]; then
    if [[ "$SCOPE" == "global" ]]; then
      append_block "${CODEX_HOME:-$HOME/.codex}/AGENTS.md"
    else
      append_block "$(pwd)/AGENTS.md"
    fi
    return 0
  fi

  if [[ "$AGENT" == "cursor" ]]; then
    if [[ "$SCOPE" == "global" ]]; then
      install_cursor_rule "$HOME/.cursor/rules/plat.mdc"
    else
      append_block "$(pwd)/AGENTS.md"
    fi
    return 0
  fi

  if [[ "$AGENT" == "*" && "$SCOPE" == "global" ]]; then
    [[ -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}" ]] && append_block "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/CLAUDE.md"
    [[ -d "${CODEX_HOME:-$HOME/.codex}" ]] && append_block "${CODEX_HOME:-$HOME/.codex}/AGENTS.md"
    [[ -d "$HOME/.cursor" ]] && install_cursor_rule "$HOME/.cursor/rules/plat.mdc"
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent)
      AGENT="${2:-}"
      shift 2
      ;;
    --scope)
      SCOPE="${2:-}"
      shift 2
      ;;
    --reconfigure)
      RECONFIGURE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 2
      ;;
  esac
done

command -v npx >/dev/null 2>&1 || { echo "npx is required." >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "python3 is required." >&2; exit 1; }
command -v curl >/dev/null 2>&1 || { echo "curl is required." >&2; exit 1; }

[[ -n "$AGENT" ]] || ask_agent
[[ -n "$SCOPE" ]] || ask_scope
[[ "$AGENT" != "all" ]] || AGENT="*"

case "$SCOPE" in
  global|project) ;;
  *) echo "Unsupported scope: $SCOPE" >&2; exit 2 ;;
esac

echo
echo "PLAT · INSTALL / UPDATE"
if [[ "$AGENT" == "*" ]]; then
  echo "Agent: all agents supported by skills@latest"
else
  echo "Agent: $AGENT"
fi
echo "Scope: $SCOPE"
echo

INSTALL_ARGS=(-y skills@latest add "$REPO" --skill plat -a "$AGENT" --copy -y)
if [[ "$SCOPE" == "global" ]]; then
  INSTALL_ARGS+=(-g)
fi

npx "${INSTALL_ARGS[@]}"

tmp_setup="$(mktemp)"
tmp_update="$(mktemp)"
trap 'rm -f "$tmp_setup" "$tmp_update"' EXIT
curl -fsSL "${RAW_BASE}/skills/plat/scripts/setup.py" -o "$tmp_setup"
curl -fsSL "${RAW_BASE}/skills/plat/scripts/update_check.py" -o "$tmp_update"

if [[ "$RECONFIGURE" -eq 1 ]]; then
  python3 "$tmp_setup" --force
else
  python3 "$tmp_setup"
fi

wire_known_agents

if [[ "$SCOPE" == "project" ]]; then
  python3 "$tmp_update" --register-scope --agent-selector "$AGENT" --scope project --project-root "$(pwd)"
else
  python3 "$tmp_update" --register-scope --agent-selector "$AGENT" --scope global
fi

python3 "$HOME/.plat/bin/update_check.py" --update-all || true

echo
echo "✓ Plat is ready."
echo "  Developer profile: $HOME/.plat/profile.md"
echo "  Registered installs: $HOME/.plat/installations.json"
echo
echo "The upstream Skills CLI owns the coding-agent catalog and install paths."
echo "Update checks run every 2 hours outside engineering sessions."
echo "Re-running this installer from any supported agent can synchronize all registered Plat groups."
