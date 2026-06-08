"""
app/tools/filesystem.py
Safe filesystem tool implementations for Gemini Agent OS.
Forces validation checks and logs tool call metadata in the audit DB.
"""

import json
from pathlib import Path
from typing import Optional
from app.guardrails import validate_path, check_write_permission, check_delete_permission
from app.audit import log_tool_call

def read_file(path: str, request_id: str = "internal") -> str:
    """
    Reads file content after performing boundary validation.
    Logs execution to the audit database.
    """
    try:
        resolved = validate_path(Path(path))
        if not resolved.is_file():
            raise FileNotFoundError(f"File not found: {path}")
        content = resolved.read_text(encoding="utf-8")
        
        log_tool_call(
            request_id=request_id,
            tool_name="read_file",
            arguments_json=json.dumps({"path": path}),
            status="success",
            safety_level="SAFE",
            result_summary=f"Read {len(content)} characters from {path}"
        )
        return content
    except Exception as e:
        log_tool_call(
            request_id=request_id,
            tool_name="read_file",
            arguments_json=json.dumps({"path": path}),
            status="failed",
            safety_level="SAFE",
            result_summary=str(e)
        )
        raise e

def write_file(
    path: str,
    content: str,
    allow_writes: bool,
    approval_token: Optional[str] = None,
    request_id: str = "internal"
) -> str:
    """
    Writes content to a file after performing boundary, inputs, and critical-writes validation.
    Logs execution to the audit database.
    """
    try:
        target_path = Path(path)
        safety_level = check_write_permission(target_path, allow_writes, approval_token)
        resolved = validate_path(target_path)
        
        # Ensure containing directories exist
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content, encoding="utf-8")
        
        log_tool_call(
            request_id=request_id,
            tool_name="write_file",
            arguments_json=json.dumps({
                "path": path,
                "allow_writes": allow_writes,
                "approval_token": approval_token
            }),
            status="success",
            safety_level=safety_level,
            result_summary=f"Successfully wrote {len(content)} characters to {path}"
        )
        return f"Successfully wrote to {path}"
    except Exception as e:
        log_tool_call(
            request_id=request_id,
            tool_name="write_file",
            arguments_json=json.dumps({
                "path": path,
                "allow_writes": allow_writes,
                "approval_token": approval_token
            }),
            status="failed",
            safety_level="UNKNOWN",
            result_summary=str(e)
        )
        raise e

def delete_file(
    path: str,
    approval_token: Optional[str] = None,
    request_id: str = "internal"
) -> str:
    """
    Deletes a file after validation checks (all deletes require approval).
    Logs execution to the audit database.
    """
    try:
        target_path = Path(path)
        safety_level = check_delete_permission(target_path, approval_token)
        resolved = validate_path(target_path)
        
        if resolved.is_file():
            resolved.unlink()
        elif resolved.is_dir():
            resolved.rmdir()
        else:
            raise FileNotFoundError(f"Path does not exist: {path}")
            
        log_tool_call(
            request_id=request_id,
            tool_name="delete_file",
            arguments_json=json.dumps({
                "path": path,
                "approval_token": approval_token
            }),
            status="success",
            safety_level=safety_level,
            result_summary=f"Deleted file/directory at {path}"
        )
        return f"Successfully deleted {path}"
    except Exception as e:
        log_tool_call(
            request_id=request_id,
            tool_name="delete_file",
            arguments_json=json.dumps({
                "path": path,
                "approval_token": approval_token
            }),
            status="failed",
            safety_level="DESTRUCTIVE",
            result_summary=str(e)
        )
        raise e