"""
app/schemas/project.py
Pydantic schemas for project and decision tracking.
Used to parse inputs/projects.md and memory/personal-os/decisions.md into structured JSON.
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class ProjectItem(BaseModel):
    id: str = Field(..., description="Project unique ID, e.g., proj_agent_os")
    slug: str = Field(..., description="Slug of the project, e.g., gemini-agent-os")
    name: str = Field(..., description="Name of the project")
    status: str = Field(..., description="Status of the project (e.g. active, completed, deferred)")
    domain: str = Field(..., description="Domain of the project (e.g., personal-os)")
    problem: str = Field(..., description="Problem statement of the project")
    success_criteria: List[str] = Field(default_factory=list, description="List of criteria for success")
    current_phase: str = Field(..., description="Current phase of execution")
    owner: str = Field(..., description="Project owner name")
    last_reviewed: str = Field(..., description="Last review date, e.g. YYYY-MM-DD")
    links: List[str] = Field(default_factory=list, description="Associated references or URLs")

class ProjectsContainer(BaseModel):
    schema_version: str = Field("1.0", description="Schema version")
    updated_at: str = Field(..., description="ISO timestamp of data generation")
    projects: List[ProjectItem] = Field(default_factory=list, description="List of projects")

class DecisionItem(BaseModel):
    id: str = Field(..., description="Unique decision ID, e.g., dec_20260607_001")
    date: str = Field(..., description="Decision date YYYY-MM-DD")
    domain: str = Field(..., description="Domain of the decision")
    decision: str = Field(..., description="Description of the decision made")
    reasoning: str = Field(..., description="Logical reasoning and context")
    tradeoff: str = Field(..., description="Identified tradeoffs")
    source: str = Field(..., description="File source of the decision, e.g. PRD-Gemini-Agent-OS.md")

class DecisionsContainer(BaseModel):
    schema_version: str = Field("1.0", description="Schema version")
    decisions: List[DecisionItem] = Field(default_factory=list, description="List of captured decisions")
