"""
app/tools/dashboard.py
Dashboard JSON refresh helpers for Gemini Agent OS.
Reads derived json logs for tasks, projects, brief, and health,
aggregates them, and writes a unified dashboard/dashboard.json file.
"""

import json
import datetime
from pathlib import Path
from app import config
from app.tools.filesystem import read_file, write_file
from app.schemas.dashboard import DashboardState, DashboardBrief, DashboardTasks, DashboardTaskItem, DashboardProjectItem, DashboardSystemHealth

def refresh_dashboard_json(domain: str = "personal-os", request_id: str = "internal") -> str:
    """
    Reads data layer JSON states and compiles a consolidated dashboard/dashboard.json.
    """
    # 1. Load tasks
    try:
        tasks_content = read_file(f"domains/{domain}/data/tasks.json", request_id=request_id)
    except FileNotFoundError:
        tasks_content = ""
    tasks_data = json.loads(tasks_content) if tasks_content else {"tasks": []}
    
    # 2. Load projects
    try:
        projects_content = read_file(f"domains/{domain}/data/projects.json", request_id=request_id)
    except FileNotFoundError:
        projects_content = ""
    projects_data = json.loads(projects_content) if projects_content else {"projects": []}
    
    # 3. Load health
    try:
        health_content = read_file(f"domains/{domain}/data/system-health.json", request_id=request_id)
    except FileNotFoundError:
        health_content = ""
    health_data = json.loads(health_content) if health_content else {}
    
    # 4. Load brief state
    try:
        brief_content = read_file(f"domains/{domain}/data/brief-state.json", request_id=request_id)
    except FileNotFoundError:
        brief_content = ""
    brief_data = json.loads(brief_content) if brief_content else {}

    # Compile brief section
    db_brief = DashboardBrief(
        latest_file=brief_data.get("last_brief_file", "briefs/latest.md"),
        summary=brief_data.get("summary", "No brief generated yet."),
        generated_at=brief_data.get("last_brief_at", datetime.datetime.now(datetime.timezone.utc).isoformat())
    )

    # Compile tasks section
    all_tasks = tasks_data.get("tasks", [])
    active_tasks = [t for t in all_tasks if t.get("status") == "active"]
    blocked_tasks = [t for t in all_tasks if t.get("status") == "blocked"]
    
    # Select top tasks (prioritize high priority)
    sorted_active = sorted(
        active_tasks,
        key=lambda x: 0 if x.get("priority") == "high" else (1 if x.get("priority") == "medium" else 2)
    )
    
    top_items = []
    for t in sorted_active[:5]:
        top_items.append(DashboardTaskItem(
            id=t.get("id"),
            title=t.get("title"),
            priority=t.get("priority"),
            status=t.get("status")
        ))
        
    db_tasks = DashboardTasks(
        active_count=len(active_tasks),
        blocked_count=len(blocked_tasks),
        top=top_items
    )

    # Compile projects section
    db_projects = []
    for p in projects_data.get("projects", []):
        db_projects.append(DashboardProjectItem(
            id=p.get("id"),
            name=p.get("name"),
            status=p.get("status"),
            current_phase=p.get("current_phase", "")
        ))

    # Compile health section
    app_health_status = health_data.get("app", {}).get("status", "unknown")
    gemini_conf = health_data.get("gemini", {}).get("configured", False)
    deploy_status = health_data.get("deployment", {}).get("docker_compose_status", "not_deployed_yet")
    
    db_health = DashboardSystemHealth(
        app_status=app_health_status,
        gemini_configured=gemini_conf,
        deployment_status=deploy_status
    )

    # Construct the total DashboardState
    state = DashboardState(
        schema_version="1.0",
        updated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        timezone=config.TIMEZONE,
        brief=db_brief,
        tasks=db_tasks,
        projects=db_projects,
        system_health=db_health
    )

    # Write dashboard.json
    result_content = state.model_dump_json(indent=2)
    write_file("dashboard/dashboard.json", result_content, allow_writes=True, request_id=request_id)
    return "Successfully refreshed dashboard/dashboard.json"