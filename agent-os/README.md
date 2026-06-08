# Gemini Agent OS

Gemini Agent OS is a local-first, self-hosted personal AI operating system. It operates on a transparent local file data layer, runs an API orchestration backend utilizing the Gemini API via the official Google Gen AI Python SDK, and displays a responsive glassmorphic dark-mode web dashboard.

The target hosting environment is an **Oracle Cloud Infrastructure (OCI) Ampere A1 Flex VPS** running Linux (ARM64).

---

## 1. Directory Structure

```text
agent-os/
├── AGENTS.md                   # Global operating instructions
├── TASKS.md                    # Active task list (human-maintained)
├── pyproject.toml              # Dependencies & packages
├── Makefile                    # Target command shortcuts
├── app/                        # FastAPI backend & workflows
│   ├── main.py                 # Web app entrypoint
│   ├── agent.py                # Gemini client (structured outputs)
│   ├── context.py              # Context loader (reads files)
│   ├── guardrails.py           # Safety constraints (inputs guard)
│   ├── audit.py                # Observability logs (SQLite)
│   ├── tools/                  # Safe filesystem/task/memory tools
│   └── workflows/              # Scheduled morning briefs & updates
├── memory/                     # Long-term cross-domain memory
├── domains/                    # Domain spaces (personal-os, code-projects, etc.)
│   └── personal-os/            
│       ├── inputs/             # Human inputs (never auto-overwritten)
│       ├── data/               # Derived JSON states
│       └── outputs/            # Generated PRDs, plans, and reports
├── toolbox/                    # Declarative skills specifications
├── briefs/                     # Generated operating briefs & archives
├── dashboard/                  # Static HTML files & dashboard.json
├── deploy/                     # Docker & VPS deployment templates
│   ├── Dockerfile              # ARM64-compatible python container
│   ├── docker-compose.yml      # Container service orchestrations
│   └── systemd/                # systemd services and brief timers
└── scripts/                    # Init, backup, and restore scripts
```

---

## 2. Local Development & Setup

### Prerequisites
* **Python**: Version 3.12+ (verified on 3.14)
* **Docker & Docker Compose** (for containerized testing)
* **Gemini API Key**: Obtain a key from Google AI Studio.

### Step 1: Configuration
Copy the env template and configure your API key:
```bash
cp .env.example .env
# Open .env and set your GEMINI_API_KEY
```

### Step 2: Initialize Workspace
Run the idempotent workspace generator:
```bash
python scripts/init_workspace.py
```
To check workspace integrity and files completeness:
```bash
python scripts/init_workspace.py --check
```

### Step 3: Run the API Server
Start the development server:
```bash
# Using python directly:
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Using Makefile (on Unix/WSL):
make dev
```
Access the static dashboard in your browser at:
`http://localhost:8000/dashboard/`

### Step 4: Run Unit Tests
Execute the unit test discovery suite (covers filesystem guardrails, SQLite auditing, and workflows):
```bash
# Using python:
python -m unittest discover -s app/tests -p "*_test.py"

# Using Makefile:
make test
```

---

## 3. VPS Docker Deployment

The deployment maps application source files and data layers to the `/data/agent-os` mount folder on the VPS host.

### Step 1: Copy Code to VPS
Use `rsync` or `scp` to copy the project contents to your target Oracle VPS:
```bash
rsync -avz --exclude='__pycache__' --exclude='runtime/' --exclude='.git' ./ user@<vps-ip>:/data/agent-os
```

### Step 2: Launch Container Stack
Log in to your VPS via SSH and boot up the Docker Compose stack:
```bash
cd /data/agent-os
docker compose -f deploy/docker-compose.yml up -d --build
```
Verify the health endpoint from the host machine:
```bash
curl -f http://localhost:8000/health
```

---

## 4. Scheduling Workflows on VPS (Systemd)

We configure the daily **Morning Brief** execution using systemd timers on the VPS host.

1. Copy the systemd files to the system manager directory:
   ```bash
   sudo cp deploy/systemd/* /etc/systemd/system/
   ```
2. Reload systemd configurations:
   ```bash
   sudo systemctl daemon-reload
   ```
3. Enable and start the Docker Compose service stack:
   ```bash
   sudo systemctl enable agent-os.service
   sudo systemctl start agent-os.service
   ```
4. Enable and start the Daily Morning Brief timer (fires daily at 08:00 America/Chicago):
   ```bash
   sudo systemctl enable morning-brief.timer
   sudo systemctl start morning-brief.timer
   ```
5. Check timer status:
   ```bash
   systemctl status morning-brief.timer
   ```

---

## 5. Backup & Recovery

The backup script archives code configurations, memory, inputs, and derived JSON states while excluding Python caches, runtime database logs, and nested backups.

### Generate a Backup
Run the backup script. By default, it saves timestamped archives to `/data/agent-os/backups/`.
```bash
# Execute on the VPS host:
bash scripts/backup.sh

# To backup from a different folder path:
AGENT_ROOT=/my/custom/path bash scripts/backup.sh
```

### Restore from a Backup
Run the restore script, passing the target backup archive path.
```bash
# Execute on the VPS host:
bash scripts/restore.sh /data/agent-os/backups/agent-os-backup-YYYYMMDD_HHMMSS.tar.gz
```
*Note:* The restore script requires you to type the safety approval word `proceed` before performing any write/extraction actions.
