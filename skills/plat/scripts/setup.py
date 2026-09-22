#!/usr/bin/env python3
"""Interactive developer-preference onboarding for Plat."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROFILE_VERSION = "2"

ROLE_OPTIONS = [
    ("backend", "Backend"),
    ("frontend", "Frontend"),
    ("fullstack", "Full-stack"),
    ("mobile", "Mobile"),
    ("ai", "AI / ML"),
    ("design", "Design / UI-UX"),
    ("platform", "Platform / DevOps"),
    ("data", "Data"),
]

EXPERIENCE_OPTIONS = [
    ("beginner", "Beginner"),
    ("intermediate", "Intermediate"),
    ("advanced", "Advanced"),
]

RESPONSE_OPTIONS = [
    ("concise", "Concise — act first, explain only what matters"),
    ("balanced", "Balanced — compact reasoning + implementation"),
    ("explanatory", "Explanatory — teach important concepts while working"),
]


def choose(title: str, options: list[tuple[str, str]], default_index: int = 0) -> str:
    print(f"\n{title}")
    for i, (_, label) in enumerate(options, start=1):
        suffix = " [default]" if i - 1 == default_index else ""
        print(f"  {i}. {label}{suffix}")

    while True:
        raw = input("> ").strip()
        if not raw:
            return options[default_index][0]
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1][0]
        values = {value for value, _ in options}
        if raw.lower() in values:
            return raw.lower()
        print(f"Choose 1-{len(options)}.")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create or update the Plat developer preference profile.")
    p.add_argument("--profile", help="Override profile path (mainly for testing).")
    p.add_argument("--role", choices=[x[0] for x in ROLE_OPTIONS])
    p.add_argument("--experience", choices=[x[0] for x in EXPERIENCE_OPTIONS])
    p.add_argument("--response", choices=[x[0] for x in RESPONSE_OPTIONS])
    p.add_argument("--stack", default=None, help="Optional comma-separated familiar technologies.")
    p.add_argument("--force", action="store_true", help="Replace an existing profile.")
    p.add_argument("--non-interactive", action="store_true", help="Require all profile choices as flags.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    path = Path(args.profile).expanduser() if args.profile else Path.home() / ".plat" / "profile.md"

    if path.exists() and not args.force:
        print(f"✓ Existing Plat preferences kept: {path}")
        print("  Re-run setup with --force only when you want to change them.")
        return 0

    if args.non_interactive:
        missing = [name for name, value in [
            ("--role", args.role),
            ("--experience", args.experience),
            ("--response", args.response),
        ] if value is None]
        if missing:
            print("Missing required non-interactive options: " + ", ".join(missing), file=sys.stderr)
            return 2

    print("\nPLAT · DEVELOPER PREFERENCES")
    print("Three quick choices. They personalize assistance; they never force architecture or reasoning depth.")
    print("Plat always prefers the lowest-cost path that preserves correctness.")

    role = args.role or choose("1/3 — What best describes your primary work?", ROLE_OPTIONS, 2)
    experience = args.experience or choose("2/3 — Your overall engineering experience?", EXPERIENCE_OPTIONS, 1)
    response = args.response or choose("3/3 — How should Plat communicate?", RESPONSE_OPTIONS, 0)

    if args.stack is None and not args.non_interactive:
        stack = input("\nOptional — familiar technologies (comma-separated, Enter to skip):\n> ").strip()
    else:
        stack = (args.stack or "").strip()

    response_desc = {
        "concise": "concise; skip fundamentals unless requested",
        "balanced": "balanced; explain decisions that materially affect the task",
        "explanatory": "explanatory; teach important concepts while working",
    }[response]

    lines = [
        "# Plat Developer Profile",
        "",
        f"Profile schema: {PROFILE_VERSION}",
        "",
        "## Role",
        f"Primary: {role}",
        "",
        "## Experience",
        f"Overall: {experience}",
        "",
        "## Assistance",
        f"Default response: {response}",
        f"Explanation: {response_desc}",
        "",
        "## Efficiency",
        "- Correctness and required safety/compatibility come first.",
        "- After that, minimize total tokens, tool calls, wall time, rereads, and repair work.",
        "- Developer requests for deep/detailed output do not force Deep specialist routing when the task does not need it.",
        "",
    ]

    if stack:
        lines.extend([
            "## Familiar stack",
            stack,
            "",
        ])

    lines.extend([
        "## Guardrails",
        "- Current repository evidence and explicit developer requirements override this profile.",
        "- Familiar technologies are explanation context, not architecture mandates.",
        "- Do not store secrets, credentials, customer data, or unrelated personal information here.",
        "",
    ])

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")

    print(f"\n✓ Plat preferences saved: {path}")
    print("  Install onboarding creates only this developer profile; no project profile is created.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
