"""
app/tests/workflows_test.py
Unit tests for Gemini Agent OS workflows (refresh_data, update_tasks, morning_brief, deploy_check).
Uses unittest.mock to isolate file parsing and Pydantic validation from live API endpoints.
"""

import unittest
import os
import json
from pathlib import Path
from unittest.mock import patch
from app import config

# Set temporary workspace root directory
TEST_ROOT = Path(__file__).resolve().parent.parent.parent / "runtime" / "test_workflows_agent_os"
os.environ["AGENT_ROOT"] = str(TEST_ROOT)
config.AGENT_ROOT = TEST_ROOT

# Import workflows under test
from app.workflows.refresh_data import run_refresh_data
from app.workflows.update_tasks import run_update_tasks
from app.workflows.morning_brief import run_morning_brief
from app.workflows.deploy_check import run_deploy_check
from app.tools.filesystem import read_file

class WorkflowsTestCase(unittest.TestCase):
    def setUp(self):
        config.AGENT_ROOT = TEST_ROOT
        # Create folder hierarchy
        TEST_ROOT.mkdir(parents=True, exist_ok=True)
        (TEST_ROOT / "domains" / "personal-os" / "inputs").mkdir(parents=True, exist_ok=True)
        (TEST_ROOT / "domains" / "personal-os" / "data").mkdir(parents=True, exist_ok=True)
        (TEST_ROOT / "domains" / "personal-os" / "outputs" / "reports").mkdir(parents=True, exist_ok=True)
        (TEST_ROOT / "domains" / "personal-os" / "outputs" / "plans").mkdir(parents=True, exist_ok=True)
        (TEST_ROOT / "domains" / "personal-os" / "outputs" / "prds").mkdir(parents=True, exist_ok=True)
        (TEST_ROOT / "memory" / "personal-os").mkdir(parents=True, exist_ok=True)
        (TEST_ROOT / "briefs" / "archive").mkdir(parents=True, exist_ok=True)
        (TEST_ROOT / "dashboard").mkdir(parents=True, exist_ok=True)
        (TEST_ROOT / "runtime").mkdir(parents=True, exist_ok=True)
        (TEST_ROOT / "toolbox").mkdir(parents=True, exist_ok=True)

        # Create seed files
        (TEST_ROOT / "AGENTS.md").write_text("global operating instructions", encoding="utf-8")
        (TEST_ROOT / "domains" / "personal-os" / "AGENTS.md").write_text("domain personal instructions", encoding="utf-8")
        (TEST_ROOT / "memory" / "people.md").write_text("Damian Kim details", encoding="utf-8")
        (TEST_ROOT / "memory" / "terminology.md").write_text("Agent OS taxonomy", encoding="utf-8")
        (TEST_ROOT / "memory" / "personal-os" / "context.md").write_text("context detail", encoding="utf-8")
        (TEST_ROOT / "memory" / "personal-os" / "open-threads.md").write_text("open threads list", encoding="utf-8")
        (TEST_ROOT / "domains" / "personal-os" / "inputs" / "routines.md").write_text("routines markdown data", encoding="utf-8")
        (TEST_ROOT / "domains" / "personal-os" / "inputs" / "inbox.md").write_text("inbox notes", encoding="utf-8")
        (TEST_ROOT / "domains" / "personal-os" / "inputs" / "projects.md").write_text("# Projects list", encoding="utf-8")
        (TEST_ROOT / "memory" / "personal-os" / "decisions.md").write_text("# Decisions list", encoding="utf-8")
        (TEST_ROOT / "TASKS.md").write_text("- [ ] Task 1 <!-- id: task_20260607_001 -->", encoding="utf-8")

    def tearDown(self):
        # Clean up files recursively
        def rm_tree(pth: Path):
            for child in pth.iterdir():
                if child.is_file():
                    child.unlink()
                else:
                    rm_tree(child)
            pth.rmdir()
        if TEST_ROOT.exists():
            rm_tree(TEST_ROOT)

    def test_run_deploy_check(self):
        # Execution of local deploy diagnostic checks
        result = run_deploy_check(domain="personal-os")
        self.assertIn("Deploy check successfully completed", result)
        
        # Verify JSON outputs exist
        health_path = TEST_ROOT / "domains" / "personal-os" / "data" / "system-health.json"
        self.assertTrue(health_path.exists())
        
        # Check app health is marked as ok
        health_obj = json.loads(health_path.read_text(encoding="utf-8"))
        self.assertEqual(health_obj["app"]["status"], "ok")
        
        # Verify markdown report exists
        reports = list((TEST_ROOT / "domains" / "personal-os" / "outputs" / "reports").glob("deploy-check-*.md"))
        self.assertEqual(len(reports), 1)

    @patch("app.workflows.refresh_data.generate_structured_response")
    def test_run_refresh_data(self, mock_structured_response):
        # Mock structural output returns
        mock_structured_response.side_effect = [
            # First call: projects parsing
            json.dumps({
                "schema_version": "1.0",
                "updated_at": "2026-06-07T09:00:00Z",
                "projects": [
                    {
                        "id": "proj_agent_os",
                        "slug": "gemini-agent-os",
                        "name": "Gemini Agent OS",
                        "status": "active",
                        "domain": "personal-os",
                        "problem": "Build OS",
                        "success_criteria": ["Pass tests"],
                        "current_phase": "v0 build",
                        "owner": "Damian",
                        "last_reviewed": "2026-06-07",
                        "links": []
                    }
                ]
            }),
            # Second call: decisions parsing
            json.dumps({
                "schema_version": "1.0",
                "decisions": [
                    {
                        "id": "dec_20260607_001",
                        "date": "2026-06-07",
                        "domain": "personal-os",
                        "decision": "Use FastAPI",
                        "reasoning": "Clean integration",
                        "tradeoff": "boilerplate",
                        "source": "PRD"
                    }
                ]
            })
        ]

        result = run_refresh_data(domain="personal-os")
        self.assertIn("Data refresh complete", result)

        # Check JSON outputs
        proj_path = TEST_ROOT / "domains" / "personal-os" / "data" / "projects.json"
        dec_path = TEST_ROOT / "domains" / "personal-os" / "data" / "decisions.json"
        dashboard_path = TEST_ROOT / "dashboard" / "dashboard.json"

        self.assertTrue(proj_path.exists())
        self.assertTrue(dec_path.exists())
        self.assertTrue(dashboard_path.exists())

        # Verify parsed items
        projects_obj = json.loads(proj_path.read_text(encoding="utf-8"))
        self.assertEqual(projects_obj["projects"][0]["slug"], "gemini-agent-os")

    @patch("app.workflows.update_tasks.generate_structured_response")
    def test_run_update_tasks_without_approval(self, mock_structured_response):
        mock_structured_response.return_value = json.dumps({
            "schema_version": "1.0",
            "updated_at": "2026-06-07T09:00:00Z",
            "tasks": [
                {
                    "id": "task_20260607_001",
                    "title": "Deploy Gemini Agent OS MVP to Oracle VPS",
                    "status": "active",
                    "priority": "high",
                    "domain": "personal-os",
                    "project_id": "proj_agent_os",
                    "due_date": None,
                    "next_action": "Complete Block 0 local setup",
                    "source": "TASKS.md",
                    "created_at": "2026-06-07T09:00:00-05:00",
                    "updated_at": "2026-06-07T09:00:00-05:00",
                    "blocked_by": [],
                    "notes": ""
                }
            ]
        })

        # Run without approval
        result = run_update_tasks(domain="personal-os", approval_token=None)
        self.assertIn("Task extraction complete", result)
        self.assertIn("NOT overwritten (requires approval_token='proceed')", result)

        # Check tasks.json was updated
        tasks_json_path = TEST_ROOT / "domains" / "personal-os" / "data" / "tasks.json"
        self.assertTrue(tasks_json_path.exists())

        # Confirm root TASKS.md remains untouched
        original_md = "- [ ] Task 1 <!-- id: task_20260607_001 -->"
        self.assertEqual(read_file("TASKS.md"), original_md)

    @patch("app.workflows.update_tasks.generate_structured_response")
    def test_run_update_tasks_with_approval(self, mock_structured_response):
        mock_structured_response.return_value = json.dumps({
            "schema_version": "1.0",
            "updated_at": "2026-06-07T09:00:00Z",
            "tasks": [
                {
                    "id": "task_20260607_001",
                    "title": "Deploy Gemini Agent OS MVP to Oracle VPS",
                    "status": "active",
                    "priority": "high",
                    "domain": "personal-os",
                    "project_id": "proj_agent_os",
                    "due_date": None,
                    "next_action": "Complete Block 0 local setup",
                    "source": "TASKS.md",
                    "created_at": "2026-06-07T09:00:00-05:00",
                    "updated_at": "2026-06-07T09:00:00-05:00",
                    "blocked_by": [],
                    "notes": ""
                }
            ]
        })

        # Run WITH approval
        result = run_update_tasks(domain="personal-os", approval_token="proceed")
        self.assertIn("Root TASKS.md updated with approval", result)

        # Confirm root TASKS.md was updated
        updated_md = read_file("TASKS.md")
        self.assertIn("Deploy Gemini Agent OS MVP to Oracle VPS", updated_md)
        self.assertIn("task_20260607_001", updated_md)

    @patch("app.workflows.update_tasks.generate_structured_response")
    def test_run_update_tasks_reads_project_plans(self, mock_structured_response):
        # Write a mock plan file
        plan_path = TEST_ROOT / "domains" / "personal-os" / "outputs" / "plans" / "plan-test-project.md"
        plan_path.write_text("Mock project plan content for tasks", encoding="utf-8")

        mock_structured_response.return_value = json.dumps({
            "schema_version": "1.0",
            "updated_at": "2026-06-07T09:00:00Z",
            "tasks": [
                {
                    "id": "task_20260607_999",
                    "title": "Task from project plan",
                    "status": "active",
                    "priority": "medium",
                    "domain": "personal-os",
                    "project_id": "proj_test",
                    "due_date": None,
                    "next_action": "Do something",
                    "source": "plan-test-project.md",
                    "created_at": "2026-06-07T09:00:00-05:00",
                    "updated_at": "2026-06-07T09:00:00-05:00",
                    "blocked_by": [],
                    "notes": ""
                }
            ]
        })

        result = run_update_tasks(domain="personal-os", approval_token="proceed")
        self.assertIn("Root TASKS.md updated with approval", result)

        # Verify mock_structured_response was called with the plan content in prompt
        mock_structured_response.assert_called_once()
        call_kwargs = mock_structured_response.call_args[1]
        self.assertIn("### Project Plans:", call_kwargs["prompt"])
        self.assertIn("Mock project plan content for tasks", call_kwargs["prompt"])

        # Check tasks.json was updated
        tasks_json_path = TEST_ROOT / "domains" / "personal-os" / "data" / "tasks.json"
        self.assertTrue(tasks_json_path.exists())
        tasks_obj = json.loads(tasks_json_path.read_text(encoding="utf-8"))
        self.assertEqual(len(tasks_obj["tasks"]), 1)
        self.assertEqual(tasks_obj["tasks"][0]["id"], "task_20260607_999")

    @patch("app.workflows.morning_brief.generate_structured_response")

    @patch("app.workflows.morning_brief.generate_response")
    def test_run_morning_brief(self, mock_response, mock_structured_response):
        mock_response.return_value = (
            "# Morning Brief: 2026-06-07\n\n"
            "## Today focus\nFinish local setup.\n\n"
            "## Top priorities\n- Complete tasks.\n"
        )
        mock_structured_response.return_value = json.dumps({
            "schema_version": "1.0",
            "last_brief_at": "2026-06-07T08:00:00Z",
            "last_brief_file": "briefs/archive/brief-2026-06-07.md",
            "summary": "Focus today: finish local setup.",
            "top_priorities": ["Complete tasks."],
            "open_questions": []
        })

        result = run_morning_brief(domain="personal-os")
        self.assertIn("Morning brief workflow complete", result)

        # Check brief outputs
        latest_brief_path = TEST_ROOT / "briefs" / "latest.md"
        brief_state_path = TEST_ROOT / "domains" / "personal-os" / "data" / "brief-state.json"
        
        self.assertTrue(latest_brief_path.exists())
        self.assertTrue(brief_state_path.exists())
        
        self.assertEqual(latest_brief_path.read_text(encoding="utf-8"), mock_response.return_value)

if __name__ == "__main__":
    unittest.main()
