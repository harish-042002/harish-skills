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
  bash install.sh [--agent claude-code|codex|cursor] [--scope global|project] [--reconfigure]

The installer:
  1. installs Plat into the selected agent using direct copy mode,
  2. verifies SKILL.md exists in the agent's real skill directory,
  3. runs one-time developer preference onboarding and creates only ~/.plat/profile.md,
  4. wires Plat into the agent instructions,
  5. registers one user-level daily background release check.

Re-running this installer updates Plat while preserving existing preferences and the daily checker.
EOF
}

ask_agent() {
  local choice raw_choice
  while true; do
    echo
    echo "Choose your coding agent:"
    echo "  1. Claude Code"
    echo "  2. Codex"
    echo "  3. Cursor"
    read -r -p "> " raw_choice || exit 1

    if [[ -z "$raw_choice" ]]; then
      choice="1"
    else
      # macOS terminals may send literal arrow-key escape sequences to plain Bash read.
      # Keep a trailing numeric choice when present; otherwise re-prompt.
      choice="${raw_choice##*[!0-9]}"
    fi

    case "$choice" in
      1) AGENT="claude-code"; return 0 ;;
      2) AGENT="codex"; return 0 ;;
      3) AGENT="cursor"; return 0 ;;
      *) echo "Please enter 1, 2, or 3." >&2 ;;
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

expected_skill_dir() {
  if [[ "$SCOPE" == "global" ]]; then
    case "$AGENT" in
      claude-code) printf '%s\n' "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/plat" ;;
      codex) printf '%s\n' "${CODEX_HOME:-$HOME/.codex}/skills/plat" ;;
      cursor) printf '%s\n' "$HOME/.cursor/skills/plat" ;;
    esac
  else
    case "$AGENT" in
      claude-code) printf '%s\n' "$(pwd)/.claude/skills/plat" ;;
      codex|cursor) printf '%s\n' "$(pwd)/.agents/skills/plat" ;;
    esac
  fi
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

wire_agent() {
  if [[ "$SCOPE" == "global" ]]; then
    case "$AGENT" in
      claude-code) append_block "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/CLAUDE.md" ;;
      codex) append_block "${CODEX_HOME:-$HOME/.codex}/AGENTS.md" ;;
      cursor) install_cursor_rule "$HOME/.cursor/rules/plat.mdc" ;;
    esac
  else
    case "$AGENT" in
      claude-code) append_block "$(pwd)/CLAUDE.md" ;;
      codex|cursor) append_block "$(pwd)/AGENTS.md" ;;
    esac
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

case "$AGENT" in
  claude-code|codex|cursor) ;;
  *) echo "Unsupported agent: $AGENT" >&2; exit 2 ;;
esac
case "$SCOPE" in
  global|project) ;;
  *) echo "Unsupported scope: $SCOPE" >&2; exit 2 ;;
esac

echo
echo "PLAT · INSTALL / UPDATE"
echo "Agent: $AGENT"
echo "Scope: $SCOPE"
echo

INSTALL_ARGS=(-y skills@latest add "$REPO" --skill plat -a "$AGENT" --copy -y)
if [[ "$SCOPE" == "global" ]]; then
  INSTALL_ARGS+=(-g)
fi

npx "${INSTALL_ARGS[@]}"

SKILL_DIR="$(expected_skill_dir)"
if [[ ! -f "$SKILL_DIR/SKILL.md" ]]; then
  echo >&2
  echo "Plat install verification failed." >&2
  echo "Expected: $SKILL_DIR/SKILL.md" >&2
  echo "Nothing else was configured. Re-run the installer after checking the error above." >&2
  exit 1
fi

echo "✓ Verified Plat skill: $SKILL_DIR/SKILL.md"

tmp_setup="$(mktemp)"
trap 'rm -f "$tmp_setup"' EXIT
curl -fsSL "${RAW_BASE}/skills/plat/scripts/setup.py" -o "$tmp_setup"

# Avoid expanding an empty Bash array here. macOS still ships Bash 3.2,
# where set -u can treat an empty array expansion as an unbound variable.
if [[ "$RECONFIGURE" -eq 1 ]]; then
  python3 "$tmp_setup" --force
else
  python3 "$tmp_setup"
fi

wire_agent

UPDATE_CHECKER="$SKILL_DIR/scripts/update_check.py"
if [[ -f "$UPDATE_CHECKER" ]]; then
  python3 "$UPDATE_CHECKER" --register "$SKILL_DIR" --agent "$AGENT" --scope "$SCOPE" || true
else
  echo "Warning: Plat daily update checker not found at $UPDATE_CHECKER" >&2
fi

echo
echo "✓ Plat is ready."
echo "  Developer profile: $HOME/.plat/profile.md"
echo "  Skill:       $SKILL_DIR"
echo
echo "Ask normally. Plat decides the smallest useful mode, depth, and specialist team."
echo "Daily update checks run outside engineering sessions and notify only when a newer release exists."
echo
echo "To install an available update, re-run this same installer command."
