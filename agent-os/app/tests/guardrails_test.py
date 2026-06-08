"""
app/tests/guardrails_test.py
Unit tests for safe filesystem tools, security guardrails, and SQLite auditing.
Runs within a clean, temporary workspace.
"""

import unittest
import os
import sqlite3
from pathlib import Path
from app import config

# Set up test environment parameters before importing modules under test
TEST_ROOT = Path(__file__).resolve().parent.parent.parent / "runtime" / "test_agent_os"
os.environ["AGENT_ROOT"] = str(TEST_ROOT)
config.AGENT_ROOT = TEST_ROOT

from app.guardrails import check_write_permission, check_delete_permission, SecurityException
from app.tools.filesystem import read_file, write_file, delete_file
from app.audit import get_db_path

class GuardrailsTestCase(unittest.TestCase):
    def setUp(self):
        config.AGENT_ROOT = TEST_ROOT
        # Set up a mock data folder hierarchy
        TEST_ROOT.mkdir(parents=True, exist_ok=True)
        (TEST_ROOT / "domains" / "personal-os" / "inputs").mkdir(parents=True, exist_ok=True)
        (TEST_ROOT / "domains" / "personal-os" / "data").mkdir(parents=True, exist_ok=True)
        (TEST_ROOT / "runtime").mkdir(parents=True, exist_ok=True)
        
        # Create dummy text files
        (TEST_ROOT / "domains" / "personal-os" / "inputs" / "inbox.md").write_text("dummy inputs data", encoding="utf-8")
        (TEST_ROOT / "domains" / "personal-os" / "data" / "tasks.json").write_text("[]", encoding="utf-8")
        (TEST_ROOT / "TASKS.md").write_text("# Dummy Tasks List", encoding="utf-8")
        
        # Remove pre-existing db if it exists
        db_path = get_db_path()
        if db_path.exists():
            db_path.unlink()

    def tearDown(self):
        # Recursively delete test repository directory
        def rm_tree(pth: Path):
            for child in pth.iterdir():
                if child.is_file():
                    child.unlink()
                else:
                    rm_tree(child)
            pth.rmdir()
        if TEST_ROOT.exists():
            rm_tree(TEST_ROOT)

    def test_inputs_write_blocked(self):
        # Writing to inputs/ path is strictly forbidden under any circumstances
        path = TEST_ROOT / "domains" / "personal-os" / "inputs" / "inbox.md"
        with self.assertRaises(SecurityException):
            check_write_permission(path, allow_writes=True, approval_token="proceed")
            
        with self.assertRaises(SecurityException):
            write_file(str(path), "new edits", allow_writes=True, approval_token="proceed")

    def test_inputs_delete_blocked(self):
        # Deleting files in inputs/ is strictly prohibited
        path = TEST_ROOT / "domains" / "personal-os" / "inputs" / "inbox.md"
        with self.assertRaises(SecurityException):
            check_delete_permission(path, approval_token="proceed")
            
        with self.assertRaises(SecurityException):
            delete_file(str(path), approval_token="proceed")

    def test_critical_write_without_token_fails(self):
        # Writing to critical files (like TASKS.md) requires 'proceed' token
        path = TEST_ROOT / "TASKS.md"
        with self.assertRaises(SecurityException):
            check_write_permission(path, allow_writes=True, approval_token=None)
            
        with self.assertRaises(SecurityException):
            write_file(str(path), "# Changed", allow_writes=True, approval_token=None)

    def test_critical_write_with_token_succeeds(self):
        # Writing to critical files succeeds when the token is provided
        path = TEST_ROOT / "TASKS.md"
        result = write_file(str(path), "# Changed", allow_writes=True, approval_token="proceed")
        self.assertIn("Successfully wrote to", result)
        self.assertEqual(path.read_text(encoding="utf-8"), "# Changed")

    def test_standard_write_without_allow_writes_fails(self):
        # Writing to standard files requires allow_writes=True
        path = TEST_ROOT / "domains" / "personal-os" / "data" / "tasks.json"
        with self.assertRaises(SecurityException):
            check_write_permission(path, allow_writes=False)
            
        with self.assertRaises(SecurityException):
            write_file(str(path), "[]", allow_writes=False)

    def test_standard_write_with_allow_writes_succeeds(self):
        # Writing to standard files succeeds when allow_writes is True
        path = TEST_ROOT / "domains" / "personal-os" / "data" / "tasks.json"
        result = write_file(str(path), "{}", allow_writes=True)
        self.assertIn("Successfully wrote to", result)
        self.assertEqual(path.read_text(encoding="utf-8"), "{}")

    def test_delete_without_token_fails(self):
        # Deleting a file requires approval
        path = TEST_ROOT / "domains" / "personal-os" / "data" / "tasks.json"
        with self.assertRaises(SecurityException):
            check_delete_permission(path, approval_token=None)
            
        with self.assertRaises(SecurityException):
            delete_file(str(path), approval_token=None)

    def test_delete_with_token_succeeds(self):
        # Deleting succeeds when the proceed token is provided
        path = TEST_ROOT / "domains" / "personal-os" / "data" / "tasks.json"
        result = delete_file(str(path), approval_token="proceed")
        self.assertIn("Successfully deleted", result)
        self.assertFalse(path.exists())

    def test_auditing_records_populated(self):
        # Perform writes (one succeeds, one fails) and check database contents
        path_succeed = TEST_ROOT / "domains" / "personal-os" / "data" / "tasks.json"
        write_file(str(path_succeed), "{}", allow_writes=True)
        
        path_fail = TEST_ROOT / "domains" / "personal-os" / "inputs" / "inbox.md"
        with self.assertRaises(SecurityException):
            write_file(str(path_fail), "new", allow_writes=True)
            
        db_path = get_db_path()
        self.assertTrue(db_path.exists(), "SQLite database must be initialized.")
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Verify event auditing
        cursor.execute("SELECT event_type, approved FROM audit_events ORDER BY id ASC")
        events = cursor.fetchall()
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0], ("write_executed", 1))
        self.assertEqual(events[1], ("write_blocked", 0))
        
        # Verify tool log auditing
        cursor.execute("SELECT tool_name, status FROM tool_calls ORDER BY id ASC")
        tool_logs = cursor.fetchall()
        self.assertEqual(len(tool_logs), 2)
        self.assertEqual(tool_logs[0], ("write_file", "success"))
        self.assertEqual(tool_logs[1], ("write_file", "failed"))
        
        conn.close()

if __name__ == "__main__":
    unittest.main()
