# Skill: create-prd

Purpose: Create a build-ready PRD for a project idea.

Inputs:
- User's project idea or selected notes.
- Optional domain, build length, constraints, and target environment.

Read:
- `AGENTS.md`
- `domains/personal-os/AGENTS.md`
- `memory/terminology.md`
- `domains/personal-os/data/projects.json`
- `domains/personal-os/inputs/projects.md`

Write:
- `domains/personal-os/outputs/prds/PRD-{slug}-YYYY-MM-DD.md`

CRITICAL: never write to any `inputs/` directory.

PRD sections:
1. Executive summary
2. Problem and context
3. Goals and non-goals
4. Users and use cases
5. Requirements
6. Architecture / approach
7. Data model
8. Build plan
9. Risks and guardrails
10. Open questions

Rules:
- Prefer concrete decisions over abstract prose.
- Include assumptions when information is missing.
- Do not ask more than one clarification unless absolutely necessary.
- If the request is buildable with current context, make reasonable assumptions and produce the PRD.
