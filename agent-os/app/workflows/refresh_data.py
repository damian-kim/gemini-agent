"""
app/workflows/refresh_data.py
Workflow to refresh derived JSON files from human-maintained markdown files.
Uses Gemini's structured output capability to parse markdown lists into schema-validated JSON.
"""

import datetime
from pathlib import Path
from app import config
from app.tools.filesystem import read_file, write_file
from app.tools.dashboard import refresh_dashboard_json
from app.agent import generate_structured_response
from app.schemas.project import ProjectsContainer, DecisionsContainer

def run_refresh_data(domain: str = "personal-os", request_id: str = "internal") -> str:
    """
    Parses inputs/projects.md and memory/decisions.md into structured JSON,
    and updates the master dashboard.json view.
    """
    # 1. Load Projects markdown
    try:
        projects_md = read_file(f"domains/{domain}/inputs/projects.md", request_id=request_id)
    except FileNotFoundError:
        projects_md = ""
        
    if projects_md.strip():
        system_instruction = (
            "You are a strict data-extraction engine. Read the markdown projects definition list "
            "and output a clean JSON conforming to the ProjectsContainer schema. "
            "For each project, derive a unique slug (lower-case with dashes), generate an ID if not explicit "
            "(e.g., 'proj_' + slug with underscores), and ensure fields like status, problem, success_criteria, "
            "current_phase, owner, last_reviewed, and links are parsed accurately. "
            "Do not invent facts or external links."
        )
        prompt = f"### Markdown Projects Content:\n{projects_md}"
        
        json_output = generate_structured_response(
            system_instruction=system_instruction,
            prompt=prompt,
            response_schema=ProjectsContainer
        )
        
        # Ground and add timestamp
        parsed_projects = ProjectsContainer.model_validate_json(json_output)
        parsed_projects.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        write_file(
            path=f"domains/{domain}/data/projects.json",
            content=parsed_projects.model_dump_json(indent=2),
            allow_writes=True,
            request_id=request_id
        )

    # 2. Load Decisions markdown
    try:
        decisions_md = read_file(f"memory/{domain}/decisions.md", request_id=request_id)
    except FileNotFoundError:
        decisions_md = ""
    if decisions_md.strip():
        system_instruction = (
            "You are a strict data-extraction engine. Read the markdown decisions list and output a clean JSON "
            "conforming to the DecisionsContainer schema. "
            "For each decision, extract date, domain, decision statement, reasoning, tradeoff, and source. "
            "Generate a unique ID (e.g. dec_YYYYMMDD_NNN)."
        )
        prompt = f"### Markdown Decisions Content:\n{decisions_md}"
        
        json_output = generate_structured_response(
            system_instruction=system_instruction,
            prompt=prompt,
            response_schema=DecisionsContainer
        )
        
        parsed_decisions = DecisionsContainer.model_validate_json(json_output)
        
        write_file(
            path=f"domains/{domain}/data/decisions.json",
            content=parsed_decisions.model_dump_json(indent=2),
            allow_writes=True,
            request_id=request_id
        )
        
    # 3. Refresh the unified dashboard.json state
    refresh_dashboard_json(domain=domain, request_id=request_id)
    
    return "Data refresh complete. Projects, decisions, and dashboard.json states updated."

if __name__ == "__main__":
    print(run_refresh_data())