"""
app/guardrails.py
File safety and write guardrails for Gemini Agent OS.
Validates path parameters, blocks modifications to inputs/ directories,
requires explicit approval tokens for critical writes, and logs events.
"""

from pathlib import Path
from app import config
from app.audit import log_audit_event

class SecurityException(PermissionError):
    """Exception raised when an operation violates security guardrails."""
    pass

def validate_path(path: Path) -> Path:
    """
    Resolves the path and ensures it resides strictly within the AGENT_ROOT boundary.
    If the path is relative, it is resolved against AGENT_ROOT.
    """
    root = Path(config.AGENT_ROOT).resolve()
    try:
        path_obj = Path(path)
        if not path_obj.is_absolute():
            resolved = (root / path_obj).resolve()
        else:
            resolved = path_obj.resolve()
    except Exception as e:
        raise SecurityException(f"Invalid path representation: {e}")
        
    if not str(resolved).startswith(str(root)):
        raise SecurityException(f"Access Denied: Path '{resolved}' is outside allowed root '{root}'.")
    return resolved

def check_write_permission(path: Path, allow_writes: bool, approval_token: str = None) -> str:
    """
    Enforces write guardrails.
    Returns safety level ('WRITE_STANDARD' or 'WRITE_CRITICAL') if allowed.
    Raises SecurityException if permission is denied.
    """
    resolved = validate_path(path)
    root = Path(config.AGENT_ROOT).resolve()
    
    # 1. Inputs Write Guard: Never write to any inputs/ subdirectory
    if any(part == "inputs" for part in resolved.parts):
        log_audit_event(
            actor="agent",
            event_type="write_blocked",
            action="write_file",
            path=str(resolved),
            safety_level="FORBIDDEN",
            approved=False,
            summary=f"Security Guard: Blocked attempt to write to inputs path: {resolved.name}"
        )
        raise SecurityException("Forbidden: System automation is strictly prohibited from writing to 'inputs/' folders.")

    # Get path representation relative to root
    rel_path_str = str(resolved.relative_to(root)).replace("\\", "/")
    
    # 2. Critical Files Guard (Requires explicit approval token 'proceed')
    is_critical = (
        rel_path_str == "AGENTS.md" or
        rel_path_str == "TASKS.md" or
        rel_path_str == "pyproject.toml" or
        rel_path_str == "Makefile" or
        rel_path_str.startswith("memory/") or
        rel_path_str.startswith("app/") or
        rel_path_str.startswith("deploy/") or
        rel_path_str.startswith("scripts/") or
        rel_path_str.endswith("AGENTS.md")
    )
    
    if is_critical:
        safety_level = "WRITE_CRITICAL"
        if approval_token != "proceed":
            log_audit_event(
                actor="agent",
                event_type="write_blocked",
                action="write_file",
                path=str(resolved),
                safety_level=safety_level,
                approved=False,
                summary=f"Blocked attempt to modify critical path '{rel_path_str}' without 'proceed' token."
            )
            raise SecurityException(f"Critical write denied: Modifying '{rel_path_str}' requires explicit human approval ('proceed').")
            
        log_audit_event(
            actor="agent",
            event_type="write_approved",
            action="write_file",
            path=str(resolved),
            safety_level=safety_level,
            approved=True,
            summary=f"Approved write to critical path '{rel_path_str}' using approval token."
        )
        return safety_level

    # 3. Standard Writes (data/, outputs/, briefs/, dashboard/, runtime/)
    is_standard = (
        rel_path_str.startswith("domains/") or
        rel_path_str.startswith("briefs/") or
        rel_path_str.startswith("dashboard/") or
        rel_path_str.startswith("runtime/")
    )
    
    if is_standard:
        safety_level = "WRITE_STANDARD"
        if not allow_writes:
            log_audit_event(
                actor="agent",
                event_type="write_blocked",
                action="write_file",
                path=str(resolved),
                safety_level=safety_level,
                approved=False,
                summary=f"Blocked write to standard path '{rel_path_str}' because allow_writes is false."
            )
            raise SecurityException(f"Write denied: Writing to '{rel_path_str}' requires allow_writes=true.")
            
        log_audit_event(
            actor="agent",
            event_type="write_executed",
            action="write_file",
            path=str(resolved),
            safety_level=safety_level,
            approved=True,
            summary=f"Executed write to standard path '{rel_path_str}'."
        )
        return safety_level

    # 4. Fail-closed for any other directory
    raise SecurityException(f"Write denied: Destination path '{rel_path_str}' is not inside allowed writable directories.")

def check_delete_permission(path: Path, approval_token: str = None) -> str:
    """
    Enforces delete guardrails. All file deletions require the approval token 'proceed'.
    Raises SecurityException if denied.
    """
    resolved = validate_path(path)
    root = Path(config.AGENT_ROOT).resolve()
    rel_path_str = str(resolved.relative_to(root)).replace("\\", "/")
    
    # 1. Inputs Guard: Never delete files inside inputs/
    if any(part == "inputs" for part in resolved.parts):
        log_audit_event(
            actor="agent",
            event_type="delete_blocked",
            action="delete_file",
            path=str(resolved),
            safety_level="FORBIDDEN",
            approved=False,
            summary=f"Security Guard: Blocked attempt to delete inputs path: {resolved.name}"
        )
        raise SecurityException("Forbidden: Deleting files inside 'inputs/' is strictly prohibited.")
        
    # Deletions require proceed
    safety_level = "DESTRUCTIVE"
    if approval_token != "proceed":
        log_audit_event(
            actor="agent",
            event_type="delete_blocked",
            action="delete_file",
            path=str(resolved),
            safety_level=safety_level,
            approved=False,
            summary=f"Blocked attempt to delete file '{rel_path_str}' without 'proceed' token."
        )
        raise SecurityException(f"Delete denied: Deleting file '{rel_path_str}' requires explicit approval ('proceed').")
        
    log_audit_event(
        actor="agent",
        event_type="delete_approved",
        action="delete_file",
        path=str(resolved),
        safety_level=safety_level,
        approved=True,
        summary=f"Approved deletion of file '{rel_path_str}' using approval token."
    )
    return safety_level