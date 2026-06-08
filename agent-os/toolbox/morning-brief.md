# Skill: morning-brief

Purpose: Generate Damian's daily operating brief.

Read these files:
- `AGENTS.md`
- `TASKS.md`
- `memory/people.md`
- `memory/terminology.md`
- `memory/personal-os/context.md`
- `memory/personal-os/open-threads.md`
- `domains/personal-os/data/tasks.json`
- `domains/personal-os/data/projects.json`
- `domains/personal-os/data/decisions.json`
- `domains/personal-os/data/system-health.json`

Write these files:
- `briefs/latest.md`
- `briefs/archive/brief-YYYY-MM-DD.md`
- `domains/personal-os/data/brief-state.json`
- `dashboard/dashboard.json`

CRITICAL: never write to any `inputs/` directory.

Output sections:
1. Today focus
2. Top priorities
3. Blockers / risks
4. Open threads
5. Suggested next actions
6. System health
7. Files used

Rules:
- Be direct and concise.
- Prioritize tasks with high priority, blockers, or recent updates.
- Do not invent deadlines.
- If data is missing, say what is missing and propose the next data-capture step.
- Keep the brief useful enough to act on in under 5 minutes.
