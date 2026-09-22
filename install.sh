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

If agent/scope are omitted, the installer asks interactively.
EOF
}

ask_agent() {
  echo
  echo "Choose your coding agent:"
  echo "  1. Claude Code"
  echo "  2. Codex"
  echo "  3. Cursor"
  read -r -p "> " choice
  case "${choice:-1}" in
    1) AGENT="claude-code" ;;
    2) AGENT="codex" ;;
    3) AGENT="cursor" ;;
    *) echo "Invalid choice." >&2; exit 2 ;;
  esac
}

ask_scope() {
  echo
  echo "Install scope:"
  echo "  1. Global — use Plat across projects"
  echo "  2. Project — use Plat only in this project"
  read -r -p "> " choice
  case "${choice:-1}" in
    1) SCOPE="global" ;;
    2) SCOPE="project" ;;
    *) echo "Invalid choice." >&2; exit 2 ;;
  esac
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
If the Plat developer profile is missing in an interactive session, complete Plat onboarding before substantive engineering work.
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
If the Plat developer profile is missing in an interactive session, complete Plat onboarding before substantive engineering work.
EOF
  echo "✓ Added Plat Cursor rule: $file"
}

wire_agent() {
  if [[ "$SCOPE" == "global" ]]; then
    case "$AGENT" in
      claude-code) append_block "${HOME}/.claude/CLAUDE.md" ;;
      codex) append_block "${HOME}/.codex/AGENTS.md" ;;
      cursor) install_cursor_rule "${HOME}/.cursor/rules/plat.mdc" ;;
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
echo "PLAT · INSTALL"
echo "Agent: $AGENT"
echo "Scope: $SCOPE"
echo

INSTALL_ARGS=(skills add "$REPO" --skill plat -a "$AGENT" -y)
if [[ "$SCOPE" == "global" ]]; then
  INSTALL_ARGS+=(-g)
fi

npx "${INSTALL_ARGS[@]}"

tmp_setup="$(mktemp)"
trap 'rm -f "$tmp_setup"' EXIT
curl -fsSL "${RAW_BASE}/skills/plat/scripts/setup.py" -o "$tmp_setup"

SETUP_ARGS=()
if [[ "$RECONFIGURE" -eq 1 ]]; then
  SETUP_ARGS+=(--force)
fi
python3 "$tmp_setup" "${SETUP_ARGS[@]}"

wire_agent

echo
echo "✓ Plat is ready."
echo
echo "Ask normally, or explicitly invoke Plat when your agent supports it."
echo
echo "Update check: npx skills check"
if [[ "$SCOPE" == "global" ]]; then
  echo "Update:       npx skills update plat -g"
else
  echo "Update:       npx skills update plat -p"
fi
