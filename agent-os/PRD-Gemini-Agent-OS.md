# PRD: Gemini Agent OS on VS Code and Oracle Cloud VPS

Status: Build-ready v0.1
Owner: Damian Kim
Target environment: VS Code locally, Gemini API as model runtime, Oracle Cloud Infrastructure Ampere A1 Flex VPS for hosting
Timezone: America/Chicago
Assumed first build window: 8 hours
Primary domain in v0: personal-os
Deferred placeholder domains: code-projects, school, career

## Source basis and adaptation notes

This PRD adapts the uploaded Cowork/Claude operating-system prompt into a non-Cowork stack. The durable concepts retained are:

- PRD-first building before non-trivial implementation.
- Local data layer as the source of truth.
- Root operating instructions and per-domain instructions.
- Human-maintained inputs, machine-refreshed data, generated outputs.
- Continuous note-taking, decision capture, and open-thread tracking.
- Scheduled briefs, dashboard, and on-demand skills.
- Explicit approval before destructive, irreversible, financial, communication, or bulk actions.

The Cowork-only concepts replaced are:

- `CLAUDE.md` becomes `AGENTS.md`.
- Cowork Productivity plugin setup becomes `scripts/init_workspace.py` and `make init`.
- Cowork `/start` becomes local repo initialization.
- Cowork `/update` becomes `python -m app.workflows.update_tasks`.
- Cowork custom skills become Markdown skill specs in `toolbox/` plus Python tool handlers in `app/tools/`.
- Cowork scheduling becomes systemd timers or cron on the Oracle VPS.

External implementation references current at PRD creation:

- Gemini Code Assist / Gemini CLI docs: https://developers.google.com/gemini-code-assist/docs/gemini-cli
- Gemini function calling docs: https://ai.google.dev/gemini-api/docs/function-calling
- Gemini structured output docs: https://ai.google.dev/gemini-api/docs/structured-output
- Google Gen AI Python SDK docs: https://googleapis.github.io/python-genai/
- OCI compute shapes docs: https://docs.oracle.com/en-us/iaas/Content/Compute/References/computeshapes.htm

---

## 1. Executive summary

Gemini Agent OS is a self-hosted personal AI operating system. It runs as a local-first repo developed in VS Code, uses Gemini through the Google Gen AI SDK, and is hosted on an Oracle Cloud Infrastructure Ampere A1 Flex VPS. It recreates the useful Cowork architecture without depending on Claude Cowork.

The v0 system covers one fully built domain:

| Domain | Purpose | v0 scope |
|---|---|---|
| `personal-os` | Coordinate tasks, notes, project planning, morning briefs, and agent memory. | Fully built. |

It creates placeholder folders for later domains:

| Deferred domain | Future purpose |
|---|---|
| `code-projects` | Track repositories, build plans, bugs, deployment notes, and coding-agent tasks. |
| `school` | Track academic deadlines, course notes, assignments, and study plans. |
| `career` | Track applications, networking, resumes, interview prep, and opportunities. |

The system exposes three interaction patterns in v0:

| Pattern | Implementation | Purpose |
|---|---|---|
| Dashboard | `dashboard/index.html` plus `dashboard/dashboard.json` | Always-on snapshot of status, tasks, brief, and system health. |
| Brief/digest | `app/workflows/morning_brief.py` | Scheduled morning summary written to `briefs/latest.md` and archive. |
| Skill | Markdown specs in `toolbox/` plus `/run-skill` API endpoint | On-demand actions such as PRD creation, project planning, task extraction, and deploy checks. |

Autonomous builder is deliberately excluded from v0. The v0 objective is to build a stable, inspectable core: data layer, Gemini runtime, skill execution, morning brief, dashboard, and VPS deployment. A brittle autonomous builder would add too much surface area before the safety and audit model is proven.

The build is sized as an 8-hour MVP because a hosted agent needs more than a folder skeleton: it needs API setup, local data model, service deployment, dashboard, scheduled jobs, and guardrails. If time runs short, cut the dashboard polish and nonessential skills before cutting the data layer or morning brief.

---

## 2. Quick start: moving this into VS Code and Oracle VPS

### 2.1 What you do first

1. Open VS Code.
2. Create a local project folder:

```bash
mkdir -p ~/agent-os
cd ~/agent-os
git init
```

3. Save this PRD as:

```text
~/agent-os/PRD-Gemini-Agent-OS.md
```

4. Install or enable:
   - VS Code.
   - Python 3.12+.
   - Docker and Docker Compose.
   - Gemini Code Assist extension for VS Code.
   - Gemini CLI if you want terminal-based coding assistance.
   - An Oracle Cloud Infrastructure account with an Ampere A1 Flex instance.
   - A Gemini API key.

### 2.2 Project instructions to paste into Gemini Code Assist / Gemini CLI

Paste this as the project-level instruction or first message to the coding agent:

```md
You are helping build Damian's Gemini Agent OS.

Read `PRD-Gemini-Agent-OS.md` before making structural changes. Treat it as the authoritative architecture and build plan.

Default style: rigorous, direct, no fluff. Push back on vague or risky requests. Do not silently overwrite contradictory instructions.

Build rules:
1. Work block by block from Section 7 of the PRD.
2. Start with Block 0.
3. After each block, report files changed, commands run, tests/checks passed, and open issues.
4. Wait for Damian's go-ahead before starting the next block.
5. Never write to any `inputs/` directory from automated refresh tasks.
6. Before deleting, overwriting, sending messages, making financial actions, or running bulk operations, show the plan and wait for explicit `proceed`.
7. Use `AGENTS.md`, `TASKS.md`, `memory/`, `domains/*/AGENTS.md`, `toolbox/`, `briefs/`, and `dashboard/` exactly as defined in the PRD.
8. Keep secrets out of Git. Use `.env` locally and environment variables in production.
9. Target timezone is America/Chicago.
10. Target host is Oracle Cloud Infrastructure Ampere A1 Flex, so Docker images and dependencies must work on linux/arm64.
```

### 2.3 How to run the build

The build agent should assume nothing is set up yet. When told to start, it must:

1. Run Block 0 from Section 7.
2. Verify local prerequisites.
3. Create the repo structure.
4. Create root operating files.
5. Install dependencies.
6. Build and test each block in order.
7. Report completion after each block and wait for approval before continuing.

### 2.4 The first thing you say in VS Code / Gemini CLI

```text
Start building Gemini Agent OS. Begin with Block 0 of PRD-Gemini-Agent-OS.md. Do not skip ahead. After Block 0, report what changed and wait for my go-ahead.
```

---

## 3. Goals and non-goals

### 3.1 Goals

| Goal | Success criteria |
|---|---|
| Local-first agent workspace | Repo contains stable folders, operating instructions, data files, memory files, skill specs, and dashboard files. |
| Gemini-powered agent backend | FastAPI service accepts chat and skill requests, loads relevant context, calls Gemini, and returns grounded outputs. |
| Safe file-backed memory | Agent can read and update allowed memory/task files while respecting `inputs/` as human-maintained. |
| Morning brief | Scheduled workflow produces `briefs/latest.md`, archives date-stamped briefs, and updates dashboard JSON. |
| Dashboard | Local/static dashboard displays tasks, latest brief summary, system health, and recent decisions. |
| VPS deployment | App runs on Oracle Ampere A1 Flex through Docker Compose and restarts automatically. |
| Explicit guardrails | Destructive actions require plan plus explicit `proceed`. Secrets are not committed. |

### 3.2 Non-goals for v0

| Non-goal | Why excluded |
|---|---|
| Autonomous builder that modifies arbitrary repos | Too risky before audit, test, rollback, and permission model are proven. |
| Gmail, Calendar, Notion, Slack connectors | Each connector adds auth, scopes, privacy, rate limits, and failure modes. Add after core is stable. |
| Multi-user auth system | v0 is personal. Use private network or simple auth first. |
| Local LLM inference | Oracle A1 Flex is useful for orchestration, not heavy local inference. Gemini handles inference remotely. |
| Vector database | Not needed until memory grows beyond simple files. Start inspectable. |
| Mobile app | Dashboard and API are sufficient for v0. |
| Financial automation or sending communications | High-risk actions require later, explicit workflows and approval gates. |

---

## 4. Architecture overview

### 4.1 Three layers

| Layer | Concrete implementation | Role |
|---|---|---|
| Local data layer | Plain files under `~/agent-os/` plus optional runtime SQLite audit DB | Source of truth for memory, tasks, briefs, skills, and generated state. |
| Agent application | Python FastAPI app in `app/` using Google Gen AI SDK | Loads context, calls Gemini, executes allowed tools, writes outputs. |
| Hosted runtime | Docker Compose on OCI Ampere A1 Flex with systemd and Caddy/Nginx | Keeps service online, exposes private/public HTTPS, runs scheduled workflows. |

### 4.2 Core runtime flow

```text
User or scheduled trigger
  -> FastAPI endpoint or CLI workflow
  -> Context loader reads AGENTS.md, domain AGENTS.md, memory, TASKS.md, data files
  -> Gemini call with system instruction, user request, relevant files, and tool declarations
  -> Tool call if needed
  -> Guardrail check before any write/destructive action
  -> Output to user plus allowed file writes
  -> Audit log entry
```

### 4.3 Interaction patterns

| Pattern | v0 component | Reads | Writes |
|---|---|---|---|
| Dashboard | `dashboard/index.html`, `app/tools/dashboard.py` | `dashboard/dashboard.json` | None from browser; refresh writes JSON. |
| Brief/digest | `app/workflows/morning_brief.py` | `TASKS.md`, memory files, domain data | `briefs/latest.md`, `briefs/archive/brief-YYYY-MM-DD.md`, `dashboard/dashboard.json` |
| Skill | `/run-skill`, `toolbox/*.md` | Skill spec plus allowed context files | Skill-specific outputs under `domains/*/outputs/` or `briefs/` |
| Data refresh | `app/workflows/refresh_data.py` | `inputs/`, memory, task files | `data/` files only |

### 4.4 Three-tier memory architecture

| Tier | File/folder | Purpose |
|---|---|---|
| Root operating memory | `AGENTS.md` | Cross-cutting behavior, safety rules, workflow rules, global preferences. |
| Deep memory | `memory/people.md`, `memory/terminology.md`, `memory/{domain}/` | Durable facts, definitions, recurring context, long-lived notes. |
| Domain role memory | `domains/{domain}/AGENTS.md` | Domain-specific role, tone, file ownership, allowed actions, and output preferences. |

### 4.5 Key architectural decisions

| Decision | Tension | Choice |
|---|---|---|
| Direct Gemini API instead of Gemini CLI runtime | CLI is convenient but harder to secure as a production service. | Use CLI/Code Assist for development; use Google Gen AI SDK in backend. |
| Files before database | DBs are robust but less transparent for a personal OS. | Use files for source of truth; optional SQLite only for audit/runtime logs. |
| One built domain | Many domains are tempting, but broad v0 systems become thin and broken. | Fully build `personal-os`; create placeholders for future domains. |
| No connectors in v0 | Connectors increase value but add auth complexity. | Stub connector interfaces; add one connector at a time later. |
| Dashboard as static UI | React app would be nicer but heavier. | Use simple HTML/JS reading `dashboard.json`. |
| Scheduled jobs through systemd/cron | App-native scheduler is easier, but less reliable after restarts. | Use systemd timers or cron on VPS. |

---

## 5. The data layer: foundation

### 5.1 Where it lives

The data layer lives in a local folder:

```text
~/agent-os/
```

On the VPS, it is mounted at:

```text
/data/agent-os/
```

Connectors, when added later, are sources or destinations. They are not the storage layer. The agent never creates a Google Drive or Notion folder as the canonical data layer.

### 5.2 Folder tree

```text
~/agent-os/                                  # Project root and local data layer
├── AGENTS.md                               # Root operating instructions and global behavior rules
├── TASKS.md                                # Human-readable active task list
├── PRD-Gemini-Agent-OS.md                  # Authoritative build PRD
├── README.md                               # Local setup and usage guide
├── pyproject.toml                          # Python dependencies and tooling config
├── Makefile                                # Common commands: init, dev, test, brief, deploy-check
├── .env.example                            # Example environment variables; no real secrets
├── .gitignore                              # Prevents secrets, logs, runtime DB, and cache from Git
├── app/                                    # FastAPI app, Gemini orchestration, tools, workflows
│   ├── __init__.py                         # Python package marker
│   ├── main.py                             # FastAPI entrypoint
│   ├── agent.py                            # Gemini client and tool orchestration
│   ├── config.py                           # Environment and path settings
│   ├── context.py                          # Context loader for instructions, memory, tasks, data
│   ├── guardrails.py                       # Permission checks and destructive-action gates
│   ├── audit.py                            # Runtime audit logging
│   ├── prompts.py                          # System prompt builders
│   ├── schemas/                            # Pydantic schemas for structured outputs
│   │   ├── agent_response.py               # Chat and tool-call response schemas
│   │   ├── task.py                         # Task extraction/update schema
│   │   ├── brief.py                        # Morning brief schema
│   │   ├── dashboard.py                    # Dashboard JSON schema
│   │   └── skill.py                        # Skill request/result schema
│   ├── tools/                              # Safe tool implementations exposed to the agent
│   │   ├── filesystem.py                   # Controlled read/write helpers
│   │   ├── tasks.py                        # TASKS.md and tasks.json helpers
│   │   ├── memory.py                       # Memory append/update helpers
│   │   ├── brief.py                        # Brief rendering helpers
│   │   ├── dashboard.py                    # Dashboard JSON refresh helpers
│   │   └── status.py                       # System health checks
│   └── workflows/                          # Scheduled and manual workflows
│       ├── refresh_data.py                 # Refresh derived data files
│       ├── update_tasks.py                 # Extract and normalize tasks
│       ├── morning_brief.py                # Generate daily brief
│       └── deploy_check.py                 # Check VPS deployment health
├── memory/                                 # Durable cross-domain memory
│   ├── people.md                           # People, roles, relationship context
│   ├── terminology.md                      # Shorthand, recurring terms, naming conventions
│   └── personal-os/                        # Deep memory for the built domain
│       ├── context.md                      # Stable facts about how this OS should behave
│       ├── decisions.md                    # Long-lived decisions and rationale
│       └── open-threads.md                 # Ongoing questions and threads to revisit
├── toolbox/                                # Skill specs; source of truth for on-demand commands
│   ├── create-prd.md                       # Skill: create PRD for a project
│   ├── plan-project.md                     # Skill: turn vague idea into concrete plan
│   ├── update-tasks.md                     # Skill: extract/update tasks from notes
│   ├── morning-brief.md                    # Skill: manual brief generation
│   ├── system-status.md                    # Skill: inspect app/data/deploy health
│   └── deploy-check.md                     # Skill: deployment checklist and health report
├── briefs/                                 # Brief outputs
│   ├── latest.md                           # Most recent morning brief
│   └── archive/                            # Date-stamped archived briefs
├── dashboard/                              # Static dashboard assets and data
│   ├── index.html                          # Browser dashboard
│   ├── dashboard.json                      # Machine-refreshed dashboard data
│   └── assets/                             # Optional CSS/JS assets
├── domains/                                # One folder per domain
│   ├── personal-os/                        # Fully built v0 domain
│   │   ├── AGENTS.md                       # Domain-specific instructions
│   │   ├── inputs/                         # Human-maintained files; never auto-overwritten
│   │   │   ├── inbox.md                    # Scratchpad for human notes and requests
│   │   │   ├── projects.md                 # Human list of projects and desired outcomes
│   │   │   └── routines.md                 # Human-maintained routines and preferences
│   │   ├── data/                           # Machine-refreshed derived data
│   │   │   ├── tasks.json                  # Normalized active tasks
│   │   │   ├── projects.json               # Normalized project state
│   │   │   ├── decisions.json              # Structured decision log
│   │   │   ├── brief-state.json            # Last brief metadata and summary state
│   │   │   └── system-health.json          # Latest health/deploy check summary
│   │   └── outputs/                        # Generated artifacts
│   │       ├── plans/                       # Generated plans
│   │       ├── prds/                        # Generated PRDs
│   │       └── reports/                     # Generated reports
│   ├── code-projects/                       # Placeholder future domain
│   │   ├── AGENTS.md                       # Future domain instructions
│   │   ├── inputs/                         # Human-maintained future inputs
│   │   ├── data/                           # Future derived code-project data
│   │   └── outputs/                        # Future generated code-project artifacts
│   ├── school/                              # Placeholder future domain
│   │   ├── AGENTS.md                       # Future domain instructions
│   │   ├── inputs/                         # Human-maintained future academic inputs
│   │   ├── data/                           # Future derived academic data
│   │   └── outputs/                        # Future generated academic artifacts
│   └── career/                              # Placeholder future domain
│       ├── AGENTS.md                       # Future domain instructions
│       ├── inputs/                         # Human-maintained future career inputs
│       ├── data/                           # Future derived career data
│       └── outputs/                        # Future generated career artifacts
├── runtime/                                # Not committed; runtime logs and audit DB
│   ├── agent.db                            # SQLite audit/runtime DB
│   └── logs/                               # App logs
├── scripts/                                # Setup, backup, and deploy scripts
│   ├── init_workspace.py                   # Creates folders and seed files idempotently
│   ├── backup.sh                           # Creates timestamped backup archive
│   └── restore.sh                          # Restores from backup with explicit approval
└── deploy/                                 # Deployment config
    ├── Dockerfile                          # ARM64-compatible Python app image
    ├── docker-compose.yml                  # App plus reverse proxy
    ├── caddy/Caddyfile                     # Optional HTTPS reverse proxy config
    ├── systemd/agent-os.service            # systemd unit for compose stack
    ├── systemd/morning-brief.service       # systemd service for daily brief
    └── systemd/morning-brief.timer         # systemd timer for daily brief
```

### 5.3 Inputs vs data vs outputs

| Folder type | Who writes | Automation rule |
|---|---|---|
| `inputs/` | Human only | Never auto-overwrite. Automated jobs may read only. |
| `data/` | Workflows | Machine-refreshed. Must be reproducible from inputs, memory, or external sources. |
| `outputs/` | Skills/workflows | Generated artifacts. May be regenerated with date-stamped filenames. |
| `memory/` | Human or approved agent writes | Durable context. Agent may append when asked or after explicit approval. |
| `runtime/` | App only | Logs, audit, cache. Not committed. |

### 5.4 Memory files

#### `memory/people.md`

Purpose: stable people context. Keep lean and useful.

Seed:

```md
# People

## Damian Kim
- Owner of this Gemini Agent OS.
- Timezone: America/Chicago.
- Works in VS Code and wants Gemini instead of Claude/Cowork for this build.
- Hosting target: Oracle Cloud Infrastructure Ampere A1 Flex VPS.

## Rules
- Do not infer sensitive personal facts unless Damian explicitly states them.
- Add people only when useful for future workflows.
```

#### `memory/terminology.md`

Purpose: recurring shorthand.

Seed:

```md
# Terminology

- Agent OS: the self-hosted Gemini-powered personal operating system in this repo.
- Data layer: local files under `~/agent-os/`, not a cloud connector.
- Inputs: human-maintained files that automation must never overwrite.
- Data: machine-refreshed derived files.
- Outputs: generated artifacts such as briefs, reports, plans, and PRDs.
- Proceed: explicit approval word required before destructive or irreversible actions.
```

#### `memory/personal-os/context.md`

Seed:

```md
# Personal OS Context

This domain coordinates tasks, notes, projects, briefs, and system operation.
The system should prefer clear written plans, auditable file changes, and reversible actions.
The first production target is a hosted FastAPI app on Oracle Ampere A1 Flex using Gemini through the Google Gen AI SDK.
```

#### `memory/personal-os/decisions.md`

Seed:

```md
# Decisions

- Use `AGENTS.md` instead of `CLAUDE.md` because the target stack is Gemini/VS Code rather than Claude/Cowork.
- Use direct Gemini API calls for production rather than Gemini CLI because API calls are easier to secure, log, and constrain.
- Use local files as source of truth before introducing databases or external connectors.
```

#### `memory/personal-os/open-threads.md`

Seed:

```md
# Open Threads

- Which external connector should be added first after v0: Gmail, Google Calendar, Notion, GitHub, or something else?
- Should the production app be exposed publicly with HTTPS or kept private through Tailscale/VPN?
- Which domain should be built next after personal-os: code-projects, school, or career?
```

### 5.5 Data file schemas

#### `domains/personal-os/data/tasks.json`

Overwrite strategy: rewritten by `update_tasks.py` after reading `TASKS.md`, `inputs/inbox.md`, and relevant outputs. Preserve stable IDs. Dedupe by normalized title plus source path.

```json
{
  "schema_version": "1.0",
  "updated_at": "2026-06-07T09:00:00-05:00",
  "tasks": [
    {
      "id": "task_20260607_001",
      "title": "Deploy Gemini Agent OS MVP to Oracle VPS",
      "status": "active",
      "priority": "high",
      "domain": "personal-os",
      "project_id": "proj_agent_os",
      "due_date": null,
      "next_action": "Complete Block 0 local setup",
      "source": "TASKS.md",
      "created_at": "2026-06-07T09:00:00-05:00",
      "updated_at": "2026-06-07T09:00:00-05:00",
      "blocked_by": [],
      "notes": "v0 build target is 8 hours."
    }
  ]
}
```

#### `domains/personal-os/data/projects.json`

Overwrite strategy: rewritten by `refresh_data.py` after reading `inputs/projects.md`, `TASKS.md`, and generated project plans. Dedupe by slug.

```json
{
  "schema_version": "1.0",
  "updated_at": "2026-06-07T09:00:00-05:00",
  "projects": [
    {
      "id": "proj_agent_os",
      "slug": "gemini-agent-os",
      "name": "Gemini Agent OS",
      "status": "active",
      "domain": "personal-os",
      "problem": "Build a self-hosted AI operating system using VS Code, Gemini, and Oracle VPS instead of Cowork and Claude.",
      "success_criteria": [
        "FastAPI app runs locally and on VPS",
        "Gemini chat endpoint works",
        "Morning brief generates and archives",
        "Dashboard reads dashboard.json",
        "Guardrails prevent automated writes to inputs/"
      ],
      "current_phase": "v0 build",
      "owner": "Damian",
      "last_reviewed": "2026-06-07",
      "links": []
    }
  ]
}
```

#### `domains/personal-os/data/decisions.json`

Append strategy: append new decisions only. Dedupe by `decision` plus date.

```json
{
  "schema_version": "1.0",
  "decisions": [
    {
      "id": "dec_20260607_001",
      "date": "2026-06-07",
      "domain": "personal-os",
      "decision": "Use FastAPI plus Google Gen AI SDK for production runtime.",
      "reasoning": "Direct API calls are easier to secure and audit than running a terminal agent as a service.",
      "tradeoff": "More custom code than using Gemini CLI directly.",
      "source": "PRD-Gemini-Agent-OS.md"
    }
  ]
}
```

#### `domains/personal-os/data/brief-state.json`

Overwrite strategy: rewritten whenever morning brief runs.

```json
{
  "schema_version": "1.0",
  "last_brief_at": "2026-06-07T08:00:00-05:00",
  "last_brief_file": "briefs/archive/brief-2026-06-07.md",
  "summary": "Focus today: finish Block 0 and Block 1 of Gemini Agent OS.",
  "top_priorities": [
    "Create repo structure",
    "Set up Gemini API key",
    "Run local FastAPI health check"
  ],
  "open_questions": [
    "Should production access be public HTTPS or private VPN?"
  ]
}
```

#### `domains/personal-os/data/system-health.json`

Overwrite strategy: rewritten by `deploy_check.py` and dashboard refresh. No secrets.

```json
{
  "schema_version": "1.0",
  "checked_at": "2026-06-07T09:00:00-05:00",
  "environment": "local",
  "app": {
    "status": "ok",
    "health_endpoint": "ok",
    "version": "0.1.0"
  },
  "gemini": {
    "configured": true,
    "model": "gemini-3.5-flash",
    "last_successful_call_at": "2026-06-07T09:00:00-05:00"
  },
  "data_layer": {
    "root_exists": true,
    "inputs_write_guard_enabled": true,
    "last_backup_at": null
  },
  "deployment": {
    "target": "oracle-ampere-a1-flex",
    "docker_compose_status": "not_deployed_yet",
    "public_url": null
  }
}
```

#### `dashboard/dashboard.json`

Overwrite strategy: rewritten after morning brief, task update, deploy check, or manual dashboard refresh.

```json
{
  "schema_version": "1.0",
  "updated_at": "2026-06-07T09:00:00-05:00",
  "timezone": "America/Chicago",
  "brief": {
    "latest_file": "briefs/latest.md",
    "summary": "Focus today: finish local MVP setup.",
    "generated_at": "2026-06-07T08:00:00-05:00"
  },
  "tasks": {
    "active_count": 4,
    "blocked_count": 1,
    "top": [
      {
        "id": "task_20260607_001",
        "title": "Complete Block 0 local setup",
        "priority": "high",
        "status": "active"
      }
    ]
  },
  "projects": [
    {
      "id": "proj_agent_os",
      "name": "Gemini Agent OS",
      "status": "active",
      "current_phase": "v0 build"
    }
  ],
  "system_health": {
    "app_status": "ok",
    "gemini_configured": true,
    "deployment_status": "not_deployed_yet"
  }
}
```

#### `runtime/agent.db`

Storage strategy: SQLite runtime audit log. Not source of truth. Not committed. Can be recreated. Used for observability.

Tables:

```sql
CREATE TABLE IF NOT EXISTS audit_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  actor TEXT NOT NULL,
  event_type TEXT NOT NULL,
  request_id TEXT,
  domain TEXT,
  action TEXT NOT NULL,
  path TEXT,
  safety_level TEXT NOT NULL,
  approved INTEGER NOT NULL DEFAULT 0,
  summary TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS model_calls (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  request_id TEXT NOT NULL,
  model TEXT NOT NULL,
  purpose TEXT NOT NULL,
  input_tokens INTEGER,
  output_tokens INTEGER,
  status TEXT NOT NULL,
  error TEXT
);

CREATE TABLE IF NOT EXISTS tool_calls (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  request_id TEXT NOT NULL,
  tool_name TEXT NOT NULL,
  arguments_json TEXT NOT NULL,
  result_summary TEXT,
  status TEXT NOT NULL,
  safety_level TEXT NOT NULL
);
```

### 5.6 Refresh strategy

| File | Populated by | Frequency | Write mode | Dedupe |
|---|---|---|---|---|
| `tasks.json` | `update_tasks.py` | Manual, after brief, daily | Overwrite with stable IDs | Normalized title + source |
| `projects.json` | `refresh_data.py` | Manual, daily | Overwrite | Project slug |
| `decisions.json` | Skills/workflows | On decision capture | Append | Date + decision text |
| `brief-state.json` | `morning_brief.py` | Daily/manual | Overwrite | Single state object |
| `system-health.json` | `deploy_check.py` | Manual, hourly optional | Overwrite | Single state object |
| `dashboard.json` | `dashboard.py` | After every state change | Overwrite | Single state object |
| `runtime/agent.db` | App runtime | Continuous | Append | Request IDs |

---

## 6. Component specifications

### 6.1 FastAPI app

Purpose: serve chat, skills, dashboard JSON, health check, and workflow triggers.

Endpoints:

| Endpoint | Method | Purpose | Writes |
|---|---|---|---|
| `/health` | GET | Return app status. | None. |
| `/chat` | POST | User chat with Gemini Agent OS. | Only approved tool writes. |
| `/run-skill` | POST | Execute named skill from `toolbox/`. | Skill-specific outputs. |
| `/brief/morning` | POST | Manually trigger morning brief. | Brief files and dashboard JSON. |
| `/dashboard.json` | GET | Serve dashboard state. | None. |

Input schema for `/chat`:

```json
{
  "message": "What should I do next on the agent OS build?",
  "domain": "personal-os",
  "allow_writes": false,
  "approval_token": null
}
```

Output schema for `/chat`:

```json
{
  "request_id": "req_20260607_001",
  "answer": "Start with Block 0: verify local prerequisites and create the repo skeleton.",
  "actions_taken": [],
  "actions_requiring_approval": [],
  "files_read": ["AGENTS.md", "TASKS.md", "domains/personal-os/data/tasks.json"],
  "files_written": []
}
```

### 6.2 Gemini agent runtime

Purpose: combine operating instructions, memory, user request, and tool results into safe, useful responses.

Reads:

- `AGENTS.md`
- `domains/{domain}/AGENTS.md`
- `TASKS.md`
- relevant `memory/*.md`
- relevant `domains/{domain}/data/*.json`
- relevant `toolbox/*.md` for skill calls

Writes:

- None directly. All writes go through `app/tools/filesystem.py`, `app/tools/tasks.py`, or approved workflow modules.

Model config:

```env
GEMINI_MODEL=gemini-3.5-flash
GEMINI_FALLBACK_MODEL=gemini-2.5-flash
GEMINI_API_KEY=replace_me
```

Safety behavior:

- Read-only by default.
- Writes require endpoint `allow_writes=true` or workflow context.
- Destructive writes require explicit approval token `proceed`.
- Tool calls must be logged to `runtime/agent.db`.

### 6.3 File safety tool

Purpose: prevent accidental overwrites and enforce local data-layer rules.

Rules:

| Action | Allowed in v0? | Conditions |
|---|---|---|
| Read root files | Yes | Must stay inside project root. |
| Read `inputs/` | Yes | Read-only. |
| Write `inputs/` | No | Only human edits. |
| Write `data/` | Yes | Workflow/tool only. |
| Write `outputs/` | Yes | Prefer date-stamped or slugged filenames. |
| Delete files | No by default | Requires plan plus explicit `proceed`. |
| Shell commands | No from agent runtime | Use deployment scripts manually or approved admin workflow later. |

### 6.4 Morning brief workflow

Purpose: generate a daily operating brief.

Reads:

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

Writes:

- `briefs/latest.md`
- `briefs/archive/brief-YYYY-MM-DD.md`
- `domains/personal-os/data/brief-state.json`
- `dashboard/dashboard.json`

Schedule:

- Daily at 08:00 America/Chicago.
- Manual through `make brief` or `POST /brief/morning`.

Output structure:

```md
# Morning Brief: YYYY-MM-DD

## Today focus

## Top priorities

## Blockers / risks

## Open threads

## Suggested next actions

## System health

## Files used
```

### 6.5 Dashboard refresh

Purpose: turn current data into one dashboard JSON file and static HTML view.

Reads:

- `briefs/latest.md`
- `tasks.json`
- `projects.json`
- `system-health.json`
- `brief-state.json`

Writes:

- `dashboard/dashboard.json`

Schedule:

- After morning brief.
- After task update.
- After deploy check.
- Manual through `make dashboard`.

### 6.6 Skills

Skill specs live in `toolbox/*.md`. Each skill is readable by humans and executable by `/run-skill`.

| Skill | Purpose | Writes |
|---|---|---|
| `create-prd` | Turn a project idea into a build-ready PRD. | `domains/personal-os/outputs/prds/PRD-{slug}-YYYY-MM-DD.md` |
| `plan-project` | Turn vague goal into scoped implementation plan. | `domains/personal-os/outputs/plans/plan-{slug}-YYYY-MM-DD.md` |
| `update-tasks` | Extract and normalize tasks. | `TASKS.md`, `tasks.json` with approval for task file changes. |
| `morning-brief` | Manual brief generation. | Brief files and dashboard JSON. |
| `system-status` | Report local/VPS health. | `system-health.json`, dashboard JSON. |
| `deploy-check` | Check deployment readiness and runtime status. | `system-health.json`, report file. |

---

## 7. The build plan

### 7.1 Block table

| Block | What gets built | Who runs it | Output | Done when... |
|---|---|---|---|---|
| Block 0: Setup and orientation | Verify local prerequisites, create repo, install VS Code/Gemini tooling, save PRD, create `.env.example`, confirm Gemini API key path. | Me + Gemini coding agent | Working local repo with PRD and initial files. | `git status` works, Python 3.12+ works, Docker works, PRD is saved, `.env.example` exists. |
| Block 1: Data layer and seed files | Create folder tree, seed `AGENTS.md`, `TASKS.md`, memory files, domain inputs, data JSON files, dashboard shell. | Gemini coding agent | Complete local data layer. | `python scripts/init_workspace.py --check` passes and no automation writes to `inputs/`. |
| Block 2: FastAPI and Gemini runtime | Build app config, health endpoint, chat endpoint, Gemini client wrapper, context loader, schemas. | Gemini coding agent | Local API service. | `make dev` starts app; `/health` passes; `/chat` can answer read-only using context. |
| Block 3: Guardrails, tools, audit | Build safe filesystem tool, task tool, memory tool, audit SQLite, destructive-action gate. | Gemini coding agent | Tool layer with safety checks. | Tests prove writes to `inputs/` fail; allowed output writes succeed; audit logs are created. |
| Block 4: Workflows and skills | Build task update, morning brief, dashboard refresh, core skill runner, first skill specs. | Gemini coding agent | Working brief/dashboard/skills loop. | `make brief`, `make dashboard`, and `make skill SKILL=system-status` work locally. |
| Block 5: Dashboard UI | Build static dashboard HTML reading `dashboard.json`; add simple local serving route. | Gemini coding agent | Browser dashboard. | Dashboard shows latest brief, top tasks, project state, system health. |
| Block 6: Docker and VPS deployment | Build Dockerfile, compose file, env handling, Caddy/Nginx config, systemd service docs. | Me + Gemini coding agent | Deployable container stack. | App runs in Docker locally and on Oracle VPS; `/health` passes. |
| Block 7: Scheduling, backup, polish | Add systemd timer/cron for morning brief, backup script, deploy check, README. | Me + Gemini coding agent | Production-ready v0. | Timer is installed or documented; backup works; README documents usage and recovery. |

### 7.2 Cut order if running behind

1. Cut dashboard styling; keep `dashboard.json`.
2. Cut `deploy-check` skill; keep `/health`.
3. Cut `create-prd` skill; keep `plan-project` and `system-status`.
4. Cut systemd timer; use manual `make brief` temporarily.
5. Cut public HTTPS; use Tailscale/private SSH tunnel temporarily.

### 7.3 Never cut

- Block 0 setup.
- Block 1 data layer.
- `AGENTS.md` operating rules.
- `inputs/` never-overwrite guard.
- Gemini chat endpoint.
- Morning brief generation.
- Basic audit logging.

---

## 8. Setup details and copy-paste prompts

### 8.1 Folder creation command

Run from `~/agent-os`:

```bash
mkdir -p app/{schemas,tools,workflows} \
  memory/personal-os \
  toolbox \
  briefs/archive \
  dashboard/assets \
  domains/personal-os/{inputs,data,outputs/{plans,prds,reports}} \
  domains/code-projects/{inputs,data,outputs} \
  domains/school/{inputs,data,outputs} \
  domains/career/{inputs,data,outputs} \
  runtime/logs \
  scripts \
  deploy/{caddy,systemd}

touch AGENTS.md TASKS.md README.md pyproject.toml Makefile .env.example .gitignore

touch app/__init__.py app/main.py app/agent.py app/config.py app/context.py app/guardrails.py app/audit.py app/prompts.py

touch app/schemas/{agent_response.py,task.py,brief.py,dashboard.py,skill.py}
touch app/tools/{filesystem.py,tasks.py,memory.py,brief.py,dashboard.py,status.py}
touch app/workflows/{refresh_data.py,update_tasks.py,morning_brief.py,deploy_check.py}

touch memory/people.md memory/terminology.md memory/personal-os/{context.md,decisions.md,open-threads.md}

touch domains/personal-os/AGENTS.md domains/personal-os/inputs/{inbox.md,projects.md,routines.md}
touch domains/code-projects/AGENTS.md domains/school/AGENTS.md domains/career/AGENTS.md

touch toolbox/{create-prd.md,plan-project.md,update-tasks.md,morning-brief.md,system-status.md,deploy-check.md}

touch dashboard/index.html dashboard/dashboard.json
```

### 8.2 Root `AGENTS.md` prompt

```md
# Agent OS Operating Instructions

You are Damian's Gemini Agent OS.

## Role
Act as a rigorous thinking partner and execution assistant. Do not be a yes-machine. Push back on vague, risky, contradictory, or under-specified requests.

## Build rule
Before building anything non-trivial, produce or reference a PRD with problem, success criteria, scope, constraints, implementation plan, and open questions. Check what already exists before proposing custom work.

## Reversibility rule
Before destructive or irreversible actions, including deleting, overwriting, sending communications, financial actions, or bulk operations:
1. Show the plan.
2. Identify what is irreversible.
3. Wait for explicit approval: `proceed`.

## Data-layer rule
- `inputs/` is human-maintained and must never be auto-overwritten.
- `data/` is machine-refreshed.
- `outputs/` is generated.
- `memory/` stores durable context.
- `TASKS.md` stores active tasks.
- Date-stamped files use `name-YYYY-MM-DD.md`.

## Working style
Be direct, concrete, and rigorous. Skip filler. State assumptions. Flag contradictions before acting. Show useful reasoning summaries, not hidden chain-of-thought. When context changes, re-interview briefly.

## Default workflow
For every request:
1. Classify the domain.
2. Load root instructions.
3. Load relevant domain instructions.
4. Read relevant memory and data files.
5. Decide whether this is read-only, write, scheduled, or destructive.
6. Act only within the allowed safety level.
7. Log decisions, open questions, and next actions.
```

### 8.3 `domains/personal-os/AGENTS.md`

```md
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
```

### 8.4 Workflow prompt: `morning_brief`

```md
# Workflow: morning_brief

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
```

### 8.5 Workflow prompt: `update_tasks`

```md
# Workflow: update_tasks

Purpose: Extract, normalize, and update tasks from human notes and project files.

Read these files:
- `TASKS.md`
- `domains/personal-os/inputs/inbox.md`
- `domains/personal-os/inputs/projects.md`
- `domains/personal-os/data/projects.json`
- `memory/personal-os/open-threads.md`

Write these files:
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
```

### 8.6 Workflow prompt: `refresh_data`

```md
# Workflow: refresh_data

Purpose: Refresh derived data files from human-maintained inputs and current memory.

Read these files:
- `domains/personal-os/inputs/projects.md`
- `domains/personal-os/inputs/routines.md`
- `TASKS.md`
- `memory/personal-os/context.md`
- `memory/personal-os/decisions.md`

Write these files:
- `domains/personal-os/data/projects.json`
- `domains/personal-os/data/decisions.json` only for newly captured decisions
- `dashboard/dashboard.json`

CRITICAL: never write to any `inputs/` directory.

Rules:
- Treat inputs as source material, not files to clean up.
- Use stable IDs where possible.
- Dedupe projects by slug.
- Dedupe decisions by date plus decision text.
- If input conflicts with existing data, flag the conflict in the workflow result instead of silently choosing one.
```

### 8.7 Skill prompt: `create-prd`

```md
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
```

### 8.8 Skill prompt: `plan-project`

```md
# Skill: plan-project

Purpose: Turn a vague project goal into an executable plan.

Read:
- `AGENTS.md`
- `TASKS.md`
- `domains/personal-os/data/projects.json`
- `domains/personal-os/data/tasks.json`
- `memory/personal-os/context.md`

Write:
- `domains/personal-os/outputs/plans/plan-{slug}-YYYY-MM-DD.md`

CRITICAL: never write to any `inputs/` directory.

Output sections:
1. Goal
2. Assumptions
3. Scope
4. Milestones
5. Step-by-step plan
6. Risks
7. Decisions needed
8. Next action

Rules:
- Push back if the goal is too broad.
- Prefer a smaller working version over a large fragile plan.
- Include a cut order.
```

### 8.9 Skill prompt: `system-status`

```md
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
```

### 8.10 Deployment environment template

`.env.example`:

```env
APP_ENV=local
APP_HOST=0.0.0.0
APP_PORT=8000
AGENT_ROOT=/data/agent-os
TIMEZONE=America/Chicago
GEMINI_API_KEY=replace_me
GEMINI_MODEL=gemini-3.5-flash
GEMINI_FALLBACK_MODEL=gemini-2.5-flash
PUBLIC_BASE_URL=http://localhost:8000
AUTH_SHARED_SECRET=replace_me_for_v0
```

### 8.11 Dockerfile

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
  && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY app ./app

RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir fastapi uvicorn[standard] google-genai pydantic python-dotenv

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 8.12 Docker Compose

```yaml
services:
  agent-os:
    build:
      context: ..
      dockerfile: deploy/Dockerfile
    container_name: agent-os
    restart: unless-stopped
    env_file:
      - ../.env
    ports:
      - "8000:8000"
    volumes:
      - /data/agent-os:/data/agent-os
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
```

---

## 9. Decision log

| Decision | Reasoning / trade-off |
|---|---|
| Use `AGENTS.md` instead of `CLAUDE.md`. | The target is Gemini/VS Code, not Claude/Cowork. `AGENTS.md` is provider-neutral and understandable to coding agents. |
| Use direct Gemini API calls in production. | Safer and more auditable than running a terminal agent as the production runtime. The trade-off is more backend code. |
| Use Gemini CLI and Code Assist for development only. | They are excellent for coding workflows but too broad for unattended hosted execution. |
| Build one full domain first. | A stable `personal-os` core is more valuable than thin partial implementations across many domains. |
| Keep local files as source of truth. | Files are inspectable, portable, git-friendly, and easy to back up. The trade-off is manual schema discipline. |
| Add SQLite only for runtime audit. | Audit logs benefit from a DB, but memory/tasks should remain readable as files in v0. |
| No external connectors in v0. | Avoids OAuth/scope complexity before the agent's safety model is proven. |
| Static dashboard first. | Fast to build and reliable. More dynamic UI can come later. |
| Systemd/cron for scheduled jobs. | More reliable across restarts than an in-process scheduler. Slightly more VPS setup work. |
| No autonomous builder in v0. | It is high value but high risk. Add after guardrails, tests, backups, and review flow exist. |
| Explicit destructive-action approval. | Prevents accidental deletion, overwrite, messages, or bulk changes. Adds friction where appropriate. |
| Use Oracle Ampere A1 Flex as orchestrator, not inference server. | ARM VPS is good for hosting lightweight services; Gemini handles model inference remotely. |
| Keep production access private at first. | Reduces security risk while testing. Public HTTPS can be enabled after auth is hardened. |

---

## 10. Out of scope / future work

### 10.1 Deferred domains

The placeholder domains already exist in the folder tree. To activate one later, add domain memory files, define data schemas, create workflows, and add dashboard panels. No restructuring is required.

| Domain | Activation work |
|---|---|
| `code-projects` | Add repo inventory, build plans, bug tracker, deployment notes, GitHub connector, code-review skill. |
| `school` | Add course list, deadline tracker, assignment planner, study brief, calendar connector. |
| `career` | Add opportunity tracker, resume versions, networking CRM, application status, interview prep briefs. |

### 10.2 Future capabilities

| Capability | Trigger to add |
|---|---|
| Gmail connector | When email triage or daily brief needs inbox context. |
| Google Calendar connector | When schedule-aware planning is needed. |
| GitHub connector | When `code-projects` becomes active. |
| Notion/Drive connector | When existing notes/docs should be indexed or summarized. |
| Vector memory | When file memory is too large for simple retrieval. |
| Autonomous builder | After backups, tests, PR review flow, and rollback model are working. |
| User auth | Before exposing the service publicly beyond private/VPN access. |
| Mobile-friendly UI | After dashboard data model stabilizes. |

### 10.3 What would force a re-architecture

- Multiple users with different permissions.
- High-volume connector ingestion.
- Need for long-term semantic search across thousands of files.
- Agent allowed to perform external side effects such as email sends, payments, or bulk account operations.
- Requirement to run local inference instead of Gemini API.
- Compliance requirements that mandate stronger encryption, retention policies, or access controls.

---

## Appendix A: Minimal acceptance tests

| Test | Command / action | Expected result |
|---|---|---|
| Repo init | `python scripts/init_workspace.py --check` | Required folders/files exist. |
| Inputs guard | Try writing to `domains/personal-os/inputs/inbox.md` through filesystem tool | Tool refuses. |
| Health | `curl http://localhost:8000/health` | JSON status `ok`. |
| Chat | POST `/chat` read-only question | Answer cites files read, writes nothing. |
| Brief | `make brief` | `briefs/latest.md` and archive file created. |
| Dashboard | Open `dashboard/index.html` | Shows data from `dashboard/dashboard.json`. |
| Docker | `docker compose -f deploy/docker-compose.yml up --build` | App starts and health check passes. |
| Audit | Run one skill | `runtime/agent.db` contains model/tool/audit rows. |

## Appendix B: MVP success definition

The v0 MVP is successful when:

1. You can ask the local agent what to do next and it answers using repo context.
2. It refuses unsafe writes to `inputs/`.
3. It can generate a morning brief and dashboard JSON.
4. It can run at least `system-status`, `plan-project`, and `create-prd` skills.
5. It runs on Oracle Ampere A1 Flex through Docker Compose.
6. You can back up `/data/agent-os` and restore it.
7. You can understand all important state by reading files, without needing a hidden platform UI.
