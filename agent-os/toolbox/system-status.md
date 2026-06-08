# Skill: system-status

Purpose: Report current system health and data-layer status.

Read:
- `domains/personal-os/data/system-health.json`
- `dashboard/dashboard.json`
- `runtime/logs/` summaries if available
- App health endpoint if running

Write:
- `domains/personal-os/data/system-health.json`
- `domains/personal-os/outputs/reports/system-status-YYYY-MM-DD.md`
- `dashboard/dashboard.json`

CRITICAL: never write to any `inputs/` directory.

Report:
1. App status
2. Gemini config status
3. Data-layer status
4. Dashboard status
5. Brief status
6. Deployment status
7. Risks
8. Recommended next action
