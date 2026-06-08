#!/usr/bin/env python3
"""
scripts/init_workspace.py
Idempotent workspace initialization script for Gemini Agent OS.
Creates folders and seeds files as specified in the PRD.
"""

import os
import argparse
import sys
import json

# Define directories to create
DIRS = [
    "app",
    "app/schemas",
    "app/tools",
    "app/workflows",
    "memory",
    "memory/personal-os",
    "toolbox",
    "briefs",
    "briefs/archive",
    "dashboard",
    "dashboard/assets",
    "domains",
    "domains/personal-os",
    "domains/personal-os/inputs",
    "domains/personal-os/data",
    "domains/personal-os/outputs",
    "domains/personal-os/outputs/plans",
    "domains/personal-os/outputs/prds",
    "domains/personal-os/outputs/reports",
    "domains/code-projects",
    "domains/code-projects/inputs",
    "domains/code-projects/data",
    "domains/code-projects/outputs",
    "domains/school",
    "domains/school/inputs",
    "domains/school/data",
    "domains/school/outputs",
    "domains/career",
    "domains/career/inputs",
    "domains/career/data",
    "domains/career/outputs",
    "runtime",
    "runtime/logs",
    "scripts",
    "deploy",
    "deploy/caddy",
    "deploy/systemd"
]

# Define files and seed contents
FILES = {}

# 1. Root configuration files
FILES["AGENTS.md"] = """# Agent OS Operating Instructions

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
"""

FILES["TASKS.md"] = """# Active Tasks

## personal-os
- [ ] Deploy Gemini Agent OS MVP to Oracle VPS <!-- id: task_20260607_001 --> (Priority: high, Next: Complete Block 0 local setup)
"""

FILES["README.md"] = """# Gemini Agent OS

A self-hosted personal AI operating system powered by Gemini, developed in VS Code, and hosted on an Oracle Cloud VPS.

## Setup

1. Copy `.env.example` to `.env` (without overwriting if already customized) and configure your `GEMINI_API_KEY`.
2. Run `python scripts/init_workspace.py` (or `make init`) to generate the folder tree and seed files.
3. Verify using `python scripts/init_workspace.py --check`.

## Core Commands

- `make init` - Initialize or check the workspace.
- `make dev` - Start the FastAPI development server.
- `make test` - Run backend unit tests.
- `make brief` - Manually trigger the morning brief workflow.
- `make dashboard` - Manually refresh the static dashboard data.
- `make deploy-check` - Run a VPS deployment check.
"""

FILES["pyproject.toml"] = """[project]
name = "gemini-agent-os"
version = "0.1.0"
description = "A self-hosted personal AI operating system powered by Gemini"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.28.0",
    "google-genai>=0.1.1",
    "pydantic>=2.6.0",
    "python-dotenv>=1.0.1"
]

[build-system]
requires = ["setuptools>=61.0.0"]
build-backend = "setuptools.build_meta"
"""

FILES["Makefile"] = """.PHONY: init dev test brief dashboard deploy-check

init:
	python scripts/init_workspace.py

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	python -m unittest discover -s app/tests -p "*_test.py"

brief:
	python -m app.workflows.morning_brief

dashboard:
	python -m app.workflows.refresh_data

deploy-check:
	python -m app.workflows.deploy_check
"""

FILES[".gitignore"] = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Environment variables
.env

# Runtime data and logs
runtime/agent.db
runtime/logs/

# OS generated files
.DS_Store
Thumbs.db

# IDEs
.vscode/
.idea/
"""

# 2. Memory files
FILES["memory/people.md"] = """# People

## Damian Kim
- Owner of this Gemini Agent OS.
- Timezone: America/Chicago.
- Works in VS Code and wants Gemini instead of Claude/Cowork for this build.
- Hosting target: Oracle Cloud Infrastructure Ampere A1 Flex VPS.

## Rules
- Do not infer sensitive personal facts unless Damian explicitly states them.
- Add people only when useful for future workflows.
"""

FILES["memory/terminology.md"] = """# Terminology

- Agent OS: the self-hosted Gemini-powered personal operating system in this repo.
- Data layer: local files under `~/agent-os/`, not a cloud connector.
- Inputs: human-maintained files that automation must never overwrite.
- Data: machine-refreshed derived files.
- Outputs: generated artifacts such as briefs, reports, plans, and PRDs.
- Proceed: explicit approval word required before destructive or irreversible actions.
"""

FILES["memory/personal-os/context.md"] = """# Personal OS Context

This domain coordinates tasks, notes, projects, briefs, and system operation.
The system should prefer clear written plans, auditable file changes, and reversible actions.
The first production target is a hosted FastAPI app on Oracle Ampere A1 Flex using Gemini through the Google Gen AI SDK.
"""

FILES["memory/personal-os/decisions.md"] = """# Decisions

- Use `AGENTS.md` instead of `CLAUDE.md` because the target stack is Gemini/VS Code rather than Claude/Cowork.
- Use direct Gemini API calls for production rather than Gemini CLI because API calls are easier to secure, log, and constrain.
- Use local files as source of truth before introducing databases or external connectors.
"""

FILES["memory/personal-os/open-threads.md"] = """# Open Threads

- Which external connector should be added first after v0: Gmail, Google Calendar, Notion, GitHub, or something else?
- Should the production app be exposed publicly with HTTPS or kept private through Tailscale/VPN?
- Which domain should be built next after personal-os: code-projects, school, or career?
"""

# 3. Domain operating files and inputs
FILES["domains/personal-os/AGENTS.md"] = """# personal-os Domain Instructions

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
"""

FILES["domains/personal-os/inputs/inbox.md"] = """# Inbox

- Initial notes and scratchpad. Feel free to dump text here for task extraction.
"""

FILES["domains/personal-os/inputs/projects.md"] = """# Projects

## Gemini Agent OS
- Slug: gemini-agent-os
- Status: active
- Problem: Build a self-hosted AI operating system using VS Code, Gemini, and Oracle VPS.
- Success Criteria:
  - FastAPI app runs locally and on VPS
  - Gemini chat endpoint works
  - Morning brief generates and archives
  - Dashboard reads dashboard.json
  - Guardrails prevent automated writes to inputs/
- Current Phase: v0 build
"""

FILES["domains/personal-os/inputs/routines.md"] = """# Routines

- Morning brief: daily at 08:00 America/Chicago.
"""

# Placeholder Domain AGENTS.md
FILES["domains/code-projects/AGENTS.md"] = """# Domain: code-projects
Status: Deferred.
This domain is reserved for future code projects tracking.
"""

FILES["domains/school/AGENTS.md"] = """# Domain: school
Status: Deferred.
This domain is reserved for future school course, assignments, and study tracking.
"""

FILES["domains/career/AGENTS.md"] = """# Domain: career
Status: Deferred.
This domain is reserved for future career, applications, and job opportunity tracking.
"""

# 4. Toolbox skills
FILES["toolbox/create-prd.md"] = """# Skill: create-prd

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
"""

FILES["toolbox/plan-project.md"] = """# Skill: plan-project

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
"""

FILES["toolbox/update-tasks.md"] = """# Skill: update-tasks

Purpose: Extract, normalize, and update tasks from human notes and project files.

Read:
- `TASKS.md`
- `domains/personal-os/inputs/inbox.md`
- `domains/personal-os/inputs/projects.md`
- `domains/personal-os/data/projects.json`
- `memory/personal-os/open-threads.md`

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
"""

FILES["toolbox/morning-brief.md"] = """# Skill: morning-brief

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
"""

FILES["toolbox/system-status.md"] = """# Skill: system-status

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
"""

FILES["toolbox/deploy-check.md"] = """# Skill: deploy-check

Purpose: Check deployment readiness and runtime status on VPS.

Read:
- `domains/personal-os/data/system-health.json`
- Docker environment configuration
- deployment settings

Write:
- `domains/personal-os/data/system-health.json`
- `domains/personal-os/outputs/reports/deploy-check-YYYY-MM-DD.md`

CRITICAL: never write to any `inputs/` directory.
"""

# 5. Seed Data files
FILES["domains/personal-os/data/tasks.json"] = json.dumps({
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
      "due_date": None,
      "next_action": "Complete Block 0 local setup",
      "source": "TASKS.md",
      "created_at": "2026-06-07T09:00:00-05:00",
      "updated_at": "2026-06-07T09:00:00-05:00",
      "blocked_by": [],
      "notes": "v0 build target is 8 hours."
    }
  ]
}, indent=2)

FILES["domains/personal-os/data/projects.json"] = json.dumps({
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
}, indent=2)

FILES["domains/personal-os/data/decisions.json"] = json.dumps({
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
}, indent=2)

FILES["domains/personal-os/data/brief-state.json"] = json.dumps({
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
}, indent=2)

FILES["domains/personal-os/data/system-health.json"] = json.dumps({
  "schema_version": "1.0",
  "checked_at": "2026-06-07T09:00:00-05:00",
  "environment": "local",
  "app": {
    "status": "ok",
    "health_endpoint": "ok",
    "version": "0.1.0"
  },
  "gemini": {
    "configured": True,
    "model": "gemini-3.5-flash",
    "last_successful_call_at": "2026-06-07T09:00:00-05:00"
  },
  "data_layer": {
    "root_exists": True,
    "inputs_write_guard_enabled": True,
    "last_backup_at": None
  },
  "deployment": {
    "target": "oracle-ampere-a1-flex",
    "docker_compose_status": "not_deployed_yet",
    "public_url": None
  }
}, indent=2)

# 6. Dashboard files
FILES["dashboard/dashboard.json"] = json.dumps({
  "schema_version": "1.0",
  "updated_at": "2026-06-07T09:00:00-05:00",
  "timezone": "America/Chicago",
  "brief": {
    "latest_file": "briefs/latest.md",
    "summary": "Focus today: finish local MVP setup.",
    "generated_at": "2026-06-07T08:00:00-05:00"
  },
  "tasks": {
    "active_count": 1,
    "blocked_count": 0,
    "top": [
      {
        "id": "task_20260607_001",
        "title": "Deploy Gemini Agent OS MVP to Oracle VPS",
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
    "gemini_configured": True,
    "deployment_status": "not_deployed_yet"
  }
}, indent=2)

# Sleek and premium dark mode index.html dashboard
FILES["dashboard/index.html"] = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemini Agent OS Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0d0f12;
            --card-bg: rgba(22, 26, 33, 0.6);
            --card-border: rgba(255, 255, 255, 0.05);
            --text-primary: #f0f3f6;
            --text-secondary: #8b949e;
            --accent-glow: rgba(56, 139, 253, 0.15);
            --accent-color: #58a6ff;
            --success-color: #3fb950;
            --warning-color: #d29922;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 2rem;
            background-image: 
                radial-gradient(at 0% 0%, rgba(31, 38, 135, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(56, 139, 253, 0.1) 0px, transparent 50%);
            background-attachment: fixed;
        }

        header {
            margin-bottom: 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--card-border);
            padding-bottom: 1.5rem;
        }

        h1 {
            font-family: 'Outfit', sans-serif;
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ffffff 0%, #a5c7f7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.5px;
        }

        .system-time {
            font-family: 'Outfit', sans-serif;
            color: var(--text-secondary);
            font-size: 0.95rem;
        }

        .grid-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
        }

        @media (max-width: 900px) {
            .grid-container {
                grid-template-columns: 1fr;
            }
        }

        .card {
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 40px 0 rgba(56, 139, 253, 0.08);
            border-color: rgba(56, 139, 253, 0.2);
        }

        .card-title {
            font-family: 'Outfit', sans-serif;
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .card-subtitle {
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-top: -0.5rem;
            margin-bottom: 1rem;
        }

        .brief-content {
            line-height: 1.6;
            color: #e6edf3;
            font-size: 0.95rem;
        }

        .task-list {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }

        .task-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.75rem;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.03);
        }

        .task-title {
            font-size: 0.9rem;
            font-weight: 500;
        }

        .priority-badge {
            font-size: 0.75rem;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-weight: 600;
            text-transform: uppercase;
        }

        .priority-high {
            background: rgba(248, 81, 73, 0.15);
            color: #ff7b72;
        }

        .status-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 0.5rem;
        }

        .status-ok {
            background-color: var(--success-color);
            box-shadow: 0 0 8px var(--success-color);
        }

        .status-warning {
            background-color: var(--warning-color);
            box-shadow: 0 0 8px var(--warning-color);
        }

        .health-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
        }

        .health-item {
            background: rgba(255, 255, 255, 0.01);
            padding: 0.75rem;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.02);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .health-label {
            font-size: 0.85rem;
            color: var(--text-secondary);
        }

        .health-val {
            font-size: 0.85rem;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <header>
        <div>
            <h1>Gemini Agent OS</h1>
            <div style="color: var(--text-secondary); margin-top: 0.25rem; font-size: 0.9rem;">Personal Orchestrator Dashboard</div>
        </div>
        <div class="system-time" id="clock">Loading system state...</div>
    </header>

    <div class="grid-container">
        <!-- Morning Brief Panel -->
        <div class="card" style="grid-column: span 2;">
            <div class="card-title">
                <span>Morning Brief & Focus</span>
                <span id="brief-date" style="font-size: 0.85rem; color: var(--text-secondary);"></span>
            </div>
            <div class="brief-content" id="brief-summary">
                Loading latest brief focus...
            </div>
        </div>

        <!-- Top Tasks Panel -->
        <div class="card">
            <div class="card-title">
                <span>Top Active Tasks</span>
                <span id="task-count" style="font-size: 0.85rem; color: var(--accent-color);">0 active</span>
            </div>
            <ul class="task-list" id="task-list">
                <!-- Tasks loaded dynamically -->
            </ul>
        </div>

        <!-- System Status Panel -->
        <div class="card">
            <div class="card-title">
                <span>System Health & Config</span>
            </div>
            <div class="health-grid">
                <div class="health-item">
                    <span class="health-label">API Status</span>
                    <span class="health-val" id="health-api"><span class="status-indicator status-warning"></span>Offline</span>
                </div>
                <div class="health-item">
                    <span class="health-label">Gemini Config</span>
                    <span class="health-val" id="health-gemini">Checking...</span>
                </div>
                <div class="health-item">
                    <span class="health-label">Environment</span>
                    <span class="health-val" id="health-env">-</span>
                </div>
                <div class="health-item">
                    <span class="health-label">Deployment</span>
                    <span class="health-val" id="health-deploy">-</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        async function fetchDashboard() {
            try {
                const response = await fetch('./dashboard.json');
                const data = await response.json();
                
                // Clock/Update Time
                const updatedTime = new Date(data.updated_at).toLocaleString('en-US', { timeZone: data.timezone });
                document.getElementById('clock').textContent = `Last updated: ${updatedTime} (${data.timezone})`;

                // Brief Summary
                document.getElementById('brief-summary').textContent = data.brief.summary;
                const briefGen = new Date(data.brief.generated_at).toLocaleDateString();
                document.getElementById('brief-date').textContent = `Generated: ${briefGen}`;

                // Task list
                const taskList = document.getElementById('task-list');
                taskList.innerHTML = '';
                document.getElementById('task-count').textContent = `${data.tasks.active_count} active`;
                
                if (data.tasks.top && data.tasks.top.length > 0) {
                    data.tasks.top.forEach(task => {
                        const li = document.createElement('li');
                        li.className = 'task-item';
                        li.innerHTML = `
                            <span class="task-title">${task.title}</span>
                            <span class="priority-badge priority-high">${task.priority}</span>
                        `;
                        taskList.appendChild(li);
                    });
                } else {
                    taskList.innerHTML = '<li class="task-item">No active tasks found</li>';
                }

                // Health
                const apiHealth = data.system_health.app_status === 'ok';
                document.getElementById('health-api').innerHTML = apiHealth 
                    ? `<span class="status-indicator status-ok"></span>Online`
                    : `<span class="status-indicator status-warning"></span>Issues`;
                
                document.getElementById('health-gemini').textContent = data.system_health.gemini_configured ? 'Active' : 'Unconfigured';
                document.getElementById('health-env').textContent = data.timezone;
                document.getElementById('health-deploy').textContent = data.system_health.deployment_status;

            } catch (err) {
                console.error("Error loading dashboard data:", err);
                document.getElementById('clock').textContent = "Error loading dashboard.json";
            }
        }

        // Fetch on load
        fetchDashboard();
        // Poll every 30 seconds
        setInterval(fetchDashboard, 30000);
    </script>
</body>
</html>
"""

# 7. Deployment Configuration files
FILES["deploy/Dockerfile"] = """FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \\
    curl \\
    ca-certificates \\
  && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY app ./app

RUN pip install --no-cache-dir --upgrade pip \\
  && pip install --no-cache-dir fastapi uvicorn[standard] google-genai pydantic python-dotenv

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

FILES["deploy/docker-compose.yml"] = """services:
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
"""

FILES["deploy/caddy/Caddyfile"] = """# Caddy reverse proxy configurations
:80 {
    reverse_proxy agent-os:8000
}
"""

FILES["deploy/systemd/agent-os.service"] = """[Unit]
Description=Gemini Agent OS Service (Docker Compose Stack)
After=docker.service
Requires=docker.service

[Service]
Type=simple
WorkingDirectory=/data/agent-os
ExecStart=/usr/bin/docker compose -f deploy/docker-compose.yml up
ExecStop=/usr/bin/docker compose -f deploy/docker-compose.yml down
Restart=always
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=agent-os

[Install]
WantedBy=multi-user.target
"""

FILES["deploy/systemd/morning-brief.service"] = """[Unit]
Description=Gemini Agent OS Morning Brief Trigger
After=agent-os.service

[Service]
Type=oneshot
ExecStart=/usr/bin/curl -X POST http://localhost:8000/brief/morning
"""

FILES["deploy/systemd/morning-brief.timer"] = """[Unit]
Description=Daily morning brief at 08:00 America/Chicago
RefuseManualStart=no
RefuseManualStop=no

[Timer]
OnCalendar=*-*-* 08:00:00 America/Chicago
Persistent=true

[Install]
WantedBy=timers.target
"""

# 8. Admin/Backup scripts
FILES["scripts/backup.sh"] = """#!/bin/bash
set -e
BACKUP_DIR="/data/agent-os/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/agent-os-backup-${TIMESTAMP}.tar.gz"

echo "Starting Gemini Agent OS backup..."
mkdir -p "${BACKUP_DIR}"

# Archive code, config, and data layers (excluding docker caches, python caches, and logs)
tar --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='runtime/logs/*' \
    -czf "${BACKUP_FILE}" \
    -C /data/agent-os .

echo "Backup created successfully at: ${BACKUP_FILE}"
"""

FILES["scripts/restore.sh"] = """#!/bin/bash
# restore.sh - Restore backup with explicit confirmation
set -e

if [ -z "$1" ]; then
    echo "Usage: $0 /path/to/backup.tar.gz"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "${BACKUP_FILE}" ]; then
    echo "Error: Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

echo "WARNING: This will overwrite files in the current workspace!"
read -p "Type 'proceed' to confirm restore of ${BACKUP_FILE}: " confirmation

if [ "${confirmation}" != "proceed" ]; then
    echo "Restore cancelled."
    exit 0
fi

echo "Restoring backup..."
tar -xzf "${BACKUP_FILE}" -C /data/agent-os

echo "Restore complete."
"""

# 9. App Python skeleton files
APP_FILES = [
    ("app/__init__.py", "# app python package"),
    ("app/main.py", '"""\\napp/main.py\\nFastAPI Entrypoint.\\n"""\\nfrom fastapi import FastAPI\\napp = FastAPI(title="Gemini Agent OS")\\n\\n@app.get("/health")\\ndef health():\\n    return {"status": "ok", "version": "0.1.0"}\\n'),
    ("app/agent.py", '"""\\napp/agent.py\\nGemini API Agent Client wrapper.\\n"""\\n'),
    ("app/config.py", '"""\\napp/config.py\\nConfiguration Loader.\\n"""\\n'),
    ("app/context.py", '"""\\napp/context.py\\nContext Loader.\\n"""\\n'),
    ("app/guardrails.py", '"""\\napp/guardrails.py\\nFile safety and destructive operations guardrails.\\n"""\\n'),
    ("app/audit.py", '"""\\napp/audit.py\\nAudit logging module.\\n"""\\n'),
    ("app/prompts.py", '"""\\napp/prompts.py\\nPrompt Builders.\\n"""\\n'),
    ("app/schemas/__init__.py", ""),
    ("app/schemas/agent_response.py", '"""\\napp/schemas/agent_response.py\\n"""\\n'),
    ("app/schemas/task.py", '"""\\napp/schemas/task.py\\n"""\\n'),
    ("app/schemas/brief.py", '"""\\napp/schemas/brief.py\\n"""\\n'),
    ("app/schemas/dashboard.py", '"""\\napp/schemas/dashboard.py\\n"""\\n'),
    ("app/schemas/skill.py", '"""\\napp/schemas/skill.py\\n"""\\n'),
    ("app/tools/__init__.py", ""),
    ("app/tools/filesystem.py", '"""\\napp/tools/filesystem.py\\nFilesystem Tool.\\n"""\\n'),
    ("app/tools/tasks.py", '"""\\napp/tools/tasks.py\\nTasks Tool.\\n"""\\n'),
    ("app/tools/memory.py", '"""\\napp/tools/memory.py\\nMemory Tool.\\n"""\\n'),
    ("app/tools/brief.py", '"""\\napp/tools/brief.py\\nBrief Tool.\\n"""\\n'),
    ("app/tools/dashboard.py", '"""\\napp/tools/dashboard.py\\nDashboard Tool.\\n"""\\n'),
    ("app/tools/status.py", '"""\\napp/tools/status.py\\nSystem Health check tools.\\n"""\\n'),
    ("app/workflows/__init__.py", ""),
    ("app/workflows/refresh_data.py", '"""\\napp/workflows/refresh_data.py\\n"""\\n'),
    ("app/workflows/update_tasks.py", '"""\\napp/workflows/update_tasks.py\\n"""\\n'),
    ("app/workflows/morning_brief.py", '"""\\napp/workflows/morning_brief.py\\n"""\\n'),
    ("app/workflows/deploy_check.py", '"""\\napp/workflows/deploy_check.py\\n"""\\n')
]

for filepath, content in APP_FILES:
    FILES[filepath] = content


def setup_workspace(force=False):
    print("Initializing directories...")
    for d in DIRS:
        os.makedirs(d, exist_ok=True)
        print(f"  Directory verified: {d}")

    print("\\nInitializing seed files...")
    created_count = 0
    skipped_count = 0
    
    for filepath, content in FILES.items():
        if os.path.exists(filepath) and not force:
            print(f"  File exists (skipping): {filepath}")
            skipped_count += 1
            continue
        
        # Avoid destructive overwrite of local .env if run accidentally
        if filepath == ".env" or filepath == "../.env":
            if os.path.exists(filepath):
                print(f"  WARNING: Refusing to overwrite existing {filepath}")
                skipped_count += 1
                continue
                
        # Ensure directories exist for the file
        parent_dir = os.path.dirname(filepath)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
            
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  File created: {filepath}")
        created_count += 1

    print(f"\\nWorkspace setup complete. Created: {created_count}, Skipped: {skipped_count}.")


def check_workspace():
    print("Checking workspace status...")
    missing_dirs = []
    missing_files = []

    for d in DIRS:
        if not os.path.isdir(d):
            missing_dirs.append(d)

    for filepath in FILES.keys():
        if not os.path.isfile(filepath):
            missing_files.append(filepath)

    if missing_dirs or missing_files:
        print("\\nSTATUS: INCOMPLETE")
        if missing_dirs:
            print("Missing directories:")
            for md in missing_dirs:
                print(f"  - {md}")
        if missing_files:
            print("Missing files:")
            for mf in missing_files:
                print(f"  - {mf}")
        return False
    else:
        print("\\nSTATUS: COMPLETE. All required directories and files exist.")
        return True


def main():
    parser = argparse.ArgumentParser(description="Gemini Agent OS Workspace Setup Utility")
    parser.add_argument("--check", action="store_true", help="Check workspace completeness and exit")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files (except .env)")
    args = parser.parse_args()

    if args.check:
        complete = check_workspace()
        sys.exit(0 if complete else 1)
    else:
        setup_workspace(force=args.force)
        complete = check_workspace()
        sys.exit(0 if complete else 1)


if __name__ == "__main__":
    main()
