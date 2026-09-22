<div align="center">

<img src="assets/plat-team.svg" alt="Plat adaptive engineering team" width="100%" />

</div>

<img src="assets/plat-activate.svg" alt="Set Plat once globally or per project, then use it normally or invoke it explicitly" width="100%" />

## Copy setup

```bash
# Claude Code — global
npx skills add harish-042002/harish-skills --skill plat -g -a claude-code -y

# Codex — global
npx skills add harish-042002/harish-skills --skill plat -g -a codex -y

# Cursor — global
npx skills add harish-042002/harish-skills --skill plat -g -a cursor -y
```

Add this once to your global or project `CLAUDE.md`, `AGENTS.md`, or agent-equivalent:

```text
For software engineering requests, use the installed Plat skill.
```

Explicit use where slash-skill invocation is supported:

```text
/plat <your engineering request>
```

Portable fallback:

```text
Use Plat: <your engineering request>
```

> Remove `-g` for a project-local install.

<img src="assets/plat-flow.svg" alt="How one engineering request moves through Plat" width="100%" />

<img src="assets/plat-roster.svg" alt="Plat specialist engineering team roster" width="100%" />

<img src="assets/plat-evidence.svg" alt="Plat benchmark evidence board with all ten pilot cases" width="100%" />

<img src="assets/plat-regression.svg" alt="Plat regression benchmark scenarios" width="100%" />

<img src="assets/plat-license.svg" alt="Plat is released under the MIT License" width="100%" />
