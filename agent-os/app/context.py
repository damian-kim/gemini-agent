"""
app/context.py
Context Loader for Gemini Agent OS.
Loads instruction, memory, task, inputs, and derived data files for a domain
and formats them into structured system prompt context.
"""

from pathlib import Path
from typing import Dict
import logging
from app import config

logger = logging.getLogger(__name__)

def get_file_content(path: Path) -> str:
    """Safely reads file content. Returns empty string if file does not exist."""
    if not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Error reading file {path}: {e}")
        return ""

def load_context(domain: str = "personal-os") -> Dict[str, str]:
    """
    Loads all relevant files for the given domain.
    Returns a dict mapping the relative path string to its file contents.
    """
    root = Path(config.AGENT_ROOT)
    
    files_to_read = [
        # Root instructions and active tasks
        "AGENTS.md",
        "TASKS.md",
        
        # Cross-domain memory
        "memory/people.md",
        "memory/terminology.md",
        
        # Domain operating guidelines
        f"domains/{domain}/AGENTS.md",
        
        # Human-maintained inputs
        f"domains/{domain}/inputs/inbox.md",
        f"domains/{domain}/inputs/projects.md",
        f"domains/{domain}/inputs/routines.md",
        
        # Domain derived data (JSON)
        f"domains/{domain}/data/tasks.json",
        f"domains/{domain}/data/projects.json",
        f"domains/{domain}/data/decisions.json",
        f"domains/{domain}/data/brief-state.json",
        f"domains/{domain}/data/system-health.json",
        
        # Domain-specific deep memory
        f"memory/{domain}/context.md",
        f"memory/{domain}/decisions.md",
        f"memory/{domain}/open-threads.md"
    ]

    context_map = {}
    for rel_path in files_to_read:
        abs_path = root / rel_path
        content = get_file_content(abs_path)
        if content.strip():
            context_map[rel_path] = content

    return context_map

def build_context_prompt(domain: str = "personal-os") -> str:
    """
    Retrieves data layer files for the domain and aggregates them
    into a structured string block to ground the LLM's answers.
    """
    context_map = load_context(domain)
    prompt_parts = []
    
    prompt_parts.append("### LOCAL DATA LAYER CONTEXT")
    prompt_parts.append("Below is the current state of the local data layer files. Ground your decisions and answers in these files. Do not assume facts outside of these contents.")
    
    for rel_path, content in context_map.items():
        prompt_parts.append(f"\n--- START FILE: {rel_path} ---")
        prompt_parts.append(content.strip())
        prompt_parts.append(f"--- END FILE: {rel_path} ---")
        
    return "\n".join(prompt_parts)