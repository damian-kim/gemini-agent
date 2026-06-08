"""
app/tools/tasks.py
Task interaction helpers for tasks.json and root TASKS.md.
Leverages the safe filesystem module to validate permissions and log audits.
"""

import json
from typing import Dict, Any, Optional
from app.tools.filesystem import read_file, write_file

def read_tasks_json(domain: str = "personal-os", request_id: str = "internal") -> Dict[str, Any]:
    """Reads the derived tasks.json for the target domain."""
    path = f"domains/{domain}/data/tasks.json"
    try:
        content = read_file(path, request_id=request_id)
    except FileNotFoundError:
        content = ""
    if not content:
        return {"schema_version": "1.0", "tasks": []}
    return json.loads(content)

def write_tasks_json(
    domain: str,
    data: Dict[str, Any],
    allow_writes: bool,
    request_id: str = "internal"
) -> str:
    """
    Writes content to tasks.json.
    This corresponds to a standard WRITE safety level.
    """
    path = f"domains/{domain}/data/tasks.json"
    content = json.dumps(data, indent=2)
    return write_file(path, content, allow_writes=allow_writes, request_id=request_id)

def read_tasks_md(request_id: str = "internal") -> str:
    """Reads the human-maintained active tasks log (TASKS.md)."""
    return read_file("TASKS.md", request_id=request_id)

def write_tasks_md(
    content: str,
    approval_token: Optional[str] = None,
    request_id: str = "internal"
) -> str:
    """
    Writes content to the root TASKS.md file.
    This corresponds to a critical WRITE level and requires the 'proceed' token.
    """
    return write_file(
        path="TASKS.md",
        content=content,
        allow_writes=True,
        approval_token=approval_token,
        request_id=request_id
    )