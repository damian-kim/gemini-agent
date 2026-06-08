"""
app/tools/status.py
Diagnostics and system health status checker for Gemini Agent OS.
Generates health data conforming to the system-health.json schema.
"""

import datetime
from pathlib import Path
from app import config

def get_system_health() -> dict:
    """
    Performs a set of diagnostic health checks.
    Checks the status of the local data layer, Gemini API setup, and server environment.
    """
    root_path = Path(config.AGENT_ROOT)
    root_exists = root_path.exists()
    gemini_configured = bool(config.GEMINI_API_KEY)
    
    return {
        "schema_version": "1.0",
        "checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "environment": config.APP_ENV,
        "app": {
            "status": "ok",
            "health_endpoint": "ok",
            "version": "0.1.0"
        },
        "gemini": {
            "configured": gemini_configured,
            "model": config.GEMINI_MODEL,
            "last_successful_call_at": None
        },
        "data_layer": {
            "root_exists": root_exists,
            "inputs_write_guard_enabled": True,
            "last_backup_at": None
        },
        "deployment": {
            "target": "oracle-ampere-a1-flex",
            "docker_compose_status": "not_deployed_yet",
            "public_url": None
        }
    }