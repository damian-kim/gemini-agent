"""
app/schemas/task.py
Pydantic schemas for individual tasks and task collection containers.
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class Task(BaseModel):
    id: str = Field(..., description="Unique task identifier, e.g., task_YYYYMMDD_NNN")
    title: str = Field(..., description="Short descriptive title of the task")
    status: str = Field(..., description="Status of the task (e.g., active, completed, blocked)")
    priority: str = Field(..., description="Priority of the task (e.g., high, medium, low)")
    domain: str = Field(..., description="Domain of the task (e.g., personal-os)")
    project_id: Optional[str] = Field(None, description="Optional associated project identifier")
    due_date: Optional[str] = Field(None, description="Optional due date string")
    next_action: Optional[str] = Field(None, description="Concrete next action step")
    source: str = Field(..., description="Source file or path of the task (e.g., TASKS.md)")
    created_at: str = Field(..., description="Creation ISO timestamp")
    updated_at: str = Field(..., description="Last update ISO timestamp")
    blocked_by: List[str] = Field(default_factory=list, description="List of task IDs blocking this task")
    notes: Optional[str] = Field(None, description="Additional notes or context")

class TasksContainer(BaseModel):
    schema_version: str = Field("1.0", description="Schema version")
    updated_at: str = Field(..., description="ISO timestamp of when the file was last updated")
    tasks: List[Task] = Field(default_factory=list, description="List of tasks")