"""
app/workflows/deploy_check.py
Workflow to execute deployment checks and log diagnostic reports.
Evaluates docker context, configuration state, and database connections.
"""

import datetime
import json
from pathlib import Path
from app import config
from app.tools.filesystem import write_file
from app.tools.status import get_system_health

def run_deploy_check(domain: str = "personal-os", request_id: str = "internal") -> str:
    """
    Executes diagnostic routines and generates a deploy-check markdown report.
    """
    # 1. Run diagnostic checks
    health_data = get_system_health()
    health_data["checked_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    # Check if DB connection works
    try:
        import sqlite3
        db_path = Path(config.AGENT_ROOT) / "runtime" / "agent.db"
        conn = sqlite3.connect(str(db_path))
        conn.close()
        db_ok = "ok"
    except Exception as e:
        db_ok = f"error: {e}"
        
    health_data["app"]["database_status"] = db_ok

    # 2. Write updated system-health.json
    write_file(
        path=f"domains/{domain}/data/system-health.json",
        content=json.dumps(health_data, indent=2),
        allow_writes=True,
        request_id=request_id
    )

    # 3. Create MD report in domain outputs/reports/
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    report_path = f"domains/{domain}/outputs/reports/deploy-check-{today_str}.md"
    
    report_markdown = (
        f"# Deployment and Health Check Report - {today_str}\n\n"
        f"- **Checked At**: {health_data['checked_at']}\n"
        f"- **Environment**: {health_data['environment']}\n"
        f"- **Timezone**: {config.TIMEZONE}\n\n"
        f"## Component Status\n"
        f"- **FastAPI API**: {health_data['app']['status']} (version {health_data['app']['version']})\n"
        f"- **SQLite DB**: {db_ok}\n"
        f"- **Gemini Runtime**: {'Configured' if health_data['gemini']['configured'] else 'Missing Key'}\n"
        f"  - Active Model: `{health_data['gemini']['model']}`\n"
        f"- **Data Layer Root**: `{'Exists' if health_data['data_layer']['root_exists'] else 'Missing'}`\n"
        f"  - Path: `{config.AGENT_ROOT}`\n"
        f"- **Deployment Target**: `{health_data['deployment']['target']}`\n"
        f"  - Status: `{health_data['deployment']['docker_compose_status']}`\n"
    )

    write_file(
        path=report_path,
        content=report_markdown,
        allow_writes=True,
        request_id=request_id
    )

    # Refresh the unified dashboard.json state
    try:
        from app.tools.dashboard import refresh_dashboard_json
        refresh_dashboard_json(domain=domain, request_id=request_id)
    except Exception as e:
        # Avoid failing the whole check if dashboard refresh fails
        pass

    return f"Deploy check successfully completed. Health report saved to {report_path}"

if __name__ == "__main__":
    print(run_deploy_check())