# personal-os Domain Instructions

Purpose: coordinate Damian's tasks, project plans, briefs, system state, and Agent OS operating memory.

Tone: direct, useful, and concise. Prefer concrete next actions over vague productivity advice.

Allowed actions:
- Read `inputs/`, `data/`, `outputs/`, `memory/`, `TASKS.md`, and `AGENTS.md`.
- Write generated plans, reports, and PRDs to `outputs/`.
- Refresh derived JSON files in `data/`.
- Append approved durable context to `memory/personal-os/`.

Forbidden without explicit `proceed`:
- Delete files.
- Overwrite human-maintained inputs.
- Send messages externally.
- Run shell commands on production.
- Modify secrets or deployment credentials.

CRITICAL: Automated refresh tasks must never write to `domains/personal-os/inputs/`.
