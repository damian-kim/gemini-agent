# Skill: update-tasks

Purpose: Extract, normalize, and update tasks from human notes and project files.

Read:
- `TASKS.md`
- `domains/personal-os/inputs/inbox.md`
- `domains/personal-os/inputs/projects.md`
- `domains/personal-os/data/projects.json`
- `memory/personal-os/open-threads.md`
- `domains/personal-os/outputs/plans/plan-*.md`

Write:
- `domains/personal-os/data/tasks.json`
- `dashboard/dashboard.json`

Optional write with explicit approval:
- `TASKS.md`

CRITICAL: never write to any `inputs/` directory.

Task fields:
- id
- title
- status
- priority
- domain
- project_id
- due_date
- next_action
- source
- created_at
- updated_at
- blocked_by
- notes

Rules:
- Preserve existing stable task IDs.
- Dedupe by normalized title and source path.
- Do not invent due dates.
- Mark vague tasks as needing clarification instead of expanding them into false specifics.
- If changing `TASKS.md`, show a diff and require approval unless the user explicitly asked for the update.
