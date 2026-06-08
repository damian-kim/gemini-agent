"""
app/tools/memory.py
Memory management helpers for read/append actions on durable memory.
Delegates to the filesystem tool for safety verification and auditing.
"""

from typing import Optional
from app.tools.filesystem import read_file, write_file

def read_memory_file(path: str, request_id: str = "internal") -> str:
    """Reads a cross-domain or domain-specific memory file."""
    clean_path = path if path.startswith("memory/") else f"memory/{path}"
    return read_file(clean_path, request_id=request_id)

def append_memory_file(
    path: str,
    content_to_append: str,
    approval_token: Optional[str] = None,
    request_id: str = "internal"
) -> str:
    """
    Appends fact/decision blocks to a memory file.
    Appends are CRITICAL writes, thus requiring the 'proceed' token.
    """
    clean_path = path if path.startswith("memory/") else f"memory/{path}"
    
    # Load current file content
    existing_content = read_file(clean_path, request_id=request_id)
    
    # Structure separator
    sep = "\n" if (existing_content.endswith("\n") or not existing_content) else "\n\n"
    updated_content = existing_content + sep + content_to_append.strip() + "\n"
    
    # Save back (monitored by critical write check in filesystem.py)
    return write_file(
        path=clean_path,
        content=updated_content,
        allow_writes=True,
        approval_token=approval_token,
        request_id=request_id
    )