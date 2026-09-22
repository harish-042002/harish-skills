# Harish Skills

Reusable AI coding-agent skills maintained by Harish.

## Plat

Plat is a backend-first engineering operating layer for coding agents. It routes natural-language engineering requests to focused guidance for repository understanding, planning, debugging, testing, backend/API/database work, security, performance, CI/CD and delivery, frontend/mobile, AI engineering, and bounded subagent delegation.

Current frozen pre-runtime benchmark release: **v0.4.0**.

Source: `skills/plat/`

Plat is designed to stay token-efficient: a small `SKILL.md` control plane loads only the reference modules relevant to the current task.

v0.4.0 was hardened through 25 adversarial review rounds (112 deterministic assertions) plus a frozen 100-prompt pre-runtime corpus. Real with-vs-without-Plat coding-agent A/B remains the next benchmark stage.
