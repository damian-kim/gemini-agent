"""
app/workflows/morning_brief.py
Workflow to generate the morning brief report and archive it daily.
Grounds the brief in active tasks, projects, decisions, and system health status.
"""

import datetime
from pathlib import Path
from app import config
from app.context import load_context, build_context_prompt
from app.tools.filesystem import read_file, write_file
from app.tools.dashboard import refresh_dashboard_json
from app.agent import generate_response, generate_structured_response
from app.schemas.brief import BriefState

def run_morning_brief(domain: str = "personal-os", request_id: str = "internal") -> str:
    """
    Orchestrates morning brief generation, archival, and dashboard updates.
    """
    # 1. Load context prompt
    context_prompt = build_context_prompt(domain)
    
    # 2. Query Gemini to generate the markdown morning brief
    system_instruction = (
        "You are Gemini Agent OS Morning Brief Generator.\n"
        "Your task is to analyze the provided files context and generate a clean daily operating brief for Damian Kim in Markdown.\n"
        "You MUST include the following sections strictly in order:\n"
        "1. Today focus\n"
        "2. Top priorities\n"
        "3. Blockers / risks\n"
        "4. Open threads\n"
        "5. Suggested next actions\n"
        "6. System health\n"
        "7. Files used\n\n"
        "Rules:\n"
        "- Be direct, analytical, and concise. Skip conversational filler.\n"
        "- Prioritize tasks with high priority, blockers, or recent updates.\n"
        "- Ground all priorities and status elements in the provided files. Do not invent deadlines.\n"
        "- Keep the brief useful enough to act on in under 5 minutes."
    )
    
    prompt = f"{context_prompt}\n\nGenerate the morning brief based on the above local data layer context."
    brief_markdown = generate_response(
        system_instruction=system_instruction,
        prompt=prompt
    )

    # 3. Query Gemini to extract structured BriefState metadata
    metadata_system_instruction = (
        "You are a strict data-extraction engine. Read the provided morning brief markdown "
        "and return a structured JSON conforming to the BriefState schema."
    )
    metadata_prompt = f"### Morning Brief Markdown:\n{brief_markdown}"
    
    json_output = generate_structured_response(
        system_instruction=metadata_system_instruction,
        prompt=metadata_prompt,
        response_schema=BriefState
    )
    
    # Parse and validate with Pydantic
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    archive_file = f"briefs/archive/brief-{today_date}.md"
    
    parsed_state = BriefState.model_validate_json(json_output)
    parsed_state.last_brief_at = now_str
    parsed_state.last_brief_file = archive_file
    
    # 4. Save brief files (Standard WRITE safety level)
    # Write briefs/latest.md
    write_file(
        path="briefs/latest.md",
        content=brief_markdown,
        allow_writes=True,
        request_id=request_id
    )
    
    # Write briefs/archive/brief-YYYY-MM-DD.md
    write_file(
        path=archive_file,
        content=brief_markdown,
        allow_writes=True,
        request_id=request_id
    )
    
    # Write data/brief-state.json
    write_file(
        path=f"domains/{domain}/data/brief-state.json",
        content=parsed_state.model_dump_json(indent=2),
        allow_writes=True,
        request_id=request_id
    )

    # 5. Refresh the unified dashboard.json state
    refresh_dashboard_json(domain=domain, request_id=request_id)
    
    return f"Morning brief workflow complete. Saved to briefs/latest.md and archived under {archive_file}."

if __name__ == "__main__":
    print(run_morning_brief())