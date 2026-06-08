"""
app/schemas/dashboard.py
Pydantic schemas for dashboard.json files.
"""

from pydantic import BaseModel, Field
from typing import List

class DashboardBrief(BaseModel):
    latest_file: str = Field(..., description="File path of the latest brief")
    summary: str = Field(..., description="Daily summary/focus string")
    generated_at: str = Field(..., description="ISO timestamp when brief was created")

class DashboardTaskItem(BaseModel):
    id: str = Field(..., description="Task unique identifier")
    title: str = Field(..., description="Task title")
    priority: str = Field(..., description="Task priority")
    status: str = Field(..., description="Task status")

class DashboardTasks(BaseModel):
    active_count: int = Field(..., description="Total count of active tasks")
    blocked_count: int = Field(..., description="Total count of blocked tasks")
    top: List[DashboardTaskItem] = Field(default_factory=list, description="List of top active tasks")

class DashboardProjectItem(BaseModel):
    id: str = Field(..., description="Project unique identifier")
    name: str = Field(..., description="Project name")
    status: str = Field(..., description="Project status")
    current_phase: str = Field(..., description="Project current phase")

class DashboardSystemHealth(BaseModel):
    app_status: str = Field(..., description="Health of the web server (e.g. ok)")
    gemini_configured: bool = Field(..., description="True if Gemini API key is validly configured")
    deployment_status: str = Field(..., description="Status of docker deployment")

class DashboardState(BaseModel):
    schema_version: str = Field("1.0", description="Schema version")
    updated_at: str = Field(..., description="ISO timestamp of when dashboard.json was generated")
    timezone: str = Field(..., description="Timezone name")
    brief: DashboardBrief = Field(..., description="Brief data subset")
    tasks: DashboardTasks = Field(..., description="Task counters and top tasks list")
    projects: List[DashboardProjectItem] = Field(default_factory=list, description="Active projects list")
    system_health: DashboardSystemHealth = Field(..., description="General system state indicators")