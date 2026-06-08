"""
app/workflows/update_tasks.py
Workflow to extract and normalize tasks from notes and threads.
Parses unstructured notes into schema-validated JSON, refreshes the dashboard,
and safely updates the root TASKS.md with explicit user approval.
"""

import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from app import config
from app.tools.filesystem import read_file, write_file
from app.tools.dashboard import refresh_dashboard_json
from app.agent import generate_structured_response
from app.schemas.task import TasksContainer

def run_update_tasks(
    domain: str = "personal-os",
    approval_token: Optional[str] = None,
    request_id: str = "internal"
) -> str:
    """
    Scans files for tasks, parses them into JSON, and optionally updates TASKS.md.
    """
    # 1. Read input source material
    try:
        tasks_md = read_file("TASKS.md", request_id=request_id)
    except FileNotFoundError:
        tasks_md = ""
        
    try:
        inbox_md = read_file(f"domains/{domain}/inputs/inbox.md", request_id=request_id)
    except FileNotFoundError:
        inbox_md = ""
        
    try:
        projects_md = read_file(f"domains/{domain}/inputs/projects.md", request_id=request_id)
    except FileNotFoundError:
        projects_md = ""
        
    try:
        projects_json = read_file(f"domains/{domain}/data/projects.json", request_id=request_id)
    except FileNotFoundError:
        projects_json = ""
        
    try:
        open_threads_md = read_file(f"memory/{domain}/open-threads.md", request_id=request_id)
    except FileNotFoundError:
        open_threads_md = ""

    # Load generated plans from domains/{domain}/outputs/plans/plan-*.md
    plans_content = []
    plans_dir = Path(config.AGENT_ROOT) / "domains" / domain / "outputs" / "plans"
    if plans_dir.is_dir():
        for plan_file in sorted(plans_dir.glob("plan-*.md")):
            try:
                rel_path = plan_file.relative_to(Path(config.AGENT_ROOT))
                content = read_file(str(rel_path).replace("\\", "/"), request_id=request_id)
                plans_content.append(f"### Plan ({rel_path.name}):\n{content}")
            except Exception:
                pass
    plans_payload = "\n\n".join(plans_content)

    # Compile content to submit to Gemini
    context_payload = (
        f"### Current TASKS.md:\n{tasks_md}\n\n"
        f"### Inbox Notes:\n{inbox_md}\n\n"
        f"### Projects Notes:\n{projects_md}\n\n"
        f"### Projects JSON:\n{projects_json}\n\n"
        f"### Open Threads:\n{open_threads_md}\n\n"
        f"### Project Plans:\n{plans_payload}"
    )

    system_instruction = (
        "You are a task parsing and normalization agent. Analyze the provided tasks list, notes, threads, and project plans. "
        "Extract all actionable tasks and output a clean JSON matching the TasksContainer schema. "
        "Rules:\n"
        "1. Extract and preserve existing task IDs (e.g. task_20260607_001). For new tasks, generate an ID: task_YYYYMMDD_NNN.\n"
        "2. Deduplicate tasks by title and source file.\n"
        "3. Keep due_date and notes accurate. Do not invent due dates.\n"
        "4. Set next_action to a concrete action step.\n"
        "5. For tasks extracted from inbox, projects, or project plans, record their status as active.\n"
        "6. When extracting tasks from project plans, associate them with the appropriate project_id and set the source to the plan's filename."
    )

    # 2. Query model to extract structured data
    json_output = generate_structured_response(
        system_instruction=system_instruction,
        prompt=context_payload,
        response_schema=TasksContainer
    )

    parsed_tasks = TasksContainer.model_validate_json(json_output)
    parsed_tasks.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # 3. Save tasks.json derived file (Standard WRITE safety level)
    write_file(
        path=f"domains/{domain}/data/tasks.json",
        content=parsed_tasks.model_dump_json(indent=2),
        allow_writes=True,
        request_id=request_id
    )

    # 4. Generate candidate TASKS.md markdown content
    new_tasks_lines = ["# Active Tasks\n"]
    
    # Group by domain namespaces
    by_domain = {}
    for task in parsed_tasks.tasks:
        by_domain.setdefault(task.domain, []).append(task)
        
    for dom_name, task_list in by_domain.items():
        new_tasks_lines.append(f"## {dom_name}")
        for t in task_list:
            status_box = "[ ]" if t.status != "completed" else "[x]"
            details = []
            if t.priority:
                details.append(f"Priority: {t.priority}")
            if t.next_action:
                details.append(f"Next: {t.next_action}")
            details_str = f" ({', '.join(details)})" if details else ""
            new_tasks_lines.append(f"- {status_box} {t.title} <!-- id: {t.id} -->{details_str}")
        new_tasks_lines.append("")

    new_tasks_md_content = "\n".join(new_tasks_lines)

    # 5. Overwrite TASKS.md if changed AND approved
    tasks_md_changed = tasks_md.strip() != new_tasks_md_content.strip()
    tasks_md_write_status = ""
    
    if tasks_md_changed:
        if approval_token == "proceed":
            write_file(
                path="TASKS.md",
                content=new_tasks_md_content,
                allow_writes=True,
                approval_token=approval_token,
                request_id=request_id
            )
            tasks_md_write_status = " Root TASKS.md updated with approval."
        else:
            tasks_md_write_status = " Root TASKS.md has updates pending, but was NOT overwritten (requires approval_token='proceed')."
    else:
        tasks_md_write_status = " No updates needed for root TASKS.md."

    # 6. Refresh dashboard JSON representation
    refresh_dashboard_json(domain=domain, request_id=request_id)

    return f"Task extraction complete. tasks.json and dashboard state refreshed.{tasks_md_write_status}"

if __name__ == "__main__":
    print(run_update_tasks())