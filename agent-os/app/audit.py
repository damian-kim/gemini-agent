"""
app/audit.py
SQLite-backed audit logger for Gemini Agent OS.
Initializes the database schema and provides helper functions to record
system events, model calls, and tool invocations.
"""

import sqlite3
import datetime
from pathlib import Path
from app import config

def get_db_path() -> Path:
    """Returns the absolute path to the SQLite audit database."""
    return Path(config.AGENT_ROOT) / "runtime" / "agent.db"

def init_db():
    """
    Initializes the SQLite database and creates audit tables if they do not exist.
    """
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # 1. audit_events table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_events (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      created_at TEXT NOT NULL,
      actor TEXT NOT NULL,
      event_type TEXT NOT NULL,
      request_id TEXT,
      domain TEXT,
      action TEXT NOT NULL,
      path TEXT,
      safety_level TEXT NOT NULL,
      approved INTEGER NOT NULL DEFAULT 0,
      summary TEXT NOT NULL
    );
    """)
    
    # 2. model_calls table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS model_calls (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      created_at TEXT NOT NULL,
      request_id TEXT NOT NULL,
      model TEXT NOT NULL,
      purpose TEXT NOT NULL,
      input_tokens INTEGER,
      output_tokens INTEGER,
      status TEXT NOT NULL,
      error TEXT
    );
    """)
    
    # 3. tool_calls table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tool_calls (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      created_at TEXT NOT NULL,
      request_id TEXT NOT NULL,
      tool_name TEXT NOT NULL,
      arguments_json TEXT NOT NULL,
      result_summary TEXT,
      status TEXT NOT NULL,
      safety_level TEXT NOT NULL
    );
    """)
    
    conn.commit()
    conn.close()

def log_audit_event(
    actor: str,
    event_type: str,
    action: str,
    safety_level: str,
    approved: bool,
    summary: str,
    request_id: str = None,
    domain: str = None,
    path: str = None
):
    """Inserts a system event audit record."""
    init_db()
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    cursor.execute("""
    INSERT INTO audit_events (created_at, actor, event_type, request_id, domain, action, path, safety_level, approved, summary)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (now, actor, event_type, request_id, domain, action, path, safety_level, 1 if approved else 0, summary))
    conn.commit()
    conn.close()

def log_model_call(
    request_id: str,
    model: str,
    purpose: str,
    status: str,
    input_tokens: int = None,
    output_tokens: int = None,
    error: str = None
):
    """Inserts a record of a Gemini model call."""
    init_db()
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    cursor.execute("""
    INSERT INTO model_calls (created_at, request_id, model, purpose, input_tokens, output_tokens, status, error)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (now, request_id, model, purpose, input_tokens, output_tokens, status, error))
    conn.commit()
    conn.close()

def log_tool_call(
    request_id: str,
    tool_name: str,
    arguments_json: str,
    status: str,
    safety_level: str,
    result_summary: str = None
):
    """Inserts a record of a tool invocation."""
    init_db()
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    cursor.execute("""
    INSERT INTO tool_calls (created_at, request_id, tool_name, arguments_json, result_summary, status, safety_level)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (now, request_id, tool_name, arguments_json, result_summary, status, safety_level))
    conn.commit()
    conn.close()